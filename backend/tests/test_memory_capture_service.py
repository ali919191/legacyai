import os
import sys
import unittest
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.memory_capture_service import MemoryCaptureService
from utils.test_logger import test_logger


class TestMemoryCaptureService(unittest.TestCase):

    def setUp(self):
        self.service = MemoryCaptureService()

    def test_create_memory_returns_id(self):
        memory_id = self.service.create_memory(
            title="First Day of School",
            description="I was nervous but made a great friend named Tom.",
            timestamp=datetime(1985, 9, 1),
            people_involved=["Tom"],
            location="Springfield Elementary",
            emotions=["nervous", "joy"],
            tags=["childhood", "school"],
        )
        self.assertIsNotNone(memory_id)
        self.assertIsInstance(memory_id, str)
        test_logger.log_test_result(
            test_name="MemoryCaptureService.create_memory_returns_id",
            input_params={"title": "First Day of School"},
            expected_result={"memory_id": "non-null string"},
            actual_result={"memory_id": memory_id},
            status="PASS",
        )

    def test_retrieve_memory_by_id(self):
        memory_id = self.service.create_memory(
            title="Summer Holiday",
            description="Camping with the family.",
            timestamp=datetime(1990, 7, 15),
        )
        memory = self.service.retrieve_memory(memory_id)
        self.assertIsNotNone(memory)
        self.assertEqual(memory.title, "Summer Holiday")
        test_logger.log_test_result(
            test_name="MemoryCaptureService.retrieve_memory_by_id",
            input_params={"memory_id": memory_id},
            expected_result={"title": "Summer Holiday"},
            actual_result={"title": memory.title},
            status="PASS",
        )

    def test_retrieve_nonexistent_memory_returns_none(self):
        result = self.service.retrieve_memory("nonexistent-id")
        self.assertIsNone(result)
        test_logger.log_test_result(
            test_name="MemoryCaptureService.retrieve_nonexistent_memory",
            input_params={"memory_id": "nonexistent-id"},
            expected_result={"result": None},
            actual_result={"result": result},
            status="PASS",
        )

    def test_update_memory_title(self):
        memory_id = self.service.create_memory(
            title="Old Title",
            description="Some description.",
            timestamp=datetime(2000, 1, 1),
        )
        success = self.service.update_memory(memory_id, title="New Title")
        updated = self.service.retrieve_memory(memory_id)
        self.assertTrue(success)
        self.assertEqual(updated.title, "New Title")
        test_logger.log_test_result(
            test_name="MemoryCaptureService.update_memory_title",
            input_params={"memory_id": memory_id, "new_title": "New Title"},
            expected_result={"success": True, "updated_title": "New Title"},
            actual_result={"success": success, "updated_title": updated.title},
            status="PASS",
        )

    def test_delete_memory(self):
        memory_id = self.service.create_memory(
            title="To Be Deleted",
            description="This will be removed.",
            timestamp=datetime(2005, 3, 10),
        )
        deleted = self.service.delete_memory(memory_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.service.retrieve_memory(memory_id))
        test_logger.log_test_result(
            test_name="MemoryCaptureService.delete_memory",
            input_params={"memory_id": memory_id},
            expected_result={"deleted": True, "retrieval_after_delete": None},
            actual_result={"deleted": deleted, "retrieval_after_delete": self.service.retrieve_memory(memory_id)},
            status="PASS",
        )

    def test_retrieve_all_memories(self):
        self.service.create_memory(title="First", description="A", timestamp=datetime(2001, 1, 1))
        self.service.create_memory(title="Second", description="B", timestamp=datetime(2002, 2, 2))
        all_memories = self.service.retrieve_all_memories()
        self.assertEqual(len(all_memories), 2)
        titles = {m.title for m in all_memories}
        self.assertIn("First", titles)
        self.assertIn("Second", titles)
        test_logger.log_test_result(
            test_name="MemoryCaptureService.retrieve_all_memories",
            input_params={"created_count": 2},
            expected_result={"count": 2},
            actual_result={"count": len(all_memories)},
            status="PASS",
        )


if __name__ == "__main__":
    unittest.main()
