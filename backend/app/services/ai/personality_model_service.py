from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from ..memory_capture_service import MemoryCaptureService, Memory
from ..timeline_engine import TimelineEngine
from ..memory.memory_embedding_service import MemoryEmbeddingService
import re
from collections import Counter


@dataclass
class PersonalityProfile:
    """
    Represents a personality profile extracted from life memories.

    This profile captures the core aspects of a person's character, values,
    and behavioral patterns as evidenced by their life experiences.
    """
    traits: List[str] = field(default_factory=list)
    core_beliefs: List[str] = field(default_factory=list)
    communication_style: Dict[str, Any] = field(default_factory=dict)
    values: List[str] = field(default_factory=list)
    decision_heuristics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the profile to a dictionary for serialization."""
        return {
            'traits': self.traits,
            'core_beliefs': self.core_beliefs,
            'communication_style': self.communication_style,
            'values': self.values,
            'decision_heuristics': self.decision_heuristics
        }


class PersonalityModelService:
    """
    Personality Modeling Engine for the Legacy AI platform.

    This service analyzes stored memories to build a comprehensive personality profile
    that captures the user's values, beliefs, communication style, and decision patterns.
    The profile can be used by the Conversation Engine to generate more authentic,
    personalized responses.

    The service integrates with:
    - MemoryCaptureService: Access to stored memories
    - TimelineEngine: Chronological context and life stage analysis
    - MemoryEmbeddingService: Semantic analysis of memory content
    """

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        timeline_engine: TimelineEngine,
        embedding_service: MemoryEmbeddingService
    ):
        """
        Initialize the Personality Modeling Service.

        Args:
            memory_service: Instance of MemoryCaptureService for accessing stored memories.
            timeline_engine: Instance of TimelineEngine for chronological and life-stage context.
            embedding_service: Instance of MemoryEmbeddingService for semantic analysis.
        """
        self.memory_service = memory_service
        self.timeline_engine = timeline_engine
        self.embedding_service = embedding_service

        # Predefined patterns for personality analysis
        self.trait_keywords = {
            'adventurous': ['adventure', 'explore', 'travel', 'risk', 'bold', 'daring'],
            'compassionate': ['care', 'help', 'support', 'empathy', 'kind', 'understanding'],
            'creative': ['create', 'art', 'music', 'write', 'design', 'innovative'],
            'disciplined': ['discipline', 'routine', 'consistent', 'focused', 'determined'],
            'optimistic': ['hope', 'positive', 'optimism', 'bright', 'future', 'possibility'],
            'practical': ['practical', 'realistic', 'logical', 'efficient', 'useful'],
            'social': ['friends', 'social', 'community', 'gather', 'together', 'relationships'],
            'independent': ['independent', 'self-reliant', 'alone', 'solo', 'autonomous']
        }

        self.value_keywords = {
            'family': ['family', 'children', 'parents', 'siblings', 'home', 'together'],
            'integrity': ['honest', 'truth', 'integrity', 'ethical', 'moral', 'right'],
            'achievement': ['success', 'accomplish', 'achieve', 'goal', 'excel', 'excellence'],
            'freedom': ['freedom', 'liberty', 'independent', 'choice', 'autonomy'],
            'justice': ['fair', 'justice', 'equality', 'right', 'wrong', 'balance'],
            'knowledge': ['learn', 'knowledge', 'education', 'wisdom', 'understand', 'grow'],
            'health': ['health', 'wellness', 'fitness', 'care', 'body', 'mind']
        }

        self.belief_patterns = [
            r'I (always|never|believe|think) that (.+)',
            r'My philosophy is (.+)',
            r'I stand for (.+)',
            r'I value (.+) above all',
            r'The most important thing is (.+)'
        ]

        self.decision_patterns = [
            r'I decided to (.+) because (.+)',
            r'I chose (.+) over (.+)',
            r'When faced with (.+), I (.+)',
            r'My approach to (.+) is (.+)'
        ]

    def build_personality_profile(self, memories: Optional[List[Memory]] = None) -> PersonalityProfile:
        """
        Build a comprehensive personality profile from memories.

        If no memories are provided, analyzes all available memories.

        Args:
            memories: Optional list of memories to analyze. If None, uses all memories.

        Returns:
            PersonalityProfile containing traits, beliefs, communication style, values, and decision patterns.
        """
        if memories is None:
            memories = self.memory_service.retrieve_all_memories()

        profile = PersonalityProfile()

        # Extract personality components
        profile.traits = self.extract_traits(memories)
        profile.values = self.extract_values(memories)
        profile.core_beliefs = self.extract_core_beliefs(memories)
        profile.communication_style = self.extract_communication_style(memories)
        profile.decision_heuristics = self.extract_decision_patterns(memories)

        return profile

    def extract_traits(self, memories: List[Memory]) -> List[str]:
        """
        Extract personality traits from memories using keyword analysis.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of identified personality traits, sorted by frequency.
        """
        trait_scores = Counter()

        for memory in memories:
            text_content = f"{memory.title} {memory.description}".lower()

            for trait, keywords in self.trait_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in text_content)
                if matches > 0:
                    trait_scores[trait] += matches

        # Return traits that appear at least once, sorted by frequency
        significant_traits = [trait for trait, score in trait_scores.most_common() if score > 0]
        return significant_traits[:8]  # Limit to top 8 traits

    def extract_values(self, memories: List[Memory]) -> List[str]:
        """
        Extract core values from memories.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of identified core values, sorted by relevance.
        """
        value_scores = Counter()

        for memory in memories:
            text_content = f"{memory.title} {memory.description}".lower()

            for value, keywords in self.value_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in text_content)
                if matches > 0:
                    value_scores[value] += matches

        # Return values that appear at least once, sorted by frequency
        significant_values = [value for value, score in value_scores.most_common() if score > 0]
        return significant_values[:6]  # Limit to top 6 values

    def extract_core_beliefs(self, memories: List[Memory]) -> List[str]:
        """
        Extract core beliefs and philosophies from memories using pattern matching.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of identified core beliefs.
        """
        beliefs = set()

        for memory in memories:
            text_content = f"{memory.title} {memory.description}"

            for pattern in self.belief_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        belief = match[1] if len(match) > 1 else match[0]
                    else:
                        belief = match

                    # Clean up the belief statement
                    belief = belief.strip()
                    if belief and len(belief) > 10:  # Only meaningful beliefs
                        beliefs.add(belief.lower())

        return list(beliefs)[:5]  # Limit to top 5 beliefs

    def extract_communication_style(self, memories: List[Memory]) -> Dict[str, Any]:
        """
        Analyze communication style from memory content and metadata.

        Args:
            memories: List of memories to analyze.

        Returns:
            Dictionary describing communication style characteristics.
        """
        style_analysis = {
            'formality': 'neutral',
            'emotional_expression': 'balanced',
            'directness': 'moderate',
            'verbosity': 'moderate',
            'humor_usage': 'occasional'
        }

        # Analyze formality based on language patterns
        formal_indicators = ['therefore', 'consequently', 'accordingly', 'moreover', 'furthermore']
        casual_indicators = ['kinda', 'sorta', 'yeah', 'like', 'totally', 'awesome']

        formal_count = 0
        casual_count = 0

        for memory in memories:
            text = f"{memory.title} {memory.description}".lower()
            formal_count += sum(1 for word in formal_indicators if word in text)
            casual_count += sum(1 for word in casual_indicators if word in text)

        if formal_count > casual_count * 2:
            style_analysis['formality'] = 'formal'
        elif casual_count > formal_count * 2:
            style_analysis['formality'] = 'casual'

        # Analyze emotional expression based on emotion tags
        emotion_frequency = Counter()
        for memory in memories:
            emotion_frequency.update(memory.emotions)

        high_emotion = emotion_frequency.most_common(1)
        if high_emotion and high_emotion[0][1] > len(memories) * 0.3:
            style_analysis['emotional_expression'] = 'expressive'
        elif len([e for e, c in emotion_frequency.items() if c > 0]) < 3:
            style_analysis['emotional_expression'] = 'reserved'

        return style_analysis

    def extract_decision_patterns(self, memories: List[Memory]) -> List[str]:
        """
        Extract decision-making patterns and heuristics from memories.

        Args:
            memories: List of memories to analyze.

        Returns:
            List of identified decision patterns.
        """
        patterns = set()

        for memory in memories:
            text_content = f"{memory.title} {memory.description}"

            for pattern in self.decision_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        decision = f"When {match[0]}, I {match[1]}"
                    else:
                        decision = match

                    # Clean up and store meaningful patterns
                    decision = decision.strip()
                    if decision and len(decision) > 15:  # Only substantial patterns
                        patterns.add(decision.lower())

        return list(patterns)[:4]  # Limit to top 4 patterns

    def analyze_personality_evolution(self, memories: List[Memory]) -> Dict[str, Any]:
        """
        Analyze how personality traits evolved over time using TimelineEngine.

        Args:
            memories: List of memories to analyze.

        Returns:
            Dictionary showing personality evolution across life stages.
        """
        # Group memories by life stage
        life_stages = self.timeline_engine.group_by_life_stage(memories)

        evolution = {}
        for stage, stage_memories in life_stages.items():
            if stage_memories:  # Only analyze stages with memories
                profile = self.build_personality_profile(stage_memories)
                evolution[stage] = {
                    'traits': profile.traits,
                    'values': profile.values,
                    'beliefs': profile.core_beliefs
                }

        return evolution

    def get_personality_insights(self, profile: PersonalityProfile) -> Dict[str, Any]:
        """
        Generate insights about the personality profile.

        Args:
            profile: PersonalityProfile to analyze.

        Returns:
            Dictionary with personality insights and recommendations.
        """
        insights = {
            'dominant_traits': profile.traits[:3] if profile.traits else [],
            'core_values': profile.values[:3] if profile.values else [],
            'communication_tips': [],
            'decision_style': 'balanced'
        }

        # Generate communication tips based on style
        style = profile.communication_style
        if style.get('formality') == 'formal':
            insights['communication_tips'].append('Uses formal, structured language')
        elif style.get('formality') == 'casual':
            insights['communication_tips'].append('Prefers casual, conversational tone')

        if style.get('emotional_expression') == 'expressive':
            insights['communication_tips'].append('Expresses emotions openly')
        elif style.get('emotional_expression') == 'reserved':
            insights['communication_tips'].append('Tends to be emotionally reserved')

        # Determine decision style
        if any('practical' in trait for trait in profile.traits):
            insights['decision_style'] = 'practical'
        elif any('creative' in trait for trait in profile.traits):
            insights['decision_style'] = 'creative'
        elif any('compassionate' in trait for trait in profile.traits):
            insights['decision_style'] = 'compassionate'

        return insights