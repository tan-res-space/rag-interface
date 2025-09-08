import datetime

import pytest

from src.error_reporting_service.domain.services.bucket_progression_service import (
    BucketProgressionService,
    BucketProgressionCriteria,
)
from src.error_reporting_service.domain.entities.speaker_profile import SpeakerProfile
from src.shared.domain.value_objects import BucketType


def _iso(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat()


def _make_reports(
    count: int,
    *,
    base_created_at: datetime.datetime,
    original_len: int,
    corrected_len: int,
    include_notes: bool = True,
) -> list[dict]:
    reports: list[dict] = []
    for i in range(count):
        created = base_created_at - datetime.timedelta(days=i)
        reports.append(
            {
                "original_text": "x" * original_len,
                "corrected_text": "x" * corrected_len,
                "error_categories": ["grammar"],
                "severity_level": "medium",
                "context_notes": "note" if include_notes else "",
                "created_at": _iso(created),
            }
        )
    return reports


def _make_profile(bucket: BucketType, *, days_in_bucket: int = 30) -> SpeakerProfile:
    now = datetime.datetime.utcnow()
    return SpeakerProfile(
        speaker_id="test-speaker",
        current_bucket=bucket,
        created_at=now,
        updated_at=now,
        days_in_current_bucket=days_in_bucket,
    )


def test_promotion_recommended_when_metrics_meet_next_bucket_thresholds():
    criteria = BucketProgressionCriteria()
    service = BucketProgressionService(criteria)

    # Start from MEDIUM_TOUCH; promote to LOW_TOUCH when metrics are strong
    profile = _make_profile(BucketType.MEDIUM_TOUCH)

    # Craft reports with very low error rate and good accuracy
    # error_rate ~= abs(ol - cl)/max -> here 0 (same length)
    base_time = datetime.datetime.utcnow()
    reports = _make_reports(
        12,
        base_created_at=base_time,
        original_len=100,
        corrected_len=100,
        include_notes=True,
    )

    rec = service.evaluate_speaker_progression(profile, reports)

    assert rec.recommended_bucket in (BucketType.LOW_TOUCH, BucketType.MEDIUM_TOUCH)
    # Expect promotion with sufficiently good metrics
    assert rec.recommended_bucket == BucketType.LOW_TOUCH
    assert rec.confidence_score >= criteria.promotion_confidence_threshold


def test_demotion_recommended_when_metrics_below_current_thresholds():
    criteria = BucketProgressionCriteria()
    service = BucketProgressionService(criteria)

    # Start from LOW_TOUCH; demote to MEDIUM_TOUCH with poor metrics
    profile = _make_profile(BucketType.LOW_TOUCH)

    # Craft reports with high error rate and poor accuracy
    # error_rate high: big length difference
    base_time = datetime.datetime.utcnow()
    reports = _make_reports(
        10,
        base_created_at=base_time,
        original_len=100,
        corrected_len=10,
        include_notes=False,
    )

    rec = service.evaluate_speaker_progression(profile, reports)

    assert rec.recommended_bucket in (BucketType.MEDIUM_TOUCH, BucketType.LOW_TOUCH)
    assert rec.recommended_bucket == BucketType.MEDIUM_TOUCH
    assert rec.confidence_score >= criteria.demotion_confidence_threshold


def test_error_rate_threshold_mapping_matches_criteria():
    criteria = BucketProgressionCriteria(
        high_touch_max_error_rate=0.15,
        medium_touch_max_error_rate=0.10,
        low_touch_max_error_rate=0.05,
        no_touch_max_error_rate=0.02,
    )
    service = BucketProgressionService(criteria)

    assert service._get_error_rate_threshold(BucketType.HIGH_TOUCH) == 0.15
    assert service._get_error_rate_threshold(BucketType.MEDIUM_TOUCH) == 0.10
    assert service._get_error_rate_threshold(BucketType.LOW_TOUCH) == 0.05
    assert service._get_error_rate_threshold(BucketType.NO_TOUCH) == 0.02

