from ingestion import load_source
from ingestion.normalization import normalize_text


def load_and_normalize(path: str) -> str:
    text = load_source(path)
    return normalize_text(text)