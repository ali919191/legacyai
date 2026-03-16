"""Database configuration for scalable hybrid memory storage architecture."""

from dataclasses import dataclass
import os


@dataclass
class DatabaseConfig:
    """Typed configuration for vector, graph, and document storage backends."""

    vector_provider: str = "local"
    vector_pg_dsn: str = ""
    vector_pg_table: str = "memory_vectors"
    vector_pinecone_api_key: str = ""
    vector_pinecone_index: str = "legacyai-memory-vectors"
    vector_local_file: str = "memory_embeddings.json"

    graph_provider: str = "inmemory"
    graph_neo4j_uri: str = "bolt://localhost:7687"
    graph_neo4j_user: str = "neo4j"
    graph_neo4j_password: str = "neo4j"

    document_provider: str = "inmemory"
    document_pg_dsn: str = ""
    document_pg_table: str = "memory_documents"


def load_database_config() -> DatabaseConfig:
    """Load storage configuration from environment variables."""
    return DatabaseConfig(
        vector_provider=os.getenv("VECTOR_DB_PROVIDER", "local").strip().lower(),
        vector_pg_dsn=os.getenv("VECTOR_DB_PGVECTOR_DSN", "").strip(),
        vector_pg_table=os.getenv("VECTOR_DB_PGVECTOR_TABLE", "memory_vectors").strip(),
        vector_pinecone_api_key=os.getenv("VECTOR_DB_PINECONE_API_KEY", "").strip(),
        vector_pinecone_index=os.getenv("VECTOR_DB_PINECONE_INDEX", "legacyai-memory-vectors").strip(),
        vector_local_file=os.getenv("VECTOR_STORE_FILE", "memory_embeddings.json").strip(),
        graph_provider=os.getenv("GRAPH_DB_PROVIDER", "inmemory").strip().lower(),
        graph_neo4j_uri=os.getenv("GRAPH_DB_NEO4J_URI", "bolt://localhost:7687").strip(),
        graph_neo4j_user=os.getenv("GRAPH_DB_NEO4J_USER", "neo4j").strip(),
        graph_neo4j_password=os.getenv("GRAPH_DB_NEO4J_PASSWORD", "neo4j").strip(),
        document_provider=os.getenv("DOCUMENT_DB_PROVIDER", "inmemory").strip().lower(),
        document_pg_dsn=os.getenv("DOCUMENT_DB_POSTGRES_DSN", "").strip(),
        document_pg_table=os.getenv("DOCUMENT_DB_POSTGRES_TABLE", "memory_documents").strip(),
    )