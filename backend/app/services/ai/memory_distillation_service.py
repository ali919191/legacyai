from typing import List, Dict, Any, Set
from collections import Counter, defaultdict
from ..memory_capture_service import Memory


class DistilledInsight:
    """
    Represents a distilled insight extracted from memories.

    Contains the insight text, source memories, category, and confidence score.
    """

    def __init__(
        self,
        insight_text: str,
        source_memory_ids: List[str],
        category: str,
        confidence_score: float
    ):
        self.insight_text = insight_text
        self.source_memory_ids = source_memory_ids
        self.category = category  # 'lesson', 'advice', 'regret', 'principle'
        self.confidence_score = confidence_score

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
    Memory Distillation Service for Legacy AI.

    Analyzes stored memories to extract higher-level wisdom and insights such as
    life lessons, advice, regrets, and guiding principles. These distilled insights
    provide a deeper understanding of the person's accumulated wisdom.

    The service identifies patterns, recurring themes, and implicit knowledge from
    memory content to create actionable, insightful summaries that can guide
    conversations and decision-making.

    Future enhancements:
    - Integrate LLM analysis (e.g., GPT-4) to interpret complex memory narratives.
    - Use embeddings for semantic clustering of insights.
    - Implement machine learning for insight validation and ranking.
    - Add temporal analysis to track wisdom evolution over time.
    """

    # Keywords and patterns for different insight categories
    LESSON_KEYWORDS = [
        'learned', 'realized', 'understood', 'lesson', 'taught me',
        'important to remember', 'key takeaway', 'valuable lesson'
    ]

    ADVICE_KEYWORDS = [
        'should', 'would recommend', 'advice', 'suggest', 'better to',
        'don\'t', 'avoid', 'try to', 'make sure', 'remember to'
    ]

    REGRET_KEYWORDS = [
        'regret', 'wish i had', 'should have', 'if only', 'missed opportunity',
        'too late', 'never got to', 'wish i could go back'
    ]

    PRINCIPLE_KEYWORDS = [
        'always', 'never', 'principle', 'belief', 'value', 'important',
        'matters most', 'guiding', 'philosophy', 'way of life'
    ]

    def __init__(self):
        """Initialize the memory distillation service."""
        pass

    def distill_life_lessons(self, memories: List[Memory]) -> List[DistilledInsight]:
        """
        Extract life lessons from memories.

        Identifies teachings, realizations, and important learnings.
        Future: Use NLP to understand causal relationships and extract nuanced lessons.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of DistilledInsight objects categorized as 'lesson'.
        """
        insights = []

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()

            # Look for lesson indicators
            if any(keyword in text for keyword in self.LESSON_KEYWORDS):
                # Extract sentences containing lesson keywords
                sentences = self._extract_sentences_with_keywords(text, self.LESSON_KEYWORDS)
                for sentence in sentences:
                    insight = DistilledInsight(
                        insight_text=sentence.strip().capitalize(),
                        source_memory_ids=[memory.id],
                        category='lesson',
                        confidence_score=self._calculate_confidence(text, self.LESSON_KEYWORDS)
                    )
                    insights.append(insight)

        # Merge similar insights
        return self._merge_similar_insights(insights)

    def extract_advice(self, memories: List[Memory]) -> List[DistilledInsight]:
        """
        Extract advice and recommendations from memories.

        Identifies suggestions, warnings, and guidance based on experiences.
        Future: Use intent analysis to distinguish different types of advice.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of DistilledInsight objects categorized as 'advice'.
        """
        insights = []

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()

            if any(keyword in text for keyword in self.ADVICE_KEYWORDS):
                sentences = self._extract_sentences_with_keywords(text, self.ADVICE_KEYWORDS)
                for sentence in sentences:
                    insight = DistilledInsight(
                        insight_text=sentence.strip().capitalize(),
                        source_memory_ids=[memory.id],
                        category='advice',
                        confidence_score=self._calculate_confidence(text, self.ADVICE_KEYWORDS)
                    )
                    insights.append(insight)

        return self._merge_similar_insights(insights)

    def extract_regrets(self, memories: List[Memory]) -> List[DistilledInsight]:
        """
        Extract regrets and missed opportunities from memories.

        Identifies expressions of regret, hindsight, and things left undone.
        Future: Use sentiment analysis combined with temporal expressions.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of DistilledInsight objects categorized as 'regret'.
        """
        insights = []

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()

            if any(keyword in text for keyword in self.REGRET_KEYWORDS):
                sentences = self._extract_sentences_with_keywords(text, self.REGRET_KEYWORDS)
                for sentence in sentences:
                    insight = DistilledInsight(
                        insight_text=sentence.strip().capitalize(),
                        source_memory_ids=[memory.id],
                        category='regret',
                        confidence_score=self._calculate_confidence(text, self.REGRET_KEYWORDS)
                    )
                    insights.append(insight)

        return self._merge_similar_insights(insights)

    def identify_recurring_patterns(self, memories: List[Memory]) -> List[DistilledInsight]:
        """
        Identify recurring patterns and principles across memories.

        Finds themes that appear consistently across different memories.
        Future: Use topic modeling and pattern mining algorithms.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of DistilledInsight objects categorized as 'principle'.
        """
        insights = []

        # Analyze recurring themes
        all_text = " ".join([f"{mem.title} {mem.description}" for mem in memories]).lower()

        # Count principle keywords
        principle_counts = Counter()
        for keyword in self.PRINCIPLE_KEYWORDS:
            count = all_text.count(keyword)
            if count > 0:
                principle_counts[keyword] = count

        # Extract patterns from frequent principles
        for principle, count in principle_counts.most_common(5):
            if count >= len(memories) * 0.3:  # Appears in at least 30% of memories
                # Find memories containing this principle
                source_ids = [
                    mem.id for mem in memories
                    if principle in f"{mem.title} {mem.description}".lower()
                ]

                insight_text = f"Consistently values {principle} in life decisions and experiences."
                insight = DistilledInsight(
                    insight_text=insight_text,
                    source_memory_ids=source_ids,
                    category='principle',
                    confidence_score=min(count / len(memories), 1.0)
                )
                insights.append(insight)

        # Look for recurring emotional patterns
        emotion_patterns = self._analyze_emotional_patterns(memories)
        for pattern, confidence in emotion_patterns.items():
            insight = DistilledInsight(
                insight_text=f"Shows a pattern of {pattern} in emotional responses.",
                source_memory_ids=[mem.id for mem in memories],
                category='principle',
                confidence_score=confidence
            )
            insights.append(insight)

        return insights

    def _extract_sentences_with_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Extract sentences containing any of the given keywords."""
        sentences = text.split('.')
        relevant_sentences = []

        for sentence in sentences:
            if any(keyword in sentence for keyword in keywords):
                relevant_sentences.append(sentence)

        return relevant_sentences

    def _calculate_confidence(self, text: str, keywords: List[str]) -> float:
        """Calculate confidence score based on keyword frequency and context."""
        keyword_count = sum(text.count(keyword) for keyword in keywords)
        text_length = len(text.split())

        # Base confidence on keyword density
        density = keyword_count / max(text_length, 1)

        # Normalize to 0-1 scale
        confidence = min(density * 10, 1.0)  # Assuming 0.1 density = high confidence

        return confidence

    def _merge_similar_insights(self, insights: List[DistilledInsight]) -> List[DistilledInsight]:
        """
        Merge similar insights to avoid duplicates.

        Groups insights with similar text and combines their sources.
        """
        merged = defaultdict(lambda: {'sources': [], 'total_confidence': 0, 'count': 0})

        for insight in insights:
            # Simple similarity check based on first 10 words
            key = ' '.join(insight.insight_text.split()[:10]).lower()
            merged[key]['sources'].extend(insight.source_memory_ids)
            merged[key]['total_confidence'] += insight.confidence_score
            merged[key]['count'] += 1
            merged[key]['category'] = insight.category
            merged[key]['text'] = insight.insight_text

        # Create final insights
        final_insights = []
        for data in merged.values():
            avg_confidence = data['total_confidence'] / data['count']
            unique_sources = list(set(data['sources']))

            final_insight = DistilledInsight(
                insight_text=data['text'],
                source_memory_ids=unique_sources,
                category=data['category'],
                confidence_score=avg_confidence
            )
            final_insights.append(final_insight)

        return final_insights

    def _analyze_emotional_patterns(self, memories: List[Memory]) -> Dict[str, float]:
        """Analyze recurring emotional patterns across memories."""
        patterns = {}

        # Count emotions across all memories
        all_emotions = []
        for memory in memories:
            all_emotions.extend(memory.emotions)

        emotion_counts = Counter(all_emotions)

        # Identify dominant emotions
        total_emotions = sum(emotion_counts.values())
        if total_emotions > 0:
            for emotion, count in emotion_counts.items():
                frequency = count / total_emotions
                if frequency > 0.2:  # More than 20% of emotions
                    patterns[f"being {emotion}"] = frequency

        return patterns