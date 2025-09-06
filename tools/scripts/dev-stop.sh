#!/bin/bash

# =====================================================
# RAG Interface - Development Environment Stop Script
# =====================================================
# This script stops the development environment services
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

# Stop services
stop_services() {
    log_info "Stopping development services..."
    
    cd "$PROJECT_ROOT"
    
    # Determine container command
    CONTAINER_CMD=$(get_container_cmd)
    
    # Stop services with Podman/Docker Compose
    log_info "Stopping services with $CONTAINER_CMD compose..."

    if [ "$CONTAINER_CMD" = "podman" ]; then
        podman-compose -f podman-compose.dev.yml down
    else
        docker compose -f docker-compose.dev.yml down
    fi
    
    log_success "Services stopped successfully"
}

# Clean up (optional)
cleanup() {
    log_info "Cleaning up development environment..."
    
    cd "$PROJECT_ROOT"
    
    # Determine container command
    CONTAINER_CMD=$(get_container_cmd)
    
    # Remove containers, networks, and volumes
    log_warning "This will remove all containers, networks, and volumes"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$CONTAINER_CMD" = "podman" ]; then
            podman-compose -f podman-compose.dev.yml down -v --remove-orphans
            podman system prune -f
        else
            docker compose -f docker-compose.dev.yml down -v --remove-orphans
            docker system prune -f
        fi
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Main function
main() {
    case "${1:-stop}" in
        "stop")
            stop_services
            ;;
        "clean")
            cleanup
            ;;
        *)
            echo "Usage: $0 [stop|clean]"
            echo "  stop  - Stop all services"
            echo "  clean - Stop services and remove volumes/containers"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
