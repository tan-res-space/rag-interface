-- =====================================================
-- Verification Service - PostgreSQL Schema
-- =====================================================
-- This script creates the complete schema for the Verification Service
-- Run this script on the rag_interface_db database as vs_user
-- 
-- Author: RAG Interface Deployment Team
-- Version: 2.0 - Single Database with Schema Separation
-- Date: 2025-01-20
-- =====================================================

\c rag_interface_db;

-- Set search path to the verification schema
SET search_path TO verification, public;

-- =====================================================
-- VERIFICATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS verification.verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correction_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'needs_review')),
    feedback TEXT,
    quality_score INTEGER CHECK (quality_score >= 1 AND quality_score <= 5),
    notes TEXT,
    verified_by VARCHAR(255) NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for verifications
CREATE INDEX IF NOT EXISTS idx_verifications_correction_id ON verification.verifications(correction_id);
CREATE INDEX IF NOT EXISTS idx_verifications_status ON verification.verifications(status);
CREATE INDEX IF NOT EXISTS idx_verifications_verified_by ON verification.verifications(verified_by);
CREATE INDEX IF NOT EXISTS idx_verifications_verified_at ON verification.verifications(verified_at);
CREATE INDEX IF NOT EXISTS idx_verifications_created_at ON verification.verifications(created_at);

-- =====================================================
-- ANALYTICS METRICS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS verification.analytics_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    time_period VARCHAR(20) NOT NULL,
    metric_data JSONB NOT NULL DEFAULT '{}',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create indexes for analytics_metrics
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_metric_name ON verification.analytics_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_metric_type ON verification.analytics_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_time_period ON verification.analytics_metrics(time_period);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_calculated_at ON verification.analytics_metrics(calculated_at);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_period_start ON verification.analytics_metrics(period_start);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_period_end ON verification.analytics_metrics(period_end);

-- =====================================================
-- QUALITY ASSESSMENTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS verification.quality_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correction_id UUID NOT NULL,
    accuracy_score DECIMAL(5,4) CHECK (accuracy_score >= 0 AND accuracy_score <= 1),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    improvement_ratio DECIMAL(5,4) CHECK (improvement_ratio >= 0),
    quality_details JSONB DEFAULT '{}',
    assessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for quality_assessments
CREATE INDEX IF NOT EXISTS idx_quality_assessments_correction_id ON verification.quality_assessments(correction_id);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_accuracy_score ON verification.quality_assessments(accuracy_score);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_confidence_score ON verification.quality_assessments(confidence_score);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_assessed_at ON verification.quality_assessments(assessed_at);

-- =====================================================
-- DASHBOARD CACHE TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS verification.dashboard_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    cache_data JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for dashboard_cache
CREATE INDEX IF NOT EXISTS idx_dashboard_cache_expires_at ON verification.dashboard_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_dashboard_cache_created_at ON verification.dashboard_cache(created_at);

-- =====================================================
-- REPORTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS verification.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    format VARCHAR(20) NOT NULL CHECK (format IN ('pdf', 'excel', 'csv', 'json')),
    filters JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    file_path VARCHAR(500),
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for reports
CREATE INDEX IF NOT EXISTS idx_reports_name ON verification.reports(name);
CREATE INDEX IF NOT EXISTS idx_reports_format ON verification.reports(format);
CREATE INDEX IF NOT EXISTS idx_reports_status ON verification.reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_created_by ON verification.reports(created_by);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON verification.reports(created_at);
CREATE INDEX IF NOT EXISTS idx_reports_completed_at ON verification.reports(completed_at);

-- =====================================================
-- ALERT RULES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS verification.alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    metric_name VARCHAR(100) NOT NULL,
    condition VARCHAR(20) NOT NULL CHECK (condition IN ('greater_than', 'less_than', 'equals', 'not_equals')),
    threshold DECIMAL(10,4) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    notification_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for alert_rules
CREATE INDEX IF NOT EXISTS idx_alert_rules_name ON verification.alert_rules(name);
CREATE INDEX IF NOT EXISTS idx_alert_rules_metric_name ON verification.alert_rules(metric_name);
CREATE INDEX IF NOT EXISTS idx_alert_rules_is_active ON verification.alert_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_alert_rules_created_at ON verification.alert_rules(created_at);

-- =====================================================
-- ALERTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS verification.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID NOT NULL REFERENCES verification.alert_rules(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    message TEXT NOT NULL,
    alert_data JSONB DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT false,
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_rule_id ON verification.alerts(rule_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON verification.alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_is_resolved ON verification.alerts(is_resolved);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON verification.alerts(triggered_at);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved_at ON verification.alerts(resolved_at);

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
CREATE TRIGGER update_alert_rules_updated_at 
    BEFORE UPDATE ON verification.alert_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- CLEANUP FUNCTIONS
-- =====================================================

-- Function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM verification.dashboard_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE verification.verifications IS 'Verification results for corrections made by the system';
COMMENT ON TABLE verification.analytics_metrics IS 'Calculated metrics for system performance and quality analysis';
COMMENT ON TABLE verification.quality_assessments IS 'Quality assessments for individual corrections';
COMMENT ON TABLE verification.dashboard_cache IS 'Cached data for dashboard performance optimization';
COMMENT ON TABLE verification.reports IS 'Generated reports and their metadata';
COMMENT ON TABLE verification.alert_rules IS 'Rules for triggering system alerts based on metrics';
COMMENT ON TABLE verification.alerts IS 'Active and historical system alerts';

COMMENT ON FUNCTION cleanup_expired_cache() IS 'Removes expired entries from dashboard_cache table';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Verification Service Schema Created Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables created in verification schema:';
    RAISE NOTICE '  - verifications (with 5 indexes)';
    RAISE NOTICE '  - analytics_metrics (with 6 indexes)';
    RAISE NOTICE '  - quality_assessments (with 4 indexes)';
    RAISE NOTICE '  - dashboard_cache (with 2 indexes)';
    RAISE NOTICE '  - reports (with 6 indexes)';
    RAISE NOTICE '  - alert_rules (with 4 indexes)';
    RAISE NOTICE '  - alerts (with 5 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - cleanup_expired_cache()';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created:';
    RAISE NOTICE '  - update_alert_rules_updated_at';
    RAISE NOTICE '=================================================';
END
$$;
