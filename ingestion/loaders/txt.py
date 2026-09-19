from pathlib import Path


def load_txt(path: str | Path) -> str:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding="utf-8")