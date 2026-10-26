"""Regression for Python 3.13+ removal of the stdlib cgi module."""
from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace

import pytest

from local_case_organizer import paths
from local_case_organizer.ui.app import _save_uploaded_files
from local_case_organizer.ui.multipart_upload import parse_multipart_files


BOUNDARY = "----tof-safe-upload"


def request(files, *, declared=None, boundary=BOUNDARY):
    body = bytearray()
    for filename, data in files:
        body.extend(("--" + boundary + "\r\n" +
                     f'Content-Disposition: form-data; name="files"; filename="{filename}"\r\n' +
                     "Content-Type: application/octet-stream\r\n\r\n").encode())
        body.extend(data)
        body.extend(b"\r\n")
    body.extend(("--" + boundary + "--\r\n").encode())
    return SimpleNamespace(
        headers={"Content-Length": str(len(body) if declared is None else declared),
                 "Content-Type": "multipart/form-data; boundary=" + boundary},
        rfile=BytesIO(bytes(body)),
    )


def test_binary_upload_preserved_under_current_python(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    raw = bytes(range(256)) * 9 + b"\x00\xff\x80\r\n"
    result = _save_uploaded_files(request([("archive.bin", raw), ("note.txt", b"hello")]))
    inbox = tmp_path / "data" / "inbox"
    assert result["uploaded_files"] == ["archive.bin", "note.txt"]
    assert (inbox / "archive.bin").read_bytes() == raw
    assert (inbox / "note.txt").read_bytes() == b"hello"


def test_same_name_is_not_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    inbox = paths.create_local_workspace().inbox_dir
    original = inbox / "report.txt"
    original.write_bytes(b"untouched")
    _save_uploaded_files(request([("report.txt", b"new")]))
    assert original.read_bytes() == b"untouched"
    assert (inbox / "report_1.txt").read_bytes() == b"new"


def test_windows_and_traversal_filenames_are_basenames(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    saved = _save_uploaded_files(request([("../../outside.txt", b"one"),
                                          (r"C:\fakepath\inside.txt", b"two")]))
    assert saved["uploaded_files"] == ["outside.txt", "inside.txt"]
    assert not (tmp_path / "outside.txt").exists()
    assert (tmp_path / "data" / "inbox" / "inside.txt").read_bytes() == b"two"


def test_oversize_short_and_malformed_are_rejected_without_writes(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_repo_root", lambda: tmp_path)
    with pytest.raises(ValueError, match="limit"):
        _save_uploaded_files(request([("a.txt", b"a")], declared=32*1024*1024+1))
    with pytest.raises(ValueError, match="Incomplete"):
        _save_uploaded_files(request([("a.txt", b"a")], declared=300))
    bad = request([("a.txt", b"a")])
    bad.headers["Content-Type"] = "multipart/form-data; boundary=not-the-boundary"
    with pytest.raises(ValueError, match="Malformed"):
        _save_uploaded_files(bad)
    assert not (tmp_path / "data" / "inbox").exists()


@pytest.mark.parametrize("unsafe", ["..", ".", "a:b.txt", "bad\x00.txt", "x" * 241])
def test_unsafe_filenames_are_rejected(unsafe):
    # Parsing the actual filename from multipart, not a manually trusted path.
    with pytest.raises(ValueError):
        parse_multipart_files(request([(unsafe, b"test")]))


def test_duplicate_files_are_bounded():
    with pytest.raises(ValueError, match="Too many"):
        parse_multipart_files(request([(f"{i}.txt", b"a") for i in range(33)]))


def test_cli_override_is_importable_without_cgi():
    from local_case_organizer.ui.app import HTML
    assert "id=\\"case-selector\\"" in HTML
