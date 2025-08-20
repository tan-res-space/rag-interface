# RAG Interface System - User Manual

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [Starting the System](#starting-the-system)
6. [Using the Application](#using-the-application)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)
9. [Security](#security)
10. [Support](#support)

## 🎯 Introduction

The RAG Interface System is a comprehensive platform for managing ASR (Automatic Speech Recognition) error reporting and correction. This manual will guide you through installing, configuring, and operating the system.

### What This System Does

- **Error Reporting**: QA personnel can report errors found in ASR transcriptions
- **Intelligent Correction**: AI-powered correction suggestions using RAG (Retrieval-Augmented Generation)
- **Verification**: Quality assurance workflow for reviewing corrections
- **Analytics**: Performance metrics and reporting dashboards
- **User Management**: Role-based access control and authentication

### System Architecture

The system consists of:
- **Frontend**: Web-based user interface (React application)
- **Backend**: 5 microservices (Python FastAPI)
- **Database**: PostgreSQL or SQL Server
- **Cache**: Redis for performance
- **Vector Database**: For AI/ML functionality (Pinecone, Weaviate, etc.)

## 💻 System Requirements

### Minimum Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 50 GB | 100 GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Software Requirements

#### Operating System
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **Windows**: Windows 10/11, Windows Server 2019+
- **macOS**: macOS 11+ (for development only)

#### Container Runtime
- **Podman** 4.0+ (recommended) OR
- **Docker** 20.10+ with Docker Compose

#### Database (choose one)
- **PostgreSQL** 12+ (recommended)
- **SQL Server** 2017+

#### Additional Software
- **Git** (for deployment)
- **curl** (for health checks)
- **Web browser** (Chrome, Firefox, Safari, Edge)

## 🚀 Installation Guide

### Step 1: Install Prerequisites

#### On Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Podman
sudo apt install -y podman podman-compose

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Git and curl
sudo apt install -y git curl
```

#### On CentOS/RHEL
```bash
# Update system
sudo dnf update -y

# Install Podman
sudo dnf install -y podman podman-compose

# Install PostgreSQL
sudo dnf install -y postgresql postgresql-server postgresql-contrib

# Install Git and curl
sudo dnf install -y git curl
```

#### On Windows
1. Install **Docker Desktop** from https://docker.com/products/docker-desktop
2. Install **Git** from https://git-scm.com/download/win
3. Install **PostgreSQL** from https://postgresql.org/download/windows

### Step 2: Download the System

```bash
# Clone the repository
git clone https://github.com/your-org/rag-interface.git
cd rag-interface

# Navigate to deployment directory
cd deployment/podman
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit configuration (see Configuration section)
nano .env  # or use your preferred editor
```

### Step 4: Deploy the System

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The deployment script will:
1. Check prerequisites
2. Build container images
3. Start database services
4. Initialize database schemas
5. Start backend services
6. Start frontend application
7. Perform health checks

## ⚙️ Configuration

### Environment Variables

Edit the `.env` file to configure your system:

#### Database Configuration
```bash
# PostgreSQL settings
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_PORT=5432

# Service database passwords
ERS_DB_PASSWORD=ers_password_here
UMS_DB_PASSWORD=ums_password_here
VS_DB_PASSWORD=vs_password_here
CES_DB_PASSWORD=ces_password_here
RIS_DB_PASSWORD=ris_password_here
```

#### Security Settings
```bash
# JWT secret for authentication
JWT_SECRET_KEY=your_very_long_random_secret_key

# Redis password
REDIS_PASSWORD=redis_password_here
```

#### API Keys (Required for AI Features)
```bash
# OpenAI API key for embeddings
OPENAI_API_KEY=sk-your-openai-key-here

# Pinecone API key for vector database
PINECONE_API_KEY=your-pinecone-key-here
```

#### Service Ports
```bash
ERS_PORT=8000          # Error Reporting Service
UMS_PORT=8001          # User Management Service
RIS_PORT=8002          # RAG Integration Service
CES_PORT=8003          # Correction Engine Service
VS_PORT=8004           # Verification Service
FRONTEND_PORT=3000     # Frontend Application
```

### Security Best Practices

1. **Change Default Passwords**: Never use default passwords in production
2. **Use Strong Passwords**: Minimum 16 characters with mixed case, numbers, and symbols
3. **Secure API Keys**: Store API keys securely and rotate them regularly
4. **Network Security**: Use firewalls to restrict access to necessary ports only

## 🎬 Starting the System

### Automatic Startup (Recommended)

```bash
# Navigate to deployment directory
cd deployment/podman

# Start all services
./deploy.sh
```

### Manual Startup

```bash
# Start database services first
podman-compose up -d postgres redis

# Wait for databases to be ready (30 seconds)
sleep 30

# Start backend services
podman-compose up -d error-reporting-service user-management-service rag-integration-service correction-engine-service verification-service

# Start frontend
podman-compose up -d frontend
```

### Verify System Status

```bash
# Check all services
podman-compose ps

# Check service logs
podman-compose logs frontend
podman-compose logs error-reporting-service
```

### Access the Application

Once started, access the system at:
- **Main Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs (Error Reporting Service)

### Default Login Credentials

**⚠️ IMPORTANT: Change these immediately after first login!**

| Username | Password | Role |
|----------|----------|------|
| admin | AdminPassword123! | Administrator |
| qa_supervisor | QASuper123! | QA Supervisor |
| qa_user | QAUser123! | QA Personnel |
| mts_user | MTSUser123! | MTS Personnel |

## 📱 Using the Application

### First-Time Setup

1. **Access the Application**
   - Open your web browser
   - Navigate to http://localhost:3000
   - You should see the login page

2. **Login as Administrator**
   - Username: `admin`
   - Password: `AdminPassword123!`

3. **Change Default Password**
   - Go to Profile Settings
   - Change your password immediately
   - Use a strong, unique password

4. **Create User Accounts**
   - Navigate to User Management
   - Create accounts for your team members
   - Assign appropriate roles

### User Roles and Permissions

| Role | Permissions |
|------|-------------|
| **Administrator** | Full system access, user management, system configuration |
| **QA Supervisor** | View/create/edit errors, view analytics, manage QA team |
| **QA Personnel** | View/create/edit errors, basic reporting |
| **MTS Personnel** | View errors and analytics (read-only) |
| **Viewer** | View-only access to errors and analytics |

### Main Features

#### Error Reporting
1. Navigate to "Error Reports"
2. Click "New Error Report"
3. Fill in the required information:
   - Original text (from ASR)
   - Corrected text
   - Error categories
   - Severity level
   - Context notes
4. Submit the report

#### Verification Workflow
1. Navigate to "Verification Dashboard"
2. Review pending corrections
3. Approve, reject, or request changes
4. Add feedback and quality scores

#### Analytics and Reporting
1. Navigate to "Analytics"
2. View performance metrics
3. Generate custom reports
4. Export data in various formats

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: Cannot Access the Application

**Symptoms**: Browser shows "This site can't be reached" or connection timeout

**Solutions**:
1. Check if services are running:
   ```bash
   podman-compose ps
   ```

2. Check service logs:
   ```bash
   podman-compose logs frontend
   ```

3. Verify ports are not blocked:
   ```bash
   curl http://localhost:3000/health
   ```

4. Check firewall settings:
   ```bash
   sudo ufw status  # Ubuntu
   sudo firewall-cmd --list-all  # CentOS/RHEL
   ```

#### Issue: Database Connection Errors

**Symptoms**: Services fail to start with database connection errors

**Solutions**:
1. Check PostgreSQL status:
   ```bash
   podman-compose logs postgres
   ```

2. Verify database credentials in `.env` file

3. Check if PostgreSQL is accepting connections:
   ```bash
   podman-compose exec postgres pg_isready -U postgres
   ```

4. Reset database if needed:
   ```bash
   podman-compose down postgres
   podman volume rm podman_postgres_data
   podman-compose up -d postgres
   ```

#### Issue: Authentication Failures

**Symptoms**: Cannot login or "Invalid credentials" errors

**Solutions**:
1. Verify you're using correct default credentials
2. Check if User Management Service is running:
   ```bash
   podman-compose logs user-management-service
   ```

3. Reset user passwords via database:
   ```bash
   podman-compose exec postgres psql -U postgres -d user_management_db
   ```

#### Issue: Slow Performance

**Symptoms**: Application loads slowly or times out

**Solutions**:
1. Check system resources:
   ```bash
   htop  # or top
   df -h  # disk space
   ```

2. Check Redis cache:
   ```bash
   podman-compose logs redis
   ```

3. Optimize database:
   ```bash
   podman-compose exec postgres psql -U postgres -c "VACUUM ANALYZE;"
   ```

### Diagnostic Commands

#### Check Service Health
```bash
# Check all services
for service in frontend error-reporting-service user-management-service rag-integration-service correction-engine-service verification-service; do
  echo "Checking $service..."
  podman-compose exec $service curl -f http://localhost:$(podman-compose port $service | cut -d: -f2)/health || echo "FAILED"
done
```

#### View Service Logs
```bash
# View logs for all services
podman-compose logs

# View logs for specific service
podman-compose logs -f frontend

# View last 100 lines
podman-compose logs --tail=100 error-reporting-service
```

#### Check Database Status
```bash
# PostgreSQL status
podman-compose exec postgres pg_isready -U postgres

# Redis status
podman-compose exec redis redis-cli ping

# Database connections
podman-compose exec postgres psql -U postgres -c "SELECT datname, numbackends FROM pg_stat_database;"
```

### Component-Specific Troubleshooting

#### Frontend Issues
- **Blank page**: Check browser console for JavaScript errors
- **API errors**: Verify backend services are running
- **Slow loading**: Check network tab in browser developer tools

#### Backend Service Issues
- **Service won't start**: Check environment variables and dependencies
- **Database errors**: Verify database connection and credentials
- **Memory issues**: Increase container memory limits

#### Database Issues
- **Connection refused**: Check if PostgreSQL is running and accepting connections
- **Authentication failed**: Verify database credentials
- **Disk space**: Ensure adequate disk space for database files

## 🔄 Maintenance

### Regular Maintenance Tasks

#### Daily Tasks
1. **Monitor System Health**
   ```bash
   # Check service status
   podman-compose ps
   
   # Check disk space
   df -h
   
   # Check logs for errors
   podman-compose logs --since=24h | grep -i error
   ```

#### Weekly Tasks
1. **Database Maintenance**
   ```bash
   # Vacuum and analyze database
   podman-compose exec postgres psql -U postgres -c "VACUUM ANALYZE;"
   
   # Clean up old logs
   podman-compose exec postgres psql -U postgres -d error_reporting_db -c "DELETE FROM error_audit_logs WHERE performed_at < NOW() - INTERVAL '30 days';"
   ```

2. **Cache Cleanup**
   ```bash
   # Clean expired cache entries
   podman-compose exec redis redis-cli FLUSHDB
   ```

#### Monthly Tasks
1. **System Updates**
   ```bash
   # Update container images
   podman-compose pull
   podman-compose up -d
   
   # Update system packages
   sudo apt update && sudo apt upgrade -y  # Ubuntu
   sudo dnf update -y  # CentOS/RHEL
   ```

2. **Security Review**
   - Review user accounts and permissions
   - Check for failed login attempts
   - Update passwords and API keys
   - Review system logs for security events

### Backup Procedures

#### Database Backup
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup all databases
for db in error_reporting_db user_management_db verification_db correction_engine_db rag_integration_db; do
  podman-compose exec postgres pg_dump -U postgres $db > backups/$(date +%Y%m%d)/${db}_backup.sql
done

# Compress backups
tar -czf backups/$(date +%Y%m%d).tar.gz backups/$(date +%Y%m%d)/
```

#### Configuration Backup
```bash
# Backup configuration files
cp .env backups/$(date +%Y%m%d)/env_backup
cp docker-compose.yml backups/$(date +%Y%m%d)/compose_backup.yml
```

#### Restore from Backup
```bash
# Stop services
podman-compose down

# Restore database
podman-compose up -d postgres
sleep 30
podman-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS error_reporting_db;"
podman-compose exec postgres psql -U postgres -c "CREATE DATABASE error_reporting_db;"
podman-compose exec postgres psql -U postgres error_reporting_db < backups/20250120/error_reporting_db_backup.sql

# Restart services
podman-compose up -d
```

### Performance Monitoring

#### Key Metrics to Monitor
1. **System Resources**
   - CPU usage
   - Memory usage
   - Disk space
   - Network I/O

2. **Application Metrics**
   - Response times
   - Error rates
   - Active users
   - Database connections

3. **Database Performance**
   - Query execution times
   - Connection pool usage
   - Lock waits
   - Index usage

#### Monitoring Commands
```bash
# System resources
htop
iostat -x 1
netstat -i

# Container resources
podman stats

# Database performance
podman-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

## 🔒 Security

### Security Checklist

#### Initial Setup
- [ ] Change all default passwords
- [ ] Configure strong JWT secret key
- [ ] Set up proper firewall rules
- [ ] Enable SSL/TLS certificates
- [ ] Configure secure API keys

#### Ongoing Security
- [ ] Regular password updates
- [ ] Monitor failed login attempts
- [ ] Review user permissions quarterly
- [ ] Update system packages monthly
- [ ] Backup encryption keys securely

### Network Security

#### Firewall Configuration
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 5432/tcp  # PostgreSQL (if external access needed)
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

#### SSL/TLS Setup
For production deployment, configure SSL certificates:
1. Obtain SSL certificates (Let's Encrypt, commercial CA)
2. Configure reverse proxy (nginx, Apache)
3. Update application URLs to use HTTPS
4. Redirect HTTP to HTTPS

### Access Control

#### User Management Best Practices
1. **Principle of Least Privilege**: Grant minimum necessary permissions
2. **Regular Access Review**: Review user accounts quarterly
3. **Strong Password Policy**: Enforce complex passwords
4. **Account Lockout**: Configure automatic lockout after failed attempts
5. **Session Management**: Set appropriate session timeouts

## 📞 Support

### Getting Help

#### Documentation
- **User Manual**: This document
- **API Documentation**: Available at service endpoints `/docs`
- **Architecture Documentation**: See `documents/` directory

#### Log Files
Important log locations:
- **Application Logs**: `podman-compose logs [service-name]`
- **System Logs**: `/var/log/syslog` (Linux)
- **Database Logs**: `podman-compose logs postgres`

#### Common Support Scenarios

1. **Performance Issues**
   - Collect system metrics
   - Review application logs
   - Check database performance
   - Monitor network connectivity

2. **Authentication Problems**
   - Verify user credentials
   - Check User Management Service logs
   - Review JWT configuration
   - Validate database connectivity

3. **Data Issues**
   - Check database integrity
   - Review recent changes
   - Verify backup availability
   - Check for data corruption

#### Contact Information
- **Technical Support**: support@raginterface.com
- **Documentation Issues**: docs@raginterface.com
- **Security Issues**: security@raginterface.com

### Reporting Issues

When reporting issues, please include:
1. **System Information**
   - Operating system and version
   - Container runtime (Podman/Docker) version
   - System resources (CPU, RAM, disk)

2. **Error Details**
   - Exact error messages
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Log Files**
   - Relevant service logs
   - System logs
   - Database logs
   - Browser console logs (for frontend issues)

4. **Configuration**
   - Environment variables (sanitized)
   - Service configuration
   - Network setup

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-20  
**Next Review**: 2025-04-20
