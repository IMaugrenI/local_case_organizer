"""Source-linked, non-inferential evidence relationship candidates for a local case."""
from __future__ import annotations

from local_case_organizer.claims import read_claims
from local_case_organizer.entities.store import read_entity_rows
from local_case_organizer.register.store import read_register_rows
from local_case_organizer.timeline.store import read_timeline_rows


def _links(value: str) -> list[str]:
    return [item.strip() for item in str(value).split(",") if item.strip()]


def evidence_graph(max_nodes: int = 180) -> dict[str, object]:
    """Expose only manually registered links. No truth or legal interpretation."""
    if not 1 <= max_nodes <= 500:
        raise ValueError("Invalid graph node limit")
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    unknown: list[dict[str, str]] = []
    files = read_register_rows()
    events = read_timeline_rows()
    entities = read_entity_rows()
    claims = read_claims()
    valid_files = {str(row.get("file_id", "")).strip() for row in files}

    for row in files:
        file_id = str(row.get("file_id", "")).strip()
        if file_id:
            nodes.append({"id": "file:" + file_id, "kind": "document",
                          "label": str(row.get("original_name") or file_id)[:120]})
    for kind, rows, id_field, label_field in (
        ("event", events, "event_id", "event_title"),
        ("entity", entities, "entity_id", "entity_name"),
    ):
        for row in rows:
            node_id = str(row.get(id_field, "")).strip()
            if not node_id:
                continue
            source = kind + ":" + node_id
            nodes.append({"id": source, "kind": kind,
                          "label": str(row.get(label_field) or node_id)[:120]})
            for file_id in _links(row.get("linked_file_ids", "")):
                if file_id not in valid_files:
                    unknown.append({"source": source, "missing_file_id": file_id})
                else:
                    edges.append({"source": source, "target": "file:" + file_id,
                                  "relation": "linked_file"})
    for row in claims[:500]:
        claim_id = str(row.get("claim_id", "")).strip()
        file_id = str(row.get("file_id", "")).strip()
        if not claim_id:
            continue
        source = "claim:" + claim_id
        nodes.append({"id": source, "kind": "claim",
                      "label": str(row.get("statement") or claim_id)[:120]})
        if file_id in valid_files:
            edges.append({"source": source, "target": "file:" + file_id,
                          "relation": "quoted_source"})
        else:
            unknown.append({"source": source, "missing_file_id": file_id})
    limited = nodes[:max_nodes]
    allowed = {item["id"] for item in limited}
    return {"nodes": limited,
            "edges": [item for item in edges if item["source"] in allowed and item["target"] in allowed],
            "unresolved": unknown[:100],
            "truncated": len(nodes) > max_nodes or len(unknown) > 100,
            "total_nodes": len(nodes)}
