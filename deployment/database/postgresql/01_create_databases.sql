-- =====================================================
-- RAG Interface System - PostgreSQL Database Creation
-- =====================================================
-- This script creates the main databases for all microservices
-- Run this script as a PostgreSQL superuser (postgres)
-- 
-- Author: RAG Interface Deployment Team
-- Version: 1.0
-- Date: 2025-01-20
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- DATABASE CREATION
-- =====================================================

-- Create databases for each microservice
-- Note: This script is idempotent - can be run multiple times safely

-- Error Reporting Service Database
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'error_reporting_db') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE error_reporting_db');
    END IF;
END
$$;

-- User Management Service Database  
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'user_management_db') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE user_management_db');
    END IF;
END
$$;

-- Verification Service Database
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'verification_db') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE verification_db');
    END IF;
END
$$;

-- Correction Engine Service Database
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'correction_engine_db') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE correction_engine_db');
    END IF;
END
$$;

-- RAG Integration Service Database (for metadata and caching)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'rag_integration_db') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE rag_integration_db');
    END IF;
END
$$;

-- =====================================================
-- USER CREATION
-- =====================================================

-- Create service-specific users with appropriate permissions
-- Each service gets its own database user for security isolation

-- Error Reporting Service User
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ers_user') THEN
        CREATE USER ers_user WITH PASSWORD 'ers_secure_password_2025';
    END IF;
END
$$;

-- User Management Service User
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ums_user') THEN
        CREATE USER ums_user WITH PASSWORD 'ums_secure_password_2025';
    END IF;
END
$$;

-- Verification Service User
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'vs_user') THEN
        CREATE USER vs_user WITH PASSWORD 'vs_secure_password_2025';
    END IF;
END
$$;

-- Correction Engine Service User
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ces_user') THEN
        CREATE USER ces_user WITH PASSWORD 'ces_secure_password_2025';
    END IF;
END
$$;

-- RAG Integration Service User
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ris_user') THEN
        CREATE USER ris_user WITH PASSWORD 'ris_secure_password_2025';
    END IF;
END
$$;

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Grant database access to respective users
GRANT ALL PRIVILEGES ON DATABASE error_reporting_db TO ers_user;
GRANT ALL PRIVILEGES ON DATABASE user_management_db TO ums_user;
GRANT ALL PRIVILEGES ON DATABASE verification_db TO vs_user;
GRANT ALL PRIVILEGES ON DATABASE correction_engine_db TO ces_user;
GRANT ALL PRIVILEGES ON DATABASE rag_integration_db TO ris_user;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'RAG Interface System Databases Created Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Databases created:';
    RAISE NOTICE '  - error_reporting_db (user: ers_user)';
    RAISE NOTICE '  - user_management_db (user: ums_user)';
    RAISE NOTICE '  - verification_db (user: vs_user)';
    RAISE NOTICE '  - correction_engine_db (user: ces_user)';
    RAISE NOTICE '  - rag_integration_db (user: ris_user)';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Run schema creation scripts for each service';
    RAISE NOTICE '  2. Run sample data insertion scripts';
    RAISE NOTICE '  3. Configure application connection strings';
    RAISE NOTICE '=================================================';
END
$$;
