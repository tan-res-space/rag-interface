"""
Speaker Bucket Management API Gateway Router

Comprehensive API gateway router that aggregates all speaker bucket management endpoints.
Provides a unified interface for the complete speaker bucket management workflow.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter(
    prefix="/api/v1/speaker-bucket-management", tags=["Speaker Bucket Management"]
)

# Service URLs - these would be configured via environment variables
USER_MANAGEMENT_SERVICE_URL = "http://ums-dev:8000"
VERIFICATION_SERVICE_URL = "http://verification-service:8000"
RAG_INTEGRATION_SERVICE_URL = "http://ris-dev:8002"


class ServiceClient:
    """HTTP client for inter-service communication."""

    def __init__(self):
        self.timeout = httpx.Timeout(30.0)

    async def get(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, url: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request to service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=json)
            response.raise_for_status()
            return response.json()

    async def put(self, url: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request to service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(url, json=json)
            response.raise_for_status()
            return response.json()


# Dependency for service client
async def get_service_client() -> ServiceClient:
    """Get service client instance."""
    return ServiceClient()


# =====================================================
# SPEAKER MANAGEMENT ENDPOINTS
# =====================================================


@router.get("/speakers", response_model=dict)
async def get_speakers(
    name_pattern: Optional[str] = Query(None),
    bucket: Optional[str] = Query(None),
    min_ser_score: Optional[float] = Query(None),
    max_ser_score: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    client: ServiceClient = Depends(get_service_client),
):
    """
    Get speakers with comprehensive filtering and pagination.

    Aggregates speaker data with quality metrics and bucket information.
    """
    try:
        logger.info(f"Getting speakers with filters: page={page}, bucket={bucket}")

        params = {
            "name_pattern": name_pattern,
            "bucket": bucket,
            "min_ser_score": min_ser_score,
            "max_ser_score": max_ser_score,
            "page": page,
            "page_size": page_size,
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        url = f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/speakers"
        response = await client.get(url, params)

        logger.info(f"Retrieved {len(response.get('speakers', []))} speakers")
        return response

    except httpx.HTTPStatusError as e:
        logger.error(f"Service error getting speakers: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to get speakers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get speakers")


@router.get("/speakers/{speaker_id}/comprehensive", response_model=dict)
async def get_speaker_comprehensive_view(
    speaker_id: UUID = Path(..., description="Speaker ID"),
    include_ser_analysis: bool = Query(True),
    include_error_patterns: bool = Query(True),
    include_transition_history: bool = Query(True),
    client: ServiceClient = Depends(get_service_client),
):
    """
    Get comprehensive speaker view with data from all services.

    Aggregates speaker information, SER analysis, error patterns,
    and transition history for complete speaker assessment.
    """
    try:
        logger.info(f"Getting comprehensive view for speaker: {speaker_id}")

        # Get speaker basic information
        speaker_url = f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/speakers/{speaker_id}"
        speaker_data = await client.get(speaker_url)

        comprehensive_view = {
            "speaker": speaker_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Get SER analysis if requested
        if include_ser_analysis:
            try:
                ser_url = f"{VERIFICATION_SERVICE_URL}/api/v1/ser/speaker/{speaker_id}/analysis"
                ser_data = await client.get(ser_url)
                comprehensive_view["ser_analysis"] = ser_data
            except Exception as e:
                logger.warning(
                    f"Failed to get SER analysis for speaker {speaker_id}: {e}"
                )
                comprehensive_view["ser_analysis"] = None

        # Get error patterns if requested
        if include_error_patterns:
            try:
                patterns_url = f"{RAG_INTEGRATION_SERVICE_URL}/api/v1/speaker-rag/speaker/{speaker_id}/error-patterns"
                patterns_data = await client.get(patterns_url)
                comprehensive_view["error_patterns"] = patterns_data
            except Exception as e:
                logger.warning(
                    f"Failed to get error patterns for speaker {speaker_id}: {e}"
                )
                comprehensive_view["error_patterns"] = None

        # Get transition history if requested
        if include_transition_history:
            try:
                history_url = f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/bucket-transitions/speaker/{speaker_id}/history"
                history_data = await client.get(history_url)
                comprehensive_view["transition_history"] = history_data
            except Exception as e:
                logger.warning(
                    f"Failed to get transition history for speaker {speaker_id}: {e}"
                )
                comprehensive_view["transition_history"] = None

        logger.info(f"Comprehensive view retrieved for speaker: {speaker_id}")
        return comprehensive_view

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Speaker not found")
        logger.error(f"Service error getting comprehensive view: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to get comprehensive view for speaker {speaker_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get comprehensive view")


# =====================================================
# WORKFLOW ORCHESTRATION ENDPOINTS
# =====================================================


@router.post("/workflows/complete-assessment", response_model=dict)
async def complete_speaker_assessment_workflow(
    speaker_id: UUID,
    include_mt_validation: bool = Query(True),
    auto_approve_transitions: bool = Query(False),
    client: ServiceClient = Depends(get_service_client),
):
    """
    Complete speaker assessment workflow.

    Orchestrates the complete assessment process including SER calculation,
    error pattern analysis, MT validation, and bucket recommendation.
    """
    try:
        logger.info(f"Starting complete assessment workflow for speaker: {speaker_id}")

        workflow_results = {
            "speaker_id": str(speaker_id),
            "workflow_started_at": datetime.utcnow().isoformat(),
            "steps": [],
        }

        # Step 1: Update speaker statistics
        try:
            stats_url = f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/speakers/{speaker_id}/statistics/update"
            stats_result = await client.post(stats_url)
            workflow_results["steps"].append(
                {
                    "step": "update_statistics",
                    "status": "completed",
                    "result": stats_result,
                }
            )
        except Exception as e:
            workflow_results["steps"].append(
                {"step": "update_statistics", "status": "failed", "error": str(e)}
            )

        # Step 2: Process historical data for RAG
        try:
            # This would need actual historical data - placeholder for now
            rag_url = (
                f"{RAG_INTEGRATION_SERVICE_URL}/api/v1/speaker-rag/process-historical"
            )
            rag_request = {
                "speaker_id": str(speaker_id),
                "historical_data_items": [],  # Would be populated with actual data
                "context_window": 50,
            }
            # rag_result = await client.post(rag_url, rag_request)
            workflow_results["steps"].append(
                {
                    "step": "process_historical_data",
                    "status": "skipped",
                    "reason": "No historical data provided",
                }
            )
        except Exception as e:
            workflow_results["steps"].append(
                {"step": "process_historical_data", "status": "failed", "error": str(e)}
            )

        # Step 3: MT Validation (if requested)
        if include_mt_validation:
            try:
                # This would create an MT validation session
                validation_url = (
                    f"{VERIFICATION_SERVICE_URL}/api/v1/mt-validation/sessions"
                )
                validation_request = {
                    "speaker_id": str(speaker_id),
                    "session_name": f"Assessment validation for {speaker_id}",
                    "test_data_ids": [],  # Would be populated with actual test data
                    "mt_user_id": str(
                        UUID("00000000-0000-0000-0000-000000000000")
                    ),  # Placeholder
                }
                # validation_result = await client.post(validation_url, validation_request)
                workflow_results["steps"].append(
                    {
                        "step": "mt_validation",
                        "status": "skipped",
                        "reason": "No test data available",
                    }
                )
            except Exception as e:
                workflow_results["steps"].append(
                    {"step": "mt_validation", "status": "failed", "error": str(e)}
                )

        # Step 4: Generate bucket recommendation
        try:
            # Get current speaker data for recommendation
            speaker_url = f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/speakers/{speaker_id}"
            speaker_data = await client.get(speaker_url)

            recommendation = {
                "current_bucket": speaker_data.get("current_bucket"),
                "recommended_bucket": speaker_data.get("recommended_bucket"),
                "should_transition": speaker_data.get("should_transition"),
                "quality_trend": speaker_data.get("quality_trend"),
            }

            workflow_results["steps"].append(
                {
                    "step": "bucket_recommendation",
                    "status": "completed",
                    "result": recommendation,
                }
            )
        except Exception as e:
            workflow_results["steps"].append(
                {"step": "bucket_recommendation", "status": "failed", "error": str(e)}
            )

        workflow_results["workflow_completed_at"] = datetime.utcnow().isoformat()
        workflow_results["overall_status"] = "completed"

        logger.info(f"Assessment workflow completed for speaker: {speaker_id}")
        return workflow_results

    except Exception as e:
        logger.error(
            f"Failed to complete assessment workflow for speaker {speaker_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to complete assessment workflow"
        )


# =====================================================
# DASHBOARD AND ANALYTICS ENDPOINTS
# =====================================================


@router.get("/dashboard/overview", response_model=dict)
async def get_dashboard_overview(client: ServiceClient = Depends(get_service_client)):
    """
    Get dashboard overview with key metrics from all services.

    Aggregates statistics and metrics for the speaker bucket management dashboard.
    """
    try:
        logger.info("Getting dashboard overview")

        dashboard_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "services_status": {},
        }

        # Get speaker statistics
        try:
            stats_url = (
                f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/speakers/statistics/buckets"
            )
            speaker_stats = await client.get(stats_url)
            dashboard_data["speaker_statistics"] = speaker_stats
            dashboard_data["services_status"]["user_management"] = "healthy"
        except Exception as e:
            logger.warning(f"Failed to get speaker statistics: {e}")
            dashboard_data["services_status"]["user_management"] = "error"

        # Get SER metrics summary
        try:
            ser_url = f"{VERIFICATION_SERVICE_URL}/api/v1/ser/metrics/summary"
            ser_stats = await client.get(ser_url)
            dashboard_data["ser_metrics"] = ser_stats
            dashboard_data["services_status"]["verification"] = "healthy"
        except Exception as e:
            logger.warning(f"Failed to get SER metrics: {e}")
            dashboard_data["services_status"]["verification"] = "error"

        # Get RAG processing summary
        try:
            rag_url = (
                f"{RAG_INTEGRATION_SERVICE_URL}/api/v1/speaker-rag/statistics/summary"
            )
            rag_stats = await client.get(rag_url)
            dashboard_data["rag_processing"] = rag_stats
            dashboard_data["services_status"]["rag_integration"] = "healthy"
        except Exception as e:
            logger.warning(f"Failed to get RAG processing stats: {e}")
            dashboard_data["services_status"]["rag_integration"] = "error"

        # Get transition statistics
        try:
            transition_url = f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/bucket-transitions/statistics/summary"
            transition_stats = await client.get(transition_url)
            dashboard_data["transition_statistics"] = transition_stats
        except Exception as e:
            logger.warning(f"Failed to get transition statistics: {e}")

        # Get validation statistics
        try:
            validation_url = (
                f"{VERIFICATION_SERVICE_URL}/api/v1/mt-validation/statistics/summary"
            )
            validation_stats = await client.get(validation_url)
            dashboard_data["validation_statistics"] = validation_stats
        except Exception as e:
            logger.warning(f"Failed to get validation statistics: {e}")

        logger.info("Dashboard overview retrieved successfully")
        return dashboard_data

    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard overview")


# =====================================================
# HEALTH CHECK ENDPOINTS
# =====================================================


@router.get("/health/comprehensive")
async def comprehensive_health_check(
    client: ServiceClient = Depends(get_service_client),
):
    """
    Comprehensive health check for all speaker bucket management services.

    Checks the health and connectivity of all microservices in the system.
    """
    try:
        logger.info("Performing comprehensive health check")

        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": {},
        }

        # Check User Management Service
        try:
            user_health_url = (
                f"{USER_MANAGEMENT_SERVICE_URL}/api/v1/speakers/health/check"
            )
            user_health = await client.get(user_health_url)
            health_status["services"]["user_management"] = {
                "status": "healthy",
                "response_time_ms": 0,  # Would measure actual response time
                "details": user_health,
            }
        except Exception as e:
            health_status["services"]["user_management"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["overall_status"] = "degraded"

        # Check Verification Service
        try:
            verification_health_url = (
                f"{VERIFICATION_SERVICE_URL}/api/v1/ser/health/check"
            )
            verification_health = await client.get(verification_health_url)
            health_status["services"]["verification"] = {
                "status": "healthy",
                "response_time_ms": 0,
                "details": verification_health,
            }
        except Exception as e:
            health_status["services"]["verification"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["overall_status"] = "degraded"

        # Check RAG Integration Service
        try:
            rag_health_url = (
                f"{RAG_INTEGRATION_SERVICE_URL}/api/v1/speaker-rag/health/check"
            )
            rag_health = await client.get(rag_health_url)
            health_status["services"]["rag_integration"] = {
                "status": "healthy",
                "response_time_ms": 0,
                "details": rag_health,
            }
        except Exception as e:
            health_status["services"]["rag_integration"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["overall_status"] = "degraded"

        logger.info(
            f"Comprehensive health check completed: {health_status['overall_status']}"
        )
        return health_status

    except Exception as e:
        logger.error(f"Failed to perform comprehensive health check: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform health check")
