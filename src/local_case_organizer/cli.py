from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.cases import create_case, get_active_case, list_cases, using_case
from local_case_organizer.comparison import comparison_report
from local_case_organizer.audit import recent_changes
from local_case_organizer.tasks import add_task, update_task, task_board
from local_case_organizer.ai_exchange import (prepare_ai_packet, import_ai_file,
                                               read_ai_suggestions, review_ai_suggestion)
from local_case_organizer.document_text import index_document, search_text
from local_case_organizer.claims import add_claim, read_claims, set_review_status
from local_case_organizer.integrity import verify_integrity
from local_case_organizer.timeline.suggestions import propose_events
from local_case_organizer.export.builder import build_export_package
from local_case_organizer.imports.ingest import import_sources
from local_case_organizer.paths import create_local_workspace, describe_workspace, get_workspace_paths
from local_case_organizer.register.generator import build_document_register
from local_case_organizer.timeline.generator import build_timeline_template
from local_case_organizer.ui.app import run_ui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local_case_organizer",
        description="Local, cloud-free dossier organizer for structured case work.",
    )
    parser.add_argument("--case", default=None, help="Explicitly select an isolated case ID; default keeps legacy workspace")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_case = subparsers.add_parser("create-case", help="Create a new isolated local case")
    new_case.add_argument("case_id", help="Lowercase identifier for this case")
    new_case.add_argument("--title", default="", help="Optional local display title")
    subparsers.add_parser("list-cases", help="List locally registered case IDs")
    subparsers.add_parser("verify-integrity", help="Explicitly verify original document hashes")
    subparsers.add_parser("propose-events", help="Suggest unverified dates from registered plaintext sources")
    subparsers.add_parser("compare-claims", help="Report manually grouped possible claim discrepancies")
    subparsers.add_parser("audit-history", help="List committed local CSV metadata changes")
    subparsers.add_parser("tasks", help="List manually managed local reminders")
    task_create = subparsers.add_parser("add-task", help="Create a manual case reminder")
    task_create.add_argument("title")
    task_create.add_argument("--due", default="", help="Operator-entered date YYYY-MM-DD")
    task_create.add_argument("--priority", choices=["low", "normal", "high"], default="normal")
    task_create.add_argument("--linked-file-ids", default="", help="Comma-separated local register file IDs")
    task_create.add_argument("--note", default="")
    task_update = subparsers.add_parser("update-task", help="Change manual task status")
    task_update.add_argument("task_id")
    task_update.add_argument("--status", choices=["open", "in_progress", "done", "cancelled"], required=True)
    index_parser = subparsers.add_parser("index-document", help="Manually index a verified imported document for offline text search")
    index_parser.add_argument("file_id")
    index_parser.add_argument("--ocr", action="store_true", help="Explicitly enable optional offline OCR")
    search_parser = subparsers.add_parser("search-text", help="Search local verified derivative text")
    search_parser.add_argument("query")
    packet_parser = subparsers.add_parser("prepare-ai-review", help="Manually prepare a private offline text packet for another local assistant")
    packet_parser.add_argument("file_ids", nargs="+")
    ai_import = subparsers.add_parser("import-ai-review", help="Read an untrusted AI JSON response from the private local inbox")
    ai_import.add_argument("filename")
    subparsers.add_parser("ai-suggestions", help="Read pending and reviewed AI suggestions")
    ai_review = subparsers.add_parser("review-ai-suggestion", help="Reject or convert one AI proposal into an unreviewed draft claim")
    ai_review.add_argument("suggestion_id")
    ai_review.add_argument("--decision", choices=["reject", "create_draft_claim"], required=True)
    subparsers.add_parser("list-claims", help="List sourced claims for selected case")
    claim_parser = subparsers.add_parser("add-claim", help="Record a draft claim bound to a source passage")
    claim_parser.add_argument("file_id")
    claim_parser.add_argument("--page", type=int, required=True)
    claim_parser.add_argument("--quote", required=True)
    claim_parser.add_argument("--statement", required=True)
    review_parser = subparsers.add_parser("review-claim", help="Set manual review metadata for a claim")
    review_parser.add_argument("claim_id")
    review_parser.add_argument("--status", choices=["draft", "needs_review", "reviewed"], required=True)

    subparsers.add_parser("setup", aliases=["init-workspace"], help="Prepare ignored local workspace folders")
    subparsers.add_parser("check", help="Show repository and local workspace status")
    subparsers.add_parser("status", help="Show a concise local workspace summary")
    subparsers.add_parser("doctor", help="Run local environment and writeability checks")

    ui_parser = subparsers.add_parser("ui", help="Start the local browser UI")
    ui_parser.add_argument("--host", type=str, default="127.0.0.1", help="UI host address")
    ui_parser.add_argument("--port", type=int, default=8765, help="UI port")
    ui_parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")

    import_parser = subparsers.add_parser("import", help="Import files from data/inbox or a chosen source path")
    import_parser.add_argument("--source", type=str, default=None, help="Optional file or folder path to import")

    subparsers.add_parser("build-register", help="Generate a document register from imported originals")
    subparsers.add_parser("build-timeline", help="Generate an editable timeline template")
    subparsers.add_parser("export-package", help="Build a neutral export package from local register data")
    return parser



def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())



def _count_directories(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.iterdir() if item.is_dir())



def _check_writable(path: Path) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    probe = path / ".write_probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False



def _base_status() -> tuple[object, dict[str, object]]:
    paths = get_workspace_paths()
    payload = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "workspace": describe_workspace(paths),
        "exists": {
            "run.py": (paths.repo_root / "run.py").exists(),
            "pyproject.toml": (paths.repo_root / "pyproject.toml").exists(),
            "src_package": (paths.repo_root / "src" / "local_case_organizer").exists(),
            "docs": (paths.repo_root / "docs").exists(),
            "examples": (paths.repo_root / "examples").exists(),
            "profiles_default": (paths.repo_root / "profiles" / "default").exists(),
            "data_dir": paths.data_dir.exists(),
            "inbox_dir": paths.inbox_dir.exists(),
            "originals_dir": paths.originals_dir.exists(),
            "register_dir": paths.register_dir.exists(),
            "exports_dir": paths.exports_dir.exists(),
        },
    }
    return paths, payload



def cmd_setup() -> int:
    paths = create_local_workspace()
    payload = {
        "created": describe_workspace(paths),
        "next_steps": [
            "start the browser UI with python run.py ui",
            "or place private files in data/inbox/ and run python run.py import",
            "run python run.py build-register",
            "run python run.py build-timeline",
            "run python run.py export-package",
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0



def cmd_check() -> int:
    _, payload = _base_status()
    print(json.dumps(payload, indent=2))
    return 0



def cmd_status() -> int:
    paths, payload = _base_status()
    summary = {
        "timestamp_utc": payload["timestamp_utc"],
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "active_case": get_active_case() or "legacy-default",
        "inbox_file_count": _count_files(paths.inbox_dir),
        "original_file_count": _count_files(paths.originals_dir),
        "import_batches": _count_directories(paths.originals_dir),
        "register_files": _count_files(paths.register_dir),
        "export_packages": _count_directories(paths.exports_dir),
    }
    print(json.dumps(summary, indent=2))
    return 0



def cmd_doctor() -> int:
    paths = create_local_workspace()
    doctor = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "checks": {
            "repo_root_exists": paths.repo_root.exists(),
            "run_py_exists": (paths.repo_root / "run.py").exists(),
            "src_package_exists": (paths.repo_root / "src" / "local_case_organizer").exists(),
            "data_dir_writable": _check_writable(paths.data_dir),
            "inbox_dir_writable": _check_writable(paths.inbox_dir),
            "originals_dir_writable": _check_writable(paths.originals_dir),
            "register_dir_writable": _check_writable(paths.register_dir),
            "exports_dir_writable": _check_writable(paths.exports_dir),
            "logs_dir_writable": _check_writable(paths.logs_dir),
        },
    }
    print(json.dumps(doctor, indent=2))
    return 0



def cmd_ui(host: str, port: int, no_browser: bool) -> int:
    return run_ui(host=host, port=port, open_browser=not no_browser)



def cmd_import(source: str | None) -> int:
    payload = import_sources(source)
    print(json.dumps(payload, indent=2))
    return 0



def cmd_build_register() -> int:
    output_path = build_document_register()
    print(json.dumps({"register_path": str(output_path)}, indent=2))
    return 0



def cmd_build_timeline() -> int:
    output_path = build_timeline_template()
    print(json.dumps({"timeline_path": str(output_path)}, indent=2))
    return 0



def cmd_export_package() -> int:
    output_dir = build_export_package()
    print(json.dumps({"export_dir": str(output_dir)}, indent=2))
    return 0



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    with using_case(args.case):
        return _dispatch(args)


def _dispatch(args: argparse.Namespace) -> int:
    if args.command == "create-case":
        print(json.dumps(create_case(get_workspace_paths().repo_root, args.case_id, args.title), indent=2))
        return 0
    if args.command == "list-cases":
        print(json.dumps({"cases": list_cases(get_workspace_paths().repo_root)}, indent=2))
        return 0
    if args.command == "verify-integrity":
        print(json.dumps(verify_integrity(), indent=2))
        return 0
    if args.command == "propose-events":
        print(json.dumps(propose_events(), indent=2, ensure_ascii=False))
        return 0
    if args.command == "compare-claims":
        print(json.dumps(comparison_report(), indent=2, ensure_ascii=False))
        return 0
    if args.command == "tasks":
        print(json.dumps(task_board(), indent=2, ensure_ascii=False))
        return 0
    if args.command == "add-task":
        print(json.dumps(add_task(args.title, args.due, args.priority,
                                  args.linked_file_ids, args.note), indent=2, ensure_ascii=False))
        return 0
    if args.command == "update-task":
        print(json.dumps(update_task(args.task_id, args.status), indent=2, ensure_ascii=False))
        return 0
    if args.command == "audit-history":
        print(json.dumps({"changes": recent_changes()}, indent=2, ensure_ascii=False))
        return 0
    if args.command == "index-document":
        print(json.dumps(index_document(args.file_id, use_ocr=args.ocr), indent=2))
        return 0
    if args.command == "search-text":
        print(json.dumps(search_text(args.query), indent=2, ensure_ascii=False))
        return 0
    if args.command == "prepare-ai-review":
        print(json.dumps(prepare_ai_packet(args.file_ids), indent=2, ensure_ascii=False))
        return 0
    if args.command == "import-ai-review":
        print(json.dumps(import_ai_file(args.filename), indent=2, ensure_ascii=False))
        return 0
    if args.command == "ai-suggestions":
        print(json.dumps({"suggestions": read_ai_suggestions()}, indent=2, ensure_ascii=False))
        return 0
    if args.command == "review-ai-suggestion":
        print(json.dumps(review_ai_suggestion(args.suggestion_id, args.decision),
                         indent=2, ensure_ascii=False))
        return 0
    if args.command == "list-claims":
        print(json.dumps({"claims": read_claims()}, indent=2, ensure_ascii=False))
        return 0
    if args.command == "add-claim":
        print(json.dumps(add_claim(args.file_id, args.page, args.quote, args.statement), indent=2, ensure_ascii=False))
        return 0
    if args.command == "review-claim":
        print(json.dumps(set_review_status(args.claim_id, args.status), indent=2))
        return 0
    if args.command in {"setup", "init-workspace"}:
        return cmd_setup()
    if args.command == "check":
        return cmd_check()
    if args.command == "status":
        return cmd_status()
    if args.command == "doctor":
        return cmd_doctor()
    if args.command == "ui":
        return cmd_ui(args.host, args.port, args.no_browser)
    if args.command == "import":
        return cmd_import(args.source)
    if args.command == "build-register":
        return cmd_build_register()
    if args.command == "build-timeline":
        return cmd_build_timeline()
    if args.command == "export-package":
        return cmd_export_package()

    parser.print_help()
    return 1
