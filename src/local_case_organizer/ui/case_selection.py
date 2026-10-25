"""Validated per-request case selection for the existing loopback browser UI."""
from __future__ import annotations

from pathlib import Path

from local_case_organizer.cases import selected_data_root, using_case, validate_case_id


def requested_case(header: str | None, default: str | None, root: Path) -> str | None:
    """Validate before changing scope. The special 'legacy-default' is explicit."""
    if header is None or header == "":
        candidate = default
    elif header == "legacy-default":
        candidate = None
    else:
        candidate = validate_case_id(header)
    with using_case(candidate):
        selected_data_root(root)  # check manifest and reject symlinked cases
    return candidate
