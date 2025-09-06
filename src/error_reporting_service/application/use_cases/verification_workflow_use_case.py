"""
Verification Workflow Use Case

Handles the verification of error corrections through InstaNote Database integration.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from error_reporting_service.domain.entities.verification_job import (
    VerificationJob,
    VerificationResult,
    CorrectionApplied,
)
from error_reporting_service.domain.ports.verification_job_repository import (
    VerificationJobRepository,
)
from error_reporting_service.application.dto.requests import (
    PullVerificationJobsRequest,
    VerifyCorrectionRequest,
)
from error_reporting_service.application.dto.responses import (
    VerificationJobResponse,
)


class VerificationWorkflowUseCase:
    """Use case for managing verification workflow"""

    def __init__(
        self,
        verification_job_repository: VerificationJobRepository,
        instanote_service,  # External service for InstaNote Database
        rag_service,  # RAG system service
    ):
        self._verification_job_repository = verification_job_repository
        self._instanote_service = instanote_service
        self._rag_service = rag_service

    async def pull_verification_jobs(
        self, request: PullVerificationJobsRequest
    ) -> List[VerificationJobResponse]:
        """Pull jobs from InstaNote Database for verification"""
        
        # Parse date range
        start_date = datetime.fromisoformat(request.date_range["start_date"])
        end_date = datetime.fromisoformat(request.date_range["end_date"])
        
        # Pull jobs from InstaNote Database
        instanote_jobs = await self._instanote_service.get_jobs_for_speaker(
            speaker_id=request.speaker_id,
            start_date=start_date,
            end_date=end_date,
            error_types=request.error_types,
            limit=request.max_jobs
        )
        
        verification_jobs = []
        
        for job in instanote_jobs:
            # Create verification job entity
            verification_job = VerificationJob(
                verification_id=uuid.uuid4(),
                job_id=job["job_id"],
                speaker_id=uuid.UUID(request.speaker_id),
                original_draft=job["original_draft"],
                retrieval_timestamp=datetime.utcnow(),
                job_metadata=job.get("metadata", {}),
                created_at=datetime.utcnow(),
            )
            
            # Save verification job
            saved_job = await self._verification_job_repository.save_verification_job(
                verification_job
            )
            
            verification_jobs.append(
                VerificationJobResponse(
                    verification_id=str(saved_job.verification_id),
                    job_id=saved_job.job_id,
                    speaker_id=str(saved_job.speaker_id),
                    verification_status=saved_job.verification_status.value,
                    verification_result=saved_job.verification_result.value if saved_job.verification_result else None,
                    corrections_count=saved_job.get_correction_count(),
                    average_confidence=saved_job.calculate_average_confidence(),
                    needs_manual_review=saved_job.needs_manual_review(),
                    verified_by=str(saved_job.verified_by) if saved_job.verified_by else None,
                    verified_at=saved_job.verified_at,
                    has_qa_comments=bool(saved_job.qa_comments),
                )
            )
        
        return verification_jobs

    async def apply_rag_corrections(self, verification_id: str) -> VerificationJobResponse:
        """Apply RAG system corrections to a verification job"""
        
        # Get verification job
        verification_job = await self._verification_job_repository.get_by_id(
            uuid.UUID(verification_id)
        )
        
        if not verification_job:
            raise ValueError(f"Verification job {verification_id} not found")
        
        # Apply RAG corrections
        rag_result = await self._rag_service.apply_corrections(
            original_text=verification_job.original_draft,
            speaker_id=str(verification_job.speaker_id),
            job_metadata=verification_job.job_metadata
        )
        
        # Create correction objects
        corrections = [
            CorrectionApplied(
                correction_type=correction["type"],
                original_text=correction["original"],
                corrected_text=correction["corrected"],
                confidence=correction["confidence"],
                position_start=correction.get("position_start"),
                position_end=correction.get("position_end"),
            )
            for correction in rag_result["corrections"]
        ]
        
        # Update verification job with corrections
        updated_job = verification_job.with_rag_corrections(
            corrected_draft=rag_result["corrected_draft"],
            corrections=corrections
        )
        
        # Save updated job
        saved_job = await self._verification_job_repository.save_verification_job(
            updated_job
        )
        
        return VerificationJobResponse(
            verification_id=str(saved_job.verification_id),
            job_id=saved_job.job_id,
            speaker_id=str(saved_job.speaker_id),
            verification_status=saved_job.verification_status.value,
            verification_result=saved_job.verification_result.value if saved_job.verification_result else None,
            corrections_count=saved_job.get_correction_count(),
            average_confidence=saved_job.calculate_average_confidence(),
            needs_manual_review=saved_job.needs_manual_review(),
            verified_by=str(saved_job.verified_by) if saved_job.verified_by else None,
            verified_at=saved_job.verified_at,
            has_qa_comments=bool(saved_job.qa_comments),
        )

    async def verify_correction_result(
        self, request: VerifyCorrectionRequest
    ) -> VerificationJobResponse:
        """Verify the result of error correction"""
        
        # Get verification job
        verification_job = await self._verification_job_repository.get_by_id(
            uuid.UUID(request.verification_id)
        )
        
        if not verification_job:
            raise ValueError(f"Verification job {request.verification_id} not found")
        
        # Update verification job with result
        updated_job = verification_job.with_verification_result(
            result=VerificationResult(request.verification_result),
            verified_by=uuid.UUID(request.verified_by),
            qa_comments=request.qa_comments
        )
        
        # Save updated job
        saved_job = await self._verification_job_repository.save_verification_job(
            updated_job
        )
        
        # Update error report status if linked
        if saved_job.error_report_id:
            await self._update_error_report_status(saved_job)
        
        return VerificationJobResponse(
            verification_id=str(saved_job.verification_id),
            job_id=saved_job.job_id,
            speaker_id=str(saved_job.speaker_id),
            verification_status=saved_job.verification_status.value,
            verification_result=saved_job.verification_result.value if saved_job.verification_result else None,
            corrections_count=saved_job.get_correction_count(),
            average_confidence=saved_job.calculate_average_confidence(),
            needs_manual_review=saved_job.needs_manual_review(),
            verified_by=str(saved_job.verified_by) if saved_job.verified_by else None,
            verified_at=saved_job.verified_at,
            has_qa_comments=bool(saved_job.qa_comments),
        )

    async def get_verification_jobs_for_review(
        self, speaker_id: Optional[str] = None
    ) -> List[VerificationJobResponse]:
        """Get verification jobs that need manual review"""
        
        jobs = await self._verification_job_repository.get_jobs_needing_review(
            speaker_id=uuid.UUID(speaker_id) if speaker_id else None
        )
        
        return [
            VerificationJobResponse(
                verification_id=str(job.verification_id),
                job_id=job.job_id,
                speaker_id=str(job.speaker_id),
                verification_status=job.verification_status.value,
                verification_result=job.verification_result.value if job.verification_result else None,
                corrections_count=job.get_correction_count(),
                average_confidence=job.calculate_average_confidence(),
                needs_manual_review=job.needs_manual_review(),
                verified_by=str(job.verified_by) if job.verified_by else None,
                verified_at=job.verified_at,
                has_qa_comments=bool(job.qa_comments),
            )
            for job in jobs
        ]

    async def get_verification_statistics(self, days: int = 30) -> dict:
        """Get verification workflow statistics"""
        
        stats = await self._verification_job_repository.get_verification_statistics(days)
        
        return {
            "period_days": days,
            "total_jobs": stats.get("total_jobs", 0),
            "verified_jobs": stats.get("verified_jobs", 0),
            "pending_jobs": stats.get("pending_jobs", 0),
            "rectified_count": stats.get("rectified_count", 0),
            "not_rectified_count": stats.get("not_rectified_count", 0),
            "partially_rectified_count": stats.get("partially_rectified_count", 0),
            "rectification_rate": stats.get("rectification_rate", 0.0),
            "average_corrections_per_job": stats.get("average_corrections_per_job", 0.0),
            "average_confidence": stats.get("average_confidence", 0.0),
            "jobs_needing_review": stats.get("jobs_needing_review", 0),
            "verification_trends": stats.get("verification_trends", {}),
        }

    async def _update_error_report_status(self, verification_job: VerificationJob):
        """Update linked error report status based on verification result"""
        
        if not verification_job.error_report_id:
            return
        
        # Map verification result to error report status
        status_mapping = {
            VerificationResult.RECTIFIED: "rectified",
            VerificationResult.NOT_RECTIFIED: "processing",
            VerificationResult.PARTIALLY_RECTIFIED: "processing",
            VerificationResult.NOT_APPLICABLE: "verified",
        }
        
        status_mapping.get(verification_job.verification_result, "processing")
        
        # Update error report status through repository
        # This would require access to error report repository
        # await self._error_report_repository.update_status(
        #     verification_job.error_report_id, new_status
        # )

    async def batch_process_verification_jobs(
        self, speaker_ids: List[str], max_jobs_per_speaker: int = 5
    ) -> dict:
        """Batch process verification jobs for multiple speakers"""
        
        results = {
            "processed_speakers": 0,
            "total_jobs_pulled": 0,
            "jobs_with_corrections": 0,
            "jobs_needing_review": 0,
            "errors": [],
        }
        
        for speaker_id in speaker_ids:
            try:
                # Pull jobs for speaker
                request = PullVerificationJobsRequest(
                    speaker_id=speaker_id,
                    date_range={
                        "start_date": (datetime.utcnow() - datetime.timedelta(days=7)).isoformat(),
                        "end_date": datetime.utcnow().isoformat(),
                    },
                    max_jobs=max_jobs_per_speaker,
                    requested_by="system"
                )
                
                jobs = await self.pull_verification_jobs(request)
                results["total_jobs_pulled"] += len(jobs)
                
                # Apply RAG corrections to each job
                for job in jobs:
                    try:
                        corrected_job = await self.apply_rag_corrections(job.verification_id)
                        
                        if corrected_job.corrections_count > 0:
                            results["jobs_with_corrections"] += 1
                        
                        if corrected_job.needs_manual_review:
                            results["jobs_needing_review"] += 1
                            
                    except Exception as e:
                        results["errors"].append({
                            "job_id": job.verification_id,
                            "speaker_id": speaker_id,
                            "error": str(e)
                        })
                
                results["processed_speakers"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "speaker_id": speaker_id,
                    "error": str(e)
                })
        
        return results
