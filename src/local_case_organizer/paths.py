from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspacePaths:
    repo_root: Path
    data_dir: Path
    inbox_dir: Path
    originals_dir: Path
    working_dir: Path
    register_dir: Path
    exports_dir: Path
    logs_dir: Path
    workspace_dir: Path
    profiles_dir: Path


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_workspace_paths(repo_root: Path | None = None) -> WorkspacePaths:
    root = repo_root or get_repo_root()
    data_dir = root / "data"
    return WorkspacePaths(
        repo_root=root,
        data_dir=data_dir,
        inbox_dir=data_dir / "inbox",
        originals_dir=data_dir / "originals",
        working_dir=data_dir / "working",
        register_dir=data_dir / "register",
        exports_dir=root / "exports",
        logs_dir=root / "logs",
        workspace_dir=root / "workspace",
        profiles_dir=root / "profiles",
    )


def create_local_workspace(repo_root: Path | None = None) -> WorkspacePaths:
    paths = get_workspace_paths(repo_root)
    for path in [
        paths.data_dir,
        paths.inbox_dir,
        paths.originals_dir,
        paths.working_dir,
        paths.register_dir,
        paths.exports_dir,
        paths.logs_dir,
        paths.workspace_dir,
        paths.profiles_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)
    return paths


def describe_workspace(paths: WorkspacePaths) -> dict[str, str]:
    return {
        "repo_root": str(paths.repo_root),
        "data_dir": str(paths.data_dir),
        "inbox_dir": str(paths.inbox_dir),
        "originals_dir": str(paths.originals_dir),
        "working_dir": str(paths.working_dir),
        "register_dir": str(paths.register_dir),
        "exports_dir": str(paths.exports_dir),
        "logs_dir": str(paths.logs_dir),
        "workspace_dir": str(paths.workspace_dir),
        "profiles_dir": str(paths.profiles_dir),
    }
