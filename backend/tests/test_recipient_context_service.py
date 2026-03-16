import os
import sys
import tempfile
import unittest
import uuid
from datetime import date, datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.ai.conversation_engine import ConversationEngine
from services.ai.recipient_context_service import RecipientContextService
from services.memory.memory_embedding_service import MemoryEmbeddingService
from services.memory_capture_service import MemoryCaptureService
from services.timeline_engine import TimelineEngine


class TestRecipientContextService(unittest.TestCase):

    def setUp(self):
        self.service = RecipientContextService()

    def test_create_and_retrieve_profile(self):
        profile = self.service.create_recipient_profile(
            user_id="child_01",
            name="Omid",
            relationship="son",
            age=10,
        )

        self.assertEqual(profile["user_id"], "child_01")
        self.assertEqual(profile["relationship"], "son")
        self.assertEqual(profile["maturity_level"], "child")
        loaded = self.service.retrieve_recipient_profile("child_01")
        self.assertEqual(loaded["name"], "Omid")

    def test_update_profile_recomputes_maturity(self):
        self.service.create_recipient_profile(
            user_id="friend_01",
            name="Sara",
            relationship="friend",
            age=17,
        )

        updated = self.service.update_recipient_profile(
            "friend_01",
            {
                "age": 26,
                "topic_preferences": ["career", "family"],
            },
        )

        self.assertEqual(updated["maturity_level"], "adult")
        self.assertEqual(updated["topic_preferences"], ["career", "family"])

    def test_determine_maturity_level_thresholds(self):
        self.assertEqual(self.service.determine_maturity_level(8), "child")
        self.assertEqual(self.service.determine_maturity_level(15), "teen")
        self.assertEqual(self.service.determine_maturity_level(22), "young_adult")
        self.assertEqual(self.service.determine_maturity_level(40), "adult")

    def test_conversation_engine_simplifies_sensitive_topics_for_children(self):
        memory_service = MemoryCaptureService()
        timeline_engine = TimelineEngine(memory_service, birth_date=date(1970, 1, 1))
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_recipient_test_{uuid.uuid4().hex}.json"
        )
        embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)
        recipient_service = RecipientContextService()

        recipient_service.create_recipient_profile(
            user_id="child_01",
            name="Omid",
            relationship="son",
            age=10,
        )

        memory_id = memory_service.create_memory(
            title="Hospital recovery",
            description="A difficult medical treatment period that required resilience.",
            timestamp=datetime(2018, 2, 14),
            tags=["family"],
            emotions=["fear", "hope"],
            sensitivity_tags=["medical"],
        )
        embedding_service.store_memory_embedding(memory_id, "hospital recovery")
        embedding_service.search_similar_memories = lambda _query, top_k=5: [
            (memory_id, 0.95),
        ][:top_k]

        engine = ConversationEngine(
            memory_service=memory_service,
            timeline_engine=timeline_engine,
            embedding_service=embedding_service,
            recipient_context_service=recipient_service,
        )

        result = engine.generate_response(
            user_query="Can you tell me what happened during that hospital period?",
            user_id="child_01",
        )

        self.assertIn("simple and safe", result["generated_answer"].lower())
        self.assertEqual(result["recipient_context"]["maturity_level"], "child")


if __name__ == "__main__":
    unittest.main()
