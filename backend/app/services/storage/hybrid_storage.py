from __future__ import annotations

import json
import math
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class VectorBackend(ABC):
    """Abstract interface for vector storage backends."""

    @abstractmethod
    def add_embedding(self, item_id: str, embedding: List[float]):
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        pass

    @abstractmethod
    def get_embedding(self, item_id: str) -> Optional[List[float]]:
        pass

    @abstractmethod
    def remove_embedding(self, item_id: str):
        pass


class GraphBackend(ABC):
    """Abstract interface for graph storage backends (people + relationships)."""

    @abstractmethod
    def upsert_person(self, person_id: str, profile: Dict[str, Any]):
        pass

    @abstractmethod
    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_people(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def upsert_relationship(self, relationship_id: str, relationship: Dict[str, Any]):
        pass

    @abstractmethod
    def get_relationships_for_person(self, person_id: str) -> List[Dict[str, Any]]:
        pass


class DocumentBackend(ABC):
    """Abstract interface for document storage of full memory records."""

    @abstractmethod
    def create_document(self, doc_id: str, document: Dict[str, Any]):
        pass

    @abstractmethod
    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_documents(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        pass


class LocalVectorBackend(VectorBackend):
    """Local file-backed vector adapter using the existing VectorStore."""

    def __init__(self, storage_file: str = "memory_embeddings.json"):
        self._storage_file = storage_file
        self._embeddings: Dict[str, List[float]] = {}
        self._load()

    def _load(self):
        if os.path.exists(self._storage_file):
            with open(self._storage_file, "r", encoding="utf-8") as fp:
                self._embeddings = json.load(fp)

    def _save(self):
        with open(self._storage_file, "w", encoding="utf-8") as fp:
            json.dump(self._embeddings, fp, indent=2)

    def _cosine_similarity(self, left: List[float], right: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(left, right))
        norm_left = math.sqrt(sum(value * value for value in left))
        norm_right = math.sqrt(sum(value * value for value in right))
        if norm_left == 0.0 or norm_right == 0.0:
            return 0.0
        return dot_product / (norm_left * norm_right)

    def add_embedding(self, item_id: str, embedding: List[float]):
        self._embeddings[item_id] = embedding
        self._save()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        scored = [
            (item_id, self._cosine_similarity(query_embedding, embedding))
            for item_id, embedding in self._embeddings.items()
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]

    def get_embedding(self, item_id: str) -> Optional[List[float]]:
        return self._embeddings.get(item_id)

    def remove_embedding(self, item_id: str):
        if item_id in self._embeddings:
            del self._embeddings[item_id]
            self._save()


class PgVectorBackend(VectorBackend):
    """PostgreSQL pgvector backend for high-scale semantic retrieval."""

    def __init__(self, dsn: str, table_name: str = "memory_vectors"):
        self._dsn = dsn
        self._table_name = table_name

        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("PgVectorBackend requires psycopg package") from exc

        self._psycopg = psycopg
        self._ensure_table()

    def _ensure_table(self):
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE EXTENSION IF NOT EXISTS vector;
                    CREATE TABLE IF NOT EXISTS {self._table_name} (
                        id TEXT PRIMARY KEY,
                        embedding vector(384) NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                conn.commit()

    def add_embedding(self, item_id: str, embedding: List[float]):
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self._table_name}(id, embedding, updated_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (id)
                    DO UPDATE SET embedding = EXCLUDED.embedding, updated_at = NOW()
                    """,
                    (item_id, embedding),
                )
                conn.commit()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, (1 - (embedding <=> %s::vector)) AS score
                    FROM {self._table_name}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (query_embedding, query_embedding, top_k),
                )
                rows = cur.fetchall()
                return [(str(row[0]), float(row[1])) for row in rows]

    def get_embedding(self, item_id: str) -> Optional[List[float]]:
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT embedding FROM {self._table_name} WHERE id = %s",
                    (item_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return list(row[0])

    def remove_embedding(self, item_id: str):
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self._table_name} WHERE id = %s", (item_id,))
                conn.commit()


class PineconeVectorBackend(VectorBackend):
    """Pinecone-managed vector backend for cloud-scale retrieval."""

    def __init__(self, api_key: str, index_name: str):
        try:
            from pinecone import Pinecone  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("PineconeVectorBackend requires pinecone package") from exc

        client = Pinecone(api_key=api_key)
        self._index = client.Index(index_name)

    def add_embedding(self, item_id: str, embedding: List[float]):
        self._index.upsert(vectors=[(item_id, embedding, {})])

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        response = self._index.query(vector=query_embedding, top_k=top_k)
        return [(match["id"], float(match.get("score", 0.0))) for match in response.get("matches", [])]

    def get_embedding(self, item_id: str) -> Optional[List[float]]:
        response = self._index.fetch(ids=[item_id])
        vector = response.get("vectors", {}).get(item_id)
        if not vector:
            return None
        return list(vector.get("values", []))

    def remove_embedding(self, item_id: str):
        self._index.delete(ids=[item_id])


class InMemoryGraphBackend(GraphBackend):
    """Default graph backend for local/dev mode and tests."""

    def __init__(self):
        self.people: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {}

    def upsert_person(self, person_id: str, profile: Dict[str, Any]):
        self.people[person_id] = dict(profile)

    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        person = self.people.get(person_id)
        return dict(person) if person else None

    def list_people(self) -> List[Dict[str, Any]]:
        return [dict(profile) for profile in self.people.values()]

    def upsert_relationship(self, relationship_id: str, relationship: Dict[str, Any]):
        self.relationships[relationship_id] = dict(relationship)

    def get_relationships_for_person(self, person_id: str) -> List[Dict[str, Any]]:
        matches = [
            dict(relationship)
            for relationship in self.relationships.values()
            if relationship.get("person_a") == person_id or relationship.get("person_b") == person_id
        ]
        return sorted(matches, key=lambda rel: rel.get("timestamp", ""))


class InMemoryDocumentBackend(DocumentBackend):
    """Default document backend for local/dev mode and tests."""

    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}

    def create_document(self, doc_id: str, document: Dict[str, Any]):
        self.documents[doc_id] = dict(document)

    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        if doc_id not in self.documents:
            return False
        self.documents[doc_id] = dict(document)
        return True

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        value = self.documents.get(doc_id)
        return dict(value) if value else None

    def list_documents(self) -> List[Dict[str, Any]]:
        return [dict(value) for value in self.documents.values()]

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False


class Neo4jGraphBackend(GraphBackend):
    """Neo4j-backed graph adapter for production-scale relationship storage."""

    def __init__(self, uri: str, user: str, password: str):
        self._uri = uri
        self._user = user
        self._password = password

        try:
            from neo4j import GraphDatabase  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Neo4jGraphBackend requires neo4j package") from exc

        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def upsert_person(self, person_id: str, profile: Dict[str, Any]):
        with self._driver.session() as session:
            session.run(
                """
                MERGE (p:Person {person_id: $person_id})
                SET p += $props
                """,
                person_id=person_id,
                props=profile,
            )

    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        with self._driver.session() as session:
            result = session.run(
                "MATCH (p:Person {person_id: $person_id}) RETURN p",
                person_id=person_id,
            ).single()
            if not result:
                return None
            return dict(result["p"])

    def list_people(self) -> List[Dict[str, Any]]:
        with self._driver.session() as session:
            rows = session.run("MATCH (p:Person) RETURN p")
            return [dict(row["p"]) for row in rows]

    def upsert_relationship(self, relationship_id: str, relationship: Dict[str, Any]):
        with self._driver.session() as session:
            session.run(
                """
                MERGE (a:Person {person_id: $person_a})
                MERGE (b:Person {person_id: $person_b})
                MERGE (a)-[r:RELATIONSHIP {relationship_id: $relationship_id}]->(b)
                SET r += $props
                """,
                person_a=relationship.get("person_a"),
                person_b=relationship.get("person_b"),
                relationship_id=relationship_id,
                props=relationship,
            )

    def get_relationships_for_person(self, person_id: str) -> List[Dict[str, Any]]:
        with self._driver.session() as session:
            rows = session.run(
                """
                MATCH (a:Person {person_id: $person_id})-[r:RELATIONSHIP]->(b:Person)
                RETURN r
                UNION
                MATCH (a:Person)-[r:RELATIONSHIP]->(b:Person {person_id: $person_id})
                RETURN r
                """,
                person_id=person_id,
            )
            return [dict(row["r"]) for row in rows]


class PostgresJsonbDocumentBackend(DocumentBackend):
    """PostgreSQL JSONB-backed document store for memory records."""

    def __init__(self, dsn: str, table_name: str = "memory_documents"):
        self._dsn = dsn
        self._table_name = table_name

        try:
            import psycopg  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("PostgresJsonbDocumentBackend requires psycopg package") from exc

        self._psycopg = psycopg
        self._ensure_table()

    def _ensure_table(self):
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._table_name} (
                        id TEXT PRIMARY KEY,
                        payload JSONB NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                conn.commit()

    def create_document(self, doc_id: str, document: Dict[str, Any]):
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self._table_name}(id, payload, updated_at)
                    VALUES (%s, %s::jsonb, NOW())
                    ON CONFLICT (id)
                    DO UPDATE SET payload = EXCLUDED.payload, updated_at = NOW()
                    """,
                    (doc_id, json.dumps(document)),
                )
                conn.commit()

    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        self.create_document(doc_id, document)
        return True

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT payload FROM {self._table_name} WHERE id = %s",
                    (doc_id,),
                )
                row = cur.fetchone()
                return dict(row[0]) if row else None

    def list_documents(self) -> List[Dict[str, Any]]:
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT payload FROM {self._table_name}")
                rows = cur.fetchall()
                return [dict(row[0]) for row in rows]

    def delete_document(self, doc_id: str) -> bool:
        with self._psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self._table_name} WHERE id = %s", (doc_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted
