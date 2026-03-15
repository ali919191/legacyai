"""Security services package for Legacy AI.

Contains access control and security services for protecting legacy information.
"""

from .legacy_access_service import (
    LegacyAccessService,
    AccessLevel,
    Relationship,
    Beneficiary,
    MemoryMetadata
)

__all__ = [
    'LegacyAccessService',
    'AccessLevel',
    'Relationship',
    'Beneficiary',
    'MemoryMetadata'
]