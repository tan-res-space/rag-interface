#!/bin/bash

# =====================================================
# RAG Interface - Local Development Shutdown Script
# =====================================================
# This script stops all services for local development
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
        exit 1
    fi
    
    if ! command_exists podman-compose; then
        log_error "podman-compose is not installed or not in PATH"
        exit 1
    fi
}

# Stop specific service group
stop_service_group() {
    local group="$1"
    shift
    local services=("$@")
    
    log_step "Stopping $group..."
    
    cd "$PROJECT_ROOT"
    
    # Stop the services
    log_service "Stopping ${services[*]}..."
    podman-compose -f podman-compose.dev.yml stop "${services[@]}"
    
    log_success "$group stopped"
}

# Stop all services gracefully
stop_all_services() {
    log_step "Stopping all RAG Interface local development services..."
    
    cd "$PROJECT_ROOT"
    
    # Stop all services
    podman-compose -f podman-compose.dev.yml down
    
    log_success "All services stopped successfully"
}

# Stop frontend only
stop_frontend() {
    stop_service_group "Frontend" "frontend"
}

# Stop backend services
stop_backend() {
    stop_service_group "Backend Services" "api-gateway" "error-reporting-service" "user-management-service" "rag-integration-service" "correction-engine-service" "verification-service"
}

# Stop infrastructure services
stop_infrastructure() {
    stop_service_group "Infrastructure Services" "postgres" "redis"
}

# Stop development tools
stop_dev_tools() {
    stop_service_group "Development Tools" "mailhog" "adminer" "redis-commander"
}

# Clean up containers, networks, and volumes
cleanup_system() {
    log_step "Cleaning up local development system resources..."
    
    cd "$PROJECT_ROOT"
    
    # Confirm cleanup
    log_warning "This will remove all containers, networks, and volumes for the RAG Interface local development"
    log_warning "This action cannot be undone and will delete all development data!"
    echo ""
    read -p "Are you sure you want to proceed? (type 'yes' to confirm): " -r
    echo
    
    if [[ $REPLY == "yes" ]]; then
        log_info "Proceeding with cleanup..."
        
        # Stop and remove everything
        podman-compose -f podman-compose.dev.yml down -v --remove-orphans
        
        # Clean up Podman system
        log_info "Cleaning up Podman system..."
        podman system prune -f
        
        # Remove specific volumes if they exist
        podman volume rm rag_postgres_dev_data rag_redis_dev_data rag_ers_venv rag_ums_venv rag_ris_venv rag_ces_venv rag_vs_venv rag_frontend_node_modules 2>/dev/null || true
        
        log_success "System cleanup completed"
        log_info "All containers, networks, and volumes have been removed"
        log_info "To restart the system, run: ./tools/scripts/local-start.sh"
        
    else
        log_info "Cleanup cancelled"
    fi
}

# Force stop all containers (emergency stop)
force_stop() {
    log_step "Force stopping all RAG Interface local development containers..."
    
    # Get all RAG Interface containers
    containers=$(podman ps -a --filter "name=rag-" --format "{{.Names}}" 2>/dev/null || true)
    
    if [ -n "$containers" ]; then
        log_info "Found containers: $containers"
        
        # Force kill containers
        echo "$containers" | xargs -r podman kill 2>/dev/null || true
        echo "$containers" | xargs -r podman rm -f 2>/dev/null || true
        
        log_success "Force stop completed"
    else
        log_info "No RAG Interface containers found"
    fi
}

# Show current service status
show_status() {
    log_step "Current Local Development Service Status"
    
    cd "$PROJECT_ROOT"
    
    echo ""
    podman-compose -f podman-compose.dev.yml ps
}

# Kill specific processes (for non-containerized services)
kill_local_processes() {
    log_step "Stopping local development processes..."
    
    # Kill Python services
    pkill -f "uvicorn.*error_reporting_service" 2>/dev/null || true
    pkill -f "uvicorn.*user_management_service" 2>/dev/null || true
    pkill -f "uvicorn.*rag_integration_service" 2>/dev/null || true
    pkill -f "uvicorn.*correction_engine_service" 2>/dev/null || true
    pkill -f "uvicorn.*verification_service" 2>/dev/null || true
    
    # Kill Vite frontend
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    
    log_success "Local processes stopped"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  stop           - Stop all services gracefully (default)"
    echo "  frontend       - Stop only frontend service"
    echo "  backend        - Stop only backend services"
    echo "  infrastructure - Stop only infrastructure services"
    echo "  tools          - Stop only development tools"
    echo "  force          - Force stop all containers immediately"
    echo "  clean          - Stop services and remove all data (destructive)"
    echo "  local          - Stop local development processes"
    echo "  status         - Show current service status"
    echo ""
    echo "Examples:"
    echo "  $0                    # Stop all services"
    echo "  $0 frontend           # Stop only frontend"
    echo "  $0 clean              # Complete cleanup (removes data)"
    echo "  $0 force              # Emergency stop"
}

# Main function
main() {
    local command="${1:-stop}"
    
    log_info "RAG Interface Local Development Service Management"
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    check_podman
    
    case "$command" in
        "stop")
            stop_all_services
            ;;
        "frontend")
            stop_frontend
            ;;
        "backend")
            stop_backend
            ;;
        "infrastructure")
            stop_infrastructure
            ;;
        "tools")
            stop_dev_tools
            ;;
        "force")
            force_stop
            ;;
        "clean")
            cleanup_system
            ;;
        "local")
            kill_local_processes
            ;;
        "status")
            show_status
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
    
    echo ""
    log_info "Local development operation completed"
}

# Run main function
main "$@"
