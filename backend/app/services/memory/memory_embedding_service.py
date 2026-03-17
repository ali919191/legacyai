from __future__ import annotations

from typing import Iterable, List, Tuple
from .vector_store import VectorStore
from ..storage.hybrid_storage import (
    LocalVectorBackend,
    PgVectorBackend,
    PineconeVectorBackend,
    VectorBackend,
)


class MemoryEmbeddingService:
    """
    Service for generating embeddings from memory text and performing semantic similarity search.

    Uses a real sentence-transformers embedding model for semantic search.

    Integrates with VectorStore for storage and search.
    Designed for conversation engine to retrieve relevant memories based on user queries.
    """

    EMBEDDING_DIMENSION = 384  # Common dimension for embeddings like BERT-based models
    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        vector_store_file: str = "memory_embeddings.json",
        vector_backend: VectorBackend | None = None,
        vector_provider: str = "local",
        vector_config: dict | None = None,
        model_name: str = DEFAULT_MODEL_NAME,
    ):
        """
        Initialize the embedding service.

        Args:
            vector_store_file: Path to the vector store JSON file.
        """
        self.vector_store = VectorStore(vector_store_file)
        self.vector_backend = vector_backend or self._build_vector_backend(
            vector_provider=vector_provider,
            vector_store_file=vector_store_file,
            vector_config=vector_config or {},
        )
        self.model_name = model_name
        self._model = None

    def _build_vector_backend(
        self,
        vector_provider: str,
        vector_store_file: str,
        vector_config: dict,
    ) -> VectorBackend:
        """Build a vector backend adapter from provider configuration."""
        provider = (vector_provider or "local").lower()
        if provider == "pgvector":
            return PgVectorBackend(
                dsn=vector_config.get("dsn", ""),
                table_name=vector_config.get("table_name", "memory_vectors"),
            )
        if provider == "pinecone":
            return PineconeVectorBackend(
                api_key=vector_config.get("api_key", ""),
                index_name=vector_config.get("index_name", "legacyai-memory-vectors"),
            )
        return LocalVectorBackend(vector_store_file)

    def _get_model(self):
        """Lazily load the sentence-transformers model used for embeddings."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "sentence-transformers is required for semantic embeddings. "
                    "Install backend requirements before running the embedding service."
                ) from exc

            self._model = SentenceTransformer(self.model_name)

        return self._model

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for the given text.

        Args:
            text: The text to embed.

        Returns:
            The embedding vector.
        """
        model = self._get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def build_memory_embedding_text(
        self,
        title: str,
        description: str,
        tags: Iterable[str] | None = None,
        emotions: Iterable[str] | None = None,
    ) -> str:
        """Build the canonical text used for memory embeddings."""
        tag_text = ", ".join(tags or [])
        emotion_text = ", ".join(emotions or [])
        parts = [
            f"Title: {title}",
            f"Description: {description}",
        ]
        if tag_text:
            parts.append(f"Tags: {tag_text}")
        if emotion_text:
            parts.append(f"Emotions: {emotion_text}")
        return "\n".join(parts)

    def store_memory_embedding(self, memory_id: str, text: str):
        """
        Generate and store an embedding for a memory.

        Args:
            memory_id: Unique identifier for the memory.
            text: The memory text to embed (e.g., title + description).
        """
        embedding = self.generate_embedding(text)
        self.vector_backend.add_embedding(memory_id, embedding)

    def search_similar_memories(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for memories semantically similar to the query.

        Args:
            query: The search query text.
            top_k: Number of top similar memories to return.

        Returns:
            List of tuples (memory_id, similarity_score) sorted by similarity descending.
        """
        query_embedding = self.generate_embedding(query)
        return self.vector_backend.search(query_embedding, top_k)

    def update_memory_embedding(self, memory_id: str, new_text: str):
        """
        Update the embedding for an existing memory.

        Args:
            memory_id: The memory ID to update.
            new_text: The new text to embed.
        """
        self.store_memory_embedding(memory_id, new_text)  # Overwrites existing

    def remove_memory_embedding(self, memory_id: str):
        """
        Remove the embedding for a memory.

        Args:
            memory_id: The memory ID to remove.
        """
        self.vector_backend.remove_embedding(memory_id)