-- =====================================================
-- Error Reporting Service - PostgreSQL Schema
-- =====================================================
-- This script creates the complete schema for the Error Reporting Service
-- Run this script on the error_reporting_db database as ers_user
-- 
-- Author: RAG Interface Deployment Team
-- Version: 1.0
-- Date: 2025-01-20
-- =====================================================

\c error_reporting_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- ERROR REPORTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS error_reports (
    error_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL,
    speaker_id UUID NOT NULL,
    reported_by UUID NOT NULL,
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    error_categories JSONB NOT NULL DEFAULT '[]',
    severity_level VARCHAR(20) NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    start_position INTEGER NOT NULL CHECK (start_position >= 0),
    end_position INTEGER NOT NULL CHECK (end_position > start_position),
    context_notes TEXT,
    error_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    reported_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved', 'rejected')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Create indexes for error_reports
CREATE INDEX IF NOT EXISTS idx_error_reports_job_id ON error_reports(job_id);
CREATE INDEX IF NOT EXISTS idx_error_reports_speaker_id ON error_reports(speaker_id);
CREATE INDEX IF NOT EXISTS idx_error_reports_reported_by ON error_reports(reported_by);
CREATE INDEX IF NOT EXISTS idx_error_reports_severity_level ON error_reports(severity_level);
CREATE INDEX IF NOT EXISTS idx_error_reports_status ON error_reports(status);
CREATE INDEX IF NOT EXISTS idx_error_reports_reported_at ON error_reports(reported_at);
CREATE INDEX IF NOT EXISTS idx_error_reports_error_timestamp ON error_reports(error_timestamp);

-- =====================================================
-- ERROR AUDIT LOGS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS error_audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    error_id UUID NOT NULL REFERENCES error_reports(error_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    performed_by UUID NOT NULL,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    reason TEXT
);

-- Create indexes for error_audit_logs
CREATE INDEX IF NOT EXISTS idx_error_audit_logs_error_id ON error_audit_logs(error_id);
CREATE INDEX IF NOT EXISTS idx_error_audit_logs_action_type ON error_audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_error_audit_logs_performed_by ON error_audit_logs(performed_by);
CREATE INDEX IF NOT EXISTS idx_error_audit_logs_performed_at ON error_audit_logs(performed_at);

-- =====================================================
-- ERROR VALIDATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS error_validations (
    validation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    error_id UUID NOT NULL REFERENCES error_reports(error_id) ON DELETE CASCADE,
    validation_type VARCHAR(50) NOT NULL,
    is_valid BOOLEAN NOT NULL,
    validation_details JSONB DEFAULT '{}',
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validated_by UUID NOT NULL
);

-- Create indexes for error_validations
CREATE INDEX IF NOT EXISTS idx_error_validations_error_id ON error_validations(error_id);
CREATE INDEX IF NOT EXISTS idx_error_validations_validation_type ON error_validations(validation_type);
CREATE INDEX IF NOT EXISTS idx_error_validations_is_valid ON error_validations(is_valid);
CREATE INDEX IF NOT EXISTS idx_error_validations_validated_by ON error_validations(validated_by);

-- =====================================================
-- ERROR CATEGORIES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS error_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for error_categories
CREATE INDEX IF NOT EXISTS idx_error_categories_category_name ON error_categories(category_name);
CREATE INDEX IF NOT EXISTS idx_error_categories_is_active ON error_categories(is_active);
CREATE INDEX IF NOT EXISTS idx_error_categories_sort_order ON error_categories(sort_order);

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
CREATE TRIGGER update_error_reports_updated_at 
    BEFORE UPDATE ON error_reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_error_categories_updated_at 
    BEFORE UPDATE ON error_categories 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE error_reports IS 'Main table storing error reports submitted by QA personnel';
COMMENT ON TABLE error_audit_logs IS 'Audit trail for all changes made to error reports';
COMMENT ON TABLE error_validations IS 'Validation results for error reports';
COMMENT ON TABLE error_categories IS 'Master list of error categories available in the system';

COMMENT ON COLUMN error_reports.error_id IS 'Unique identifier for the error report';
COMMENT ON COLUMN error_reports.job_id IS 'Reference to the ASR job where the error was found';
COMMENT ON COLUMN error_reports.speaker_id IS 'Reference to the speaker in the audio file';
COMMENT ON COLUMN error_reports.reported_by IS 'User ID of the QA personnel who reported the error';
COMMENT ON COLUMN error_reports.original_text IS 'Original text from ASR output containing the error';
COMMENT ON COLUMN error_reports.corrected_text IS 'Corrected version of the text';
COMMENT ON COLUMN error_reports.error_categories IS 'JSON array of error category names';
COMMENT ON COLUMN error_reports.severity_level IS 'Impact level of the error (low, medium, high, critical)';
COMMENT ON COLUMN error_reports.start_position IS 'Character position where the error starts';
COMMENT ON COLUMN error_reports.end_position IS 'Character position where the error ends';
COMMENT ON COLUMN error_reports.context_notes IS 'Additional context or notes about the error';
COMMENT ON COLUMN error_reports.error_timestamp IS 'When the error occurred in the original audio';
COMMENT ON COLUMN error_reports.reported_at IS 'When the error was reported to the system';
COMMENT ON COLUMN error_reports.status IS 'Current processing status of the error report';
COMMENT ON COLUMN error_reports.metadata IS 'Additional metadata in JSON format';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Error Reporting Service Schema Created Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - error_reports (with 8 indexes)';
    RAISE NOTICE '  - error_audit_logs (with 4 indexes)';
    RAISE NOTICE '  - error_validations (with 4 indexes)';
    RAISE NOTICE '  - error_categories (with 3 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created:';
    RAISE NOTICE '  - update_error_reports_updated_at';
    RAISE NOTICE '  - update_error_categories_updated_at';
    RAISE NOTICE '=================================================';
END
$$;
