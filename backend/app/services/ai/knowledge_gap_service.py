from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import re

from ..memory_capture_service import MemoryCaptureService, Memory
from ..entity.person_profile_service import PersonProfileService


class KnowledgeGapService:
    """Detect missing context and manage enhanced follow-up questions."""

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        person_profile_service: Optional[PersonProfileService] = None,
    ):
        self.memory_service = memory_service
        self.person_profile_service = person_profile_service
        self._questions: Dict[str, Dict[str, Any]] = {}
        self._question_sequence = 1

    def detect_missing_context(self, conversation_text: str) -> Dict[str, Any]:
        """
        Detect likely knowledge gaps from free-style conversation text.

        Returns a context object consumed by generate_followup_questions().
        """
        memories = self.memory_service.retrieve_all_memories()
        known_people = {
            person.strip().lower()
            for memory in memories
            for person in (memory.people_involved or [])
            if person and person.strip()
        }
        if self.person_profile_service:
            for profile in self.person_profile_service.search_person_by_name(""):
                if profile.get("name"):
                    known_people.add(profile["name"].strip().lower())

        unknown_people = []
        # Capture capitalized names while avoiding sentence starters like I/We/The.
        candidate_names = re.findall(r"\b[A-Z][a-z]+\b", conversation_text)
        for name in candidate_names:
            lowered = name.lower()
            if lowered not in known_people and lowered not in {"i", "we", "the", "my", "our"}:
                if not any(person["name"] == name for person in unknown_people):
                    person_id = ""
                    if self.person_profile_service:
                        profile = self.person_profile_service.create_temporary_profile(
                            name=name,
                            context_description=(
                                f"Temporary profile created from conversation: {conversation_text}"
                            ),
                        )
                        person_id = profile["person_id"]
                    unknown_people.append({"name": name, "person_id": person_id})

        incomplete_memories = []
        for memory in memories:
            missing_fields = []
            if not memory.people_involved:
                missing_fields.append("people_involved")
            if not memory.location:
                missing_fields.append("location")
            if not memory.emotions:
                missing_fields.append("emotions")
            if not memory.tags:
                missing_fields.append("tags")
            if not memory.time_of_day or not memory.day_of_week:
                missing_fields.append("temporal_context")

            if missing_fields:
                incomplete_memories.append(
                    {
                        "memory_id": memory.id,
                        "title": memory.title,
                        "missing_fields": missing_fields,
                    }
                )

        contextual_gaps = []
        lowered_text = conversation_text.lower()
        # If story references event timing loosely, ask for richer temporal detail.
        if any(token in lowered_text for token in ["that day", "later", "then", "after"]):
            contextual_gaps.append("temporal_details")
        if "friend" in lowered_text and "name" not in lowered_text:
            contextual_gaps.append("relationship_identity")

        return {
            "conversation_text": conversation_text,
            "detected_at": datetime.now().isoformat(),
            "unknown_people": unknown_people,
            "incomplete_memories": incomplete_memories,
            "contextual_gaps": contextual_gaps,
        }

    def generate_followup_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate follow-up questions from a missing-context analysis context."""
        questions: List[Dict[str, Any]] = []
        source_timestamp = context.get("detected_at", datetime.now().isoformat())

        for person in context.get("unknown_people", []):
            person_name = person["name"] if isinstance(person, dict) else str(person)
            person_id = person.get("person_id", "") if isinstance(person, dict) else ""
            questions.append(
                {
                    "question": f"Who was {person_name}?",
                    "related_memory_id": "",
                    "person_id": person_id,
                    "source_conversation_timestamp": source_timestamp,
                    "context_description": (
                        f"User mentioned {person_name} during free-style storytelling without prior context"
                    ),
                    "priority": "medium",
                    "status": "pending",
                }
            )

        for memory_gap in context.get("incomplete_memories", [])[:5]:
            memory_id = memory_gap["memory_id"]
            title = memory_gap["title"]
            missing = set(memory_gap["missing_fields"])

            if "people_involved" in missing:
                questions.append(
                    {
                        "question": f"Who else was involved in '{title}'?",
                        "related_memory_id": memory_id,
                        "source_conversation_timestamp": source_timestamp,
                        "context_description": f"Memory '{title}' is missing people details",
                        "priority": "medium",
                        "status": "pending",
                    }
                )
            if "location" in missing:
                questions.append(
                    {
                        "question": f"Where did '{title}' take place?",
                        "related_memory_id": memory_id,
                        "source_conversation_timestamp": source_timestamp,
                        "context_description": f"Memory '{title}' is missing location",
                        "priority": "low",
                        "status": "pending",
                    }
                )
            if "temporal_context" in missing:
                questions.append(
                    {
                        "question": (
                            f"Do you remember what time of day '{title}' happened "
                            "and when it started or ended?"
                        ),
                        "related_memory_id": memory_id,
                        "source_conversation_timestamp": source_timestamp,
                        "context_description": f"Memory '{title}' is missing temporal context",
                        "priority": "medium",
                        "status": "pending",
                    }
                )

        if "temporal_details" in context.get("contextual_gaps", []):
            questions.append(
                {
                    "question": "Do you remember the day of week or approximate time this happened?",
                    "related_memory_id": "",
                    "source_conversation_timestamp": source_timestamp,
                    "context_description": "Story references sequence without concrete temporal details",
                    "priority": "low",
                    "status": "pending",
                }
            )

        return questions

    def store_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a generated question for the Enhanced Questions widget."""
        question_id = f"gap_{self._question_sequence:03d}"
        self._question_sequence += 1

        record = {
            "question_id": question_id,
            "question": question_data.get("question", ""),
            "related_memory_id": question_data.get("related_memory_id", ""),
            "source_conversation_timestamp": question_data.get(
                "source_conversation_timestamp", datetime.now().isoformat()
            ),
            "context_description": question_data.get("context_description", ""),
            "priority": question_data.get("priority", "medium"),
            "status": question_data.get("status", "pending"),
            "user_id": question_data.get("user_id", "anonymous"),
            "person_id": question_data.get("person_id", ""),
            "answer": question_data.get("answer"),
            "answered_timestamp": question_data.get("answered_timestamp"),
        }
        self._questions[question_id] = record
        return record

    def retrieve_pending_questions(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve pending follow-up questions for a user."""
        pending = [
            q for q in self._questions.values()
            if q.get("user_id") == user_id and q.get("status") == "pending"
        ]
        return sorted(pending, key=lambda q: q["source_conversation_timestamp"])

    def answer_question(
        self,
        question_id: str,
        answer_text: str,
        memory_updates: Optional[Dict[str, Any]] = None,
        person_updates: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Mark a question as answered and enrich the related memory when possible.

        This stores new knowledge and supports the Enhanced Questions completion flow.
        """
        record = self._questions.get(question_id)
        if not record:
            return None

        record["status"] = "answered"
        record["answer"] = answer_text
        record["answered_timestamp"] = datetime.now().isoformat()

        person_id = record.get("person_id")
        if person_id and self.person_profile_service:
            updates = person_updates or {}
            if not updates:
                updates = {
                    "description": answer_text,
                    "confidence_score": 0.7,
                }
            self.person_profile_service.update_person_profile(person_id, updates)

        related_memory_id = record.get("related_memory_id")
        if related_memory_id:
            memory = self.memory_service.retrieve_memory(related_memory_id)
            if memory:
                updates = memory_updates or {}

                # If no explicit updates are passed, preserve answer as narrative enrichment.
                if not updates:
                    enriched_description = memory.description.strip()
                    if enriched_description:
                        enriched_description += f"\n\nAdditional context: {answer_text}"
                    else:
                        enriched_description = f"Additional context: {answer_text}"
                    updates = {"description": enriched_description}

                self.memory_service.update_memory(
                    related_memory_id,
                    title=updates.get("title"),
                    description=updates.get("description"),
                    people_involved=updates.get("people_involved"),
                    location=updates.get("location"),
                    emotions=updates.get("emotions"),
                    tags=updates.get("tags"),
                    time_of_day=updates.get("time_of_day"),
                    start_time=updates.get("start_time"),
                    end_time=updates.get("end_time"),
                    day_of_week=updates.get("day_of_week"),
                )

        return record
