from typing import Any, Dict, List


class MemoryGroundingService:
    """Build grounded context and prompts so responses stay tied to stored memories."""

    def build_context_packet(self, memories: List[Any]) -> Dict[str, Any]:
        """Build a compact, serializable context packet from validated memories."""
        packet = {
            "memory_count": 0,
            "memory_ids": [],
            "grounded_facts": [],
        }

        for memory in memories:
            packet["memory_count"] += 1
            packet["memory_ids"].append(getattr(memory, "id", ""))
            packet["grounded_facts"].append(
                {
                    "id": getattr(memory, "id", ""),
                    "title": getattr(memory, "title", ""),
                    "description": getattr(memory, "description", ""),
                    "timestamp": getattr(memory, "timestamp", None).isoformat()
                    if getattr(memory, "timestamp", None)
                    else None,
                    "people_involved": list(getattr(memory, "people_involved", []) or []),
                    "location": getattr(memory, "location", ""),
                    "emotions": list(getattr(memory, "emotions", []) or []),
                    "tags": list(getattr(memory, "tags", []) or []),
                }
            )

        return packet

    def validate_memory_sources(self, memories: List[Any]) -> List[Any]:
        """Filter to memories with minimum usable fields and deduplicate by ID."""
        validated: List[Any] = []
        seen_ids = set()

        for memory in memories:
            memory_id = getattr(memory, "id", None)
            title = getattr(memory, "title", None)
            description = getattr(memory, "description", None)
            timestamp = getattr(memory, "timestamp", None)
            if not memory_id or memory_id in seen_ids:
                continue
            if not title or not description or not timestamp:
                continue

            seen_ids.add(memory_id)
            validated.append(memory)

        return validated

    def generate_grounded_prompt(self, question: str, memories: List[Any]) -> str:
        """Create a strict prompt that only allows using supplied memory evidence."""
        context_packet = self.build_context_packet(memories)

        memory_lines = []
        for fact in context_packet["grounded_facts"]:
            memory_lines.append(
                f"- [{fact['id']}] {fact['timestamp']}: {fact['title']} | "
                f"{fact['description']} | People: {', '.join(fact['people_involved']) or 'none'} | "
                f"Location: {fact['location'] or 'unknown'} | "
                f"Emotions: {', '.join(fact['emotions']) or 'none'} | "
                f"Tags: {', '.join(fact['tags']) or 'none'}"
            )

        evidence_block = "\n".join(memory_lines) if memory_lines else "- No valid memory evidence available."

        return f"""You are Legacy AI. Answer using ONLY the supplied memory evidence.

Strict grounding rules:
1. Do not invent names, events, dates, or details not explicitly present in memory evidence.
2. If evidence is insufficient for part of the question, say so clearly.
3. Keep response anchored to cited memory IDs when possible.

User question: {question}

Memory evidence:
{evidence_block}

Grounded answer:"""
