"""AI services package for Legacy AI.

Contains conversation engine, personality modeling, and memory distillation services for AI-powered interactions with memories.
"""

from .conversation_engine import ConversationEngine
from .personality_model_service import PersonalityModelService, PersonalityProfile
from .memory_distillation_service import MemoryDistillationService, DistilledInsight

__all__ = [
    'ConversationEngine',
    'PersonalityModelService',
    'PersonalityProfile',
    'MemoryDistillationService',
    'DistilledInsight'
]