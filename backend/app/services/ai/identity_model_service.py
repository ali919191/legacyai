import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class IdentityProfile:
    """Identity traits used to shape response personality and tone."""

    user_id: str
    communication_style: str
    values: List[str] = field(default_factory=list)
    tone_preferences: List[str] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "communication_style": self.communication_style,
            "values": list(self.values),
            "tone_preferences": list(self.tone_preferences),
            "interaction_history": list(self.interaction_history),
        }


class IdentityModelService:
    """Stores and retrieves identity profiles for response adaptation."""

    def __init__(self, data_store_path: Optional[str] = None):
        if data_store_path:
            self._data_store_path = data_store_path
        else:
            self._data_store_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "..",
                    "data",
                    "identity_profiles.json",
                )
            )
        self._profiles: Dict[str, IdentityProfile] = {}
        self._load_profiles()

    def _load_profiles(self) -> None:
        os.makedirs(os.path.dirname(self._data_store_path), exist_ok=True)
        if not os.path.exists(self._data_store_path):
            with open(self._data_store_path, "w", encoding="utf-8") as fp:
                json.dump({}, fp, indent=2)
            return

        with open(self._data_store_path, "r", encoding="utf-8") as fp:
            raw_data = json.load(fp) or {}

        for user_id, profile in raw_data.items():
            self._profiles[user_id] = IdentityProfile(
                user_id=profile.get("user_id", user_id),
                communication_style=profile.get("communication_style", "warm"),
                values=profile.get("values", ["family", "honesty"]),
                tone_preferences=profile.get("tone_preferences", ["supportive"]),
                interaction_history=profile.get("interaction_history", []),
            )

    def _save_profiles(self) -> None:
        with open(self._data_store_path, "w", encoding="utf-8") as fp:
            json.dump({k: v.to_dict() for k, v in self._profiles.items()}, fp, indent=2)

    def create_identity_profile(
        self,
        user_id: str,
        communication_style: str,
        values: Optional[List[str]] = None,
        tone_preferences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        profile = IdentityProfile(
            user_id=user_id,
            communication_style=communication_style,
            values=list(values or ["family", "honesty"]),
            tone_preferences=list(tone_preferences or ["supportive"]),
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

    def update_identity_profile(self, user_id: str, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        profile = self._profiles.get(user_id)
        if not profile:
            return None

        if "communication_style" in details and details["communication_style"] is not None:
            profile.communication_style = str(details["communication_style"])
        if "values" in details and details["values"] is not None:
            profile.values = list(details["values"])
        if "tone_preferences" in details and details["tone_preferences"] is not None:
            profile.tone_preferences = list(details["tone_preferences"])

        profile.interaction_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "profile_updated",
                "details": details,
            }
        )
        self._save_profiles()
        return profile.to_dict()

    def retrieve_identity_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        profile = self._profiles.get(user_id)
        return profile.to_dict() if profile else None

    def resolve_identity_profile(
        self,
        user_id: Optional[str],
        fallback_values: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        resolved_user_id = user_id or "default"
        profile = self.retrieve_identity_profile(resolved_user_id)
        if profile:
            return profile

        # Create a stable default profile the first time this user is seen.
        return self.create_identity_profile(
            user_id=resolved_user_id,
            communication_style="warm",
            values=fallback_values or ["family", "discipline", "honesty"],
            tone_preferences=["supportive", "clear"],
        )