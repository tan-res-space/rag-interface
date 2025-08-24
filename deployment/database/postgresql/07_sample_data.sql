-- =====================================================
-- RAG Interface System - Sample Data Insertion
-- =====================================================
-- This script inserts sample data for testing and initial setup
-- Run this script after creating all schemas
--
-- Author: RAG Interface Deployment Team
-- Version: 2.0 - Single Database with Schema Separation
-- Date: 2025-01-20
-- =====================================================

-- =====================================================
-- USER MANAGEMENT SERVICE SAMPLE DATA
-- =====================================================

\c rag_interface_db;

-- Set search path for user management
SET search_path TO user_management, public;

-- Insert default permissions
INSERT INTO permissions (name, description, resource, action) VALUES
    ('view_errors', 'View error reports', 'error_reports', 'read'),
    ('create_errors', 'Create new error reports', 'error_reports', 'create'),
    ('edit_errors', 'Edit existing error reports', 'error_reports', 'update'),
    ('delete_errors', 'Delete error reports', 'error_reports', 'delete'),
    ('view_users', 'View user accounts', 'users', 'read'),
    ('create_users', 'Create new user accounts', 'users', 'create'),
    ('edit_users', 'Edit user accounts', 'users', 'update'),
    ('delete_users', 'Delete user accounts', 'users', 'delete'),
    ('view_analytics', 'View system analytics', 'analytics', 'read'),
    ('manage_system', 'Manage system settings', 'system', 'manage')
ON CONFLICT (name) DO NOTHING;

-- Insert role permissions
INSERT INTO role_permissions (role, permission_id) 
SELECT 'admin', id FROM permissions
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO role_permissions (role, permission_id) 
SELECT 'qa_supervisor', id FROM permissions WHERE name IN ('view_errors', 'create_errors', 'edit_errors', 'view_users', 'view_analytics')
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO role_permissions (role, permission_id) 
SELECT 'qa_personnel', id FROM permissions WHERE name IN ('view_errors', 'create_errors', 'edit_errors')
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO role_permissions (role, permission_id) 
SELECT 'mts_personnel', id FROM permissions WHERE name IN ('view_errors', 'view_analytics')
ON CONFLICT (role, permission_id) DO NOTHING;

INSERT INTO role_permissions (role, permission_id) 
SELECT 'viewer', id FROM permissions WHERE name IN ('view_errors', 'view_analytics')
ON CONFLICT (role, permission_id) DO NOTHING;

-- Insert default admin user
INSERT INTO users (username, email, password_hash, first_name, last_name, roles, status) VALUES
    ('admin', 'admin@raginterface.com', hash_password('AdminPassword123!'), 'System', 'Administrator', '["admin"]', 'active'),
    ('qa_supervisor', 'qa.supervisor@raginterface.com', hash_password('QASuper123!'), 'QA', 'Supervisor', '["qa_supervisor"]', 'active'),
    ('qa_user', 'qa.user@raginterface.com', hash_password('QAUser123!'), 'QA', 'Personnel', '["qa_personnel"]', 'active'),
    ('mts_user', 'mts.user@raginterface.com', hash_password('MTSUser123!'), 'MTS', 'Personnel', '["mts_personnel"]', 'active')
ON CONFLICT (username) DO NOTHING;

-- =====================================================
-- ERROR REPORTING SERVICE SAMPLE DATA
-- =====================================================

-- Set search path for error reporting
SET search_path TO error_reporting, public;

-- Insert default error categories
INSERT INTO error_categories (category_name, description, is_active, sort_order) VALUES
    ('Pronunciation Error', 'Incorrect pronunciation of words', true, 1),
    ('Grammar Error', 'Grammatical mistakes in transcription', true, 2),
    ('Word Substitution', 'Wrong word used in place of correct word', true, 3),
    ('Missing Word', 'Word omitted from transcription', true, 4),
    ('Extra Word', 'Unnecessary word added to transcription', true, 5),
    ('Number Error', 'Incorrect transcription of numbers', true, 6),
    ('Proper Noun Error', 'Incorrect transcription of names or places', true, 7),
    ('Technical Term Error', 'Incorrect transcription of technical terminology', true, 8),
    ('Punctuation Error', 'Missing or incorrect punctuation', true, 9),
    ('Capitalization Error', 'Incorrect capitalization', true, 10)
ON CONFLICT (category_name) DO NOTHING;

-- Insert sample error reports
INSERT INTO error_reports (
    job_id, speaker_id, reported_by, original_text, corrected_text, 
    error_categories, severity_level, start_position, end_position, 
    context_notes, error_timestamp, status
) VALUES
    (
        gen_random_uuid(), gen_random_uuid(), 
        (SELECT id FROM user_management.users WHERE username = 'qa_user' LIMIT 1),
        'The patient has a temperature of ninety eight point six degrees.',
        'The patient has a temperature of 98.6 degrees.',
        '["Number Error"]', 'medium', 35, 58,
        'Numbers should be transcribed in numeric format for medical records',
        NOW() - INTERVAL '2 hours', 'pending'
    ),
    (
        gen_random_uuid(), gen_random_uuid(),
        (SELECT id FROM user_management.users WHERE username = 'qa_user' LIMIT 1),
        'Dr. Smith will see you at three PM.',
        'Dr. Smith will see you at 3 PM.',
        '["Number Error", "Proper Noun Error"]', 'low', 26, 34,
        'Time should be in numeric format',
        NOW() - INTERVAL '1 hour', 'pending'
    )
ON CONFLICT DO NOTHING;

-- =====================================================
-- VERIFICATION SERVICE SAMPLE DATA
-- =====================================================

-- Set search path for verification
SET search_path TO verification, public;

-- Insert sample alert rules
INSERT INTO alert_rules (name, metric_name, condition, threshold, is_active, notification_config) VALUES
    ('High Error Rate', 'error_rate', 'greater_than', 0.05, true, '{"email": ["admin@raginterface.com"], "slack": true}'),
    ('Low Verification Rate', 'verification_rate', 'less_than', 0.80, true, '{"email": ["qa.supervisor@raginterface.com"]}'),
    ('Processing Time Alert', 'avg_processing_time', 'greater_than', 5.0, true, '{"email": ["admin@raginterface.com"]}')
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- CORRECTION ENGINE SERVICE SAMPLE DATA
-- =====================================================

-- Set search path for correction engine
SET search_path TO correction_engine, public;

-- Insert sample correction patterns
INSERT INTO correction_patterns (pattern_hash, pattern_text, correction_text, success_rate, usage_count, avg_confidence) VALUES
    (generate_pattern_hash('ninety eight point six'), 'ninety eight point six', '98.6', 0.95, 15, 0.92),
    (generate_pattern_hash('three PM'), 'three PM', '3 PM', 0.88, 8, 0.85),
    (generate_pattern_hash('Dr Smith'), 'Dr Smith', 'Dr. Smith', 0.99, 25, 0.98),
    (generate_pattern_hash('cant'), 'cant', 'can''t', 0.92, 12, 0.89)
ON CONFLICT (pattern_hash) DO NOTHING;

-- =====================================================
-- RAG INTEGRATION SERVICE SAMPLE DATA
-- =====================================================

-- Set search path for RAG integration
SET search_path TO rag_integration, public;

-- Insert sample vector database sync status
INSERT INTO vector_db_sync_status (vector_db_type, sync_status, total_vectors, synced_vectors) VALUES
    ('pinecone', 'completed', 1000, 1000),
    ('weaviate', 'pending', 0, 0)
ON CONFLICT DO NOTHING;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Sample Data Inserted Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Default users created:';
    RAISE NOTICE '  - admin (password: AdminPassword123!)';
    RAISE NOTICE '  - qa_supervisor (password: QASuper123!)';
    RAISE NOTICE '  - qa_user (password: QAUser123!)';
    RAISE NOTICE '  - mts_user (password: MTSUser123!)';
    RAISE NOTICE '';
    RAISE NOTICE 'Sample data includes:';
    RAISE NOTICE '  - 10 default permissions';
    RAISE NOTICE '  - Role-permission mappings';
    RAISE NOTICE '  - 10 error categories';
    RAISE NOTICE '  - 2 sample error reports';
    RAISE NOTICE '  - 3 alert rules';
    RAISE NOTICE '  - 4 correction patterns';
    RAISE NOTICE '  - Vector DB sync status';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANT: Change default passwords in production!';
    RAISE NOTICE '=================================================';
END
$$;
