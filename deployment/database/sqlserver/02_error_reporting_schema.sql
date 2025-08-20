-- =====================================================
-- Error Reporting Service - SQL Server Schema
-- =====================================================
-- This script creates the complete schema for the Error Reporting Service
-- Run this script on the ErrorReportingDB database as ers_user
-- 
-- Author: RAG Interface Deployment Team
-- Version: 1.0
-- Date: 2025-01-20
-- =====================================================

USE ErrorReportingDB;

-- =====================================================
-- ERROR REPORTS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[error_reports]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[error_reports] (
        [error_id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [job_id] UNIQUEIDENTIFIER NOT NULL,
        [speaker_id] UNIQUEIDENTIFIER NOT NULL,
        [reported_by] UNIQUEIDENTIFIER NOT NULL,
        [original_text] NVARCHAR(MAX) NOT NULL,
        [corrected_text] NVARCHAR(MAX) NOT NULL,
        [error_categories] NVARCHAR(MAX) NOT NULL DEFAULT '[]' CHECK (ISJSON([error_categories]) = 1),
        [severity_level] NVARCHAR(20) NOT NULL CHECK ([severity_level] IN ('low', 'medium', 'high', 'critical')),
        [start_position] INT NOT NULL CHECK ([start_position] >= 0),
        [end_position] INT NOT NULL CHECK ([end_position] > [start_position]),
        [context_notes] NVARCHAR(MAX),
        [error_timestamp] DATETIMEOFFSET NOT NULL,
        [reported_at] DATETIMEOFFSET NOT NULL DEFAULT SYSDATETIMEOFFSET(),
        [status] NVARCHAR(20) NOT NULL DEFAULT 'pending' CHECK ([status] IN ('pending', 'in_progress', 'resolved', 'rejected')),
        [metadata] NVARCHAR(MAX) DEFAULT '{}' CHECK (ISJSON([metadata]) = 1),
        [created_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [updated_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [created_by] UNIQUEIDENTIFIER,
        [updated_by] UNIQUEIDENTIFIER
    );
    PRINT 'Created table: error_reports';
END;

-- Create indexes for error_reports
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_reports_job_id')
    CREATE INDEX IX_error_reports_job_id ON [dbo].[error_reports]([job_id]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_reports_speaker_id')
    CREATE INDEX IX_error_reports_speaker_id ON [dbo].[error_reports]([speaker_id]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_reports_reported_by')
    CREATE INDEX IX_error_reports_reported_by ON [dbo].[error_reports]([reported_by]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_reports_severity_level')
    CREATE INDEX IX_error_reports_severity_level ON [dbo].[error_reports]([severity_level]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_reports_status')
    CREATE INDEX IX_error_reports_status ON [dbo].[error_reports]([status]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_reports_reported_at')
    CREATE INDEX IX_error_reports_reported_at ON [dbo].[error_reports]([reported_at]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_reports_error_timestamp')
    CREATE INDEX IX_error_reports_error_timestamp ON [dbo].[error_reports]([error_timestamp]);

-- =====================================================
-- ERROR AUDIT LOGS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[error_audit_logs]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[error_audit_logs] (
        [audit_id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [error_id] UNIQUEIDENTIFIER NOT NULL,
        [action_type] NVARCHAR(50) NOT NULL,
        [old_values] NVARCHAR(MAX) CHECK (ISJSON([old_values]) = 1 OR [old_values] IS NULL),
        [new_values] NVARCHAR(MAX) CHECK (ISJSON([new_values]) = 1 OR [new_values] IS NULL),
        [performed_by] UNIQUEIDENTIFIER NOT NULL,
        [performed_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [ip_address] NVARCHAR(45),
        [user_agent] NVARCHAR(MAX),
        [reason] NVARCHAR(MAX),
        FOREIGN KEY ([error_id]) REFERENCES [dbo].[error_reports]([error_id]) ON DELETE CASCADE
    );
    PRINT 'Created table: error_audit_logs';
END;

-- Create indexes for error_audit_logs
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_audit_logs_error_id')
    CREATE INDEX IX_error_audit_logs_error_id ON [dbo].[error_audit_logs]([error_id]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_audit_logs_action_type')
    CREATE INDEX IX_error_audit_logs_action_type ON [dbo].[error_audit_logs]([action_type]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_audit_logs_performed_by')
    CREATE INDEX IX_error_audit_logs_performed_by ON [dbo].[error_audit_logs]([performed_by]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_audit_logs_performed_at')
    CREATE INDEX IX_error_audit_logs_performed_at ON [dbo].[error_audit_logs]([performed_at]);

-- =====================================================
-- ERROR VALIDATIONS TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[error_validations]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[error_validations] (
        [validation_id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [error_id] UNIQUEIDENTIFIER NOT NULL,
        [validation_type] NVARCHAR(50) NOT NULL,
        [is_valid] BIT NOT NULL,
        [validation_details] NVARCHAR(MAX) DEFAULT '{}' CHECK (ISJSON([validation_details]) = 1),
        [validated_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [validated_by] UNIQUEIDENTIFIER NOT NULL,
        FOREIGN KEY ([error_id]) REFERENCES [dbo].[error_reports]([error_id]) ON DELETE CASCADE
    );
    PRINT 'Created table: error_validations';
END;

-- Create indexes for error_validations
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_validations_error_id')
    CREATE INDEX IX_error_validations_error_id ON [dbo].[error_validations]([error_id]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_validations_validation_type')
    CREATE INDEX IX_error_validations_validation_type ON [dbo].[error_validations]([validation_type]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_validations_is_valid')
    CREATE INDEX IX_error_validations_is_valid ON [dbo].[error_validations]([is_valid]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_validations_validated_by')
    CREATE INDEX IX_error_validations_validated_by ON [dbo].[error_validations]([validated_by]);

-- =====================================================
-- ERROR CATEGORIES TABLE
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[error_categories]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[error_categories] (
        [category_id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        [category_name] NVARCHAR(100) NOT NULL UNIQUE,
        [description] NVARCHAR(MAX),
        [is_active] BIT NOT NULL DEFAULT 1,
        [sort_order] INT DEFAULT 0,
        [created_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(),
        [updated_at] DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET()
    );
    PRINT 'Created table: error_categories';
END;

-- Create indexes for error_categories
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_categories_category_name')
    CREATE INDEX IX_error_categories_category_name ON [dbo].[error_categories]([category_name]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_categories_is_active')
    CREATE INDEX IX_error_categories_is_active ON [dbo].[error_categories]([is_active]);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_error_categories_sort_order')
    CREATE INDEX IX_error_categories_sort_order ON [dbo].[error_categories]([sort_order]);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Create trigger for error_reports updated_at
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_error_reports_updated_at')
BEGIN
    EXEC('
    CREATE TRIGGER TR_error_reports_updated_at
    ON [dbo].[error_reports]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE [dbo].[error_reports]
        SET [updated_at] = SYSDATETIMEOFFSET()
        FROM [dbo].[error_reports] er
        INNER JOIN inserted i ON er.[error_id] = i.[error_id];
    END
    ');
    PRINT 'Created trigger: TR_error_reports_updated_at';
END;

-- Create trigger for error_categories updated_at
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_error_categories_updated_at')
BEGIN
    EXEC('
    CREATE TRIGGER TR_error_categories_updated_at
    ON [dbo].[error_categories]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE [dbo].[error_categories]
        SET [updated_at] = SYSDATETIMEOFFSET()
        FROM [dbo].[error_categories] ec
        INNER JOIN inserted i ON ec.[category_id] = i.[category_id];
    END
    ');
    PRINT 'Created trigger: TR_error_categories_updated_at';
END;

-- =====================================================
-- EXTENDED PROPERTIES FOR DOCUMENTATION
-- =====================================================

-- Add table descriptions
EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Main table storing error reports submitted by QA personnel',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'error_reports';

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Audit trail for all changes made to error reports',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'error_audit_logs';

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Validation results for error reports',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'error_validations';

EXEC sys.sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Master list of error categories available in the system',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'error_categories';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

PRINT '=================================================';
PRINT 'Error Reporting Service Schema Created Successfully';
PRINT '=================================================';
PRINT 'Tables created:';
PRINT '  - error_reports (with 7 indexes)';
PRINT '  - error_audit_logs (with 4 indexes)';
PRINT '  - error_validations (with 4 indexes)';
PRINT '  - error_categories (with 3 indexes)';
PRINT '';
PRINT 'Triggers created:';
PRINT '  - TR_error_reports_updated_at';
PRINT '  - TR_error_categories_updated_at';
PRINT '';
PRINT 'Extended properties added for documentation';
PRINT '=================================================';
