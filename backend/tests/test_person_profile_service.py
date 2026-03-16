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

from services.memory_capture_service import MemoryCaptureService
from services.timeline_engine import TimelineEngine
from services.memory.memory_embedding_service import MemoryEmbeddingService
from services.ai.conversation_engine import ConversationEngine
from services.ai.knowledge_gap_service import KnowledgeGapService
from services.entity.person_profile_service import PersonProfileService


class TestPersonProfileService(unittest.TestCase):

    def setUp(self):
        self.memory_service = MemoryCaptureService()
        self.person_profile_service = PersonProfileService(memory_service=self.memory_service)
        self.memory_service.set_person_profile_service(self.person_profile_service)
        self.timeline_engine = TimelineEngine(self.memory_service, birth_date=date(1970, 1, 1))
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_person_test_{uuid.uuid4().hex}.json"
        )
        self.embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)
        self.knowledge_gap_service = KnowledgeGapService(
            memory_service=self.memory_service,
            person_profile_service=self.person_profile_service,
        )

    def test_create_and_search_partial_profile(self):
        created = self.person_profile_service.create_person_profile("Sarah")
        self.assertTrue(created["person_id"].startswith("person_"))
        self.assertIsNone(created["relationship_to_user"])

        matches = self.person_profile_service.search_person_by_name("Sarah")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Sarah")

    def test_update_profile_merges_details(self):
        created = self.person_profile_service.create_person_profile("Mike")
        updated = self.person_profile_service.update_person_profile(
            created["person_id"],
            {
                "relationship_to_user": "friend",
                "origin": "First IT job",
                "age": 29,
                "children": ["Ella"],
                "description": "Network operations teammate",
                "confidence_score": 0.8,
            },
        )

        self.assertEqual(updated["relationship_to_user"], "friend")
        self.assertEqual(updated["age"], 29)
        self.assertIn("Ella", updated["children"])
        self.assertEqual(updated["confidence_score"], 0.8)

    def test_memory_creation_auto_syncs_person_profiles(self):
        memory_id = self.memory_service.create_memory(
            title="Started my first job",
            description="Sarah helped me learn the ticketing system.",
            timestamp=datetime(1994, 3, 1, 9, 0),
            people_involved=["Sarah"],
            location="City office",
            emotions=["nervous", "grateful"],
            tags=["career"],
        )

        matches = self.person_profile_service.search_person_by_name("Sarah")
        self.assertEqual(len(matches), 1)
        self.assertIn(memory_id, matches[0]["connected_memories"])
        self.assertGreaterEqual(matches[0]["confidence_score"], 0.5)

    def test_knowledge_gap_creates_temporary_profile_for_unknown_person(self):
        context = self.knowledge_gap_service.detect_missing_context(
            "Then Mike showed up and helped me fix the router."
        )
        self.assertTrue(any(person["name"] == "Mike" for person in context["unknown_people"]))

        matches = self.person_profile_service.search_person_by_name("Mike")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["origin"], "Detected in conversation")

    def test_conversation_engine_resolution_updates_profile(self):
        memory_id = self.memory_service.create_memory(
            title="Server outage night",
            description="We worked late to restore service.",
            timestamp=datetime(1998, 6, 12, 21, 0),
            people_involved=["Sarah"],
            location="Data center",
            emotions=["stress", "relief"],
            tags=["career"],
        )
        self.embedding_service.store_memory_embedding(memory_id, "Server outage night We worked late")

        engine = ConversationEngine(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
            embedding_service=self.embedding_service,
            person_profile_service=self.person_profile_service,
            knowledge_gap_service=self.knowledge_gap_service,
        )

        result = engine.generate_response(
            "Mike helped me during the outage later that night.",
            user_id="child_user",
        )
        self.assertGreater(len(result["enhanced_questions"]), 0)

        question = result["enhanced_questions"][0]
        resolved = engine.answer_enhanced_question(
            question_id=question["question_id"],
            answer_text="Mike was my teammate from network operations.",
            person_updates={
                "relationship_to_user": "coworker",
                "description": "Network operations teammate",
                "confidence_score": 0.85,
            },
        )

        self.assertEqual(resolved["status"], "answered")
        mike_profile = self.person_profile_service.search_person_by_name("Mike")[0]
        self.assertEqual(mike_profile["relationship_to_user"], "coworker")
        self.assertEqual(mike_profile["confidence_score"], 0.85)


if __name__ == "__main__":
    unittest.main()
