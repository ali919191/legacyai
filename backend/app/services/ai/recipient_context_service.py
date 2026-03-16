import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class RecipientProfile:
    """Stores recipient metadata used to tailor AI responses."""

    user_id: str
    name: str
    relationship_to_user: str
    age: Optional[int]
    age_bucket: str
    maturity_level: str
    topic_preferences: List[str] = field(default_factory=list)
    known_children: List[str] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "relationship_to_user": self.relationship_to_user,
            "age": self.age,
            "age_bucket": self.age_bucket,
            "maturity_level": self.maturity_level,
            "topic_preferences": list(self.topic_preferences),
            "known_children": list(self.known_children),
            "interaction_history": list(self.interaction_history),
        }


class RecipientContextService:
    """Manages recipient profiles for age-aware and relationship-aware responses."""

    def __init__(self, data_store_path: Optional[str] = None):
        if data_store_path:
            self._data_store_path = data_store_path
        else:
            self._data_store_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "recipient_profiles.json")
            )
        self._profiles: Dict[str, RecipientProfile] = {}
        self._load_profiles()

    def _load_profiles(self):
        """Load recipient profiles from the JSON data store."""
        os.makedirs(os.path.dirname(self._data_store_path), exist_ok=True)
        if not os.path.exists(self._data_store_path):
            with open(self._data_store_path, "w", encoding="utf-8") as fp:
                json.dump({}, fp, indent=2)
            return

        with open(self._data_store_path, "r", encoding="utf-8") as fp:
            raw_data = json.load(fp) or {}

        for user_id, profile in raw_data.items():
            self._profiles[user_id] = RecipientProfile(
                user_id=profile.get("user_id", user_id),
                name=profile.get("name", "recipient"),
                relationship_to_user=profile.get("relationship_to_user", "unknown"),
                age=profile.get("age"),
                age_bucket=profile.get("age_bucket", "unknown"),
                maturity_level=profile.get("maturity_level", "adult"),
                topic_preferences=profile.get("topic_preferences", []),
                known_children=profile.get("known_children", []),
                interaction_history=profile.get("interaction_history", []),
            )

    def _save_profiles(self):
        """Persist recipient profiles to the JSON data store."""
        data = {user_id: profile.to_dict() for user_id, profile in self._profiles.items()}
        with open(self._data_store_path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)

    def create_recipient_profile(
        self,
        user_id: str,
        name: str,
        relationship: str,
        age: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a recipient profile with inferred maturity level."""
        age_bucket = self.determine_age_bucket(age) if age is not None else "unknown"
        profile = RecipientProfile(
            user_id=user_id,
            name=name,
            relationship_to_user=relationship,
            age=age,
            age_bucket=age_bucket,
            maturity_level=self.determine_maturity_level(age),
            topic_preferences=[],
            known_children=[],
            interaction_history=[
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "event": "profile_created",
                }
            ],
        )
        self._profiles[user_id] = profile
        self._save_profiles()
        return profile.to_dict()

    def update_recipient_profile(self, user_id: str, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing recipient profile fields."""
        profile = self._profiles.get(user_id)
        if not profile:
            return None

        if "name" in details and details["name"] is not None:
            profile.name = str(details["name"])
        if "relationship" in details and details["relationship"] is not None:
            profile.relationship_to_user = str(details["relationship"])
        if "relationship_to_user" in details and details["relationship_to_user"] is not None:
            profile.relationship_to_user = str(details["relationship_to_user"])
        if "age" in details and details["age"] is not None:
            profile.age = int(details["age"])
            profile.age_bucket = self.determine_age_bucket(profile.age)
            profile.maturity_level = self.determine_maturity_level(profile.age)
        if "topic_preferences" in details and details["topic_preferences"] is not None:
            profile.topic_preferences = list(details["topic_preferences"])
        if "known_children" in details and details["known_children"] is not None:
            profile.known_children = list(details["known_children"])

        profile.interaction_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "profile_updated",
                "details": {k: v for k, v in details.items() if k != "interaction_history"},
            }
        )

        self._save_profiles()
        return profile.to_dict()

    def retrieve_recipient_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Return recipient profile by user ID when available."""
        profile = self._profiles.get(user_id)
        return profile.to_dict() if profile else None

    def determine_age_bucket(self, age: int) -> str:
        """Infer age bucket used for response adaptation."""
        if age <= 7:
            return "young_child"
        if age <= 12:
            return "child"
        if age <= 17:
            return "teenager"
        if age <= 25:
            return "young_adult"
        if age <= 40:
            return "adult"
        return "mature_adult"

    def determine_maturity_level(self, age: Optional[int]) -> str:
        """Infer maturity bucket from age."""
        if age is None:
            return "adult"
        if age < 13:
            return "child"
        if age < 18:
            return "teen"
        if age < 25:
            return "young_adult"
        return "adult"

    def extract_family_profiles_from_conversation(self, conversation_text: str) -> List[Dict[str, Any]]:
        """Extract child/family recipient profiles from conversation statements."""
        text = conversation_text.lower()
        created_profiles: List[Dict[str, Any]] = []

        if "children" not in text and "child" not in text:
            return created_profiles

        ages = [int(value) for value in re.findall(r"\b(\d{1,2})\b", conversation_text) if int(value) <= 120]
        if not ages:
            return created_profiles

        for index, age in enumerate(ages, start=1):
            generated_user_id = f"auto_child_{age}_{index}"
            if generated_user_id in self._profiles:
                continue
            profile = self.create_recipient_profile(
                user_id=generated_user_id,
                name=f"Child {index}",
                relationship="child",
                age=age,
            )
            profile["interaction_history"].append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "event": "extracted_from_conversation",
                    "source": conversation_text,
                }
            )
            self._profiles[generated_user_id].interaction_history = profile["interaction_history"]
            created_profiles.append(profile)

        if created_profiles:
            self._save_profiles()
        return created_profiles