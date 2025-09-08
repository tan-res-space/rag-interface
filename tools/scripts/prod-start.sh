#!/bin/bash

# =====================================================
# RAG Interface - Production Deployment Startup Script
# =====================================================
# This script starts all services for production deployment
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

# Configuration
STARTUP_TIMEOUT=600  # 10 minutes total timeout for production
SERVICE_WAIT_TIMEOUT=120  # 2 minutes per service
HEALTH_CHECK_INTERVAL=10  # 10 seconds between health checks

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

log_service() {
    echo -e "${CYAN}[SERVICE]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Podman availability
check_podman() {
    if ! command_exists podman; then
        log_error "Podman is not installed or not in PATH"
        log_info "Please install Podman and try again"
        exit 1
    fi
    
    if ! podman info >/dev/null 2>&1; then
        log_error "Podman is not running or not accessible"
        log_info "Please start Podman service and try again"
        exit 1
    fi
    
    if ! command_exists podman-compose; then
        log_error "podman-compose is not installed or not in PATH"
        log_info "Please install podman-compose and try again"
        exit 1
    fi
    
    log_success "Podman runtime is available"
}

# Check production prerequisites
check_prerequisites() {
    log_step "Checking production prerequisites..."
    
    cd "$PROJECT_ROOT"
    
    # Check Podman
    check_podman
    
    # Check if production compose file exists
    if [ ! -f "deployment/podman/docker-compose.yml" ]; then
        log_error "Production compose file not found: deployment/podman/docker-compose.yml"
        exit 1
    fi
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        log_warning ".env.production not found. Creating from template..."
        if [ -f "config/environments/production.env" ]; then
            cp config/environments/production.env .env.production
        else
            log_error "No production environment template found. Please create .env.production manually."
            exit 1
        fi
        log_warning "Please edit .env.production with your production configuration"
    fi
    
    # Load environment variables
    set -a
    source .env.production
    set +a
    
    # Check required environment variables
    local required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "JWT_SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required environment variable $var is not set in .env.production"
            exit 1
        fi
    done
    
    log_success "Production prerequisites check completed"
}

# Pull latest images
pull_images() {
    log_step "Pulling latest production images..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Pull images defined in compose file
    podman-compose pull
    
    log_success "Latest images pulled successfully"
}

# Start infrastructure services (PostgreSQL, Redis)
start_infrastructure() {
    log_step "Starting production infrastructure services..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Start infrastructure services first
    podman-compose up -d postgres redis
    
    # Wait for PostgreSQL
    log_service "Waiting for PostgreSQL to be ready..."
    local timeout=$SERVICE_WAIT_TIMEOUT
    while ! nc -z localhost "${POSTGRES_PORT:-5432}" 2>/dev/null; do
        sleep $HEALTH_CHECK_INTERVAL
        timeout=$((timeout - HEALTH_CHECK_INTERVAL))
        if [ $timeout -le 0 ]; then
            log_error "Timeout waiting for PostgreSQL"
            return 1
        fi
        echo -n "."
    done
    echo
    log_success "PostgreSQL is ready"
    
    # Wait for Redis
    log_service "Waiting for Redis to be ready..."
    timeout=$SERVICE_WAIT_TIMEOUT
    while ! nc -z localhost "${REDIS_PORT:-6379}" 2>/dev/null; do
        sleep $HEALTH_CHECK_INTERVAL
        timeout=$((timeout - HEALTH_CHECK_INTERVAL))
        if [ $timeout -le 0 ]; then
            log_error "Timeout waiting for Redis"
            return 1
        fi
        echo -n "."
    done
    echo
    log_success "Redis is ready"
    
    log_success "Infrastructure services started successfully"
}

# Run database migrations
run_migrations() {
    log_step "Running database migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Run migrations for each service
    local services=("error_reporting" "user_management" "rag_integration" "correction_engine" "verification")
    
    for service in "${services[@]}"; do
        log_service "Running migrations for $service..."
        
        # Run migration using the service container
        podman run --rm \
            --network rag-network \
            -e DATABASE_URL="postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-postgres}?options=-csearch_path%3D${service}" \
            -v "$PROJECT_ROOT:/app:Z" \
            -w /app \
            docker.io/library/python:3.11-slim \
            sh -c "
                apt-get update && apt-get install -y gcc &&
                pip install alembic psycopg2-binary &&
                pip install -r requirements.txt &&
                alembic -c src/${service}_service/alembic.ini upgrade head
            " || log_warning "Migration failed for $service (may be expected if no migrations exist)"
    done
    
    log_success "Database migrations completed"
}

# Start backend services
start_backend_services() {
    log_step "Starting production backend services..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Start backend services. Include API Gateway if present in compose file
    local compose_services
    compose_services=$(podman-compose config --services)

    if echo "$compose_services" | grep -q "^api-gateway$"; then
        podman-compose up -d api-gateway error-reporting-service user-management-service rag-integration-service correction-engine-service verification-service
    else
        podman-compose up -d error-reporting-service user-management-service rag-integration-service correction-engine-service verification-service
    fi
    
    # Wait for backend services
    local services=()
    local service_names=()

    if echo "$compose_services" | grep -q "^api-gateway$"; then
        services+=("${GATEWAY_PORT:-8000}")
        service_names+=("API Gateway")
    fi
    services+=("${ERS_PORT:-8010}" "${UMS_PORT:-8011}" "${RIS_PORT:-8012}" "${CES_PORT:-8013}" "${VS_PORT:-8014}")
    service_names+=("Error Reporting Service" "User Management Service" "RAG Integration Service" "Correction Engine Service" "Verification Service")
    
    for i in "${!services[@]}"; do
        local port="${services[$i]}"
        local name="${service_names[$i]}"
        
        log_service "Waiting for $name on port $port..."
        local timeout=$SERVICE_WAIT_TIMEOUT
        while ! curl -s "http://localhost:$port/health" >/dev/null 2>&1; do
            sleep $HEALTH_CHECK_INTERVAL
            timeout=$((timeout - HEALTH_CHECK_INTERVAL))
            if [ $timeout -le 0 ]; then
                log_warning "Timeout waiting for $name on port $port"
                break
            fi
            echo -n "."
        done
        echo
        
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            log_success "$name is ready"
        else
            log_warning "$name may not be fully ready"
        fi
    done
    
    log_success "Backend services started"
}

# Start frontend service
start_frontend() {
    log_step "Starting production frontend service..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Start frontend
    podman-compose up -d frontend
    
    # Wait for frontend
    log_service "Waiting for frontend on port ${FRONTEND_PORT:-80}..."
    local timeout=$SERVICE_WAIT_TIMEOUT
    while ! curl -s "http://localhost:${FRONTEND_PORT:-80}" >/dev/null 2>&1; do
        sleep $HEALTH_CHECK_INTERVAL
        timeout=$((timeout - HEALTH_CHECK_INTERVAL))
        if [ $timeout -le 0 ]; then
            log_warning "Timeout waiting for frontend"
            break
        fi
        echo -n "."
    done
    echo
    
    if curl -s "http://localhost:${FRONTEND_PORT:-80}" >/dev/null 2>&1; then
        log_success "Frontend is ready"
    else
        log_warning "Frontend may not be fully ready"
    fi
}

# Start monitoring services
start_monitoring() {
    log_step "Starting monitoring services..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Start monitoring services if they exist in compose file
    if podman-compose config --services | grep -q "prometheus"; then
        podman-compose up -d prometheus grafana
        log_success "Monitoring services started"
    else
        log_info "No monitoring services defined in production compose file"
    fi
}

# Start load balancer
start_load_balancer() {
    log_step "Starting load balancer..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Start nginx load balancer if it exists
    if podman-compose config --services | grep -q "nginx"; then
        podman-compose up -d nginx
        log_success "Load balancer started"
    else
        log_info "No load balancer defined in production compose file"
    fi
}

# Show production status and URLs
show_status() {
    log_step "RAG Interface Production Deployment Status"
    echo ""
    echo "🌐 Frontend Application:"
    echo "   http://localhost:${FRONTEND_PORT:-80}"
    echo ""
    echo "🔧 Backend Services:"
    # Show API Gateway if defined
    if podman-compose -f "$PROJECT_ROOT/deployment/podman/docker-compose.yml" config --services | grep -q "^api-gateway$"; then
      echo "   API Gateway:          http://localhost:${GATEWAY_PORT:-8000}"
    fi
    echo "   Error Reporting:       http://localhost:${ERS_PORT:-8010}"
    echo "   User Management:       http://localhost:${UMS_PORT:-8011}"
    echo "   RAG Integration:       http://localhost:${RIS_PORT:-8012}"
    echo "   Correction Engine:     http://localhost:${CES_PORT:-8013}"
    echo "   Verification:          http://localhost:${VS_PORT:-8014}"
    echo ""
    echo "📚 API Documentation:"
    echo "   Error Reporting Docs:  http://localhost:${ERS_PORT:-8010}/docs"
    echo "   User Management Docs:  http://localhost:${UMS_PORT:-8011}/docs"
    echo "   RAG Integration Docs:  http://localhost:${RIS_PORT:-8012}/docs"
    echo "   Correction Engine Docs: http://localhost:${CES_PORT:-8013}/docs"
    echo "   Verification Docs:     http://localhost:${VS_PORT:-8014}/docs"
    echo ""
    echo "📊 Monitoring (if enabled):"
    echo "   Prometheus:            http://localhost:${PROMETHEUS_PORT:-9090}"
    echo "   Grafana:               http://localhost:${GRAFANA_PORT:-3000}"
    echo ""
    echo "📝 Management Commands:"
    echo "   View logs:             ./tools/scripts/prod-logs.sh"
    echo "   Stop services:         ./tools/scripts/prod-stop.sh"
}

# Main function
main() {
    local command="${1:-all}"
    local start_time=$(date +%s)
    
    log_info "Starting RAG Interface Production Deployment..."
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    case "$command" in
        "all")
            check_prerequisites
            pull_images
            start_infrastructure
            run_migrations
            start_backend_services
            start_frontend
            start_monitoring
            start_load_balancer
            ;;
        "infrastructure")
            check_prerequisites
            start_infrastructure
            ;;
        "backend")
            start_backend_services
            ;;
        "frontend")
            start_frontend
            ;;
        "monitoring")
            start_monitoring
            ;;
        "migrations")
            run_migrations
            ;;
        *)
            echo "Usage: $0 [all|infrastructure|backend|frontend|monitoring|migrations]"
            echo ""
            echo "Commands:"
            echo "  all            - Start all services (default)"
            echo "  infrastructure - Start only infrastructure (PostgreSQL, Redis)"
            echo "  backend        - Start only backend services"
            echo "  frontend       - Start only frontend"
            echo "  monitoring     - Start only monitoring services"
            echo "  migrations     - Run database migrations only"
            exit 1
            ;;
    esac
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    log_success "RAG Interface Production Deployment started successfully in ${duration}s!"
    echo ""
    show_status
}

# Run main function
main "$@"
