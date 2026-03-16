from datetime import datetime
from typing import Any, Dict, List


class MemoryPriorityService:
    """Ranks memories by life importance, emotional weight, and recency."""

    IMPORTANT_TAGS = {
        "family": 1.0,
        "career": 0.9,
        "lesson": 1.0,
        "milestone": 1.0,
        "graduation": 1.0,
        "wedding": 1.0,
        "birth": 1.0,
        "death": 1.0,
        "retirement": 0.9,
        "achievement": 0.85,
        "major_event": 1.0,
    }

    MILESTONE_KEYWORDS = {
        "first",
        "graduation",
        "married",
        "wedding",
        "born",
        "birth",
        "promotion",
        "retirement",
        "funeral",
        "milestone",
        "lesson",
        "turning point",
    }

    EMOTION_INTENSITY = {
        "joy": 0.8,
        "happiness": 0.75,
        "gratitude": 0.7,
        "pride": 0.8,
        "love": 0.9,
        "surprise": 0.65,
        "sadness": 0.8,
        "grief": 0.95,
        "fear": 0.85,
        "anger": 0.8,
        "regret": 0.85,
        "determination": 0.7,
        "nostalgia": 0.7,
        "excitement": 0.75,
        "anxious": 0.65,
        "nervous": 0.6,
        "triumph": 0.9,
    }

    def calculate_importance(self, memory: Any) -> float:
        """Calculate a normalized importance score based on milestones, events, and tags."""
        title = (getattr(memory, "title", "") or "").lower()
        description = (getattr(memory, "description", "") or "").lower()
        tags = [tag.lower() for tag in (getattr(memory, "tags", []) or [])]

        tag_score = 0.0
        if tags:
            weighted = [self.IMPORTANT_TAGS.get(tag, 0.0) for tag in tags]
            tag_score = min(sum(weighted) / max(len(tags), 1), 1.0)

        milestone_hit = any(keyword in title or keyword in description for keyword in self.MILESTONE_KEYWORDS)
        milestone_score = 1.0 if milestone_hit else 0.0

        major_event_signal = 0.0
        if len(getattr(memory, "people_involved", []) or []) >= 3:
            major_event_signal += 0.5
        if len(set(tags) & {"family", "career", "lesson", "major_event", "milestone"}) >= 2:
            major_event_signal += 0.5
        major_event_score = min(major_event_signal, 1.0)

        # Importance blends explicit tags with inferred milestone/event cues.
        importance = (0.45 * tag_score) + (0.35 * milestone_score) + (0.20 * major_event_score)
        return round(min(max(importance, 0.0), 1.0), 3)

    def calculate_emotional_weight(self, memory: Any) -> float:
        """Calculate emotional weight from attached emotions and inferred intensity."""
        emotions = [emotion.lower() for emotion in (getattr(memory, "emotions", []) or [])]
        if not emotions:
            return 0.0

        intensities = [self.EMOTION_INTENSITY.get(emotion, 0.5) for emotion in emotions]
        average_intensity = sum(intensities) / len(intensities)

        # More emotion descriptors usually indicates richer emotional context.
        richness_boost = min(len(set(emotions)) / 6.0, 1.0)
        emotional_weight = (0.8 * average_intensity) + (0.2 * richness_boost)
        return round(min(max(emotional_weight, 0.0), 1.0), 3)

    def rank_memories(self, memory_list: List[Any]) -> List[Dict[str, Any]]:
        """Return memories ranked by combined priority score.

        Formula:
            priority_score =
                (importance_score * 0.6)
                + (emotional_weight * 0.3)
                + (recency_factor * 0.1)
        """
        now = datetime.now()
        ranked: List[Dict[str, Any]] = []

        for memory in memory_list:
            importance_score = self.calculate_importance(memory)
            emotional_weight = self.calculate_emotional_weight(memory)
            recency_factor = self._calculate_recency_factor(memory, now)
            priority_score = (
                (importance_score * 0.6)
                + (emotional_weight * 0.3)
                + (recency_factor * 0.1)
            )

            ranked.append(
                {
                    "memory": memory,
                    "importance_score": round(importance_score, 3),
                    "emotional_weight": round(emotional_weight, 3),
                    "recency_factor": round(recency_factor, 3),
                    "priority_score": round(min(max(priority_score, 0.0), 1.0), 3),
                }
            )

        ranked.sort(key=lambda item: item["priority_score"], reverse=True)
        return ranked

    def _calculate_recency_factor(self, memory: Any, reference_time: datetime) -> float:
        """Convert memory age into a normalized recency score where recent=1.0."""
        timestamp = getattr(memory, "timestamp", None)
        if not timestamp:
            return 0.0

        age_days = max((reference_time - timestamp).days, 0)
        # Half-life style decay over ~5 years for light recency influence.
        decay_window_days = 365 * 5
        recency = max(0.0, 1.0 - (age_days / decay_window_days))
        return round(min(recency, 1.0), 3)
