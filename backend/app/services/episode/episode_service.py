from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from app.services.memory_capture_service import MemoryCaptureService, Memory


@dataclass
class Episode:
    """Represents a grouped period or event made of related memories."""

    episode_id: str
    title: str
    life_stage: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    summary: str = ""
    related_memories: List[str] = field(default_factory=list)
    related_people: List[str] = field(default_factory=list)
    importance_score: float = 0.0


class EpisodeService:
    """Service for managing episodic memory groupings."""

    def __init__(self, memory_service: MemoryCaptureService, timeline_engine: Optional[Any] = None):
        self.memory_service = memory_service
        self.timeline_engine = timeline_engine
        self.episodes: Dict[str, Episode] = {}

    def create_episode(
        self,
        title: str,
        life_stage: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        summary: str = "",
    ) -> str:
        """Create a new episode and return its ID."""
        episode_id = str(uuid.uuid4())
        self.episodes[episode_id] = Episode(
            episode_id=episode_id,
            title=title,
            life_stage=life_stage,
            start_date=start_date,
            end_date=end_date,
            summary=summary,
        )
        return episode_id

    def link_memory_to_episode(self, memory_id: str, episode_id: str) -> bool:
        """Attach a memory to an episode and refresh episode metadata."""
        episode = self.episodes.get(episode_id)
        memory = self.memory_service.retrieve_memory(memory_id)
        if not episode or not memory:
            return False

        if memory_id not in episode.related_memories:
            episode.related_memories.append(memory_id)

        if episode.start_date is None or memory.timestamp < episode.start_date:
            episode.start_date = memory.timestamp
        if episode.end_date is None or memory.timestamp > episode.end_date:
            episode.end_date = memory.timestamp

        known_people = set(episode.related_people)
        known_people.update(memory.people_involved)
        episode.related_people = sorted(known_people)

        episode.importance_score = self._calculate_importance(episode)
        return True

    def retrieve_episode(self, episode_id: str) -> Optional[Episode]:
        """Return an episode by ID."""
        return self.episodes.get(episode_id)

    def list_episode_memories(self, episode_id: str) -> List[Memory]:
        """Return full memory objects linked to a specific episode."""
        episode = self.episodes.get(episode_id)
        if not episode:
            return []

        memories = [
            memory
            for memory_id in episode.related_memories
            if (memory := self.memory_service.retrieve_memory(memory_id)) is not None
        ]
        return sorted(memories, key=lambda memory: memory.timestamp)

    def generate_episode_summary(self, episode_id: str) -> str:
        """Generate and persist a narrative summary for an episode."""
        episode = self.episodes.get(episode_id)
        if not episode:
            return ""

        memories = self.list_episode_memories(episode_id)
        if not memories:
            episode.summary = "No memories linked to this episode yet."
            episode.importance_score = 0.0
            return episode.summary

        tags = [tag.lower() for memory in memories for tag in memory.tags]
        top_tags = [tag for tag, _ in Counter(tags).most_common(3)]

        start_str = episode.start_date.strftime("%B %Y") if episode.start_date else "unknown start"
        end_str = episode.end_date.strftime("%B %Y") if episode.end_date else "unknown end"
        top_tag_str = ", ".join(top_tags) if top_tags else "shared life moments"
        people_str = ", ".join(episode.related_people[:5]) if episode.related_people else "key relationships"

        episode.summary = (
            f"{episode.title} captures {len(memories)} related memories from {start_str} to {end_str}. "
            f"The dominant themes include {top_tag_str}, with recurring people such as {people_str}."
        )
        episode.importance_score = self._calculate_importance(episode)
        return episode.summary

    def group_memory_by_similarity(
        self,
        memory_id: str,
        window_days: int = 45,
        min_tag_overlap: int = 1,
    ) -> Optional[str]:
        """Group a memory into an existing or new episode based on tags or time period proximity."""
        memory = self.memory_service.retrieve_memory(memory_id)
        if not memory:
            return None

        # Prefer linking to an existing episode when there is a clear overlap.
        best_episode = self._find_best_matching_episode(
            memory=memory,
            window_days=window_days,
            min_tag_overlap=min_tag_overlap,
        )
        if best_episode:
            self.link_memory_to_episode(memory_id, best_episode.episode_id)
            return best_episode.episode_id

        similar_memories = [
            candidate
            for candidate in self.memory_service.retrieve_all_memories()
            if candidate.id != memory_id
            and self._memories_are_related(memory, candidate, window_days, min_tag_overlap)
        ]
        if not similar_memories:
            return None

        life_stage = self._infer_life_stage(memory)
        seed_tag = memory.tags[0] if memory.tags else "Life Event"
        title = f"{seed_tag.title()} Period ({memory.timestamp.strftime('%Y')})"
        episode_id = self.create_episode(title=title, life_stage=life_stage)
        self.link_memory_to_episode(memory.id, episode_id)
        for candidate in similar_memories:
            self.link_memory_to_episode(candidate.id, episode_id)

        self.generate_episode_summary(episode_id)
        return episode_id

    def find_episode_by_memory_cluster(self, memory_ids: List[str]) -> Optional[str]:
        """Find an existing episode that already contains all provided memory IDs."""
        expected = set(memory_ids)
        if not expected:
            return None

        for episode in self.episodes.values():
            if expected.issubset(set(episode.related_memories)):
                return episode.episode_id
        return None

    def list_episodes(self) -> List[Episode]:
        """List all episodes ordered by start date."""
        return sorted(
            self.episodes.values(),
            key=lambda episode: episode.start_date or datetime.max,
        )

    def _find_best_matching_episode(
        self,
        memory: Memory,
        window_days: int,
        min_tag_overlap: int,
    ) -> Optional[Episode]:
        candidates: List[tuple[int, Episode]] = []
        memory_tags = set(tag.lower() for tag in memory.tags)

        for episode in self.episodes.values():
            episode_memories = self.list_episode_memories(episode.episode_id)
            if not episode_memories:
                continue

            episode_tags = {
                tag.lower() for episode_memory in episode_memories for tag in episode_memory.tags
            }
            overlap = len(memory_tags & episode_tags)

            in_window = False
            if episode.start_date and episode.end_date:
                in_window = (
                    abs((memory.timestamp - episode.start_date).days) <= window_days
                    or abs((memory.timestamp - episode.end_date).days) <= window_days
                    or episode.start_date <= memory.timestamp <= episode.end_date
                )

            if overlap >= min_tag_overlap or in_window:
                # Higher score means stronger match.
                score = overlap + (1 if in_window else 0)
                candidates.append((score, episode))

        if not candidates:
            return None

        candidates.sort(key=lambda pair: pair[0], reverse=True)
        return candidates[0][1]

    def _memories_are_related(
        self,
        first: Memory,
        second: Memory,
        window_days: int,
        min_tag_overlap: int,
    ) -> bool:
        first_tags = set(tag.lower() for tag in first.tags)
        second_tags = set(tag.lower() for tag in second.tags)
        tag_overlap = len(first_tags & second_tags)
        close_in_time = abs((first.timestamp - second.timestamp).days) <= window_days
        return tag_overlap >= min_tag_overlap or close_in_time

    def _infer_life_stage(self, memory: Memory) -> str:
        if self.timeline_engine and hasattr(self.timeline_engine, "_calculate_age") and hasattr(
            self.timeline_engine, "_get_life_stage"
        ):
            age = self.timeline_engine._calculate_age(memory.timestamp)
            return self.timeline_engine._get_life_stage(age)
        return "unknown"

    def _calculate_importance(self, episode: Episode) -> float:
        """Compute a bounded importance score from breadth and density of context."""
        memory_count_score = min(len(episode.related_memories) / 5.0, 1.0)
        people_score = min(len(episode.related_people) / 5.0, 1.0)

        memory_emotions = []
        for memory in self.list_episode_memories(episode.episode_id):
            memory_emotions.extend(memory.emotions)
        emotion_score = min(len(set(emotion.lower() for emotion in memory_emotions)) / 5.0, 1.0)

        weighted_score = (0.5 * memory_count_score) + (0.3 * people_score) + (0.2 * emotion_score)
        return round(min(weighted_score, 1.0), 3)
