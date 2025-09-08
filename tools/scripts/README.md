# RAG Interface - Service Management Scripts

This directory contains 8 comprehensive scripts for managing the RAG Interface system services across local development and production deployment environments.

## 📋 **Script Overview**

The scripts are organized into two deployment categories with 4 scripts each:

### 🏠 **Local Development Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| `local-start.sh` | Start all local development services | `./local-start.sh [all\|infrastructure\|backend\|frontend\|tools]` |
| `local-stop.sh` | Stop all local development services | `./local-stop.sh [stop\|frontend\|backend\|infrastructure\|tools\|force\|clean\|local\|status]` |
| `local-logs.sh` | View logs for local development | `./local-logs.sh [service\|group\|all] [-f] [-n lines] [-l level]` |
| `local-setup.sh` | Setup local development environment | `./local-setup.sh [setup\|podman\|python\|nodejs\|environment\|verify]` |

### 🚀 **Production Deployment Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| `prod-start.sh` | Start all production services | `./prod-start.sh [all\|infrastructure\|backend\|frontend\|monitoring\|migrations]` |
| `prod-stop.sh` | Stop all production services | `./prod-stop.sh [stop\|graceful\|frontend\|backend\|infrastructure\|monitoring\|force\|clean\|backup\|maintenance]` |
| `prod-logs.sh` | View logs for production deployment | `./prod-logs.sh [service\|group\|all] [-f] [-n lines] [-l level]` |
| `prod-setup.sh` | Setup production environment | `./prod-setup.sh [setup\|podman\|environment\|directories\|ssl\|monitoring\|backup\|verify]` |

## 🎯 **Quick Start Guide**

### 1. **Local Development Setup**
```bash
# Setup local development environment
./tools/scripts/local-setup.sh

# Start all local development services
./tools/scripts/local-start.sh

# View logs
./tools/scripts/local-logs.sh all -f

# Stop services when done
./tools/scripts/local-stop.sh
```

### 2. **Production Deployment Setup**
```bash
# Setup production environment
./tools/scripts/prod-setup.sh

# Start all production services
./tools/scripts/prod-start.sh

# Monitor production logs
./tools/scripts/prod-logs.sh all -f -l ERROR

# Graceful shutdown
./tools/scripts/prod-stop.sh graceful
```

### 3. **Daily Development Workflow**
```bash
# Start infrastructure only
./tools/scripts/local-start.sh infrastructure

# Start specific service group
./tools/scripts/local-start.sh backend

# View specific service logs
./tools/scripts/local-logs.sh postgres -f

# Stop specific service group
./tools/scripts/local-stop.sh backend
```

## 🏗️ **System Architecture**

### **Container Runtime**
- **Podman Only**: All scripts use Podman and podman-compose exclusively
- **No Docker Support**: Docker references have been completely removed
- **Rootless Containers**: Designed for secure rootless container operation

### **Services Managed**

#### **Infrastructure Services**
- `postgres` - PostgreSQL database (Local: 5433, Prod: 5432)
- `redis` - Redis cache (Local: 6380, Prod: 6379)

#### **Backend Services**
- `error-reporting-service` - Error Reporting Service (Port: 8010)
- `user-management-service` - User Management Service (Port: 8011)
- `rag-integration-service` - RAG Integration Service (Port: 8012)
- `correction-engine-service` - Correction Engine Service (Port: 8013)
- `verification-service` - Verification Service (Port: 8014)

#### **Frontend Services**
- `frontend` - React/Vite application (Local: 3001, Prod: 80)

#### **Development Tools (Local Only)**
- `mailhog` - Email testing (Port: 8025)
- `adminer` - Database admin (Port: 8080)
- `redis-commander` - Redis management (Port: 8081)

#### **Production Services**
- `nginx` - Load balancer and reverse proxy
- `prometheus` - Metrics collection (Port: 9090)
- `grafana` - Monitoring dashboards (Port: 3000)

## 🔧 **Configuration**

### **Environment Files**
- `.env.local` - Local development configuration
- `.env.production` - Production deployment configuration
- `config/environments/development.env` - Development template
- `config/environments/production.env` - Production template

### **Compose Files**
- `podman-compose.dev.yml` - Local development services
- `deployment/podman/docker-compose.yml` - Production deployment services

### **Service Dependencies**
```
Infrastructure (PostgreSQL, Redis)
    ↓
Backend Services (ERS, UMS, RIS, CES, VS)
    ↓
Frontend (React Application)
    ↓
Monitoring & Tools (Prometheus, Grafana, Development Tools)
```

## 📖 **Detailed Script Documentation**

### **Local Development Scripts**

#### **local-start.sh**
Comprehensive local development startup with dependency management.

**Features:**
- Podman-only container runtime
- Prerequisite checking (.env.local, venv, node_modules)
- Sequential service startup with health checks
- Timeout handling and error recovery
- Service status reporting

**Commands:**
```bash
./local-start.sh all                   # Start all services (default)
./local-start.sh infrastructure        # Start only infrastructure
./local-start.sh backend               # Start only backend services
./local-start.sh frontend              # Start only frontend
./local-start.sh tools                 # Start only dev tools
```

#### **local-stop.sh**
Graceful shutdown for local development services.

**Features:**
- Selective service stopping
- Force stop for emergency situations
- Complete cleanup (removes volumes/data)
- Local process termination

**Commands:**
```bash
./local-stop.sh stop                   # Stop all services (default)
./local-stop.sh frontend               # Stop only frontend
./local-stop.sh backend                # Stop only backend
./local-stop.sh infrastructure         # Stop only infrastructure
./local-stop.sh tools                  # Stop only dev tools
./local-stop.sh force                  # Force stop all containers
./local-stop.sh clean                  # Complete cleanup (destructive)
./local-stop.sh local                  # Stop local processes
```

#### **local-logs.sh**
Comprehensive log viewing for local development.

**Features:**
- Individual service log viewing
- Service group log aggregation
- Real-time log following
- Log level filtering
- Advanced monitoring with filters

**Commands:**
```bash
./local-logs.sh <service_name>          # Show service logs
./local-logs.sh <service_name> -f       # Follow logs in real-time
./local-logs.sh infrastructure          # Infrastructure service logs
./local-logs.sh backend                 # Backend service logs
./local-logs.sh all -f                  # Follow all service logs
./local-logs.sh monitor ERROR backend   # Monitor backend for errors
```

#### **local-setup.sh**
Complete local development environment setup.

**Features:**
- System requirements checking
- Podman installation and configuration
- Python virtual environment setup
- Node.js dependency management
- Environment configuration creation
- Pre-commit hooks setup

**Commands:**
```bash
./local-setup.sh setup                 # Complete setup (default)
./local-setup.sh podman                # Setup Podman only
./local-setup.sh python                # Setup Python environment only
./local-setup.sh nodejs                # Setup Node.js environment only
./local-setup.sh environment           # Setup environment config only
./local-setup.sh verify                # Verify setup only
```

### **Production Deployment Scripts**

#### **prod-start.sh**
Comprehensive production deployment startup.

**Features:**
- Production environment validation
- Image pulling and updates
- Database migrations
- Sequential service startup with extended timeouts
- Production monitoring integration

**Commands:**
```bash
./prod-start.sh all                     # Start all services (default)
./prod-start.sh infrastructure          # Start only infrastructure
./prod-start.sh backend                 # Start only backend services
./prod-start.sh frontend                # Start only frontend
./prod-start.sh monitoring              # Start only monitoring
./prod-start.sh migrations              # Run database migrations only
```

#### **prod-stop.sh**
Production-grade shutdown with backup and maintenance options.

**Features:**
- Graceful shutdown sequence
- Load balancer draining
- Backup creation before shutdown
- Maintenance mode support
- Emergency force stop

**Commands:**
```bash
./prod-stop.sh stop                    # Stop all services (default)
./prod-stop.sh graceful                # Graceful shutdown sequence
./prod-stop.sh backup                  # Create backup before shutdown
./prod-stop.sh maintenance             # Enable maintenance mode
./prod-stop.sh clean                   # Complete cleanup (destructive)
./prod-stop.sh force                   # Emergency stop
```

#### **prod-logs.sh**
Advanced production log management.

**Features:**
- Production log viewing with filtering
- Log level filtering (ERROR, WARNING, INFO, DEBUG)
- Real-time monitoring
- Log export functionality
- Service group aggregation

**Commands:**
```bash
./prod-logs.sh <service_name>          # Show service logs
./prod-logs.sh backend -l ERROR        # Show backend errors only
./prod-logs.sh all -f                  # Follow all service logs
./prod-logs.sh export all 5000         # Export last 5000 lines
./prod-logs.sh monitor "database" backend ERROR  # Monitor backend for database errors
```

#### **prod-setup.sh**
Complete production environment setup.

**Features:**
- Production system requirements checking
- Secure environment configuration generation
- SSL certificate setup
- Production monitoring configuration
- Automated backup system setup

**Commands:**
```bash
./prod-setup.sh setup                  # Complete setup (default)
./prod-setup.sh environment            # Setup environment config only
./prod-setup.sh ssl                    # Setup SSL certificates only
./prod-setup.sh monitoring             # Setup monitoring only
./prod-setup.sh backup                 # Setup backup system only
./prod-setup.sh verify                 # Verify setup only
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Podman Not Available**
```bash
# Check if Podman is running
podman info

# Start Podman service (if using system service)
sudo systemctl start podman

# Enable Podman socket for user
systemctl --user enable podman.socket
systemctl --user start podman.socket
```

#### **Port Conflicts**
```bash
# Check what's using a port
sudo netstat -tulpn | grep :5433
sudo lsof -i :5433

# Kill process using port
sudo kill -9 <PID>
```

#### **Permission Issues**
```bash
# Make scripts executable
chmod +x tools/scripts/*.sh

# Fix Podman permissions
podman system reset

# Check rootless configuration
podman info | grep -i rootless
```

#### **Environment Issues**
```bash
# Create .env.local from template
cp config/environments/development.env .env.local

# Create .env.production from template
cp config/environments/production.env .env.production

# Check environment loading
source .env.local && env | grep -E "(DB_|REDIS_|FRONTEND_)"
```

### **Service Health Checks**

#### **PostgreSQL**
```bash
# Local development
PGPASSWORD=dev_password_2025 psql -h localhost -p 5433 -U rag_user -d rag_interface_dev -c "SELECT version();"

# Production
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U rag_user -d rag_interface_prod -c "SELECT version();"
```

#### **Redis**
```bash
# Local development
redis-cli -h localhost -p 6380 -a dev_redis_2025 ping

# Production
redis-cli -h localhost -p 6379 -a $REDIS_PASSWORD ping
```

#### **HTTP Services**
```bash
# Local development
curl http://localhost:8010/health  # Error Reporting
curl http://localhost:8011/health  # User Management
curl http://localhost:8012/health  # RAG Integration
curl http://localhost:3001         # Frontend

# Production
curl http://localhost:8010/health  # Error Reporting
curl http://localhost:80           # Frontend
```

## 📝 **Workflow Examples**

### **Local Development Workflow**
```bash
# 1. Setup (first time only)
./tools/scripts/local-setup.sh

# 2. Start all services
./tools/scripts/local-start.sh

# 3. View logs
./tools/scripts/local-logs.sh all -f

# 4. Stop when done
./tools/scripts/local-stop.sh
```

### **Frontend-Only Development**
```bash
# 1. Start infrastructure
./tools/scripts/local-start.sh infrastructure

# 2. Start frontend
./tools/scripts/local-start.sh frontend

# 3. View frontend logs
./tools/scripts/local-logs.sh frontend -f

# 4. Stop frontend when done
./tools/scripts/local-stop.sh frontend
```

### **Backend Service Development**
```bash
# 1. Start infrastructure
./tools/scripts/local-start.sh infrastructure

# 2. Start backend services
./tools/scripts/local-start.sh backend

# 3. Monitor specific service
./tools/scripts/local-logs.sh error-reporting-service -f

# 4. Stop backend when done
./tools/scripts/local-stop.sh backend
```

### **Production Deployment Workflow**
```bash
# 1. Setup production environment (first time only)
./tools/scripts/prod-setup.sh

# 2. Start production services
./tools/scripts/prod-start.sh

# 3. Monitor production logs
./tools/scripts/prod-logs.sh all -f -l ERROR

# 4. Graceful shutdown
./tools/scripts/prod-stop.sh graceful
```

### **Production Maintenance**
```bash
# 1. Create backup before maintenance
./tools/scripts/prod-stop.sh backup

# 2. Enable maintenance mode
./tools/scripts/prod-stop.sh maintenance

# 3. Perform maintenance tasks
# ... maintenance work ...

# 4. Restart services
./tools/scripts/prod-start.sh

# 5. Monitor for issues
./tools/scripts/prod-logs.sh all -f -l WARNING
```

## 🔗 **Related Documentation**

- [Main README](../../README.md) - Project overview
- [Development Guide](../../docs/development.md) - Development setup
- [API Documentation](../../docs/api.md) - API reference
- [Deployment Guide](../../docs/deployment.md) - Production deployment

## 🤝 **Contributing**

When adding new scripts:
1. Follow the 8-script structure (4 local + 4 production)
2. Use Podman and podman-compose exclusively
3. Include comprehensive error handling
4. Add logging with consistent formatting
5. Make scripts executable (`chmod +x`)
6. Update this README with new script documentation
7. Test with Podman in both rootless and rootful modes

## 📋 **Script Summary**

The RAG Interface system now uses exactly 8 scripts organized into two deployment categories:

**Local Development (4 scripts):**
- `local-start.sh` - Start local development services
- `local-stop.sh` - Stop local development services
- `local-logs.sh` - View local development logs
- `local-setup.sh` - Setup local development environment

**Production Deployment (4 scripts):**
- `prod-start.sh` - Start production services
- `prod-stop.sh` - Stop production services
- `prod-logs.sh` - View production logs
- `prod-setup.sh` - Setup production environment

All scripts use **Podman exclusively** with no Docker fallback, ensuring consistent container runtime behavior across all environments.
