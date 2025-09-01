#!/bin/bash

# =====================================================
# RAG Interface - Development Environment Logs Script
# =====================================================
# This script shows logs from development services
# =====================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Determine container command (prefer Podman over Docker)
get_container_cmd() {
    if command_exists podman && podman info >/dev/null 2>&1; then
        echo "podman"
    elif command_exists docker && docker info >/dev/null 2>&1; then
        echo "docker"
    else
        log_error "Neither Podman nor Docker is available or running"
        exit 1
    fi
}

# Show logs for specific service
show_service_logs() {
    local service="$1"
    local follow="${2:-false}"
    
    cd "$PROJECT_ROOT"
    
    # Determine container command
    CONTAINER_CMD=$(get_container_cmd)
    
    log_info "Showing logs for service: $service"
    
    if [ "$follow" = "true" ]; then
        if [ "$CONTAINER_CMD" = "podman" ]; then
            podman-compose -f podman-compose.dev.yml logs -f "$service"
        else
            docker compose -f docker-compose.dev.yml logs -f "$service"
        fi
    else
        if [ "$CONTAINER_CMD" = "podman" ]; then
            podman-compose -f podman-compose.dev.yml logs --tail=100 "$service"
        else
            docker compose -f docker-compose.dev.yml logs --tail=100 "$service"
        fi
    fi
}

# Show logs for all services
show_all_logs() {
    local follow="${1:-false}"
    
    cd "$PROJECT_ROOT"
    
    # Determine container command
    CONTAINER_CMD=$(get_container_cmd)
    
    log_info "Showing logs for all services"
    
    if [ "$follow" = "true" ]; then
        if [ "$CONTAINER_CMD" = "podman" ]; then
            podman-compose -f podman-compose.dev.yml logs -f
        else
            docker compose -f docker-compose.dev.yml logs -f
        fi
    else
        if [ "$CONTAINER_CMD" = "podman" ]; then
            podman-compose -f podman-compose.dev.yml logs --tail=50
        else
            docker compose -f docker-compose.dev.yml logs --tail=50
        fi
    fi
}

# List available services
list_services() {
    log_info "Available services:"
    echo "  - postgres"
    echo "  - redis"
    echo "  - error-reporting-service"
    echo "  - user-management-service"
    echo "  - rag-integration-service"
    echo "  - correction-engine-service"
    echo "  - verification-service"
    echo "  - frontend"
    echo "  - mailhog"
    echo "  - adminer"
    echo "  - redis-commander"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [SERVICE]"
    echo ""
    echo "Options:"
    echo "  -f, --follow    Follow log output"
    echo "  -l, --list      List available services"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                              # Show recent logs for all services"
    echo "  $0 -f                           # Follow logs for all services"
    echo "  $0 frontend                     # Show recent logs for frontend"
    echo "  $0 -f error-reporting-service   # Follow logs for error-reporting-service"
    echo "  $0 --list                       # List available services"
}

# Main function
main() {
    local follow=false
    local service=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--follow)
                follow=true
                shift
                ;;
            -l|--list)
                list_services
                exit 0
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                service="$1"
                shift
                ;;
        esac
    done
    
    # Show logs
    if [ -n "$service" ]; then
        show_service_logs "$service" "$follow"
    else
        show_all_logs "$follow"
    fi
}

# Run main function
main "$@"
