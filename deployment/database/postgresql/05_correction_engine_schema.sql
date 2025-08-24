-- =====================================================
-- Correction Engine Service - PostgreSQL Schema
-- =====================================================
-- This script creates the complete schema for the Correction Engine Service
-- Run this script on the rag_interface_db database as ces_user
-- 
-- Author: RAG Interface Deployment Team
-- Version: 2.0 - Single Database with Schema Separation
-- Date: 2025-01-20
-- =====================================================

\c rag_interface_db;

-- Set search path to the correction_engine schema
SET search_path TO correction_engine, public;

-- =====================================================
-- CORRECTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS correction_engine.corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255),
    speaker_id VARCHAR(255),
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    processing_time DECIMAL(8,3) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL
);

-- Create indexes for corrections
CREATE INDEX IF NOT EXISTS idx_corrections_job_id ON correction_engine.corrections(job_id);
CREATE INDEX IF NOT EXISTS idx_corrections_speaker_id ON correction_engine.corrections(speaker_id);
CREATE INDEX IF NOT EXISTS idx_corrections_confidence_score ON correction_engine.corrections(confidence_score);
CREATE INDEX IF NOT EXISTS idx_corrections_created_at ON correction_engine.corrections(created_at);
CREATE INDEX IF NOT EXISTS idx_corrections_created_by ON correction_engine.corrections(created_by);

-- =====================================================
-- APPLIED CORRECTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS correction_engine.applied_corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correction_id UUID NOT NULL REFERENCES correction_engine.corrections(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    start_position INTEGER NOT NULL CHECK (start_position >= 0),
    end_position INTEGER NOT NULL CHECK (end_position > start_position),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    pattern_id VARCHAR(255),
    correction_type VARCHAR(50) NOT NULL,
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for applied_corrections
CREATE INDEX IF NOT EXISTS idx_applied_corrections_correction_id ON correction_engine.applied_corrections(correction_id);
CREATE INDEX IF NOT EXISTS idx_applied_corrections_pattern_id ON correction_engine.applied_corrections(pattern_id);
CREATE INDEX IF NOT EXISTS idx_applied_corrections_correction_type ON correction_engine.applied_corrections(correction_type);
CREATE INDEX IF NOT EXISTS idx_applied_corrections_confidence_score ON correction_engine.applied_corrections(confidence_score);
CREATE INDEX IF NOT EXISTS idx_applied_corrections_created_at ON correction_engine.applied_corrections(created_at);

-- =====================================================
-- CORRECTION FEEDBACK TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS correction_engine.correction_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correction_id UUID NOT NULL REFERENCES correction_engine.corrections(id) ON DELETE CASCADE,
    is_correct BOOLEAN NOT NULL,
    user_correction TEXT,
    feedback_notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for correction_feedback
CREATE INDEX IF NOT EXISTS idx_correction_feedback_correction_id ON correction_engine.correction_feedback(correction_id);
CREATE INDEX IF NOT EXISTS idx_correction_feedback_is_correct ON correction_engine.correction_feedback(is_correct);
CREATE INDEX IF NOT EXISTS idx_correction_feedback_rating ON correction_engine.correction_feedback(rating);
CREATE INDEX IF NOT EXISTS idx_correction_feedback_user_id ON correction_engine.correction_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_correction_feedback_created_at ON correction_engine.correction_feedback(created_at);

-- =====================================================
-- CORRECTION PATTERNS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS correction_engine.correction_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_hash VARCHAR(64) NOT NULL UNIQUE,
    pattern_text TEXT NOT NULL,
    correction_text TEXT NOT NULL,
    success_rate DECIMAL(5,4) DEFAULT 0.0 CHECK (success_rate >= 0 AND success_rate <= 1),
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    avg_confidence DECIMAL(5,4) DEFAULT 0.0 CHECK (avg_confidence >= 0 AND avg_confidence <= 1),
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for correction_patterns
CREATE INDEX IF NOT EXISTS idx_correction_patterns_pattern_hash ON correction_engine.correction_patterns(pattern_hash);
CREATE INDEX IF NOT EXISTS idx_correction_patterns_success_rate ON correction_engine.correction_patterns(success_rate);
CREATE INDEX IF NOT EXISTS idx_correction_patterns_usage_count ON correction_engine.correction_patterns(usage_count);
CREATE INDEX IF NOT EXISTS idx_correction_patterns_last_used ON correction_engine.correction_patterns(last_used);
CREATE INDEX IF NOT EXISTS idx_correction_patterns_created_at ON correction_engine.correction_patterns(created_at);

-- =====================================================
-- CORRECTION METRICS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS correction_engine.correction_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL,
    time_period VARCHAR(20) NOT NULL,
    metric_data JSONB NOT NULL DEFAULT '{}',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for correction_metrics
CREATE INDEX IF NOT EXISTS idx_correction_metrics_metric_type ON correction_engine.correction_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_correction_metrics_time_period ON correction_engine.correction_metrics(time_period);
CREATE INDEX IF NOT EXISTS idx_correction_metrics_calculated_at ON correction_engine.correction_metrics(calculated_at);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_correction_patterns_updated_at 
    BEFORE UPDATE ON correction_engine.correction_patterns 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- PATTERN MANAGEMENT FUNCTIONS
-- =====================================================

-- Function to update pattern statistics
CREATE OR REPLACE FUNCTION update_pattern_stats(
    p_pattern_id UUID,
    p_success BOOLEAN,
    p_confidence DECIMAL(5,4)
)
RETURNS VOID AS $$
DECLARE
    current_count INTEGER;
    current_avg DECIMAL(5,4);
    current_success_rate DECIMAL(5,4);
BEGIN
    -- Get current statistics
    SELECT usage_count, avg_confidence, success_rate 
    INTO current_count, current_avg, current_success_rate
    FROM correction_engine.correction_patterns 
    WHERE id = p_pattern_id;
    
    -- Update statistics
    UPDATE correction_engine.correction_patterns 
    SET 
        usage_count = current_count + 1,
        avg_confidence = ((current_avg * current_count) + p_confidence) / (current_count + 1),
        success_rate = CASE 
            WHEN p_success THEN ((current_success_rate * current_count) + 1) / (current_count + 1)
            ELSE (current_success_rate * current_count) / (current_count + 1)
        END,
        last_used = NOW(),
        updated_at = NOW()
    WHERE id = p_pattern_id;
END;
$$ LANGUAGE plpgsql;

-- Function to generate pattern hash
CREATE OR REPLACE FUNCTION generate_pattern_hash(pattern_text TEXT)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(pattern_text, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE correction_engine.corrections IS 'Main table storing correction operations and results';
COMMENT ON TABLE correction_engine.applied_corrections IS 'Individual corrections applied within a correction operation';
COMMENT ON TABLE correction_engine.correction_feedback IS 'User feedback on correction quality and accuracy';
COMMENT ON TABLE correction_engine.correction_patterns IS 'Learned patterns for text corrections with success metrics';
COMMENT ON TABLE correction_engine.correction_metrics IS 'Performance metrics for the correction engine';

COMMENT ON COLUMN correction_engine.corrections.id IS 'Unique identifier for the correction operation';
COMMENT ON COLUMN correction_engine.corrections.job_id IS 'Reference to the ASR job being corrected';
COMMENT ON COLUMN correction_engine.corrections.speaker_id IS 'Reference to the speaker in the audio file';
COMMENT ON COLUMN correction_engine.corrections.original_text IS 'Original text before correction';
COMMENT ON COLUMN correction_engine.corrections.corrected_text IS 'Text after applying corrections';
COMMENT ON COLUMN correction_engine.corrections.confidence_score IS 'Overall confidence in the correction quality';
COMMENT ON COLUMN correction_engine.corrections.processing_time IS 'Time taken to process the correction in seconds';

COMMENT ON FUNCTION update_pattern_stats(UUID, BOOLEAN, DECIMAL) IS 'Updates usage statistics for a correction pattern';
COMMENT ON FUNCTION generate_pattern_hash(TEXT) IS 'Generates SHA256 hash for pattern deduplication';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Correction Engine Service Schema Created Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables created in correction_engine schema:';
    RAISE NOTICE '  - corrections (with 5 indexes)';
    RAISE NOTICE '  - applied_corrections (with 5 indexes)';
    RAISE NOTICE '  - correction_feedback (with 5 indexes)';
    RAISE NOTICE '  - correction_patterns (with 5 indexes)';
    RAISE NOTICE '  - correction_metrics (with 3 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - update_pattern_stats()';
    RAISE NOTICE '  - generate_pattern_hash()';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created:';
    RAISE NOTICE '  - update_correction_patterns_updated_at';
    RAISE NOTICE '=================================================';
END
$$;
