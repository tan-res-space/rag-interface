# RAG Interface System - Troubleshooting Guide

## 🎯 Quick Diagnostic Checklist

When experiencing issues, run through this checklist first:

1. **System Status Check**
   ```bash
   # Check all services
   podman-compose ps
   
   # Quick health check
   curl http://localhost:3000/health
   curl http://localhost:8000/health
   ```

2. **Resource Check**
   ```bash
   # System resources
   free -h          # Memory
   df -h            # Disk space
   top              # CPU usage
   ```

3. **Network Check**
   ```bash
   # Port availability
   netstat -tlnp | grep -E ':(3000|8000|8001|8002|8003|8004|5432|6379)'
   ```

4. **Log Review**
   ```bash
   # Recent errors
   podman-compose logs --since=1h | grep -i error
   ```

## 🔍 Component-Specific Diagnostics

### Frontend Application Issues

#### Symptom: Blank Page or Loading Forever

**Diagnostic Steps:**
1. Check browser console (F12 → Console tab)
2. Check network requests (F12 → Network tab)
3. Verify frontend service status

**Commands:**
```bash
# Check frontend service
podman-compose logs frontend

# Check if frontend is responding
curl -I http://localhost:3000

# Check nginx configuration
podman-compose exec frontend nginx -t
```

**Common Causes & Solutions:**
- **JavaScript errors**: Check browser console, update browser
- **API connection issues**: Verify backend services are running
- **Nginx misconfiguration**: Check nginx.conf and default.conf

#### Symptom: API Calls Failing

**Diagnostic Steps:**
1. Check browser Network tab for failed requests
2. Verify API endpoints are accessible
3. Check CORS configuration

**Commands:**
```bash
# Test API endpoints directly
curl http://localhost:8000/api/v1/health
curl http://localhost:8001/api/v1/health

# Check API logs
podman-compose logs error-reporting-service
podman-compose logs user-management-service
```

### Backend Service Issues

#### Symptom: Service Won't Start

**Diagnostic Steps:**
1. Check service logs for startup errors
2. Verify environment variables
3. Check database connectivity
4. Verify port availability

**Commands:**
```bash
# Check specific service logs
podman-compose logs error-reporting-service

# Check environment variables
podman-compose exec error-reporting-service env | grep -E '(DATABASE|REDIS|JWT)'

# Test database connection
podman-compose exec error-reporting-service python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

**Common Causes & Solutions:**
- **Missing environment variables**: Check .env file
- **Database connection issues**: Verify database is running and credentials are correct
- **Port conflicts**: Check if ports are already in use
- **Dependency issues**: Rebuild container images

#### Symptom: High Memory Usage

**Diagnostic Steps:**
1. Monitor container resource usage
2. Check for memory leaks in application logs
3. Review database connection pooling

**Commands:**
```bash
# Monitor container resources
podman stats

# Check memory usage per service
podman-compose exec error-reporting-service ps aux --sort=-%mem

# Check database connections
podman-compose exec postgres psql -U postgres -c "
SELECT datname, numbackends, xact_commit, xact_rollback 
FROM pg_stat_database 
WHERE datname NOT IN ('template0', 'template1', 'postgres');
"
```

### Database Issues

#### Symptom: Connection Refused

**Diagnostic Steps:**
1. Check if PostgreSQL is running
2. Verify connection parameters
3. Check network connectivity
4. Review authentication configuration

**Commands:**
```bash
# Check PostgreSQL status
podman-compose logs postgres

# Test connection
podman-compose exec postgres pg_isready -U postgres

# Check active connections
podman-compose exec postgres psql -U postgres -c "
SELECT pid, usename, application_name, client_addr, state 
FROM pg_stat_activity 
WHERE state = 'active';
"

# Check authentication
podman-compose exec postgres cat /var/lib/postgresql/data/pg_hba.conf
```

**Common Causes & Solutions:**
- **PostgreSQL not running**: Start PostgreSQL service
- **Wrong credentials**: Check username/password in .env
- **Network issues**: Verify container networking
- **Authentication misconfiguration**: Review pg_hba.conf

#### Symptom: Slow Query Performance

**Diagnostic Steps:**
1. Identify slow queries
2. Check index usage
3. Analyze query execution plans
4. Review database statistics

**Commands:**
```bash
# Enable query logging (temporary)
podman-compose exec postgres psql -U postgres -c "
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
"

# Check slow queries
podman-compose exec postgres psql -U postgres -c "
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
"

# Check index usage
podman-compose exec postgres psql -U postgres -d error_reporting_db -c "
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
"
```

### Redis Cache Issues

#### Symptom: Cache Not Working

**Diagnostic Steps:**
1. Check Redis connectivity
2. Verify cache configuration
3. Monitor cache hit rates
4. Check memory usage

**Commands:**
```bash
# Test Redis connection
podman-compose exec redis redis-cli ping

# Check Redis info
podman-compose exec redis redis-cli info

# Monitor Redis operations
podman-compose exec redis redis-cli monitor

# Check cache statistics
podman-compose exec redis redis-cli info stats
```

**Common Causes & Solutions:**
- **Redis not running**: Start Redis service
- **Authentication issues**: Check Redis password
- **Memory limits**: Increase Redis memory allocation
- **Configuration errors**: Review Redis configuration

## 🚨 Error Code Reference

### HTTP Status Codes

| Code | Meaning | Common Causes | Solutions |
|------|---------|---------------|-----------|
| 400 | Bad Request | Invalid input data, malformed JSON | Validate request format and data |
| 401 | Unauthorized | Invalid credentials, expired token | Check authentication, refresh token |
| 403 | Forbidden | Insufficient permissions | Verify user roles and permissions |
| 404 | Not Found | Resource doesn't exist, wrong URL | Check resource ID and endpoint |
| 500 | Internal Server Error | Application error, database issue | Check service logs, database connectivity |
| 502 | Bad Gateway | Service unavailable, proxy error | Check service status, restart if needed |
| 503 | Service Unavailable | Service overloaded, maintenance | Check resource usage, scale if needed |

### Application Error Codes

#### Error Reporting Service (ERS)
- **ERS-001**: Database connection failed
- **ERS-002**: Invalid error report format
- **ERS-003**: Duplicate error report
- **ERS-004**: Category not found
- **ERS-005**: Validation failed

#### User Management Service (UMS)
- **UMS-001**: User authentication failed
- **UMS-002**: Invalid JWT token
- **UMS-003**: User not found
- **UMS-004**: Permission denied
- **UMS-005**: Password policy violation

#### RAG Integration Service (RIS)
- **RIS-001**: Vector database connection failed
- **RIS-002**: Embedding generation failed
- **RIS-003**: Similarity search timeout
- **RIS-004**: Invalid query format
- **RIS-005**: API key invalid

## 🔧 Advanced Diagnostics

### Performance Profiling

#### Database Performance
```bash
# Enable detailed logging
podman-compose exec postgres psql -U postgres -c "
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 0;
SELECT pg_reload_conf();
"

# Analyze query performance
podman-compose exec postgres psql -U postgres -c "
SELECT query, calls, total_exec_time, mean_exec_time, stddev_exec_time
FROM pg_stat_statements 
WHERE calls > 100
ORDER BY total_exec_time DESC 
LIMIT 20;
"
```

#### Application Performance
```bash
# Monitor application metrics
podman-compose exec error-reporting-service python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'CPU: {process.cpu_percent()}%')
print(f'Threads: {process.num_threads()}')
"
```

### Network Diagnostics

#### Container Networking
```bash
# Check container network
podman network ls
podman network inspect rag-network

# Test inter-container connectivity
podman-compose exec frontend ping postgres
podman-compose exec error-reporting-service ping redis

# Check port mappings
podman-compose port frontend
podman-compose port error-reporting-service
```

#### DNS Resolution
```bash
# Test DNS resolution
podman-compose exec frontend nslookup postgres
podman-compose exec frontend nslookup redis

# Check /etc/hosts
podman-compose exec frontend cat /etc/hosts
```

### Security Diagnostics

#### Authentication Issues
```bash
# Check JWT token validity
podman-compose exec user-management-service python -c "
import jwt
import os
token = 'your-jwt-token-here'
secret = os.environ['JWT_SECRET_KEY']
try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
    print('Token valid:', payload)
except jwt.ExpiredSignatureError:
    print('Token expired')
except jwt.InvalidTokenError:
    print('Token invalid')
"
```

#### Permission Verification
```bash
# Check user permissions
podman-compose exec postgres psql -U postgres -d user_management_db -c "
SELECT u.username, u.roles, p.name as permission
FROM users u
JOIN role_permissions rp ON rp.role = ANY(string_to_array(trim(both '[]' from u.roles::text), ','))
JOIN permissions p ON p.id = rp.permission_id
WHERE u.username = 'your-username';
"
```

## 🔄 Recovery Procedures

### Service Recovery

#### Restart Individual Service
```bash
# Restart specific service
podman-compose restart error-reporting-service

# Force recreate service
podman-compose up -d --force-recreate error-reporting-service
```

#### Full System Recovery
```bash
# Stop all services
podman-compose down

# Clean up containers and networks
podman system prune -f

# Restart system
podman-compose up -d
```

### Database Recovery

#### Restore from Backup
```bash
# Stop services
podman-compose down

# Start only database
podman-compose up -d postgres

# Wait for database to be ready
sleep 30

# Restore database
podman-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS error_reporting_db;"
podman-compose exec postgres psql -U postgres -c "CREATE DATABASE error_reporting_db;"
cat backup/error_reporting_db.sql | podman-compose exec -T postgres psql -U postgres error_reporting_db

# Restart all services
podman-compose up -d
```

#### Database Corruption Recovery
```bash
# Check database integrity
podman-compose exec postgres psql -U postgres -c "
SELECT datname, pg_database_size(datname) as size
FROM pg_database 
WHERE datistemplate = false;
"

# Repair database (if needed)
podman-compose exec postgres psql -U postgres -c "REINDEX DATABASE error_reporting_db;"
```

## 📊 Monitoring and Alerting

### Health Check Scripts

#### Comprehensive Health Check
```bash
#!/bin/bash
# health_check.sh

echo "=== RAG Interface System Health Check ==="
echo "Timestamp: $(date)"
echo

# Check services
echo "Service Status:"
podman-compose ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

# Check endpoints
echo "Endpoint Health:"
endpoints=(
    "http://localhost:3000/health:Frontend"
    "http://localhost:8000/health:Error Reporting"
    "http://localhost:8001/health:User Management"
    "http://localhost:8002/health:RAG Integration"
    "http://localhost:8003/health:Correction Engine"
    "http://localhost:8004/health:Verification"
)

for endpoint in "${endpoints[@]}"; do
    url="${endpoint%:*}"
    name="${endpoint#*:}"
    if curl -f -s "$url" > /dev/null; then
        echo "✓ $name: OK"
    else
        echo "✗ $name: FAILED"
    fi
done
echo

# Check resources
echo "System Resources:"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
```

### Log Analysis

#### Error Pattern Detection
```bash
# Find common error patterns
podman-compose logs --since=24h | grep -i error | sort | uniq -c | sort -nr | head -10

# Check for specific error types
podman-compose logs --since=24h | grep -E "(500|502|503|504)" | wc -l

# Monitor authentication failures
podman-compose logs user-management-service --since=24h | grep -i "authentication failed" | wc -l
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-20  
**Next Review**: 2025-04-20
