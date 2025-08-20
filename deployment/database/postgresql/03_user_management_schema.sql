-- =====================================================
-- User Management Service - PostgreSQL Schema
-- =====================================================
-- This script creates the complete schema for the User Management Service
-- Run this script on the user_management_db database as ums_user
-- 
-- Author: RAG Interface Deployment Team
-- Version: 1.0
-- Date: 2025-01-20
-- =====================================================

\c user_management_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    roles JSONB NOT NULL DEFAULT '[]',
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending')),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_last_login_at ON users(last_login_at);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- =====================================================
-- USER SESSIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    refresh_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_revoked BOOLEAN DEFAULT false,
    ip_address INET,
    user_agent TEXT
);

-- Create indexes for user_sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_refresh_token ON user_sessions(refresh_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_revoked ON user_sessions(is_revoked);

-- =====================================================
-- PERMISSIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for permissions
CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);
CREATE INDEX IF NOT EXISTS idx_permissions_action ON permissions(action);

-- =====================================================
-- ROLE PERMISSIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'qa_supervisor', 'qa_personnel', 'mts_personnel', 'viewer')),
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role, permission_id)
);

-- Create indexes for role_permissions
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);

-- =====================================================
-- USER AUDIT LOGS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS user_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for user_audit_logs
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_user_id ON user_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_action ON user_audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_resource ON user_audit_logs(resource);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_created_at ON user_audit_logs(created_at);

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
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_permissions_updated_at 
    BEFORE UPDATE ON permissions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SECURITY FUNCTIONS
-- =====================================================

-- Function to hash passwords using bcrypt
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(password, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql;

-- Function to verify passwords
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE users IS 'Main table storing user accounts and authentication information';
COMMENT ON TABLE user_sessions IS 'Active user sessions with JWT tokens';
COMMENT ON TABLE permissions IS 'System permissions that can be assigned to roles';
COMMENT ON TABLE role_permissions IS 'Mapping between roles and their assigned permissions';
COMMENT ON TABLE user_audit_logs IS 'Audit trail for user actions and system events';

COMMENT ON COLUMN users.id IS 'Unique identifier for the user';
COMMENT ON COLUMN users.username IS 'Unique username for login';
COMMENT ON COLUMN users.email IS 'User email address (must be unique)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.roles IS 'JSON array of assigned roles';
COMMENT ON COLUMN users.status IS 'Current account status';
COMMENT ON COLUMN users.metadata IS 'Additional user metadata in JSON format';

COMMENT ON FUNCTION hash_password(TEXT) IS 'Hash a password using bcrypt with salt rounds 12';
COMMENT ON FUNCTION verify_password(TEXT, TEXT) IS 'Verify a password against its hash';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'User Management Service Schema Created Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - users (with 6 indexes)';
    RAISE NOTICE '  - user_sessions (with 5 indexes)';
    RAISE NOTICE '  - permissions (with 3 indexes)';
    RAISE NOTICE '  - role_permissions (with 2 indexes)';
    RAISE NOTICE '  - user_audit_logs (with 4 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - hash_password()';
    RAISE NOTICE '  - verify_password()';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created:';
    RAISE NOTICE '  - update_users_updated_at';
    RAISE NOTICE '  - update_permissions_updated_at';
    RAISE NOTICE '=================================================';
END
$$;
