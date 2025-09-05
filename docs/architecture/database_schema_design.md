# Database Schema Design - Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**Version:** 2.0  
**Database:** PostgreSQL 14+

---

## Overview

This document outlines the database schema design for the Quality-Based Speaker Bucket Management System, supporting enhanced metadata capture, speaker history tracking, and verification workflows.

---

## Core Tables

### 1. Enhanced Error Reports Table

```sql
CREATE TABLE error_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) NOT NULL,
    speaker_id VARCHAR(255) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    bucket_type VARCHAR(50) NOT NULL CHECK (bucket_type IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch')),
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    error_categories JSONB NOT NULL,
    severity_level VARCHAR(20) NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    start_position INTEGER NOT NULL,
    end_position INTEGER NOT NULL,
    context_notes TEXT,
    
    -- Core Metadata
    audio_quality VARCHAR(20) NOT NULL CHECK (audio_quality IN ('good', 'fair', 'poor')),
    speaker_clarity VARCHAR(30) NOT NULL CHECK (speaker_clarity IN ('clear', 'somewhat_clear', 'unclear', 'very_unclear')),
    background_noise VARCHAR(20) NOT NULL CHECK (background_noise IN ('none', 'low', 'medium', 'high')),
    
    -- Enhanced Metadata Fields
    number_of_speakers VARCHAR(10) NOT NULL CHECK (number_of_speakers IN ('one', 'two', 'three', 'four', 'five')),
    overlapping_speech BOOLEAN NOT NULL,
    requires_specialized_knowledge BOOLEAN NOT NULL,
    additional_notes TEXT,
    
    -- System Fields
    reported_by VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'submitted' CHECK (status IN ('submitted', 'processing', 'rectified', 'verified', 'rejected')),
    vector_db_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT error_reports_additional_notes_length CHECK (char_length(additional_notes) <= 1000)
);

-- Indexes for performance
CREATE INDEX idx_error_reports_speaker_id ON error_reports(speaker_id);
CREATE INDEX idx_error_reports_bucket_type ON error_reports(bucket_type);
CREATE INDEX idx_error_reports_status ON error_reports(status);
CREATE INDEX idx_error_reports_created_at ON error_reports(created_at);
CREATE INDEX idx_error_reports_client_id ON error_reports(client_id);
```

### 2. Speaker Bucket History Table

```sql
CREATE TABLE speaker_bucket_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id VARCHAR(255) NOT NULL,
    bucket_type VARCHAR(50) NOT NULL CHECK (bucket_type IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch')),
    previous_bucket VARCHAR(50) CHECK (previous_bucket IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch')),
    assigned_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by VARCHAR(255) NOT NULL,
    assignment_reason TEXT NOT NULL,
    
    -- Performance metrics at time of assignment
    error_count_at_assignment INTEGER DEFAULT 0,
    rectification_rate_at_assignment DECIMAL(5,4),
    quality_score_at_assignment DECIMAL(5,4),
    
    -- Metadata
    assignment_type VARCHAR(20) DEFAULT 'manual' CHECK (assignment_type IN ('manual', 'automatic', 'system')),
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_speaker_bucket_history_speaker_id ON speaker_bucket_history(speaker_id);
CREATE INDEX idx_speaker_bucket_history_assigned_date ON speaker_bucket_history(assigned_date);
CREATE INDEX idx_speaker_bucket_history_bucket_type ON speaker_bucket_history(bucket_type);
```

### 3. Verification Jobs Table

```sql
CREATE TABLE verification_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) NOT NULL, -- InstaNote job ID
    speaker_id VARCHAR(255) NOT NULL,
    error_report_id UUID REFERENCES error_reports(id),
    
    -- Job content
    original_draft TEXT NOT NULL,
    rag_corrected_draft TEXT,
    corrections_applied JSONB,
    
    -- Verification details
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'not_rectified', 'partially_rectified')),
    verification_result VARCHAR(20) CHECK (verification_result IN ('rectified', 'not_rectified', 'partially_rectified')),
    qa_comments TEXT,
    verified_by VARCHAR(255),
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Job metadata from InstaNote
    job_metadata JSONB,
    retrieval_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_verification_jobs_speaker_id ON verification_jobs(speaker_id);
CREATE INDEX idx_verification_jobs_status ON verification_jobs(verification_status);
CREATE INDEX idx_verification_jobs_job_id ON verification_jobs(job_id);
CREATE INDEX idx_verification_jobs_error_report_id ON verification_jobs(error_report_id);
```

### 4. Speaker Performance Metrics Table

```sql
CREATE TABLE speaker_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id VARCHAR(255) NOT NULL,
    current_bucket VARCHAR(50) NOT NULL CHECK (current_bucket IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch')),
    
    -- Error metrics
    total_errors_reported INTEGER DEFAULT 0,
    errors_rectified INTEGER DEFAULT 0,
    errors_pending INTEGER DEFAULT 0,
    rectification_rate DECIMAL(5,4) DEFAULT 0.0000,
    
    -- Quality metrics
    average_audio_quality DECIMAL(3,2),
    average_clarity_score DECIMAL(3,2),
    specialized_knowledge_frequency DECIMAL(5,4),
    overlapping_speech_frequency DECIMAL(5,4),
    
    -- Performance trends
    quality_trend VARCHAR(20) CHECK (quality_trend IN ('improving', 'stable', 'declining')),
    last_assessment_date TIMESTAMP WITH TIME ZONE,
    next_assessment_date TIMESTAMP WITH TIME ZONE,
    
    -- Time metrics
    average_time_to_rectification INTERVAL,
    time_in_current_bucket INTERVAL,
    
    -- System fields
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_speaker_metrics UNIQUE(speaker_id)
);

-- Indexes
CREATE INDEX idx_speaker_performance_speaker_id ON speaker_performance_metrics(speaker_id);
CREATE INDEX idx_speaker_performance_bucket ON speaker_performance_metrics(current_bucket);
CREATE INDEX idx_speaker_performance_trend ON speaker_performance_metrics(quality_trend);
```

### 5. System Configuration Table

```sql
CREATE TABLE system_configuration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default configurations
INSERT INTO system_configuration (config_key, config_value, description, category, created_by) VALUES
('bucket_thresholds', '{"no_touch": {"error_rate": 0.02}, "low_touch": {"error_rate": 0.05}, "medium_touch": {"error_rate": 0.10}, "high_touch": {"error_rate": 0.20}}', 'Error rate thresholds for bucket classification', 'bucket_management', 'system'),
('verification_settings', '{"auto_pull_jobs": true, "max_jobs_per_pull": 10, "verification_window_days": 7}', 'Settings for verification workflow', 'verification', 'system'),
('metadata_validation', '{"required_fields": ["audio_quality", "speaker_clarity", "background_noise", "number_of_speakers", "overlapping_speech", "requires_specialized_knowledge"], "max_additional_notes_length": 1000}', 'Metadata validation rules', 'validation', 'system');
```

---

## Views for Analytics

### 1. Speaker Bucket Distribution View

```sql
CREATE VIEW speaker_bucket_distribution AS
SELECT 
    current_bucket,
    COUNT(*) as speaker_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage,
    AVG(rectification_rate) as avg_rectification_rate,
    AVG(EXTRACT(EPOCH FROM time_in_current_bucket) / 86400) as avg_days_in_bucket
FROM speaker_performance_metrics 
GROUP BY current_bucket;
```

### 2. Error Reporting Trends View

```sql
CREATE VIEW error_reporting_trends AS
SELECT 
    DATE_TRUNC('week', created_at) as week_start,
    bucket_type,
    COUNT(*) as error_count,
    COUNT(CASE WHEN status = 'rectified' THEN 1 END) as rectified_count,
    ROUND(COUNT(CASE WHEN status = 'rectified' THEN 1 END) * 100.0 / COUNT(*), 2) as rectification_percentage,
    AVG(CASE WHEN audio_quality = 'good' THEN 3 WHEN audio_quality = 'fair' THEN 2 ELSE 1 END) as avg_audio_quality_score
FROM error_reports 
WHERE created_at >= NOW() - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', created_at), bucket_type
ORDER BY week_start DESC, bucket_type;
```

### 3. Speaker Performance Summary View

```sql
CREATE VIEW speaker_performance_summary AS
SELECT 
    spm.speaker_id,
    spm.current_bucket,
    spm.total_errors_reported,
    spm.rectification_rate,
    spm.quality_trend,
    spm.time_in_current_bucket,
    sbh.assignment_reason as current_bucket_reason,
    sbh.assigned_date as bucket_assigned_date,
    COUNT(er.id) as recent_errors_30_days,
    AVG(CASE WHEN er.audio_quality = 'good' THEN 3 WHEN er.audio_quality = 'fair' THEN 2 ELSE 1 END) as recent_avg_audio_quality
FROM speaker_performance_metrics spm
LEFT JOIN speaker_bucket_history sbh ON spm.speaker_id = sbh.speaker_id 
    AND sbh.assigned_date = (
        SELECT MAX(assigned_date) 
        FROM speaker_bucket_history 
        WHERE speaker_id = spm.speaker_id
    )
LEFT JOIN error_reports er ON spm.speaker_id = er.speaker_id 
    AND er.created_at >= NOW() - INTERVAL '30 days'
GROUP BY spm.speaker_id, spm.current_bucket, spm.total_errors_reported, 
         spm.rectification_rate, spm.quality_trend, spm.time_in_current_bucket,
         sbh.assignment_reason, sbh.assigned_date;
```

---

## Stored Procedures

### 1. Update Speaker Performance Metrics

```sql
CREATE OR REPLACE FUNCTION update_speaker_performance_metrics(p_speaker_id VARCHAR(255))
RETURNS VOID AS $$
DECLARE
    v_total_errors INTEGER;
    v_rectified_errors INTEGER;
    v_rectification_rate DECIMAL(5,4);
    v_avg_audio_quality DECIMAL(3,2);
    v_current_bucket VARCHAR(50);
BEGIN
    -- Calculate metrics from error reports
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN status = 'rectified' THEN 1 END),
        CASE WHEN COUNT(*) > 0 THEN 
            COUNT(CASE WHEN status = 'rectified' THEN 1 END)::DECIMAL / COUNT(*)
        ELSE 0 END,
        AVG(CASE WHEN audio_quality = 'good' THEN 3 WHEN audio_quality = 'fair' THEN 2 ELSE 1 END)
    INTO v_total_errors, v_rectified_errors, v_rectification_rate, v_avg_audio_quality
    FROM error_reports 
    WHERE speaker_id = p_speaker_id;
    
    -- Get current bucket
    SELECT bucket_type INTO v_current_bucket
    FROM speaker_bucket_history 
    WHERE speaker_id = p_speaker_id 
    ORDER BY assigned_date DESC 
    LIMIT 1;
    
    -- Update or insert performance metrics
    INSERT INTO speaker_performance_metrics (
        speaker_id, current_bucket, total_errors_reported, 
        errors_rectified, rectification_rate, average_audio_quality
    ) VALUES (
        p_speaker_id, v_current_bucket, v_total_errors,
        v_rectified_errors, v_rectification_rate, v_avg_audio_quality
    )
    ON CONFLICT (speaker_id) DO UPDATE SET
        current_bucket = EXCLUDED.current_bucket,
        total_errors_reported = EXCLUDED.total_errors_reported,
        errors_rectified = EXCLUDED.errors_rectified,
        rectification_rate = EXCLUDED.rectification_rate,
        average_audio_quality = EXCLUDED.average_audio_quality,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
```

### 2. Trigger for Automatic Metrics Update

```sql
CREATE OR REPLACE FUNCTION trigger_update_speaker_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update metrics when error report is inserted or updated
    PERFORM update_speaker_performance_metrics(NEW.speaker_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER error_reports_metrics_update
    AFTER INSERT OR UPDATE ON error_reports
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_speaker_metrics();
```

---

## Migration Scripts

### Migration from Previous Schema

```sql
-- Add new columns to existing error_reports table
ALTER TABLE error_reports ADD COLUMN IF NOT EXISTS number_of_speakers VARCHAR(10);
ALTER TABLE error_reports ADD COLUMN IF NOT EXISTS overlapping_speech BOOLEAN;
ALTER TABLE error_reports ADD COLUMN IF NOT EXISTS requires_specialized_knowledge BOOLEAN;
ALTER TABLE error_reports ADD COLUMN IF NOT EXISTS additional_notes TEXT;

-- Update bucket type values
UPDATE error_reports SET bucket_type = 'high_touch' WHERE bucket_type = 'beginner';
UPDATE error_reports SET bucket_type = 'medium_touch' WHERE bucket_type = 'intermediate';
UPDATE error_reports SET bucket_type = 'low_touch' WHERE bucket_type = 'advanced';
UPDATE error_reports SET bucket_type = 'no_touch' WHERE bucket_type = 'expert';

-- Add constraints for new fields
ALTER TABLE error_reports ADD CONSTRAINT check_number_of_speakers 
    CHECK (number_of_speakers IN ('one', 'two', 'three', 'four', 'five'));
ALTER TABLE error_reports ADD CONSTRAINT check_additional_notes_length 
    CHECK (char_length(additional_notes) <= 1000);
```
