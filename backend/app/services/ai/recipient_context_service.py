from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RecipientProfile:
    """Stores recipient metadata used to tailor AI responses."""

    user_id: str
    name: str
    relationship: str
    age: int
    maturity_level: str
    topic_preferences: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "relationship": self.relationship,
            "age": self.age,
            "maturity_level": self.maturity_level,
            "topic_preferences": list(self.topic_preferences),
        }


class RecipientContextService:
    """Manages recipient profiles for age-aware and relationship-aware responses."""

    def __init__(self):
        self._profiles: Dict[str, RecipientProfile] = {}

    def create_recipient_profile(
        self,
        user_id: str,
        name: str,
        relationship: str,
        age: int,
    ) -> Dict[str, Any]:
        """Create a recipient profile with inferred maturity level."""
        profile = RecipientProfile(
            user_id=user_id,
            name=name,
            relationship=relationship,
            age=age,
            maturity_level=self.determine_maturity_level(age),
            topic_preferences=[],
        )
        self._profiles[user_id] = profile
        return profile.to_dict()

    def update_recipient_profile(self, user_id: str, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing recipient profile fields."""
        profile = self._profiles.get(user_id)
        if not profile:
            return None

        if "name" in details and details["name"] is not None:
            profile.name = str(details["name"])
        if "relationship" in details and details["relationship"] is not None:
            profile.relationship = str(details["relationship"])
        if "age" in details and details["age"] is not None:
            profile.age = int(details["age"])
            profile.maturity_level = self.determine_maturity_level(profile.age)
        if "topic_preferences" in details and details["topic_preferences"] is not None:
            profile.topic_preferences = list(details["topic_preferences"])

        return profile.to_dict()

    def retrieve_recipient_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Return recipient profile by user ID when available."""
        profile = self._profiles.get(user_id)
        return profile.to_dict() if profile else None

    def determine_maturity_level(self, age: int) -> str:
        """Infer maturity bucket from age."""
        if age < 13:
            return "child"
        if age < 18:
            return "teen"
        if age < 25:
            return "young_adult"
        return "adult"