import os
import sys
import unittest
import tempfile
import uuid
from datetime import datetime, date

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.memory_capture_service import MemoryCaptureService
from services.timeline_engine import TimelineEngine
from services.memory.memory_embedding_service import MemoryEmbeddingService
from services.ai.memory_priority_service import MemoryPriorityService
from services.ai.conversation_engine import ConversationEngine
from utils.test_logger import test_logger


class TestMemoryPriorityService(unittest.TestCase):

    def setUp(self):
        self.priority_service = MemoryPriorityService()
        self.memory_service = MemoryCaptureService()

    def test_calculate_importance_rewards_milestones_and_tags(self):
        memory_id = self.memory_service.create_memory(
            title="First Promotion",
            description="A major career milestone that changed our family life.",
            timestamp=datetime(2012, 5, 1),
            tags=["career", "milestone", "family", "lesson"],
            emotions=["pride", "joy"],
            people_involved=["Sara", "Amin", "Mona"],
        )
        memory = self.memory_service.retrieve_memory(memory_id)

        score = self.priority_service.calculate_importance(memory)
        self.assertGreaterEqual(score, 0.75)

    def test_calculate_emotional_weight_uses_intensity(self):
        strong_id = self.memory_service.create_memory(
            title="Funeral Day",
            description="A deeply emotional and difficult day.",
            timestamp=datetime(2015, 7, 3),
            emotions=["grief", "sadness", "regret"],
            tags=["family"],
        )
        mild_id = self.memory_service.create_memory(
            title="Normal Workday",
            description="Routine tasks and meetings.",
            timestamp=datetime(2015, 7, 4),
            emotions=["nervous"],
            tags=["career"],
        )

        strong = self.priority_service.calculate_emotional_weight(
            self.memory_service.retrieve_memory(strong_id)
        )
        mild = self.priority_service.calculate_emotional_weight(
            self.memory_service.retrieve_memory(mild_id)
        )
        self.assertGreater(strong, mild)

    def test_rank_memories_orders_by_priority_formula(self):
        top_id = self.memory_service.create_memory(
            title="Wedding Day",
            description="One of the most important family milestones.",
            timestamp=datetime.now(),
            emotions=["love", "joy", "gratitude"],
            tags=["family", "milestone", "lesson"],
            people_involved=["Partner", "Parents", "Friends"],
        )
        low_id = self.memory_service.create_memory(
            title="Routine Errand",
            description="Bought groceries after work.",
            timestamp=datetime(2001, 4, 5),
            emotions=["nervous"],
            tags=["daily"],
        )

        ranked = self.priority_service.rank_memories(
            [
                self.memory_service.retrieve_memory(low_id),
                self.memory_service.retrieve_memory(top_id),
            ]
        )

        self.assertEqual(ranked[0]["memory"].id, top_id)
        self.assertGreaterEqual(ranked[0]["priority_score"], ranked[1]["priority_score"])
        test_logger.log_test_result(
            test_name="MemoryPriorityService.rank_memories_orders_by_priority",
            input_params={"candidate_count": 2},
            expected_result={"top_memory_id": top_id},
            actual_result={"top_memory_id": ranked[0]["memory"].id},
            status="PASS",
        )

    def test_conversation_engine_uses_priority_order_for_memories(self):
        timeline_engine = TimelineEngine(self.memory_service, birth_date=date(1970, 1, 1))
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_priority_test_{uuid.uuid4().hex}.json"
        )
        embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)

        high_id = self.memory_service.create_memory(
            title="Family Graduation Celebration",
            description="A major family milestone full of joy and pride.",
            timestamp=datetime(2019, 6, 1),
            emotions=["joy", "pride", "gratitude"],
            tags=["family", "milestone", "lesson"],
            people_involved=["Family", "Friends", "Mentor"],
        )
        low_id = self.memory_service.create_memory(
            title="Office Coffee Break",
            description="A short routine pause between meetings.",
            timestamp=datetime(2019, 6, 2),
            emotions=["nervous"],
            tags=["career"],
        )

        # Store embeddings so IDs exist in vector store, then patch deterministic order.
        embedding_service.store_memory_embedding(high_id, "high")
        embedding_service.store_memory_embedding(low_id, "low")
        embedding_service.search_similar_memories = lambda _query, top_k=5: [
            (low_id, 0.99),
            (high_id, 0.75),
        ][:top_k]

        engine = ConversationEngine(
            memory_service=self.memory_service,
            timeline_engine=timeline_engine,
            embedding_service=embedding_service,
            memory_priority_service=self.priority_service,
        )

        result = engine.generate_response("Tell me about important moments")

        self.assertGreaterEqual(len(result["memories_used"]), 2)
        self.assertEqual(result["memories_used"][0], high_id)


if __name__ == "__main__":
    unittest.main()
