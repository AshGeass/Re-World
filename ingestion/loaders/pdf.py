from pathlib import Path


def load_pdf(path: str | Path) -> str:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        import pypdf
    except ImportError as exc:
        raise ImportError(
            "Install pypdf with: pip install pypdf"
        ) from exc

    reader = pypdf.PdfReader(str(path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n\n".join(pages)