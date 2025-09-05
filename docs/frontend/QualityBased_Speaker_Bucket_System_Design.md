# Quality-Based Speaker Bucket Management System - Design Documentation

**Date:** December 19, 2024  
**Status:** Updated Requirements Implementation  
**Technology Stack:** React 18+ with TypeScript, Material-UI, FastAPI Backend  
**Project:** RAG Interface - Medical Transcription Quality Management System

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Bucket Classification System](#2-bucket-classification-system)
3. [Enhanced Metadata Requirements](#3-enhanced-metadata-requirements)
4. [User Workflows](#4-user-workflows)
5. [Backend API Design](#5-backend-api-design)
6. [Frontend Component Design](#6-frontend-component-design)
7. [Database Schema Updates](#7-database-schema-updates)
8. [Integration Requirements](#8-integration-requirements)

---

## 1. System Overview

### 1.1 Purpose
The Quality-Based Speaker Bucket Management System is designed to categorize speakers based on ASR draft quality and enable targeted error correction for Medical Transcriptionists (MTs) and Quality Assurance (QA) personnel.

### 1.2 Key Stakeholders
- **QA Personnel**: Primary users who identify and report speaker-specific errors
- **Medical Transcriptionists (MTs)**: Users who perform post-processing corrections
- **System Administrators**: Manage system configuration and user access

### 1.3 Business Objectives
- **Reduce Feedback Loop**: Shorten the time between error reporting and validation
- **Improve QA Coverage**: Enable QA team to focus on important errors rather than repetitive ones
- **Enhance ASR Quality**: Systematic improvement of ASR output for specific speakers
- **Resource Optimization**: Efficient allocation of MT resources based on quality levels

---

## 2. Bucket Classification System

### 2.1 Quality-Based Bucket Types

| Bucket Type | Icon | Description | MT Effort Required | Quality Level |
|-------------|------|-------------|-------------------|---------------|
| **No Touch** | 🎯 | ASR draft is of very high quality and no corrections are required | None | Excellent |
| **Low Touch** | 🔧 | ASR draft is of high quality and minimal corrections are required by MTs | Minimal | Good |
| **Medium Touch** | ⚙️ | ASR draft is of medium quality and some corrections are required | Moderate | Fair |
| **High Touch** | 🛠️ | ASR draft is of low quality and significant corrections are required | Extensive | Poor |

### 2.2 Bucket Assignment Criteria
- **QA Assessment**: Based on QA personnel evaluation of ASR draft quality
- **Error Frequency**: Number and severity of errors in ASR output
- **Correction Complexity**: Level of intervention required by MTs
- **Consistency**: Reliability of ASR output quality for the speaker

### 2.3 Bucket Transition Logic
- **Quality Improvement**: Speakers can move to better buckets (High → Medium → Low → No Touch)
- **Quality Degradation**: Speakers may move to worse buckets if quality declines
- **Performance Tracking**: System monitors bucket transitions over time
- **Manual Override**: QA personnel can manually adjust bucket assignments

---

## 3. Enhanced Metadata Requirements

### 3.1 Core Metadata Fields
- **Speaker ID**: Unique identifier provided by user (required)
- **Client ID**: Source system or client identifier (required)
- **Speaker Bucket**: Selected from dropdown (no_touch, low_touch, medium_touch, high_touch)

### 3.2 Audio Quality Assessment
- **Audio Quality**: User input (good, fair, poor)
- **Speaker Clarity**: User input (clear, somewhat clear, unclear, very unclear)
- **Background Noise**: User input (none, low, medium, high)

### 3.3 New Enhanced Metadata Fields
- **Number of Speakers**: User input (one, two, three, four, five)
- **Overlapping Speech**: User input (yes, no)
- **Requires Specialized Knowledge**: User input (yes, no)
- **Additional Notes**: Free text field for contextual information

### 3.4 Metadata Validation Rules
- All core metadata fields are required
- Audio quality assessment fields have predefined options
- Enhanced metadata fields provide additional context for error analysis
- Additional notes field supports up to 1000 characters

---

## 4. User Workflows

### 4.1 QA Error Reporting Workflow
1. **Error Identification**: QA notices specific error for specific speaker in ASR draft
2. **Speaker Classification**: QA identifies speaker with appropriate bucket type
3. **Error Selection**: QA selects and highlights error text in ASR draft
4. **Error Categorization**: QA categorizes error type (pronunciation, medical terminology, etc.)
5. **Correction Input**: QA provides corrected text for the error
6. **Metadata Capture**: QA fills in all required and enhanced metadata fields
7. **Submission**: Error and corrections submitted to vector database with metadata

### 4.2 Speaker History Viewing Workflow
1. **Speaker Search**: QA searches for specific speaker by ID
2. **History Display**: System shows complete error history for speaker
3. **Performance Trends**: Visual representation of speaker improvement over time
4. **Bucket Transitions**: Timeline of bucket changes with reasons

### 4.3 Verification Workflow
1. **Job Retrieval**: System pulls jobs for same speaker from InstaNote Database
2. **RAG Application**: Apply RAG-based corrections to new drafts
3. **Verification Check**: QA verifies that reported errors are rectified
4. **Performance Update**: Update speaker performance metrics based on verification results

### 4.4 Dashboard Overview Workflow
1. **Bucket Distribution**: View current distribution of speakers across buckets
2. **Performance Metrics**: Monitor overall system performance and trends
3. **Quality Indicators**: Track improvement in ASR quality over time
4. **Resource Planning**: Analyze MT workload distribution across bucket types

---

## 5. Backend API Design

### 5.1 Enhanced Error Reporting API

#### POST /api/v1/errors
**Enhanced Request Body:**
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
  "context_notes": "Medical terminology should be simplified",
  "metadata": {
    "audio_quality": "good",
    "speaker_clarity": "clear",
    "background_noise": "low",
    "number_of_speakers": "one",
    "overlapping_speech": "no",
    "requires_specialized_knowledge": "yes",
    "additional_notes": "Complex medical terminology used throughout"
  }
}
```

### 5.2 Speaker Management API

#### GET /api/v1/speakers/{speaker_id}/history
**Response:**
```json
{
  "speaker_id": "speaker-123",
  "current_bucket": "medium_touch",
  "bucket_history": [
    {
      "bucket_type": "high_touch",
      "assigned_date": "2024-11-01T10:00:00Z",
      "reason": "Initial assessment"
    },
    {
      "bucket_type": "medium_touch", 
      "assigned_date": "2024-12-01T10:00:00Z",
      "reason": "Quality improvement observed"
    }
  ],
  "error_history": [
    {
      "error_id": "error-789",
      "reported_date": "2024-11-15T14:30:00Z",
      "error_type": "medical_terminology",
      "status": "rectified"
    }
  ],
  "performance_metrics": {
    "total_errors_reported": 15,
    "errors_rectified": 12,
    "improvement_rate": 0.8,
    "last_assessment_date": "2024-12-15T10:00:00Z"
  }
}
```

### 5.3 Verification API

#### POST /api/v1/verification/pull-jobs
**Request:**
```json
{
  "speaker_id": "speaker-123",
  "date_range": {
    "start_date": "2024-12-01T00:00:00Z",
    "end_date": "2024-12-19T23:59:59Z"
  }
}
```

**Response:**
```json
{
  "jobs_found": 5,
  "jobs": [
    {
      "job_id": "job-456",
      "draft_text": "Original ASR draft text",
      "corrected_text": "RAG-corrected text",
      "corrections_applied": ["medical_terminology", "pronunciation"],
      "verification_status": "pending"
    }
  ]
}
```

---

## 6. Frontend Component Design

### 6.1 Enhanced Metadata Input Component
- **Bucket Type Selector**: Dropdown with four quality-based options
- **Audio Assessment Section**: Grouped fields for audio quality evaluation
- **Enhanced Metadata Section**: New fields for speaker count, overlapping speech, specialized knowledge
- **Validation**: Real-time validation with clear error messages
- **Accessibility**: WCAG 2.1 AA compliance with screen reader support

### 6.2 Speaker History Dashboard Component
- **Search Interface**: Speaker ID search with autocomplete
- **History Timeline**: Visual timeline of bucket transitions and error reports
- **Performance Charts**: Graphs showing improvement trends over time
- **Error Summary**: Categorized view of reported errors and their status

### 6.3 Verification Interface Component
- **Job List**: Display of pulled jobs for verification
- **Side-by-side Comparison**: Original vs. RAG-corrected text
- **Verification Controls**: Mark as verified/not verified with comments
- **Batch Operations**: Verify multiple jobs simultaneously

### 6.4 Dashboard Overview Component
- **Bucket Distribution Chart**: Pie chart showing speaker distribution across buckets
- **Performance Metrics**: Key performance indicators and trends
- **Quality Improvement Tracking**: Visual representation of system-wide improvements
- **Resource Allocation**: MT workload distribution across bucket types

---

## 7. Database Schema Updates

### 7.1 Enhanced Error Reports Table
```sql
ALTER TABLE error_reports ADD COLUMN number_of_speakers VARCHAR(10);
ALTER TABLE error_reports ADD COLUMN overlapping_speech BOOLEAN;
ALTER TABLE error_reports ADD COLUMN requires_specialized_knowledge BOOLEAN;
ALTER TABLE error_reports ADD COLUMN additional_notes TEXT;
```

### 7.2 Speaker Bucket History Table
```sql
CREATE TABLE speaker_bucket_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id VARCHAR(255) NOT NULL,
    bucket_type VARCHAR(50) NOT NULL,
    assigned_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by VARCHAR(255),
    reason TEXT,
    previous_bucket VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 7.3 Verification Jobs Table
```sql
CREATE TABLE verification_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) NOT NULL,
    speaker_id VARCHAR(255) NOT NULL,
    original_text TEXT NOT NULL,
    corrected_text TEXT,
    corrections_applied JSONB,
    verification_status VARCHAR(50) DEFAULT 'pending',
    verified_by VARCHAR(255),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 8. Integration Requirements

### 8.1 InstaNote Database Integration
- **Connection**: Establish secure connection to InstaNote Database
- **Job Retrieval**: Query jobs by speaker ID and date range
- **Data Mapping**: Map InstaNote job structure to internal format
- **Error Handling**: Robust error handling for database connectivity issues

### 8.2 RAG System Integration
- **Correction Application**: Apply RAG-based corrections to retrieved drafts
- **Pattern Matching**: Match reported errors with correction patterns
- **Quality Assessment**: Evaluate effectiveness of applied corrections
- **Feedback Loop**: Update RAG models based on verification results

### 8.3 Vector Database Integration
- **Enhanced Metadata Storage**: Store all new metadata fields in vector database
- **Search Optimization**: Optimize search queries for enhanced metadata fields
- **Similarity Matching**: Improve similarity matching with additional context
- **Performance Monitoring**: Track query performance with expanded metadata

---

## Implementation Priority

### Phase 1: Core Bucket System Updates
1. Update bucket type definitions and UI components
2. Enhance metadata input forms with new fields
3. Update API endpoints for enhanced metadata

### Phase 2: Speaker History and Performance Tracking
1. Implement speaker history viewing functionality
2. Create performance tracking dashboard
3. Add bucket transition monitoring

### Phase 3: Verification Workflow
1. Integrate with InstaNote Database
2. Implement job retrieval and RAG correction application
3. Create verification interface for QA personnel

### Phase 4: Advanced Analytics and Reporting
1. Implement comprehensive dashboard analytics
2. Add performance trend analysis
3. Create resource allocation reporting
