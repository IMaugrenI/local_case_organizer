from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path

from local_case_organizer.export.builder import build_export_package
from local_case_organizer.paths import create_local_workspace, describe_workspace, get_workspace_paths
from local_case_organizer.register.generator import build_document_register
from local_case_organizer.timeline.generator import build_timeline_template


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local_case_organizer",
        description="Local, cloud-free dossier organizer for structured case work.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Show repository and local workspace status")
    subparsers.add_parser("init-workspace", help="Create ignored local workspace folders")
    subparsers.add_parser("build-register", help="Generate a document register from local originals")
    subparsers.add_parser("build-timeline", help="Generate an editable timeline template")
    subparsers.add_parser("export-package", help="Build a neutral export package from local register data")
    return parser


def cmd_check() -> int:
    paths = get_workspace_paths()
    status = {
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
            "originals_dir": paths.originals_dir.exists(),
            "register_dir": paths.register_dir.exists(),
            "exports_dir": paths.exports_dir.exists(),
        },
    }
    print(json.dumps(status, indent=2))
    return 0


def cmd_init_workspace() -> int:
    paths = create_local_workspace()
    print(json.dumps({"created": describe_workspace(paths)}, indent=2))
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

    if args.command == "check":
        return cmd_check()
    if args.command == "init-workspace":
        return cmd_init_workspace()
    if args.command == "build-register":
        return cmd_build_register()
    if args.command == "build-timeline":
        return cmd_build_timeline()
    if args.command == "export-package":
        return cmd_export_package()

    parser.print_help()
    return 1
