from __future__ import annotations

import re


def normalize_entity_name(name: str) -> str:
    name = name.strip()

    name = re.sub(
        r"\s+",
        " ",
        name,
    )

    return name


def entity_id(name: str) -> str:
    return (
        re.sub(
            r"[^a-z0-9]+",
            "_",
            name.lower(),
        )
        .strip("_")
    )