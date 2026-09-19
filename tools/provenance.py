from core.world import Provenance


def label_source(
    provenance: Provenance,
    source_id: str,
    location: str | None = None,
    confidence: float = 1.0,
) -> dict:
    return {
        "provenance": provenance.value,
        "source_id": source_id,
        "location": location,
        "confidence": confidence,
    }