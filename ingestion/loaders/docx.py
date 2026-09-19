from pathlib import Path


def load_docx(path: str | Path) -> str:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "Install python-docx with: pip install python-docx"
        ) from exc

    document = Document(str(path))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n\n".join(paragraphs)