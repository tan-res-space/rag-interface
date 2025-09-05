-- Enhanced Metadata Migration for Quality-Based Speaker Bucket Management
-- Migration: 001_enhanced_metadata_migration
-- Date: 2024-12-19
-- Description: Add enhanced metadata fields and quality-based bucket system

BEGIN;

-- Add new columns to error_reports table
ALTER TABLE error_reports 
ADD COLUMN IF NOT EXISTS client_id UUID,
ADD COLUMN IF NOT EXISTS bucket_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS audio_quality VARCHAR(20),
ADD COLUMN IF NOT EXISTS speaker_clarity VARCHAR(30),
ADD COLUMN IF NOT EXISTS background_noise VARCHAR(20),
ADD COLUMN IF NOT EXISTS number_of_speakers VARCHAR(10),
ADD COLUMN IF NOT EXISTS overlapping_speech BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS requires_specialized_knowledge BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS additional_notes TEXT,
ADD COLUMN IF NOT EXISTS vector_db_id VARCHAR(255);

-- Update bucket type values from progression-based to quality-based
UPDATE error_reports 
SET bucket_type = CASE 
    WHEN bucket_type = 'beginner' THEN 'high_touch'
    WHEN bucket_type = 'intermediate' THEN 'medium_touch'
    WHEN bucket_type = 'advanced' THEN 'low_touch'
    WHEN bucket_type = 'expert' THEN 'no_touch'
    ELSE bucket_type
END
WHERE bucket_type IN ('beginner', 'intermediate', 'advanced', 'expert');

-- Update status values
UPDATE error_reports 
SET status = CASE 
    WHEN status = 'pending' THEN 'submitted'
    WHEN status = 'processed' THEN 'rectified'
    WHEN status = 'archived' THEN 'verified'
    ELSE status
END
WHERE status IN ('pending', 'processed', 'archived');

-- Add constraints for enhanced metadata fields
ALTER TABLE error_reports 
ADD CONSTRAINT check_bucket_type 
CHECK (bucket_type IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch'));

ALTER TABLE error_reports 
ADD CONSTRAINT check_audio_quality 
CHECK (audio_quality IN ('good', 'fair', 'poor'));

ALTER TABLE error_reports 
ADD CONSTRAINT check_speaker_clarity 
CHECK (speaker_clarity IN ('clear', 'somewhat_clear', 'unclear', 'very_unclear'));

ALTER TABLE error_reports 
ADD CONSTRAINT check_background_noise 
CHECK (background_noise IN ('none', 'low', 'medium', 'high'));

ALTER TABLE error_reports 
ADD CONSTRAINT check_number_of_speakers 
CHECK (number_of_speakers IN ('one', 'two', 'three', 'four', 'five'));

ALTER TABLE error_reports 
ADD CONSTRAINT check_status 
CHECK (status IN ('submitted', 'processing', 'rectified', 'verified', 'rejected'));

ALTER TABLE error_reports 
ADD CONSTRAINT check_additional_notes_length 
CHECK (char_length(additional_notes) <= 1000);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_error_reports_bucket_type ON error_reports(bucket_type);
CREATE INDEX IF NOT EXISTS idx_error_reports_client_id ON error_reports(client_id);
CREATE INDEX IF NOT EXISTS idx_error_reports_audio_quality ON error_reports(audio_quality);
CREATE INDEX IF NOT EXISTS idx_error_reports_requires_specialized_knowledge ON error_reports(requires_specialized_knowledge);
CREATE INDEX IF NOT EXISTS idx_error_reports_overlapping_speech ON error_reports(overlapping_speech);
CREATE INDEX IF NOT EXISTS idx_error_reports_number_of_speakers ON error_reports(number_of_speakers);

-- Create speaker_bucket_history table
CREATE TABLE IF NOT EXISTS speaker_bucket_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL,
    bucket_type VARCHAR(20) NOT NULL CHECK (bucket_type IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch')),
    previous_bucket VARCHAR(20) CHECK (previous_bucket IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch')),
    assigned_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    assigned_by UUID NOT NULL,
    assignment_reason TEXT NOT NULL,
    assignment_type VARCHAR(20) NOT NULL DEFAULT 'manual' CHECK (assignment_type IN ('manual', 'automatic', 'system')),
    
    -- Performance metrics at time of assignment
    error_count_at_assignment INTEGER DEFAULT 0,
    rectification_rate_at_assignment DECIMAL(5,4),
    quality_score_at_assignment DECIMAL(5,4),
    confidence_score DECIMAL(5,4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for speaker_bucket_history
CREATE INDEX IF NOT EXISTS idx_speaker_bucket_history_speaker_id ON speaker_bucket_history(speaker_id);
CREATE INDEX IF NOT EXISTS idx_speaker_bucket_history_assigned_date ON speaker_bucket_history(assigned_date);
CREATE INDEX IF NOT EXISTS idx_speaker_bucket_history_bucket_type ON speaker_bucket_history(bucket_type);

-- Create speaker_performance_metrics table
CREATE TABLE IF NOT EXISTS speaker_performance_metrics (
    metrics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL UNIQUE,
    current_bucket VARCHAR(20) NOT NULL CHECK (current_bucket IN ('no_touch', 'low_touch', 'medium_touch', 'high_touch')),
    
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
    
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for speaker_performance_metrics
CREATE INDEX IF NOT EXISTS idx_speaker_performance_speaker_id ON speaker_performance_metrics(speaker_id);
CREATE INDEX IF NOT EXISTS idx_speaker_performance_bucket ON speaker_performance_metrics(current_bucket);
CREATE INDEX IF NOT EXISTS idx_speaker_performance_trend ON speaker_performance_metrics(quality_trend);

-- Create verification_jobs table
CREATE TABLE IF NOT EXISTS verification_jobs (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) NOT NULL, -- InstaNote job ID
    speaker_id UUID NOT NULL,
    error_report_id UUID REFERENCES error_reports(error_id),
    
    -- Job content
    original_draft TEXT NOT NULL,
    rag_corrected_draft TEXT,
    corrections_applied JSONB DEFAULT '[]'::jsonb,
    
    -- Verification details
    verification_status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'not_rectified', 'partially_rectified')),
    verification_result VARCHAR(30) CHECK (verification_result IN ('rectified', 'not_rectified', 'partially_rectified', 'not_applicable')),
    qa_comments TEXT,
    verified_by UUID,
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Job metadata from InstaNote
    job_metadata JSONB DEFAULT '{}'::jsonb,
    retrieval_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for verification_jobs
CREATE INDEX IF NOT EXISTS idx_verification_jobs_speaker_id ON verification_jobs(speaker_id);
CREATE INDEX IF NOT EXISTS idx_verification_jobs_status ON verification_jobs(verification_status);
CREATE INDEX IF NOT EXISTS idx_verification_jobs_job_id ON verification_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_verification_jobs_error_report_id ON verification_jobs(error_report_id);

-- Create system_configuration table for bucket thresholds and settings
CREATE TABLE IF NOT EXISTS system_configuration (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default configurations
INSERT INTO system_configuration (config_key, config_value, description, category, created_by) VALUES
('bucket_thresholds', '{"no_touch": {"error_rate": 0.02}, "low_touch": {"error_rate": 0.05}, "medium_touch": {"error_rate": 0.10}, "high_touch": {"error_rate": 0.20}}'::jsonb, 'Error rate thresholds for bucket classification', 'bucket_management', gen_random_uuid()),
('verification_settings', '{"auto_pull_jobs": true, "max_jobs_per_pull": 10, "verification_window_days": 7}'::jsonb, 'Settings for verification workflow', 'verification', gen_random_uuid()),
('metadata_validation', '{"required_fields": ["audio_quality", "speaker_clarity", "background_noise", "number_of_speakers", "overlapping_speech", "requires_specialized_knowledge"], "max_additional_notes_length": 1000}'::jsonb, 'Metadata validation rules', 'validation', gen_random_uuid())
ON CONFLICT (config_key) DO NOTHING;

-- Create views for analytics
CREATE OR REPLACE VIEW speaker_bucket_distribution AS
SELECT 
    current_bucket,
    COUNT(*) as speaker_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage,
    AVG(rectification_rate) as avg_rectification_rate,
    AVG(EXTRACT(EPOCH FROM time_in_current_bucket) / 86400) as avg_days_in_bucket
FROM speaker_performance_metrics 
GROUP BY current_bucket;

CREATE OR REPLACE VIEW error_reporting_trends AS
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

-- Create stored procedure for updating speaker performance metrics
CREATE OR REPLACE FUNCTION update_speaker_performance_metrics(p_speaker_id UUID)
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

-- Create trigger for automatic metrics update
CREATE OR REPLACE FUNCTION trigger_update_speaker_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update metrics when error report is inserted or updated
    PERFORM update_speaker_performance_metrics(NEW.speaker_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS error_reports_metrics_update ON error_reports;
CREATE TRIGGER error_reports_metrics_update
    AFTER INSERT OR UPDATE ON error_reports
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_speaker_metrics();

COMMIT;
