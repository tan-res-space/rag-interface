# RAG Interface System - Database Architecture Changes

## 📋 Overview

This document outlines the significant architectural change from a **multiple database approach** to a **single database with multiple schemas** approach for the RAG Interface System.

## 🔄 Architecture Change Summary

### Previous Architecture (v1.0)
- **5 separate databases**: One for each microservice
- **Database isolation**: Complete separation between services
- **Complex administration**: Multiple database backups, connections, and maintenance

### New Architecture (v2.0)
- **1 unified database**: Single database with logical schema separation
- **Schema-based isolation**: Each service has its own schema within the database
- **Simplified administration**: Single database backup, easier maintenance
- **Maintained security**: Schema-level permissions ensure service isolation

## 🗄️ Database Structure Comparison

### Before (Multiple Databases)
```
PostgreSQL Instance
├── error_reporting_db
├── user_management_db
├── verification_db
├── correction_engine_db
└── rag_integration_db

SQL Server Instance
├── ErrorReportingDB
├── UserManagementDB
├── VerificationDB
├── CorrectionEngineDB
└── RAGIntegrationDB
```

### After (Single Database with Schemas)
```
PostgreSQL: rag_interface_db
├── error_reporting schema
├── user_management schema
├── verification schema
├── correction_engine schema
└── rag_integration schema

SQL Server: RAGInterfaceDB
├── ErrorReporting schema
├── UserManagement schema
├── Verification schema
├── CorrectionEngine schema
└── RAGIntegration schema
```

## 🔧 Technical Changes

### 1. Database Creation Scripts

#### PostgreSQL Changes
- **File**: `01_create_databases.sql`
- **Before**: Created 5 separate databases
- **After**: Creates 1 database (`rag_interface_db`) with 5 schemas
- **Schema creation**: Added schema creation and permission management

#### SQL Server Changes
- **File**: `01_create_databases.sql`
- **Before**: Created 5 separate databases
- **After**: Creates 1 database (`RAGInterfaceDB`) with 5 schemas
- **Schema creation**: Added schema creation with proper naming conventions

### 2. Schema Scripts Updates

All schema scripts (02-06) have been updated to:
- Connect to the unified database instead of individual databases
- Use schema-qualified table names (e.g., `error_reporting.error_reports`)
- Set appropriate search paths for each service
- Maintain all existing table structures and relationships

### 3. Connection String Changes

#### Before
```bash
# Each service connected to its own database
ERS: postgresql://ers_user:password@host:5432/error_reporting_db
UMS: postgresql://ums_user:password@host:5432/user_management_db
VS: postgresql://vs_user:password@host:5432/verification_db
CES: postgresql://ces_user:password@host:5432/correction_engine_db
RIS: postgresql://ris_user:password@host:5432/rag_integration_db
```

#### After
```bash
# All services connect to the same database with schema-specific search paths
ERS: postgresql://ers_user:password@host:5432/rag_interface_db?options=-csearch_path%3Derror_reporting
UMS: postgresql://ums_user:password@host:5432/rag_interface_db?options=-csearch_path%3Duser_management
VS: postgresql://vs_user:password@host:5432/rag_interface_db?options=-csearch_path%3Dverification
CES: postgresql://ces_user:password@host:5432/rag_interface_db?options=-csearch_path%3Dcorrection_engine
RIS: postgresql://ris_user:password@host:5432/rag_interface_db?options=-csearch_path%3Drag_integration
```

### 4. Security Model Changes

#### User Permissions
- **Before**: Each user had full access to their dedicated database
- **After**: Each user has schema-specific permissions within the unified database

#### Cross-Schema Access
- **Error Reporting Service**: Can reference `user_management.users` for user lookups
- **Verification Service**: Can reference `correction_engine` tables for correction data
- **Correction Engine Service**: Can reference `rag_integration` for AI/ML integration

## 📊 Benefits of the New Architecture

### 1. Simplified Administration
- **Single backup**: One database backup instead of five
- **Unified monitoring**: Monitor one database instance
- **Easier maintenance**: Single point of database administration
- **Reduced complexity**: Fewer connection pools and configurations

### 2. Improved Performance
- **Connection pooling**: More efficient connection management
- **Cross-schema queries**: Easier data integration between services
- **Reduced overhead**: Less database instance overhead

### 3. Better Data Consistency
- **ACID transactions**: Cross-service transactions when needed
- **Referential integrity**: Foreign keys can span schemas
- **Unified constraints**: Global constraints across the system

### 4. Cost Optimization
- **Resource efficiency**: Single database instance uses resources more efficiently
- **Licensing**: Reduced database licensing costs (especially for SQL Server)
- **Infrastructure**: Simpler deployment and scaling

## 🔒 Security Considerations

### Schema-Level Isolation
- Each service user can only access their designated schema
- Cross-schema access is explicitly granted only where needed
- Maintains the principle of least privilege

### Permission Matrix
| User | Own Schema | Cross-Schema Access |
|------|------------|-------------------|
| ers_user | error_reporting (full) | user_management (usage) |
| ums_user | user_management (full) | None |
| vs_user | verification (full) | correction_engine (usage) |
| ces_user | correction_engine (full) | rag_integration (usage) |
| ris_user | rag_integration (full) | None |

## 🚀 Migration Guide

### For New Deployments
1. Use the updated database creation scripts
2. Run schema scripts in order (01-07)
3. Update application connection strings
4. Deploy with new environment variables

### For Existing Deployments
1. **Backup existing databases**
2. **Create new unified database**
3. **Migrate data schema by schema**
4. **Update application configurations**
5. **Test thoroughly before switching**

#### Migration Script Example
```bash
# 1. Backup existing databases
pg_dump -U postgres error_reporting_db > backup_ers.sql
pg_dump -U postgres user_management_db > backup_ums.sql
# ... repeat for all databases

# 2. Create new unified database
psql -U postgres -f 01_create_databases.sql

# 3. Create schemas
psql -U postgres -f 02_error_reporting_schema.sql
psql -U postgres -f 03_user_management_schema.sql
# ... repeat for all schemas

# 4. Migrate data (example for error reporting)
psql -U postgres -d rag_interface_db -c "SET search_path TO error_reporting;"
psql -U postgres -d rag_interface_db < backup_ers.sql
```

## 📝 Configuration Updates

### Environment Variables
- Added `DATABASE_NAME=rag_interface_db`
- Updated connection string templates
- Maintained individual user passwords for security

### Docker Compose Changes
- Updated all service database URLs
- Added schema-specific search path parameters
- Maintained service isolation through user permissions

## 🔍 Monitoring and Troubleshooting

### New Monitoring Points
- **Schema-level metrics**: Monitor performance per schema
- **Cross-schema queries**: Track inter-service data access
- **Connection distribution**: Monitor connections per service user

### Troubleshooting
- **Schema path issues**: Ensure search_path is correctly set
- **Permission errors**: Verify schema-level permissions
- **Cross-schema references**: Check foreign key constraints

## 📚 Documentation Updates

All documentation has been updated to reflect the new architecture:
- Database README with new connection examples
- User Manual with updated configuration
- Deployment guides with new procedures
- Troubleshooting guides with schema-specific diagnostics

## 🎯 Conclusion

The migration to a single database with multiple schemas provides:
- **Simplified operations** without sacrificing security
- **Better resource utilization** and performance
- **Easier maintenance** and administration
- **Maintained service isolation** through schema-level permissions

This architectural change positions the RAG Interface System for better scalability and operational efficiency while maintaining the microservices principles of service isolation and independence.

---

**Document Version**: 2.0  
**Last Updated**: 2025-01-20  
**Migration Status**: Complete  
**Compatibility**: Backward compatible with proper migration
