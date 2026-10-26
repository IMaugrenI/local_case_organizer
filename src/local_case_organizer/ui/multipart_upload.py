"""Bounded multipart/form-data decoding on Python 3.11–3.14 (no deprecated cgi).

The email MIME parser performs binary-safe boundary and part extraction.
All fields are parsed into memory only after a strict Content-Length gate.
No filesystem changes occur in this module.
"""
from __future__ import annotations

from email.parser import BytesParser
from email.policy import default

MAX_UPLOAD_BODY = 32 * 1024 * 1024
MAX_PARTS = 64
MAX_FILES = 32


def _safe_filename(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Uploaded file has no valid filename")
    # Browsers may send Windows-style paths; never trust a client-supplied path.
    name = value.replace("\\", "/").rsplit("/", 1)[-1]
    if (not name or name in {".", ".."} or len(name.encode("utf-8")) > 240
            or any(ord(character) < 32 or ord(character) == 127 for character in name)
            or ":" in name):
        raise ValueError("Uploaded filename is unsafe")
    return name


def parse_multipart_files(handler) -> list[tuple[str, bytes]]:
    """Return (safe basename, exact bytes) for 'files' fields only."""
    raw_length = str(handler.headers.get("Content-Length", ""))
    if not raw_length.isascii() or not raw_length.isdecimal():
        raise ValueError("Multipart request requires a valid Content-Length")
    length = int(raw_length)
    if length <= 0 or length > MAX_UPLOAD_BODY:
        raise ValueError("Multipart request exceeds the 32 MiB limit")
    content_type = handler.headers.get("Content-Type", "")
    if (not isinstance(content_type, str) or len(content_type) > 512
            or any(character in content_type for character in "\r\n")):
        raise ValueError("Invalid multipart Content-Type")
    try:
        header = content_type.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("Invalid multipart header encoding") from exc

    body = handler.rfile.read(length)
    if len(body) != length:
        raise ValueError("Incomplete multipart upload")
    message = BytesParser(policy=default).parsebytes(
        b"Content-Type: " + header + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
    )
    boundary = message.get_boundary()
    if (message.get_content_type() != "multipart/form-data"
            or not isinstance(boundary, str) or not 1 <= len(boundary) <= 70
            or not message.is_multipart() or message.defects):
        raise ValueError("Malformed multipart/form-data body")
    parts = list(message.iter_parts())
    if len(parts) > MAX_PARTS:
        raise ValueError("Too many multipart fields")
    files = []
    for part in parts:
        if part.defects or part.is_multipart():
            raise ValueError("Malformed or nested multipart field")
        if part.get_content_disposition() != "form-data":
            raise ValueError("Invalid multipart content disposition")
        if part.get_param("name", header="content-disposition") != "files":
            continue
        filename = part.get_filename()
        if filename is None:
            raise ValueError("File field lacks a filename")
        data = part.get_payload(decode=True)
        if not isinstance(data, bytes):
            raise ValueError("Malformed multipart file payload")
        files.append((_safe_filename(filename), data))
        if len(files) > MAX_FILES:
            raise ValueError("Too many uploaded files")
    if not files:
        raise ValueError("No file part named 'files' in multipart request")
    return files
