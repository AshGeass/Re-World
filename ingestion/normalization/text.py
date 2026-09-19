from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive whitespace while preserving paragraphs.
    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()