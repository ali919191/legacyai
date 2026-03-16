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


class TestKnowledgeGapService(unittest.TestCase):

    def setUp(self):
        self.memory_service = MemoryCaptureService()
        self.timeline_engine = TimelineEngine(self.memory_service, birth_date=date(1970, 1, 1))
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_kg_test_{uuid.uuid4().hex}.json"
        )
        self.embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)
        self.knowledge_gap_service = KnowledgeGapService(self.memory_service)

        self.memory_id = self.memory_service.create_memory(
            title="First IT Job",
            description="I joined a small IT support company and learned fast.",
            timestamp=datetime(1994, 3, 1, 9, 0),
            people_involved=["Sarah"],
            location="City office",
            emotions=["excitement"],
            tags=["career", "job"],
            day_of_week="Tuesday",
            time_of_day="morning",
            start_time="09:00",
            end_time="17:00",
        )
        self.embedding_service.store_memory_embedding(
            self.memory_id,
            "First IT Job I joined a small IT support company and learned fast.",
        )

    def test_detect_and_generate_followup_questions(self):
        context = self.knowledge_gap_service.detect_missing_context(
            "I remember Mike helping me on that day during my first IT job."
        )
        generated = self.knowledge_gap_service.generate_followup_questions(context)

        self.assertGreater(len(generated), 0)
        self.assertTrue(any("Who was Mike" in q["question"] for q in generated))

    def test_store_and_retrieve_pending_questions(self):
        record = self.knowledge_gap_service.store_question(
            {
                "question": "Who was Mike?",
                "related_memory_id": self.memory_id,
                "source_conversation_timestamp": datetime.now().isoformat(),
                "context_description": "User mentioned Mike during a story about first IT job",
                "priority": "medium",
                "status": "pending",
                "user_id": "child_user",
            }
        )

        self.assertIn("question_id", record)
        pending = self.knowledge_gap_service.retrieve_pending_questions("child_user")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["status"], "pending")

    def test_answer_question_updates_memory_and_status(self):
        record = self.knowledge_gap_service.store_question(
            {
                "question": "Who was Mike?",
                "related_memory_id": self.memory_id,
                "source_conversation_timestamp": datetime.now().isoformat(),
                "context_description": "Missing context",
                "priority": "medium",
                "status": "pending",
                "user_id": "child_user",
            }
        )

        resolved = self.knowledge_gap_service.answer_question(
            question_id=record["question_id"],
            answer_text="Mike was my teammate from network operations.",
            memory_updates={"people_involved": ["Sarah", "Mike"]},
        )

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["status"], "answered")
        updated_memory = self.memory_service.retrieve_memory(self.memory_id)
        self.assertIn("Mike", updated_memory.people_involved)

    def test_conversation_engine_triggers_enhanced_questions(self):
        engine = ConversationEngine(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
            embedding_service=self.embedding_service,
            knowledge_gap_service=self.knowledge_gap_service,
        )

        result = engine.generate_response(
            "My friend Mike helped me solve a server outage later that day.",
            user_id="child_user",
        )

        self.assertIn("enhanced_questions", result)
        self.assertGreater(len(result["enhanced_questions"]), 0)
        pending = self.knowledge_gap_service.retrieve_pending_questions("child_user")
        self.assertGreater(len(pending), 0)


if __name__ == "__main__":
    unittest.main()
