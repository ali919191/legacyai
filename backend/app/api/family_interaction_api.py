"""
Family Interaction API for Legacy AI Platform

This module provides REST API endpoints that allow beneficiaries and family members
to interact with the Legacy AI system. The API serves as the primary interface for
conversational interactions, memory browsing, and timeline exploration.

The API integrates with the complete AI reasoning pipeline:
1. User queries are processed through the ConversationEngine
2. Access control is enforced via LegacyAccessService
3. Responses are moderated through ResponseModerationService
4. Memory retrieval respects authorization boundaries
5. Timeline data provides chronological context

Authentication is designed to be added later through middleware or decorators.
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

# Import core services
from ..services.memory_capture_service import MemoryCaptureService, Memory
from ..services.timeline_engine import TimelineEngine
from ..services.ai.conversation_engine import ConversationEngine
from ..services.memory.memory_embedding_service import MemoryEmbeddingService
from ..services.security.legacy_access_service import LegacyAccessService, MemoryMetadata
from ..services.security.response_moderation_service import ResponseModerationService


# Pydantic models for API requests/responses
class AskRequest(BaseModel):
    """Request model for asking questions to Legacy AI."""
    query: str
    user_id: Optional[str] = None  # For access control (can be None for now)


class AskResponse(BaseModel):
    """Response model for Legacy AI answers."""
    answer: str
    memories_used: List[str]
    memory_details: List[Dict[str, Any]]
    memory_priority: List[Dict[str, Any]]
    insights_used: List[str]
    enhanced_questions: List[Dict[str, Any]]
    confidence_score: float
    access_denied: bool
    moderation_applied: bool
    timestamp: datetime


class EnhancedQuestionResponse(BaseModel):
    """Response model for pending or answered enhanced questions."""
    question_id: str
    question: str
    related_memory_id: str
    source_conversation_timestamp: str
    context_description: str
    priority: str
    status: str
    user_id: str
    person_id: Optional[str] = None
    answer: Optional[str] = None
    answered_timestamp: Optional[str] = None


class EnhancedQuestionAnswerRequest(BaseModel):
    """Request model for answering an enhanced follow-up question."""
    answer: str
    memory_updates: Optional[Dict[str, Any]] = None
    person_updates: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    """Response model for individual memories."""
    id: str
    title: str
    description: str
    timestamp: datetime
    people_involved: List[str]
    location: str
    emotions: List[str]
    tags: List[str]


class TimelineEvent(BaseModel):
    """Response model for timeline events."""
    id: str
    title: str
    description: str
    timestamp: datetime
    life_stage: str
    age: int


class CreateMemoryRequest(BaseModel):
    """Request model for ingesting a new memory."""
    title: str
    description: str
    timestamp: Optional[str] = None          # ISO-8601 string; defaults to now
    people_involved: Optional[List[str]] = None
    location: Optional[str] = ""
    emotions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    sensitivity_tags: Optional[List[str]] = None


class CreateMemoryResponse(BaseModel):
    """Response model after memory creation."""
    memory_id: str
    title: str


class FamilyInteractionAPI:
    """
    Family Interaction API for the Legacy AI platform.

    This API provides endpoints for family members to interact with the AI system,
    browse memories, and explore life timelines. It integrates with the complete
    AI reasoning pipeline while enforcing access controls and response moderation.

    The API is designed with future authentication in mind - user_id parameters
    can be populated from authentication tokens or session data.
    """

    def __init__(
        self,
        memory_service: MemoryCaptureService,
        timeline_engine: TimelineEngine,
        conversation_engine: ConversationEngine,
        access_service: Optional[LegacyAccessService] = None,
        moderation_service: Optional[ResponseModerationService] = None,
        embedding_service: Optional[MemoryEmbeddingService] = None,
    ):
        """
        Initialize the Family Interaction API.

        Args:
            memory_service: Service for memory storage and retrieval
            timeline_engine: Engine for chronological memory organization
            conversation_engine: Engine for generating AI responses
            access_service: Optional service for access control and privacy
            moderation_service: Optional service for response safety and appropriateness
            embedding_service: Optional service for storing/searching memory embeddings
        """
        self.memory_service = memory_service
        self.timeline_engine = timeline_engine
        self.conversation_engine = conversation_engine
        self.access_service = access_service
        self.moderation_service = moderation_service
        self.embedding_service = embedding_service

        # Create FastAPI app
        self.app = FastAPI(
            title="Legacy AI Family Interaction API",
            description="API for family members to interact with Legacy AI system",
            version="1.0.0"
        )

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register all API routes."""

        @self.app.post("/memories", response_model=CreateMemoryResponse, tags=["Memories"])
        async def ingest_memory(request: CreateMemoryRequest):
            """Ingest a new memory into the platform."""
            try:
                ts = datetime.fromisoformat(request.timestamp) if request.timestamp else None
                memory_id = self.memory_service.create_memory(
                    title=request.title,
                    description=request.description,
                    timestamp=ts,
                    people_involved=request.people_involved or [],
                    location=request.location or "",
                    emotions=request.emotions or [],
                    tags=request.tags or [],
                    sensitivity_tags=request.sensitivity_tags or [],
                )
                if self.embedding_service:
                    embed_text = f"{request.title}. {request.description}"
                    self.embedding_service.store_memory_embedding(memory_id, embed_text)
                return CreateMemoryResponse(memory_id=memory_id, title=request.title)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error creating memory: {str(e)}")

        @self.app.post("/ask", response_model=AskResponse)
        async def ask_question(request: AskRequest):
            """
            Ask a question to the Legacy AI system.

            This endpoint processes user queries through the complete AI reasoning pipeline:
            1. Semantic search for relevant memories
            2. Access control filtering (if user_id provided)
            3. Response generation with personality and context
            4. Response moderation for safety and appropriateness
            5. Return structured response with metadata

            Args:
                request: AskRequest containing the query and optional user_id

            Returns:
                AskResponse with the AI answer and processing metadata
            """
            try:
                # Generate response using conversation engine
                result = self.conversation_engine.generate_response(
                    user_query=request.query,
                    user_id=request.user_id
                )

                # Extract moderation info
                moderation_applied = (result.get('moderation') or {}).get('is_safe', True) == False

                return AskResponse(
                    answer=result['generated_answer'],
                    memories_used=result['memories_used'],
                    memory_details=result.get('memory_details', []),
                    memory_priority=result.get('memory_priority', []),
                    insights_used=result['insights_used'],
                    enhanced_questions=result.get('enhanced_questions', []),
                    confidence_score=result['confidence_score'],
                    access_denied=result['access_denied'],
                    moderation_applied=moderation_applied,
                    timestamp=datetime.now()
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

        @self.app.get("/enhanced-questions", response_model=List[EnhancedQuestionResponse])
        async def get_enhanced_questions(
            user_id: str = Query(..., description="User ID for pending enhanced questions"),
        ):
            """Retrieve pending enhanced questions for the widget UI."""
            try:
                service = getattr(self.conversation_engine, "knowledge_gap_service", None)
                if not service:
                    return []
                return service.retrieve_pending_questions(user_id)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error retrieving enhanced questions: {str(e)}",
                )

        @self.app.post(
            "/enhanced-questions/{question_id}/answer",
            response_model=EnhancedQuestionResponse,
        )
        async def answer_enhanced_question(
            question_id: str,
            request: EnhancedQuestionAnswerRequest,
        ):
            """Answer a pending enhanced question and enrich stored knowledge."""
            try:
                result = self.conversation_engine.answer_enhanced_question(
                    question_id=question_id,
                    answer_text=request.answer,
                    memory_updates=request.memory_updates,
                    person_updates=request.person_updates,
                )
                if not result:
                    raise HTTPException(status_code=404, detail="Enhanced question not found")
                return result
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error answering enhanced question: {str(e)}",
                )

        @self.app.get("/timeline", response_model=List[TimelineEvent])
        async def get_timeline(
            user_id: Optional[str] = Query(None, description="User ID for access control"),
            limit: int = Query(50, description="Maximum number of events to return")
        ):
            """
            Get major life events from the timeline.

            This endpoint returns chronologically organized life events, filtered
            by access control if a user_id is provided. Events are enriched with
            life stage and age information.

            Args:
                user_id: Optional user ID for access filtering
                limit: Maximum number of events to return

            Returns:
                List of TimelineEvent objects with chronological life events
            """
            try:
                # Get chronological timeline
                timeline_memories = self.timeline_engine.get_chronological_timeline()

                # Apply access control if user_id provided
                if user_id and self.access_service:
                    filtered_memories = []
                    for memory in timeline_memories:
                        memory_metadata = MemoryMetadata(
                            memory_id=memory.id,
                            sensitivity_tags=memory.sensitivity_tags or [],
                            created_date=memory.timestamp.isoformat() if hasattr(memory.timestamp, 'isoformat') else str(memory.timestamp),
                            is_legacy_active=True
                        )

                        if self.access_service.authorize_memory_access(user_id, memory_metadata):
                            filtered_memories.append(memory)
                    timeline_memories = filtered_memories

                # Convert to timeline events
                events = []
                for memory in timeline_memories[:limit]:
                    age = self.timeline_engine._calculate_age(memory.timestamp)
                    life_stage = self.timeline_engine._get_life_stage(age)

                    events.append(TimelineEvent(
                        id=memory.id,
                        title=memory.title,
                        description=memory.description[:200] + "..." if len(memory.description) > 200 else memory.description,
                        timestamp=memory.timestamp,
                        life_stage=life_stage,
                        age=age
                    ))

                return events

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error retrieving timeline: {str(e)}")

        @self.app.get("/memories", response_model=List[MemoryResponse])
        async def get_memories(
            user_id: Optional[str] = Query(None, description="User ID for access control"),
            category: Optional[str] = Query(None, description="Filter by memory category/tag"),
            limit: int = Query(20, description="Maximum number of memories to return"),
            offset: int = Query(0, description="Number of memories to skip")
        ):
            """
            Retrieve memories that the user is authorized to view.

            This endpoint returns memories filtered by access control permissions.
            Memories can be further filtered by category/tags and paginated.

            Args:
                user_id: Optional user ID for access filtering
                category: Optional category/tag to filter memories
                limit: Maximum number of memories to return
                offset: Number of memories to skip (for pagination)

            Returns:
                List of MemoryResponse objects containing authorized memories
            """
            try:
                # Get all memories
                all_memories = self.memory_service.retrieve_all_memories()

                # Apply access control if user_id provided
                if user_id and self.access_service:
                    filtered_memories = []
                    for memory in all_memories:
                        memory_metadata = MemoryMetadata(
                            memory_id=memory.id,
                            sensitivity_tags=memory.sensitivity_tags or [],
                            created_date=memory.timestamp.isoformat() if hasattr(memory.timestamp, 'isoformat') else str(memory.timestamp),
                            is_legacy_active=True
                        )

                        if self.access_service.authorize_memory_access(user_id, memory_metadata):
                            filtered_memories.append(memory)
                    all_memories = filtered_memories

                # Apply category filter if specified
                if category:
                    category_memories = [
                        mem for mem in all_memories
                        if category.lower() in [tag.lower() for tag in mem.tags]
                    ]
                    all_memories = category_memories

                # Apply pagination
                paginated_memories = all_memories[offset:offset + limit]

                # Convert to response format
                memory_responses = []
                for memory in paginated_memories:
                    memory_responses.append(MemoryResponse(
                        id=memory.id,
                        title=memory.title,
                        description=memory.description,
                        timestamp=memory.timestamp,
                        people_involved=memory.people_involved,
                        location=memory.location,
                        emotions=memory.emotions,
                        tags=memory.tags
                    ))

                return memory_responses

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error retrieving memories: {str(e)}")

        @self.app.get("/health")
        async def health_check():
            """
            Health check endpoint to verify API status.

            Returns:
                Dict with API status and service information
            """
            return {
                "status": "healthy",
                "timestamp": datetime.now(),
                "services": {
                    "memory_service": "available",
                    "timeline_engine": "available",
                    "conversation_engine": "available",
                    "access_service": "available" if self.access_service else "not_configured",
                    "moderation_service": "available" if self.moderation_service else "not_configured"
                }
            }


# Create a function to get the FastAPI app instance
def create_family_interaction_api(
    memory_service: MemoryCaptureService,
    timeline_engine: TimelineEngine,
    conversation_engine: ConversationEngine,
    access_service: Optional[LegacyAccessService] = None,
    moderation_service: Optional[ResponseModerationService] = None,
    embedding_service: Optional[MemoryEmbeddingService] = None,
) -> FastAPI:
    """
    Factory function to create and configure the Family Interaction API.

    Args:
        memory_service: Service for memory storage and retrieval
        timeline_engine: Engine for chronological memory organization
        conversation_engine: Engine for generating AI responses
        access_service: Optional service for access control and privacy
        moderation_service: Optional service for response safety and appropriateness
        embedding_service: Optional service for storing/searching memory embeddings

    Returns:
        Configured FastAPI application instance
    """
    api = FamilyInteractionAPI(
        memory_service=memory_service,
        timeline_engine=timeline_engine,
        conversation_engine=conversation_engine,
        access_service=access_service,
        moderation_service=moderation_service,
        embedding_service=embedding_service,
    )

    return api.app