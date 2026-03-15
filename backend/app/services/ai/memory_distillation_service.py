from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from ..memory_capture_service import MemoryCaptureService, Memory
from ..timeline_engine import TimelineEngine
from ..memory.memory_embedding_service import MemoryEmbeddingService
from .personality_model_service import PersonalityModelService, PersonalityProfile
import re
from collections import Counter, defaultdict


@dataclass
class DistilledInsight:
    """
    Represents a distilled insight extracted from memories.

    Contains the insight text, source memories, category, and confidence score.
    """
    insight_text: str
    source_memory_ids: List[str] = field(default_factory=list)
    category: str = ""  # 'lesson', 'advice', 'regret', 'principle'
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary for serialization."""
        return {
            'insight_text': self.insight_text,
            'source_memory_ids': self.source_memory_ids,
            'category': self.category,
            'confidence_score': self.confidence_score
        }


class MemoryDistillationService:
    """
    Memory Distillation Engine for the Legacy AI platform.

    This service analyzes stored memories to extract higher-level wisdom and insights
    such as life lessons, advice, regrets, and guiding principles. It transforms raw
    memories into actionable knowledge that can guide conversations and decision-making.

    The service integrates with:
    - MemoryCaptureService: Access to stored memories
    - TimelineEngine: Chronological context and life stage analysis
    - MemoryEmbeddingService: Semantic analysis and similarity detection
    - PersonalityModelService: Personality-informed insight interpretation

    Future LLM Integration:
    - Use GPT-4 or similar models to interpret complex narratives and extract nuanced insights
    - Implement semantic clustering of insights using embedding similarity
    - Apply natural language understanding for causal relationship analysis
    - Use machine learning for insight validation, ranking, and cross-referencing

    Future Embedding Clustering:
    - Cluster similar insights using vector embeddings for consolidation
    - Identify thematic patterns across memory collections
    - Enable semantic search and retrieval of distilled wisdom
    - Support multi-dimensional insight analysis and visualization
    """

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        timeline_engine: TimelineEngine,
        embedding_service: MemoryEmbeddingService,
        personality_service: Optional[PersonalityModelService] = None
    ):
        """
        Initialize the Memory Distillation Service.

        Args:
            memory_service: Instance of MemoryCaptureService for accessing stored memories.
            timeline_engine: Instance of TimelineEngine for chronological and life-stage context.
            embedding_service: Instance of MemoryEmbeddingService for semantic analysis.
            personality_service: Optional PersonalityModelService for personality-informed analysis.
        """
        self.memory_service = memory_service
        self.timeline_engine = timeline_engine
        self.embedding_service = embedding_service
        self.personality_service = personality_service

        # Keywords and patterns for different insight categories
        self.lesson_patterns = [
            r'I (learned|realized|understood|discovered) that (.+)',
            r'The (lesson|teaching|key takeaway) (was|is) (.+)',
            r'(Learned|Realized) (.+) the hard way',
            r'Important to remember that (.+)',
            r'That taught me (.+)'
        ]

        self.advice_patterns = [
            r'(Should|Would) (recommend|suggest|advise) (.+)',
            r'(Don\'t|Never|Avoid) (.+) if you (.+)',
            r'Better to (.+) than (.+)',
            r'Make sure to (.+) when (.+)',
            r'Remember to (.+) before (.+)'
        ]

        self.regret_patterns = [
            r'I (regret|wish) I had (.+)',
            r'(Should have|Could have|Would have) (.+) but (.+)',
            r'If only I (.+)',
            r'Never got to (.+)',
            r'Missed (opportunity|chance) to (.+)'
        ]

        self.principle_patterns = [
            r'(Always|Never) (.+) because (.+)',
            r'My (principle|belief|philosophy) is (.+)',
            r'I stand for (.+)',
            r'(Value|Believe) that (.+) above all',
            r'Guiding principle (.+)'
        ]

        # Keywords for validation
        self.lesson_keywords = ['learned', 'lesson', 'realized', 'understood', 'taught', 'key', 'takeaway']
        self.advice_keywords = ['should', 'recommend', 'suggest', 'don\'t', 'avoid', 'better', 'remember']
        self.regret_keywords = ['regret', 'wish', 'should have', 'if only', 'missed', 'never got']
        self.principle_keywords = ['always', 'never', 'principle', 'belief', 'value', 'philosophy']

    def distill_life_lessons(self, memories: Optional[List[Memory]] = None) -> List[DistilledInsight]:
        """
        Extract life lessons from memories using pattern matching and semantic analysis.

        Analyzes memory content to identify teachings, realizations, and important learnings
        that represent accumulated wisdom from life experiences.

        Future LLM Enhancement:
        - Use language models to understand complex causal relationships
        - Extract nuanced lessons from implicit narratives
        - Validate lesson authenticity through cross-memory verification

        Args:
            memories: Optional list of memories to analyze. If None, uses all memories.

        Returns:
            List of DistilledInsight objects categorized as 'lesson'.
        """
        if memories is None:
            memories = self.memory_service.list_memories()

        insights = []

        for memory in memories:
            text_content = f"{memory.title} {memory.description}"

            # Extract lessons using regex patterns
            for pattern in self.lesson_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        lesson_text = match[1] if len(match) > 1 else match[0]
                    else:
                        lesson_text = match

                    # Clean and validate the lesson
                    lesson_text = self._clean_insight_text(lesson_text)
                    if lesson_text and len(lesson_text) > 10:
                        confidence = self._calculate_insight_confidence(
                            lesson_text, self.lesson_keywords, memory
                        )

                        insight = DistilledInsight(
                            insight_text=f"I learned that {lesson_text}",
                            source_memory_ids=[memory.id],
                            category='lesson',
                            confidence_score=confidence
                        )
                        insights.append(insight)

        return self._merge_and_rank_insights(insights)

    def extract_advice(self, memories: Optional[List[Memory]] = None) -> List[DistilledInsight]:
        """
        Extract advice and recommendations from memories.

        Identifies practical guidance, warnings, and suggestions based on personal experiences
        that can help others avoid mistakes or make better decisions.

        Future LLM Enhancement:
        - Use intent analysis to distinguish different types of advice
        - Generate contextual advice based on situation similarity
        - Validate advice applicability through outcome analysis

        Args:
            memories: Optional list of memories to analyze. If None, uses all memories.

        Returns:
            List of DistilledInsight objects categorized as 'advice'.
        """
        if memories is None:
            memories = self.memory_service.list_memories()

        insights = []

        for memory in memories:
            text_content = f"{memory.title} {memory.description}"

            # Extract advice using regex patterns
            for pattern in self.advice_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        advice_text = ' '.join(match)
                    else:
                        advice_text = match

                    # Clean and validate the advice
                    advice_text = self._clean_insight_text(advice_text)
                    if advice_text and len(advice_text) > 8:
                        confidence = self._calculate_insight_confidence(
                            advice_text, self.advice_keywords, memory
                        )

                        insight = DistilledInsight(
                            insight_text=advice_text,
                            source_memory_ids=[memory.id],
                            category='advice',
                            confidence_score=confidence
                        )
                        insights.append(insight)

        return self._merge_and_rank_insights(insights)

    def identify_recurring_patterns(self, memories: Optional[List[Memory]] = None) -> List[DistilledInsight]:
        """
        Identify recurring patterns and principles across memories.

        Finds themes, behaviors, and principles that appear consistently across different
        life experiences, representing core life patterns and philosophies.

        Future Embedding Clustering:
        - Use vector embeddings to cluster similar patterns
        - Identify thematic relationships across memory collections
        - Enable semantic pattern discovery and analysis

        Args:
            memories: Optional list of memories to analyze. If None, uses all memories.

        Returns:
            List of DistilledInsight objects categorized as 'principle'.
        """
        if memories is None:
            memories = self.memory_service.list_memories()

        insights = []

        # Analyze recurring themes across all memories
        all_text = " ".join([f"{mem.title} {mem.description}" for mem in memories]).lower()

        # Extract principles using patterns
        for pattern in self.principle_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    principle_text = ' '.join(match)
                else:
                    principle_text = match

                principle_text = self._clean_insight_text(principle_text)
                if principle_text and len(principle_text) > 15:
                    # Find all memories containing this principle
                    source_ids = [
                        mem.id for mem in memories
                        if principle_text.lower() in f"{mem.title} {mem.description}".lower()
                    ]

                    if len(source_ids) >= 2:  # Must appear in at least 2 memories
                        confidence = min(len(source_ids) / len(memories), 1.0)

                        insight = DistilledInsight(
                            insight_text=principle_text,
                            source_memory_ids=source_ids,
                            category='principle',
                            confidence_score=confidence
                        )
                        insights.append(insight)

        # Analyze emotional patterns
        emotional_patterns = self._analyze_emotional_patterns(memories)
        for pattern_text, confidence in emotional_patterns.items():
            insight = DistilledInsight(
                insight_text=pattern_text,
                source_memory_ids=[mem.id for mem in memories],
                category='principle',
                confidence_score=confidence
            )
            insights.append(insight)

        return self._merge_and_rank_insights(insights)

    def categorize_insights(self, insights: List[DistilledInsight]) -> Dict[str, List[DistilledInsight]]:
        """
        Categorize insights by type and return organized collections.

        Groups insights by their category for easier access and analysis.

        Args:
            insights: List of DistilledInsight objects to categorize.

        Returns:
            Dictionary mapping category names to lists of insights.
        """
        categorized = defaultdict(list)

        for insight in insights:
            categorized[insight.category].append(insight)

        # Sort each category by confidence score (highest first)
        for category in categorized:
            categorized[category].sort(key=lambda x: x.confidence_score, reverse=True)

        return dict(categorized)

    def get_wisdom_by_life_stage(self, memories: Optional[List[Memory]] = None) -> Dict[str, List[DistilledInsight]]:
        """
        Extract wisdom and insights organized by life stages.

        Uses TimelineEngine to group memories by life stages and extract
        stage-specific wisdom and lessons.

        Args:
            memories: Optional list of memories to analyze. If None, uses all memories.

        Returns:
            Dictionary mapping life stage names to lists of insights.
        """
        if memories is None:
            memories = self.memory_service.list_memories()

        life_stages = self.timeline_engine.group_by_life_stage(memories)
        stage_wisdom = {}

        for stage, stage_memories in life_stages.items():
            if stage_memories:  # Only analyze stages with memories
                # Extract all types of insights for this stage
                lessons = self.distill_life_lessons(stage_memories)
                advice = self.extract_advice(stage_memories)
                patterns = self.identify_recurring_patterns(stage_memories)

                stage_wisdom[stage] = lessons + advice + patterns

        return stage_wisdom

    def get_personality_aligned_insights(
        self,
        memories: Optional[List[Memory]] = None,
        personality_profile: Optional[PersonalityProfile] = None
    ) -> List[DistilledInsight]:
        """
        Extract insights that align with or are informed by personality traits.

        Uses personality information to prioritize and interpret insights in
        the context of the person's character and values.

        Args:
            memories: Optional list of memories to analyze.
            personality_profile: Optional personality profile for context.

        Returns:
            List of insights prioritized by personality alignment.
        """
        if memories is None:
            memories = self.memory_service.list_memories()

        all_insights = (
            self.distill_life_lessons(memories) +
            self.extract_advice(memories) +
            self.identify_recurring_patterns(memories)
        )

        if not personality_profile:
            return all_insights

        # Prioritize insights that align with personality traits
        prioritized_insights = []
        for insight in all_insights:
            alignment_score = self._calculate_personality_alignment(insight, personality_profile)
            # Boost confidence based on personality alignment
            insight.confidence_score = min(insight.confidence_score * (1 + alignment_score), 1.0)
            prioritized_insights.append(insight)

        # Sort by adjusted confidence
        prioritized_insights.sort(key=lambda x: x.confidence_score, reverse=True)

        return prioritized_insights

    def _clean_insight_text(self, text: str) -> str:
        """Clean and normalize insight text."""
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        # Remove trailing punctuation if it's not part of the sentence
        text = text.rstrip('.,!?;')
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        return text

    def _calculate_insight_confidence(self, text: str, keywords: List[str], memory: Memory) -> float:
        """Calculate confidence score for an insight based on various factors."""
        # Base confidence on keyword matches
        keyword_matches = sum(1 for keyword in keywords if keyword in text.lower())
        keyword_score = min(keyword_matches / len(keywords), 1.0)

        # Factor in memory emotional intensity
        emotion_score = len(memory.emotions) / 10.0  # Normalize to 0-1

        # Factor in memory recency (newer memories might be more relevant)
        # This is a simple approximation - in practice, you'd use actual timestamps
        recency_score = 0.5  # Default neutral score

        # Combine factors
        confidence = (keyword_score * 0.6) + (emotion_score * 0.3) + (recency_score * 0.1)
        return min(confidence, 1.0)

    def _merge_and_rank_insights(self, insights: List[DistilledInsight]) -> List[DistilledInsight]:
        """Merge similar insights and rank by confidence."""
        # Group similar insights
        merged = defaultdict(lambda: {
            'insights': [],
            'total_confidence': 0,
            'all_sources': set()
        })

        for insight in insights:
            # Create a key based on the first 8 words for similarity
            key = ' '.join(insight.insight_text.split()[:8]).lower()
            merged[key]['insights'].append(insight)
            merged[key]['total_confidence'] += insight.confidence_score
            merged[key]['all_sources'].update(insight.source_memory_ids)

        # Create final merged insights
        final_insights = []
        for data in merged.values():
            if data['insights']:
                primary_insight = data['insights'][0]
                avg_confidence = data['total_confidence'] / len(data['insights'])

                merged_insight = DistilledInsight(
                    insight_text=primary_insight.insight_text,
                    source_memory_ids=list(data['all_sources']),
                    category=primary_insight.category,
                    confidence_score=avg_confidence
                )
                final_insights.append(merged_insight)

        # Sort by confidence and return top insights
        final_insights.sort(key=lambda x: x.confidence_score, reverse=True)
        return final_insights[:10]  # Limit to top 10 per category

    def _analyze_emotional_patterns(self, memories: List[Memory]) -> Dict[str, float]:
        """Analyze recurring emotional patterns across memories."""
        patterns = {}

        # Count emotions across all memories
        all_emotions = []
        for memory in memories:
            all_emotions.extend(memory.emotions)

        emotion_counts = Counter(all_emotions)

        # Identify dominant emotional patterns
        total_emotions = sum(emotion_counts.values())
        if total_emotions > 0:
            for emotion, count in emotion_counts.items():
                frequency = count / total_emotions
                if frequency > 0.15:  # More than 15% of emotions
                    patterns[f"Shows a pattern of experiencing {emotion} in significant moments"] = frequency

        return patterns

    def _calculate_personality_alignment(self, insight: DistilledInsight, profile: PersonalityProfile) -> float:
        """Calculate how well an insight aligns with personality traits."""
        alignment_score = 0.0
        insight_text = insight.insight_text.lower()

        # Check alignment with personality traits
        for trait in profile.traits:
            if trait.lower() in insight_text:
                alignment_score += 0.3

        # Check alignment with values
        for value in profile.values:
            if value.lower() in insight_text:
                alignment_score += 0.4

        # Check alignment with communication style
        style = profile.communication_style
        if insight.category == 'advice' and style.get('directness') == 'direct':
            alignment_score += 0.2
        elif insight.category == 'lesson' and style.get('formality') == 'formal':
            alignment_score += 0.2

        return min(alignment_score, 1.0)