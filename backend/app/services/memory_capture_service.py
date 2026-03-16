from dataclasses import dataclass
from typing import Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class Memory:
    """Represents a memory entry in the Legacy AI platform."""
    id: str
    title: str
    description: str
    timestamp: datetime
    people_involved: List[str]
    location: str
    emotions: List[str]
    tags: List[str]
    time_of_day: str = ""
    start_time: str = ""
    end_time: str = ""
    day_of_week: str = ""
    sensitivity_tags: Optional[List[str]] = None  # For access control: 'public', 'personal', 'medical', 'financial', 'intimate'


class MemoryCaptureService:
    """Service for capturing, updating, and retrieving memories."""

    def __init__(self, person_profile_service: Optional[Any] = None):
        """Initialize the service with an in-memory storage for memories."""
        self.memories: dict[str, Memory] = {}
        self.person_profile_service = person_profile_service

    def set_person_profile_service(self, person_profile_service: Any):
        """Attach a profile service used for entity sync from memory mentions."""
        self.person_profile_service = person_profile_service

    def _sync_person_profiles_from_memory(self, memory: Memory):
        """Push memory people references into the person-profile system when available."""
        if self.person_profile_service and hasattr(self.person_profile_service, "sync_memory_entities"):
            self.person_profile_service.sync_memory_entities(memory)

    def _infer_time_of_day(self, timestamp: datetime) -> str:
        """Infer a narrative-friendly time bucket from a timestamp hour."""
        hour = timestamp.hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 21:
            return "evening"
        return "night"

    def create_memory(
        self,
        title: str,
        description: str,
        timestamp: Optional[datetime] = None,
        people_involved: Optional[List[str]] = None,
        location: str = "",
        emotions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        time_of_day: str = "",
        start_time: str = "",
        end_time: str = "",
        day_of_week: str = "",
        sensitivity_tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new memory entry.

        Args:
            title: The title of the memory.
            description: Detailed description of the memory.
            timestamp: When the memory occurred. Defaults to current time.
            people_involved: List of people involved in the memory.
            location: Where the memory took place.
            emotions: List of emotions associated with the memory.
            tags: List of tags for categorization.
            time_of_day: Optional temporal bucket ('morning', 'afternoon', 'evening', 'night').
            start_time: Optional memory start time in HH:MM format.
            end_time: Optional memory end time in HH:MM format.
            day_of_week: Optional day-of-week label (e.g., Monday).
            sensitivity_tags: Access control tags ('public', 'personal', 'medical', 'financial', 'intimate').

        Returns:
            The ID of the created memory.
        """
        if timestamp is None:
            timestamp = datetime.now()
        if people_involved is None:
            people_involved = []
        if emotions is None:
            emotions = []
        if tags is None:
            tags = []
        if sensitivity_tags is None:
            sensitivity_tags = []

        if not start_time:
            start_time = timestamp.strftime("%H:%M")
        if not end_time:
            end_time = start_time
        if not day_of_week:
            day_of_week = timestamp.strftime("%A")
        if not time_of_day:
            time_of_day = self._infer_time_of_day(timestamp)

        memory_id = str(uuid.uuid4())
        memory = Memory(
            id=memory_id,
            title=title,
            description=description,
            timestamp=timestamp,
            people_involved=people_involved,
            location=location,
            emotions=emotions,
            tags=tags,
            time_of_day=time_of_day,
            start_time=start_time,
            end_time=end_time,
            day_of_week=day_of_week,
            sensitivity_tags=sensitivity_tags
        )
        self.memories[memory_id] = memory
        self._sync_person_profiles_from_memory(memory)
        return memory_id

    def update_memory(
        self,
        memory_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        people_involved: Optional[List[str]] = None,
        location: Optional[str] = None,
        emotions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        time_of_day: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        day_of_week: Optional[str] = None,
        sensitivity_tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update an existing memory entry.

        Args:
            memory_id: The ID of the memory to update.
            Other args: Fields to update (only provided fields will be changed).

        Returns:
            True if updated successfully, False if memory not found.
        """
        if memory_id not in self.memories:
            return False

        memory = self.memories[memory_id]
        if title is not None:
            memory.title = title
        if description is not None:
            memory.description = description
        if timestamp is not None:
            memory.timestamp = timestamp
        if people_involved is not None:
            memory.people_involved = people_involved
        if location is not None:
            memory.location = location
        if emotions is not None:
            memory.emotions = emotions
        if tags is not None:
            memory.tags = tags
        if time_of_day is not None:
            memory.time_of_day = time_of_day
        if start_time is not None:
            memory.start_time = start_time
        if end_time is not None:
            memory.end_time = end_time
        if day_of_week is not None:
            memory.day_of_week = day_of_week
        if sensitivity_tags is not None:
            memory.sensitivity_tags = sensitivity_tags

        if timestamp is not None:
            if time_of_day is None:
                memory.time_of_day = self._infer_time_of_day(timestamp)
            if start_time is None:
                memory.start_time = timestamp.strftime("%H:%M")
            if end_time is None and not memory.end_time:
                memory.end_time = memory.start_time
            if day_of_week is None:
                memory.day_of_week = timestamp.strftime("%A")

        self._sync_person_profiles_from_memory(memory)
        return True

    def retrieve_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a memory by its ID.

        Args:
            memory_id: The ID of the memory to retrieve.

        Returns:
            The Memory object if found, None otherwise.
        """
        return self.memories.get(memory_id)

    def retrieve_all_memories(self) -> List[Memory]:
        """
        Retrieve all stored memories.

        Returns:
            List of all Memory objects.
        """
        return list(self.memories.values())

    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by its ID.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            True if deleted successfully, False if not found.
        """
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False