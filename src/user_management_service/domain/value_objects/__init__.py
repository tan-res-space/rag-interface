"""
Domain Value Objects

This module contains value objects that represent immutable concepts
in the user management domain.
"""

from .user_role import UserRole
from .user_status import UserStatus
from .speaker_bucket import SpeakerBucket

__all__ = [
    "UserRole",
    "UserStatus",
    "SpeakerBucket"
]