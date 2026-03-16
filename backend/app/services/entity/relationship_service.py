from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from typing import Any, Dict, List, Optional
import uuid

from ..storage.hybrid_storage import GraphBackend, InMemoryGraphBackend


@dataclass
class Relationship:
    """Represents a directed relationship between two people."""

    relationship_id: str
    person_a: str
    person_b: str
    relationship_type: str
    context_memory: Optional[str]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "person_a": self.person_a,
            "person_b": self.person_b,
            "relationship_type": self.relationship_type,
            "context_memory": self.context_memory,
            "timestamp": self.timestamp.isoformat(),
        }


class RelationshipService:
    """Track and infer relationships between people in memories and conversations."""

    RELATIONSHIP_TYPES = {
        "friend_of",
        "mentor_of",
        "introduced",
        "colleague_of",
        "family_of",
    }

    def __init__(
        self,
        person_profile_service: Optional[Any] = None,
        graph_backend: Optional[GraphBackend] = None,
    ):
        self.person_profile_service = person_profile_service
        self.graph_backend = graph_backend or InMemoryGraphBackend()
        self._relationships: Dict[str, Relationship] = {}

    def create_relationship(
        self,
        person_a: str,
        person_b: str,
        relationship_type: str,
        context_memory: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Create and persist a relationship record."""
        normalized_type = (relationship_type or "friend_of").strip().lower()
        if normalized_type not in self.RELATIONSHIP_TYPES:
            normalized_type = "friend_of"

        person_a_id = self._resolve_person_identifier(person_a)
        person_b_id = self._resolve_person_identifier(person_b)

        existing = self._find_existing(person_a_id, person_b_id, normalized_type)
        if existing:
            if context_memory and not existing.context_memory:
                existing.context_memory = context_memory
            existing.timestamp = timestamp or datetime.now()
            return existing.to_dict()

        relationship_id = f"rel_{uuid.uuid4().hex[:10]}"
        relationship = Relationship(
            relationship_id=relationship_id,
            person_a=person_a_id,
            person_b=person_b_id,
            relationship_type=normalized_type,
            context_memory=context_memory,
            timestamp=timestamp or datetime.now(),
        )
        self._relationships[relationship_id] = relationship
        self.graph_backend.upsert_relationship(relationship_id, relationship.to_dict())
        return relationship.to_dict()

    def update_relationship(self, relationship_id: str, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update mutable relationship fields."""
        relationship = self._relationships.get(relationship_id)
        if not relationship:
            return None

        if "relationship_type" in details and details["relationship_type"]:
            candidate_type = str(details["relationship_type"]).strip().lower()
            if candidate_type in self.RELATIONSHIP_TYPES:
                relationship.relationship_type = candidate_type

        if "context_memory" in details and details["context_memory"] is not None:
            relationship.context_memory = details["context_memory"]

        if "person_a" in details and details["person_a"]:
            relationship.person_a = self._resolve_person_identifier(str(details["person_a"]))

        if "person_b" in details and details["person_b"]:
            relationship.person_b = self._resolve_person_identifier(str(details["person_b"]))

        if "timestamp" in details and isinstance(details["timestamp"], datetime):
            relationship.timestamp = details["timestamp"]
        else:
            relationship.timestamp = datetime.now()

        self.graph_backend.upsert_relationship(relationship_id, relationship.to_dict())
        return relationship.to_dict()

    def retrieve_relationships_for_person(self, person_id: str) -> List[Dict[str, Any]]:
        """Retrieve all relationships where a person appears as source or target."""
        resolved = self._resolve_person_identifier(person_id)
        matches = [
            relationship.to_dict()
            for relationship in self._relationships.values()
            if relationship.person_a == resolved or relationship.person_b == resolved
        ]
        if not matches:
            matches = self.graph_backend.get_relationships_for_person(resolved)
        return sorted(matches, key=lambda rel: rel["timestamp"])

    def detect_relationships_from_memory(self, memory: Any) -> List[Dict[str, Any]]:
        """Infer and store relationships for people co-mentioned in a memory."""
        people = [name.strip() for name in (getattr(memory, "people_involved", []) or []) if name.strip()]
        if len(people) < 2:
            return []

        relationship_type = self._infer_relationship_type(memory)
        detected: List[Dict[str, Any]] = []
        for person_a, person_b in combinations(people, 2):
            detected.append(
                self.create_relationship(
                    person_a=person_a,
                    person_b=person_b,
                    relationship_type=relationship_type,
                    context_memory=getattr(memory, "id", None),
                    timestamp=getattr(memory, "timestamp", None),
                )
            )
        return detected

    def detect_relationships_from_conversation(self, text: str) -> List[Dict[str, Any]]:
        """Infer lightweight relationships from conversation when two names are present."""
        if not self.person_profile_service or not text:
            return []

        known_profiles = getattr(self.person_profile_service, "_profiles", {})
        names_in_text = [
            profile.name
            for profile in known_profiles.values()
            if profile.name.lower() in text.lower()
        ]
        unique_names = list(dict.fromkeys(names_in_text))
        if len(unique_names) < 2:
            return []

        relationship_type = self._infer_relationship_type_from_text(text)
        detected: List[Dict[str, Any]] = []
        for person_a, person_b in combinations(unique_names, 2):
            detected.append(
                self.create_relationship(
                    person_a=person_a,
                    person_b=person_b,
                    relationship_type=relationship_type,
                    context_memory=None,
                    timestamp=datetime.now(),
                )
            )
        return detected

    def _resolve_person_identifier(self, person_ref: str) -> str:
        if not self.person_profile_service:
            return person_ref

        ref = (person_ref or "").strip()
        if not ref:
            return ref

        existing_profiles = getattr(self.person_profile_service, "_profiles", {})
        if ref in existing_profiles:
            return ref

        matches = self.person_profile_service.search_person_by_name(ref)
        if matches:
            return matches[0]["person_id"]

        profile = self.person_profile_service.create_person_profile(ref)
        return profile["person_id"]

    def _find_existing(self, person_a: str, person_b: str, relationship_type: str) -> Optional[Relationship]:
        for relationship in self._relationships.values():
            same_direction = relationship.person_a == person_a and relationship.person_b == person_b
            reverse_direction = relationship.person_a == person_b and relationship.person_b == person_a
            if (same_direction or reverse_direction) and relationship.relationship_type == relationship_type:
                return relationship
        return None

    def _infer_relationship_type(self, memory: Any) -> str:
        text = f"{getattr(memory, 'title', '')} {getattr(memory, 'description', '')}".lower()
        tags = {tag.lower() for tag in (getattr(memory, "tags", []) or [])}

        if {"family", "parent", "mother", "father", "sibling"} & tags or "family" in text:
            return "family_of"
        if {"mentor", "teacher", "coach"} & tags or "mentor" in text:
            return "mentor_of"
        if {"work", "career", "office", "job", "colleague"} & tags or "colleague" in text:
            return "colleague_of"
        if "introduced" in text or "introduce" in text:
            return "introduced"
        return "friend_of"

    def _infer_relationship_type_from_text(self, text: str) -> str:
        lowered = text.lower()
        if any(token in lowered for token in ["family", "brother", "sister", "mother", "father"]):
            return "family_of"
        if any(token in lowered for token in ["mentor", "teacher", "coach"]):
            return "mentor_of"
        if any(token in lowered for token in ["colleague", "coworker", "teammate", "office"]):
            return "colleague_of"
        if any(token in lowered for token in ["introduced", "introduce", "met through"]):
            return "introduced"
        return "friend_of"
