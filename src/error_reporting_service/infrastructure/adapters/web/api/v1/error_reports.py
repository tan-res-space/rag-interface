"""
Error Reports API Router

FastAPI router for error report endpoints.
Handles HTTP requests and responses for error reporting operations.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from error_reporting_service.application.dto.requests import (
    GetErrorReportRequest,
    SearchErrorsRequest,
    SubmitErrorReportRequest,
)
from error_reporting_service.application.dto.responses import (
    GetErrorReportResponse,
    SearchErrorsResponse,
    SubmitErrorReportResponse,
)
from error_reporting_service.application.use_cases.submit_error_report import (
    SubmitErrorReportUseCase,
)
from error_reporting_service.infrastructure.adapters.database.postgresql.adapter import (
    PostgreSQLAdapter,
)
from error_reporting_service.infrastructure.adapters.events.mock_event_publisher import (
    MockEventPublisher,
)

# Import bucket progression components
from error_reporting_service.infrastructure.adapters.database.in_memory.speaker_profile_adapter import InMemorySpeakerProfileAdapter
from error_reporting_service.application.use_cases.evaluate_bucket_progression_use_case import (
    EvaluateBucketProgressionUseCase,
    EvaluateBucketProgressionRequest
)
from error_reporting_service.domain.services.bucket_progression_service import BucketProgressionService
from error_reporting_service.domain.services.validation_service import (
    ErrorValidationService,
)
from error_reporting_service.domain.services.categorization_service import (
    ErrorCategorizationService,
)

# Create router
router = APIRouter()

# Simple in-memory storage for testing
_error_reports_storage = [
    {
        "id": "sample-report-1",
        "job_id": "job-123",
        "speaker_id": "speaker-456",
        "client_id": "client-789",
        "bucket_type": "medium_touch",
        "reported_by": "user-123",
        "original_text": "The patient has a history of hypertension and diabetes.",
        "corrected_text": "The patient has a history of high blood pressure and diabetes.",
        "error_categories": ["medical_terminology"],
        "severity_level": "medium",
        "start_position": 29,
        "end_position": 41,
        "context_notes": "Medical terminology should be simplified for patient understanding",
        "error_timestamp": "2024-12-19T10:30:00Z",
        "status": "pending",
        "created_at": "2024-12-19T10:30:00Z",
        "updated_at": "2024-12-19T10:30:00Z",
        "metadata": {
            "audio_quality": "good",
            "background_noise": "low",
            "speaker_clarity": "clear"
        }
    },
    {
        "id": "sample-report-2",
        "job_id": "job-456",
        "speaker_id": "speaker-789",
        "client_id": "client-123",
        "bucket_type": "high_touch",
        "reported_by": "user-456",
        "original_text": "The medication dosage is 10mg twice daily.",
        "corrected_text": "The medication dosage is 10 milligrams twice daily.",
        "error_categories": ["abbreviation"],
        "severity_level": "low",
        "start_position": 25,
        "end_position": 29,
        "context_notes": "Abbreviations should be spelled out for clarity",
        "error_timestamp": "2024-12-19T11:15:00Z",
        "status": "processed",
        "created_at": "2024-12-19T11:15:00Z",
        "updated_at": "2024-12-19T11:45:00Z",
        "metadata": {
            "audio_quality": "fair",
            "background_noise": "medium",
            "speaker_clarity": "somewhat_clear"
        }
    },
    {
        "id": "sample-report-3",
        "job_id": "job-789",
        "speaker_id": "speaker-123",
        "client_id": "client-456",
        "bucket_type": "low_touch",
        "reported_by": "user-789",
        "original_text": "Patient exhibits symptoms of acute myocardial infarction.",
        "corrected_text": "Patient exhibits symptoms of acute heart attack.",
        "error_categories": ["medical_terminology"],
        "severity_level": "high",
        "start_position": 32,
        "end_position": 56,
        "context_notes": "Complex medical terms should be simplified",
        "error_timestamp": "2024-12-19T12:00:00Z",
        "status": "archived",
        "created_at": "2024-12-19T12:00:00Z",
        "updated_at": "2024-12-19T12:30:00Z",
        "metadata": {
            "audio_quality": "excellent",
            "background_noise": "none",
            "speaker_clarity": "clear"
        }
    },
    {
        "id": "sample-report-4",
        "job_id": "job-101",
        "speaker_id": "speaker-202",
        "client_id": "client-303",
        "bucket_type": "no_touch",
        "reported_by": "user-404",
        "original_text": "The patient's vital signs are stable.",
        "corrected_text": "The patient's vital signs are stable.",
        "error_categories": ["pronunciation"],
        "severity_level": "low",
        "start_position": 0,
        "end_position": 37,
        "context_notes": "Minor pronunciation issue, no text change needed",
        "error_timestamp": "2024-12-19T13:30:00Z",
        "status": "rejected",
        "created_at": "2024-12-19T13:30:00Z",
        "updated_at": "2024-12-19T14:00:00Z",
        "metadata": {
            "audio_quality": "excellent",
            "background_noise": "none",
            "speaker_clarity": "clear"
        }
    }
]

# Initialize bucket progression components
speaker_profile_adapter = InMemorySpeakerProfileAdapter()
progression_service = BucketProgressionService()
bucket_evaluation_use_case = EvaluateBucketProgressionUseCase(
    speaker_profile_repository=speaker_profile_adapter,
    error_reports_repository=None,  # Will be integrated later
    progression_service=progression_service
)

# Placeholder dependency for authentication
async def get_current_user():
    """Get current authenticated user (placeholder)"""
    return {"user_id": str(uuid.uuid4()), "username": "test_user"}

# Helper function to generate error report ID
def generate_error_id():
    """Generate a unique error report ID"""
    return str(uuid.uuid4())


@router.post("/errors", status_code=status.HTTP_201_CREATED)
async def submit_error_report(
    request_data: dict,  # Accept raw dict to handle frontend format
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Submit a new error report.

    Args:
        request_data: Error report submission data (raw dict from frontend)
        current_user: Current authenticated user

    Returns:
        Response with error report ID and status
    """
    try:
        # Generate error ID
        error_id = generate_error_id()

        # Create error report record
        error_report = {
            "id": error_id,
            "job_id": request_data.get("job_id"),
            "speaker_id": request_data.get("speaker_id"),
            "client_id": request_data.get("metadata", {}).get("client_id", "unknown"),
            "bucket_type": request_data.get("bucket_type", "medium_touch"),
            "reported_by": current_user["user_id"],
            "original_text": request_data.get("original_text"),
            "corrected_text": request_data.get("corrected_text"),
            "error_categories": request_data.get("error_categories", []),
            "severity_level": request_data.get("severity_level", "medium"),
            "start_position": request_data.get("start_position", 0),
            "end_position": request_data.get("end_position", 0),
            "context_notes": request_data.get("context_notes"),
            "error_timestamp": "2024-12-19T10:30:00Z",
            "status": "pending",
            "created_at": "2024-12-19T10:30:00Z",
            "updated_at": "2024-12-19T10:30:00Z",
            "metadata": request_data.get("metadata", {})
        }

        # Store in memory
        _error_reports_storage.append(error_report)

        # Trigger bucket progression evaluation for the speaker
        try:
            speaker_id = request_data.get("speaker_id")
            if speaker_id:
                eval_request = EvaluateBucketProgressionRequest(
                    speaker_id=speaker_id,
                    trigger_event="new_report_submitted",
                    force_evaluation=False
                )

                # Execute bucket evaluation asynchronously (don't block response)
                eval_response = await bucket_evaluation_use_case.execute(eval_request)

                # Add bucket progression info to response if bucket changed
                response_data = {
                    "errorId": error_id,
                    "status": "success",
                    "message": "Error report submitted successfully"
                }

                if eval_response.bucket_changed:
                    response_data["bucket_progression"] = {
                        "bucket_changed": True,
                        "old_bucket": eval_response.old_bucket.value,
                        "new_bucket": eval_response.new_bucket.value,
                        "change_reason": eval_response.change_reason
                    }

                return response_data

        except Exception as e:
            # Log bucket evaluation error but don't fail the submission
            print(f"Bucket evaluation error: {str(e)}")

        # Return standard response if bucket evaluation fails
        return {
            "errorId": error_id,
            "status": "success",
            "message": "Error report submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/errors/{error_id}")
async def get_error_report(
    error_id: str, current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get an error report by ID.

    Args:
        error_id: Error report ID
        current_user: Current authenticated user

    Returns:
        Error report details
    """
    # Placeholder implementation
    try:
        uuid.UUID(error_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid error ID format")

    # Simulate not found for demonstration
    if error_id == "00000000-0000-0000-0000-000000000000":
        raise HTTPException(status_code=404, detail="Error report not found")

    # Find report in storage
    for report in _error_reports_storage:
        if report["id"] == error_id:
            return report

    # If not found in storage, return mock data
    return {
        "id": error_id,
        "job_id": str(uuid.uuid4()),
        "speaker_id": "speaker-456",
        "client_id": "client-789",
        "bucket_type": "medium_touch",
        "reported_by": str(uuid.uuid4()),
        "original_text": "The patient has a history of hypertension and diabetes. The doctor prescribed medication for the condition.",
        "corrected_text": "The patient has a history of high blood pressure and diabetes. The doctor prescribed medication for the condition.",
        "error_categories": ["medical_terminology"],
        "severity_level": "medium",
        "start_position": 29,
        "end_position": 41,
        "context_notes": "Medical terminology correction - hypertension should be high blood pressure for patient understanding",
        "error_timestamp": "2024-12-19T10:30:00Z",
        "status": "pending",
        "created_at": "2024-12-19T10:30:00Z",
        "updated_at": "2024-12-19T10:30:00Z",
        "metadata": {
            "audio_quality": "good",
            "background_noise": "low",
            "speaker_clarity": "clear",
            "urgency_level": "medium"
        }
    }


@router.put("/errors/{error_id}")
async def update_error_report(
    error_id: str, update_data: dict, current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Update an error report.

    Args:
        error_id: Error report ID
        update_data: Update data
        current_user: Current authenticated user

    Returns:
        Updated error report
    """
    # Placeholder implementation
    try:
        uuid.UUID(error_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid error ID format")

    # Simulate not found for demonstration
    if error_id == "00000000-0000-0000-0000-000000000000":
        raise HTTPException(status_code=404, detail="Error report not found")

    return {
        "id": error_id,
        "original_text": "Sample original text",
        "corrected_text": "Sample corrected text",
        "severity_level": update_data.get("severity_level", "medium"),
        "error_categories": ["grammar"],
        "status": update_data.get("status", "pending"),
        "context_notes": update_data.get("context_notes", ""),
        "metadata": update_data.get("metadata", {}),
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }


@router.delete("/errors/{error_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_error_report(
    error_id: str, current_user: dict = Depends(get_current_user)
):
    """
    Delete an error report.

    Args:
        error_id: Error report ID
        current_user: Current authenticated user
    """
    # Placeholder implementation
    try:
        uuid.UUID(error_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid error ID format")

    # Simulate not found for demonstration
    if error_id == "00000000-0000-0000-0000-000000000000":
        raise HTTPException(status_code=404, detail="Error report not found")

    # Return 204 No Content (no response body)
    return


@router.get("/errors")
async def search_errors(
    page: int = 1,
    size: int = 10,
    severity_level: Optional[str] = None,
    categories: Optional[str] = None,
    job_id: Optional[str] = None,
    speaker_id: Optional[str] = None,
    client_id: Optional[str] = None,
    bucket_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Search error reports.

    Args:
        page: Page number
        size: Page size
        severity_level: Filter by severity level
        categories: Filter by categories
        job_id: Filter by job ID
        speaker_id: Filter by speaker ID
        status: Filter by status
        current_user: Current authenticated user

    Returns:
        Search results with pagination
    """
    # Validate pagination parameters
    if page <= 0 or size <= 0:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")

    # Filter stored reports
    filtered_reports = _error_reports_storage.copy()

    # Apply filters
    if speaker_id:
        filtered_reports = [r for r in filtered_reports if r.get("speaker_id") == speaker_id]
    if job_id:
        filtered_reports = [r for r in filtered_reports if r.get("job_id") == job_id]
    if client_id:
        filtered_reports = [r for r in filtered_reports if r.get("client_id") == client_id]
    if bucket_type:
        filtered_reports = [r for r in filtered_reports if r.get("bucket_type") == bucket_type]
    if severity_level:
        filtered_reports = [r for r in filtered_reports if r.get("severity_level") == severity_level]
    if status:
        filtered_reports = [r for r in filtered_reports if r.get("status") == status]
    if search:
        search_lower = search.lower()
        filtered_reports = [r for r in filtered_reports
                          if search_lower in r.get("original_text", "").lower()
                          or search_lower in r.get("corrected_text", "").lower()
                          or search_lower in r.get("id", "").lower()]

    # Apply pagination
    total = len(filtered_reports)
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    items = filtered_reports[start_idx:end_idx]

    pages = (total + size - 1) // size if size > 0 else 0

    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}
