import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config.database_config import load_database_config


class TestDatabaseConfig(unittest.TestCase):

    def test_load_database_config_from_environment(self):
        os.environ["VECTOR_DB_PROVIDER"] = "pgvector"
        os.environ["VECTOR_DB_PGVECTOR_DSN"] = "postgresql://user:pass@localhost:5432/legacy"
        os.environ["GRAPH_DB_PROVIDER"] = "neo4j"
        os.environ["GRAPH_DB_NEO4J_URI"] = "bolt://localhost:7687"
        os.environ["DOCUMENT_DB_PROVIDER"] = "postgres_jsonb"
        os.environ["DOCUMENT_DB_POSTGRES_DSN"] = "postgresql://user:pass@localhost:5432/legacy"

        cfg = load_database_config()

        self.assertEqual(cfg.vector_provider, "pgvector")
        self.assertEqual(cfg.graph_provider, "neo4j")
        self.assertEqual(cfg.document_provider, "postgres_jsonb")
        self.assertIn("legacy", cfg.vector_pg_dsn)
        self.assertIn("legacy", cfg.document_pg_dsn)


if __name__ == "__main__":
    unittest.main()
