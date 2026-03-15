import os
import sys
import unittest

# Ensure tests import from the correct package path without pulling in backend/app.py
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.security.legacy_access_service import (
    LegacyAccessService,
    Relationship,
    MemoryMetadata,
    AccessLevel,
)


class TestLegacyAccessService(unittest.TestCase):
    def test_register_beneficiary_and_duplicate_registration(self):
        service = LegacyAccessService()

        # Register a beneficiary and ensure it succeeds
        result = service.register_beneficiary("user_1", Relationship.CHILD)
        self.assertTrue(result)

        # Registering the same user again should fail
        result_duplicate = service.register_beneficiary("user_1", Relationship.CHILD)
        self.assertFalse(result_duplicate)

    def test_access_level_assignment_by_relationship(self):
        service = LegacyAccessService()

        mapping = {
            Relationship.CHILD: AccessLevel.FULL_ACCESS,
            Relationship.SPOUSE: AccessLevel.FULL_ACCESS,
            Relationship.PARENT: AccessLevel.LIMITED_ACCESS,
            Relationship.SIBLING: AccessLevel.LIMITED_ACCESS,
            Relationship.FRIEND: AccessLevel.RESTRICTED_ACCESS,
            Relationship.OTHER: AccessLevel.RESTRICTED_ACCESS,
        }

        for relationship, expected_level in mapping.items():
            service = LegacyAccessService()
            service.register_beneficiary("user_2", relationship)
            service.verify_legacy_activation("deceased")
            self.assertEqual(service.get_access_level("user_2"), expected_level)

    def test_authorize_memory_access_restrictions_and_allowances(self):
        service = LegacyAccessService()
        service.register_beneficiary("child_id", Relationship.CHILD)
        service.register_beneficiary("friend_id", Relationship.FRIEND)

        # Legacy must be activated for access to be granted
        self.assertFalse(
            service.authorize_memory_access(
                "child_id",
                MemoryMetadata(
                    memory_id="mem1",
                    sensitivity_tags=["public"],
                    created_date="2026-01-01",
                    is_legacy_active=False,
                ),
            )
        )

        service.verify_legacy_activation("deceased")

        # Child has FULL_ACCESS: should authorize all sensitivity tags
        for tag in ["public", "personal", "medical", "financial", "intimate"]:
            self.assertTrue(
                service.authorize_memory_access(
                    "child_id",
                    MemoryMetadata(
                        memory_id=f"mem_{tag}",
                        sensitivity_tags=[tag],
                        created_date="2026-01-01",
                        is_legacy_active=True,
                    ),
                )
            )

        # Friend has RESTRICTED_ACCESS: should allow public but deny personal and higher
        self.assertTrue(
            service.authorize_memory_access(
                "friend_id",
                MemoryMetadata(
                    memory_id="mem_public",
                    sensitivity_tags=["public"],
                    created_date="2026-01-01",
                    is_legacy_active=True,
                ),
            )
        )

        self.assertFalse(
            service.authorize_memory_access(
                "friend_id",
                MemoryMetadata(
                    memory_id="mem_personal",
                    sensitivity_tags=["personal"],
                    created_date="2026-01-01",
                    is_legacy_active=True,
                ),
            )
        )

        self.assertFalse(
            service.authorize_memory_access(
                "friend_id",
                MemoryMetadata(
                    memory_id="mem_medical",
                    sensitivity_tags=["medical"],
                    created_date="2026-01-01",
                    is_legacy_active=True,
                ),
            )
        )

    def test_authorize_memory_access_intimate_requires_spouse_or_child(self):
        service = LegacyAccessService()
        service.register_beneficiary("sibling_id", Relationship.SIBLING)
        service.verify_legacy_activation("deceased")

        # Sibling should be denied access to intimate memory
        self.assertFalse(
            service.authorize_memory_access(
                "sibling_id",
                MemoryMetadata(
                    memory_id="mem_intimate",
                    sensitivity_tags=["intimate"],
                    created_date="2026-01-01",
                    is_legacy_active=True,
                ),
            )
        )

        # Add spouse and check intimate access is allowed
        service.register_beneficiary("spouse_id", Relationship.SPOUSE)
        self.assertTrue(
            service.authorize_memory_access(
                "spouse_id",
                MemoryMetadata(
                    memory_id="mem_intimate",
                    sensitivity_tags=["intimate"],
                    created_date="2026-01-01",
                    is_legacy_active=True,
                ),
            )
        )
