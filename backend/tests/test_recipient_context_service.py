import os
import sys
import tempfile
import unittest
import uuid
import json
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
        self.store_path = os.path.join(
            tempfile.gettempdir(), f"legacyai_recipient_profiles_{uuid.uuid4().hex}.json"
        )
        self.service = RecipientContextService(data_store_path=self.store_path)

    def test_create_and_retrieve_profile(self):
        profile = self.service.create_recipient_profile(
            user_id="child_01",
            name="Omid",
            relationship="son",
            age=10,
        )

        self.assertEqual(profile["user_id"], "child_01")
        self.assertEqual(profile["relationship_to_user"], "son")
        self.assertEqual(profile["age_bucket"], "child")
        self.assertEqual(profile["maturity_level"], "child")
        loaded = self.service.retrieve_recipient_profile("child_01")
        self.assertEqual(loaded["name"], "Omid")
        self.assertIn("interaction_history", loaded)

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
        self.assertEqual(updated["age_bucket"], "adult")
        self.assertEqual(updated["topic_preferences"], ["career", "family"])

    def test_determine_age_bucket_and_maturity_thresholds(self):
        self.assertEqual(self.service.determine_age_bucket(6), "young_child")
        self.assertEqual(self.service.determine_maturity_level(8), "child")
        self.assertEqual(self.service.determine_age_bucket(8), "child")
        self.assertEqual(self.service.determine_maturity_level(15), "teen")
        self.assertEqual(self.service.determine_age_bucket(15), "teenager")
        self.assertEqual(self.service.determine_maturity_level(22), "young_adult")
        self.assertEqual(self.service.determine_age_bucket(22), "young_adult")
        self.assertEqual(self.service.determine_maturity_level(40), "adult")
        self.assertEqual(self.service.determine_age_bucket(40), "adult")
        self.assertEqual(self.service.determine_age_bucket(55), "mature_adult")

    def test_extract_family_profiles_from_conversation_creates_children(self):
        created = self.service.extract_family_profiles_from_conversation(
            "I have two children, one is 10 and the other is 15"
        )

        self.assertEqual(len(created), 2)
        buckets = sorted(item["age_bucket"] for item in created)
        self.assertEqual(buckets, ["child", "teenager"])

        with open(self.store_path, "r", encoding="utf-8") as fp:
            persisted = json.load(fp)
        self.assertEqual(len(persisted.keys()), 2)

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
        self.assertEqual(result["recipient_context"]["age_bucket"], "child")


if __name__ == "__main__":
    unittest.main()
