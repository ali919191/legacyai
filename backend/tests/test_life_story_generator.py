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
from services.ai.life_story_generator import LifeStoryGenerator, LifeStory, LifeStageSummary
from utils.test_logger import test_logger


def _make_engine_with_memories():
    """Helper: return (memory_service, timeline_engine) with a few seeded memories."""
    ms = MemoryCaptureService()
    te = TimelineEngine(ms, birth_date=date(1970, 1, 1))
    ms.create_memory(
        title="Childhood Adventure",
        description="I learned to ride a bike and discovered that falling down was part of learning.",
        timestamp=datetime(1978, 5, 1),
        emotions=["joy", "pride"],
        tags=["childhood", "milestone"],
        people_involved=["Dad"],
        location="Backyard",
    )
    ms.create_memory(
        title="University Graduation",
        description="Graduated with honours. I realized hard work always pays off.",
        timestamp=datetime(1993, 6, 15),
        emotions=["pride", "gratitude"],
        tags=["graduation", "education", "milestone"],
        people_involved=["Mum", "Dad", "Professor Smith"],
        location="University Hall",
    )
    ms.create_memory(
        title="First Job",
        description="Started my career at a small engineering firm. Exciting and terrifying at the same time.",
        timestamp=datetime(1994, 3, 1),
        emotions=["excitement", "fear"],
        tags=["career", "job"],
        people_involved=["Manager Alice"],
        location="Downtown Office",
    )
    return ms, te


class TestLifeStoryGenerator(unittest.TestCase):

    def setUp(self):
        self.memory_service, self.timeline_engine = _make_engine_with_memories()
        self.generator = LifeStoryGenerator(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
        )

    def test_generate_life_story_returns_life_story_object(self):
        story = self.generator.generate_life_story(user_id="user_001")
        self.assertIsInstance(story, LifeStory)
        self.assertEqual(story.user_id, "user_001")
        self.assertIsNotNone(story.full_narrative)
        self.assertGreater(len(story.memories_used), 0)
        test_logger.log_test_result(
            test_name="LifeStoryGenerator.generate_life_story_returns_object",
            input_params={"user_id": "user_001"},
            expected_result={"type": "LifeStory", "memories_used>0": True},
            actual_result={
                "type": type(story).__name__,
                "memories_used": len(story.memories_used),
            },
            status="PASS",
        )

    def test_full_narrative_contains_memory_titles(self):
        story = self.generator.generate_life_story(user_id="user_001")
        self.assertIn("Childhood Adventure", story.full_narrative)
        self.assertIn("University Graduation", story.full_narrative)
        test_logger.log_test_result(
            test_name="LifeStoryGenerator.full_narrative_contains_titles",
            input_params={"user_id": "user_001"},
            expected_result={"contains_childhood": True, "contains_graduation": True},
            actual_result={
                "contains_childhood": "Childhood Adventure" in story.full_narrative,
                "contains_graduation": "University Graduation" in story.full_narrative,
            },
            status="PASS",
        )

    def test_generate_life_stage_summary_childhood(self):
        summary = self.generator.generate_life_stage_summary("childhood")
        self.assertIsInstance(summary, LifeStageSummary)
        self.assertEqual(summary.stage_name, "childhood")
        self.assertEqual(summary.memory_count, 1)
        test_logger.log_test_result(
            test_name="LifeStoryGenerator.generate_life_stage_summary_childhood",
            input_params={"stage": "childhood"},
            expected_result={"stage_name": "childhood", "memory_count": 1},
            actual_result={"stage_name": summary.stage_name, "memory_count": summary.memory_count},
            status="PASS",
        )

    def test_generate_life_stage_summary_nonexistent_returns_none(self):
        summary = self.generator.generate_life_stage_summary("retirement")
        self.assertIsNone(summary)
        test_logger.log_test_result(
            test_name="LifeStoryGenerator.generate_life_stage_summary_nonexistent",
            input_params={"stage": "retirement"},
            expected_result={"result": None},
            actual_result={"result": summary},
            status="PASS",
        )

    def test_compile_chronological_narrative_empty(self):
        narrative = self.generator.compile_chronological_narrative([])
        self.assertIn("No memories", narrative)
        test_logger.log_test_result(
            test_name="LifeStoryGenerator.compile_chronological_narrative_empty",
            input_params={"memories": []},
            expected_result={"contains_no_memories_text": True},
            actual_result={"narrative_snippet": narrative[:50]},
            status="PASS",
        )

    def test_generate_life_story_empty_memories_returns_placeholder(self):
        empty_ms = MemoryCaptureService()
        empty_te = TimelineEngine(empty_ms, birth_date=date(1970, 1, 1))
        generator = LifeStoryGenerator(memory_service=empty_ms, timeline_engine=empty_te)
        story = generator.generate_life_story(user_id="empty_user")
        self.assertEqual(story.user_id, "empty_user")
        self.assertIn("No memories", story.full_narrative)
        test_logger.log_test_result(
            test_name="LifeStoryGenerator.generate_life_story_empty_memories",
            input_params={"user_id": "empty_user"},
            expected_result={"contains_no_memories_text": True},
            actual_result={"narrative_snippet": story.full_narrative[:60]},
            status="PASS",
        )


if __name__ == "__main__":
    unittest.main()
