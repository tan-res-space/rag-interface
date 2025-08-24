-- =====================================================
-- RAG Interface System - PostgreSQL Database Creation
-- =====================================================
-- This script creates the unified database with separate schemas for all microservices
-- Run this script as a PostgreSQL superuser (postgres)
--
-- Author: RAG Interface Deployment Team
-- Version: 2.0 - Single Database with Multiple Schemas
-- Date: 2025-01-20
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- DATABASE CREATION
-- =====================================================

-- Create unified database for all microservices
-- Note: This script is idempotent - can be run multiple times safely

-- RAG Interface Unified Database
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'rag_interface_db') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE rag_interface_db');
    END IF;
END
$$;

-- Connect to the new database to create schemas
\c rag_interface_db;

-- Enable required extensions in the new database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- SCHEMA CREATION
-- =====================================================

-- Create schemas for each microservice
-- This provides logical separation while using a single database

-- Error Reporting Service Schema
CREATE SCHEMA IF NOT EXISTS error_reporting;

-- User Management Service Schema
CREATE SCHEMA IF NOT EXISTS user_management;

-- Verification Service Schema
CREATE SCHEMA IF NOT EXISTS verification;

-- Correction Engine Service Schema
CREATE SCHEMA IF NOT EXISTS correction_engine;

-- RAG Integration Service Schema
CREATE SCHEMA IF NOT EXISTS rag_integration;

-- =====================================================
-- USER CREATION
-- =====================================================

-- Create service-specific users with appropriate permissions
-- Each service gets its own database user for schema-level security isolation

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

-- Grant database connection privileges
GRANT CONNECT ON DATABASE rag_interface_db TO ers_user;
GRANT CONNECT ON DATABASE rag_interface_db TO ums_user;
GRANT CONNECT ON DATABASE rag_interface_db TO vs_user;
GRANT CONNECT ON DATABASE rag_interface_db TO ces_user;
GRANT CONNECT ON DATABASE rag_interface_db TO ris_user;

-- Grant schema-specific privileges
-- Each service user gets full access to their own schema and usage on others for cross-schema references

-- Error Reporting Service permissions
GRANT ALL PRIVILEGES ON SCHEMA error_reporting TO ers_user;
GRANT USAGE ON SCHEMA user_management TO ers_user;  -- For user references
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA error_reporting TO ers_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA error_reporting TO ers_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA error_reporting GRANT ALL ON TABLES TO ers_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA error_reporting GRANT ALL ON SEQUENCES TO ers_user;

-- User Management Service permissions
GRANT ALL PRIVILEGES ON SCHEMA user_management TO ums_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA user_management TO ums_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA user_management TO ums_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA user_management GRANT ALL ON TABLES TO ums_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA user_management GRANT ALL ON SEQUENCES TO ums_user;

-- Verification Service permissions
GRANT ALL PRIVILEGES ON SCHEMA verification TO vs_user;
GRANT USAGE ON SCHEMA correction_engine TO vs_user;  -- For correction references
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA verification TO vs_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA verification TO vs_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA verification GRANT ALL ON TABLES TO vs_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA verification GRANT ALL ON SEQUENCES TO vs_user;

-- Correction Engine Service permissions
GRANT ALL PRIVILEGES ON SCHEMA correction_engine TO ces_user;
GRANT USAGE ON SCHEMA rag_integration TO ces_user;  -- For RAG service integration
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA correction_engine TO ces_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA correction_engine TO ces_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA correction_engine GRANT ALL ON TABLES TO ces_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA correction_engine GRANT ALL ON SEQUENCES TO ces_user;

-- RAG Integration Service permissions
GRANT ALL PRIVILEGES ON SCHEMA rag_integration TO ris_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA rag_integration TO ris_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA rag_integration TO ris_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag_integration GRANT ALL ON TABLES TO ris_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag_integration GRANT ALL ON SEQUENCES TO ris_user;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'RAG Interface System Database Created Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Database created: rag_interface_db';
    RAISE NOTICE '';
    RAISE NOTICE 'Schemas created:';
    RAISE NOTICE '  - error_reporting (user: ers_user)';
    RAISE NOTICE '  - user_management (user: ums_user)';
    RAISE NOTICE '  - verification (user: vs_user)';
    RAISE NOTICE '  - correction_engine (user: ces_user)';
    RAISE NOTICE '  - rag_integration (user: ris_user)';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Run schema creation scripts for each service';
    RAISE NOTICE '  2. Run sample data insertion scripts';
    RAISE NOTICE '  3. Configure application connection strings to use:';
    RAISE NOTICE '     postgresql://user:password@host:5432/rag_interface_db';
    RAISE NOTICE '  4. Set default schema search path in applications';
    RAISE NOTICE '=================================================';
END
$$;
