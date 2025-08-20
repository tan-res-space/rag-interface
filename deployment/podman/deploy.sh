#!/bin/bash

# =====================================================
# RAG Interface System - Deployment Script
# =====================================================
# Automated deployment script for Podman/Docker Compose
# Author: RAG Interface Deployment Team
# Version: 1.0
# Date: 2025-01-20
# =====================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

# Functions
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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if podman or docker is available
    if command -v podman &> /dev/null; then
        CONTAINER_ENGINE="podman"
        COMPOSE_CMD="podman-compose"
    elif command -v docker &> /dev/null; then
        CONTAINER_ENGINE="docker"
        COMPOSE_CMD="docker-compose"
    else
        log_error "Neither Podman nor Docker is installed. Please install one of them."
        exit 1
    fi
    
    log_info "Using container engine: $CONTAINER_ENGINE"
    
    # Check if compose is available
    if ! command -v $COMPOSE_CMD &> /dev/null; then
        log_error "$COMPOSE_CMD is not installed. Please install it."
        exit 1
    fi
    
    # Check if git is available (for VCS_REF)
    if ! command -v git &> /dev/null; then
        log_warning "Git is not installed. VCS_REF will be set to 'unknown'."
        VCS_REF="unknown"
    else
        VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    fi
    
    log_success "Prerequisites check completed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning ".env file not found. Creating from template..."
        cp "$SCRIPT_DIR/.env.template" "$ENV_FILE"
        log_warning "Please edit $ENV_FILE with your configuration before running again."
        exit 1
    fi
    
    # Export environment variables
    export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    export VCS_REF="$VCS_REF"
    
    log_success "Environment setup completed"
}

validate_configuration() {
    log_info "Validating configuration..."
    
    # Source the .env file
    source "$ENV_FILE"
    
    # Check critical variables
    local critical_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET_KEY"
        "ERS_DB_PASSWORD"
        "UMS_DB_PASSWORD"
    )
    
    for var in "${critical_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
        
        # Check if using default passwords
        if [[ "${!var}" == *"CHANGE_ME"* ]]; then
            log_error "Please change the default password for $var"
            exit 1
        fi
    done
    
    log_success "Configuration validation completed"
}

build_images() {
    log_info "Building container images..."
    
    cd "$PROJECT_ROOT"
    
    # Build images using compose
    $COMPOSE_CMD -f "$COMPOSE_FILE" build --no-cache
    
    log_success "Container images built successfully"
}

deploy_database() {
    log_info "Deploying database..."
    
    # Start only PostgreSQL and Redis first
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d postgres redis
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 30
    
    # Run database initialization scripts
    log_info "Initializing database schemas..."
    
    # The initialization scripts are mounted in the postgres container
    # and will be executed automatically on first startup
    
    log_success "Database deployment completed"
}

deploy_services() {
    log_info "Deploying backend services..."
    
    # Start backend services
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d \
        error-reporting-service \
        user-management-service \
        rag-integration-service \
        correction-engine-service \
        verification-service
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 60
    
    log_success "Backend services deployment completed"
}

deploy_frontend() {
    log_info "Deploying frontend..."
    
    # Start frontend
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d frontend
    
    log_success "Frontend deployment completed"
}

check_health() {
    log_info "Checking service health..."
    
    # Wait a bit for services to fully start
    sleep 30
    
    # Check service health
    local services=(
        "postgres:5432"
        "redis:6379"
        "error-reporting-service:8000"
        "user-management-service:8001"
        "rag-integration-service:8002"
        "correction-engine-service:8003"
        "verification-service:8004"
        "frontend:3000"
    )
    
    for service in "${services[@]}"; do
        local name="${service%:*}"
        local port="${service#*:}"
        
        if $COMPOSE_CMD -f "$COMPOSE_FILE" exec -T "$name" curl -f "http://localhost:$port/health" &>/dev/null; then
            log_success "$name is healthy"
        else
            log_warning "$name health check failed"
        fi
    done
}

show_status() {
    log_info "Deployment Status:"
    echo
    $COMPOSE_CMD -f "$COMPOSE_FILE" ps
    echo
    log_info "Access URLs:"
    echo "  Frontend:              http://localhost:${FRONTEND_PORT:-3000}"
    echo "  Error Reporting API:   http://localhost:${ERS_PORT:-8000}"
    echo "  User Management API:   http://localhost:${UMS_PORT:-8001}"
    echo "  RAG Integration API:   http://localhost:${RIS_PORT:-8002}"
    echo "  Correction Engine API: http://localhost:${CES_PORT:-8003}"
    echo "  Verification API:      http://localhost:${VS_PORT:-8004}"
    echo
    log_info "Default login: admin / AdminPassword123!"
    log_warning "Please change default passwords!"
}

# Main deployment function
main() {
    log_info "Starting RAG Interface System deployment..."
    
    check_prerequisites
    setup_environment
    validate_configuration
    build_images
    deploy_database
    deploy_services
    deploy_frontend
    check_health
    show_status
    
    log_success "RAG Interface System deployed successfully!"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
