import os
import sys
import tempfile
import unittest
import uuid
from datetime import date, datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.ai.conversation_engine import ConversationEngine
from services.entity.person_profile_service import PersonProfileService
from services.entity.relationship_service import RelationshipService
from services.memory.memory_embedding_service import MemoryEmbeddingService
from services.memory_capture_service import MemoryCaptureService
from services.timeline_engine import TimelineEngine


class TestRelationshipService(unittest.TestCase):

    def setUp(self):
        self.memory_service = MemoryCaptureService()
        self.person_profile_service = PersonProfileService(memory_service=self.memory_service)
        self.relationship_service = RelationshipService(
            person_profile_service=self.person_profile_service
        )
        self.person_profile_service.set_relationship_service(self.relationship_service)
        self.memory_service.set_person_profile_service(self.person_profile_service)
        self.memory_service.set_relationship_service(self.relationship_service)
        self.timeline_engine = TimelineEngine(self.memory_service, birth_date=date(1970, 1, 1))
        vector_store_file = os.path.join(
            tempfile.gettempdir(), f"legacyai_relationship_test_{uuid.uuid4().hex}.json"
        )
        self.embedding_service = MemoryEmbeddingService(vector_store_file=vector_store_file)

    def test_create_and_update_relationship(self):
        rel = self.relationship_service.create_relationship("Sarah", "Mike", "colleague_of")
        self.assertTrue(rel["relationship_id"].startswith("rel_"))
        self.assertEqual(rel["relationship_type"], "colleague_of")

        updated = self.relationship_service.update_relationship(
            rel["relationship_id"],
            {"relationship_type": "mentor_of", "context_memory": "mem_x"},
        )
        self.assertEqual(updated["relationship_type"], "mentor_of")
        self.assertEqual(updated["context_memory"], "mem_x")

    def test_detect_relationships_from_memory(self):
        memory_id = self.memory_service.create_memory(
            title="Office onboarding",
            description="Sarah introduced Mike to the team during onboarding.",
            timestamp=datetime(2010, 1, 15),
            people_involved=["Sarah", "Mike"],
            tags=["career", "office"],
            emotions=["excitement"],
        )
        memory = self.memory_service.retrieve_memory(memory_id)
        detected = self.relationship_service.detect_relationships_from_memory(memory)
        self.assertGreaterEqual(len(detected), 1)
        self.assertEqual(detected[0]["context_memory"], memory_id)

    def test_retrieve_relationships_for_person(self):
        self.relationship_service.create_relationship("Sarah", "Mike", "friend_of")
        self.relationship_service.create_relationship("Sarah", "Lina", "mentor_of")

        sarah_id = self.person_profile_service.search_person_by_name("Sarah")[0]["person_id"]
        relationships = self.relationship_service.retrieve_relationships_for_person(sarah_id)
        self.assertEqual(len(relationships), 2)

    def test_memory_capture_auto_detects_relationships(self):
        self.memory_service.create_memory(
            title="Family dinner",
            description="Had dinner with my sister and cousin.",
            timestamp=datetime(2011, 5, 4),
            people_involved=["Maya", "Lina"],
            tags=["family"],
            emotions=["joy"],
        )
        maya_id = self.person_profile_service.search_person_by_name("Maya")[0]["person_id"]
        rels = self.relationship_service.retrieve_relationships_for_person(maya_id)
        self.assertGreaterEqual(len(rels), 1)
        self.assertEqual(rels[0]["relationship_type"], "family_of")

    def test_conversation_engine_detects_relationships_from_query(self):
        mem_id = self.memory_service.create_memory(
            title="Work mentor",
            description="Sarah mentored Mike on the first project.",
            timestamp=datetime(2012, 8, 10),
            people_involved=["Sarah", "Mike"],
            tags=["career", "mentor"],
            emotions=["gratitude"],
        )
        self.embedding_service.store_memory_embedding(mem_id, "Work mentor Sarah Mike")

        engine = ConversationEngine(
            memory_service=self.memory_service,
            timeline_engine=self.timeline_engine,
            embedding_service=self.embedding_service,
            person_profile_service=self.person_profile_service,
            relationship_service=self.relationship_service,
        )
        engine.generate_response("Sarah and Mike worked together in the office.", user_id="child")

        sarah_id = self.person_profile_service.search_person_by_name("Sarah")[0]["person_id"]
        rels = self.relationship_service.retrieve_relationships_for_person(sarah_id)
        self.assertGreaterEqual(len(rels), 1)


if __name__ == "__main__":
    unittest.main()
