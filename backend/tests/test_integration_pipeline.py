"""
Integration Tests — Legacy AI Reasoning Pipeline
================================================

These tests exercise the end-to-end path from an incoming /ask-style request
through the full AI reasoning pipeline:

    FamilyInteractionAPI (POST /ask)
        → ConversationEngine.generate_response()
            → MemoryEmbeddingService  (semantic search)
            → MemoryCaptureService    (full memory retrieval)
            → TimelineEngine          (chronological context)
            → PersonalityModelService (personality profile)
            → MemoryDistillationService (distilled wisdom)
            → LegacyAccessService     (access control)
            → ResponseModerationService (safety review)
        ← structured AskResponse

All services are constructed in process — no mocking — so these tests verify
real interactions between components. Run with:

    pytest backend/tests/test_integration_pipeline.py -v
or
    make test
"""

import os
import sys
import unittest
import json
import tempfile
import uuid
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — mirror the pattern used by all other test modules
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

# ---------------------------------------------------------------------------
# Service imports
# ---------------------------------------------------------------------------
from services.memory_capture_service import MemoryCaptureService  # noqa: E402
from services.timeline_engine import TimelineEngine  # noqa: E402
from services.memory.memory_embedding_service import MemoryEmbeddingService  # noqa: E402
from services.ai.conversation_engine import ConversationEngine  # noqa: E402
from services.ai.personality_model_service import PersonalityModelService  # noqa: E402
from services.ai.memory_distillation_service import MemoryDistillationService  # noqa: E402
from services.security.legacy_access_service import (  # noqa: E402
    LegacyAccessService,
    Relationship,
)
from services.security.response_moderation_service import ResponseModerationService  # noqa: E402
from utils.test_logger import test_logger  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

BIRTH_DATE = date(1945, 6, 15)
DEFAULT_SAMPLE_DATASET = Path(ROOT_DIR) / "data" / "sample_memories.json"
SAMPLE_DATASET_ENV_VAR = "LEGACY_SAMPLE_MEMORIES_FILE"

# A set of realistic memories used across the integration suite
SEED_MEMORIES = [
    {
        "title": "Learning to ride a bicycle",
        "description": (
            "I learned to ride a bicycle in the summer of 1953. "
            "My father held the seat and let go when I wasn't looking. "
            "I realized I could balance on my own and pedalled down the street laughing."
        ),
        "timestamp": datetime(1953, 7, 4),
        "people_involved": ["father"],
        "location": "Front street, hometown",
        "emotions": ["joy", "pride", "surprise"],
        "tags": ["childhood", "learning", "family"],
        "sensitivity_tags": ["public"],
    },
    {
        "title": "First day at university",
        "description": (
            "Arrived at the university dormitory with a single suitcase. "
            "The city was enormous and I felt very small. "
            "Learned that adapting to new environments is a skill worth developing."
        ),
        "timestamp": datetime(1963, 9, 1),
        "people_involved": [],
        "location": "University campus",
        "emotions": ["nervous", "excited", "hopeful"],
        "tags": ["education", "independence", "growth"],
        "sensitivity_tags": ["personal"],
    },
    {
        "title": "Meeting my future spouse",
        "description": (
            "Met Sarah at a library during a study group session. "
            "We talked for hours and I completely lost track of time. "
            "Better to take chances on connection than to remain alone."
        ),
        "timestamp": datetime(1966, 3, 12),
        "people_involved": ["Sarah"],
        "location": "City library",
        "emotions": ["excitement", "nervousness", "happiness"],
        "tags": ["relationships", "love", "friendship"],
        "sensitivity_tags": ["personal"],
    },
    {
        "title": "Career promotion setback",
        "description": (
            "I was passed over for promotion after ten years with the company. "
            "I regret not speaking up about my accomplishments earlier. "
            "Should have advocated for myself instead of waiting to be noticed."
        ),
        "timestamp": datetime(1978, 11, 3),
        "people_involved": ["manager"],
        "location": "Office, downtown",
        "emotions": ["disappointment", "frustration", "determination"],
        "tags": ["career", "growth", "regret"],
        "sensitivity_tags": ["personal"],
    },
    {
        "title": "Retirement farewell party",
        "description": (
            "After forty years the team organised a wonderful farewell. "
            "I learned that the relationships you build matter far more than the titles you hold. "
            "Family and colleagues gathered — it was the proudest day of my working life."
        ),
        "timestamp": datetime(2005, 4, 28),
        "people_involved": ["Sarah", "colleagues", "children"],
        "location": "Company headquarters",
        "emotions": ["gratitude", "pride", "nostalgia"],
        "tags": ["retirement", "career", "family", "reflection"],
        "sensitivity_tags": ["public"],
    },
]


def _parse_memory_timestamp(value):
    """Parse timestamp values from JSON into datetime objects."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError(f"Unsupported timestamp format: {type(value).__name__}")


def _load_seed_memories():
    """
    Load seed memories from JSON when requested via env var, otherwise use default fixture.

    If LEGACY_SAMPLE_MEMORIES_FILE is set to a valid path, this helper uses that dataset.
    If the env var is set to "1" or "true", it uses backend/data/sample_memories.json.
    """
    selector = os.getenv(SAMPLE_DATASET_ENV_VAR)
    if not selector:
        return SEED_MEMORIES

    if selector.lower() in {"1", "true", "yes", "on"}:
        dataset_path = DEFAULT_SAMPLE_DATASET
    else:
        dataset_path = Path(selector).expanduser()
        if not dataset_path.is_absolute():
            dataset_path = Path(ROOT_DIR) / dataset_path

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Sample dataset file not found: {dataset_path} (from {SAMPLE_DATASET_ENV_VAR})"
        )

    with dataset_path.open("r", encoding="utf-8") as fp:
        loaded = json.load(fp)

    if not isinstance(loaded, list):
        raise ValueError("Sample memory dataset must be a JSON array")

    normalized = []
    required_keys = {
        "title",
        "description",
        "timestamp",
        "people_involved",
        "emotions",
        "tags",
    }
    for entry in loaded:
        missing_keys = required_keys - set(entry.keys())
        if missing_keys:
            raise ValueError(f"Sample memory entry missing keys: {sorted(missing_keys)}")

        normalized.append(
            {
                "title": entry["title"],
                "description": entry["description"],
                "timestamp": _parse_memory_timestamp(entry["timestamp"]),
                "people_involved": entry.get("people_involved", []),
                "location": entry.get("location", ""),
                "emotions": entry.get("emotions", []),
                "tags": entry.get("tags", []),
                "sensitivity_tags": entry.get("sensitivity_tags", ["public"]),
            }
        )

    return normalized


def _build_pipeline(with_personality: bool = False, with_distillation: bool = False):
    """
    Create a fully wired service stack pre-loaded with SEED_MEMORIES.

    Returns a dict with all constructed service objects and the memory IDs
    so individual tests can reference specific memories.
    """
    memory_service = MemoryCaptureService()
    timeline_engine = TimelineEngine(memory_service, BIRTH_DATE)
    vector_store_file = os.path.join(
        tempfile.gettempdir(), f"legacyai_memory_test_{uuid.uuid4().hex}.json"
    )
    embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)

    # Seed memories from either hardcoded fixture or optional JSON dataset.
    seed_memories = _load_seed_memories()
    memory_ids = []
    for m in seed_memories:
        mid = memory_service.create_memory(**m)
        embedding_service.store_memory_embedding(
            mid, m["title"] + " " + m["description"]
        )
        memory_ids.append(mid)

    personality_service = None
    if with_personality:
        personality_service = PersonalityModelService(
            memory_service=memory_service,
            timeline_engine=timeline_engine,
            embedding_service=embedding_service,
        )

    distillation_service = None
    if with_distillation:
        distillation_service = MemoryDistillationService(
            memory_service=memory_service,
            timeline_engine=timeline_engine,
            embedding_service=embedding_service,
            personality_service=personality_service,
        )

    access_service = LegacyAccessService()
    moderation_service = ResponseModerationService()

    conversation_engine = ConversationEngine(
        memory_service=memory_service,
        timeline_engine=timeline_engine,
        embedding_service=embedding_service,
        distillation_service=distillation_service,
        access_service=access_service,
        moderation_service=moderation_service,
    )

    return {
        "memory_service": memory_service,
        "timeline_engine": timeline_engine,
        "embedding_service": embedding_service,
        "personality_service": personality_service,
        "distillation_service": distillation_service,
        "access_service": access_service,
        "moderation_service": moderation_service,
        "conversation_engine": conversation_engine,
        "memory_ids": memory_ids,
    }


# ---------------------------------------------------------------------------
# Integration test suite
# ---------------------------------------------------------------------------

class TestIntegrationPipeline(unittest.TestCase):
    """
    End-to-end integration tests for the Legacy AI reasoning pipeline.

    Each test constructs a complete service stack, submits a query, and
    verifies the structured response returned by ConversationEngine —
    mirroring exactly what the /ask endpoint does.
    """

    # ------------------------------------------------------------------ #
    # 1. Basic pipeline — response structure                              #
    # ------------------------------------------------------------------ #

    def test_ask_returns_required_response_keys(self):
        """
        The pipeline must always return a dict with the four mandatory keys
        expected by AskResponse: generated_answer, memories_used,
        confidence_score, and access_denied.
        """
        pipeline = _build_pipeline()
        engine = pipeline["conversation_engine"]
        test_name = "Integration.ask_returns_required_response_keys"

        try:
            result = engine.generate_response("Tell me about your childhood")

            required_keys = {"generated_answer", "memories_used", "confidence_score", "access_denied"}
            missing = required_keys - result.keys()

            self.assertFalse(missing, f"Response is missing keys: {missing}")
            self.assertIsInstance(result["generated_answer"], str)
            self.assertIsInstance(result["memories_used"], list)
            self.assertIsInstance(result["confidence_score"], float)
            self.assertIsInstance(result["access_denied"], bool)

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "Tell me about your childhood"},
                expected_result={"has_all_required_keys": True},
                actual_result={
                    "keys_present": list(result.keys()),
                    "generated_answer_type": type(result["generated_answer"]).__name__,
                    "memories_used_count": len(result["memories_used"]),
                    "confidence_score": result["confidence_score"],
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "Tell me about your childhood"},
                expected_result={"has_all_required_keys": True},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 2. Memory retrieval — pipeline surfaces stored memories             #
    # ------------------------------------------------------------------ #

    def test_memories_used_references_seeded_memory_ids(self):
        """
        After seeding known memories, a relevant query should return
        memories_used IDs that are a subset of the seeded memory IDs.
        """
        pipeline = _build_pipeline()
        engine = pipeline["conversation_engine"]
        seeded_ids = set(pipeline["memory_ids"])
        test_name = "Integration.memories_used_references_seeded_memory_ids"

        try:
            result = engine.generate_response("What did you learn growing up?")
            returned_ids = set(result["memories_used"])

            # All returned IDs must belong to the seeded set
            self.assertTrue(
                returned_ids.issubset(seeded_ids),
                f"memories_used contains unknown IDs: {returned_ids - seeded_ids}",
            )

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What did you learn growing up?"},
                expected_result={"memories_used_subset_of_seeded": True},
                actual_result={
                    "memories_used": list(returned_ids),
                    "seeded_count": len(seeded_ids),
                    "returned_count": len(returned_ids),
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What did you learn growing up?"},
                expected_result={"memories_used_subset_of_seeded": True},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 3. Confidence score — valid range                                   #
    # ------------------------------------------------------------------ #

    def test_confidence_score_within_valid_range(self):
        """
        confidence_score must be a float in [0.0, 1.0].
        """
        pipeline = _build_pipeline()
        engine = pipeline["conversation_engine"]
        test_name = "Integration.confidence_score_within_valid_range"

        try:
            result = engine.generate_response("What advice would you give about relationships?")
            score = result["confidence_score"]

            self.assertGreaterEqual(score, 0.0, "confidence_score must be >= 0.0")
            self.assertLessEqual(score, 1.0, "confidence_score must be <= 1.0")

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What advice would you give about relationships?"},
                expected_result={"confidence_score_range": "[0.0, 1.0]"},
                actual_result={"confidence_score": score},
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What advice would you give about relationships?"},
                expected_result={"confidence_score_range": "[0.0, 1.0]"},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 4. ConversationEngine + PersonalityModelService                     #
    # ------------------------------------------------------------------ #

    def test_pipeline_with_personality_model_integration(self):
        """
        When PersonalityModelService is in the stack the pipeline must still
        return a valid response. Validates that the personality layer does not
        break the pipeline contract.
        """
        pipeline = _build_pipeline(with_personality=True)
        engine = pipeline["conversation_engine"]
        personality_service = pipeline["personality_service"]
        test_name = "Integration.pipeline_with_personality_model"

        try:
            # Build the profile directly and verify it is non-trivial
            profile = personality_service.build_personality_profile()
            self.assertIsNotNone(profile)

            # Attach the profile to the conversation engine
            engine.personality_profile = profile

            result = engine.generate_response("How did you handle tough decisions?")

            self.assertIn("generated_answer", result)
            self.assertIsInstance(result["generated_answer"], str)
            self.assertGreaterEqual(result["confidence_score"], 0.0)

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "How did you handle tough decisions?"},
                expected_result={"pipeline_intact_with_personality": True},
                actual_result={
                    "profile_traits": profile.traits,
                    "profile_values": profile.values,
                    "confidence_score": result["confidence_score"],
                    "memories_used_count": len(result["memories_used"]),
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "How did you handle tough decisions?"},
                expected_result={"pipeline_intact_with_personality": True},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 5. ConversationEngine + MemoryDistillationService                   #
    # ------------------------------------------------------------------ #

    def test_pipeline_with_memory_distillation_integration(self):
        """
        When MemoryDistillationService is wired in, the pipeline should
        surface insights_used and still satisfy the response contract.
        """
        pipeline = _build_pipeline(with_personality=True, with_distillation=True)
        engine = pipeline["conversation_engine"]
        test_name = "Integration.pipeline_with_memory_distillation"

        try:
            result = engine.generate_response(
                "What lessons did you learn from your career?"
            )

            self.assertIn("generated_answer", result)
            self.assertIn("insights_used", result)
            self.assertIsInstance(result["insights_used"], list)
            self.assertGreaterEqual(result["confidence_score"], 0.0)

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What lessons did you learn from your career?"},
                expected_result={
                    "pipeline_intact_with_distillation": True,
                    "insights_used_is_list": True,
                },
                actual_result={
                    "insights_used_count": len(result["insights_used"]),
                    "insights_sample": result["insights_used"][:2],
                    "confidence_score": result["confidence_score"],
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What lessons did you learn from your career?"},
                expected_result={"pipeline_intact_with_distillation": True},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 6. ResponseModerationService — safe content passes through          #
    # ------------------------------------------------------------------ #

    def test_moderation_does_not_block_safe_response(self):
        """
        A query about normal life memories should pass the moderation layer
        without triggering the safe_alternative fallback.
        """
        pipeline = _build_pipeline()
        moderation_service = pipeline["moderation_service"]
        engine = pipeline["conversation_engine"]
        test_name = "Integration.moderation_does_not_block_safe_response"

        try:
            result = engine.generate_response("Tell me about your family vacations")

            # Independently verify the moderation service's own judgement
            review = moderation_service.review_response(result["generated_answer"])
            is_safe = review.get("is_safe", True)

            self.assertTrue(
                is_safe,
                f"Moderation flagged a safe response: {result['generated_answer']!r}",
            )

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "Tell me about your family vacations"},
                expected_result={"moderation_is_safe": True},
                actual_result={
                    "is_safe": is_safe,
                    "moderation_keys": list(review.keys()),
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "Tell me about your family vacations"},
                expected_result={"moderation_is_safe": True},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 7. Access control — authorised beneficiary receives memories        #
    # ------------------------------------------------------------------ #

    def test_authorised_beneficiary_can_retrieve_public_memories(self):
        """
        A registered child beneficiary must be able to access memories
        tagged 'public'. access_denied should remain False.
        """
        pipeline = _build_pipeline()
        access_service = pipeline["access_service"]
        engine = pipeline["conversation_engine"]
        test_name = "Integration.authorised_beneficiary_receives_public_memories"

        try:
            # Register a child and activate the legacy
            access_service.register_beneficiary("child_user", Relationship.CHILD)
            access_service.verify_legacy_activation("deceased")

            result = engine.generate_response(
                "What are some of your favourite memories?",
                user_id="child_user",
            )

            self.assertIn("generated_answer", result)
            self.assertFalse(
                result.get("access_denied", False),
                "access_denied should be False for an authorised child beneficiary",
            )

            test_logger.log_test_result(
                test_name=test_name,
                input_params={
                    "query": "What are some of your favourite memories?",
                    "user_id": "child_user",
                    "relationship": "CHILD",
                },
                expected_result={"access_denied": False},
                actual_result={
                    "access_denied": result.get("access_denied"),
                    "memories_used_count": len(result["memories_used"]),
                    "confidence_score": result["confidence_score"],
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"user_id": "child_user", "relationship": "CHILD"},
                expected_result={"access_denied": False},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 8. Empty memory store — graceful degradation                        #
    # ------------------------------------------------------------------ #

    def test_pipeline_handles_empty_memory_store_gracefully(self):
        """
        When no memories have been seeded the pipeline must still return a
        structurally valid response (not raise an exception) and
        memories_used should be an empty list.
        """
        memory_service = MemoryCaptureService()
        birth_date = date(1950, 1, 1)
        timeline_engine = TimelineEngine(memory_service, birth_date)
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_memory_empty_test_{uuid.uuid4().hex}.json"
        )
        embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)

        engine = ConversationEngine(
            memory_service=memory_service,
            timeline_engine=timeline_engine,
            embedding_service=embedding_service,
        )
        test_name = "Integration.pipeline_handles_empty_memory_store"

        try:
            result = engine.generate_response("What was your childhood like?")

            self.assertIn("generated_answer", result)
            self.assertIsInstance(result["memories_used"], list)
            self.assertEqual(
                result["memories_used"],
                [],
                "memories_used should be empty when no memories have been stored",
            )

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What was your childhood like?", "seeded_memories": 0},
                expected_result={"memories_used": []},
                actual_result={
                    "memories_used": result["memories_used"],
                    "confidence_score": result["confidence_score"],
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "What was your childhood like?", "seeded_memories": 0},
                expected_result={"memories_used": []},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 9. Timeline context — chronological ordering preserved              #
    # ------------------------------------------------------------------ #

    def test_timeline_engine_provides_chronological_context(self):
        """
        TimelineEngine.get_chronological_timeline() must return seeded
        memories in ascending timestamp order, confirming the timeline
        service is correctly wired into the pipeline.
        """
        pipeline = _build_pipeline()
        timeline_engine = pipeline["timeline_engine"]
        test_name = "Integration.timeline_engine_chronological_order"

        try:
            timeline = timeline_engine.get_chronological_timeline()
            expected_seed_count = len(_load_seed_memories())

            self.assertEqual(len(timeline), expected_seed_count)

            timestamps = [m.timestamp for m in timeline]
            self.assertEqual(
                timestamps,
                sorted(timestamps),
                "Timeline memories are not in ascending chronological order",
            )

            test_logger.log_test_result(
                test_name=test_name,
                input_params={"seeded_memories": expected_seed_count},
                expected_result={"memories_sorted_ascending": True},
                actual_result={
                    "timeline_length": len(timeline),
                    "first_event_title": timeline[0].title if timeline else None,
                    "last_event_title": timeline[-1].title if timeline else None,
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"seeded_memories": "dynamic"},
                expected_result={"memories_sorted_ascending": True},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise

    # ------------------------------------------------------------------ #
    # 10. Full stack — all services active simultaneously                 #
    # ------------------------------------------------------------------ #

    def test_full_stack_all_services_active(self):
        """
        Runs the pipeline with every optional service enabled
        (PersonalityModelService + MemoryDistillationService +
        LegacyAccessService + ResponseModerationService) and asserts
        the complete response contract is satisfied.
        """
        pipeline = _build_pipeline(with_personality=True, with_distillation=True)
        engine = pipeline["conversation_engine"]
        access_service = pipeline["access_service"]
        test_name = "Integration.full_stack_all_services_active"

        try:
            access_service.register_beneficiary("spouse_user", Relationship.SPOUSE)
            access_service.verify_legacy_activation("deceased")

            result = engine.generate_response(
                "What do you remember most about your life?",
                user_id="spouse_user",
            )

            # Full contract check
            self.assertIn("generated_answer", result)
            self.assertIn("memories_used", result)
            self.assertIn("insights_used", result)
            self.assertIn("confidence_score", result)
            self.assertIn("access_denied", result)

            self.assertIsInstance(result["generated_answer"], str)
            self.assertIsInstance(result["memories_used"], list)
            self.assertIsInstance(result["insights_used"], list)
            self.assertGreaterEqual(result["confidence_score"], 0.0)
            self.assertLessEqual(result["confidence_score"], 1.0)

            test_logger.log_test_result(
                test_name=test_name,
                input_params={
                    "query": "What do you remember most about your life?",
                    "user_id": "spouse_user",
                    "services_active": [
                        "PersonalityModelService",
                        "MemoryDistillationService",
                        "LegacyAccessService",
                        "ResponseModerationService",
                    ],
                },
                expected_result={"all_response_keys_present": True, "pipeline_intact": True},
                actual_result={
                    "memories_used_count": len(result["memories_used"]),
                    "insights_used_count": len(result["insights_used"]),
                    "confidence_score": result["confidence_score"],
                    "access_denied": result["access_denied"],
                    "moderation_present": result.get("moderation") is not None,
                },
                status="PASS",
            )
        except Exception as exc:
            test_logger.log_test_result(
                test_name=test_name,
                input_params={"query": "full_stack"},
                expected_result={"pipeline_intact": True},
                actual_result=f"Exception: {exc}",
                status="FAIL",
            )
            raise


if __name__ == "__main__":
    unittest.main()
