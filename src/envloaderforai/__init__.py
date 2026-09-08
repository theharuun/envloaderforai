"""Personal env loader — projeler için tek konvansiyon."""
from __future__ import annotations
from pathlib import Path
from typing import Sequence

SECRETS_DIR = Path.home() / "Secrets"


def resolve_env_files(
    project_root: Path,
    project_name: str | None = None,
) -> Sequence[Path]:
    """
    Env dosyalarını sırayla döndürür:
      1) project_root / ".env"          (prod baseline)
      2) ~/Secrets/<project_name>.env   (local override)
    """
    name = project_name or project_root.name
    return (
        project_root / ".env",
        SECRETS_DIR / f"{name}.env",
    )

def load_into_environ(
    project_root: Path,
    project_name: str | None = None,
) -> None:
    """
    python-dotenv kullanan projeler için convenience wrapper.
    """
    from dotenv import load_dotenv
    for path in resolve_env_files(project_root, project_name):
        load_dotenv(path, override=True)