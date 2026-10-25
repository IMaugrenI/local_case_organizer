"""Explicit offline text extraction, optional OCR, and bounded local search.

Source bytes must match the provenance hash. Original evidence is never edited.
Extracted derivatives live only in the existing ignored case working directory.
No network calls, unrequested scans, or mandatory third-party dependencies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from local_case_organizer.export.helpers import _resolve_original_path, load_provenance_index
from local_case_organizer.paths import create_local_workspace, get_workspace_paths
from local_case_organizer.register.store import read_register_rows

MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_PAGE_CHARS = 16_000
MAX_PAGES = 8
MAX_INDEX_ITEMS = 300
ALLOWED_SUFFIXES = {".txt", ".md", ".csv", ".eml", ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".eml"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def _index_dir() -> Path:
    return get_workspace_paths().working_dir / "text_index"


def _index_path(file_id: str) -> Path:
    if not isinstance(file_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,110}", file_id):
        raise ValueError("Invalid document ID")
    digest = hashlib.sha256(file_id.encode("utf-8")).hexdigest()
    return _index_dir() / (digest + ".json")


def _source_for(file_id: str) -> tuple[Path, dict[str, str]]:
    paths = get_workspace_paths()
    if file_id not in {str(row.get("file_id", "")) for row in read_register_rows()}:
        raise ValueError("Document ID is not in the selected case register")
    prov = load_provenance_index(paths.register_dir).get(file_id)
    if not prov or not re.fullmatch(r"[a-fA-F0-9]{64}", str(prov.get("sha256", ""))):
        raise ValueError("Valid source provenance is required")
    original = _resolve_original_path(paths.originals_dir, str(prov.get("stored_relative_path", "")))
    if original.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Original exceeds local extraction size limit")
    sha = hashlib.sha256()
    with original.open("rb") as fd:
        for block in iter(lambda: fd.read(1024 * 1024), b""):
            sha.update(block)
    if sha.hexdigest() != str(prov["sha256"]).lower():
        raise ValueError("Original integrity mismatch; extraction refused")
    return original, prov


def _run_command(command: list[str], *, max_output: int = 700_000) -> str:
    """Bound command duration and stdout; never invoke a shell or remote endpoint."""
    try:
        completed = subprocess.run(command, capture_output=True, timeout=22, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Optional offline extraction tool unavailable or timed out") from exc
    if completed.returncode:
        # Never expose tool stderr; it can contain private absolute paths.
        raise ValueError("Optional offline extraction tool failed")
    if len(completed.stdout) > max_output:
        raise ValueError("Extracted text exceeds bounded output limit")
    return completed.stdout.decode("utf-8", errors="replace")


def _pdf_text(path: Path) -> tuple[list[dict], str]:
    executable = shutil.which("pdftotext")
    if executable is not None:
        with tempfile.TemporaryDirectory(prefix="lco-pdf-") as tmp:
            output = Path(tmp) / "pages.txt"
            try:
                completed = subprocess.run(
                    [executable, "-f", "1", "-l", str(MAX_PAGES), "-enc", "UTF-8",
                     str(path), str(output)], capture_output=True, timeout=22, check=False
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ValueError("Offline PDF extraction timed out or unavailable") from exc
            if completed.returncode or not output.is_file():
                raise ValueError("Cannot extract PDF text; document may be protected or invalid")
            if output.stat().st_size > 700_000:
                raise ValueError("Extracted PDF text exceeds limit")
            body = output.read_text(encoding="utf-8", errors="replace")
        pages = [{"page": i, "text": piece[:MAX_PAGE_CHARS]} for i, piece in
                 enumerate(body.split("\f")[:MAX_PAGES], 1) if piece.strip()]
        return pages, "pdftotext"
    try:
        from pypdf import PdfReader  # optional local dependency, not installed by default
    except ImportError as exc:
        raise ValueError("PDF extraction requires pdftotext or the optional pypdf library") from exc
    try:
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")
        pages = [{"page": i + 1, "text": (page.extract_text() or "")[:MAX_PAGE_CHARS]}
                 for i, page in enumerate(reader.pages[:MAX_PAGES])]
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Could not parse this PDF locally") from exc
    return pages, "pypdf"


def _ocr_image(path: Path) -> str:
    tesseract = shutil.which("tesseract")
    if tesseract is None:
        raise ValueError("OCR requires optional local Tesseract executable")
    return _run_command([tesseract, str(path), "stdout"], max_output=300_000)


def _ocr_pdf(path: Path) -> list[dict]:
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise ValueError("Scanned-PDF OCR also requires optional local pdftoppm")
    if shutil.which("tesseract") is None:
        raise ValueError("Scanned-PDF OCR requires optional local Tesseract")
    result = []
    with tempfile.TemporaryDirectory(prefix="lco-ocr-") as tmp:
        for page in range(1, min(MAX_PAGES, 3) + 1):
            prefix = Path(tmp) / ("page" + str(page))
            try:
                process = subprocess.run([
                    renderer, "-f", str(page), "-l", str(page), "-r", "110",
                    "-scale-to", "1400", "-singlefile", "-png", str(path), str(prefix)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=22, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ValueError("Offline PDF OCR renderer unavailable or timed out") from exc
            picture = prefix.with_suffix(".png")
            if process.returncode != 0 or not picture.is_file():
                # Page outside the PDF page range ends the optional OCR scan.
                break
            if picture.stat().st_size > 8 * 1024 * 1024:
                raise ValueError("Rendered PDF OCR page exceeds size limit")
            text = _ocr_image(picture)
            result.append({"page": page, "text": text[:MAX_PAGE_CHARS]})
    return result


def index_document(file_id: str, *, use_ocr: bool = False) -> dict[str, object]:
    """An explicit user action; only a registered and hash-matching source is accepted."""
    source, provenance = _source_for(file_id)
    suffix = Path(str(provenance.get("original_name", source.name))).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("File type is unsupported for local text extraction")
    if suffix in TEXT_SUFFIXES:
        with source.open("rb") as fd:
            raw = fd.read(MAX_INPUT_BYTES + 1)
        if b"\x00" in raw:
            raise ValueError("Binary content is not a supported text document")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("Text document must be UTF-8") from exc
        pages, method = [{"page": 1, "text": text[:MAX_PAGE_CHARS]}], "plaintext"
    elif suffix == ".pdf":
        try:
            pages, method = _pdf_text(source)
        except ValueError:
            if not use_ocr:
                raise
            pages, method = [], "ocr_pdf"
        if use_ocr and not any(str(p["text"]).strip() for p in pages):
            pages, method = _ocr_pdf(source), "ocr_pdf"
    else:
        if not use_ocr:
            raise ValueError("Image OCR is opt-in; retry with use_ocr enabled")
        pages, method = [{"page": 1, "text": _ocr_image(source)[:MAX_PAGE_CHARS]}], "tesseract"
    pages = [{ "page": int(p["page"]), "text": str(p["text"])[:MAX_PAGE_CHARS]}
             for p in pages[:MAX_PAGES]]
    folder = _index_dir()
    folder.mkdir(parents=True, exist_ok=True)
    target = _index_path(file_id)
    if not target.exists() and len(list(folder.glob("*.json"))) >= MAX_INDEX_ITEMS:
        raise ValueError("Maximum locally indexed documents reached")
    payload = {
        "version": 1, "file_id": file_id,
        "source_sha256": str(provenance["sha256"]).lower(),
        "original_name": str(provenance.get("original_name", ""))[:120],
        "created_at_utc": datetime.now(UTC).isoformat(),
        "method": method, "pages": pages,
    }
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=folder,
                                         prefix=".text-index-", delete=False) as stream:
            temp_path = stream.name
            os.chmod(temp_path, 0o600)
            json.dump(payload, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, target)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
    return {"file_id": file_id, "method": method, "pages": len(pages),
            "characters": sum(len(p["text"]) for p in pages), "status": "indexed_locally"}


def get_indexed(file_id: str, *, verify_original: bool = False) -> dict:
    target = _index_path(file_id)
    if not target.is_file() or target.is_symlink() or target.stat().st_size > 800_000:
        raise ValueError("Document has no valid local text index")
    data = json.loads(target.read_text(encoding="utf-8"))
    if data.get("version") != 1 or data.get("file_id") != file_id or not isinstance(data.get("pages"), list):
        raise ValueError("Local text index is invalid")
    if verify_original:
        _, provenance = _source_for(file_id)
        if str(provenance["sha256"]).lower() != data.get("source_sha256"):
            raise ValueError("Local text index is stale")
    return data


def search_text(query: str, max_hits: int = 35) -> dict[str, object]:
    if not isinstance(query, str) or not (2 <= len(query.strip()) <= 100):
        raise ValueError("Search query must be between 2 and 100 characters")
    if not 1 <= max_hits <= 50:
        raise ValueError("Invalid search limit")
    root = _index_dir()
    hits = []
    searched = 0
    if not root.exists():
        return {"matches": [], "indexed_files": 0}
    for path in sorted(root.glob("*.json"))[:MAX_INDEX_ITEMS]:
        if path.is_symlink() or path.stat().st_size > 800_000:
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        file_id = str(doc.get("file_id", ""))
        # Search is scoped to the selected case only, and stale/mutated sources are excluded.
        try:
            valid = get_indexed(file_id, verify_original=True)
        except (ValueError, OSError):
            continue
        searched += 1
        needle = query.strip().casefold()
        for page in valid["pages"][:MAX_PAGES]:
            text = str(page.get("text", ""))
            spot = text.casefold().find(needle)
            if spot < 0:
                continue
            start = max(0, spot - 90)
            end = min(len(text), spot + len(needle) + 90)
            hits.append({"file_id": file_id, "page": int(page.get("page", 1)),
                         "original_name": str(doc.get("original_name", ""))[:120],
                         "excerpt": text[start:end]})
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    return {"matches": hits, "indexed_files": searched, "limit_reached": len(hits) >= max_hits}
