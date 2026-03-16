import os
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, date

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.ai.conversation_engine import ConversationEngine
from services.ai.memory_grounding_service import MemoryGroundingService
from services.memory.memory_embedding_service import MemoryEmbeddingService
from services.memory_capture_service import MemoryCaptureService
from services.timeline_engine import TimelineEngine


class TestMemoryGroundingService(unittest.TestCase):

    def setUp(self):
        self.memory_service = MemoryCaptureService()
        self.timeline_engine = TimelineEngine(self.memory_service, birth_date=date(1970, 1, 1))
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_grounding_test_{uuid.uuid4().hex}.json"
        )
        self.embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)
        self.grounding_service = MemoryGroundingService()

    def test_build_context_packet_contains_memory_facts(self):
        memory_id = self.memory_service.create_memory(
            title="School play",
            description="I performed in the annual school play.",
            timestamp=datetime(1985, 5, 1),
            people_involved=["Teacher"],
            location="School hall",
            emotions=["joy"],
            tags=["school"],
        )
        memory = self.memory_service.retrieve_memory(memory_id)

        packet = self.grounding_service.build_context_packet([memory])
        self.assertEqual(packet["memory_count"], 1)
        self.assertEqual(packet["memory_ids"], [memory_id])
        self.assertEqual(packet["grounded_facts"][0]["title"], "School play")

    def test_validate_memory_sources_filters_invalid(self):
        valid_id = self.memory_service.create_memory(
            title="Family picnic",
            description="We spent the day by the river.",
            timestamp=datetime(1990, 6, 1),
            tags=["family"],
            emotions=["joy"],
        )
        valid_memory = self.memory_service.retrieve_memory(valid_id)

        class InvalidMemory:
            id = "bad"
            title = ""
            description = ""
            timestamp = None

        validated = self.grounding_service.validate_memory_sources([valid_memory, InvalidMemory()])
        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0].id, valid_id)

    def test_generate_grounded_prompt_contains_strict_instruction(self):
        memory_id = self.memory_service.create_memory(
            title="First job",
            description="I started at a small office downtown.",
            timestamp=datetime(1993, 2, 1),
            tags=["career"],
            emotions=["nervous"],
        )
        memory = self.memory_service.retrieve_memory(memory_id)

        prompt = self.grounding_service.generate_grounded_prompt(
            "Where did you first work?",
            [memory],
        )
        self.assertIn("Answer using ONLY the supplied memory evidence", prompt)
        self.assertIn(memory_id, prompt)

    def test_conversation_engine_fallback_on_missing_memories(self):
        engine = ConversationEngine(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
            embedding_service=self.embedding_service,
            memory_grounding_service=self.grounding_service,
        )

        result = engine.generate_response("What happened during your graduation?")
        self.assertEqual(result["generated_answer"], "I don't remember that clearly.")
        self.assertEqual(result["memories_used"], [])


if __name__ == "__main__":
    unittest.main()
