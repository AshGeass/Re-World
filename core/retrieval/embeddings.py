from __future__ import annotations


class EmbeddingProvider:
    """
    Interface for generating embeddings.

    A real embedding API/provider can be connected later.
    """

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError(
            "Connect an embedding provider before generating embeddings."
        )

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]