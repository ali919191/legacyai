import logging
from typing import List, Dict, Any, Optional
from ..memory_capture_service import MemoryCaptureService, Memory
from ..timeline_engine import TimelineEngine
from ..memory.memory_embedding_service import MemoryEmbeddingService
from ..entity.person_profile_service import PersonProfileService
from ..entity.relationship_service import RelationshipService
from .personality_model_service import PersonalityProfile
from .memory_distillation_service import MemoryDistillationService, DistilledInsight
from .knowledge_gap_service import KnowledgeGapService
from .memory_grounding_service import MemoryGroundingService
from .memory_priority_service import MemoryPriorityService
from .recipient_context_service import RecipientContextService
from ..security.legacy_access_service import LegacyAccessService, MemoryMetadata
from ..security.response_moderation_service import ResponseModerationService

logger = logging.getLogger(__name__)


class ConversationEngine:
    """
    Conversation Engine for the Legacy AI platform.

    This engine allows family members to ask questions and receive responses
    generated from stored memories. It integrates with memory services to find
    relevant experiences and construct meaningful answers.

    The engine combines:
    - Retrieved memories for specific context
    - Personality profile for authentic responses
    - Distilled insights for wisdom-based guidance
    - LegacyAccessService for access control and privacy protection
    """

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        timeline_engine: TimelineEngine,
        embedding_service: MemoryEmbeddingService,
        person_profile_service: Optional[PersonProfileService] = None,
        relationship_service: Optional[RelationshipService] = None,
        personality_profile: Optional[PersonalityProfile] = None,
        distillation_service: Optional[MemoryDistillationService] = None,
        knowledge_gap_service: Optional[KnowledgeGapService] = None,
        memory_grounding_service: Optional[MemoryGroundingService] = None,
        memory_priority_service: Optional[MemoryPriorityService] = None,
        recipient_context_service: Optional[RecipientContextService] = None,
        access_service: Optional[LegacyAccessService] = None,
        moderation_service: Optional[ResponseModerationService] = None
    ):
        """
        Initialize the Conversation Engine.

        Args:
            memory_service: Instance of MemoryCaptureService for accessing stored memories.
            timeline_engine: Instance of TimelineEngine for chronological context.
            embedding_service: Instance of MemoryEmbeddingService for semantic search.
            person_profile_service: Optional PersonProfileService for entity profile tracking.
            relationship_service: Optional RelationshipService for entity relationship graph tracking.
            personality_profile: Optional PersonalityProfile for personalized responses.
            distillation_service: Optional MemoryDistillationService for wisdom insights.
            knowledge_gap_service: Optional KnowledgeGapService for missing-context follow-up questions.
            memory_grounding_service: Optional MemoryGroundingService for prompt grounding and source validation.
            memory_priority_service: Optional MemoryPriorityService for ranking retrieved memories.
            access_service: Optional LegacyAccessService for access control and privacy.
            moderation_service: Optional ResponseModerationService for response safety.
        """
        self.memory_service = memory_service
        self.timeline_engine = timeline_engine
        self.embedding_service = embedding_service
        self.person_profile_service = person_profile_service
        self.relationship_service = relationship_service
        self.personality_profile = personality_profile
        self.distillation_service = distillation_service
        self.knowledge_gap_service = knowledge_gap_service
        self.memory_grounding_service = memory_grounding_service
        self.memory_priority_service = memory_priority_service
        self.recipient_context_service = recipient_context_service
        self.access_service = access_service
        self.moderation_service = moderation_service

    def generate_response(self, user_query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response to the user's query based on relevant memories.

        Workflow:
        1. Use MemoryEmbeddingService to find similar memories via semantic search.
        2. Apply access control filtering if LegacyAccessService is available.
        3. Use TimelineEngine to add chronological context.
        4. Build context object with memory information.
        5. Add distilled insights if available.
        6. Construct AI prompt and generate response (placeholder for now).
        7. Return structured response.

        Args:
            user_query: The user's question or query string.
            user_id: Optional user ID for access control (required if access_service is used).

        Returns:
            Dict containing:
            - 'generated_answer': The AI-generated response text.
            - 'memories_used': List of memory IDs used in the response.
            - 'insights_used': List of distilled insight texts used.
            - 'confidence_score': Float between 0-1 indicating response confidence.
            - 'access_denied': Boolean indicating if access was denied for some memories.
        """
        # Step 1: Semantic search for relevant memories; fall back to all memories
        # when the vector store is empty (e.g. no embeddings have been indexed yet).
        similar_memories = self.embedding_service.search_similar_memories(user_query, top_k=5)
        if not similar_memories:
            all_memories = self.memory_service.retrieve_all_memories()
            similar_memories = [(m.id, 0.5) for m in all_memories[:5]]
        memory_ids = [mem_id for mem_id, _ in similar_memories]

        # Step 2: Retrieve full memory objects
        relevant_memories = []
        access_denied = False

        for mem_id in memory_ids:
            memory = self.memory_service.retrieve_memory(mem_id)
            if memory:
                # Apply access control if service is available
                if self.access_service and user_id:
                    # Create memory metadata for access control
                    memory_metadata = MemoryMetadata(
                        memory_id=memory.id,
                        sensitivity_tags=memory.sensitivity_tags or [],
                        created_date=memory.timestamp.isoformat() if hasattr(memory.timestamp, 'isoformat') else str(memory.timestamp),
                        is_legacy_active=True  # Assume legacy is active for now
                    )

                    if self.access_service.authorize_memory_access(user_id, memory_metadata):
                        relevant_memories.append(memory)
                    else:
                        access_denied = True
                else:
                    # No access control, include all memories
                    relevant_memories.append(memory)

        # Step 3: Re-rank memories by importance and emotional weight when available.
        memory_priority = []
        if self.memory_priority_service and relevant_memories:
            memory_priority = self.memory_priority_service.rank_memories(relevant_memories)
            relevant_memories = [item["memory"] for item in memory_priority]

        # Step 3b: Extract family profiles from conversation and resolve recipient context.
        extracted_family_profiles: List[Dict[str, Any]] = []
        if self.recipient_context_service:
            extracted_family_profiles = self.recipient_context_service.extract_family_profiles_from_conversation(
                user_query
            )

        # Step 3c: Resolve recipient context so every response is recipient-aware.
        recipient_profile = self._resolve_recipient_profile(user_id)
        recipient_context_text = self._build_recipient_context_text(recipient_profile)

        # Step 4: Validate memories for grounding and keep ranking aligned.
        grounded_memories = relevant_memories
        if self.memory_grounding_service:
            grounded_memories = self.memory_grounding_service.validate_memory_sources(relevant_memories)
            grounded_ids = {memory.id for memory in grounded_memories}
            if memory_priority:
                memory_priority = [
                    item for item in memory_priority if item["memory"].id in grounded_ids
                ]
            relevant_memories = grounded_memories

        # Step 5: Add chronological context using TimelineEngine
        chronological_context = self.timeline_engine.get_chronological_timeline()
        # Filter chronological context to only include relevant memories
        prioritized_ids = [memory.id for memory in relevant_memories]
        relevant_chronological = [mem for mem in chronological_context if mem.id in prioritized_ids]

        # Step 6: Build context object
        context = self._build_context(relevant_memories, relevant_chronological, memory_priority)

        if self.memory_grounding_service:
            context["grounding_packet"] = self.memory_grounding_service.build_context_packet(
                relevant_memories
            )

        context["recipient_profile"] = recipient_profile

        if self.person_profile_service:
            context["person_profiles"] = self._get_related_person_profiles(
                user_query=user_query,
                relevant_memories=relevant_memories,
            )

        if self.relationship_service:
            context["relationships"] = self._get_related_relationships(
                user_query=user_query,
                relevant_memories=relevant_memories,
            )
            self.relationship_service.detect_relationships_from_conversation(user_query)

        # Step 7: Add distilled insights if service is available
        relevant_insights = []
        if self.distillation_service:
            relevant_insights = self._get_relevant_insights(user_query, relevant_memories)
            context['distilled_insights'] = [insight.to_dict() for insight in relevant_insights]

        # Step 8: If this is an advice-oriented question, build wisdom from lived experience.
        wisdom_context: Dict[str, Any] = {}
        if self._is_advice_oriented_query(user_query) and self.distillation_service and relevant_memories:
            lessons = self.distillation_service.extract_wisdom_lessons(relevant_memories)
            if lessons:
                lesson_lines = "\n".join(
                    f"  * {item.get('lesson', '').strip()}" for item in lessons if item.get("lesson")
                )
                logger.info("LESSONS EXTRACTED:\n%s", lesson_lines or "  * NONE")
            else:
                logger.info("LESSONS EXTRACTED: NONE")

            # Use WisdomEngine directly when available to make the integration explicit.
            # Fall back to distillation_service.generate_advice_from_experiences for compatibility.
            wisdom_engine = getattr(self.distillation_service, "wisdom_engine", None)
            if wisdom_engine:
                patterns = wisdom_engine.identify_patterns(relevant_memories)
                principles = wisdom_engine.generate_principle(lessons)
                advice = wisdom_engine.generate_advice(user_query, principles)
                wisdom_context = {
                    "lessons": lessons,
                    "patterns": patterns,
                    "principles": principles,
                    "advice": advice,
                }
            else:
                wisdom_context = self.distillation_service.generate_advice_from_experiences(
                    user_query,
                    relevant_memories,
                )
            context['wisdom'] = wisdom_context

        # Step 9: Detect knowledge gaps and create follow-up questions for widget display.
        generated_question_records = []
        if self.knowledge_gap_service:
            gap_context = self.knowledge_gap_service.detect_missing_context(user_query)
            followup_questions = self.knowledge_gap_service.generate_followup_questions(gap_context)
            for question in followup_questions:
                question["user_id"] = user_id or "anonymous"
                generated_question_records.append(
                    self.knowledge_gap_service.store_question(question)
                )

        # Step 10: Construct prompt and generate response (always memory-grounded)
        if not relevant_memories:
            logger.info(
                "Generated response for user=%s. MEMORIES USED: NONE",
                user_id or "anonymous",
            )
            response = "I don't remember that clearly."
        else:
            prompt = self._construct_prompt(user_query, context)
            response = self._generate_ai_response(prompt, context=context)
            mem_trace = "\n".join(
                f"  * {m.id}: {m.title}" for m in relevant_memories
            )
            logger.info(
                "Generated response for user=%s using %d memories:\n%s",
                user_id or "anonymous",
                len(relevant_memories),
                mem_trace,
            )

        # Step 10b: Adjust for recipient age/relationship on sensitive topics.
        response = self._apply_recipient_safety(response, recipient_profile, relevant_memories)

        # Step 11: Review response through moderation layer (if available)
        moderation_result = None
        if self.moderation_service:
            moderated_response = self.moderation_service.adjust_response_if_needed(response)
            moderation_result = self.moderation_service.review_response(response)
            response = moderated_response

        # Step 12: Calculate confidence based on similarity scores and insights
        confidence = self._calculate_confidence(similar_memories, relevant_insights)

        wisdom_lessons = [item.get("lesson", "") for item in wisdom_context.get("lessons", [])]
        wisdom_principles = wisdom_context.get("principles", [])
        combined_insights = [insight.insight_text for insight in relevant_insights] + wisdom_principles

        return {
            'generated_answer': response,
            'memories_used': [mem.id for mem in relevant_memories],
            'memory_details': [
                {'id': mem.id, 'title': mem.title}
                for mem in relevant_memories
            ],
            'memory_priority': [
                {
                    'memory_id': item['memory'].id,
                    'importance_score': item['importance_score'],
                    'emotional_weight': item['emotional_weight'],
                    'recency_factor': item['recency_factor'],
                    'priority_score': item['priority_score'],
                }
                for item in memory_priority
            ],
            'insights_used': combined_insights,
            'lessons_used': wisdom_lessons,
            'wisdom_principles': wisdom_principles,
            'confidence_score': confidence,
            'access_denied': access_denied,
            'moderation': moderation_result,
            'enhanced_questions': generated_question_records,
            'recipient_context': recipient_profile,
            'extracted_family_profiles': extracted_family_profiles,
        }

    def _is_advice_oriented_query(self, user_query: str) -> bool:
        """Return True when the query asks for advice, lessons, or guidance."""
        advice_triggers = {
            "advice",
            "what advice",
            "what should",
            "what should i do",
            "what would you do",
            "how should",
            "how should i handle",
            "guidance",
            "lesson",
            "recommend",
            "best way",
            "tell me what to do",
        }
        query_lower = user_query.lower()
        return any(trigger in query_lower for trigger in advice_triggers)

    def answer_enhanced_question(
        self,
        question_id: str,
        answer_text: str,
        memory_updates: Optional[Dict[str, Any]] = None,
        person_updates: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Answer a stored enhanced question and enrich the related memory."""
        if not self.knowledge_gap_service:
            return None
        return self.knowledge_gap_service.answer_question(
            question_id=question_id,
            answer_text=answer_text,
            memory_updates=memory_updates,
            person_updates=person_updates,
        )

    def _build_context(
        self,
        memories: List[Memory],
        chronological: List[Memory],
        memory_priority: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Build a context object from relevant memories.

        Args:
            memories: List of relevant Memory objects.
            chronological: Chronologically sorted relevant memories.

        Returns:
            Dict with context information including descriptions, timestamps, tags, emotions.
        """
        context = {
            'memories': [],
            'chronological_order': [],
            'emotions': set(),
            'tags': set(),
            'time_range': {},
            'person_profiles': [],
            'relationships': [],
            'memory_priority': [],
        }

        priority_lookup: Dict[str, Dict[str, Any]] = {}
        if memory_priority:
            priority_lookup = {
                item["memory"].id: {
                    "importance_score": item["importance_score"],
                    "emotional_weight": item["emotional_weight"],
                    "recency_factor": item["recency_factor"],
                    "priority_score": item["priority_score"],
                }
                for item in memory_priority
            }

        for memory in memories:
            memory_info = {
                'id': memory.id,
                'title': memory.title,
                'description': memory.description,
                'timestamp': memory.timestamp.isoformat(),
                'people_involved': memory.people_involved,
                'location': memory.location,
                'emotions': memory.emotions,
                'tags': memory.tags
            }
            context['memories'].append(memory_info)
            context['emotions'].update(memory.emotions)
            context['tags'].update(memory.tags)

            if memory.id in priority_lookup:
                context['memory_priority'].append(
                    {
                        'id': memory.id,
                        **priority_lookup[memory.id],
                    }
                )

        # Chronological order
        context['chronological_order'] = [
            {'id': mem.id, 'timestamp': mem.timestamp.isoformat()}
            for mem in chronological
        ]

        # Time range
        if memories:
            timestamps = [mem.timestamp for mem in memories]
            context['time_range'] = {
                'earliest': min(timestamps).isoformat(),
                'latest': max(timestamps).isoformat()
            }

        context['emotions'] = list(context['emotions'])
        context['tags'] = list(context['tags'])

        return context

    def _construct_prompt(self, user_query: str, context: Dict[str, Any]) -> str:
        """
        Construct a prompt template for AI response generation.

        Args:
            user_query: The user's question.
            context: Context object with memory information.

        Returns:
            Formatted prompt string.
        """
        memory_lines = []
        for i, mem in enumerate(context['memories'], start=1):
            memory_lines.append(
                f"Memory {i}: [{mem['id']}] {mem['title']}\n"
                f"  Description: {mem['description']}\n"
                f"  Date: {mem['timestamp']}"
                f" | Location: {mem['location'] or 'unknown'}"
                f" | People: {', '.join(mem['people_involved']) or 'none'}"
                f" | Emotions: {', '.join(mem['emotions']) or 'none'}"
                f" | Tags: {', '.join(mem['tags']) or 'none'}"
            )
        memories_text = "\n".join(memory_lines)

        personality_text = ""
        if self.personality_profile:
            profile = self.personality_profile
            personality_text = f"""
Personality traits: {', '.join(profile.traits)}
Core beliefs: {', '.join(profile.core_beliefs)}
Communication style: {profile.communication_style.get('formality', 'neutral')} and {profile.communication_style.get('emotional_expression', 'balanced')}
Values: {', '.join(profile.values)}
Decision patterns: {', '.join(profile.decision_heuristics)}

Respond in a way that reflects these personality characteristics."""

        person_profile_text = ""
        if context.get("person_profiles"):
            person_profile_text = "\nKnown people related to these memories:\n" + "\n".join([
                f"- {profile['name']} (relationship: {profile.get('relationship_to_user') or 'unknown'}, "
                f"origin: {profile.get('origin') or 'unknown'}, memories linked: {len(profile.get('connected_memories', []))})"
                for profile in context["person_profiles"]
            ])

        recipient_text = ""
        if context.get("recipient_profile"):
            recipient_text = (
                "\nRecipient context: "
                + self._build_recipient_context_text(context["recipient_profile"])
            )

        wisdom_text = ""
        if context.get("wisdom"):
            principles = context["wisdom"].get("principles", [])
            lessons = context["wisdom"].get("lessons", [])
            lesson_lines = [
                f"- {item.get('lesson', '').strip()}"
                for item in lessons
                if item.get("lesson")
            ][:3]
            principle_lines = [f"- {text}" for text in principles[:3]]
            wisdom_text = (
                "\nWisdom distilled from these same memories:\n"
                + ("Principles:\n" + "\n".join(principle_lines) + "\n" if principle_lines else "")
                + ("Lessons:\n" + "\n".join(lesson_lines) + "\n" if lesson_lines else "")
            )

        prompt = f"""You are an AI representation of a person built from their life memories. You MUST use ONLY the memories below to answer the question. If the answer is not present in these memories, say "I don't remember that clearly." Do not use any knowledge outside of these memories.{personality_text}{person_profile_text}{recipient_text}{wisdom_text}

User's question: {user_query}

Relevant memories from my life:
{memories_text}

Please answer the question using ONLY these memories. If the memories do not contain relevant information, say "I don't remember that clearly." Be conversational and authentic, as if sharing personal stories."""

        return prompt

    def _get_related_person_profiles(
        self,
        user_query: str,
        relevant_memories: List[Memory],
    ) -> List[Dict[str, Any]]:
        """Collect known person profiles connected to the current query and memories."""
        if not self.person_profile_service:
            return []

        profile_map: Dict[str, Dict[str, Any]] = {}
        for memory in relevant_memories:
            for person_name in memory.people_involved:
                for profile in self.person_profile_service.search_person_by_name(person_name):
                    profile_map[profile["person_id"]] = profile

        for token in user_query.split():
            clean_token = token.strip(",.?!:;\"'()")
            if clean_token[:1].isupper():
                for profile in self.person_profile_service.search_person_by_name(clean_token):
                    profile_map[profile["person_id"]] = profile

        return list(profile_map.values())

    def _get_related_relationships(
        self,
        user_query: str,
        relevant_memories: List[Memory],
    ) -> List[Dict[str, Any]]:
        """Collect relationship graph edges for people seen in the current context."""
        if not self.relationship_service or not self.person_profile_service:
            return []

        related_person_ids = set()
        for memory in relevant_memories:
            for person_name in memory.people_involved:
                for profile in self.person_profile_service.search_person_by_name(person_name):
                    related_person_ids.add(profile["person_id"])

        for token in user_query.split():
            clean_token = token.strip(",.?!:;\"'()")
            if clean_token[:1].isupper():
                for profile in self.person_profile_service.search_person_by_name(clean_token):
                    related_person_ids.add(profile["person_id"])

        relationship_map: Dict[str, Dict[str, Any]] = {}
        for person_id in related_person_ids:
            for relationship in self.relationship_service.retrieve_relationships_for_person(person_id):
                relationship_map[relationship["relationship_id"]] = relationship

        return list(relationship_map.values())

    def _generate_ai_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response grounded in the provided memory context.

        Synthesises a first-person narrative from the highest-priority memories
        found in *context*. The *prompt* string is accepted for
        forward-compatibility: when an LLM integration is added (OpenAI, Azure
        OpenAI, local model, etc.) replace this method body with an API call
        that sends *prompt* directly to the model.

        Args:
            prompt: Fully-constructed, memory-grounded prompt string.
            context: Optional context dict produced by _build_context, containing
                     'memories' and 'memory_priority' lists.

        Returns:
            Response text synthesised from memory content, or
            "I don't remember that clearly." when no memory data is available.
        """
        if not context or not context.get("memories"):
            return "I don't remember that clearly."

        memories = list(context["memories"])

        # Sort by priority score when priority data is available
        priority_lookup: Dict[str, float] = {
            p["id"]: p["priority_score"]
            for p in context.get("memory_priority", [])
        }
        if priority_lookup:
            memories = sorted(
                memories,
                key=lambda m: priority_lookup.get(m["id"], 0.0),
                reverse=True,
            )

        top_memories = memories[:3]
        if not top_memories:
            logger.info("MEMORIES USED in response synthesis: NONE")
            return "I don't remember that clearly."

        mem_trace_lines = "\n".join(
            f"  * {m['id']}: {m.get('title', 'untitled')}" for m in top_memories
        )
        logger.info("MEMORIES USED in response synthesis:\n%s", mem_trace_lines)

        intro_phrases = ["I remember", "I recall", "There was a time when"]
        sentences: List[str] = []

        for idx, mem in enumerate(top_memories):
            title: str = mem.get("title", "")
            description: str = mem.get("description", "")
            location: str = mem.get("location", "") or ""
            people: List[str] = mem.get("people_involved", []) or []
            emotions: List[str] = mem.get("emotions", []) or []

            raw_text = description or title
            if not raw_text:
                continue

            intro = intro_phrases[idx % len(intro_phrases)]
            sentence = f"{intro} {raw_text.rstrip('.')}."

            details: List[str] = []
            if location:
                details.append(f"at {location}")
            if len(people) == 1:
                details.append(f"with {people[0]}")
            elif len(people) == 2:
                details.append(f"with {people[0]} and {people[1]}")
            elif len(people) > 2:
                details.append(f"with {', '.join(people[:-1])}, and {people[-1]}")

            if details:
                sentence = sentence.rstrip(".") + " " + ", ".join(details) + "."

            if emotions:
                emotion_str = " and ".join(emotions[:2])
                sentence += f" I felt {emotion_str}."

            sentences.append(sentence)

        if not sentences:
            return "I don't remember that clearly."

        response = " ".join(sentences)
        principles = context.get("wisdom", {}).get("principles", [])
        if principles:
            response += f" A guiding principle I learned is: {principles[0]}"

        return response

    def _get_relevant_insights(self, user_query: str, relevant_memories: List[Memory]) -> List[DistilledInsight]:
        """
        Get distilled insights relevant to the user query.

        Args:
            user_query: The user's question.
            relevant_memories: Memories that were found relevant to the query.

        Returns:
            List of relevant DistilledInsight objects.
        """
        if not self.distillation_service:
            return []

        # Get all types of insights from relevant memories
        all_insights = []
        all_insights.extend(self.distillation_service.distill_life_lessons(relevant_memories))
        all_insights.extend(self.distillation_service.extract_advice(relevant_memories))
        all_insights.extend(self.distillation_service.identify_recurring_patterns(relevant_memories))

        # Filter insights relevant to the query (simple keyword matching for now)
        query_lower = user_query.lower()
        relevant_insights = []

        for insight in all_insights:
            insight_text_lower = insight.insight_text.lower()
            # Check if query keywords appear in insight
            query_words = set(query_lower.split())
            insight_words = set(insight_text_lower.split())

            if query_words & insight_words:  # Intersection of words
                relevant_insights.append(insight)

        # Return top 3 most confident insights
        relevant_insights.sort(key=lambda x: x.confidence_score, reverse=True)
        return relevant_insights[:3]

    def _calculate_confidence(self, similar_memories: List[tuple], insights: Optional[List[DistilledInsight]] = None) -> float:
        """
        Calculate confidence score for the response.

        Based on average similarity score, number of memories, and insight quality.

        Args:
            similar_memories: List of (memory_id, similarity_score) tuples.
            insights: Optional list of distilled insights used.

        Returns:
            Confidence score between 0 and 1.
        """
        if not similar_memories:
            return 0.0

        avg_similarity = sum(score for _, score in similar_memories) / len(similar_memories)
        memory_count_factor = min(len(similar_memories) / 5.0, 1.0)  # Normalize to 0-1

        base_confidence = (avg_similarity + memory_count_factor) / 2.0

        # Boost confidence if insights are available
        insight_boost = 0.0
        if insights:
            avg_insight_confidence = sum(insight.confidence_score for insight in insights) / len(insights)
            insight_boost = avg_insight_confidence * 0.2  # 20% boost from insights

        confidence = base_confidence + insight_boost
        return min(confidence, 1.0)

    def _resolve_recipient_profile(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Resolve recipient profile or provide a safe default context."""
        if user_id and self.recipient_context_service:
            profile = self.recipient_context_service.retrieve_recipient_profile(user_id)
            if profile:
                return profile
        return {
            "user_id": user_id or "unknown",
            "name": "recipient",
            "relationship_to_user": "unknown",
            "age": 30,
            "age_bucket": "adult",
            "maturity_level": "adult",
            "topic_preferences": [],
            "known_children": [],
            "interaction_history": [],
        }

    def _build_recipient_context_text(self, recipient_profile: Dict[str, Any]) -> str:
        """Build prompt instruction with recipient relationship and maturity context."""
        relationship = recipient_profile.get("relationship_to_user", "unknown")
        age = recipient_profile.get("age", "unknown")
        age_bucket = recipient_profile.get("age_bucket", "adult")
        maturity = recipient_profile.get("maturity_level", "adult")
        return (
            f"The question is asked by the user's {relationship} who is {age} years old "
            f"(age bucket: {age_bucket}, maturity level: {maturity}). Adjust explanations accordingly."
        )

    def _apply_recipient_safety(
        self,
        response: str,
        recipient_profile: Dict[str, Any],
        relevant_memories: List[Memory],
    ) -> str:
        """Simplify or filter sensitive topics for younger recipients."""
        age_bucket = recipient_profile.get("age_bucket", "adult")
        maturity_level = recipient_profile.get("maturity_level", "adult")
        is_young = age_bucket in {"young_child", "child", "teenager"} or maturity_level in {"child", "teen"}
        if not is_young:
            return response

        sensitive_tags = {"medical", "financial", "intimate"}
        has_sensitive_memory = any(
            bool(set(memory.sensitivity_tags or []) & sensitive_tags)
            for memory in relevant_memories
        )

        if age_bucket in {"young_child", "child"} and has_sensitive_memory:
            return (
                "I'll keep this simple and safe: this topic is important, but some details are best "
                "shared when you're older."
            )

        if age_bucket in {"young_child", "child"}:
            return "Here is a simple version: " + response

        if age_bucket == "teenager" and has_sensitive_memory:
            return "Here is a careful summary: " + response

        return response