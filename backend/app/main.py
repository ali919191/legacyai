"""
Legacy AI Platform — FastAPI Application Entry Point

Start locally:
    uvicorn backend.app.main:app --reload

Start with Docker:
    docker compose up
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import date

from dotenv import load_dotenv

# Load .env before any service modules so environment-driven settings are present.
load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from .api.family_interaction_api import create_family_interaction_api  # noqa: E402
from .services.ai.conversation_engine import ConversationEngine  # noqa: E402
from .services.ai.knowledge_gap_service import KnowledgeGapService  # noqa: E402
from .services.ai.identity_model_service import IdentityModelService  # noqa: E402
from .services.ai.memory_distillation_service import MemoryDistillationService  # noqa: E402
from .services.ai.memory_grounding_service import MemoryGroundingService  # noqa: E402
from .services.ai.memory_priority_service import MemoryPriorityService  # noqa: E402
from .services.ai.recipient_context_service import RecipientContextService  # noqa: E402
from .services.ai.wisdom_engine import WisdomEngine  # noqa: E402
from .services.entity.person_profile_service import PersonProfileService  # noqa: E402
from .services.entity.relationship_service import RelationshipService  # noqa: E402
from .services.episode.episode_service import EpisodeService  # noqa: E402
from .services.memory_capture_service import MemoryCaptureService  # noqa: E402
from .services.memory.memory_embedding_service import MemoryEmbeddingService  # noqa: E402
from .services.security.legacy_access_service import LegacyAccessService  # noqa: E402
from .services.security.response_moderation_service import ResponseModerationService  # noqa: E402
from .services.timeline_engine import TimelineEngine  # noqa: E402
from ..config.database_config import load_database_config  # noqa: E402
from .services.storage.hybrid_storage import (  # noqa: E402
    InMemoryDocumentBackend,
    InMemoryGraphBackend,
    Neo4jGraphBackend,
    PostgresJsonbDocumentBackend,
)

# ── Logging ───────────────────────────────────────────────────────────────────

_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("legacyai")


# ── Service wiring ────────────────────────────────────────────────────────────

def _parse_birth_date() -> date:
    """
    Read PERSONA_BIRTH_DATE from the environment (format: YYYY-MM-DD).
    Falls back to 1950-01-01 when the variable is absent or malformed.
    Set this in .env to match the person whose memories are being preserved.
    """
    raw = os.getenv("PERSONA_BIRTH_DATE", "1950-01-01")
    try:
        return date.fromisoformat(raw)
    except ValueError:
        logger.warning(
            "PERSONA_BIRTH_DATE='%s' is not a valid ISO date; defaulting to 1950-01-01.",
            raw,
        )
        return date(1950, 1, 1)


def _build_services() -> dict:
    """Instantiate and wire all platform services."""
    vector_store_file = os.getenv("VECTOR_STORE_FILE", "memory_embeddings.json")
    birth_date = _parse_birth_date()
    db_config = load_database_config()

    graph_backend = InMemoryGraphBackend()
    if db_config.graph_provider == "neo4j":
        graph_backend = Neo4jGraphBackend(
            uri=db_config.graph_neo4j_uri,
            user=db_config.graph_neo4j_user,
            password=db_config.graph_neo4j_password,
        )

    document_backend = InMemoryDocumentBackend()
    if db_config.document_provider == "postgres_jsonb":
        document_backend = PostgresJsonbDocumentBackend(
            dsn=db_config.document_pg_dsn,
            table_name=db_config.document_pg_table,
        )

    memory_service = MemoryCaptureService(document_backend=document_backend)
    person_profile_service = PersonProfileService(
        memory_service=memory_service,
        graph_backend=graph_backend,
    )
    relationship_service = RelationshipService(
        person_profile_service=person_profile_service,
        graph_backend=graph_backend,
    )
    person_profile_service.set_relationship_service(relationship_service)
    memory_service.set_person_profile_service(person_profile_service)
    memory_service.set_relationship_service(relationship_service)
    timeline_engine = TimelineEngine(
        memory_service=memory_service,
        birth_date=birth_date,
    )
    episode_service = EpisodeService(
        memory_service=memory_service,
        timeline_engine=timeline_engine,
    )
    memory_service.set_episode_service(episode_service)
    timeline_engine.set_episode_service(episode_service)
    vector_config = {
        "dsn": db_config.vector_pg_dsn,
        "table_name": db_config.vector_pg_table,
        "api_key": db_config.vector_pinecone_api_key,
        "index_name": db_config.vector_pinecone_index,
    }
    embedding_service = MemoryEmbeddingService(
        vector_store_file=vector_store_file,
        vector_provider=db_config.vector_provider,
        vector_config=vector_config,
    )
    knowledge_gap_service = KnowledgeGapService(
        memory_service=memory_service,
        person_profile_service=person_profile_service,
    )
    identity_model_service = IdentityModelService()
    recipient_context_service = RecipientContextService()
    wisdom_engine = WisdomEngine()
    distillation_service = MemoryDistillationService(
        memory_service=memory_service,
        timeline_engine=timeline_engine,
        embedding_service=embedding_service,
        wisdom_engine=wisdom_engine,
    )
    memory_grounding_service = MemoryGroundingService()
    memory_priority_service = MemoryPriorityService()
    conversation_engine = ConversationEngine(
        memory_service=memory_service,
        timeline_engine=timeline_engine,
        embedding_service=embedding_service,
        person_profile_service=person_profile_service,
        relationship_service=relationship_service,
        distillation_service=distillation_service,
        knowledge_gap_service=knowledge_gap_service,
        memory_grounding_service=memory_grounding_service,
        memory_priority_service=memory_priority_service,
        recipient_context_service=recipient_context_service,
        identity_model_service=identity_model_service,
    )
    access_service = LegacyAccessService()
    moderation_service = ResponseModerationService()

    logger.info("All platform services initialised (birth_date=%s).", birth_date)
    return {
        "memory_service": memory_service,
        "embedding_service": embedding_service,
        "document_backend": document_backend,
        "graph_backend": graph_backend,
        "person_profile_service": person_profile_service,
        "relationship_service": relationship_service,
        "episode_service": episode_service,
        "timeline_engine": timeline_engine,
        "conversation_engine": conversation_engine,
        "knowledge_gap_service": knowledge_gap_service,
        "identity_model_service": identity_model_service,
        "recipient_context_service": recipient_context_service,
        "distillation_service": distillation_service,
        "wisdom_engine": wisdom_engine,
        "memory_grounding_service": memory_grounding_service,
        "memory_priority_service": memory_priority_service,
        "access_service": access_service,
        "moderation_service": moderation_service,
    }


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def _lifespan(application: FastAPI):  # noqa: ARG001
    logger.info("Legacy AI Platform starting up …")
    yield
    logger.info("Legacy AI Platform shutting down.")


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Create and configure the root FastAPI application.

    The Family Interaction API is mounted at ``/api/v1``, giving the following
    public routes:

    ========================  ===============================================
    Route                     Description
    ========================  ===============================================
    GET  /health              Top-level liveness check
    GET  /api/v1/health       Service-level health with dependency status
    POST /api/v1/ask          Ask a question to the Legacy AI persona
    GET  /api/v1/memories     Browse accessible memories (paginated)
    GET  /api/v1/timeline     Explore the chronological life timeline
    ========================  ===============================================

    Returns the configured :class:`fastapi.FastAPI` instance.
    """
    services = _build_services()

    # Build the Family Interaction sub-application
    family_api = create_family_interaction_api(
        memory_service=services["memory_service"],
        timeline_engine=services["timeline_engine"],
        conversation_engine=services["conversation_engine"],
        access_service=services["access_service"],
        moderation_service=services["moderation_service"],
        embedding_service=services["embedding_service"],
    )

    # Root application — wraps the sub-app with CORS, lifespan, and metadata
    root = FastAPI(
        title="Legacy AI Platform",
        description=(
            "Platform for capturing life experiences and enabling AI-powered "
            "conversations with the preserved memories of a loved one."
        ),
        version="0.1.0",
        lifespan=_lifespan,
    )

    # CORS — restrict origins in production via CORS_ORIGINS env var
    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
    root.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount family interaction API
    root.mount("/api/v1", family_api)

    @root.get("/health", tags=["Meta"])
    async def health():
        """Top-level liveness probe used by Docker and load-balancers."""
        return {"status": "ok", "service": "legacyai"}

    return root


# ── Module-level app instance consumed by uvicorn / gunicorn ──────────────────

app = create_app()
