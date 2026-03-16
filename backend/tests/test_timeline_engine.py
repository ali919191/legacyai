import os
import sys
import unittest
from datetime import datetime, date

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.memory_capture_service import MemoryCaptureService
from services.timeline_engine import TimelineEngine
from utils.test_logger import test_logger


class TestTimelineEngine(unittest.TestCase):

    def setUp(self):
        self.memory_service = MemoryCaptureService()
        # Birth date: 1970-01-01  →  childhood ends ~1982, education ~1983-1992, career 1993+
        self.birth_date = date(1970, 1, 1)
        self.engine = TimelineEngine(self.memory_service, self.birth_date)

        # Seed memories across life stages
        self.memory_service.create_memory(
            title="Childhood Memory",
            description="Playing in the backyard.",
            timestamp=datetime(1978, 6, 1),  # age 8 → childhood
            emotions=["joy"],
            tags=["childhood"],
        )
        self.memory_service.create_memory(
            title="University Memory",
            description="Studying for finals.",
            timestamp=datetime(1990, 4, 15),  # age 20 → education
            emotions=["stress"],
            tags=["education"],
        )
        self.memory_service.create_memory(
            title="Career Memory",
            description="First day at a new job.",
            timestamp=datetime(2000, 3, 10),  # age 30 → career
            emotions=["excitement"],
            tags=["career"],
        )

    def test_get_chronological_timeline_is_sorted(self):
        timeline = self.engine.get_chronological_timeline()
        self.assertEqual(len(timeline), 3)
        timestamps = [m.timestamp for m in timeline]
        self.assertEqual(timestamps, sorted(timestamps))
        test_logger.log_test_result(
            test_name="TimelineEngine.get_chronological_timeline_is_sorted",
            input_params={"memory_count": 3},
            expected_result={"sorted": True},
            actual_result={"sorted": timestamps == sorted(timestamps)},
            status="PASS",
        )

    def test_group_by_life_stage_assigns_correctly(self):
        grouped = self.engine.group_by_life_stage()
        self.assertEqual(len(grouped["childhood"]), 1)
        self.assertEqual(grouped["childhood"][0].title, "Childhood Memory")
        self.assertEqual(len(grouped["education"]), 1)
        self.assertEqual(grouped["education"][0].title, "University Memory")
        self.assertEqual(len(grouped["career"]), 1)
        self.assertEqual(grouped["career"][0].title, "Career Memory")
        test_logger.log_test_result(
            test_name="TimelineEngine.group_by_life_stage_assigns_correctly",
            input_params={"birth_date": str(self.birth_date)},
            expected_result={"childhood": 1, "education": 1, "career": 1},
            actual_result={
                "childhood": len(grouped["childhood"]),
                "education": len(grouped["education"]),
                "career": len(grouped["career"]),
            },
            status="PASS",
        )

    def test_query_by_date_range(self):
        results = self.engine.query_by_date_range(
            datetime(1975, 1, 1),
            datetime(1995, 12, 31),
        )
        titles = {m.title for m in results}
        self.assertIn("Childhood Memory", titles)
        self.assertIn("University Memory", titles)
        self.assertNotIn("Career Memory", titles)
        test_logger.log_test_result(
            test_name="TimelineEngine.query_by_date_range",
            input_params={"start": "1975-01-01", "end": "1995-12-31"},
            expected_result={"count": 2, "titles": ["Childhood Memory", "University Memory"]},
            actual_result={"count": len(results), "titles": list(titles)},
            status="PASS",
        )

    def test_query_by_life_stage_career(self):
        career_memories = self.engine.query_by_life_stage("career")
        self.assertEqual(len(career_memories), 1)
        self.assertEqual(career_memories[0].title, "Career Memory")
        test_logger.log_test_result(
            test_name="TimelineEngine.query_by_life_stage_career",
            input_params={"stage": "career"},
            expected_result={"count": 1, "title": "Career Memory"},
            actual_result={"count": len(career_memories), "title": career_memories[0].title},
            status="PASS",
        )

    def test_query_by_unknown_life_stage_returns_empty(self):
        result = self.engine.query_by_life_stage("invalid_stage")
        self.assertEqual(result, [])
        test_logger.log_test_result(
            test_name="TimelineEngine.query_by_unknown_life_stage_returns_empty",
            input_params={"stage": "invalid_stage"},
            expected_result={"result": []},
            actual_result={"result": result},
            status="PASS",
        )


if __name__ == "__main__":
    unittest.main()
