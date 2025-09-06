"""
Test data factories for Error Reporting Service.

This module provides factory classes for generating test data following
the Factory Boy pattern for consistent and maintainable test data creation.
"""

import uuid
from datetime import datetime
from typing import List

import factory
from faker import Faker

from src.error_reporting_service.application.dto.requests import (
    SubmitErrorReportRequest,
)
from src.error_reporting_service.domain.entities.error_report import (
    ErrorReport,
    ErrorStatus,
    SeverityLevel,
)
from src.error_reporting_service.domain.events.domain_events import ErrorReportedEvent

fake = Faker()


class ErrorReportFactory(factory.Factory):
    """Factory for creating ErrorReport domain entities."""

    class Meta:
        model = ErrorReport

    error_id = factory.LazyFunction(uuid.uuid4)
    job_id = factory.LazyFunction(uuid.uuid4)
    speaker_id = factory.LazyFunction(uuid.uuid4)
    reported_by = factory.LazyFunction(uuid.uuid4)

    # Medical text examples for realistic testing
    original_text = factory.Iterator(
        [
            "The patient has diabetis",
            "Patient shows signs of hypertention",
            "Diagnosed with pnemonia",
            "History of cardiak issues",
            "Suffers from arthritus",
            "Patient has alergies to penicillin",
            "Experiencing shortnes of breath",
            "Blood presure is elevated",
        ]
    )

    corrected_text = factory.Iterator(
        [
            "The patient has diabetes",
            "Patient shows signs of hypertension",
            "Diagnosed with pneumonia",
            "History of cardiac issues",
            "Suffers from arthritis",
            "Patient has allergies to penicillin",
            "Experiencing shortness of breath",
            "Blood pressure is elevated",
        ]
    )

    error_categories = factory.LazyFunction(
        lambda: fake.random_elements(
            elements=["medical_terminology", "spelling", "grammar", "pronunciation"],
            length=fake.random_int(min=1, max=3),
            unique=True,
        )
    )

    severity_level = factory.Iterator(
        [
            SeverityLevel.LOW,
            SeverityLevel.MEDIUM,
            SeverityLevel.HIGH,
            SeverityLevel.CRITICAL,
        ]
    )

    start_position = factory.LazyAttribute(
        lambda obj: fake.random_int(min=0, max=max(0, len(obj.original_text) - 10))
    )
    end_position = factory.LazyAttribute(
        lambda obj: min(
            obj.start_position + fake.random_int(min=1, max=10), len(obj.original_text)
        )
    )

    context_notes = factory.LazyFunction(
        lambda: (
            fake.sentence(nb_words=10)
            if fake.boolean(chance_of_getting_true=70)
            else None
        )
    )

    error_timestamp = factory.LazyFunction(
        lambda: fake.date_time_between(start_date="-30d", end_date="now")
    )
    reported_at = factory.LazyFunction(datetime.utcnow)

    status = factory.Iterator(
        [ErrorStatus.PENDING, ErrorStatus.PROCESSED, ErrorStatus.ARCHIVED]
    )

    metadata = factory.LazyFunction(
        lambda: {
            "audio_quality": fake.random_element(
                elements=["poor", "fair", "good", "excellent"]
            ),
            "background_noise": fake.boolean(),
            "confidence_score": round(fake.random.uniform(0.1, 1.0), 2),
            "speaker_accent": fake.random_element(
                elements=["american", "british", "australian", "canadian"]
            ),
            "technical_issues": (
                fake.random_elements(
                    elements=["static", "echo", "volume_low", "distortion"],
                    length=fake.random_int(min=0, max=2),
                    unique=True,
                )
                if fake.boolean(chance_of_getting_true=30)
                else []
            ),
        }
    )


class SubmitErrorReportRequestFactory(factory.Factory):
    """Factory for creating SubmitErrorReportRequest DTOs."""

    class Meta:
        model = SubmitErrorReportRequest

    job_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    speaker_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    reported_by = factory.LazyFunction(lambda: str(uuid.uuid4()))

    original_text = factory.Iterator(
        [
            "The patient has diabetis",
            "Patient shows signs of hypertention",
            "Diagnosed with pnemonia",
        ]
    )

    corrected_text = factory.Iterator(
        [
            "The patient has diabetes",
            "Patient shows signs of hypertension",
            "Diagnosed with pneumonia",
        ]
    )

    error_categories = factory.LazyFunction(
        lambda: fake.random_elements(
            elements=["medical_terminology", "spelling", "grammar"],
            length=fake.random_int(min=1, max=2),
            unique=True,
        )
    )

    severity_level = factory.Iterator(["low", "medium", "high", "critical"])

    start_position = factory.LazyFunction(lambda: fake.random_int(min=0, max=30))
    end_position = factory.LazyAttribute(
        lambda obj: obj.start_position + fake.random_int(min=1, max=15)
    )

    context_notes = factory.LazyFunction(
        lambda: fake.sentence() if fake.boolean(chance_of_getting_true=60) else None
    )

    metadata = factory.LazyFunction(
        lambda: {
            "audio_quality": fake.random_element(
                elements=["poor", "fair", "good", "excellent"]
            ),
            "confidence_score": round(fake.random.uniform(0.5, 1.0), 2),
        }
    )


class ErrorReportedEventFactory(factory.Factory):
    """Factory for creating ErrorReportedEvent domain events."""

    class Meta:
        model = ErrorReportedEvent

    event_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    correlation_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    timestamp = factory.LazyFunction(datetime.utcnow)

    error_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    speaker_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    job_id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    original_text = factory.Iterator(
        ["The patient has diabetis", "Patient shows signs of hypertention"]
    )

    corrected_text = factory.Iterator(
        ["The patient has diabetes", "Patient shows signs of hypertension"]
    )

    categories = factory.LazyFunction(
        lambda: fake.random_elements(
            elements=["medical_terminology", "spelling", "grammar"],
            length=fake.random_int(min=1, max=2),
            unique=True,
        )
    )

    severity = factory.Iterator(["low", "medium", "high", "critical"])
    reported_by = factory.LazyFunction(lambda: str(uuid.uuid4()))

    metadata = factory.LazyFunction(
        lambda: {
            "audio_quality": fake.random_element(elements=["good", "excellent"]),
            "confidence_score": round(fake.random.uniform(0.7, 1.0), 2),
        }
    )


# Specialized Factories for Edge Cases
class CriticalErrorReportFactory(ErrorReportFactory):
    """Factory for creating critical severity error reports."""

    severity_level = SeverityLevel.CRITICAL
    error_categories = ["medical_terminology", "critical_error"]


class LongTextErrorReportFactory(ErrorReportFactory):
    """Factory for creating error reports with long text content."""

    original_text = factory.LazyFunction(lambda: fake.text(max_nb_chars=5000))
    corrected_text = factory.LazyFunction(lambda: fake.text(max_nb_chars=5000))


class MinimalErrorReportFactory(ErrorReportFactory):
    """Factory for creating error reports with minimal required fields."""

    context_notes = None
    metadata = factory.LazyFunction(lambda: {})


class InvalidErrorReportDataFactory(factory.Factory):
    """Factory for creating invalid error report data for testing validation."""

    class Meta:
        model = dict

    job_id = factory.LazyFunction(lambda: "invalid-uuid")
    speaker_id = ""
    original_text = ""
    corrected_text = ""
    error_categories = []
    severity_level = "invalid_severity"
    start_position = -1
    end_position = 0
    context_notes = factory.LazyFunction(lambda: "x" * 1001)  # Exceeds max length
    metadata = {}


# Utility Functions for Test Data
def create_error_reports_batch(count: int = 10) -> List[ErrorReport]:
    """Create a batch of error reports for bulk testing."""
    return ErrorReportFactory.create_batch(count)


def create_medical_error_report() -> ErrorReport:
    """Create an error report with medical terminology focus."""
    return ErrorReportFactory.create(
        original_text="Patient diagnosed with pnemonia and hypertention",
        corrected_text="Patient diagnosed with pneumonia and hypertension",
        error_categories=["medical_terminology", "spelling"],
        severity_level=SeverityLevel.HIGH,
        start_position=20,
        end_position=28,
        context_notes="Medical terminology correction needed",
    )


def create_edge_case_error_report() -> ErrorReport:
    """Create an error report for edge case testing."""
    return ErrorReportFactory.create(
        original_text="a",
        corrected_text="A",
        error_categories=["capitalization"],
        severity_level=SeverityLevel.LOW,
        start_position=0,
        end_position=1,
        context_notes=None,
        metadata={},
    )
