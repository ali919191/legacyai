from typing import List, Dict, Optional, Any
from datetime import datetime, date
from app.services.memory_capture_service import Memory, MemoryCaptureService


class TimelineEngine:
    """Engine for organizing and querying memories in a timeline."""

    LIFE_STAGES = {
        'childhood': (0, 12),
        'education': (13, 22),
        'career': (23, 64),
        'retirement': (65, 150)  # Assuming max age 150
    }

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        birth_date: date,
        episode_service: Optional[Any] = None,
    ):
        """
        Initialize the timeline engine.

        Args:
            memory_service: The memory capture service instance.
            birth_date: The birth date of the person for age calculations.
        """
        self.memory_service = memory_service
        self.birth_date = birth_date
        self.episode_service = episode_service

    def set_episode_service(self, episode_service: Any):
        """Attach episode service used for higher-level memory period groupings."""
        self.episode_service = episode_service

    def _calculate_age(self, timestamp: datetime) -> int:
        """Calculate age at the given timestamp."""
        age = timestamp.year - self.birth_date.year
        if (timestamp.month, timestamp.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def _get_life_stage(self, age: int) -> str:
        """Determine life stage based on age."""
        for stage, (min_age, max_age) in self.LIFE_STAGES.items():
            if min_age <= age <= max_age:
                return stage
        return 'unknown'

    def get_chronological_timeline(self) -> List[Memory]:
        """
        Get all memories organized chronologically (oldest first).

        Returns:
            List of Memory objects sorted by timestamp.
        """
        memories = self.memory_service.retrieve_all_memories()
        return sorted(memories, key=lambda m: m.timestamp)

    def group_by_life_stage(self) -> Dict[str, List[Memory]]:
        """
        Group memories by life stage.

        Returns:
            Dictionary with life stages as keys and lists of Memory objects as values.
        """
        grouped = {stage: [] for stage in self.LIFE_STAGES.keys()}
        grouped['unknown'] = []

        for memory in self.memory_service.retrieve_all_memories():
            age = self._calculate_age(memory.timestamp)
            stage = self._get_life_stage(age)
            grouped[stage].append(memory)

        # Sort each group chronologically
        for stage in grouped:
            grouped[stage].sort(key=lambda m: m.timestamp)

        return grouped

    def query_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Memory]:
        """
        Query memories within a specific date range.

        Args:
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).

        Returns:
            List of Memory objects within the date range, sorted chronologically.
        """
        memories = self.memory_service.retrieve_all_memories()
        filtered = [m for m in memories if start_date <= m.timestamp <= end_date]
        return sorted(filtered, key=lambda m: m.timestamp)

    def query_by_life_stage(self, life_stage: str) -> List[Memory]:
        """
        Query memories for a specific life stage.

        Args:
            life_stage: The life stage to query ('childhood', 'education', 'career', 'retirement').

        Returns:
            List of Memory objects for the life stage, sorted chronologically.
        """
        if life_stage not in self.LIFE_STAGES and life_stage != 'unknown':
            return []

        grouped = self.group_by_life_stage()
        return grouped.get(life_stage, [])

    def get_life_stage_summary(self) -> Dict[str, int]:
        """
        Get a summary of memory counts per life stage.

        Returns:
            Dictionary with life stages as keys and memory counts as values.
        """
        grouped = self.group_by_life_stage()
        return {stage: len(memories) for stage, memories in grouped.items()}

    def format_temporal_context(self, memory: Memory) -> str:
        """Build a compact temporal phrase for narrative rendering."""
        parts = []
        if memory.day_of_week:
            parts.append(memory.day_of_week)
        if memory.time_of_day:
            parts.append(memory.time_of_day)

        if memory.start_time and memory.end_time and memory.start_time != memory.end_time:
            parts.append(f"{memory.start_time}-{memory.end_time}")
        elif memory.start_time:
            parts.append(memory.start_time)

        return ", ".join(parts)

    def query_by_time_of_day(self, time_of_day: str) -> List[Memory]:
        """
        Query memories that occurred during a specific time-of-day bucket.

        Args:
            time_of_day: One of morning, afternoon, evening, night.

        Returns:
            List of matching memories sorted chronologically.
        """
        normalized = time_of_day.strip().lower()
        matches = [
            m for m in self.memory_service.retrieve_all_memories()
            if m.time_of_day and m.time_of_day.lower() == normalized
        ]
        return sorted(matches, key=lambda m: m.timestamp)

    def group_related_memories_into_episodes(
        self,
        window_days: int = 45,
        min_shared_tags: int = 1,
    ) -> List[str]:
        """Group related memories into episodes using common tags or close time periods."""
        if not self.episode_service:
            return []

        created_episode_ids: List[str] = []
        grouped_by_stage = self.group_by_life_stage()

        for stage, memories in grouped_by_stage.items():
            if len(memories) < 2:
                continue

            current_cluster: List[Memory] = []
            cluster_tag_set: set[str] = set()

            for memory in memories:
                if not current_cluster:
                    current_cluster = [memory]
                    cluster_tag_set = set(tag.lower() for tag in memory.tags)
                    continue

                previous = current_cluster[-1]
                memory_tags = set(tag.lower() for tag in memory.tags)
                shared_tags = len(cluster_tag_set & memory_tags)
                close_in_time = abs((memory.timestamp - previous.timestamp).days) <= window_days

                if shared_tags >= min_shared_tags or close_in_time:
                    current_cluster.append(memory)
                    cluster_tag_set |= memory_tags
                    continue

                episode_id = self._create_episode_from_cluster(stage, current_cluster)
                if episode_id:
                    created_episode_ids.append(episode_id)

                current_cluster = [memory]
                cluster_tag_set = set(tag.lower() for tag in memory.tags)

            episode_id = self._create_episode_from_cluster(stage, current_cluster)
            if episode_id:
                created_episode_ids.append(episode_id)

        return created_episode_ids

    def _create_episode_from_cluster(self, life_stage: str, cluster: List[Memory]) -> Optional[str]:
        """Create and populate an episode from a memory cluster when meaningful."""
        if not self.episode_service or len(cluster) < 2:
            return None

        memory_ids = [memory.id for memory in cluster]
        if hasattr(self.episode_service, "find_episode_by_memory_cluster"):
            existing = self.episode_service.find_episode_by_memory_cluster(memory_ids)
            if existing:
                return None

        lead_memory = cluster[0]
        dominant_tag = lead_memory.tags[0].title() if lead_memory.tags else "Life"
        episode_title = f"{dominant_tag} Chapter ({lead_memory.timestamp.strftime('%Y')})"
        episode_id = self.episode_service.create_episode(
            title=episode_title,
            life_stage=life_stage,
        )
        for memory in cluster:
            self.episode_service.link_memory_to_episode(memory.id, episode_id)
        self.episode_service.generate_episode_summary(episode_id)
        return episode_id