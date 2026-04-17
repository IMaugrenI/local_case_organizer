from __future__ import annotations

import csv
from pathlib import Path

from local_case_organizer.paths import create_local_workspace, get_workspace_paths
from local_case_organizer.timeline.store import TIMELINE_FIELDS, read_timeline_rows



def build_timeline_template() -> Path:
    create_local_workspace()
    paths = get_workspace_paths()
    output_path = paths.register_dir / "timeline.csv"

    existing_rows = read_timeline_rows()
    if existing_rows:
        return output_path

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TIMELINE_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "event_id": "EV-000001",
                "event_date": "",
                "event_title": "",
                "linked_file_ids": "",
                "people_or_entities": "",
                "summary": "",
                "status": "draft",
            }
        )

    return output_path
