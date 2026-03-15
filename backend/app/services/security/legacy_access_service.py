from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class AccessLevel(Enum):
    """Enumeration of access levels for legacy beneficiaries."""
    RESTRICTED_ACCESS = "restricted"
    LIMITED_ACCESS = "limited"
    FULL_ACCESS = "full"


class Relationship(Enum):
    """Enumeration of beneficiary relationships."""
    CHILD = "child"
    SPOUSE = "spouse"
    PARENT = "parent"
    SIBLING = "sibling"
    FRIEND = "friend"
    OTHER = "other"


@dataclass
class Beneficiary:
    """Represents a registered beneficiary."""
    user_id: str
    relationship: Relationship
    access_level: AccessLevel
    registered_date: str
    is_active: bool = False


@dataclass
class MemoryMetadata:
    """Metadata for a memory including sensitivity information."""
    memory_id: str
    sensitivity_tags: List[str]  # e.g., ['personal', 'medical', 'financial']
    created_date: str
    is_legacy_active: bool = False


class LegacyAccessService:
    """
    Legacy Access Control Service for the Legacy AI platform.

    Manages beneficiary access to the AI system, ensuring that sensitive memories
    and information are only accessible to authorized individuals under appropriate
    conditions. This service implements a multi-layered access control system that
    considers relationship, access level, memory sensitivity, and legacy activation status.

    The system is designed to protect privacy while allowing meaningful access for
    designated beneficiaries. It includes provisions for post-mortem activation and
    graduated access levels based on relationship and trust.

    Future integration points:
    - Legal verification services for death confirmation
    - Digital estate management platforms
    - Multi-factor authentication for high-sensitivity access
    - Audit logging for compliance and security monitoring
    - Integration with government or institutional verification systems
    """

    # Sensitivity levels and their access requirements
    SENSITIVITY_REQUIREMENTS = {
        'public': AccessLevel.RESTRICTED_ACCESS,
        'personal': AccessLevel.LIMITED_ACCESS,
        'medical': AccessLevel.FULL_ACCESS,
        'financial': AccessLevel.FULL_ACCESS,
        'intimate': AccessLevel.FULL_ACCESS
    }

    # Relationship-based default access levels
    RELATIONSHIP_ACCESS_LEVELS = {
        Relationship.CHILD: AccessLevel.FULL_ACCESS,
        Relationship.SPOUSE: AccessLevel.FULL_ACCESS,
        Relationship.PARENT: AccessLevel.LIMITED_ACCESS,
        Relationship.SIBLING: AccessLevel.LIMITED_ACCESS,
        Relationship.FRIEND: AccessLevel.RESTRICTED_ACCESS,
        Relationship.OTHER: AccessLevel.RESTRICTED_ACCESS
    }

    def __init__(self):
        """Initialize the access control service."""
        self.beneficiaries: Dict[str, Beneficiary] = {}
        self.legacy_activated = False  # Global flag for legacy activation

    def register_beneficiary(self, user_id: str, relationship: Relationship) -> bool:
        """
        Register a new beneficiary for legacy access.

        Args:
            user_id: Unique identifier for the beneficiary.
            relationship: Relationship to the legacy owner.

        Returns:
            True if registered successfully, False if already exists.

        Future: Integrate with identity verification services.
        """
        if user_id in self.beneficiaries:
            return False

        access_level = self.RELATIONSHIP_ACCESS_LEVELS.get(relationship, AccessLevel.RESTRICTED_ACCESS)

        beneficiary = Beneficiary(
            user_id=user_id,
            relationship=relationship,
            access_level=access_level,
            registered_date=self._get_current_date(),
            is_active=False  # Will be activated after legacy conditions are met
        )

        self.beneficiaries[user_id] = beneficiary
        return True

    def verify_legacy_activation(self, user_status: str) -> bool:
        """
        Verify and activate legacy access based on user status.

        This method checks if the legacy activation conditions have been met.
        In a real implementation, this would integrate with legal verification,
        death certificates, or designated activation triggers.

        Args:
            user_status: Status indicator (e.g., 'deceased', 'activated').

        Returns:
            True if legacy is activated, False otherwise.

        Future integration:
        - Death certificate verification APIs
        - Legal executor confirmation systems
        - Time-delayed activation mechanisms
        - Multi-party approval processes
        """
        if user_status.lower() in ['deceased', 'activated', 'confirmed']:
            self.legacy_activated = True
            # Activate all registered beneficiaries
            for beneficiary in self.beneficiaries.values():
                beneficiary.is_active = True
            return True

        return False

    def authorize_memory_access(self, user_id: str, memory_metadata: MemoryMetadata) -> bool:
        """
        Authorize access to a specific memory based on user permissions and memory sensitivity.

        Evaluates multiple factors:
        - User's access level
        - User's relationship to the legacy owner
        - Memory sensitivity tags
        - Legacy activation status

        Args:
            user_id: The user requesting access.
            memory_metadata: Metadata about the memory being accessed.

        Returns:
            True if access is authorized, False otherwise.
        """
        # Check if legacy is activated
        if not self.legacy_activated:
            return False

        # Check if user is registered and active
        if user_id not in self.beneficiaries:
            return False

        beneficiary = self.beneficiaries[user_id]
        if not beneficiary.is_active:
            return False

        # Evaluate access based on sensitivity
        user_access_level = beneficiary.access_level

        # Check each sensitivity tag
        for tag in memory_metadata.sensitivity_tags:
            required_level = self.SENSITIVITY_REQUIREMENTS.get(tag, AccessLevel.FULL_ACCESS)
            if not self._has_required_access(user_access_level, required_level):
                return False

        # Additional checks for special cases
        if 'intimate' in memory_metadata.sensitivity_tags and beneficiary.relationship not in [Relationship.SPOUSE, Relationship.CHILD]:
            return False

        return True

    def get_access_level(self, user_id: str) -> Optional[AccessLevel]:
        """
        Get the current access level for a user.

        Args:
            user_id: The user ID to check.

        Returns:
            AccessLevel if user exists and is active, None otherwise.
        """
        if user_id in self.beneficiaries:
            beneficiary = self.beneficiaries[user_id]
            if beneficiary.is_active:
                return beneficiary.access_level
        return None

    def get_registered_beneficiaries(self) -> List[Dict[str, Any]]:
        """
        Get list of all registered beneficiaries (for admin purposes).

        Returns:
            List of beneficiary information dictionaries.
        """
        return [
            {
                'user_id': b.user_id,
                'relationship': b.relationship.value,
                'access_level': b.access_level.value,
                'registered_date': b.registered_date,
                'is_active': b.is_active
            }
            for b in self.beneficiaries.values()
        ]

    def update_beneficiary_access(self, user_id: str, new_access_level: AccessLevel) -> bool:
        """
        Update a beneficiary's access level (admin function).

        Args:
            user_id: The beneficiary to update.
            new_access_level: The new access level.

        Returns:
            True if updated successfully, False if user not found.
        """
        if user_id in self.beneficiaries:
            self.beneficiaries[user_id].access_level = new_access_level
            return True
        return False

    def _has_required_access(self, user_level: AccessLevel, required_level: AccessLevel) -> bool:
        """Check if user's access level meets the required level."""
        level_hierarchy = {
            AccessLevel.RESTRICTED_ACCESS: 1,
            AccessLevel.LIMITED_ACCESS: 2,
            AccessLevel.FULL_ACCESS: 3
        }

        return level_hierarchy.get(user_level, 0) >= level_hierarchy.get(required_level, 999)

    def _get_current_date(self) -> str:
        """Get current date as string (placeholder implementation)."""
        from datetime import datetime
        return datetime.now().isoformat()

    def filter_authorized_memories(self, user_id: str, memories_metadata: List[MemoryMetadata]) -> List[MemoryMetadata]:
        """
        Filter a list of memories to only include those the user is authorized to access.

        Args:
            user_id: The user requesting access.
            memories_metadata: List of memory metadata to filter.

        Returns:
            List of authorized memory metadata.
        """
        authorized = []
        for metadata in memories_metadata:
            if self.authorize_memory_access(user_id, metadata):
                authorized.append(metadata)
        return authorized