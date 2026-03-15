from typing import List, Dict, Any, Set
from collections import Counter, defaultdict
from ..memory_capture_service import Memory


class PersonalityProfile:
    """
    Structured representation of a person's personality derived from memories.

    Contains traits, beliefs, values, and patterns that define their character.
    Used by the Conversation Engine to generate authentic responses.
    """

    def __init__(self):
        self.traits: List[str] = []
        self.core_beliefs: List[str] = []
        self.communication_style: Dict[str, Any] = {}
        self.values: List[str] = []
        self.decision_heuristics: List[str] = []
        self.emotional_patterns: Dict[str, float] = {}
        self.relationship_patterns: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization."""
        return {
            'traits': self.traits,
            'core_beliefs': self.core_beliefs,
            'communication_style': self.communication_style,
            'values': self.values,
            'decision_heuristics': self.decision_heuristics,
            'emotional_patterns': self.emotional_patterns,
            'relationship_patterns': self.relationship_patterns
        }


class PersonalityModelService:
    """
    Personality Modeling Service for Legacy AI.

    Analyzes stored memories to extract and model personality traits, beliefs, values,
    and behavioral patterns. This creates a comprehensive personality profile that can
    be used by the Conversation Engine to generate responses that authentically reflect
    the person's character.

    Future enhancements:
    - Integrate LLM analysis (e.g., GPT-4) to interpret memory content and extract nuanced traits.
    - Use embeddings for semantic clustering of personality indicators.
    - Implement machine learning models for trait prediction and validation.
    - Add temporal analysis to track personality evolution over time.
    """

    # Common personality traits to look for
    COMMON_TRAITS = [
        'adventurous', 'analytical', 'artistic', 'compassionate', 'creative',
        'disciplined', 'empathetic', 'extroverted', 'generous', 'honest',
        'humble', 'independent', 'introspective', 'loyal', 'optimistic',
        'patient', 'practical', 'resilient', 'responsible', 'wise'
    ]

    # Common values
    COMMON_VALUES = [
        'family', 'friendship', 'honesty', 'integrity', 'justice',
        'kindness', 'learning', 'loyalty', 'perseverance', 'respect',
        'responsibility', 'wisdom', 'compassion', 'courage', 'empathy'
    ]

    def __init__(self):
        """Initialize the personality modeling service."""
        pass

    def build_personality_profile(self, memories: List[Memory]) -> PersonalityProfile:
        """
        Build a comprehensive personality profile from memories.

        Analyzes all aspects of the provided memories to extract personality characteristics.

        Args:
            memories: List of Memory objects to analyze.

        Returns:
            PersonalityProfile object containing extracted traits and patterns.
        """
        profile = PersonalityProfile()

        if not memories:
            return profile

        # Extract different aspects
        profile.traits = self._extract_traits(memories)
        profile.core_beliefs = self._extract_beliefs(memories)
        profile.communication_style = self._extract_communication_style(memories)
        profile.values = self.extract_values(memories)
        profile.decision_heuristics = self.extract_decision_patterns(memories)
        profile.emotional_patterns = self._extract_emotional_patterns(memories)
        profile.relationship_patterns = self._extract_relationship_patterns(memories)

        return profile

    def _extract_traits(self, memories: List[Memory]) -> List[str]:
        """
        Extract personality traits from memories.

        Currently uses keyword matching and pattern recognition.
        Future: Use LLM to analyze memory content for trait indicators.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of identified personality traits.
        """
        trait_indicators = defaultdict(int)

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()

            # Simple keyword matching for traits
            for trait in self.COMMON_TRAITS:
                if trait in text:
                    trait_indicators[trait] += 1

            # Pattern-based trait detection
            if any(word in text for word in ['helped', 'supported', 'cared for']):
                trait_indicators['compassionate'] += 1
            if any(word in text for word in ['learned', 'studied', 'explored']):
                trait_indicators['curious'] += 1
            if any(word in text for word in ['decided', 'chose', 'planned']):
                trait_indicators['decisive'] += 1

        # Return traits that appear in at least 10% of memories
        min_occurrences = max(1, len(memories) // 10)
        return [trait for trait, count in trait_indicators.items() if count >= min_occurrences]

    def _extract_beliefs(self, memories: List[Memory]) -> List[str]:
        """
        Extract core beliefs from memories.

        Looks for recurring statements about life, people, or principles.
        Future: Use NLP to identify belief statements and cluster similar beliefs.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of core beliefs.
        """
        beliefs = set()

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()

            # Look for belief indicators
            belief_phrases = []
            if 'believe' in text or 'always thought' in text or 'principle' in text:
                # Extract sentences containing belief words
                sentences = text.split('.')
                for sentence in sentences:
                    if any(word in sentence for word in ['believe', 'thought', 'principle', 'value']):
                        belief_phrases.append(sentence.strip())

            # Common belief patterns
            if 'family comes first' in text or 'family is important' in text:
                beliefs.add('Family is the most important thing')
            if 'honesty' in text and 'important' in text:
                beliefs.add('Honesty is crucial')
            if 'hard work' in text and 'pays off' in text:
                beliefs.add('Hard work leads to success')

        return list(beliefs)

    def _extract_communication_style(self, memories: List[Memory]) -> Dict[str, Any]:
        """
        Extract communication style patterns.

        Analyzes how the person expresses themselves in memories.
        Future: Use linguistic analysis to determine formality, directness, etc.

        Args:
            memories: List of memories to analyze.

        Returns:
            Dict describing communication style.
        """
        style = {
            'formality': 'neutral',
            'directness': 'moderate',
            'emotional_expression': 'balanced',
            'storytelling': False
        }

        total_memories = len(memories)
        formal_count = 0
        direct_count = 0
        emotional_count = 0
        storytelling_count = 0

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()

            # Check formality
            if any(word in text for word in ['please', 'thank you', 'excuse me']):
                formal_count += 1

            # Check directness
            if any(word in text for word in ['clearly', 'directly', 'straightforward']):
                direct_count += 1

            # Check emotional expression
            emotional_words = ['happy', 'sad', 'angry', 'excited', 'worried', 'proud']
            if any(word in text for word in emotional_words):
                emotional_count += 1

            # Check storytelling
            if any(word in text for word in ['remember when', 'there was this time', 'story']):
                storytelling_count += 1

        # Determine style based on counts
        if formal_count > total_memories * 0.6:
            style['formality'] = 'formal'
        elif formal_count < total_memories * 0.2:
            style['formality'] = 'casual'

        if direct_count > total_memories * 0.5:
            style['directness'] = 'direct'
        elif direct_count < total_memories * 0.2:
            style['directness'] = 'indirect'

        if emotional_count > total_memories * 0.7:
            style['emotional_expression'] = 'expressive'
        elif emotional_count < total_memories * 0.3:
            style['emotional_expression'] = 'reserved'

        style['storytelling'] = storytelling_count > total_memories * 0.4

        return style

    def extract_values(self, memories: List[Memory]) -> List[str]:
        """
        Extract core values from memories.

        Identifies what the person considers important in life.
        Future: Use semantic analysis to cluster and rank values.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of identified values.
        """
        value_counts = Counter()

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()
            tags = [tag.lower() for tag in memory.tags]

            # Count value mentions in text and tags
            for value in self.COMMON_VALUES:
                if value in text or value in tags:
                    value_counts[value] += 1

            # Additional value detection
            if any(word in text for word in ['helped others', 'volunteered', 'gave back']):
                value_counts['compassion'] += 1
            if any(word in text for word in ['learned new', 'education', 'studied']):
                value_counts['learning'] += 1

        # Return top values (appearing in at least 15% of memories)
        min_occurrences = max(1, len(memories) // 7)
        return [value for value, count in value_counts.most_common() if count >= min_occurrences]

    def extract_decision_patterns(self, memories: List[Memory]) -> List[str]:
        """
        Extract decision-making patterns and heuristics.

        Identifies how the person typically makes decisions.
        Future: Use pattern recognition and causal analysis.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of decision patterns.
        """
        patterns = set()

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()

            # Look for decision indicators
            if any(phrase in text for phrase in ['decided to', 'chose to', 'made the choice']):
                if 'carefully' in text or 'thought about' in text:
                    patterns.add('Makes decisions after careful consideration')
                elif 'quickly' in text or 'immediately' in text:
                    patterns.add('Makes quick decisions when needed')
                elif 'heart' in text or 'feeling' in text:
                    patterns.add('Follows heart/emotions in decisions')
                elif 'logic' in text or 'reason' in text:
                    patterns.add('Uses logical reasoning for decisions')

            # Risk patterns
            if 'risk' in text or 'gamble' in text:
                if 'took the risk' in text:
                    patterns.add('Willing to take calculated risks')
                elif 'avoided risk' in text:
                    patterns.add('Prefers to avoid risks')

            # Social decision patterns
            if 'friends' in text and 'advice' in text:
                patterns.add('Seeks advice from friends/family')
            if 'alone' in text and 'decided' in text:
                patterns.add('Makes independent decisions')

        return list(patterns)

    def _extract_emotional_patterns(self, memories: List[Memory]) -> Dict[str, float]:
        """
        Extract emotional response patterns.

        Analyzes emotional content across memories.
        Future: Use sentiment analysis and emotion detection models.

        Args:
            memories: List of memories to analyze.

        Returns:
            Dict mapping emotions to frequency percentages.
        """
        emotion_counts = Counter()

        for memory in memories:
            for emotion in memory.emotions:
                emotion_counts[emotion.lower()] += 1

        total_emotions = sum(emotion_counts.values())
        if total_emotions == 0:
            return {}

        return {emotion: count / total_emotions for emotion, count in emotion_counts.items()}

    def _extract_relationship_patterns(self, memories: List[Memory]) -> Dict[str, Any]:
        """
        Extract relationship and social interaction patterns.

        Analyzes how the person interacts with others.
        Future: Use social network analysis on people_involved data.

        Args:
            memories: List of memories to analyze.

        Returns:
            Dict describing relationship patterns.
        """
        patterns = {
            'social_orientation': 'neutral',
            'relationship_focus': [],
            'interaction_style': 'balanced'
        }

        total_people_mentions = 0
        family_mentions = 0
        friend_mentions = 0
        colleague_mentions = 0

        for memory in memories:
            people = memory.people_involved
            total_people_mentions += len(people)

            for person in people:
                person_lower = person.lower()
                if any(rel in person_lower for rel in ['mom', 'dad', 'brother', 'sister', 'family']):
                    family_mentions += 1
                elif any(rel in person_lower for rel in ['friend', 'buddy']):
                    friend_mentions += 1
                elif any(rel in person_lower for rel in ['colleague', 'coworker', 'boss']):
                    colleague_mentions += 1

        if total_people_mentions > 0:
            family_ratio = family_mentions / total_people_mentions
            friend_ratio = friend_mentions / total_people_mentions

            if family_ratio > 0.6:
                patterns['relationship_focus'].append('Family-oriented')
            if friend_ratio > 0.4:
                patterns['relationship_focus'].append('Friend-focused')

            if total_people_mentions / len(memories) > 2:
                patterns['social_orientation'] = 'social'
            elif total_people_mentions / len(memories) < 0.5:
                patterns['social_orientation'] = 'private'

        return patterns