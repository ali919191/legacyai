from typing import List, Dict, Any, Optional
from ..memory_capture_service import MemoryCaptureService, Memory
from ..timeline_engine import TimelineEngine
from ..memory.memory_embedding_service import MemoryEmbeddingService
from .personality_model_service import PersonalityProfile
from .memory_distillation_service import MemoryDistillationService, DistilledInsight


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
    - LegacyAccessService for access control (future)
    """

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        timeline_engine: TimelineEngine,
        embedding_service: MemoryEmbeddingService,
        personality_profile: Optional[PersonalityProfile] = None,
        distillation_service: Optional[MemoryDistillationService] = None
    ):
        """
        Initialize the Conversation Engine.

        Args:
            memory_service: Instance of MemoryCaptureService for accessing stored memories.
            timeline_engine: Instance of TimelineEngine for chronological context.
            embedding_service: Instance of MemoryEmbeddingService for semantic search.
            personality_profile: Optional PersonalityProfile for personalized responses.
            distillation_service: Optional MemoryDistillationService for wisdom insights.
        """
        self.memory_service = memory_service
        self.timeline_engine = timeline_engine
        self.embedding_service = embedding_service
        self.personality_profile = personality_profile
        self.distillation_service = distillation_service

    def generate_response(self, user_query: str) -> Dict[str, Any]:
        """
        Generate a response to the user's query based on relevant memories.

        Workflow:
        1. Use MemoryEmbeddingService to find similar memories via semantic search.
        2. Use TimelineEngine to add chronological context.
        3. Build context object with memory information.
        4. Add distilled insights if available.
        5. Construct AI prompt and generate response (placeholder for now).
        6. Return structured response.

        Args:
            user_query: The user's question or query string.

        Returns:
            Dict containing:
            - 'generated_answer': The AI-generated response text.
            - 'memories_used': List of memory IDs used in the response.
            - 'insights_used': List of distilled insight texts used.
            - 'confidence_score': Float between 0-1 indicating response confidence.
        """
        # Step 1: Semantic search for relevant memories
        similar_memories = self.embedding_service.search_similar_memories(user_query, top_k=5)
        memory_ids = [mem_id for mem_id, _ in similar_memories]

        # Step 2: Retrieve full memory objects
        relevant_memories = []
        for mem_id in memory_ids:
            memory = self.memory_service.retrieve_memory(mem_id)
            if memory:
                relevant_memories.append(memory)

        # Step 3: Add chronological context using TimelineEngine
        chronological_context = self.timeline_engine.get_chronological_timeline()
        # Filter chronological context to only include relevant memories
        relevant_chronological = [mem for mem in chronological_context if mem.id in memory_ids]

        # Step 4: Build context object
        context = self._build_context(relevant_memories, relevant_chronological)

        # Step 5: Add distilled insights if service is available
        relevant_insights = []
        if self.distillation_service:
            relevant_insights = self._get_relevant_insights(user_query, relevant_memories)
            context['distilled_insights'] = [insight.to_dict() for insight in relevant_insights]

        # Step 6: Construct prompt and generate response
        prompt = self._construct_prompt(user_query, context)
        response = self._generate_ai_response(prompt)

        # Step 7: Calculate confidence based on similarity scores and insights
        confidence = self._calculate_confidence(similar_memories, relevant_insights)

        return {
            'generated_answer': response,
            'memories_used': memory_ids,
            'insights_used': [insight.insight_text for insight in relevant_insights],
            'confidence_score': confidence
        }

    def _build_context(self, memories: List[Memory], chronological: List[Memory]) -> Dict[str, Any]:
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
            'time_range': {}
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
        memories_text = "\n".join([
            f"- {mem['timestamp']}: {mem['title']} - {mem['description']} "
            f"(Location: {mem['location']}, People: {', '.join(mem['people_involved'])}, "
            f"Emotions: {', '.join(mem['emotions'])}, Tags: {', '.join(mem['tags'])})"
            for mem in context['memories']
        ])

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

        prompt = f"""You are an AI representation of a person built from their life memories. Use the memories below to answer the user's question.{personality_text}

User's question: {user_query}

Relevant memories from my life:
{memories_text}

Please answer the question using these memories. Be conversational and authentic, as if sharing personal stories."""

        return prompt

    def _generate_ai_response(self, prompt: str) -> str:
        """
        Generate AI response from the prompt.

        Currently a placeholder. In production, integrate with:
        - OpenAI API
        - Local LLM models
        - Azure OpenAI

        Args:
            prompt: The constructed prompt.

        Returns:
            Generated response text.
        """
        # Placeholder response generation
        # TODO: Replace with actual LLM integration
        if "school" in prompt.lower():
            return "I remember my school days fondly. There was this time when..."
        elif "family" in prompt.lower():
            return "Family has always been important to me. Let me tell you about..."
        else:
            return "Based on my memories, I can share that..."

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