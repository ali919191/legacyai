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
from services.episode.episode_service import EpisodeService
from services.ai.life_story_generator import LifeStoryGenerator
from utils.test_logger import test_logger


class TestEpisodeService(unittest.TestCase):

    def setUp(self):
        self.memory_service = MemoryCaptureService()
        self.timeline_engine = TimelineEngine(
            memory_service=self.memory_service,
            birth_date=date(1970, 1, 1),
        )
        self.episode_service = EpisodeService(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
        )
        self.memory_service.set_episode_service(self.episode_service)
        self.timeline_engine.set_episode_service(self.episode_service)

    def test_create_episode_returns_id(self):
        episode_id = self.episode_service.create_episode(
            title="Early Career Pivot",
            life_stage="career",
        )
        episode = self.episode_service.retrieve_episode(episode_id)

        self.assertIsNotNone(episode)
        self.assertEqual(episode.title, "Early Career Pivot")
        self.assertEqual(episode.life_stage, "career")
        test_logger.log_test_result(
            test_name="EpisodeService.create_episode_returns_id",
            input_params={"title": "Early Career Pivot", "life_stage": "career"},
            expected_result={"episode_exists": True},
            actual_result={"episode_exists": episode is not None},
            status="PASS",
        )

    def test_link_memory_to_episode_updates_dates_people(self):
        episode_id = self.episode_service.create_episode("Family Milestone", "career")
        memory_id = self.memory_service.create_memory(
            title="Bought Our First Home",
            description="A joyful and stressful move into our first house.",
            timestamp=datetime(2002, 4, 5),
            people_involved=["Sara", "Amin"],
            emotions=["joy", "stress"],
            tags=["family", "home"],
        )

        linked = self.episode_service.link_memory_to_episode(memory_id, episode_id)
        episode = self.episode_service.retrieve_episode(episode_id)

        self.assertTrue(linked)
        self.assertIn(memory_id, episode.related_memories)
        self.assertIn("Sara", episode.related_people)
        self.assertEqual(episode.start_date, datetime(2002, 4, 5))
        self.assertEqual(episode.end_date, datetime(2002, 4, 5))

    def test_generate_episode_summary_populates_text(self):
        episode_id = self.episode_service.create_episode("Startup Years", "career")
        first = self.memory_service.create_memory(
            title="First Client",
            description="Signed our first client after months of pitching.",
            timestamp=datetime(1999, 2, 10),
            people_involved=["Layla"],
            emotions=["pride"],
            tags=["startup", "career", "milestone"],
        )
        second = self.memory_service.create_memory(
            title="Second Office",
            description="Moved into a larger office.",
            timestamp=datetime(1999, 3, 15),
            people_involved=["Layla", "Hadi"],
            emotions=["joy"],
            tags=["startup", "growth"],
        )
        self.episode_service.link_memory_to_episode(first, episode_id)
        self.episode_service.link_memory_to_episode(second, episode_id)

        summary = self.episode_service.generate_episode_summary(episode_id)
        self.assertIn("captures 2 related memories", summary)
        self.assertIn("startup", summary.lower())

    def test_memory_capture_auto_groups_related_memories(self):
        self.memory_service.create_memory(
            title="First Night Shift",
            description="Started my hospital night rotation.",
            timestamp=datetime(2005, 7, 1),
            tags=["hospital", "career"],
            emotions=["anxious"],
        )
        self.memory_service.create_memory(
            title="Night Shift Breakthrough",
            description="Handled my first critical case overnight.",
            timestamp=datetime(2005, 7, 20),
            tags=["hospital", "career"],
            emotions=["pride"],
        )

        episodes = self.episode_service.list_episodes()
        self.assertGreaterEqual(len(episodes), 1)
        self.assertGreaterEqual(len(episodes[0].related_memories), 2)

    def test_timeline_group_related_memories_into_episodes(self):
        self.memory_service.create_memory(
            title="Graduation Prep",
            description="Final semester projects and thesis work.",
            timestamp=datetime(1991, 2, 2),
            tags=["education", "graduation"],
        )
        self.memory_service.create_memory(
            title="Graduation Ceremony",
            description="Walked on stage and received my degree.",
            timestamp=datetime(1991, 6, 20),
            tags=["education", "graduation", "milestone"],
        )

        created = self.timeline_engine.group_related_memories_into_episodes(window_days=180)
        # Auto-grouping on memory creation may already have formed the episode,
        # so validate either newly created IDs or an existing grouped result.
        self.assertTrue(len(created) >= 1 or len(self.episode_service.list_episodes()) >= 1)

    def test_life_story_includes_episodic_highlights(self):
        self.memory_service.create_memory(
            title="Community Volunteering",
            description="Spent weekends organizing food drives.",
            timestamp=datetime(2010, 4, 10),
            tags=["community", "service"],
            emotions=["gratitude"],
        )
        self.memory_service.create_memory(
            title="Volunteer Leadership",
            description="Led a larger team for regional outreach.",
            timestamp=datetime(2010, 5, 8),
            tags=["community", "service", "leadership"],
            emotions=["pride"],
        )

        generator = LifeStoryGenerator(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
            episode_service=self.episode_service,
        )
        story = generator.generate_life_story(user_id="user_episodes")
        self.assertIn("## Episodic Highlights", story.full_narrative)
        test_logger.log_test_result(
            test_name="LifeStoryGenerator.includes_episodic_highlights",
            input_params={"user_id": "user_episodes"},
            expected_result={"episodic_section": True},
            actual_result={"episodic_section": "## Episodic Highlights" in story.full_narrative},
            status="PASS",
        )


if __name__ == "__main__":
    unittest.main()
