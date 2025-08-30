"""
Domain Value Objects

This module contains value objects that represent immutable concepts
in the user management domain.
"""

from .speaker_bucket import SpeakerBucket
from .user_role import UserRole
from .user_status import UserStatus

__all__ = ["UserRole", "UserStatus", "SpeakerBucket"]
