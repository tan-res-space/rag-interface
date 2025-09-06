# ERS Quick Reference Card

## 🚀 Quick Start (5 minutes)

```bash
# 1. Setup
cd /path/to/rag-interface
python -m venv ers_env
source ers_env/bin/activate  # Linux/macOS
# ers_env\Scripts\activate   # Windows
pip install -r requirements.txt

# 2. Configure (create .env file)
echo "DB_TYPE=in_memory" > .env
echo "EVENT_BUS_TYPE=in_memory" >> .env

# 3. Test
python test_ers.py

# 4. Health Check
python health_check.py
```

## 🐘 PostgreSQL Local Development

- Full guide: see docs/postgres-local-dev.md
- Handy Makefile targets:
```bash
make db-up        # Start/launch local Postgres (Podman)
make db-init      # Create tables via app adapter
make db-health    # App-level DB health check
make db-crud-test # CRUD smoke test through adapter
make db-down      # Stop Postgres container
```

## 📋 Essential Commands

### Health & Status
```bash
python health_check.py              # Check all components
python performance_test.py          # Performance test
python query_errors.py              # View stored errors
```

### Testing
```bash
python test_ers.py                  # Basic functionality test
python submit_test_errors.py        # Submit various error types
python -m pytest tests/integration/ # Run integration tests
```

### Data Management
```bash
python clear_test_data.py           # Clear all test data
python submit_test_errors.py        # Add sample data
```

### Configuration
```bash
# Switch to in-memory (testing)
export DB_TYPE=in_memory
export EVENT_BUS_TYPE=in_memory

# Switch to PostgreSQL (production)
export DB_TYPE=postgresql
export EVENT_BUS_TYPE=in_memory
```

## 🔧 Configuration Templates

### Testing (.env)
```bash
DB_TYPE=in_memory
EVENT_BUS_TYPE=in_memory
DEBUG=true
LOG_LEVEL=DEBUG
```

### Production (.env)
```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=error_reporting
DB_USERNAME=ers_user
DB_PASSWORD=ers_password
EVENT_BUS_TYPE=in_memory
DEBUG=false
LOG_LEVEL=INFO
```

## 🚨 Troubleshooting

### Common Issues
```bash
# Python not found
python --version  # Should show 3.11+

# Module not found
cd /path/to/rag-interface
source ers_env/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# Database connection failed
export DB_TYPE=in_memory  # Use for testing

# Permission denied
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

### Reset to Working State
```bash
export DB_TYPE=in_memory
export EVENT_BUS_TYPE=in_memory
python clear_test_data.py
python health_check.py
```

## 📊 Expected Outputs

### Healthy System
```
🏥 ERS Health Check
📊 Database Health: ✅ HEALTHY
📡 Event Bus Health: ✅ HEALTHY
🎉 OVERALL STATUS: ✅ HEALTHY
```

### Successful Test
```
🧪 Testing Error Reporting Service...
✅ Response: success
✅ Error ID: 550e8400-e29b-41d4-a716-446655440000
🎉 All tests completed successfully!
```

### Good Performance
```
📈 Performance Results:
   Average Time per Error: 15.20 ms
   Performance: ✅ EXCELLENT (< 100ms per error)
```

## 📞 Support Checklist

Before contacting support, run:
```bash
python health_check.py > health_report.txt
python --version > system_info.txt
cat .env > config_info.txt  # Remove passwords!
```

Include these files with your support request.

## 🎯 Success Criteria

✅ Health check shows all components healthy
✅ Test script completes without errors
✅ Performance under 100ms per error
✅ Can submit and query error reports
✅ Database and event bus adapters working

**Time to complete setup: < 30 minutes**
