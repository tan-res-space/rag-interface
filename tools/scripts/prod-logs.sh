#!/bin/bash

# =====================================================
# RAG Interface - Production Deployment Logs Script
# =====================================================
# This script provides log viewing for production deployment
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

# Show available production services
show_services() {
    log_step "Available Production Services"
    
    echo ""
    echo "Infrastructure Services:"
    echo "  postgres              - PostgreSQL database"
    echo "  redis                 - Redis cache"
    echo ""
    echo "Backend Services:"
    echo "  api-gateway                - API Gateway (if configured)"
    echo "  error-reporting-service    - Error Reporting service"
    echo "  user-management-service    - User Management service"
    echo "  rag-integration-service    - RAG Integration service"
    echo "  correction-engine-service  - Correction Engine service"
    echo "  verification-service       - Verification service"
    echo ""
    echo "Frontend Services:"
    echo "  frontend              - React frontend application"
    echo ""
    echo "Infrastructure Services:"
    echo "  nginx                 - Load balancer (if configured)"
    echo "  prometheus            - Monitoring (if configured)"
    echo "  grafana               - Dashboards (if configured)"
}

# View logs for specific service
view_service_logs() {
    local service="$1"
    local follow="${2:-false}"
    local lines="${3:-200}"
    local level="${4:-}"
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    log_step "Viewing production logs for: $service"
    
    # Check if service exists in compose file
    if ! podman-compose config --services | grep -q "^$service$"; then
        log_error "Service '$service' not found in production compose file"
        echo ""
        show_services
        exit 1
    fi
    
    # Build podman-compose logs command
    local cmd="podman-compose logs"
    
    if [ "$follow" = "true" ]; then
        cmd="$cmd -f"
    fi
    
    cmd="$cmd --tail=$lines $service"
    
    # Add log level filtering if specified
    if [ -n "$level" ]; then
        cmd="$cmd | grep -i '$level'"
    fi
    
    log_info "Executing: $cmd"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# View logs for all services
view_all_logs() {
    local follow="${1:-false}"
    local lines="${2:-200}"
    local level="${3:-}"
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    log_step "Viewing logs for all production services"
    
    # Build podman-compose logs command
    local cmd="podman-compose logs"
    
    if [ "$follow" = "true" ]; then
        cmd="$cmd -f"
    fi
    
    cmd="$cmd --tail=$lines"
    
    # Add log level filtering if specified
    if [ -n "$level" ]; then
        cmd="$cmd | grep -i '$level'"
    fi
    
    log_info "Executing: $cmd"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# View logs for service group
view_group_logs() {
    local group="$1"
    local follow="${2:-false}"
    local lines="${3:-200}"
    local level="${4:-}"
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    local services=()
    
    case "$group" in
        "infrastructure")
            services=("postgres" "redis")
            ;;
        "backend")
            # Include API Gateway if present
            if podman-compose config --services | grep -q "^api-gateway$"; then
                services=("api-gateway" "error-reporting-service" "user-management-service" "rag-integration-service" "correction-engine-service" "verification-service")
            else
                services=("error-reporting-service" "user-management-service" "rag-integration-service" "correction-engine-service" "verification-service")
            fi
            ;;
        "frontend")
            services=("frontend")
            ;;
        "monitoring")
            # Check which monitoring services exist
            if podman-compose config --services | grep -q "prometheus"; then
                services+=("prometheus")
            fi
            if podman-compose config --services | grep -q "grafana"; then
                services+=("grafana")
            fi
            if [ ${#services[@]} -eq 0 ]; then
                log_warning "No monitoring services found in production deployment"
                return
            fi
            ;;
        "loadbalancer")
            if podman-compose config --services | grep -q "nginx"; then
                services=("nginx")
            else
                log_warning "No load balancer found in production deployment"
                return
            fi
            ;;
        *)
            log_error "Unknown service group: $group"
            echo ""
            echo "Available groups: infrastructure, backend, frontend, monitoring, loadbalancer"
            exit 1
            ;;
    esac
    
    log_step "Viewing logs for $group services: ${services[*]}"
    
    # Build podman-compose logs command
    local cmd="podman-compose logs"
    
    if [ "$follow" = "true" ]; then
        cmd="$cmd -f"
    fi
    
    cmd="$cmd --tail=$lines ${services[*]}"
    
    # Add log level filtering if specified
    if [ -n "$level" ]; then
        cmd="$cmd | grep -i '$level'"
    fi
    
    log_info "Executing: $cmd"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# Show service status
show_status() {
    log_step "Production Service Status"
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    echo ""
    podman-compose ps
}

# Monitor logs in real-time with advanced filtering
monitor_logs() {
    local filter="${1:-}"
    local services="${2:-}"
    local level="${3:-}"
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    log_step "Monitoring production logs in real-time"
    
    if [ -n "$filter" ]; then
        log_info "Filter: $filter"
    fi
    
    if [ -n "$level" ]; then
        log_info "Log Level: $level"
    fi
    
    if [ -n "$services" ]; then
        log_info "Services: $services"
    fi
    
    # Build command
    local cmd="podman-compose logs -f --tail=100"
    
    if [ -n "$services" ]; then
        cmd="$cmd $services"
    fi
    
    # Add filtering
    local filters=()
    if [ -n "$level" ]; then
        filters+=("grep -i '$level'")
    fi
    if [ -n "$filter" ]; then
        filters+=("grep --line-buffered '$filter'")
    fi
    
    if [ ${#filters[@]} -gt 0 ]; then
        for filter_cmd in "${filters[@]}"; do
            cmd="$cmd | $filter_cmd"
        done
    fi
    
    log_info "Executing: $cmd"
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    # Execute the command
    eval "$cmd"
}

# Export logs to file
export_logs() {
    local service="${1:-all}"
    local lines="${2:-1000}"
    local output_dir="$PROJECT_ROOT/logs/export/$(date +%Y%m%d_%H%M%S)"
    
    mkdir -p "$output_dir"
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    log_step "Exporting production logs to: $output_dir"
    
    if [ "$service" = "all" ]; then
        # Export all services
        local services
        services=$(podman-compose config --services)
        
        for svc in $services; do
            log_info "Exporting logs for $svc..."
            podman-compose logs --tail="$lines" "$svc" > "$output_dir/${svc}.log" 2>&1
        done
        
        # Create combined log
        podman-compose logs --tail="$lines" > "$output_dir/combined.log" 2>&1
    else
        # Export specific service
        log_info "Exporting logs for $service..."
        podman-compose logs --tail="$lines" "$service" > "$output_dir/${service}.log" 2>&1
    fi
    
    # Create metadata file
    cat > "$output_dir/metadata.txt" << EOF
Export Date: $(date)
Project: RAG Interface Production
Service: $service
Lines: $lines
Exported by: $(whoami)
Host: $(hostname)
EOF
    
    log_success "Logs exported to: $output_dir"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [SERVICE|GROUP|COMMAND] [OPTIONS]"
    echo ""
    echo "View logs for specific service:"
    echo "  $0 <service_name>              # Show last 200 lines"
    echo "  $0 <service_name> -f           # Follow logs in real-time"
    echo "  $0 <service_name> -n 500       # Show last 500 lines"
    echo "  $0 <service_name> -l ERROR     # Filter by log level"
    echo "  $0 <service_name> -f -n 100 -l WARNING  # Combined options"
    echo ""
    echo "View logs for service groups:"
    echo "  $0 infrastructure              # Infrastructure services"
    echo "  $0 backend                     # Backend services"
    echo "  $0 frontend                    # Frontend service"
    echo "  $0 monitoring                  # Monitoring services"
    echo "  $0 loadbalancer                # Load balancer"
    echo ""
    echo "Special commands:"
    echo "  $0 all                         # All services"
    echo "  $0 all -f                      # Follow all services"
    echo "  $0 monitor [filter] [services] [level]  # Advanced monitoring"
    echo "  $0 export [service] [lines]    # Export logs to file"
    echo "  $0 status                      # Show service status"
    echo "  $0 services                    # List available services"
    echo ""
    echo "Options:"
    echo "  -f, --follow                   # Follow log output"
    echo "  -n, --lines NUMBER             # Number of lines to show (default: 200)"
    echo "  -l, --level LEVEL              # Filter by log level (ERROR, WARNING, INFO, DEBUG)"
    echo ""
    echo "Examples:"
    echo "  $0 postgres                    # Show PostgreSQL logs"
    echo "  $0 error-reporting-service -f  # Follow Error Reporting service logs"
    echo "  $0 backend -n 500 -l ERROR     # Show last 500 lines of backend errors"
    echo "  $0 monitor 'database connection' backend ERROR  # Monitor backend for database connection errors"
    echo "  $0 export all 2000             # Export last 2000 lines of all services"
}

# Parse command line arguments
parse_args() {
    local service_or_command="$1"
    shift || true
    
    local follow=false
    local lines=200
    local level=""
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
            -l|--level)
                level="$2"
                shift 2
                ;;
            *)
                # For monitor/export commands, treat as additional parameters
                if [ "$service_or_command" = "monitor" ]; then
                    if [ -z "$filter" ]; then
                        filter="$1"
                    elif [ -z "$services" ]; then
                        services="$1"
                    elif [ -z "$level" ]; then
                        level="$1"
                    fi
                elif [ "$service_or_command" = "export" ]; then
                    if [ -z "$services" ]; then
                        services="$1"
                    elif [ -z "$lines" ] || [ "$lines" = "200" ]; then
                        lines="$1"
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
    
    echo "$service_or_command $follow $lines $level $filter $services"
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    local args
    args=$(parse_args "$@")
    read -r service_or_command follow lines level filter services <<< "$args"
    
    log_info "RAG Interface Production Logs"
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    check_podman
    
    case "$service_or_command" in
        "all")
            view_all_logs "$follow" "$lines" "$level"
            ;;
        "infrastructure"|"backend"|"frontend"|"monitoring"|"loadbalancer")
            view_group_logs "$service_or_command" "$follow" "$lines" "$level"
            ;;
        "monitor")
            monitor_logs "$filter" "$services" "$level"
            ;;
        "export")
            export_logs "${services:-all}" "${lines:-1000}"
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
            view_service_logs "$service_or_command" "$follow" "$lines" "$level"
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}[INFO]${NC} Log viewing stopped by user"; exit 0' INT TERM

# Run main function
main "$@"
