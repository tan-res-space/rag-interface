# Enhanced Error Reporting API Documentation
## Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**API Version:** v2.0  
**Base URL:** `/api/v1/errors`

---

## Overview

The Enhanced Error Reporting API supports the quality-based speaker bucket management system with extended metadata fields, speaker history tracking, and verification workflows. This API enables QA personnel to report speaker-specific errors and track ASR quality improvements over time.

---

## Enhanced Error Reporting Endpoints

### POST /api/v1/errors
Submit an error report with enhanced metadata for quality-based speaker bucket management.

**Request Body:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440010",
  "speaker_id": "speaker-123",
  "client_id": "client-456", 
  "bucket_type": "medium_touch",
  "original_text": "The patient has severe hypertension",
  "corrected_text": "The patient has severe high blood pressure",
  "error_categories": ["medical_terminology"],
  "severity_level": "medium",
  "start_position": 20,
  "end_position": 32,
  "context_notes": "Medical terminology should be simplified for patient understanding",
  "metadata": {
    "audio_quality": "good",
    "speaker_clarity": "clear", 
    "background_noise": "low",
    "number_of_speakers": "one",
    "overlapping_speech": "no",
    "requires_specialized_knowledge": "yes",
    "additional_notes": "Complex medical terminology used throughout the transcript"
  }
}
```

**Enhanced Metadata Fields:**

| Field | Type | Options | Required | Description |
|-------|------|---------|----------|-------------|
| `bucket_type` | string | no_touch, low_touch, medium_touch, high_touch | Yes | Quality-based speaker classification |
| `audio_quality` | string | good, fair, poor | Yes | Overall audio quality assessment |
| `speaker_clarity` | string | clear, somewhat_clear, unclear, very_unclear | Yes | Speaker speech clarity level |
| `background_noise` | string | none, low, medium, high | Yes | Background noise level |
| `number_of_speakers` | string | one, two, three, four, five | Yes | Number of speakers in audio |
| `overlapping_speech` | string | yes, no | Yes | Presence of overlapping speech |
| `requires_specialized_knowledge` | string | yes, no | Yes | Whether specialized knowledge is required |
| `additional_notes` | string | Free text (max 1000 chars) | No | Additional contextual information |

**Response:**
```json
{
  "error_id": "550e8400-e29b-41d4-a716-446655440011",
  "status": "submitted",
  "speaker_bucket_updated": true,
  "bucket_transition": {
    "previous_bucket": "high_touch",
    "current_bucket": "medium_touch",
    "reason": "Quality improvement observed based on error patterns"
  },
  "submission_timestamp": "2024-12-19T14:30:00Z",
  "vector_db_id": "vec_550e8400-e29b-41d4-a716-446655440012"
}
```

---

## Speaker History and Performance Tracking

### GET /api/v1/speakers/{speaker_id}/history
Retrieve complete error history and performance metrics for a specific speaker.

**Path Parameters:**
- `speaker_id` (string): Unique speaker identifier

**Query Parameters:**
- `limit` (integer, default: 50): Maximum number of history entries
- `start_date` (string, ISO 8601): Filter history from this date
- `end_date` (string, ISO 8601): Filter history until this date

**Response:**
```json
{
  "speaker_id": "speaker-123",
  "current_bucket": "medium_touch",
  "bucket_history": [
    {
      "bucket_type": "high_touch",
      "assigned_date": "2024-11-01T10:00:00Z",
      "assigned_by": "qa-user-456",
      "reason": "Initial assessment - multiple errors observed"
    },
    {
      "bucket_type": "medium_touch",
      "assigned_date": "2024-12-01T10:00:00Z", 
      "assigned_by": "system",
      "reason": "Quality improvement - error rate decreased"
    }
  ],
  "error_history": [
    {
      "error_id": "error-789",
      "reported_date": "2024-11-15T14:30:00Z",
      "error_type": "medical_terminology",
      "original_text": "hypertension",
      "corrected_text": "high blood pressure",
      "status": "rectified",
      "verification_date": "2024-11-20T09:15:00Z"
    }
  ],
  "performance_metrics": {
    "total_errors_reported": 15,
    "errors_rectified": 12,
    "rectification_rate": 0.8,
    "average_time_to_rectification": "4.2 days",
    "last_assessment_date": "2024-12-15T10:00:00Z",
    "quality_trend": "improving"
  },
  "metadata_analysis": {
    "common_audio_quality": "good",
    "common_clarity_issues": ["medical_terminology", "pronunciation"],
    "specialized_knowledge_frequency": 0.7
  }
}
```

### GET /api/v1/speakers/{speaker_id}/performance-trends
Get performance trend analysis for speaker quality improvement tracking.

**Response:**
```json
{
  "speaker_id": "speaker-123",
  "trend_period": "last_6_months",
  "bucket_transitions": [
    {
      "date": "2024-07-01",
      "bucket": "high_touch",
      "error_count": 8
    },
    {
      "date": "2024-09-01", 
      "bucket": "medium_touch",
      "error_count": 5
    },
    {
      "date": "2024-12-01",
      "bucket": "medium_touch", 
      "error_count": 2
    }
  ],
  "improvement_indicators": {
    "error_reduction_rate": 0.75,
    "quality_consistency": 0.85,
    "time_in_current_bucket": "18 days",
    "projected_next_bucket": "low_touch",
    "confidence_score": 0.78
  }
}
```

---

## Verification Workflow APIs

### POST /api/v1/verification/pull-jobs
Pull jobs for a specific speaker from InstaNote Database for verification.

**Request Body:**
```json
{
  "speaker_id": "speaker-123",
  "date_range": {
    "start_date": "2024-12-01T00:00:00Z",
    "end_date": "2024-12-19T23:59:59Z"
  },
  "error_types": ["medical_terminology", "pronunciation"],
  "max_jobs": 10
}
```

**Response:**
```json
{
  "jobs_found": 5,
  "speaker_id": "speaker-123",
  "retrieval_timestamp": "2024-12-19T15:00:00Z",
  "jobs": [
    {
      "job_id": "instanote-job-456",
      "original_draft": "The patient has severe hypertension and diabetes",
      "rag_corrected_draft": "The patient has severe high blood pressure and diabetes",
      "corrections_applied": [
        {
          "type": "medical_terminology",
          "original": "hypertension", 
          "corrected": "high blood pressure",
          "confidence": 0.95
        }
      ],
      "verification_status": "pending",
      "job_metadata": {
        "audio_quality": "good",
        "speaker_clarity": "clear",
        "specialized_knowledge_required": true
      }
    }
  ]
}
```

### POST /api/v1/verification/verify-correction
Verify that a reported error has been rectified in subsequent drafts.

**Request Body:**
```json
{
  "verification_id": "verify-789",
  "job_id": "instanote-job-456",
  "error_id": "error-789",
  "verification_result": "rectified",
  "qa_comments": "Error successfully corrected in new draft",
  "verified_by": "qa-user-456"
}
```

**Response:**
```json
{
  "verification_id": "verify-789",
  "status": "verified",
  "verification_timestamp": "2024-12-19T15:30:00Z",
  "speaker_performance_updated": true,
  "bucket_reassessment_triggered": false,
  "next_verification_date": "2024-12-26T00:00:00Z"
}
```

---

## Dashboard Analytics APIs

### GET /api/v1/dashboard/bucket-overview
Get speaker distribution across quality-based buckets for dashboard display.

**Response:**
```json
{
  "total_speakers": 1250,
  "bucket_distribution": {
    "no_touch": {
      "count": 125,
      "percentage": 10.0,
      "trend": "increasing"
    },
    "low_touch": {
      "count": 375,
      "percentage": 30.0,
      "trend": "stable"
    },
    "medium_touch": {
      "count": 500,
      "percentage": 40.0,
      "trend": "decreasing"
    },
    "high_touch": {
      "count": 250,
      "percentage": 20.0,
      "trend": "decreasing"
    }
  },
  "quality_metrics": {
    "overall_improvement_rate": 0.15,
    "average_time_to_improvement": "21 days",
    "rectification_success_rate": 0.82
  },
  "generated_at": "2024-12-19T16:00:00Z"
}
```

### GET /api/v1/dashboard/performance-metrics
Get system-wide performance metrics for quality tracking.

**Response:**
```json
{
  "reporting_period": "last_30_days",
  "error_reporting_metrics": {
    "total_errors_reported": 1847,
    "errors_rectified": 1516,
    "rectification_rate": 0.82,
    "average_rectification_time": "3.8 days"
  },
  "bucket_transition_metrics": {
    "total_transitions": 156,
    "improvements": 134,
    "degradations": 22,
    "improvement_rate": 0.86
  },
  "metadata_insights": {
    "most_common_audio_quality": "good",
    "specialized_knowledge_percentage": 0.65,
    "overlapping_speech_percentage": 0.23,
    "multi_speaker_percentage": 0.18
  },
  "resource_allocation": {
    "mt_workload_distribution": {
      "no_touch": 0.05,
      "low_touch": 0.25,
      "medium_touch": 0.45,
      "high_touch": 0.25
    },
    "estimated_time_savings": "127 hours/month"
  }
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid bucket type provided",
    "details": {
      "field": "bucket_type",
      "provided_value": "invalid_bucket",
      "valid_options": ["no_touch", "low_touch", "medium_touch", "high_touch"]
    },
    "timestamp": "2024-12-19T16:30:00Z"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid input data
- `SPEAKER_NOT_FOUND`: Speaker ID does not exist
- `INSTANOTE_CONNECTION_ERROR`: Cannot connect to InstaNote Database
- `VECTOR_DB_ERROR`: Vector database operation failed
- `UNAUTHORIZED`: Authentication required
- `RATE_LIMIT_EXCEEDED`: Too many requests
