from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from ..memory_capture_service import MemoryCaptureService, Memory
from ..timeline_engine import TimelineEngine
from .personality_model_service import PersonalityModelService, PersonalityProfile
from .memory_distillation_service import MemoryDistillationService, DistilledInsight


@dataclass
class LifeStory:
    """
    Represents a complete life story narrative.

    Contains the chronological narrative, key life stage summaries, personality insights,
    and lessons learned, compiled into a coherent biography.
    """
    user_id: str
    full_narrative: str
    life_stages: Dict[str, str] = field(default_factory=dict)
    key_events: List[Dict[str, Any]] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    personality_insights: Dict[str, Any] = field(default_factory=dict)
    memories_used: List[str] = field(default_factory=list)
    generation_timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the life story to a dictionary for serialization."""
        return {
            'user_id': self.user_id,
            'full_narrative': self.full_narrative,
            'life_stages': self.life_stages,
            'key_events': self.key_events,
            'lessons_learned': self.lessons_learned,
            'personality_insights': self.personality_insights,
            'memories_used': self.memories_used,
            'generation_timestamp': self.generation_timestamp.isoformat() if self.generation_timestamp else None
        }


@dataclass
class LifeStageSummary:
    """
    Represents a summary of a specific life stage.

    Contains key events, themes, personality development, and wisdom from that stage.
    """
    stage_name: str
    age_range: tuple
    key_events: List[Dict[str, Any]] = field(default_factory=list)
    dominant_themes: List[str] = field(default_factory=list)
    personality_development: str = ""
    lessons_from_stage: List[str] = field(default_factory=list)
    memory_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the life stage summary to a dictionary."""
        return {
            'stage_name': self.stage_name,
            'age_range': self.age_range,
            'key_events': self.key_events,
            'dominant_themes': self.dominant_themes,
            'personality_development': self.personality_development,
            'lessons_from_stage': self.lessons_from_stage,
            'memory_count': self.memory_count
        }


class LifeStoryGenerator:
    """
    Life Story Generator for the Legacy AI platform.

    This service generates chronological narratives of a person's life using stored memories,
    timeline data, personality insights, and distilled wisdom. It transforms raw memories
    into cohesive life stories that capture key events, life lessons, and personality evolution.

    The service integrates with:
    - MemoryCaptureService: Access to stored memories
    - TimelineEngine: Chronological organization and life stage grouping
    - PersonalityModelService: Personality profile and character insights
    - MemoryDistillationService: Wisdom extraction and lesson learning

    Future LLM Integration:
    - Use GPT-4 or similar models for narrative summarization and story enhancement
    - Implement sophisticated prose generation for richer, more readable narratives
    - Apply dialogue synthesis to include direct quotes from memories
    - Use semantic analysis for thematic pattern detection and narrative threading
    """

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        timeline_engine: TimelineEngine,
        personality_service: Optional[PersonalityModelService] = None,
        distillation_service: Optional[MemoryDistillationService] = None
    ):
        """
        Initialize the Life Story Generator.

        Args:
            memory_service: Instance of MemoryCaptureService for accessing stored memories.
            timeline_engine: Instance of TimelineEngine for chronological context and life stage grouping.
            personality_service: Optional PersonalityModelService for personality-informed narratives.
            distillation_service: Optional MemoryDistillationService for wisdom and lesson extraction.
        """
        self.memory_service = memory_service
        self.timeline_engine = timeline_engine
        self.personality_service = personality_service
        self.distillation_service = distillation_service

    def generate_life_story(self, user_id: str) -> LifeStory:
        """
        Generate a complete life story narrative for a user.

        This method orchestrates the full life story generation process:
        1. Retrieve all memories for the user
        2. Organize memories chronologically and by life stage
        3. Generate summaries for each life stage
        4. Extract personality insights and lessons learned
        5. Compile a coherent full narrative
        6. Assemble all components into a LifeStory object

        Args:
            user_id: The user ID for whom to generate the life story.

        Returns:
            A LifeStory object containing the complete narrative, life stage summaries,
            key events, lessons learned, and personality insights.

        Future Enhancements:
            - Accept LLM configuration for enhanced narrative generation
            - Implement narrative themes and thematic threading
            - Add dialogue synthesis for direct quotes from memories
            - Support contextual story enhancement and emotional resonance tuning
        """
        # Retrieve and organize all memories
        all_memories = self.memory_service.retrieve_all_memories()
        
        if not all_memories:
            # Return empty life story if no memories exist
            return LifeStory(
                user_id=user_id,
                full_narrative="No memories found for this user. The life story will be written as memories are added.",
                generation_timestamp=datetime.now()
            )

        # Get chronological timeline
        chronological_memories = self.timeline_engine.get_chronological_timeline()
        
        # Get life stage groupings
        memories_by_stage = self.timeline_engine.group_by_life_stage()
        
        # Generate life stage summaries
        life_stage_summaries = {}
        for stage, memories in memories_by_stage.items():
            if memories:
                summary = self.generate_life_stage_summary(stage)
                if summary:
                    life_stage_summaries[stage] = summary.to_dict()

        # Compile the full chronological narrative
        full_narrative = self.compile_chronological_narrative(chronological_memories)
        
        # Extract lessons learned
        lessons_learned = self._extract_lessons_learned()
        
        # Get personality insights
        personality_insights = self._get_personality_insights()
        
        # Extract key events
        key_events = self._extract_key_events(chronological_memories)
        
        # Create and return the LifeStory object
        life_story = LifeStory(
            user_id=user_id,
            full_narrative=full_narrative,
            life_stages=life_stage_summaries,
            key_events=key_events,
            lessons_learned=lessons_learned,
            personality_insights=personality_insights,
            memories_used=[m.id for m in all_memories],
            generation_timestamp=datetime.now()
        )
        
        return life_story

    def generate_life_stage_summary(self, stage: str) -> Optional[LifeStageSummary]:
        """
        Generate a summary for a specific life stage.

        This method creates a focused narrative summary for one life stage:
        1. Retrieve all memories for that life stage
        2. Identify key events and dominant themes
        3. Trace personality development during that stage
        4. Extract lessons and wisdom from that period
        5. Assemble into a LifeStageSummary

        Args:
            stage: The life stage to summarize (e.g., 'childhood', 'education', 'career', 'retirement').

        Returns:
            A LifeStageSummary object with stage-specific narrative, events, and insights,
            or None if the stage has no memories.

        Supported Stages:
            - 'childhood': Ages 0-12
            - 'education': Ages 13-22
            - 'career': Ages 23-64
            - 'retirement': Ages 65+
        """
        # Get memories for the specific life stage
        memories_by_stage = self.timeline_engine.group_by_life_stage()
        stage_memories = memories_by_stage.get(stage, [])
        
        if not stage_memories:
            return None
        
        # Get age range for the stage
        age_range = self.timeline_engine.LIFE_STAGES.get(stage, (0, 0))
        
        # Extract key events for this stage
        key_events = self._extract_key_events(stage_memories)
        
        # Identify dominant themes from emotions and tags
        dominant_themes = self._identify_dominant_themes(stage_memories)
        
        # Trace personality development
        personality_dev = self._trace_personality_development(stage_memories, stage)
        
        # Extract lessons from this stage
        stage_lessons = self._extract_stage_lessons(stage_memories)
        
        # Create and return the LifeStageSummary
        summary = LifeStageSummary(
            stage_name=stage,
            age_range=age_range,
            key_events=key_events,
            dominant_themes=dominant_themes,
            personality_development=personality_dev,
            lessons_from_stage=stage_lessons,
            memory_count=len(stage_memories)
        )
        
        return summary

    def compile_chronological_narrative(self, memories: List[Memory]) -> str:
        """
        Compile a chronological narrative from a list of memories.

        This method transforms a collection of memories into a coherent narrative:
        1. Sort memories chronologically
        2. Group related memories into thematic blocks
        3. Create transitions between blocks for narrative flow
        4. Add contextual information and connections
        5. Generate readable prose (currently templated, future LLM enhancement)

        Args:
            memories: A list of Memory objects to compile into narrative form.

        Returns:
            A string containing the compiled chronological narrative.

        Future Enhancements:
            - Integrate with LLM for natural language prose generation
            - Implement semantic clustering for thematic grouping
            - Add transitional phrases and narrative flow optimization
            - Support multiple narrative styles and tones
            - Include dialogue synthesis from memory descriptions
        """
        if not memories:
            return "No memories to compile into a narrative."
        
        # Sort memories chronologically
        sorted_memories = sorted(memories, key=lambda m: m.timestamp)
        
        # Build narrative sections
        narrative_sections = []
        
        # Opening statement
        if sorted_memories:
            start_date = sorted_memories[0].timestamp.year
            end_date = sorted_memories[-1].timestamp.year if sorted_memories[-1] else start_date
            temporal_summary = self._summarize_temporal_patterns(sorted_memories)
            narrative_sections.append(
                f"# Life Narrative ({start_date} - {end_date})\n"
                f"{temporal_summary}"
            )
        
        # Compile memories into narrative sections
        for i, memory in enumerate(sorted_memories):
            section = self._memory_to_narrative_section(memory, i + 1)
            narrative_sections.append(section)
        
        # Add concluding reflection
        narrative_sections.append(self._generate_concluding_reflection(sorted_memories))
        
        # Join all sections into a cohesive narrative
        full_narrative = "\n\n".join(narrative_sections)
        
        return full_narrative

    def _memory_to_narrative_section(self, memory: Memory, sequence: int) -> str:
        """
        Convert a single memory into a narrative section.

        Args:
            memory: The Memory object to convert.
            sequence: The sequence number of this memory in the narrative.

        Returns:
            A formatted narrative section as a string.
        """
        timestamp_str = memory.timestamp.strftime("%B %d, %Y")
        temporal_context = self.timeline_engine.format_temporal_context(memory)
        
        section = f"""## {sequence}. {memory.title}
**Date:** {timestamp_str}
**Temporal Context:** {temporal_context if temporal_context else "Not specified"}
**Location:** {memory.location if memory.location else "Not specified"}
**People Involved:** {', '.join(memory.people_involved) if memory.people_involved else "Not specified"}

**Story:**
{memory.description}

**Emotions:** {', '.join(memory.emotions) if memory.emotions else "Not documented"}
**Tags:** {', '.join(memory.tags) if memory.tags else "Not tagged"}"""
        
        return section

    def _extract_key_events(self, memories: List[Memory]) -> List[Dict[str, Any]]:
        """
        Extract key events from a list of memories.

        Key events are identified by:
        - Presence of strong emotions (joy, sadness, surprise, fear)
        - Multiple people involved
        - Major life milestone tags
        - Significant location changes

        Args:
            memories: List of Memory objects to analyze.

        Returns:
            List of key event dictionaries with title, date, significance, and participants.
        """
        key_events = []
        
        for memory in memories:
            # Calculate significance score
            significance = 0
            
            # Strong emotions indicate significance
            strong_emotions = {'joy', 'sadness', 'pride', 'fear', 'triumph', 'regret', 'gratitude'}
            if any(emotion.lower() in strong_emotions for emotion in memory.emotions):
                significance += 2
            
            # Multiple participants indicate significance
            if len(memory.people_involved) > 2:
                significance += 1
            
            # Specific tags indicate life milestones
            milestone_tags = {
                'graduation', 'wedding', 'birth', 'death', 'accident', 'injury',
                'achievement', 'promotion', 'job', 'meeting', 'travel', 'milestone'
            }
            if any(tag.lower() in milestone_tags for tag in memory.tags):
                significance += 2
            
            # Include events with significance score > 2
            if significance > 2:
                key_events.append({
                    'title': memory.title,
                    'date': memory.timestamp.isoformat(),
                    'time_of_day': memory.time_of_day,
                    'day_of_week': memory.day_of_week,
                    'start_time': memory.start_time,
                    'end_time': memory.end_time,
                    'significance': significance,
                    'primary_emotions': memory.emotions,
                    'location': memory.location,
                    'participants': memory.people_involved
                })
        
        # Sort by date
        key_events.sort(key=lambda e: e['date'])
        
        return key_events

    def _identify_dominant_themes(self, memories: List[Memory]) -> List[str]:
        """
        Identify dominant themes from a list of memories.

        Themes are extracted from:
        - Tags (most frequent tags)
        - Emotions (most common emotional patterns)
        - Locations (frequently appearing locations)
        - People (recurring relationships)

        Args:
            memories: List of Memory objects to analyze.

        Returns:
            List of identified dominant themes as strings.
        """
        themes = set()
        
        # Collect all tags
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.tags)
        
        # Get most common tags (top 5)
        if all_tags:
            from collections import Counter
            tag_counts = Counter(all_tags)
            top_tags = [tag for tag, count in tag_counts.most_common(5)]
            themes.update(top_tags)
        
        # Identify emotional themes
        all_emotions = []
        for memory in memories:
            all_emotions.extend(memory.emotions)
        
        if all_emotions:
            emotion_counts = Counter(all_emotions)
            top_emotions = [f"Theme of {emotion.lower()}" for emotion, count in emotion_counts.most_common(3)]
            themes.update(top_emotions)
        
        # Identify location themes
        all_locations = [m.location for m in memories if m.location]
        if all_locations:
            location_counts = Counter(all_locations)
            top_locations = [f"Connection to {location}" for location, count in location_counts.most_common(2)]
            themes.update(top_locations)
        
        return list(themes)

    def _trace_personality_development(self, memories: List[Memory], stage: str) -> str:
        """
        Trace how personality developed during a specific life stage.

        Analyzes memories to identify growth patterns, value development, and
        personality evolution during the stage.

        Args:
            memories: List of Memory objects from the life stage.
            stage: The name of the life stage being analyzed.

        Returns:
            A narrative description of personality development during that stage.
        """
        if not memories:
            return f"No memories recorded for the {stage} stage."
        
        # Basic narrative template (can be enhanced with LLM)
        early_memories = sorted(memories, key=lambda m: m.timestamp)[:3]
        late_memories = sorted(memories, key=lambda m: m.timestamp)[-3:]
        
        early_themes = self._identify_dominant_themes(early_memories)
        late_themes = self._identify_dominant_themes(late_memories)
        
        development = f"""During the {stage} stage, significant personal development occurred. 
Early in this period, dominant themes included {', '.join(early_themes[:2]) if early_themes else 'personal growth'}.
As the stage progressed, the focus shifted toward {', '.join(late_themes[:2]) if late_themes else 'new challenges'}.
This progression reflects growth, learning, and evolving priorities throughout this important life chapter."""
        
        return development

    def _extract_stage_lessons(self, memories: List[Memory]) -> List[str]:
        """
        Extract lessons learned during a specific life stage.

        Derives wisdom from:
        - Challenges overcome (indicated by difficulty-related tags)
        - Emotional growth (emotional journey patterns)
        - Relationship insights (from interaction descriptions)
        - Achievement experiences

        Args:
            memories: List of Memory objects from the life stage.

        Returns:
            List of lesson strings extracted from the stage.
        """
        lessons = []
        
        # Extract explicit lessons from memory descriptions
        lesson_keywords = ['learned', 'taught', 'lesson', 'discovered', 'realized', 'understood']
        
        for memory in memories:
            description_lower = memory.description.lower()
            if any(keyword in description_lower for keyword in lesson_keywords):
                # Extract the lesson (simplified - would benefit from LLM)
                lessons.append(f"From {memory.title.lower()}: valuable insights about life and relationships")
        
        # Generate implicit lessons based on emotions and outcomes
        if memories:
            if any('joy' in m.emotions for m in memories):
                lessons.append("The importance of celebrating and cherishing joyful moments")
            if any('sadness' in m.emotions for m in memories):
                lessons.append("Resilience and growth through life's difficult periods")
            if any('gratitude' in m.emotions for m in memories):
                lessons.append("Appreciating the people and experiences that shaped my journey")
        
        return list(set(lessons))  # Remove duplicates

    def _extract_lessons_learned(self) -> List[str]:
        """
        Extract all lessons learned across the entire life story.

        Combines insights from the distillation service and memory analysis
        to create a comprehensive list of life lessons.

        Returns:
            List of lesson strings extracted from the entire life history.
        """
        lessons = []
        
        # Get lessons from distillation service if available
        if self.distillation_service:
            insights = self.distillation_service.extract_life_lessons()
            lessons.extend([insight.insight_text for insight in insights if insight.category == 'lesson'])
        
        # Get all memories and extract lessons from each stage
        memories_by_stage = self.timeline_engine.group_by_life_stage()
        for stage, stage_memories in memories_by_stage.items():
            stage_lessons = self._extract_stage_lessons(stage_memories)
            lessons.extend(stage_lessons)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_lessons = []
        for lesson in lessons:
            if lesson not in seen:
                seen.add(lesson)
                unique_lessons.append(lesson)
        
        return unique_lessons

    def _get_personality_insights(self) -> Dict[str, Any]:
        """
        Gather personality insights to include in the life story.

        Collects profile information from the personality service and
        formats it for inclusion in the narrative.

        Returns:
            Dictionary containing personality traits, values, and insights.
        """
        insights = {
            'traits': [],
            'core_values': [],
            'communication_style': {},
            'behavioral_patterns': []
        }
        
        # Get from personality service if available
        if self.personality_service:
            profile = self.personality_service.build_personality_profile()
            if profile:
                insights['traits'] = profile.traits
                insights['core_values'] = profile.values
                insights['communication_style'] = profile.communication_style
                insights['behavioral_patterns'] = profile.decision_heuristics
        
        return insights

    def _generate_concluding_reflection(self, memories: List[Memory]) -> str:
        """
        Generate a concluding reflection for the life narrative.

        Creates a summary statement that captures the overall arc and significance
        of the life story.

        Args:
            memories: All memories in chronological order.

        Returns:
            A narrative conclusion as a string.
        """
        if not memories:
            return ""
        
        memory_count = len(memories)
        year_span = memories[-1].timestamp.year - memories[0].timestamp.year if len(memories) > 1 else 0
        
        conclusion = f"""## Epilogue: A Life Well-Documented

This life story is built from {memory_count} cherished memories spanning {year_span} years. 
Each memory represents a moment that shaped who this person became—the challenges overcome, 
the joys celebrated, the people loved, and the lessons learned.

The narrative presented here honors the complexity, resilience, and growth evident throughout this life journey. 
These memories and insights serve as a bridge between generations, preserving not just events, 
but the essence of a life lived with meaning, connection, and purpose.

As new memories are added, this life story continues to evolve, growing richer with each retelling."""
        
        return conclusion

    def _summarize_temporal_patterns(self, memories: List[Memory]) -> str:
        """Summarize dominant time-of-day and weekday patterns across memories."""
        if not memories:
            return ""

        from collections import Counter

        time_buckets = [m.time_of_day for m in memories if m.time_of_day]
        weekdays = [m.day_of_week for m in memories if m.day_of_week]

        if not time_buckets and not weekdays:
            return ""

        top_time = Counter(time_buckets).most_common(1)[0][0] if time_buckets else ""
        top_day = Counter(weekdays).most_common(1)[0][0] if weekdays else ""

        segments = []
        if top_time:
            segments.append(f"Many key memories happened in the {top_time}.")
        if top_day:
            segments.append(f"{top_day} appears most often in the remembered timeline.")

        return " ".join(segments)
