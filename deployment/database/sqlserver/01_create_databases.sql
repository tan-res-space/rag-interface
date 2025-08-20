-- =====================================================
-- RAG Interface System - SQL Server Database Creation
-- =====================================================
-- This script creates the main databases for all microservices
-- Run this script as a SQL Server administrator (sa or sysadmin role)
-- 
-- Author: RAG Interface Deployment Team
-- Version: 1.0
-- Date: 2025-01-20
-- =====================================================

-- Enable advanced options for configuration changes
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;

-- =====================================================
-- DATABASE CREATION
-- =====================================================

-- Create databases for each microservice
-- Note: This script is idempotent - can be run multiple times safely

-- Error Reporting Service Database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ErrorReportingDB')
BEGIN
    CREATE DATABASE ErrorReportingDB
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'Created database: ErrorReportingDB';
END
ELSE
BEGIN
    PRINT 'Database ErrorReportingDB already exists';
END;

-- User Management Service Database  
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'UserManagementDB')
BEGIN
    CREATE DATABASE UserManagementDB
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'Created database: UserManagementDB';
END
ELSE
BEGIN
    PRINT 'Database UserManagementDB already exists';
END;

-- Verification Service Database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'VerificationDB')
BEGIN
    CREATE DATABASE VerificationDB
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'Created database: VerificationDB';
END
ELSE
BEGIN
    PRINT 'Database VerificationDB already exists';
END;

-- Correction Engine Service Database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'CorrectionEngineDB')
BEGIN
    CREATE DATABASE CorrectionEngineDB
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'Created database: CorrectionEngineDB';
END
ELSE
BEGIN
    PRINT 'Database CorrectionEngineDB already exists';
END;

-- RAG Integration Service Database (for metadata and caching)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'RAGIntegrationDB')
BEGIN
    CREATE DATABASE RAGIntegrationDB
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'Created database: RAGIntegrationDB';
END
ELSE
BEGIN
    PRINT 'Database RAGIntegrationDB already exists';
END;

-- =====================================================
-- LOGIN AND USER CREATION
-- =====================================================

-- Create service-specific logins and users with appropriate permissions
-- Each service gets its own database user for security isolation

-- Error Reporting Service Login and User
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'ers_user')
BEGIN
    CREATE LOGIN ers_user WITH PASSWORD = 'ERS_Secure_Password_2025!';
    PRINT 'Created login: ers_user';
END;

USE ErrorReportingDB;
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'ers_user')
BEGIN
    CREATE USER ers_user FOR LOGIN ers_user;
    ALTER ROLE db_owner ADD MEMBER ers_user;
    PRINT 'Created user ers_user in ErrorReportingDB';
END;

-- User Management Service Login and User
USE master;
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'ums_user')
BEGIN
    CREATE LOGIN ums_user WITH PASSWORD = 'UMS_Secure_Password_2025!';
    PRINT 'Created login: ums_user';
END;

USE UserManagementDB;
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'ums_user')
BEGIN
    CREATE USER ums_user FOR LOGIN ums_user;
    ALTER ROLE db_owner ADD MEMBER ums_user;
    PRINT 'Created user ums_user in UserManagementDB';
END;

-- Verification Service Login and User
USE master;
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'vs_user')
BEGIN
    CREATE LOGIN vs_user WITH PASSWORD = 'VS_Secure_Password_2025!';
    PRINT 'Created login: vs_user';
END;

USE VerificationDB;
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'vs_user')
BEGIN
    CREATE USER vs_user FOR LOGIN vs_user;
    ALTER ROLE db_owner ADD MEMBER vs_user;
    PRINT 'Created user vs_user in VerificationDB';
END;

-- Correction Engine Service Login and User
USE master;
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'ces_user')
BEGIN
    CREATE LOGIN ces_user WITH PASSWORD = 'CES_Secure_Password_2025!';
    PRINT 'Created login: ces_user';
END;

USE CorrectionEngineDB;
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'ces_user')
BEGIN
    CREATE USER ces_user FOR LOGIN ces_user;
    ALTER ROLE db_owner ADD MEMBER ces_user;
    PRINT 'Created user ces_user in CorrectionEngineDB';
END;

-- RAG Integration Service Login and User
USE master;
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'ris_user')
BEGIN
    CREATE LOGIN ris_user WITH PASSWORD = 'RIS_Secure_Password_2025!';
    PRINT 'Created login: ris_user';
END;

USE RAGIntegrationDB;
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'ris_user')
BEGIN
    CREATE USER ris_user FOR LOGIN ris_user;
    ALTER ROLE db_owner ADD MEMBER ris_user;
    PRINT 'Created user ris_user in RAGIntegrationDB';
END;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

USE master;
PRINT '=================================================';
PRINT 'RAG Interface System Databases Created Successfully';
PRINT '=================================================';
PRINT 'Databases created:';
PRINT '  - ErrorReportingDB (user: ers_user)';
PRINT '  - UserManagementDB (user: ums_user)';
PRINT '  - VerificationDB (user: vs_user)';
PRINT '  - CorrectionEngineDB (user: ces_user)';
PRINT '  - RAGIntegrationDB (user: ris_user)';
PRINT '';
PRINT 'Next steps:';
PRINT '  1. Run schema creation scripts for each service';
PRINT '  2. Run sample data insertion scripts';
PRINT '  3. Configure application connection strings';
PRINT '=================================================';
