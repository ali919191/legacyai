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
from services.ai.memory_distillation_service import MemoryDistillationService
from services.ai.wisdom_engine import WisdomEngine
from services.memory.memory_embedding_service import MemoryEmbeddingService
from services.memory_capture_service import MemoryCaptureService
from services.timeline_engine import TimelineEngine


class TestWisdomEngine(unittest.TestCase):

    def setUp(self):
        self.memory_service = MemoryCaptureService()
        self.timeline_engine = TimelineEngine(self.memory_service, birth_date=date(1970, 1, 1))
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_wisdom_test_{uuid.uuid4().hex}.json"
        )
        self.embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)
        self.wisdom_engine = WisdomEngine()
        self.distillation_service = MemoryDistillationService(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
            embedding_service=self.embedding_service,
            wisdom_engine=self.wisdom_engine,
        )

    def test_extract_lesson_from_failure_memory(self):
        memory_id = self.memory_service.create_memory(
            title="Missed promotion",
            description="I regret not advocating for myself and learning from that setback.",
            timestamp=datetime(1998, 4, 3),
            tags=["career", "regret"],
            emotions=["disappointment", "determination"],
        )
        memory = self.memory_service.retrieve_memory(memory_id)

        lesson = self.wisdom_engine.extract_lesson(memory)
        self.assertEqual(lesson["category"], "failure")
        self.assertIn("setbacks", lesson["lesson"].lower())

    def test_identify_patterns_finds_common_categories(self):
        first = self.memory_service.create_memory(
            title="Graduation day",
            description="A proud milestone after years of discipline.",
            timestamp=datetime(1990, 6, 1),
            tags=["education", "milestone"],
            emotions=["pride", "joy"],
        )
        second = self.memory_service.create_memory(
            title="First major client win",
            description="A successful project that came from consistent preparation.",
            timestamp=datetime(1995, 8, 1),
            tags=["career", "success"],
            emotions=["gratitude", "pride"],
        )

        patterns = self.wisdom_engine.identify_patterns(
            [
                self.memory_service.retrieve_memory(first),
                self.memory_service.retrieve_memory(second),
            ]
        )

        self.assertGreaterEqual(len(patterns), 1)
        self.assertGreaterEqual(patterns[0]["count"], 1)

    def test_generate_principle_from_mixed_lessons(self):
        lessons = [
            {
                "memory_id": "1",
                "category": "failure",
                "lesson": "Learn from setbacks.",
            },
            {
                "memory_id": "2",
                "category": "success",
                "lesson": "Consistency creates momentum.",
            },
        ]

        principles = self.wisdom_engine.generate_principle(lessons)
        self.assertGreaterEqual(len(principles), 2)
        self.assertTrue(any("setbacks" in principle.lower() for principle in principles))

    def test_conversation_engine_generates_advice_for_advice_question(self):
        high_id = self.memory_service.create_memory(
            title="Career setback and recovery",
            description=(
                "I failed to secure a promotion, then I asked for feedback, upskilled, "
                "and succeeded the following year."
            ),
            timestamp=datetime(2001, 9, 1),
            tags=["career", "regret", "milestone"],
            emotions=["disappointment", "determination", "pride"],
        )
        low_id = self.memory_service.create_memory(
            title="Routine office lunch",
            description="A normal lunch break with the team.",
            timestamp=datetime(2002, 1, 10),
            tags=["daily"],
            emotions=["calm"],
        )

        self.embedding_service.store_memory_embedding(high_id, "high")
        self.embedding_service.store_memory_embedding(low_id, "low")
        self.embedding_service.search_similar_memories = lambda _query, top_k=5: [
            (high_id, 0.95),
            (low_id, 0.70),
        ][:top_k]

        engine = ConversationEngine(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
            embedding_service=self.embedding_service,
            distillation_service=self.distillation_service,
        )

        result = engine.generate_response("What advice would you give me for career setbacks?")

        self.assertIn("Based on what life taught me", result["generated_answer"])
        self.assertGreater(len(result["memories_used"]), 0)
        self.assertGreater(len(result["lessons_used"]), 0)
        self.assertGreater(len(result["wisdom_principles"]), 0)


if __name__ == "__main__":
    unittest.main()
