# RAG Interface System - Maintenance and Operations Guide

## 📋 Table of Contents

1. [Maintenance Schedule](#maintenance-schedule)
2. [Backup Procedures](#backup-procedures)
3. [Update Processes](#update-processes)
4. [Monitoring Guidelines](#monitoring-guidelines)
5. [Performance Optimization](#performance-optimization)
6. [Security Maintenance](#security-maintenance)
7. [Disaster Recovery](#disaster-recovery)
8. [Capacity Planning](#capacity-planning)

## 📅 Maintenance Schedule

### Daily Tasks (Automated)

#### System Health Monitoring
```bash
#!/bin/bash
# daily_health_check.sh - Run via cron daily

LOG_FILE="/var/log/rag-interface/daily_health_$(date +%Y%m%d).log"
mkdir -p /var/log/rag-interface

{
    echo "=== Daily Health Check - $(date) ==="
    
    # Service status
    echo "Service Status:"
    cd /opt/rag-interface/deployment/podman
    podman-compose ps
    
    # Resource usage
    echo -e "\nResource Usage:"
    echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
    echo "Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
    echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
    
    # Error count
    echo -e "\nError Summary (last 24h):"
    podman-compose logs --since=24h | grep -i error | wc -l
    
    # Database connections
    echo -e "\nDatabase Connections:"
    podman-compose exec postgres psql -U postgres -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';" -t
    
} >> "$LOG_FILE"

# Alert if critical issues found
if podman-compose ps | grep -q "Exit\|Restarting"; then
    echo "ALERT: Service issues detected" | mail -s "RAG Interface Alert" admin@company.com
fi
```

#### Log Rotation
```bash
# Setup logrotate for application logs
cat > /etc/logrotate.d/rag-interface << EOF
/var/log/rag-interface/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
```

### Weekly Tasks

#### Database Maintenance
```bash
#!/bin/bash
# weekly_db_maintenance.sh

cd /opt/rag-interface/deployment/podman

echo "=== Weekly Database Maintenance - $(date) ==="

# Vacuum and analyze all databases
databases=("error_reporting_db" "user_management_db" "verification_db" "correction_engine_db" "rag_integration_db")

for db in "${databases[@]}"; do
    echo "Maintaining database: $db"
    podman-compose exec postgres psql -U postgres -d "$db" -c "VACUUM ANALYZE;"
    
    # Check database size
    size=$(podman-compose exec postgres psql -U postgres -d "$db" -c "SELECT pg_size_pretty(pg_database_size('$db'));" -t)
    echo "Database $db size: $size"
done

# Clean old audit logs (older than 90 days)
podman-compose exec postgres psql -U postgres -d error_reporting_db -c "
DELETE FROM error_audit_logs WHERE performed_at < NOW() - INTERVAL '90 days';
"

podman-compose exec postgres psql -U postgres -d user_management_db -c "
DELETE FROM user_audit_logs WHERE created_at < NOW() - INTERVAL '90 days';
"

# Update database statistics
podman-compose exec postgres psql -U postgres -c "SELECT pg_stat_reset();"

echo "Database maintenance completed"
```

#### Cache Cleanup
```bash
#!/bin/bash
# weekly_cache_cleanup.sh

cd /opt/rag-interface/deployment/podman

echo "=== Weekly Cache Cleanup - $(date) ==="

# Clean expired cache entries
podman-compose exec postgres psql -U postgres -d verification_db -c "SELECT cleanup_expired_cache();"
podman-compose exec postgres psql -U postgres -d rag_integration_db -c "SELECT cleanup_expired_cache();"

# Redis memory optimization
podman-compose exec redis redis-cli MEMORY PURGE

# Check Redis memory usage
memory_used=$(podman-compose exec redis redis-cli info memory | grep used_memory_human | cut -d: -f2)
echo "Redis memory usage: $memory_used"

echo "Cache cleanup completed"
```

### Monthly Tasks

#### System Updates
```bash
#!/bin/bash
# monthly_system_update.sh

echo "=== Monthly System Update - $(date) ==="

# Update system packages
if command -v apt &> /dev/null; then
    sudo apt update && sudo apt upgrade -y
elif command -v dnf &> /dev/null; then
    sudo dnf update -y
fi

# Update container images
cd /opt/rag-interface/deployment/podman
podman-compose pull

# Restart services with new images
podman-compose up -d

# Wait for services to be ready
sleep 60

# Verify all services are healthy
./health_check.sh

echo "System update completed"
```

#### Security Audit
```bash
#!/bin/bash
# monthly_security_audit.sh

echo "=== Monthly Security Audit - $(date) ==="

cd /opt/rag-interface/deployment/podman

# Check for failed login attempts
echo "Failed login attempts (last 30 days):"
podman-compose exec postgres psql -U postgres -d user_management_db -c "
SELECT COUNT(*) as failed_attempts 
FROM user_audit_logs 
WHERE action = 'login_failed' 
AND created_at > NOW() - INTERVAL '30 days';
"

# Check user account status
echo "User account summary:"
podman-compose exec postgres psql -U postgres -d user_management_db -c "
SELECT status, COUNT(*) as count 
FROM users 
GROUP BY status;
"

# Check for inactive users
echo "Inactive users (no login in 30 days):"
podman-compose exec postgres psql -U postgres -d user_management_db -c "
SELECT username, last_login_at 
FROM users 
WHERE last_login_at < NOW() - INTERVAL '30 days' 
OR last_login_at IS NULL;
"

# Check container vulnerabilities (if available)
if command -v podman &> /dev/null; then
    echo "Scanning container images for vulnerabilities..."
    podman-compose images --format "{{.Repository}}:{{.Tag}}" | xargs -I {} podman image scan {} || echo "Vulnerability scanning not available"
fi

echo "Security audit completed"
```

## 💾 Backup Procedures

### Automated Daily Backups

#### Database Backup Script
```bash
#!/bin/bash
# daily_backup.sh

BACKUP_DIR="/opt/backups/rag-interface"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR/$DATE"
cd /opt/rag-interface/deployment/podman

echo "=== Daily Backup - $(date) ==="

# Database backups
databases=("error_reporting_db" "user_management_db" "verification_db" "correction_engine_db" "rag_integration_db")

for db in "${databases[@]}"; do
    echo "Backing up database: $db"
    podman-compose exec postgres pg_dump -U postgres -Fc "$db" > "$BACKUP_DIR/$DATE/${db}.dump"
    
    # Verify backup
    if [ -s "$BACKUP_DIR/$DATE/${db}.dump" ]; then
        echo "✓ $db backup successful"
    else
        echo "✗ $db backup failed"
        exit 1
    fi
done

# Configuration backup
echo "Backing up configuration..."
cp .env "$BACKUP_DIR/$DATE/env_backup"
cp docker-compose.yml "$BACKUP_DIR/$DATE/compose_backup.yml"

# Redis backup
echo "Backing up Redis..."
podman-compose exec redis redis-cli BGSAVE
sleep 10
podman cp $(podman-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/$DATE/redis_dump.rdb"

# Compress backup
echo "Compressing backup..."
tar -czf "$BACKUP_DIR/rag_interface_backup_$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

# Clean old backups
echo "Cleaning old backups..."
find "$BACKUP_DIR" -name "rag_interface_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup integrity
if tar -tzf "$BACKUP_DIR/rag_interface_backup_$DATE.tar.gz" > /dev/null; then
    echo "✓ Backup integrity verified"
    echo "Backup completed: $BACKUP_DIR/rag_interface_backup_$DATE.tar.gz"
else
    echo "✗ Backup integrity check failed"
    exit 1
fi
```

#### Backup Restoration
```bash
#!/bin/bash
# restore_backup.sh

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /opt/backups/rag-interface/rag_interface_backup_20250120_120000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/rag_restore_$(date +%s)"

echo "=== Backup Restoration - $(date) ==="
echo "Restoring from: $BACKUP_FILE"

# Extract backup
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

cd /opt/rag-interface/deployment/podman

# Stop services
echo "Stopping services..."
podman-compose down

# Start only database
echo "Starting database..."
podman-compose up -d postgres redis
sleep 30

# Restore databases
databases=("error_reporting_db" "user_management_db" "verification_db" "correction_engine_db" "rag_integration_db")

for db in "${databases[@]}"; do
    echo "Restoring database: $db"
    
    # Drop and recreate database
    podman-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS $db;"
    podman-compose exec postgres psql -U postgres -c "CREATE DATABASE $db;"
    
    # Restore from backup
    cat "$RESTORE_DIR"/*/"${db}.dump" | podman-compose exec -T postgres pg_restore -U postgres -d "$db"
    
    echo "✓ $db restored"
done

# Restore Redis
echo "Restoring Redis..."
podman cp "$RESTORE_DIR"/*/redis_dump.rdb $(podman-compose ps -q redis):/data/dump.rdb
podman-compose restart redis

# Restore configuration (manual review recommended)
echo "Configuration files available in: $RESTORE_DIR"
echo "Please review and manually restore configuration if needed"

# Start all services
echo "Starting all services..."
podman-compose up -d

echo "Restoration completed"
```

## 🔄 Update Processes

### Application Updates

#### Rolling Update Procedure
```bash
#!/bin/bash
# rolling_update.sh

VERSION="$1"
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "=== Rolling Update to Version $VERSION ==="

cd /opt/rag-interface/deployment/podman

# Create backup before update
./daily_backup.sh

# Update git repository
git fetch origin
git checkout "v$VERSION"

# Update environment if needed
if [ -f ".env.v$VERSION" ]; then
    echo "Updating environment configuration..."
    cp ".env.v$VERSION" .env
fi

# Build new images
echo "Building new images..."
podman-compose build

# Update services one by one
services=("error-reporting-service" "user-management-service" "rag-integration-service" "correction-engine-service" "verification-service" "frontend")

for service in "${services[@]}"; do
    echo "Updating $service..."
    
    # Update service
    podman-compose up -d --no-deps "$service"
    
    # Wait for health check
    sleep 30
    
    # Verify service is healthy
    if ! curl -f "http://localhost:$(podman-compose port $service | cut -d: -f2)/health" > /dev/null 2>&1; then
        echo "✗ $service health check failed"
        echo "Rolling back..."
        git checkout -
        podman-compose up -d --no-deps "$service"
        exit 1
    fi
    
    echo "✓ $service updated successfully"
done

echo "Rolling update completed successfully"
```

### Database Schema Updates

#### Schema Migration Script
```bash
#!/bin/bash
# migrate_schema.sh

MIGRATION_DIR="/opt/rag-interface/deployment/database/migrations"
VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "=== Database Schema Migration to Version $VERSION ==="

cd /opt/rag-interface/deployment/podman

# Create backup before migration
./daily_backup.sh

# Run migration scripts
if [ -d "$MIGRATION_DIR/v$VERSION" ]; then
    for script in "$MIGRATION_DIR/v$VERSION"/*.sql; do
        if [ -f "$script" ]; then
            echo "Running migration: $(basename $script)"
            podman-compose exec postgres psql -U postgres -f "/migrations/v$VERSION/$(basename $script)"
        fi
    done
else
    echo "No migration scripts found for version $VERSION"
fi

echo "Schema migration completed"
```

## 📊 Monitoring Guidelines

### Key Performance Indicators (KPIs)

#### System Metrics
- **CPU Usage**: < 80% average
- **Memory Usage**: < 85% of available
- **Disk Usage**: < 90% of available
- **Network I/O**: Monitor for unusual spikes

#### Application Metrics
- **Response Time**: < 2 seconds for 95th percentile
- **Error Rate**: < 1% of total requests
- **Throughput**: Monitor requests per second
- **Active Users**: Track concurrent sessions

#### Database Metrics
- **Connection Pool Usage**: < 80% of max connections
- **Query Performance**: < 100ms for 95th percentile
- **Lock Waits**: Monitor for blocking queries
- **Database Size Growth**: Track growth rate

### Monitoring Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rag-interface'
    static_configs:
      - targets: ['localhost:8000', 'localhost:8001', 'localhost:8002', 'localhost:8003', 'localhost:8004']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "RAG Interface System",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"rag-interface\"}",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Alerting Rules

#### Critical Alerts
```yaml
# alerts.yml
groups:
  - name: rag-interface
    rules:
      - alert: ServiceDown
        expr: up{job="rag-interface"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.instance }}"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connections high"
```

## 🚀 Performance Optimization

### Database Optimization

#### Index Optimization
```sql
-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
AND n_distinct > 100
AND correlation < 0.1;

-- Create recommended indexes
CREATE INDEX CONCURRENTLY idx_error_reports_created_at_status 
ON error_reports(created_at, status) 
WHERE status IN ('pending', 'in_progress');
```

#### Query Optimization
```sql
-- Identify slow queries
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY total_exec_time DESC
LIMIT 10;

-- Optimize connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

### Application Optimization

#### Container Resource Limits
```yaml
# docker-compose.yml
services:
  error-reporting-service:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

#### Caching Strategy
```python
# Redis caching configuration
CACHE_CONFIG = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        },
        'TIMEOUT': 300,  # 5 minutes
    }
}
```

## 🔒 Security Maintenance

### Regular Security Tasks

#### Certificate Management
```bash
#!/bin/bash
# check_certificates.sh

echo "=== Certificate Status Check ==="

# Check SSL certificate expiration
if command -v openssl &> /dev/null; then
    echo "Checking SSL certificates..."
    echo | openssl s_client -servername localhost -connect localhost:443 2>/dev/null | openssl x509 -noout -dates
fi

# Check container image vulnerabilities
echo "Checking container vulnerabilities..."
podman-compose images --format "{{.Repository}}:{{.Tag}}" | while read image; do
    echo "Scanning $image..."
    podman image scan "$image" || echo "Scan failed for $image"
done
```

#### Access Review
```bash
#!/bin/bash
# access_review.sh

cd /opt/rag-interface/deployment/podman

echo "=== Access Review - $(date) ==="

# List all users and their last login
podman-compose exec postgres psql -U postgres -d user_management_db -c "
SELECT username, roles, status, last_login_at,
       CASE 
           WHEN last_login_at IS NULL THEN 'Never logged in'
           WHEN last_login_at < NOW() - INTERVAL '90 days' THEN 'Inactive (90+ days)'
           WHEN last_login_at < NOW() - INTERVAL '30 days' THEN 'Inactive (30+ days)'
           ELSE 'Active'
       END as activity_status
FROM users
ORDER BY last_login_at DESC NULLS LAST;
"

# Check for admin users
echo -e "\nAdmin users:"
podman-compose exec postgres psql -U postgres -d user_management_db -c "
SELECT username, created_at, last_login_at
FROM users
WHERE roles::text LIKE '%admin%';
"
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-20  
**Next Review**: 2025-04-20
