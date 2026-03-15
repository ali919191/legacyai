from typing import List, Dict, Optional
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

    def __init__(self, memory_service: MemoryCaptureService, birth_date: date):
        """
        Initialize the timeline engine.

        Args:
            memory_service: The memory capture service instance.
            birth_date: The birth date of the person for age calculations.
        """
        self.memory_service = memory_service
        self.birth_date = birth_date

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