from dataclasses import dataclass
from typing import List, Optional
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


class MemoryCaptureService:
    """Service for capturing, updating, and retrieving memories."""

    def __init__(self):
        """Initialize the service with an in-memory storage for memories."""
        self.memories: dict[str, Memory] = {}

    def create_memory(
        self,
        title: str,
        description: str,
        timestamp: Optional[datetime] = None,
        people_involved: Optional[List[str]] = None,
        location: str = "",
        emotions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
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

        memory_id = str(uuid.uuid4())
        memory = Memory(
            id=memory_id,
            title=title,
            description=description,
            timestamp=timestamp,
            people_involved=people_involved,
            location=location,
            emotions=emotions,
            tags=tags
        )
        self.memories[memory_id] = memory
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
        tags: Optional[List[str]] = None
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