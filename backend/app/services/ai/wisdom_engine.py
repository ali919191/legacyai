from collections import Counter
from typing import Any, Dict, List

from ..memory_capture_service import Memory


class WisdomEngine:
    """Transforms memories into generalized lessons, principles, and advice."""

    def __init__(self):
        self.failure_keywords = {
            "failed",
            "failure",
            "regret",
            "mistake",
            "setback",
            "lost",
            "missed",
            "hard way",
            "should have",
        }
        self.success_keywords = {
            "success",
            "achieved",
            "promotion",
            "graduated",
            "won",
            "proud",
            "accomplished",
            "milestone",
        }
        self.major_event_tags = {
            "marriage",
            "family",
            "career",
            "retirement",
            "education",
            "milestone",
            "birth",
            "death",
            "graduation",
        }

    def extract_lesson(self, memory: Memory) -> Dict[str, Any]:
        """Extract a single life lesson from one memory."""
        text = f"{memory.title} {memory.description}".lower()
        tags = {tag.lower() for tag in memory.tags}
        emotions = {emotion.lower() for emotion in memory.emotions}

        category = "emotional_experience"
        lesson = "Stay present and value meaningful moments with people who matter."

        has_failure_signal = bool(tags & {"regret", "failure", "mistake"}) or any(
            kw in text for kw in self.failure_keywords
        )
        has_success_signal = bool(tags & {"success", "achievement", "milestone"}) or any(
            kw in text for kw in self.success_keywords
        )
        has_major_event_signal = bool(tags & self.major_event_tags)
        emotional_intensity = len(emotions) >= 2 or any(
            e in {"grief", "joy", "love", "fear", "pride", "gratitude", "sadness"}
            for e in emotions
        )

        if has_failure_signal:
            category = "failure"
            lesson = "Speak up early, adapt quickly, and treat setbacks as feedback for growth."
        elif has_success_signal:
            category = "success"
            lesson = "Consistent effort and strong relationships create lasting success."
        elif has_major_event_signal:
            category = "major_life_event"
            lesson = "Major life transitions are best handled with preparation and trusted support."
        elif emotional_intensity:
            category = "emotional_experience"
            lesson = "Strong emotions often mark what matters most and should guide priorities."

        return {
            "memory_id": memory.id,
            "category": category,
            "lesson": lesson,
            "evidence": {
                "title": memory.title,
                "tags": memory.tags,
                "emotions": memory.emotions,
            },
        }

    def identify_patterns(self, memories: List[Memory]) -> List[Dict[str, Any]]:
        """Identify repeated lesson categories across memories."""
        if not memories:
            return []

        extracted = [self.extract_lesson(memory) for memory in memories]
        category_counts = Counter(item["category"] for item in extracted)

        patterns = []
        for category, count in category_counts.most_common():
            memory_ids = [item["memory_id"] for item in extracted if item["category"] == category]
            patterns.append(
                {
                    "pattern": category,
                    "count": count,
                    "memory_ids": memory_ids,
                    "sample_lesson": next(
                        item["lesson"] for item in extracted if item["category"] == category
                    ),
                }
            )

        return patterns

    def generate_principle(self, lessons: List[Dict[str, Any]]) -> List[str]:
        """Convert lesson clusters into generalized life principles."""
        if not lessons:
            return []

        categories = Counter(lesson.get("category", "") for lesson in lessons)
        principles = []

        if categories.get("failure", 0):
            principles.append("Learn quickly from setbacks and take action before problems compound.")
        if categories.get("success", 0):
            principles.append("Protect daily discipline because small consistent actions shape outcomes.")
        if categories.get("major_life_event", 0):
            principles.append("For major transitions, plan ahead and lean on trusted relationships.")
        if categories.get("emotional_experience", 0):
            principles.append("Use emotionally significant moments to clarify long-term priorities.")

        if not principles:
            principles.append("Reflect on experience, identify patterns, and make the next choice more intentional.")

        return principles

    def generate_advice(self, question: str, principles: List[str]) -> str:
        """Generate advice response grounded in distilled life principles."""
        if not principles:
            return "I don't have enough lived examples to offer clear advice yet."

        top_principles = principles[:2]
        guidance = " ".join(top_principles)
        return (
            "Based on what life taught me, here is my advice: "
            f"{guidance} For your situation ({question.strip()}), start with one practical step today "
            "and review what you learn before taking the next step."
        )