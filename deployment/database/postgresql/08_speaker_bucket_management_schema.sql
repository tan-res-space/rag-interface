-- =====================================================
-- Speaker Bucket Management - PostgreSQL Schema Extensions
-- =====================================================
-- This script extends existing schemas for speaker bucket management functionality
-- Run this script on the rag_interface_db database after all other schemas
-- 
-- Author: RAG Interface Development Team
-- Version: 1.0 - Speaker Bucket Management Feature
-- Date: 2025-08-26
-- =====================================================

\c rag_interface_db;

-- =====================================================
-- SPEAKER MANAGEMENT EXTENSIONS (User Management Schema)
-- =====================================================

-- Set search path to user_management schema
SET search_path TO user_management, public;

-- Speaker Bucket Enum Type
CREATE TYPE user_management.speaker_bucket_type AS ENUM (
    'no_touch',
    'low_touch', 
    'medium_touch',
    'high_touch'
);

-- Speakers table
CREATE TABLE IF NOT EXISTS user_management.speakers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_identifier VARCHAR(100) NOT NULL UNIQUE, -- External speaker ID from InstaNote
    speaker_name VARCHAR(255) NOT NULL,
    current_bucket user_management.speaker_bucket_type NOT NULL DEFAULT 'high_touch',
    total_notes_count INTEGER DEFAULT 0,
    processed_notes_count INTEGER DEFAULT 0,
    average_ser_score DECIMAL(5,2), -- Average SER score for this speaker
    last_processed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}', -- Additional speaker metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for speakers
CREATE INDEX IF NOT EXISTS idx_speakers_identifier ON user_management.speakers(speaker_identifier);
CREATE INDEX IF NOT EXISTS idx_speakers_name ON user_management.speakers(speaker_name);
CREATE INDEX IF NOT EXISTS idx_speakers_bucket ON user_management.speakers(current_bucket);
CREATE INDEX IF NOT EXISTS idx_speakers_ser_score ON user_management.speakers(average_ser_score);
CREATE INDEX IF NOT EXISTS idx_speakers_last_processed ON user_management.speakers(last_processed_at);
CREATE INDEX IF NOT EXISTS idx_speakers_created_at ON user_management.speakers(created_at);

-- Speaker bucket transition history
CREATE TABLE IF NOT EXISTS user_management.speaker_bucket_transitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL REFERENCES user_management.speakers(id) ON DELETE CASCADE,
    from_bucket user_management.speaker_bucket_type,
    to_bucket user_management.speaker_bucket_type NOT NULL,
    transition_reason TEXT,
    ser_improvement DECIMAL(5,2), -- SER improvement that triggered transition
    approved_by UUID REFERENCES user_management.users(id),
    transition_data JSONB DEFAULT '{}', -- Additional transition metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for speaker_bucket_transitions
CREATE INDEX IF NOT EXISTS idx_bucket_transitions_speaker_id ON user_management.speaker_bucket_transitions(speaker_id);
CREATE INDEX IF NOT EXISTS idx_bucket_transitions_from_bucket ON user_management.speaker_bucket_transitions(from_bucket);
CREATE INDEX IF NOT EXISTS idx_bucket_transitions_to_bucket ON user_management.speaker_bucket_transitions(to_bucket);
CREATE INDEX IF NOT EXISTS idx_bucket_transitions_approved_by ON user_management.speaker_bucket_transitions(approved_by);
CREATE INDEX IF NOT EXISTS idx_bucket_transitions_created_at ON user_management.speaker_bucket_transitions(created_at);

-- Historical ASR data tracking
CREATE TABLE IF NOT EXISTS user_management.historical_asr_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL REFERENCES user_management.speakers(id) ON DELETE CASCADE,
    instanote_job_id VARCHAR(255), -- Reference to InstaNote job
    asr_draft TEXT NOT NULL,
    final_note TEXT NOT NULL,
    note_type VARCHAR(100),
    asr_engine VARCHAR(100),
    processing_date TIMESTAMP WITH TIME ZONE,
    is_test_data BOOLEAN DEFAULT false, -- Marks 2% test data
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for historical_asr_data
CREATE INDEX IF NOT EXISTS idx_historical_asr_speaker_id ON user_management.historical_asr_data(speaker_id);
CREATE INDEX IF NOT EXISTS idx_historical_asr_instanote_job ON user_management.historical_asr_data(instanote_job_id);
CREATE INDEX IF NOT EXISTS idx_historical_asr_is_test_data ON user_management.historical_asr_data(is_test_data);
CREATE INDEX IF NOT EXISTS idx_historical_asr_processing_date ON user_management.historical_asr_data(processing_date);
CREATE INDEX IF NOT EXISTS idx_historical_asr_created_at ON user_management.historical_asr_data(created_at);

-- Create trigger for speakers updated_at
CREATE TRIGGER update_speakers_updated_at
    BEFORE UPDATE ON user_management.speakers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SER CALCULATION EXTENSIONS (Verification Schema)
-- =====================================================

-- Set search path to verification schema
SET search_path TO verification, public;

-- SER calculation results
CREATE TABLE IF NOT EXISTS verification.ser_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL, -- References user_management.speakers(id)
    historical_data_id UUID, -- References user_management.historical_asr_data(id)
    asr_text TEXT NOT NULL,
    reference_text TEXT NOT NULL,
    calculation_type VARCHAR(50) NOT NULL CHECK (calculation_type IN ('original', 'rag_corrected')),
    ser_score DECIMAL(5,2) NOT NULL,
    insert_percentage DECIMAL(5,2) NOT NULL,
    delete_percentage DECIMAL(5,2) NOT NULL,
    move_percentage DECIMAL(5,2) NOT NULL,
    edit_percentage DECIMAL(5,2) NOT NULL,
    edit_distance INTEGER NOT NULL,
    reference_length INTEGER NOT NULL,
    hypothesis_length INTEGER NOT NULL,
    quality_score DECIMAL(5,2), -- Derived quality score (100 - SER)
    metadata JSONB DEFAULT '{}',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for ser_calculations
CREATE INDEX IF NOT EXISTS idx_ser_calculations_speaker_id ON verification.ser_calculations(speaker_id);
CREATE INDEX IF NOT EXISTS idx_ser_calculations_historical_data_id ON verification.ser_calculations(historical_data_id);
CREATE INDEX IF NOT EXISTS idx_ser_calculations_type ON verification.ser_calculations(calculation_type);
CREATE INDEX IF NOT EXISTS idx_ser_calculations_ser_score ON verification.ser_calculations(ser_score);
CREATE INDEX IF NOT EXISTS idx_ser_calculations_quality_score ON verification.ser_calculations(quality_score);
CREATE INDEX IF NOT EXISTS idx_ser_calculations_calculated_at ON verification.ser_calculations(calculated_at);

-- Validation test sessions for MT workflow
CREATE TABLE IF NOT EXISTS verification.validation_test_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL, -- References user_management.speakers(id)
    session_name VARCHAR(255) NOT NULL,
    test_data_count INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    mt_user_id UUID, -- References user_management.users(id) - Medical Transcriptionist
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    session_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for validation_test_sessions
CREATE INDEX IF NOT EXISTS idx_validation_sessions_speaker_id ON verification.validation_test_sessions(speaker_id);
CREATE INDEX IF NOT EXISTS idx_validation_sessions_status ON verification.validation_test_sessions(status);
CREATE INDEX IF NOT EXISTS idx_validation_sessions_mt_user_id ON verification.validation_test_sessions(mt_user_id);
CREATE INDEX IF NOT EXISTS idx_validation_sessions_started_at ON verification.validation_test_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_validation_sessions_created_at ON verification.validation_test_sessions(created_at);

-- MT feedback and validation results
CREATE TABLE IF NOT EXISTS verification.mt_validation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES verification.validation_test_sessions(id) ON DELETE CASCADE,
    historical_data_id UUID NOT NULL, -- References user_management.historical_asr_data(id)
    original_asr_text TEXT NOT NULL,
    rag_corrected_text TEXT NOT NULL,
    final_reference_text TEXT NOT NULL,
    mt_feedback_rating INTEGER CHECK (mt_feedback_rating >= 1 AND mt_feedback_rating <= 5),
    mt_comments TEXT,
    improvement_assessment VARCHAR(50) CHECK (improvement_assessment IN ('significant', 'moderate', 'minimal', 'none', 'worse')),
    recommended_for_bucket_change BOOLEAN,
    feedback_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for mt_validation_feedback
CREATE INDEX IF NOT EXISTS idx_mt_feedback_session_id ON verification.mt_validation_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_mt_feedback_historical_data_id ON verification.mt_validation_feedback(historical_data_id);
CREATE INDEX IF NOT EXISTS idx_mt_feedback_rating ON verification.mt_validation_feedback(mt_feedback_rating);
CREATE INDEX IF NOT EXISTS idx_mt_feedback_improvement ON verification.mt_validation_feedback(improvement_assessment);
CREATE INDEX IF NOT EXISTS idx_mt_feedback_bucket_change ON verification.mt_validation_feedback(recommended_for_bucket_change);
CREATE INDEX IF NOT EXISTS idx_mt_feedback_created_at ON verification.mt_validation_feedback(created_at);

-- =====================================================
-- RAG PROCESSING EXTENSIONS (RAG Integration Schema)
-- =====================================================

-- Set search path to rag_integration schema
SET search_path TO rag_integration, public;

-- Error-correction pairs for speaker-specific RAG training
CREATE TABLE IF NOT EXISTS rag_integration.speaker_error_correction_pairs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL, -- References user_management.speakers(id)
    historical_data_id UUID NOT NULL, -- References user_management.historical_asr_data(id)
    error_text TEXT NOT NULL,
    correction_text TEXT NOT NULL,
    error_type VARCHAR(100),
    context_before TEXT,
    context_after TEXT,
    confidence_score DECIMAL(5,4),
    embedding_id UUID, -- References embedding_metadata(id)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for speaker_error_correction_pairs
CREATE INDEX IF NOT EXISTS idx_speaker_error_pairs_speaker_id ON rag_integration.speaker_error_correction_pairs(speaker_id);
CREATE INDEX IF NOT EXISTS idx_speaker_error_pairs_historical_data_id ON rag_integration.speaker_error_correction_pairs(historical_data_id);
CREATE INDEX IF NOT EXISTS idx_speaker_error_pairs_error_type ON rag_integration.speaker_error_correction_pairs(error_type);
CREATE INDEX IF NOT EXISTS idx_speaker_error_pairs_confidence ON rag_integration.speaker_error_correction_pairs(confidence_score);
CREATE INDEX IF NOT EXISTS idx_speaker_error_pairs_embedding_id ON rag_integration.speaker_error_correction_pairs(embedding_id);
CREATE INDEX IF NOT EXISTS idx_speaker_error_pairs_created_at ON rag_integration.speaker_error_correction_pairs(created_at);

-- Speaker-specific RAG processing jobs
CREATE TABLE IF NOT EXISTS rag_integration.speaker_rag_processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL, -- References user_management.speakers(id)
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('historical_analysis', 'error_pair_generation', 'vectorization', 'rag_correction')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    total_records INTEGER,
    processed_records INTEGER DEFAULT 0,
    error_records INTEGER DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    error_message TEXT,
    job_metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for speaker_rag_processing_jobs
CREATE INDEX IF NOT EXISTS idx_speaker_rag_jobs_speaker_id ON rag_integration.speaker_rag_processing_jobs(speaker_id);
CREATE INDEX IF NOT EXISTS idx_speaker_rag_jobs_type ON rag_integration.speaker_rag_processing_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_speaker_rag_jobs_status ON rag_integration.speaker_rag_processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_speaker_rag_jobs_started_at ON rag_integration.speaker_rag_processing_jobs(started_at);
CREATE INDEX IF NOT EXISTS idx_speaker_rag_jobs_created_at ON rag_integration.speaker_rag_processing_jobs(created_at);

-- Extend embedding_metadata table for speaker-specific embeddings
ALTER TABLE rag_integration.embedding_metadata
ADD COLUMN IF NOT EXISTS speaker_id UUID,
ADD COLUMN IF NOT EXISTS error_correction_pair_id UUID,
ADD COLUMN IF NOT EXISTS is_speaker_specific BOOLEAN DEFAULT false;

-- Create indexes for new speaker-specific columns
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_speaker_id ON rag_integration.embedding_metadata(speaker_id);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_error_pair_id ON rag_integration.embedding_metadata(error_correction_pair_id);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_is_speaker_specific ON rag_integration.embedding_metadata(is_speaker_specific);

-- =====================================================
-- CORRECTION ENGINE EXTENSIONS (Correction Engine Schema)
-- =====================================================

-- Set search path to correction_engine schema
SET search_path TO correction_engine, public;

-- Speaker-specific correction patterns
CREATE TABLE IF NOT EXISTS correction_engine.speaker_correction_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    speaker_id UUID NOT NULL, -- References user_management.speakers(id)
    pattern_type VARCHAR(100) NOT NULL,
    pattern_text TEXT NOT NULL,
    correction_text TEXT NOT NULL,
    frequency_count INTEGER DEFAULT 1,
    success_rate DECIMAL(5,4),
    confidence_score DECIMAL(5,4),
    last_used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    pattern_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for speaker_correction_patterns
CREATE INDEX IF NOT EXISTS idx_speaker_patterns_speaker_id ON correction_engine.speaker_correction_patterns(speaker_id);
CREATE INDEX IF NOT EXISTS idx_speaker_patterns_type ON correction_engine.speaker_correction_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_speaker_patterns_frequency ON correction_engine.speaker_correction_patterns(frequency_count);
CREATE INDEX IF NOT EXISTS idx_speaker_patterns_success_rate ON correction_engine.speaker_correction_patterns(success_rate);
CREATE INDEX IF NOT EXISTS idx_speaker_patterns_is_active ON correction_engine.speaker_correction_patterns(is_active);
CREATE INDEX IF NOT EXISTS idx_speaker_patterns_created_at ON correction_engine.speaker_correction_patterns(created_at);

-- Create trigger for speaker_correction_patterns updated_at
CREATE TRIGGER update_speaker_patterns_updated_at
    BEFORE UPDATE ON correction_engine.speaker_correction_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Set search path back to user_management for utility functions
SET search_path TO user_management, public;

-- Function to calculate speaker bucket recommendation based on SER scores
CREATE OR REPLACE FUNCTION calculate_speaker_bucket_recommendation(
    p_speaker_id UUID,
    p_average_ser_score DECIMAL(5,2)
) RETURNS user_management.speaker_bucket_type AS $$
DECLARE
    recommended_bucket user_management.speaker_bucket_type;
BEGIN
    -- Bucket recommendation logic based on SER scores
    -- Lower SER scores indicate better quality
    IF p_average_ser_score IS NULL THEN
        RETURN 'high_touch';
    ELSIF p_average_ser_score <= 5.0 THEN
        recommended_bucket := 'no_touch';
    ELSIF p_average_ser_score <= 15.0 THEN
        recommended_bucket := 'low_touch';
    ELSIF p_average_ser_score <= 30.0 THEN
        recommended_bucket := 'medium_touch';
    ELSE
        recommended_bucket := 'high_touch';
    END IF;

    RETURN recommended_bucket;
END;
$$ LANGUAGE plpgsql;

-- Function to update speaker statistics
CREATE OR REPLACE FUNCTION update_speaker_statistics(p_speaker_id UUID)
RETURNS VOID AS $$
DECLARE
    v_total_count INTEGER;
    v_processed_count INTEGER;
    v_avg_ser DECIMAL(5,2);
BEGIN
    -- Calculate total notes count
    SELECT COUNT(*) INTO v_total_count
    FROM user_management.historical_asr_data
    WHERE speaker_id = p_speaker_id;

    -- Calculate processed notes count (those with SER calculations)
    SELECT COUNT(DISTINCT had.id) INTO v_processed_count
    FROM user_management.historical_asr_data had
    INNER JOIN verification.ser_calculations sc ON had.id = sc.historical_data_id
    WHERE had.speaker_id = p_speaker_id;

    -- Calculate average SER score
    SELECT AVG(sc.ser_score) INTO v_avg_ser
    FROM user_management.historical_asr_data had
    INNER JOIN verification.ser_calculations sc ON had.id = sc.historical_data_id
    WHERE had.speaker_id = p_speaker_id
    AND sc.calculation_type = 'original';

    -- Update speaker record
    UPDATE user_management.speakers
    SET
        total_notes_count = v_total_count,
        processed_notes_count = v_processed_count,
        average_ser_score = v_avg_ser,
        updated_at = NOW()
    WHERE id = p_speaker_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TYPE user_management.speaker_bucket_type IS 'Enum for speaker quality buckets: no_touch (highest quality), low_touch, medium_touch, high_touch (lowest quality)';

COMMENT ON TABLE user_management.speakers IS 'Speaker entities with bucket categorization and quality metrics';
COMMENT ON TABLE user_management.speaker_bucket_transitions IS 'History of speaker bucket transitions with approval tracking';
COMMENT ON TABLE user_management.historical_asr_data IS 'Historical ASR drafts and final notes for speaker analysis';

COMMENT ON TABLE verification.ser_calculations IS 'SER (Sentence Edit Rate) calculation results for quality assessment';
COMMENT ON TABLE verification.validation_test_sessions IS 'MT validation sessions for speaker bucket evaluation';
COMMENT ON TABLE verification.mt_validation_feedback IS 'Medical transcriptionist feedback on RAG corrections';

COMMENT ON TABLE rag_integration.speaker_error_correction_pairs IS 'Error-correction pairs extracted from speaker historical data for RAG training';
COMMENT ON TABLE rag_integration.speaker_rag_processing_jobs IS 'Background jobs for speaker-specific RAG processing';

COMMENT ON TABLE correction_engine.speaker_correction_patterns IS 'Speaker-specific correction patterns learned from historical data';

COMMENT ON FUNCTION calculate_speaker_bucket_recommendation(UUID, DECIMAL) IS 'Calculate recommended speaker bucket based on average SER score';
COMMENT ON FUNCTION update_speaker_statistics(UUID) IS 'Update speaker statistics including note counts and average SER score';

-- =====================================================
-- SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample speaker bucket permissions
INSERT INTO user_management.permissions (name, description, resource, action) VALUES
('speaker_management.read', 'View speaker information and bucket status', 'speakers', 'read'),
('speaker_management.write', 'Manage speaker bucket assignments', 'speakers', 'write'),
('speaker_bucket.transition', 'Approve speaker bucket transitions', 'speaker_buckets', 'transition'),
('mt_validation.participate', 'Participate in MT validation sessions', 'validation_sessions', 'participate'),
('ser_calculations.view', 'View SER calculation results', 'ser_calculations', 'read')
ON CONFLICT (name) DO NOTHING;

-- Assign permissions to roles
INSERT INTO user_management.role_permissions (role, permission_id)
SELECT 'admin', id FROM user_management.permissions WHERE name IN (
    'speaker_management.read', 'speaker_management.write', 'speaker_bucket.transition',
    'mt_validation.participate', 'ser_calculations.view'
)
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO user_management.role_permissions (role, permission_id)
SELECT 'qa_supervisor', id FROM user_management.permissions WHERE name IN (
    'speaker_management.read', 'speaker_bucket.transition', 'ser_calculations.view'
)
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO user_management.role_permissions (role, permission_id)
SELECT 'mts_personnel', id FROM user_management.permissions WHERE name IN (
    'speaker_management.read', 'mt_validation.participate', 'ser_calculations.view'
)
ON CONFLICT (role, permission_id) DO NOTHING;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=======================================================';
    RAISE NOTICE 'Speaker Bucket Management Schema Created Successfully';
    RAISE NOTICE '=======================================================';
    RAISE NOTICE 'Extensions added to existing schemas:';
    RAISE NOTICE '';
    RAISE NOTICE 'User Management Schema:';
    RAISE NOTICE '  - speakers (with 6 indexes)';
    RAISE NOTICE '  - speaker_bucket_transitions (with 5 indexes)';
    RAISE NOTICE '  - historical_asr_data (with 5 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Verification Schema:';
    RAISE NOTICE '  - ser_calculations (with 6 indexes)';
    RAISE NOTICE '  - validation_test_sessions (with 5 indexes)';
    RAISE NOTICE '  - mt_validation_feedback (with 6 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'RAG Integration Schema:';
    RAISE NOTICE '  - speaker_error_correction_pairs (with 6 indexes)';
    RAISE NOTICE '  - speaker_rag_processing_jobs (with 5 indexes)';
    RAISE NOTICE '  - embedding_metadata extended (with 3 new indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Correction Engine Schema:';
    RAISE NOTICE '  - speaker_correction_patterns (with 6 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - calculate_speaker_bucket_recommendation()';
    RAISE NOTICE '  - update_speaker_statistics()';
    RAISE NOTICE '';
    RAISE NOTICE 'Permissions and roles configured for speaker bucket management';
    RAISE NOTICE '=======================================================';
END
$$;
