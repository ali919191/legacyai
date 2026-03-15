"""Memory services package for Legacy AI.

Contains embedding and vector storage services for semantic memory search.
"""

from .memory_embedding_service import MemoryEmbeddingService
from .vector_store import VectorStore

__all__ = ['MemoryEmbeddingService', 'VectorStore']