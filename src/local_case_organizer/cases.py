"""Opt-in isolated case workspaces; the unselected legacy workspace remains unchanged."""
from __future__ import annotations

import json
import re
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path

_ACTIVE_CASE: ContextVar[str | None] = ContextVar("local_case_active", default=None)
_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")


def validate_case_id(case_id: str) -> str:
    if not isinstance(case_id, str) or not _ID.fullmatch(case_id):
        raise ValueError("Case ID must be 1–48 lowercase ASCII characters: a-z, 0-9, _ or -")
    return case_id


def get_active_case() -> str | None:
    return _ACTIVE_CASE.get()


@contextmanager
def using_case(case_id: str | None):
    if case_id is not None:
        validate_case_id(case_id)
    token = _ACTIVE_CASE.set(case_id)
    try:
        yield
    finally:
        _ACTIVE_CASE.reset(token)


def _case_base(root: Path, case_id: str) -> Path:
    validate_case_id(case_id)
    base = root / "cases" / case_id
    # Refuse symlinks escaping the designated private case root.
    resolved_root = (root / "cases").resolve()
    if not base.resolve().is_relative_to(resolved_root):
        raise ValueError("Case directory escapes private case root")
    return base


def selected_data_root(root: Path) -> Path:
    active = get_active_case()
    if active is None:
        return root
    base = _case_base(root, active)
    if not (base / "case.json").is_file():
        raise ValueError("Unknown case ID; create it explicitly with create-case")
    return base


def create_case(root: Path, case_id: str, title: str = "") -> dict[str, str]:
    base = _case_base(root, case_id)
    if base.exists():
        raise FileExistsError("Case ID already exists")
    if len(title) > 120 or any(ord(ch) < 32 for ch in title):
        raise ValueError("Invalid case title")
    base.mkdir(parents=True, exist_ok=False)
    manifest = {
        "case_id": case_id, "title": title or case_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
    }
    with (base / "case.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
    # Scoped setup goes through the existing workspace factory.
    from local_case_organizer.paths import create_local_workspace
    with using_case(case_id):
        create_local_workspace(root)
    return manifest


def list_cases(root: Path) -> list[dict[str, str]]:
    directory = root / "cases"
    if not directory.is_dir():
        return []
    result = []
    for child in sorted(directory.iterdir()):
        if not child.is_dir() or child.is_symlink():
            continue
        try:
            _case_base(root, child.name)
            data = json.loads((child / "case.json").read_text(encoding="utf-8"))
            if data.get("case_id") == child.name:
                result.append({key: str(data.get(key, "")) for key in ("case_id", "title", "created_at_utc")})
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return result
