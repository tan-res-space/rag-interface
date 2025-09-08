#!/bin/bash

# =====================================================
# RAG Interface - Local Development Logs Script
# =====================================================
# This script provides log viewing for local development
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

# Check Podman availability
check_podman() {
    if ! command_exists podman; then
        log_error "Podman is not installed or not in PATH"
        exit 1
    fi
    
    if ! command_exists podman-compose; then
        log_error "podman-compose is not installed or not in PATH"
        exit 1
    fi
}

# Show available services
show_services() {
    log_step "Available Local Development Services"
    
    echo ""
    echo "Infrastructure Services:"
    echo "  postgres              - PostgreSQL database"
    echo "  redis                 - Redis cache"
    echo ""
    echo "Backend Services:"
    echo "  api-gateway              - API Gateway"
    echo "  error-reporting-service    - Error Reporting service"
    echo "  user-management-service    - User Management service"
    echo "  rag-integration-service    - RAG Integration service"
    echo "  correction-engine-service  - Correction Engine service"
    echo "  verification-service       - Verification service"
    echo ""
    echo "Frontend Services:"
    echo "  frontend              - React frontend application"
    echo ""
    echo "Development Tools:"
    echo "  mailhog               - Email testing service"
    echo "  adminer               - Database administration"
    echo "  redis-commander       - Redis management interface"
}

# View logs for specific service
view_service_logs() {
    local service="$1"
    local follow="${2:-false}"
    local lines="${3:-100}"
    
    cd "$PROJECT_ROOT"
    
    log_step "Viewing logs for: $service"
    
    # Check if service exists in compose file
    if ! podman-compose -f podman-compose.dev.yml config --services | grep -q "^$service$"; then
        log_error "Service '$service' not found in podman-compose.dev.yml"
        echo ""
        show_services
        exit 1
    fi
    
    # Build podman-compose logs command
    local cmd="podman-compose -f podman-compose.dev.yml logs"
    
    if [ "$follow" = "true" ]; then
        cmd="$cmd -f"
    fi
    
    cmd="$cmd --tail=$lines $service"
    
    log_info "Executing: $cmd"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# View logs for all services
view_all_logs() {
    local follow="${1:-false}"
    local lines="${2:-100}"
    
    cd "$PROJECT_ROOT"
    
    log_step "Viewing logs for all local development services"
    
    # Build podman-compose logs command
    local cmd="podman-compose -f podman-compose.dev.yml logs"
    
    if [ "$follow" = "true" ]; then
        cmd="$cmd -f"
    fi
    
    cmd="$cmd --tail=$lines"
    
    log_info "Executing: $cmd"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# View logs for service group
view_group_logs() {
    local group="$1"
    local follow="${2:-false}"
    local lines="${3:-100}"
    
    cd "$PROJECT_ROOT"
    
    local services=()
    
    case "$group" in
        "infrastructure")
            services=("postgres" "redis")
            ;;
        "backend")
            services=("api-gateway" "error-reporting-service" "user-management-service" "rag-integration-service" "correction-engine-service" "verification-service")
            ;;
        "frontend")
            services=("frontend")
            ;;
        "tools")
            services=("mailhog" "adminer" "redis-commander")
            ;;
        *)
            log_error "Unknown service group: $group"
            echo ""
            echo "Available groups: infrastructure, backend, frontend, tools"
            exit 1
            ;;
    esac
    
    log_step "Viewing logs for $group services: ${services[*]}"
    
    # Build podman-compose logs command
    local cmd="podman-compose -f podman-compose.dev.yml logs"
    
    if [ "$follow" = "true" ]; then
        cmd="$cmd -f"
    fi
    
    cmd="$cmd --tail=$lines ${services[*]}"
    
    log_info "Executing: $cmd"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# Show service status
show_status() {
    log_step "Local Development Service Status"
    
    cd "$PROJECT_ROOT"
    
    echo ""
    podman-compose -f podman-compose.dev.yml ps
}

# Monitor logs in real-time with filtering
monitor_logs() {
    local filter="${1:-}"
    local services="${2:-}"
    
    cd "$PROJECT_ROOT"
    
    log_step "Monitoring logs in real-time"
    
    if [ -n "$filter" ]; then
        log_info "Filter: $filter"
    fi
    
    if [ -n "$services" ]; then
        log_info "Services: $services"
    fi
    
    # Build command
    local cmd="podman-compose -f podman-compose.dev.yml logs -f --tail=50"
    
    if [ -n "$services" ]; then
        cmd="$cmd $services"
    fi
    
    if [ -n "$filter" ]; then
        cmd="$cmd | grep --line-buffered '$filter'"
    fi
    
    log_info "Executing: $cmd"
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [SERVICE|GROUP|COMMAND] [OPTIONS]"
    echo ""
    echo "View logs for specific service:"
    echo "  $0 <service_name>              # Show last 100 lines"
    echo "  $0 <service_name> -f           # Follow logs in real-time"
    echo "  $0 <service_name> -n 200       # Show last 200 lines"
    echo "  $0 <service_name> -f -n 50     # Follow with last 50 lines"
    echo ""
    echo "View logs for service groups:"
    echo "  $0 infrastructure              # Infrastructure services"
    echo "  $0 backend                     # Backend services"
    echo "  $0 frontend                    # Frontend service"
    echo "  $0 tools                       # Development tools"
    echo ""
    echo "Special commands:"
    echo "  $0 all                         # All services"
    echo "  $0 all -f                      # Follow all services"
    echo "  $0 monitor [filter] [services] # Monitor with optional filter"
    echo "  $0 status                      # Show service status"
    echo "  $0 services                    # List available services"
    echo ""
    echo "Options:"
    echo "  -f, --follow                   # Follow log output"
    echo "  -n, --lines NUMBER             # Number of lines to show (default: 100)"
    echo ""
    echo "Examples:"
    echo "  $0 postgres                    # Show PostgreSQL logs"
    echo "  $0 error-reporting-service -f  # Follow Error Reporting service logs"
    echo "  $0 backend -n 200              # Show last 200 lines of backend services"
    echo "  $0 monitor ERROR               # Monitor all logs for ERROR messages"
    echo "  $0 monitor WARNING frontend    # Monitor frontend logs for WARNING messages"
}

# Parse command line arguments
parse_args() {
    local service_or_command="$1"
    shift || true
    
    local follow=false
    local lines=100
    local filter=""
    local services=""
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--follow)
                follow=true
                shift
                ;;
            -n|--lines)
                lines="$2"
                shift 2
                ;;
            *)
                # For monitor command, treat as filter or services
                if [ "$service_or_command" = "monitor" ]; then
                    if [ -z "$filter" ]; then
                        filter="$1"
                    else
                        services="$1"
                    fi
                else
                    log_error "Unknown option: $1"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    echo "$service_or_command $follow $lines $filter $services"
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    local args
    args=$(parse_args "$@")
    read -r service_or_command follow lines filter services <<< "$args"
    
    log_info "RAG Interface Local Development Logs"
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    check_podman
    
    case "$service_or_command" in
        "all")
            view_all_logs "$follow" "$lines"
            ;;
        "infrastructure"|"backend"|"frontend"|"tools")
            view_group_logs "$service_or_command" "$follow" "$lines"
            ;;
        "monitor")
            monitor_logs "$filter" "$services"
            ;;
        "status")
            show_status
            ;;
        "services")
            show_services
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            # Assume it's a service name
            view_service_logs "$service_or_command" "$follow" "$lines"
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}[INFO]${NC} Log viewing stopped by user"; exit 0' INT TERM

# Run main function
main "$@"
