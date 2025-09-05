# Speaker Bucket Management API Documentation
## Quality-Based Speaker Bucket Management System

## Overview

The Speaker Bucket Management API provides comprehensive endpoints for managing speaker categorization, quality assessment, and bucket management in the ASR Error Reporting System. The system enables quality-based speaker classification, error tracking, performance monitoring, and verification workflows for Medical Transcriptionists and QA personnel.

**Last Updated:** December 19, 2024
**API Version:** v1
**Base URL:** `/api/v1/speakers`

### Key Features
- **Quality-Based Classification**: Speakers categorized by ASR draft quality (No Touch, Low Touch, Medium Touch, High Touch)
- **Enhanced Metadata Capture**: Extended metadata fields including speaker count, overlapping speech, specialized knowledge requirements
- **Speaker History Tracking**: Complete error history and performance monitoring for each speaker
- **Verification Workflow**: Integration with InstaNote Database for error rectification verification
- **RAG-Based Corrections**: Apply corrections to subsequent drafts for same speakers

## Service Architecture

### User Management Service (Port 8004)
- **Base URL**: `http://localhost:8004`
- **Responsibilities**: Speaker CRUD operations, bucket transitions, user authentication

### Verification Service (Port 8001)
- **Base URL**: `http://localhost:8001`
- **Responsibilities**: SER calculation, MT validation workflow, quality metrics

### RAG Integration Service (Port 8002)
- **Base URL**: `http://localhost:8002`
- **Responsibilities**: Speaker-specific RAG processing, error pattern analysis

### API Gateway
- **Base URL**: `http://localhost:8000`
- **Responsibilities**: Unified interface, workflow orchestration, dashboard data

## Authentication

All endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## API Endpoints

### 1. Speaker Management

#### GET /api/v1/speakers
Search speakers with comprehensive filtering and pagination.

**Query Parameters:**
- `name_pattern` (string, optional): Speaker name pattern to search for
- `bucket` (enum, optional): Filter by speaker bucket (HIGH_TOUCH, MEDIUM_TOUCH, LOW_TOUCH, NO_TOUCH)
- `min_ser_score` (float, optional): Minimum SER score filter (0-100)
- `max_ser_score` (float, optional): Maximum SER score filter (0-100)
- `has_sufficient_data` (boolean, optional): Filter by data sufficiency
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50, max: 200): Page size

**Response:**
```json
{
  "speakers": [
    {
      "speaker_id": "uuid",
      "speaker_identifier": "string",
      "speaker_name": "string",
      "current_bucket": "HIGH_TOUCH",
      "recommended_bucket": "MEDIUM_TOUCH",
      "note_count": 150,
      "average_ser_score": 18.5,
      "quality_trend": "improving",
      "should_transition": true,
      "has_sufficient_data": true,
      "created_at": "2025-08-26T10:00:00Z",
      "updated_at": "2025-08-26T10:00:00Z"
    }
  ],
  "total_count": 246,
  "page": 1,
  "page_size": 50,
  "total_pages": 5
}
```

#### POST /api/v1/speakers
Create a new speaker.

**Request Body:**
```json
{
  "speaker_identifier": "SPEAKER_001",
  "speaker_name": "Dr. John Smith",
  "initial_bucket": "HIGH_TOUCH",
  "metadata": {
    "department": "Cardiology",
    "location": "Main Hospital"
  }
}
```

#### GET /api/v1/speakers/{speaker_id}
Get detailed speaker information by ID.

#### PUT /api/v1/speakers/{speaker_id}
Update speaker information.

#### GET /api/v1/speakers/identifier/{speaker_identifier}
Get speaker by external identifier.

#### GET /api/v1/speakers/bucket/{bucket}
Get all speakers in a specific bucket.

#### GET /api/v1/speakers/transitions/needed
Get speakers that need bucket transition based on quality metrics.

#### POST /api/v1/speakers/{speaker_id}/statistics/update
Update speaker statistics from historical data.

### 1.2. Dynamic Bucket Progression (NEW)

#### GET /api/v1/speakers/{speaker_id}/profile
Get comprehensive speaker profile with bucket progression data.

**Response:**
```json
{
  "speaker_id": "550e8400-e29b-41d4-a716-446655440001",
  "current_bucket": "intermediate",
  "bucket_info": {
    "label": "Intermediate",
    "description": "Developing speaker with moderate experience",
    "color": "#ff9800",
    "icon": "🌿",
    "level": 1
  },
  "statistics": {
    "total_reports": 25,
    "total_errors_found": 18,
    "total_corrections_made": 22,
    "average_error_rate": 0.08,
    "average_correction_accuracy": 0.82,
    "days_in_current_bucket": 15,
    "bucket_change_count": 2
  },
  "timestamps": {
    "created_at": "2024-11-01T10:00:00Z",
    "updated_at": "2024-12-19T14:30:00Z",
    "last_report_date": "2024-12-19T12:15:00Z"
  },
  "metadata": {}
}
```

#### GET /api/v1/speakers/{speaker_id}/bucket-history
Get bucket change history for a speaker.

**Query Parameters:**
- `limit` (integer, default: 50, max: 100): Maximum number of history entries

**Response:**
```json
{
  "speaker_id": "550e8400-e29b-41d4-a716-446655440001",
  "total_changes": 3,
  "history": [
    {
      "change_id": "change-uuid-1",
      "old_bucket": {
        "type": "beginner",
        "label": "Beginner",
        "level": 0
      },
      "new_bucket": {
        "type": "intermediate",
        "label": "Intermediate",
        "level": 1
      },
      "change_reason": "Excellent performance qualifies for intermediate level: Error rate 7.2%, Accuracy 85.3%, Consistency 78.1%",
      "changed_at": "2024-11-15T09:30:00Z",
      "metrics_at_change": {
        "total_reports": 12,
        "average_error_rate": 0.072,
        "average_correction_accuracy": 0.853,
        "consistency_score": 0.781,
        "improvement_trend": 0.15
      },
      "metadata": {}
    }
  ]
}
```

#### POST /api/v1/speakers/{speaker_id}/evaluate-progression
Trigger manual bucket progression evaluation.

**Query Parameters:**
- `force_evaluation` (boolean, default: false): Force evaluation even if criteria not met

**Response:**
```json
{
  "speaker_id": "550e8400-e29b-41d4-a716-446655440001",
  "evaluation_performed": true,
  "bucket_changed": true,
  "old_bucket": "intermediate",
  "new_bucket": "advanced",
  "change_reason": "Excellent performance qualifies for advanced level: Error rate 4.8%, Accuracy 88.7%, Consistency 82.4%",
  "recommendation": {
    "recommended_bucket": "advanced",
    "direction": "promotion",
    "confidence_score": 0.87,
    "reason": "Performance consistently exceeds intermediate level requirements"
  },
  "evaluation_timestamp": "2024-12-19T14:30:00Z"
}
```

#### POST /api/v1/speakers/batch-evaluate
Trigger batch bucket progression evaluation.

**Query Parameters:**
- `max_profiles` (integer, default: 100, max: 500): Maximum profiles to evaluate
- `force_evaluation` (boolean, default: false): Force evaluation for all profiles

**Response:**
```json
{
  "total_profiles_evaluated": 45,
  "bucket_changes_applied": 8,
  "evaluation_timestamp": "2024-12-19T14:30:00Z",
  "results_summary": [
    {
      "speaker_id": "speaker-1",
      "bucket_changed": true,
      "old_bucket": "beginner",
      "new_bucket": "intermediate",
      "confidence_score": 0.85
    }
  ]
}
```

#### GET /api/v1/speakers/bucket-statistics
Get global bucket distribution and progression statistics.

**Response:**
```json
{
  "total_profiles": 1250,
  "bucket_distribution": {
    "beginner": {
      "count": 450,
      "percentage": 36.0,
      "info": {
        "label": "Beginner",
        "description": "New speaker, learning basic transcription patterns",
        "color": "#f44336",
        "icon": "🌱"
      }
    },
    "intermediate": {
      "count": 520,
      "percentage": 41.6,
      "info": {
        "label": "Intermediate",
        "description": "Developing speaker with moderate experience",
        "color": "#ff9800",
        "icon": "🌿"
      }
    },
    "advanced": {
      "count": 230,
      "percentage": 18.4,
      "info": {
        "label": "Advanced",
        "description": "Experienced speaker with good transcription skills",
        "color": "#2196f3",
        "icon": "🌳"
      }
    },
    "expert": {
      "count": 50,
      "percentage": 4.0,
      "info": {
        "label": "Expert",
        "description": "Highly skilled speaker with excellent transcription quality",
        "color": "#4caf50",
        "icon": "🏆"
      }
    }
  },
  "change_statistics": {
    "total_bucket_changes": 2847,
    "recent_bucket_changes": 156,
    "average_changes_per_profile": 2.3
  },
  "generated_at": "2024-12-19T14:30:00Z"
}
```

#### GET /api/v1/speakers/bucket-types
Get bucket type definitions and progression information.

**Response:**
```json
{
  "bucket_types": {
    "beginner": {
      "label": "Beginner",
      "description": "New speaker, learning basic transcription patterns",
      "color": "#f44336",
      "icon": "🌱"
    },
    "intermediate": {
      "label": "Intermediate",
      "description": "Developing speaker with moderate experience",
      "color": "#ff9800",
      "icon": "🌿"
    },
    "advanced": {
      "label": "Advanced",
      "description": "Experienced speaker with good transcription skills",
      "color": "#2196f3",
      "icon": "🌳"
    },
    "expert": {
      "label": "Expert",
      "description": "Highly skilled speaker with excellent transcription quality",
      "color": "#4caf50",
      "icon": "🏆"
    }
  },
  "progression_order": ["beginner", "intermediate", "advanced", "expert"],
  "total_levels": 4
}
```

### 2. Bucket Transitions

#### POST /api/v1/bucket-transitions
Create a new bucket transition request.

**Request Body:**
```json
{
  "speaker_id": "uuid",
  "from_bucket": "HIGH_TOUCH",
  "to_bucket": "MEDIUM_TOUCH",
  "transition_reason": "Consistent quality improvement over 30 days",
  "ser_improvement": 15.2,
  "requested_by": "uuid"
}
```

#### GET /api/v1/bucket-transitions
Get transition requests with filters.

**Query Parameters:**
- `status` (string, optional): Filter by status (pending, approved, rejected)
- `speaker_id` (uuid, optional): Filter by speaker ID
- `urgent_only` (boolean, default: false): Show only urgent requests
- `limit` (integer, default: 100, max: 500): Maximum number of requests

#### GET /api/v1/bucket-transitions/pending
Get all pending transition requests sorted by priority.

#### POST /api/v1/bucket-transitions/{request_id}/approve
Approve a bucket transition request.

#### POST /api/v1/bucket-transitions/{request_id}/reject
Reject a bucket transition request.

#### GET /api/v1/bucket-transitions/speaker/{speaker_id}/history
Get complete transition history for a speaker.

### 3. SER Calculation

#### POST /api/v1/ser/calculate
Calculate SER metrics for a single text pair.

**Request Body:**
```json
{
  "speaker_id": "uuid",
  "original_text": "The patient has chest pain",
  "corrected_text": "The patient has chest pain and shortness of breath",
  "calculation_metadata": {
    "note_type": "progress_note",
    "specialty": "cardiology"
  }
}
```

**Response:**
```json
{
  "ser_metrics": {
    "ser_score": 18.5,
    "edit_distance": 12,
    "insertions": 5,
    "deletions": 2,
    "substitutions": 3,
    "moves": 2,
    "quality_level": "medium",
    "is_acceptable_quality": true
  },
  "calculation_metadata": {},
  "processing_time": 0.125
}
```

#### POST /api/v1/ser/calculate/batch
Calculate SER metrics for multiple text pairs efficiently.

#### POST /api/v1/ser/compare
Compare SER results between original and corrected texts.

#### GET /api/v1/ser/speaker/{speaker_id}/analysis
Get comprehensive SER analysis for a speaker.

**Query Parameters:**
- `include_historical_trend` (boolean, default: true)
- `include_quality_distribution` (boolean, default: true)
- `include_error_pattern_analysis` (boolean, default: false)
- `date_range_start` (string, optional): Start date (ISO format)
- `date_range_end` (string, optional): End date (ISO format)

### 4. MT Validation Workflow

#### POST /api/v1/mt-validation/sessions
Start a new MT validation session.

**Request Body:**
```json
{
  "speaker_id": "uuid",
  "session_name": "Quality Assessment - Dr. Smith",
  "test_data_ids": ["uuid1", "uuid2", "uuid3"],
  "mt_user_id": "uuid",
  "session_metadata": {
    "priority": "high",
    "deadline": "2025-08-30T17:00:00Z"
  }
}
```

#### GET /api/v1/mt-validation/sessions/{session_id}/test-data
Get test data for MT validation session with SER metrics.

#### POST /api/v1/mt-validation/sessions/{session_id}/feedback
Submit MT feedback for a validation item.

**Request Body:**
```json
{
  "historical_data_id": "uuid",
  "original_asr_text": "Patient has chest pain",
  "rag_corrected_text": "Patient has chest pain and dyspnea",
  "final_reference_text": "Patient has chest pain and shortness of breath",
  "mt_feedback_rating": 4,
  "mt_comments": "Good correction, minor terminology preference",
  "improvement_assessment": "moderate",
  "recommended_for_bucket_change": true,
  "feedback_metadata": {}
}
```

#### POST /api/v1/mt-validation/sessions/{session_id}/complete
Complete a validation session and generate final recommendations.

### 5. Speaker RAG Processing

#### POST /api/v1/speaker-rag/process-historical
Process historical data for a speaker to generate error-correction pairs.

#### POST /api/v1/speaker-rag/generate-pairs
Generate error-correction pairs from ASR and final text.

#### POST /api/v1/speaker-rag/vectorize
Vectorize error-correction pairs for similarity search.

#### GET /api/v1/speaker-rag/speaker/{speaker_id}/error-patterns
Get comprehensive error patterns analysis for a speaker.

#### POST /api/v1/speaker-rag/jobs
Create a new speaker RAG processing job.

#### GET /api/v1/speaker-rag/jobs/{job_id}
Get processing job status and progress.

### 6. Workflow Orchestration (API Gateway)

#### GET /api/v1/speaker-bucket-management/speakers/{speaker_id}/comprehensive
Get comprehensive speaker view with data from all services.

**Query Parameters:**
- `include_ser_analysis` (boolean, default: true)
- `include_error_patterns` (boolean, default: true)
- `include_transition_history` (boolean, default: true)

#### POST /api/v1/speaker-bucket-management/workflows/complete-assessment
Complete speaker assessment workflow with orchestrated processing.

#### GET /api/v1/speaker-bucket-management/dashboard/overview
Get dashboard overview with key metrics from all services.

### 7. Statistics and Analytics

#### GET /api/v1/speakers/statistics/buckets
Get comprehensive speaker bucket statistics.

#### GET /api/v1/ser/metrics/summary
Get system-wide SER metrics summary.

#### GET /api/v1/speaker-rag/statistics/summary
Get RAG processing statistics and performance metrics.

#### GET /api/v1/mt-validation/statistics/summary
Get MT validation workflow statistics.

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Speaker not found",
    "details": "Speaker with ID 12345 does not exist"
  },
  "timestamp": "2025-08-26T10:00:00Z",
  "request_id": "uuid",
  "version": "1.0.0"
}
```

## Health Checks

Each service provides health check endpoints:

- `GET /health` - Basic service health
- `GET /api/v1/speakers/health/check` - Speaker management health
- `GET /api/v1/ser/health/check` - SER calculation health
- `GET /api/v1/mt-validation/health/check` - MT validation health
- `GET /api/v1/speaker-rag/health/check` - Speaker RAG processing health

## Rate Limiting

API endpoints are rate-limited to ensure system stability:

- Standard endpoints: 1000 requests/hour per user
- Batch processing endpoints: 100 requests/hour per user
- Statistics endpoints: 500 requests/hour per user

## Pagination

List endpoints support cursor-based pagination:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_count": 246,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```
