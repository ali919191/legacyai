import json
import os
import math
from typing import List, Tuple, Dict


class VectorStore:
    """
    Simple in-memory vector store with cosine similarity search.
    Stores embeddings as JSON for persistence.

    Future integration: Replace with a real vector database like Pinecone, Weaviate, or pgvector
    for scalable, high-performance similarity search with indexing and metadata filtering.
    """

    def __init__(self, storage_file: str = "vector_store.json"):
        """
        Initialize the vector store.

        Args:
            storage_file: Path to the JSON file for persistence.
        """
        self.storage_file = storage_file
        self.embeddings: Dict[str, List[float]] = {}
        self._load_from_file()

    def _load_from_file(self):
        """Load embeddings from JSON file if it exists."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                self.embeddings = json.load(f)

    def _save_to_file(self):
        """Save embeddings to JSON file."""
        with open(self.storage_file, 'w') as f:
            json.dump(self.embeddings, f, indent=2)

    def add_embedding(self, item_id: str, embedding: List[float]):
        """
        Add an embedding to the store.

        Args:
            item_id: Unique identifier for the item.
            embedding: The embedding vector.
        """
        self.embeddings[item_id] = embedding
        self._save_to_file()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for the most similar embeddings.

        Args:
            query_embedding: The query embedding vector.
            top_k: Number of top results to return.

        Returns:
            List of tuples (item_id, similarity_score) sorted by similarity descending.
        """
        similarities = []
        for item_id, embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((item_id, similarity))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_embedding(self, item_id: str) -> List[float]:
        """Retrieve an embedding by item ID."""
        return self.embeddings.get(item_id)

    def remove_embedding(self, item_id: str):
        """Remove an embedding by item ID."""
        if item_id in self.embeddings:
            del self.embeddings[item_id]
            self._save_to_file()