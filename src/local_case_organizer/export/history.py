from __future__ import annotations

import json
from pathlib import Path

from local_case_organizer.paths import get_workspace_paths



def read_export_history(limit: int = 10) -> list[dict[str, str]]:
    exports_dir = get_workspace_paths().exports_dir
    if not exports_dir.exists():
        return []

    rows: list[dict[str, str]] = []
    export_dirs = sorted([path for path in exports_dir.iterdir() if path.is_dir()], key=lambda p: p.name, reverse=True)
    for export_dir in export_dirs[:limit]:
        manifest_path = export_dir / 'export_manifest.json'
        zip_path = export_dir.with_suffix('.zip')
        row = {
            'export_dir': export_dir.name,
            'zip_name': zip_path.name if zip_path.exists() else '',
            'manifest_name': manifest_path.name if manifest_path.exists() else '',
            'selected_originals_count': '',
        }
        if manifest_path.exists():
            try:
                payload = json.loads(manifest_path.read_text(encoding='utf-8'))
                row['selected_originals_count'] = str(payload.get('selected_originals_count', ''))
            except Exception:
                pass
        rows.append(row)
    return rows
