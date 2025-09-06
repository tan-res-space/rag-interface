# RAG Interface System - Database Deployment Scripts

This directory contains comprehensive database creation and schema scripts for both PostgreSQL and SQL Server databases supporting the RAG Interface System's five microservices.

## 📁 Directory Structure

```
deployment/database/
├── postgresql/                 # PostgreSQL scripts
│   ├── 01_create_databases.sql    # Database and user creation
│   ├── 02_error_reporting_schema.sql
│   ├── 03_user_management_schema.sql
│   ├── 04_verification_service_schema.sql
│   ├── 05_correction_engine_schema.sql
│   ├── 06_rag_integration_schema.sql
│   └── 07_sample_data.sql         # Sample data for testing
├── sqlserver/                  # SQL Server scripts
│   ├── 01_create_databases.sql    # Database and login creation
│   ├── 02_error_reporting_schema.sql
│   ├── 03_user_management_schema.sql
│   └── [additional schemas...]
└── README.md                   # This file
```

## 🗄️ Database Architecture

The RAG Interface System uses a **single database with multiple schemas** approach for better administration while maintaining service isolation:

| Service | PostgreSQL Schema | SQL Server Schema | Purpose |
|---------|-------------------|-------------------|---------|
| Error Reporting Service | `error_reporting` | `ErrorReporting` | Error reports, categories, audit logs |
| User Management Service | `user_management` | `UserManagement` | Users, sessions, permissions |
| Verification Service | `verification` | `Verification` | Verifications, analytics, reports |
| Correction Engine Service | `correction_engine` | `CorrectionEngine` | Corrections, patterns, feedback |
| RAG Integration Service | `rag_integration` | `RAGIntegration` | Metadata, cache, sync status |

**Database Names:**
- PostgreSQL: `rag_interface_db`
- SQL Server: `RAGInterfaceDB`

## 🚀 Quick Start

### PostgreSQL Deployment

1. **Prerequisites**
   - PostgreSQL 12+ installed and running
   - Superuser access (postgres user)
   - `dblink` extension available

2. **Run Scripts in Order**
   ```bash
   # Connect as postgres superuser
   psql -U postgres -h localhost

   # Create database and schemas
   \i deployment/database/postgresql/01_create_databases.sql

   # Create schemas (run each as respective user on rag_interface_db)
   \i deployment/database/postgresql/02_error_reporting_schema.sql
   \i deployment/database/postgresql/03_user_management_schema.sql
   \i deployment/database/postgresql/04_verification_service_schema.sql
   \i deployment/database/postgresql/05_correction_engine_schema.sql
   \i deployment/database/postgresql/06_rag_integration_schema.sql

   # Insert sample data
   \i deployment/database/postgresql/07_sample_data.sql
   ```

### SQL Server Deployment

1. **Prerequisites**
   - SQL Server 2017+ installed and running
   - sysadmin or sa access
   - SQL Server Management Studio or sqlcmd

2. **Run Scripts in Order**
   ```sql
   -- Connect as sa or sysadmin
   sqlcmd -S localhost -U sa -P YourPassword

   -- Create database and schemas
   :r deployment\database\sqlserver\01_create_databases.sql

   -- Create schemas (run each on RAGInterfaceDB)
   :r deployment\database\sqlserver\02_error_reporting_schema.sql
   :r deployment\database\sqlserver\03_user_management_schema.sql
   -- Continue with remaining schema files...
   ```

## 🔐 Security Configuration

### Default Credentials

**⚠️ IMPORTANT: Change these passwords in production!**

#### PostgreSQL Users
- `ers_user` / `ers_secure_password_2025`
- `ums_user` / `ums_secure_password_2025`
- `vs_user` / `vs_secure_password_2025`
- `ces_user` / `ces_secure_password_2025`
- `ris_user` / `ris_secure_password_2025`

#### SQL Server Logins
- `ers_user` / `ERS_Secure_Password_2025!`
- `ums_user` / `UMS_Secure_Password_2025!`
- `vs_user` / `VS_Secure_Password_2025!`
- `ces_user` / `CES_Secure_Password_2025!`
- `ris_user` / `RIS_Secure_Password_2025!`

#### Default Application Users
- `admin` / `AdminPassword123!`
- `qa_supervisor` / `QASuper123!`
- `qa_user` / `QAUser123!`
- `mts_user` / `MTSUser123!`

### Security Best Practices

1. **Change Default Passwords**
   ```sql
   -- PostgreSQL
   ALTER USER ers_user PASSWORD 'your_secure_password';
   
   -- SQL Server
   ALTER LOGIN ers_user WITH PASSWORD = 'YourSecurePassword!';
   ```

2. **Restrict Network Access**
   - Configure `pg_hba.conf` for PostgreSQL
   - Use SQL Server Configuration Manager for SQL Server

3. **Enable SSL/TLS**
   - Configure SSL certificates for database connections

4. **Schema-Level Security**
   - Each service user has access only to their specific schema
   - Cross-schema access is granted only where needed for service integration

## 📊 Database Schema Overview

### Error Reporting Service
- **error_reports**: Main error report data
- **error_audit_logs**: Change tracking
- **error_validations**: Validation results
- **error_categories**: Error classification

### User Management Service
- **users**: User accounts and authentication
- **user_sessions**: Active sessions
- **permissions**: System permissions
- **role_permissions**: Role-based access control
- **user_audit_logs**: User activity tracking

### Verification Service
- **verifications**: Correction verifications
- **analytics_metrics**: Performance metrics
- **quality_assessments**: Quality scoring
- **dashboard_cache**: UI performance cache
- **reports**: Generated reports
- **alert_rules** & **alerts**: Monitoring system

### Correction Engine Service
- **corrections**: Correction operations
- **applied_corrections**: Individual corrections
- **correction_feedback**: User feedback
- **correction_patterns**: Learned patterns
- **correction_metrics**: Performance data

### RAG Integration Service
- **embedding_metadata**: Vector embedding metadata
- **similarity_search_cache**: Search result cache
- **pattern_analysis_results**: Analysis results
- **vector_db_sync_status**: External DB sync
- **ml_model_performance**: Model metrics

## 🔧 Maintenance

### Regular Tasks

1. **Backup Database**
   ```bash
   # PostgreSQL - Full database backup
   pg_dump -U postgres rag_interface_db > backup_rag_interface_$(date +%Y%m%d).sql

   # PostgreSQL - Schema-specific backup
   pg_dump -U postgres -n error_reporting rag_interface_db > backup_error_reporting_$(date +%Y%m%d).sql

   # SQL Server
   BACKUP DATABASE RAGInterfaceDB TO DISK = 'C:\Backups\RAGInterfaceDB.bak'
   ```

2. **Clean Cache Tables**
   ```sql
   -- PostgreSQL
   SELECT cleanup_expired_cache();
   
   -- SQL Server
   DELETE FROM dashboard_cache WHERE expires_at < SYSDATETIMEOFFSET();
   ```

3. **Monitor Performance**
   - Check index usage
   - Analyze query performance
   - Monitor disk space

### Troubleshooting

#### Common Issues

1. **Permission Denied**
   - Verify user has correct database permissions
   - Check connection string credentials

2. **Foreign Key Violations**
   - Ensure parent records exist before inserting child records
   - Check referential integrity

3. **JSON Validation Errors**
   - Verify JSON format in JSONB/NVARCHAR(MAX) columns
   - Use proper JSON validation functions

## 📞 Support

For issues with database deployment:

1. Check the application logs for specific error messages
2. Verify database connectivity using connection strings
3. Ensure all prerequisites are met
4. Review the troubleshooting section in the User Manual

## 🔄 Version History

- **v1.0** (2025-01-20): Initial release with complete schema for all services
- Support for both PostgreSQL and SQL Server
- Comprehensive indexing and constraints
- Sample data for testing
