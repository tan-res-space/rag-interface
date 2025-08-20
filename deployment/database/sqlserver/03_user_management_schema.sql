-- =====================================================
-- User Management Service - SQL Server Schema
-- =====================================================
-- This script creates the complete schema for the User Management Service
-- Run this script on the UserManagementDB database as ums_user
-- 
-- Author: RAG Interface Deployment Team
-- Version: 1.0
-- Date: 2025-01-20
-- =====================================================

USE UserManagementDB;

-- =====================================================
-- USERS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[users] (
        [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [username] NVARCHAR(50) NOT NULL UNIQUE,
        [email] NVARCHAR(255) NOT NULL UNIQUE,
        [password_hash] NVARCHAR(255) NOT NULL,
        [first_name] NVARCHAR(100) NOT NULL,
        [last_name] NVARCHAR(100) NOT NULL,
        [roles] NVARCHAR(MAX) NOT NULL DEFAULT '[]' CHECK (ISJSON([roles]) = 1),
        [status] NVARCHAR(20) NOT NULL DEFAULT 'active' CHECK ([status] IN ('active', 'inactive', 'suspended', 'pending')),
        [is_active] BIT DEFAULT 1,
        [last_login_at] DATETIMEOFFSET,
        [metadata] NVARCHAR(MAX) DEFAULT '{}' CHECK (ISJSON([metadata]) = 1),
        [created_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [updated_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET()
    );
    PRINT 'Created table: users';
END;

-- Create indexes for users
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_users_username')
    CREATE INDEX IX_users_username ON [dbo].[users]([username]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_users_email')
    CREATE INDEX IX_users_email ON [dbo].[users]([email]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_users_status')
    CREATE INDEX IX_users_status ON [dbo].[users]([status]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_users_is_active')
    CREATE INDEX IX_users_is_active ON [dbo].[users]([is_active]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_users_last_login_at')
    CREATE INDEX IX_users_last_login_at ON [dbo].[users]([last_login_at]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_users_created_at')
    CREATE INDEX IX_users_created_at ON [dbo].[users]([created_at]);

-- =====================================================
-- USER SESSIONS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_sessions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_sessions] (
        [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [user_id] UNIQUEIDENTIFIER NOT NULL,
        [session_token] NVARCHAR(255) NOT NULL UNIQUE,
        [refresh_token] NVARCHAR(255) NOT NULL UNIQUE,
        [expires_at] DATETIMEOFFSET NOT NULL,
        [created_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [is_revoked] BIT DEFAULT 0,
        [ip_address] NVARCHAR(45),
        [user_agent] NVARCHAR(MAX),
        FOREIGN KEY ([user_id]) REFERENCES [dbo].[users]([id]) ON DELETE CASCADE
    );
    PRINT 'Created table: user_sessions';
END;

-- Create indexes for user_sessions
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_sessions_user_id')
    CREATE INDEX IX_user_sessions_user_id ON [dbo].[user_sessions]([user_id]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_sessions_session_token')
    CREATE INDEX IX_user_sessions_session_token ON [dbo].[user_sessions]([session_token]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_sessions_refresh_token')
    CREATE INDEX IX_user_sessions_refresh_token ON [dbo].[user_sessions]([refresh_token]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_sessions_expires_at')
    CREATE INDEX IX_user_sessions_expires_at ON [dbo].[user_sessions]([expires_at]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_sessions_is_revoked')
    CREATE INDEX IX_user_sessions_is_revoked ON [dbo].[user_sessions]([is_revoked]);

-- =====================================================
-- PERMISSIONS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[permissions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[permissions] (
        [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [name] NVARCHAR(100) NOT NULL UNIQUE,
        [description] NVARCHAR(MAX),
        [resource] NVARCHAR(100) NOT NULL,
        [action] NVARCHAR(50) NOT NULL,
        [created_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [updated_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET()
    );
    PRINT 'Created table: permissions';
END;

-- Create indexes for permissions
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_permissions_name')
    CREATE INDEX IX_permissions_name ON [dbo].[permissions]([name]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_permissions_resource')
    CREATE INDEX IX_permissions_resource ON [dbo].[permissions]([resource]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_permissions_action')
    CREATE INDEX IX_permissions_action ON [dbo].[permissions]([action]);

-- =====================================================
-- ROLE PERMISSIONS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[role_permissions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[role_permissions] (
        [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [role] NVARCHAR(50) NOT NULL CHECK ([role] IN ('admin', 'qa_supervisor', 'qa_personnel', 'mts_personnel', 'viewer')),
        [permission_id] UNIQUEIDENTIFIER NOT NULL,
        [created_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        FOREIGN KEY ([permission_id]) REFERENCES [dbo].[permissions]([id]) ON DELETE CASCADE,
        UNIQUE([role], [permission_id])
    );
    PRINT 'Created table: role_permissions';
END;

-- Create indexes for role_permissions
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_role_permissions_role')
    CREATE INDEX IX_role_permissions_role ON [dbo].[role_permissions]([role]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_role_permissions_permission_id')
    CREATE INDEX IX_role_permissions_permission_id ON [dbo].[role_permissions]([permission_id]);

-- =====================================================
-- USER AUDIT LOGS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_audit_logs]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_audit_logs] (
        [id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [user_id] UNIQUEIDENTIFIER,
        [action] NVARCHAR(100) NOT NULL,
        [resource] NVARCHAR(100) NOT NULL,
        [details] NVARCHAR(MAX) DEFAULT '{}' CHECK (ISJSON([details]) = 1),
        [ip_address] NVARCHAR(45),
        [user_agent] NVARCHAR(MAX),
        [created_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        FOREIGN KEY ([user_id]) REFERENCES [dbo].[users]([id]) ON DELETE SET NULL
    );
    PRINT 'Created table: user_audit_logs';
END;

-- Create indexes for user_audit_logs
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_audit_logs_user_id')
    CREATE INDEX IX_user_audit_logs_user_id ON [dbo].[user_audit_logs]([user_id]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_audit_logs_action')
    CREATE INDEX IX_user_audit_logs_action ON [dbo].[user_audit_logs]([action]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_audit_logs_resource')
    CREATE INDEX IX_user_audit_logs_resource ON [dbo].[user_audit_logs]([resource]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_audit_logs_created_at')
    CREATE INDEX IX_user_audit_logs_created_at ON [dbo].[user_audit_logs]([created_at]);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Create trigger for users updated_at
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_users_updated_at')
BEGIN
    EXEC('
    CREATE TRIGGER TR_users_updated_at
    ON [dbo].[users]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE [dbo].[users]
        SET [updated_at] = SYSDATETIMEOFFSET()
        FROM [dbo].[users] u
        INNER JOIN inserted i ON u.[id] = i.[id];
    END
    ');
    PRINT 'Created trigger: TR_users_updated_at';
END;

-- Create trigger for permissions updated_at
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_permissions_updated_at')
BEGIN
    EXEC('
    CREATE TRIGGER TR_permissions_updated_at
    ON [dbo].[permissions]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE [dbo].[permissions]
        SET [updated_at] = SYSDATETIMEOFFSET()
        FROM [dbo].[permissions] p
        INNER JOIN inserted i ON p.[id] = i.[id];
    END
    ');
    PRINT 'Created trigger: TR_permissions_updated_at';
END;

-- =====================================================
-- SECURITY FUNCTIONS
-- =====================================================

-- Function to hash passwords using HASHBYTES
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[hash_password]') AND type in (N'FN'))
BEGIN
    EXEC('
    CREATE FUNCTION [dbo].[hash_password](@password NVARCHAR(255))
    RETURNS NVARCHAR(255)
    AS
    BEGIN
        DECLARE @salt NVARCHAR(255) = CONVERT(NVARCHAR(255), NEWID());
        DECLARE @hash NVARCHAR(255) = CONVERT(NVARCHAR(255), HASHBYTES(''SHA2_256'', @password + @salt), 2);
        RETURN @salt + '':'' + @hash;
    END
    ');
    PRINT 'Created function: hash_password';
END;

-- Function to verify passwords
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[verify_password]') AND type in (N'FN'))
BEGIN
    EXEC('
    CREATE FUNCTION [dbo].[verify_password](@password NVARCHAR(255), @hash NVARCHAR(255))
    RETURNS BIT
    AS
    BEGIN
        DECLARE @salt NVARCHAR(255) = LEFT(@hash, CHARINDEX('':'', @hash) - 1);
        DECLARE @stored_hash NVARCHAR(255) = SUBSTRING(@hash, CHARINDEX('':'', @hash) + 1, LEN(@hash));
        DECLARE @computed_hash NVARCHAR(255) = CONVERT(NVARCHAR(255), HASHBYTES(''SHA2_256'', @password + @salt), 2);

        IF @stored_hash = @computed_hash
            RETURN 1;
        RETURN 0;
    END
    ');
    PRINT 'Created function: verify_password';
END;

-- =====================================================
-- EXTENDED PROPERTIES FOR DOCUMENTATION
-- =====================================================

-- Add table descriptions
EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Main table storing user accounts and authentication information',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'users';

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Active user sessions with JWT tokens',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'user_sessions';

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'System permissions that can be assigned to roles',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'permissions';

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Mapping between roles and their assigned permissions',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'role_permissions';

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Audit trail for user actions and system events',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'user_audit_logs';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

PRINT '=================================================';
PRINT 'User Management Service Schema Created Successfully';
PRINT '=================================================';
PRINT 'Tables created:';
PRINT '  - users (with 6 indexes)';
PRINT '  - user_sessions (with 5 indexes)';
PRINT '  - permissions (with 3 indexes)';
PRINT '  - role_permissions (with 2 indexes)';
PRINT '  - user_audit_logs (with 4 indexes)';
PRINT '';
PRINT 'Functions created:';
PRINT '  - hash_password()';
PRINT '  - verify_password()';
PRINT '';
PRINT 'Triggers created:';
PRINT '  - TR_users_updated_at';
PRINT '  - TR_permissions_updated_at';
PRINT '';
PRINT 'Extended properties added for documentation';
PRINT '=================================================';
