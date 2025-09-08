#!/bin/bash

# =====================================================
# RAG Interface - Production Environment Setup Script
# =====================================================
# This script sets up the production deployment environment
# using Podman and podman-compose exclusively
# =====================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Generate secure random password
generate_password() {
    local length="${1:-32}"
    openssl rand -base64 "$length" | tr -d "=+/" | cut -c1-"$length"
}

# Check production system requirements
check_production_requirements() {
    log_step "Checking production system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Operating System: Linux (production ready)"
    else
        log_warning "Operating System: $OSTYPE (Linux recommended for production)"
    fi
    
    # Check architecture
    local arch=$(uname -m)
    log_info "Architecture: $arch"
    
    # Check available memory (minimum 8GB for production)
    if command_exists free; then
        local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$mem_gb" -ge 8 ]; then
            log_success "Memory: ${mem_gb}GB (sufficient for production)"
        else
            log_warning "Memory: ${mem_gb}GB (minimum 8GB recommended for production)"
        fi
    fi
    
    # Check available disk space (minimum 50GB for production)
    local disk_gb=$(df -BG "$PROJECT_ROOT" | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$disk_gb" -ge 50 ]; then
        log_success "Disk Space: ${disk_gb}GB available (sufficient for production)"
    else
        log_warning "Disk Space: ${disk_gb}GB available (minimum 50GB recommended for production)"
    fi
    
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root (not recommended for production)"
        log_info "Consider using a dedicated service user for production deployment"
    fi
}

# Setup Podman for production
setup_production_podman() {
    log_step "Setting up Podman for production..."
    
    if command_exists podman; then
        local podman_version=$(podman --version | cut -d' ' -f3)
        log_success "Podman is installed: $podman_version"
        
        # Test Podman
        if podman info >/dev/null 2>&1; then
            log_success "Podman is working correctly"
        else
            log_error "Podman is installed but not working properly"
            log_info "Please configure Podman for production use"
            exit 1
        fi
    else
        log_error "Podman is not installed"
        log_info "Please install Podman for production deployment"
        exit 1
    fi
    
    # Check podman-compose
    if command_exists podman-compose; then
        local compose_version=$(podman-compose --version | cut -d' ' -f3)
        log_success "podman-compose is installed: $compose_version"
    else
        log_error "podman-compose is not installed"
        log_info "Please install podman-compose for production deployment"
        exit 1
    fi
    
    # Configure Podman for production
    log_info "Configuring Podman for production..."
    
    # Enable Podman socket for API access
    if systemctl --user is-enabled podman.socket >/dev/null 2>&1; then
        log_success "Podman socket is enabled"
    else
        log_info "Enabling Podman socket..."
        systemctl --user enable podman.socket
        systemctl --user start podman.socket
        log_success "Podman socket enabled and started"
    fi
    
    # Configure resource limits
    log_info "Configuring resource limits for production..."
    
    # Create or update containers.conf for production settings
    local config_dir="$HOME/.config/containers"
    mkdir -p "$config_dir"
    
    cat > "$config_dir/containers.conf" << 'EOF'
[containers]
# Production container configuration
default_ulimits = [
  "nofile=65536:65536",
  "nproc=8192:8192"
]

# Security settings
seccomp_profile = "/usr/share/containers/seccomp.json"
apparmor_profile = "containers-default-0.44.0"

# Resource management
cgroup_manager = "systemd"
events_logger = "journald"

# Network settings
dns_servers = ["8.8.8.8", "8.8.4.4"]

[engine]
# Production engine settings
runtime = "runc"
stop_timeout = 30
EOF
    
    log_success "Podman configured for production"
}

# Setup production environment configuration
setup_production_environment() {
    log_step "Setting up production environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Create .env.production if it doesn't exist
    if [ ! -f ".env.production" ]; then
        log_info "Creating .env.production with secure defaults..."
        
        # Generate secure passwords
        local postgres_password=$(generate_password 32)
        local redis_password=$(generate_password 32)
        local jwt_secret=$(generate_password 64)
        
        cat > .env.production << EOF
# RAG Interface Production Configuration
# Generated on $(date)

# Database Configuration
POSTGRES_DB=rag_interface_prod
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=$postgres_password
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PASSWORD=$redis_password
REDIS_PORT=6379

# Security Configuration
JWT_SECRET_KEY=$jwt_secret
ENCRYPTION_KEY=$(generate_password 32)

# Service Ports
ERS_PORT=8010
UMS_PORT=8011
RIS_PORT=8012
CES_PORT=8013
VS_PORT=8014
FRONTEND_PORT=80

# Monitoring Ports
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# SSL/TLS Configuration
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/rag-interface.crt
SSL_KEY_PATH=/etc/ssl/private/rag-interface.key

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30

# Performance Configuration
WORKER_PROCESSES=4
MAX_CONNECTIONS=1000
TIMEOUT=30

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=7

# Monitoring Configuration
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
ALERT_EMAIL=admin@example.com

# External Services
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=$(generate_password 16)

# API Keys (replace with actual values)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
EOF
        
        # Secure the file
        chmod 600 .env.production
        
        log_success ".env.production created with secure defaults"
        log_warning "Please review and update .env.production with your actual configuration"
        log_warning "Especially update API keys and external service credentials"
        
    else
        log_info ".env.production already exists"
        
        # Validate existing configuration
        log_info "Validating existing production configuration..."
        
        source .env.production
        
        local issues=0
        
        # Check required variables
        local required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "JWT_SECRET_KEY")
        for var in "${required_vars[@]}"; do
            if [ -z "${!var:-}" ]; then
                log_error "Required environment variable $var is not set"
                issues=$((issues + 1))
            fi
        done
        
        if [ $issues -eq 0 ]; then
            log_success "Production configuration validation passed"
        else
            log_error "Production configuration validation failed ($issues issues)"
            exit 1
        fi
    fi
}

# Setup production directories
setup_production_directories() {
    log_step "Setting up production directories..."
    
    cd "$PROJECT_ROOT"
    
    # Create production directories
    local dirs=(
        "logs/production"
        "backups/database"
        "backups/redis"
        "backups/config"
        "ssl/certs"
        "ssl/private"
        "data/postgres"
        "data/redis"
        "monitoring/prometheus"
        "monitoring/grafana"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done
    
    # Set appropriate permissions
    chmod 700 ssl/private backups data
    chmod 755 logs monitoring
    
    log_success "Production directories created"
}

# Setup SSL certificates
setup_ssl_certificates() {
    log_step "Setting up SSL certificates..."
    
    cd "$PROJECT_ROOT"
    
    local ssl_dir="ssl"
    local cert_file="$ssl_dir/certs/rag-interface.crt"
    local key_file="$ssl_dir/private/rag-interface.key"
    
    if [ ! -f "$cert_file" ] || [ ! -f "$key_file" ]; then
        log_info "Generating self-signed SSL certificate for development/testing..."
        
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$key_file" \
            -out "$cert_file" \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=rag-interface.local" \
            2>/dev/null
        
        # Set permissions
        chmod 600 "$key_file"
        chmod 644 "$cert_file"
        
        log_success "Self-signed SSL certificate generated"
        log_warning "For production, replace with certificates from a trusted CA"
    else
        log_info "SSL certificates already exist"
    fi
}

# Setup production monitoring
setup_production_monitoring() {
    log_step "Setting up production monitoring..."
    
    cd "$PROJECT_ROOT"
    
    # Create Prometheus configuration
    local prometheus_config="monitoring/prometheus/prometheus.yml"
    if [ ! -f "$prometheus_config" ]; then
        log_info "Creating Prometheus configuration..."
        
        cat > "$prometheus_config" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'rag-interface-services'
    static_configs:
      - targets: 
        - 'error-reporting-service:8010'
        - 'user-management-service:8011'
        - 'rag-integration-service:8012'
        - 'correction-engine-service:8013'
        - 'verification-service:8014'
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
EOF
        
        log_success "Prometheus configuration created"
    fi
    
    # Create Grafana provisioning
    local grafana_dir="monitoring/grafana"
    mkdir -p "$grafana_dir/dashboards" "$grafana_dir/datasources"
    
    if [ ! -f "$grafana_dir/datasources/prometheus.yml" ]; then
        cat > "$grafana_dir/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
        log_success "Grafana datasource configuration created"
    fi
}

# Setup production backup system
setup_production_backup() {
    log_step "Setting up production backup system..."
    
    cd "$PROJECT_ROOT"
    
    # Create backup script
    local backup_script="scripts/backup-production.sh"
    if [ ! -f "$backup_script" ]; then
        log_info "Creating production backup script..."
        
        mkdir -p "$(dirname "$backup_script")"
        
        cat > "$backup_script" << 'EOF'
#!/bin/bash
# Production backup script for RAG Interface

set -euo pipefail

BACKUP_DIR="/var/backups/rag-interface"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
podman exec rag-postgres pg_dumpall -U postgres | gzip > "$BACKUP_DIR/postgres_$DATE.sql.gz"

# Backup Redis
podman exec rag-redis redis-cli --rdb - | gzip > "$BACKUP_DIR/redis_$DATE.rdb.gz"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env.production ssl/

# Clean old backups
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
EOF
        
        chmod +x "$backup_script"
        log_success "Production backup script created"
    fi
    
    # Setup cron job for automated backups
    log_info "Setting up automated backup schedule..."
    
    # Add cron job if not exists
    if ! crontab -l 2>/dev/null | grep -q "backup-production.sh"; then
        (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_ROOT/$backup_script") | crontab -
        log_success "Automated backup schedule configured (daily at 2 AM)"
    else
        log_info "Automated backup schedule already configured"
    fi
}

# Verify production setup
verify_production_setup() {
    log_step "Verifying production setup..."
    
    cd "$PROJECT_ROOT"
    
    local issues=0
    
    # Check Podman
    if command_exists podman && podman info >/dev/null 2>&1; then
        log_success "✓ Podman is working"
    else
        log_error "✗ Podman is not working"
        issues=$((issues + 1))
    fi
    
    # Check podman-compose
    if command_exists podman-compose; then
        log_success "✓ podman-compose is available"
    else
        log_error "✗ podman-compose is not available"
        issues=$((issues + 1))
    fi
    
    # Check production compose file
    if [ -f "deployment/podman/docker-compose.yml" ]; then
        log_success "✓ Production compose file exists"
    else
        log_error "✗ Production compose file is missing"
        issues=$((issues + 1))
    fi
    
    # Check environment configuration
    if [ -f ".env.production" ]; then
        log_success "✓ Production environment configuration exists"
    else
        log_error "✗ Production environment configuration is missing"
        issues=$((issues + 1))
    fi
    
    # Check SSL certificates
    if [ -f "ssl/certs/rag-interface.crt" ] && [ -f "ssl/private/rag-interface.key" ]; then
        log_success "✓ SSL certificates are available"
    else
        log_error "✗ SSL certificates are missing"
        issues=$((issues + 1))
    fi
    
    # Check directories
    local required_dirs=("logs/production" "backups" "data" "monitoring")
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "✓ Directory exists: $dir"
        else
            log_error "✗ Directory missing: $dir"
            issues=$((issues + 1))
        fi
    done
    
    echo ""
    if [ $issues -eq 0 ]; then
        log_success "Production setup verification completed successfully!"
        log_info "You can now start the production deployment with:"
        echo "  ./tools/scripts/prod-start.sh"
    else
        log_error "Production setup verification found $issues issue(s)"
        log_info "Please resolve the issues above and run this script again"
        exit 1
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup          - Complete production setup (default)"
    echo "  podman         - Setup Podman for production only"
    echo "  environment    - Setup environment configuration only"
    echo "  directories    - Setup production directories only"
    echo "  ssl            - Setup SSL certificates only"
    echo "  monitoring     - Setup monitoring configuration only"
    echo "  backup         - Setup backup system only"
    echo "  verify         - Verify production setup only"
    echo ""
    echo "Examples:"
    echo "  $0             # Complete production setup"
    echo "  $0 verify      # Verify current setup"
    echo "  $0 ssl         # Setup SSL certificates only"
}

# Main function
main() {
    local command="${1:-setup}"
    
    log_info "RAG Interface Production Environment Setup"
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    case "$command" in
        "setup")
            check_production_requirements
            setup_production_podman
            setup_production_environment
            setup_production_directories
            setup_ssl_certificates
            setup_production_monitoring
            setup_production_backup
            verify_production_setup
            ;;
        "podman")
            setup_production_podman
            ;;
        "environment")
            setup_production_environment
            ;;
        "directories")
            setup_production_directories
            ;;
        "ssl")
            setup_ssl_certificates
            ;;
        "monitoring")
            setup_production_monitoring
            ;;
        "backup")
            setup_production_backup
            ;;
        "verify")
            verify_production_setup
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
