from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.export.builder import build_export_package
from local_case_organizer.imports.ingest import import_sources
from local_case_organizer.paths import create_local_workspace, describe_workspace, get_workspace_paths
from local_case_organizer.register.generator import build_document_register
from local_case_organizer.timeline.generator import build_timeline_template


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local_case_organizer",
        description="Local, cloud-free dossier organizer for structured case work.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", aliases=["init-workspace"], help="Prepare ignored local workspace folders")
    subparsers.add_parser("check", help="Show repository and local workspace status")
    subparsers.add_parser("status", help="Show a concise local workspace summary")
    subparsers.add_parser("doctor", help="Run local environment and writeability checks")

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
            "place private files in data/inbox/ or use python run.py import --source /path/to/files",
            "run python run.py import",
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

    if args.command in {"setup", "init-workspace"}:
        return cmd_setup()
    if args.command == "check":
        return cmd_check()
    if args.command == "status":
        return cmd_status()
    if args.command == "doctor":
        return cmd_doctor()
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
