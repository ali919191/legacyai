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

        self.query_intent_keywords = {
            "failure": {"failure", "fail", "mistake", "regret", "setback", "wrong"},
            "career": {"career", "job", "work", "office", "promotion", "manager", "engineer"},
            "relationships": {"relationship", "family", "marriage", "wife", "husband", "son", "daughter", "friend"},
            "discipline": {"discipline", "consistent", "habit", "routine", "focus", "practice"},
            "growth": {"grow", "growth", "learn", "become", "shape", "improve", "change"},
        }

        self.principle_catalog = {
            "failure": "Failure is a necessary part of growth.",
            "career": "Career progress comes from learning, communication, and long-term consistency.",
            "relationships": "Strong relationships require empathy, presence, and honest communication.",
            "discipline": "Consistency in small daily actions creates lasting results.",
            "growth": "Personal growth comes from reflection, adaptation, and persistence.",
            "major_life_event": "Major transitions are easier when you prepare early and lean on trusted people.",
            "emotional_experience": "Emotionally significant moments reveal what matters most.",
            "success": "Success compounds when discipline and relationships move together.",
        }

    def classify_query_intent(self, question: str) -> str:
        """Classify user advice question into a coarse intent category."""
        query = question.lower()
        scores = {}
        for intent, keywords in self.query_intent_keywords.items():
            scores[intent] = sum(1 for keyword in keywords if keyword in query)

        best_intent = max(scores, key=scores.get)
        return best_intent if scores[best_intent] > 0 else "growth"

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
        return [item["text"] for item in self.generate_categorized_principles(lessons)]

    def generate_categorized_principles(self, lessons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate principle records with text/category/weight for contextual selection."""
        if not lessons:
            return [
                {
                    "text": "Reflect on experience, identify patterns, and make the next choice more intentional.",
                    "category": "growth",
                    "weight": 1,
                }
            ]

        categories = Counter(lesson.get("category", "") for lesson in lessons)
        principles: List[Dict[str, Any]] = []
        for category, count in categories.items():
            mapped = category
            if category == "major_life_event":
                mapped = "relationships"
            elif category == "emotional_experience":
                mapped = "growth"

            principle_text = self.principle_catalog.get(
                category,
                self.principle_catalog.get(mapped, "Reflect on experience, identify patterns, and make the next choice more intentional."),
            )
            principles.append({"text": principle_text, "category": mapped, "weight": count})

        principles.sort(key=lambda item: item["weight"], reverse=True)
        return principles

    def select_principles_for_query(
        self,
        question: str,
        categorized_principles: List[Dict[str, Any]],
        max_items: int = 3,
    ) -> List[str]:
        """Select top context-relevant principles using classified query intent."""
        if not categorized_principles:
            return []

        intent = self.classify_query_intent(question)
        matching = [
            item for item in categorized_principles
            if item.get("category") == intent
        ]
        fallback = [
            item for item in categorized_principles
            if item.get("category") != intent
        ]

        ordered = matching + fallback
        selected: List[str] = []
        for item in ordered:
            text = item.get("text", "").strip()
            if text and text not in selected:
                selected.append(text)
            if len(selected) >= max_items:
                break

        return selected

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