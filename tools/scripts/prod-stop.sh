#!/bin/bash

# =====================================================
# RAG Interface - Production Deployment Shutdown Script
# =====================================================
# This script stops all services for production deployment
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
GRACEFUL_TIMEOUT=30  # 30 seconds for graceful shutdown

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
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Stop the services gracefully
    log_service "Stopping ${services[*]}..."
    podman-compose stop -t $GRACEFUL_TIMEOUT "${services[@]}"
    
    log_success "$group stopped"
}

# Stop all production services gracefully
stop_all_services() {
    log_step "Stopping all RAG Interface production services..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Stop all services gracefully
    podman-compose down -t $GRACEFUL_TIMEOUT
    
    log_success "All production services stopped successfully"
}

# Stop load balancer first (to stop accepting new requests)
stop_load_balancer() {
    log_step "Stopping load balancer..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    if podman-compose config --services | grep -q "nginx"; then
        stop_service_group "Load Balancer" "nginx"
    else
        log_info "No load balancer to stop"
    fi
}

# Stop frontend services
stop_frontend() {
    stop_service_group "Frontend Services" "frontend"
}

# Stop backend services
stop_backend() {
    cd "$PROJECT_ROOT/deployment/podman"
    local services=("error-reporting-service" "user-management-service" "rag-integration-service" "correction-engine-service" "verification-service")
    if podman-compose config --services | grep -q "^api-gateway$"; then
        services=("api-gateway" "${services[@]}")
    fi
    stop_service_group "Backend Services" "${services[@]}"
}

# Stop monitoring services
stop_monitoring() {
    log_step "Stopping monitoring services..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    local monitoring_services=()
    
    # Check which monitoring services exist
    if podman-compose config --services | grep -q "prometheus"; then
        monitoring_services+=("prometheus")
    fi
    
    if podman-compose config --services | grep -q "grafana"; then
        monitoring_services+=("grafana")
    fi
    
    if [ ${#monitoring_services[@]} -gt 0 ]; then
        stop_service_group "Monitoring Services" "${monitoring_services[@]}"
    else
        log_info "No monitoring services to stop"
    fi
}

# Stop infrastructure services (PostgreSQL, Redis)
stop_infrastructure() {
    stop_service_group "Infrastructure Services" "postgres" "redis"
}

# Graceful shutdown sequence
graceful_shutdown() {
    log_step "Performing graceful shutdown sequence..."
    
    # Stop in reverse order of startup
    stop_load_balancer
    sleep 5  # Allow connections to drain
    
    stop_frontend
    sleep 5
    
    stop_backend
    sleep 5
    
    stop_monitoring
    sleep 5
    
    stop_infrastructure
    
    log_success "Graceful shutdown completed"
}

# Clean up production containers, networks, and volumes
cleanup_system() {
    log_step "Cleaning up production system resources..."
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    # Confirm cleanup
    log_warning "This will remove all containers, networks, and volumes for the RAG Interface production deployment"
    log_warning "This action cannot be undone and will delete all production data!"
    echo ""
    read -p "Are you sure you want to proceed? (type 'YES' to confirm): " -r
    echo
    
    if [[ $REPLY == "YES" ]]; then
        log_info "Proceeding with production cleanup..."
        
        # Stop and remove everything
        podman-compose down -v --remove-orphans
        
        # Clean up Podman system
        log_info "Cleaning up Podman system..."
        podman system prune -f
        
        # Remove specific production volumes if they exist
        podman volume rm rag_postgres_data rag_redis_data rag_logs_data 2>/dev/null || true
        
        log_success "Production system cleanup completed"
        log_info "All production containers, networks, and volumes have been removed"
        log_info "To restart the production system, run: ./tools/scripts/prod-start.sh"
        
    else
        log_info "Production cleanup cancelled"
    fi
}

# Force stop all containers (emergency stop)
force_stop() {
    log_step "Force stopping all RAG Interface production containers..."
    
    # Get all RAG Interface production containers
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

# Create backup before shutdown
create_backup() {
    log_step "Creating production backup before shutdown..."
    
    local backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database
    log_service "Backing up PostgreSQL database..."
    podman exec rag-postgres pg_dumpall -U postgres > "$backup_dir/database_backup.sql" 2>/dev/null || log_warning "Database backup failed"
    
    # Backup Redis data
    log_service "Backing up Redis data..."
    podman exec rag-redis redis-cli --rdb - > "$backup_dir/redis_backup.rdb" 2>/dev/null || log_warning "Redis backup failed"
    
    # Backup configuration
    log_service "Backing up configuration..."
    cp .env.production "$backup_dir/" 2>/dev/null || log_warning "Configuration backup failed"
    
    if [ -f "$backup_dir/database_backup.sql" ] || [ -f "$backup_dir/redis_backup.rdb" ]; then
        log_success "Backup created at: $backup_dir"
    else
        log_warning "Backup creation failed or incomplete"
    fi
}

# Show current service status
show_status() {
    log_step "Current Production Service Status"
    
    cd "$PROJECT_ROOT/deployment/podman"
    
    echo ""
    podman-compose ps
}

# Maintenance mode
enable_maintenance_mode() {
    log_step "Enabling maintenance mode..."
    
    # This would typically involve:
    # 1. Updating load balancer config to show maintenance page
    # 2. Draining existing connections
    # 3. Stopping services gracefully
    
    log_info "Maintenance mode would be implemented here"
    log_info "This typically involves updating load balancer configuration"
    
    # For now, just perform graceful shutdown
    graceful_shutdown
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  stop           - Stop all services gracefully (default)"
    echo "  graceful       - Graceful shutdown sequence"
    echo "  frontend       - Stop only frontend services"
    echo "  backend        - Stop only backend services"
    echo "  infrastructure - Stop only infrastructure services"
    echo "  monitoring     - Stop only monitoring services"
    echo "  force          - Force stop all containers immediately"
    echo "  clean          - Stop services and remove all data (destructive)"
    echo "  backup         - Create backup before shutdown"
    echo "  maintenance    - Enable maintenance mode and shutdown"
    echo "  status         - Show current service status"
    echo ""
    echo "Examples:"
    echo "  $0                    # Stop all services gracefully"
    echo "  $0 graceful           # Graceful shutdown sequence"
    echo "  $0 backup             # Create backup before shutdown"
    echo "  $0 clean              # Complete cleanup (removes data)"
    echo "  $0 force              # Emergency stop"
}

# Main function
main() {
    local command="${1:-stop}"
    
    log_info "RAG Interface Production Service Management"
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    check_podman
    
    case "$command" in
        "stop")
            stop_all_services
            ;;
        "graceful")
            graceful_shutdown
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
        "monitoring")
            stop_monitoring
            ;;
        "force")
            force_stop
            ;;
        "clean")
            cleanup_system
            ;;
        "backup")
            create_backup
            ;;
        "maintenance")
            enable_maintenance_mode
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
    log_info "Production operation completed"
}

# Run main function
main "$@"
