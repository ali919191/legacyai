from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re
import uuid

from ..storage.hybrid_storage import GraphBackend, InMemoryGraphBackend


@dataclass
class PersonProfile:
    """Represents a person mentioned in memories or conversations."""

    person_id: str
    name: str
    relationship_to_user: Optional[str] = None
    origin: Optional[str] = None
    age: Optional[int] = None
    marital_status: Optional[str] = None
    children: List[str] = field(default_factory=list)
    description: str = ""
    connected_memories: List[str] = field(default_factory=list)
    confidence_score: float = 0.2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "person_id": self.person_id,
            "name": self.name,
            "relationship_to_user": self.relationship_to_user,
            "origin": self.origin,
            "age": self.age,
            "marital_status": self.marital_status,
            "children": list(self.children),
            "description": self.description,
            "connected_memories": list(self.connected_memories),
            "confidence_score": self.confidence_score,
        }


class PersonProfileService:
    """Track and enrich entity profiles for people mentioned across memories."""

    def __init__(self, memory_service=None, graph_backend: Optional[GraphBackend] = None):
        self.memory_service = memory_service
        self.graph_backend = graph_backend or InMemoryGraphBackend()
        self._profiles: Dict[str, PersonProfile] = {}
        self._name_index: Dict[str, str] = {}
        self.relationship_service: Optional[Any] = None

    def set_relationship_service(self, relationship_service: Any):
        """Attach relationship graph service for cross-entity links."""
        self.relationship_service = relationship_service

    def _normalize_name(self, name: str) -> str:
        return re.sub(r"\s+", " ", name.strip().lower())

    def create_person_profile(self, name: str) -> Dict[str, Any]:
        normalized = self._normalize_name(name)
        existing_id = self._name_index.get(normalized)
        if existing_id:
            return self._profiles[existing_id].to_dict()

        person_id = f"person_{uuid.uuid4().hex[:8]}"
        profile = PersonProfile(person_id=person_id, name=name.strip())
        self._profiles[person_id] = profile
        self._name_index[normalized] = person_id
        self.graph_backend.upsert_person(person_id, profile.to_dict())
        return profile.to_dict()

    def update_person_profile(self, person_id: str, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        profile = self._profiles.get(person_id)
        if not profile:
            return None

        old_name_normalized = self._normalize_name(profile.name)
        new_name = details.get("name")
        if new_name:
            profile.name = new_name.strip()
            new_name_normalized = self._normalize_name(profile.name)
            if new_name_normalized != old_name_normalized:
                self._name_index.pop(old_name_normalized, None)
                self._name_index[new_name_normalized] = person_id

        scalar_fields = [
            "relationship_to_user",
            "origin",
            "age",
            "marital_status",
            "description",
        ]
        for field_name in scalar_fields:
            if field_name in details and details[field_name] is not None:
                setattr(profile, field_name, details[field_name])

        if "children" in details and details["children"] is not None:
            children = list(dict.fromkeys(profile.children + list(details["children"])))
            profile.children = children

        if "connected_memories" in details and details["connected_memories"] is not None:
            connected = list(
                dict.fromkeys(profile.connected_memories + list(details["connected_memories"]))
            )
            profile.connected_memories = connected

        if "confidence_score" in details and details["confidence_score"] is not None:
            profile.confidence_score = max(0.0, min(float(details["confidence_score"]), 1.0))
        else:
            profile.confidence_score = min(profile.confidence_score + 0.1, 1.0)

        self.graph_backend.upsert_person(person_id, profile.to_dict())
        return profile.to_dict()

    def retrieve_person_profile(self, person_id: str) -> Optional[Dict[str, Any]]:
        profile = self._profiles.get(person_id)
        if not profile:
            return None

        profile_dict = profile.to_dict()
        if self.relationship_service and hasattr(
            self.relationship_service, "retrieve_relationships_for_person"
        ):
            profile_dict["relationships"] = self.relationship_service.retrieve_relationships_for_person(
                person_id
            )
        return profile_dict

    def link_memory_to_person(self, memory_id: str, person_id: str) -> bool:
        profile = self._profiles.get(person_id)
        if not profile:
            return False
        if memory_id not in profile.connected_memories:
            profile.connected_memories.append(memory_id)
            profile.confidence_score = min(profile.confidence_score + 0.1, 1.0)
            self.graph_backend.upsert_person(person_id, profile.to_dict())
        return True

    def search_person_by_name(self, name: str) -> List[Dict[str, Any]]:
        normalized = self._normalize_name(name)
        matches: List[PersonProfile] = []

        exact_id = self._name_index.get(normalized)
        if exact_id:
            matches.append(self._profiles[exact_id])
        else:
            for profile in self._profiles.values():
                profile_normalized = self._normalize_name(profile.name)
                if normalized in profile_normalized or profile_normalized in normalized:
                    matches.append(profile)

        return [profile.to_dict() for profile in matches]

    def sync_memory_entities(self, memory) -> List[Dict[str, Any]]:
        """Create or enrich profiles from a memory's people_involved list."""
        synced_profiles = []
        for person_name in memory.people_involved or []:
            person_name = person_name.strip()
            if not person_name:
                continue
            existing = self.search_person_by_name(person_name)
            if existing:
                profile_dict = existing[0]
            else:
                profile_dict = self.create_person_profile(person_name)

            person_id = profile_dict["person_id"]
            details = {
                "origin": profile_dict.get("origin") or f"Mentioned in memory '{memory.title}'",
                "connected_memories": [memory.id],
                "confidence_score": max(profile_dict.get("confidence_score", 0.2), 0.5),
            }
            updated = self.update_person_profile(person_id, details)
            if updated:
                synced_profiles.append(updated)
        return synced_profiles

    def create_temporary_profile(
        self,
        name: str,
        context_description: str = "",
        relationship_to_user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or enrich a low-confidence temporary profile from conversation."""
        matches = self.search_person_by_name(name)
        if matches:
            person_id = matches[0]["person_id"]
        else:
            person_id = self.create_person_profile(name)["person_id"]

        profile = self.update_person_profile(
            person_id,
            {
                "relationship_to_user": relationship_to_user,
                "origin": "Detected in conversation",
                "description": context_description or f"Temporary profile created for {name}",
                "confidence_score": max(
                    self._profiles[person_id].confidence_score,
                    0.3,
                ),
            },
        )
        return profile
