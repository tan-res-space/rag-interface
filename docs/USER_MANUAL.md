# Error Reporting Service (ERS) - User Manual

**Version**: 1.0  
**Target Audience**: QA Personnel, System Administrators, Non-Technical Users  
**Estimated Setup Time**: 30 minutes  

---

## 📋 Table of Contents

1. [Prerequisites and Installation](#1-prerequisites-and-installation)
2. [Database Setup](#2-database-setup)
3. [Configuration Guide](#3-configuration-guide)
4. [Running the Application](#4-running-the-application)
5. [Testing and Validation](#5-testing-and-validation)
6. [Health Monitoring](#6-health-monitoring)
7. [Common Operations](#7-common-operations)
8. [Troubleshooting Guide](#8-troubleshooting-guide)

---

## 1. Prerequisites and Installation

### 1.1 System Requirements

**Minimum Requirements:**
- **Operating System**: Windows 10, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.11 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free disk space
- **Network**: Internet connection for downloading dependencies

### 1.2 Check Python Installation

**Step 1**: Open your command prompt or terminal
- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **macOS**: Press `Cmd + Space`, type `terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

**Step 2**: Check Python version
```bash
python --version
```

**Expected Output:**
```
Python 3.11.x
```

**If Python is not installed or version is too old:**
- **Windows**: Download from [python.org](https://python.org/downloads)
- **macOS**: Use Homebrew: `brew install python@3.11`
- **Linux**: Use package manager: `sudo apt install python3.11`

### 1.3 Install the Error Reporting Service

**Step 1**: Navigate to the project directory
```bash
cd /path/to/rag-interface
```

**Step 2**: Create a virtual environment (recommended)
```bash
python -m venv ers_env
```

**Step 3**: Activate the virtual environment
```bash
# Windows
ers_env\Scripts\activate

# macOS/Linux
source ers_env/bin/activate
```

**Step 4**: Install required dependencies
```bash
pip install -r requirements.txt
```

**✅ Validation**: You should see packages being installed without errors.

---

## 2. Database Setup

### 2.1 Option A: PostgreSQL Setup (Recommended)

**Step 1**: Install PostgreSQL
- **Windows**: Download from [postgresql.org](https://postgresql.org/download)
- **macOS**: Use Homebrew: `brew install postgresql`
- **Linux**: `sudo apt install postgresql postgresql-contrib`

**Step 2**: Start PostgreSQL service
```bash
# Windows (as Administrator)
net start postgresql-x64-14

# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

**Step 3**: Create database and user
```bash
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL prompt, run these commands:
CREATE DATABASE error_reporting;
CREATE USER ers_user WITH PASSWORD 'ers_password';
GRANT ALL PRIVILEGES ON DATABASE error_reporting TO ers_user;
\q
```

**Step 4**: Test database connection
```bash
psql -U ers_user -d error_reporting -h localhost
```

**Expected Output:**
```
error_reporting=>
```

Type `\q` to exit.

### 2.2 Option B: In-Memory Database (For Testing)

If you want to skip database setup for quick testing, the ERS can use an in-memory database.

**Step 1**: Set environment variable
```bash
# Windows
set DB_TYPE=in_memory

# macOS/Linux
export DB_TYPE=in_memory
```

**✅ Validation**: No additional setup required for in-memory option.

### 2.3 Create Database Schema

**Step 1**: Navigate to the ERS directory
```bash
cd src/error_reporting_service
```

**Step 2**: Create database tables
```bash
python -c "
import asyncio
from infrastructure.adapters.database.factory import DatabaseAdapterFactory
from infrastructure.config.settings import settings

async def create_tables():
    adapter = await DatabaseAdapterFactory.create(settings.database)
    if hasattr(adapter, 'create_tables'):
        await adapter.create_tables()
        print('✅ Database tables created successfully')
    else:
        print('✅ Using in-memory database - no tables needed')

asyncio.run(create_tables())
"
```

**Expected Output:**
```
✅ Database tables created successfully
```

---

## 3. Configuration Guide

### 3.1 Environment Variables

The ERS uses environment variables for configuration. Create a `.env` file in the project root.

**Step 1**: Create configuration file
```bash
# Navigate to project root
cd /path/to/rag-interface

# Create .env file
touch .env  # Linux/macOS
# or create .env file manually on Windows
```

**Step 2**: Add configuration to `.env` file

**For PostgreSQL (Production):**
```bash
# Application Settings
APP_NAME=Error Reporting Service
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=error_reporting
DB_USERNAME=ers_user
DB_PASSWORD=ers_password

# Event Bus Configuration
EVENT_BUS_TYPE=in_memory
EVENT_BUS_CLIENT_ID=ers-service

# API Settings
API_PREFIX=/api/v1
SECRET_KEY=your-secret-key-change-in-production
```

**For In-Memory (Testing):**
```bash
# Application Settings
APP_NAME=Error Reporting Service - Test
DEBUG=true
LOG_LEVEL=DEBUG

# Database Configuration
DB_TYPE=in_memory

# Event Bus Configuration
EVENT_BUS_TYPE=in_memory
EVENT_BUS_CLIENT_ID=ers-test

# API Settings
API_PREFIX=/api/v1
SECRET_KEY=test-secret-key
```

### 3.2 Configuration Templates

**Development Environment (.env.dev):**
```bash
APP_NAME=ERS Development
DEBUG=true
LOG_LEVEL=DEBUG
DB_TYPE=in_memory
EVENT_BUS_TYPE=in_memory
```

**Staging Environment (.env.staging):**
```bash
APP_NAME=ERS Staging
DEBUG=false
LOG_LEVEL=INFO
DB_TYPE=postgresql
DB_HOST=staging-db.company.com
DB_DATABASE=error_reporting_staging
EVENT_BUS_TYPE=in_memory
```

**Production Environment (.env.prod):**
```bash
APP_NAME=ERS Production
DEBUG=false
LOG_LEVEL=WARNING
DB_TYPE=postgresql
DB_HOST=prod-db.company.com
DB_DATABASE=error_reporting_prod
EVENT_BUS_TYPE=kafka
EVENT_BUS_CONNECTION_STRING=prod-kafka.company.com:9092
```

**✅ Validation**: Check configuration by running:
```bash
python -c "
from src.error_reporting_service.infrastructure.config.settings import settings
print(f'App Name: {settings.app_name}')
print(f'Database Type: {settings.database.type}')
print(f'Event Bus Type: {settings.event_bus.type}')
"
```

---

## 4. Running the Application

### 4.1 Start the Error Reporting Service

**Step 1**: Ensure virtual environment is activated
```bash
# Check if virtual environment is active (you should see (ers_env) in prompt)
# If not active, run:
source ers_env/bin/activate  # macOS/Linux
# or
ers_env\Scripts\activate     # Windows
```

**Step 2**: Navigate to the ERS directory
```bash
cd src/error_reporting_service
```

**Step 3**: Start the service
```bash
python -m pytest tests/integration/test_multi_adapter_integration.py::TestMultiAdapterIntegration::test_submit_error_report_with_in_memory_adapters -v
```

**Expected Output:**
```
============================= test session starts ==============================
...
test_submit_error_report_with_in_memory_adapters PASSED [100%]
=============================== 1 passed in 0.05s ===============================
```

### 4.2 Verify Service is Running

**Step 1**: Check database connectivity
```bash
python -c "
import asyncio
from infrastructure.adapters.database.factory import DatabaseAdapterFactory
from infrastructure.config.settings import settings

async def check_db():
    adapter = await DatabaseAdapterFactory.create(settings.database)
    health = await adapter.health_check()
    print(f'✅ Database Health: {\"OK\" if health else \"FAILED\"}')
    
    info = adapter.get_connection_info()
    print(f'✅ Database Type: {info[\"adapter_type\"]}')

asyncio.run(check_db())
"
```

**Expected Output:**
```
✅ Database Health: OK
✅ Database Type: postgresql
```

**Step 2**: Check event bus connectivity
```bash
python -c "
import asyncio
from infrastructure.adapters.messaging.factory import EventBusAdapterFactory
from infrastructure.config.settings import settings

async def check_events():
    adapter = await EventBusAdapterFactory.create(settings.event_bus)
    health = await adapter.health_check()
    print(f'✅ Event Bus Health: {\"OK\" if health else \"FAILED\"}')
    
    info = adapter.get_connection_info()
    print(f'✅ Event Bus Type: {info[\"adapter_type\"]}')

asyncio.run(check_events())
"
```

**Expected Output:**
```
✅ Event Bus Health: OK
✅ Event Bus Type: in_memory
```

**✅ Validation**: Both database and event bus should show "OK" status.

---

## 5. Testing and Validation

### 5.1 Run Automated Test Suite

**Step 1**: Run all tests
```bash
cd /path/to/rag-interface
python -m pytest tests/unit/domain/ tests/unit/application/ tests/integration/ -v
```

**Expected Output:**
```
============================= test session starts ==============================
...
tests/unit/domain/test_error_report.py::TestErrorReportEntity::test_create_valid_error_report PASSED
tests/unit/application/test_submit_error_report_use_case.py::TestSubmitErrorReportUseCase::test_execute_valid_request_success PASSED
tests/integration/test_multi_adapter_integration.py::TestMultiAdapterIntegration::test_submit_error_report_with_in_memory_adapters PASSED
...
======================== 38 passed in 0.50s ===============================
```

**Step 2**: Run specific integration tests
```bash
python -m pytest tests/integration/ -v
```

**Expected Output:**
```
4 passed in 0.10s
```

### 5.2 Manual Testing with Sample Data

**Step 1**: Create a test script
```bash
# Create test_ers.py file
cat > test_ers.py << 'EOF'
import asyncio
from uuid import uuid4
from datetime import datetime

from src.error_reporting_service.domain.entities.error_report import ErrorReport, SeverityLevel
from src.error_reporting_service.domain.services.validation_service import ErrorValidationService
from src.error_reporting_service.domain.services.categorization_service import ErrorCategorizationService
from src.error_reporting_service.application.use_cases.submit_error_report import SubmitErrorReportUseCase
from src.error_reporting_service.application.dto.requests import SubmitErrorReportRequest
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.infrastructure.adapters.messaging.factory import EventBusAdapterFactory
from src.error_reporting_service.infrastructure.config.settings import settings

# Bridge classes
class DatabaseAdapterRepository:
    def __init__(self, db_adapter):
        self._db_adapter = db_adapter
    
    async def save(self, error_report):
        return await self._db_adapter.save_error_report(error_report)
    
    async def find_by_id(self, error_id):
        return await self._db_adapter.find_error_by_id(error_id)
    
    async def find_by_speaker(self, speaker_id, filters=None):
        return await self._db_adapter.find_errors_by_speaker(speaker_id, filters)
    
    async def find_by_job(self, job_id, filters=None):
        return await self._db_adapter.find_errors_by_job(job_id, filters)
    
    async def update(self, error_id, updates):
        return await self._db_adapter.update_error_report(error_id, updates)
    
    async def delete(self, error_id):
        return await self._db_adapter.delete_error_report(error_id)
    
    async def search(self, criteria, page=1, limit=20):
        return await self._db_adapter.search_errors(criteria)
    
    async def count(self, criteria=None):
        results = await self._db_adapter.search_errors(criteria or {})
        return len(results)

class EventBusAdapterPublisher:
    def __init__(self, event_adapter):
        self._event_adapter = event_adapter
    
    async def publish_error_reported(self, event):
        await self._event_adapter.publish_event("error.reported", event)
    
    async def publish_error_updated(self, event):
        await self._event_adapter.publish_event("error.updated", event)
    
    async def publish_error_deleted(self, event):
        await self._event_adapter.publish_event("error.deleted", event)

async def test_error_submission():
    print("🧪 Testing Error Reporting Service...")
    
    # Create adapters
    db_adapter = await DatabaseAdapterFactory.create(settings.database)
    event_adapter = await EventBusAdapterFactory.create(settings.event_bus)
    
    # Create repository and event publisher
    repository = DatabaseAdapterRepository(db_adapter)
    event_publisher = EventBusAdapterPublisher(event_adapter)
    
    # Create domain services
    validation_service = ErrorValidationService()
    categorization_service = ErrorCategorizationService()
    
    # Create use case
    use_case = SubmitErrorReportUseCase(
        repository=repository,
        event_publisher=event_publisher,
        validation_service=validation_service,
        categorization_service=categorization_service
    )
    
    # Test Case 1: Medical terminology error
    print("\n📝 Test Case 1: Medical Terminology Error")
    request1 = SubmitErrorReportRequest(
        job_id=str(uuid4()),
        speaker_id=str(uuid4()),
        original_text="The patient has diabetis and hypertention",
        corrected_text="The patient has diabetes and hypertension",
        error_categories=["medical_terminology", "spelling"],
        severity_level="high",
        start_position=16,
        end_position=40,
        context_notes="Common medical term misspellings",
        reported_by=str(uuid4()),
        metadata={"audio_quality": "good", "confidence": 0.95}
    )
    
    response1 = await use_case.execute(request1)
    print(f"✅ Response: {response1.status}")
    print(f"✅ Error ID: {response1.error_id}")
    print(f"✅ Message: {response1.message}")
    
    # Test Case 2: Grammar error
    print("\n📝 Test Case 2: Grammar Error")
    request2 = SubmitErrorReportRequest(
        job_id=str(uuid4()),
        speaker_id=str(uuid4()),
        original_text="The patient are feeling better",
        corrected_text="The patient is feeling better",
        error_categories=["grammar"],
        severity_level="medium",
        start_position=12,
        end_position=15,
        context_notes="Subject-verb agreement error",
        reported_by=str(uuid4()),
        metadata={"audio_quality": "fair"}
    )
    
    response2 = await use_case.execute(request2)
    print(f"✅ Response: {response2.status}")
    print(f"✅ Error ID: {response2.error_id}")
    print(f"✅ Message: {response2.message}")
    
    # Verify data was saved
    print("\n🔍 Verifying Data Storage...")
    from uuid import UUID
    saved_error1 = await db_adapter.find_error_by_id(UUID(response1.error_id))
    saved_error2 = await db_adapter.find_error_by_id(UUID(response2.error_id))
    
    print(f"✅ Error 1 saved: {saved_error1 is not None}")
    print(f"✅ Error 2 saved: {saved_error2 is not None}")
    
    if saved_error1:
        print(f"   Original: {saved_error1.original_text}")
        print(f"   Corrected: {saved_error1.corrected_text}")
        print(f"   Severity: {saved_error1.severity_level.value}")
    
    # Check events were published
    print("\n📡 Verifying Event Publishing...")
    if hasattr(event_adapter, 'get_events_for_topic'):
        events = event_adapter.get_events_for_topic("error.reported")
        print(f"✅ Events published: {len(events)}")
        for i, event in enumerate(events, 1):
            print(f"   Event {i}: {event['payload']['original_text'][:30]}...")
    
    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_error_submission())
EOF
```

**Step 2**: Run the test script
```bash
python test_ers.py
```

**Expected Output:**
```
🧪 Testing Error Reporting Service...

📝 Test Case 1: Medical Terminology Error
✅ Response: success
✅ Error ID: 550e8400-e29b-41d4-a716-446655440000
✅ Message: Error report submitted successfully

📝 Test Case 2: Grammar Error
✅ Response: success
✅ Error ID: 550e8400-e29b-41d4-a716-446655440001
✅ Message: Error report submitted successfully

🔍 Verifying Data Storage...
✅ Error 1 saved: True
✅ Error 2 saved: True
   Original: The patient has diabetis and hypertention
   Corrected: The patient has diabetes and hypertension
   Severity: high

📡 Verifying Event Publishing...
✅ Events published: 2
   Event 1: The patient has diabetis and hy...
   Event 2: The patient are feeling better...

🎉 All tests completed successfully!
```

**✅ Validation**: All test cases should show "success" status and data should be properly saved.

---

## 6. Health Monitoring

### 6.1 Application Health Check

**Step 1**: Create health check script
```bash
cat > health_check.py << 'EOF'
import asyncio
import sys
from datetime import datetime

from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.infrastructure.adapters.messaging.factory import EventBusAdapterFactory
from src.error_reporting_service.infrastructure.config.settings import settings

async def health_check():
    print(f"🏥 ERS Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    overall_health = True

    # Check Database
    print("\n📊 Database Health:")
    try:
        db_adapter = await DatabaseAdapterFactory.create(settings.database)
        db_health = await db_adapter.health_check()
        db_info = db_adapter.get_connection_info()

        print(f"   Status: {'✅ HEALTHY' if db_health else '❌ UNHEALTHY'}")
        print(f"   Type: {db_info['adapter_type']}")

        if db_info['adapter_type'] == 'postgresql':
            print(f"   Pool Size: {db_info.get('engine_info', {}).get('pool_size', 'N/A')}")
            print(f"   Active Connections: {db_info.get('engine_info', {}).get('checked_out', 'N/A')}")
        elif db_info['adapter_type'] == 'in_memory':
            print(f"   Records: {db_info.get('total_records', 0)}")

        if not db_health:
            overall_health = False

    except Exception as e:
        print(f"   Status: ❌ ERROR - {str(e)}")
        overall_health = False

    # Check Event Bus
    print("\n📡 Event Bus Health:")
    try:
        event_adapter = await EventBusAdapterFactory.create(settings.event_bus)
        event_health = await event_adapter.health_check()
        event_info = event_adapter.get_connection_info()

        print(f"   Status: {'✅ HEALTHY' if event_health else '❌ UNHEALTHY'}")
        print(f"   Type: {event_info['adapter_type']}")

        if event_info['adapter_type'] == 'in_memory':
            print(f"   Topics: {len(event_info.get('topics', []))}")
            print(f"   Total Events: {event_info.get('total_events', 0)}")

        if not event_health:
            overall_health = False

    except Exception as e:
        print(f"   Status: ❌ ERROR - {str(e)}")
        overall_health = False

    # Check Configuration
    print("\n⚙️ Configuration:")
    print(f"   App Name: {settings.app_name}")
    print(f"   Debug Mode: {settings.debug}")
    print(f"   Log Level: {settings.log_level}")
    print(f"   Database Type: {settings.database.type}")
    print(f"   Event Bus Type: {settings.event_bus.type}")

    # Overall Status
    print("\n" + "=" * 50)
    if overall_health:
        print("🎉 OVERALL STATUS: ✅ HEALTHY")
        sys.exit(0)
    else:
        print("⚠️ OVERALL STATUS: ❌ UNHEALTHY")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(health_check())
EOF
```

**Step 2**: Run health check
```bash
python health_check.py
```

**Expected Output (Healthy System):**
```
🏥 ERS Health Check - 2025-08-07 14:30:00
==================================================

📊 Database Health:
   Status: ✅ HEALTHY
   Type: postgresql
   Pool Size: 10
   Active Connections: 0

📡 Event Bus Health:
   Status: ✅ HEALTHY
   Type: in_memory
   Topics: 0
   Total Events: 0

⚙️ Configuration:
   App Name: Error Reporting Service
   Debug Mode: False
   Log Level: INFO
   Database Type: postgresql
   Event Bus Type: in_memory

==================================================
🎉 OVERALL STATUS: ✅ HEALTHY
```

### 6.2 Performance Monitoring

**Step 1**: Create performance test script
```bash
cat > performance_test.py << 'EOF'
import asyncio
import time
from uuid import uuid4

from src.error_reporting_service.domain.services.validation_service import ErrorValidationService
from src.error_reporting_service.domain.services.categorization_service import ErrorCategorizationService
from src.error_reporting_service.application.use_cases.submit_error_report import SubmitErrorReportUseCase
from src.error_reporting_service.application.dto.requests import SubmitErrorReportRequest
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.infrastructure.adapters.messaging.factory import EventBusAdapterFactory
from src.error_reporting_service.infrastructure.config.settings import settings

# Bridge classes (same as before)
class DatabaseAdapterRepository:
    def __init__(self, db_adapter):
        self._db_adapter = db_adapter
    async def save(self, error_report):
        return await self._db_adapter.save_error_report(error_report)
    async def find_by_id(self, error_id):
        return await self._db_adapter.find_error_by_id(error_id)
    async def find_by_speaker(self, speaker_id, filters=None):
        return await self._db_adapter.find_errors_by_speaker(speaker_id, filters)
    async def find_by_job(self, job_id, filters=None):
        return await self._db_adapter.find_errors_by_job(job_id, filters)
    async def update(self, error_id, updates):
        return await self._db_adapter.update_error_report(error_id, updates)
    async def delete(self, error_id):
        return await self._db_adapter.delete_error_report(error_id)
    async def search(self, criteria, page=1, limit=20):
        return await self._db_adapter.search_errors(criteria)
    async def count(self, criteria=None):
        results = await self._db_adapter.search_errors(criteria or {})
        return len(results)

class EventBusAdapterPublisher:
    def __init__(self, event_adapter):
        self._event_adapter = event_adapter
    async def publish_error_reported(self, event):
        await self._event_adapter.publish_event("error.reported", event)
    async def publish_error_updated(self, event):
        await self._event_adapter.publish_event("error.updated", event)
    async def publish_error_deleted(self, event):
        await self._event_adapter.publish_event("error.deleted", event)

async def performance_test():
    print("⚡ ERS Performance Test")
    print("=" * 40)

    # Setup
    db_adapter = await DatabaseAdapterFactory.create(settings.database)
    event_adapter = await EventBusAdapterFactory.create(settings.event_bus)
    repository = DatabaseAdapterRepository(db_adapter)
    event_publisher = EventBusAdapterPublisher(event_adapter)
    validation_service = ErrorValidationService()
    categorization_service = ErrorCategorizationService()

    use_case = SubmitErrorReportUseCase(
        repository=repository,
        event_publisher=event_publisher,
        validation_service=validation_service,
        categorization_service=categorization_service
    )

    # Performance Test: Submit multiple errors
    num_errors = 10
    print(f"\n📊 Submitting {num_errors} error reports...")

    start_time = time.time()

    for i in range(num_errors):
        request = SubmitErrorReportRequest(
            job_id=str(uuid4()),
            speaker_id=str(uuid4()),
            original_text=f"Test error number {i+1} with some text",
            corrected_text=f"Test correction number {i+1} with some text",
            error_categories=["grammar"],
            severity_level="low",
            start_position=0,
            end_position=10,
            reported_by=str(uuid4()),
            metadata={"test_run": True}
        )

        response = await use_case.execute(request)
        if response.status != "success":
            print(f"❌ Error {i+1} failed: {response.message}")
        else:
            print(f"✅ Error {i+1} submitted")

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n📈 Performance Results:")
    print(f"   Total Time: {total_time:.2f} seconds")
    print(f"   Average Time per Error: {(total_time/num_errors)*1000:.2f} ms")
    print(f"   Throughput: {num_errors/total_time:.2f} errors/second")

    # Performance thresholds
    avg_time_ms = (total_time/num_errors)*1000
    if avg_time_ms < 100:
        print("   Performance: ✅ EXCELLENT (< 100ms per error)")
    elif avg_time_ms < 500:
        print("   Performance: ✅ GOOD (< 500ms per error)")
    elif avg_time_ms < 1000:
        print("   Performance: ⚠️ ACCEPTABLE (< 1s per error)")
    else:
        print("   Performance: ❌ SLOW (> 1s per error)")

if __name__ == "__main__":
    asyncio.run(performance_test())
EOF
```

**Step 2**: Run performance test
```bash
python performance_test.py
```

**Expected Output:**
```
⚡ ERS Performance Test
========================================

📊 Submitting 10 error reports...
✅ Error 1 submitted
✅ Error 2 submitted
...
✅ Error 10 submitted

📈 Performance Results:
   Total Time: 0.15 seconds
   Average Time per Error: 15.20 ms
   Throughput: 66.67 errors/second
   Performance: ✅ EXCELLENT (< 100ms per error)
```

### 6.3 Log Monitoring

**Step 1**: Check log locations
```bash
# ERS doesn't create log files by default, but you can enable logging
# Create a simple logging test
python -c "
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ERS')
logger.info('✅ ERS logging is working')
logger.warning('⚠️ This is a warning message')
logger.error('❌ This is an error message')
"
```

**Expected Output:**
```
2025-08-07 14:30:00,123 - ERS - INFO - ✅ ERS logging is working
2025-08-07 14:30:00,124 - ERS - WARNING - ⚠️ This is a warning message
2025-08-07 14:30:00,125 - ERS - ERROR - ❌ This is an error message
```

**✅ Validation**: Health checks should show all components as healthy, and performance should be under 100ms per error.

---

## 7. Common Operations

### 7.1 Submit Test Error Reports

**Step 1**: Create different types of test errors
```bash
cat > submit_test_errors.py << 'EOF'
import asyncio
from uuid import uuid4

# Import all necessary components (same setup as before)
from src.error_reporting_service.domain.services.validation_service import ErrorValidationService
from src.error_reporting_service.domain.services.categorization_service import ErrorCategorizationService
from src.error_reporting_service.application.use_cases.submit_error_report import SubmitErrorReportUseCase
from src.error_reporting_service.application.dto.requests import SubmitErrorReportRequest
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.infrastructure.adapters.messaging.factory import EventBusAdapterFactory
from src.error_reporting_service.infrastructure.config.settings import settings

# Bridge classes (abbreviated for space)
class DatabaseAdapterRepository:
    def __init__(self, db_adapter):
        self._db_adapter = db_adapter
    async def save(self, error_report):
        return await self._db_adapter.save_error_report(error_report)
    async def find_by_id(self, error_id):
        return await self._db_adapter.find_error_by_id(error_id)
    async def find_by_speaker(self, speaker_id, filters=None):
        return await self._db_adapter.find_errors_by_speaker(speaker_id, filters)
    async def find_by_job(self, job_id, filters=None):
        return await self._db_adapter.find_errors_by_job(job_id, filters)
    async def update(self, error_id, updates):
        return await self._db_adapter.update_error_report(error_id, updates)
    async def delete(self, error_id):
        return await self._db_adapter.delete_error_report(error_id)
    async def search(self, criteria, page=1, limit=20):
        return await self._db_adapter.search_errors(criteria)
    async def count(self, criteria=None):
        results = await self._db_adapter.search_errors(criteria or {})
        return len(results)

class EventBusAdapterPublisher:
    def __init__(self, event_adapter):
        self._event_adapter = event_adapter
    async def publish_error_reported(self, event):
        await self._event_adapter.publish_event("error.reported", event)
    async def publish_error_updated(self, event):
        await self._event_adapter.publish_event("error.updated", event)
    async def publish_error_deleted(self, event):
        await self._event_adapter.publish_event("error.deleted", event)

async def submit_test_errors():
    print("📝 Submitting Various Test Error Types")
    print("=" * 45)

    # Setup
    db_adapter = await DatabaseAdapterFactory.create(settings.database)
    event_adapter = await EventBusAdapterFactory.create(settings.event_bus)
    repository = DatabaseAdapterRepository(db_adapter)
    event_publisher = EventBusAdapterPublisher(event_adapter)
    validation_service = ErrorValidationService()
    categorization_service = ErrorCategorizationService()

    use_case = SubmitErrorReportUseCase(
        repository=repository,
        event_publisher=event_publisher,
        validation_service=validation_service,
        categorization_service=categorization_service
    )

    # Test Error Types
    test_errors = [
        {
            "name": "Medical Terminology Error",
            "original": "Patient has diabetis and hypertention",
            "corrected": "Patient has diabetes and hypertension",
            "categories": ["medical_terminology", "spelling"],
            "severity": "high"
        },
        {
            "name": "Grammar Error",
            "original": "The patient are feeling better today",
            "corrected": "The patient is feeling better today",
            "categories": ["grammar"],
            "severity": "medium"
        },
        {
            "name": "Pronunciation Error",
            "original": "The patient has a coff",
            "corrected": "The patient has a cough",
            "categories": ["pronunciation"],
            "severity": "low"
        },
        {
            "name": "Context Error",
            "original": "Patient is taking medication for their heart condition",
            "corrected": "Patient is taking medication for his heart condition",
            "categories": ["context", "grammar"],
            "severity": "medium"
        }
    ]

    submitted_errors = []

    for i, error in enumerate(test_errors, 1):
        print(f"\n{i}. {error['name']}")
        print(f"   Original: {error['original']}")
        print(f"   Corrected: {error['corrected']}")

        request = SubmitErrorReportRequest(
            job_id=str(uuid4()),
            speaker_id=str(uuid4()),
            original_text=error['original'],
            corrected_text=error['corrected'],
            error_categories=error['categories'],
            severity_level=error['severity'],
            start_position=0,
            end_position=len(error['original']),
            context_notes=f"Test error type: {error['name']}",
            reported_by=str(uuid4()),
            metadata={"test_type": error['name'], "automated": True}
        )

        try:
            response = await use_case.execute(request)
            print(f"   Status: ✅ {response.status}")
            print(f"   Error ID: {response.error_id}")
            submitted_errors.append(response.error_id)
        except Exception as e:
            print(f"   Status: ❌ Failed - {str(e)}")

    print(f"\n📊 Summary:")
    print(f"   Total Errors Submitted: {len(submitted_errors)}")
    print(f"   Error IDs: {submitted_errors}")

    return submitted_errors

if __name__ == "__main__":
    asyncio.run(submit_test_errors())
EOF
```

**Step 2**: Run the test error submission
```bash
python submit_test_errors.py
```

**Expected Output:**
```
📝 Submitting Various Test Error Types
=============================================

1. Medical Terminology Error
   Original: Patient has diabetis and hypertention
   Corrected: Patient has diabetes and hypertension
   Status: ✅ success
   Error ID: 550e8400-e29b-41d4-a716-446655440000

2. Grammar Error
   Original: The patient are feeling better today
   Corrected: The patient is feeling better today
   Status: ✅ success
   Error ID: 550e8400-e29b-41d4-a716-446655440001

3. Pronunciation Error
   Original: The patient has a coff
   Corrected: The patient has a cough
   Status: ✅ success
   Error ID: 550e8400-e29b-41d4-a716-446655440002

4. Context Error
   Original: Patient is taking medication for their heart condition
   Corrected: Patient is taking medication for his heart condition
   Status: ✅ success
   Error ID: 550e8400-e29b-41d4-a716-446655440003

📊 Summary:
   Total Errors Submitted: 4
   Error IDs: ['550e8400-e29b-41d4-a716-446655440000', ...]
```

### 7.2 Query Existing Error Reports

**Step 1**: Create query script
```bash
cat > query_errors.py << 'EOF'
import asyncio
from uuid import UUID

from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.infrastructure.config.settings import settings

async def query_errors():
    print("🔍 Querying Error Reports")
    print("=" * 30)

    db_adapter = await DatabaseAdapterFactory.create(settings.database)

    # Query all errors
    print("\n📋 All Error Reports:")
    all_errors = await db_adapter.search_errors({})

    if not all_errors:
        print("   No error reports found.")
        return

    for i, error in enumerate(all_errors, 1):
        print(f"\n   {i}. Error ID: {error.error_id}")
        print(f"      Original: {error.original_text[:50]}...")
        print(f"      Corrected: {error.corrected_text[:50]}...")
        print(f"      Categories: {', '.join(error.error_categories)}")
        print(f"      Severity: {error.severity_level.value}")
        print(f"      Status: {error.status.value}")
        print(f"      Reported: {error.reported_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # Query by severity
    print(f"\n🔥 High Severity Errors:")
    high_severity_errors = await db_adapter.search_errors({"severity_level": "high"})
    print(f"   Found: {len(high_severity_errors)} high severity errors")

    # Query by category
    print(f"\n💊 Medical Terminology Errors:")
    medical_errors = []
    for error in all_errors:
        if "medical_terminology" in error.error_categories:
            medical_errors.append(error)
    print(f"   Found: {len(medical_errors)} medical terminology errors")

    print(f"\n📊 Summary:")
    print(f"   Total Errors: {len(all_errors)}")
    print(f"   High Severity: {len(high_severity_errors)}")
    print(f"   Medical Terms: {len(medical_errors)}")

if __name__ == "__main__":
    asyncio.run(query_errors())
EOF
```

**Step 2**: Run the query script
```bash
python query_errors.py
```

**Expected Output:**
```
🔍 Querying Error Reports
==============================

📋 All Error Reports:

   1. Error ID: 550e8400-e29b-41d4-a716-446655440000
      Original: Patient has diabetis and hypertention...
      Corrected: Patient has diabetes and hypertension...
      Categories: medical_terminology, spelling
      Severity: high
      Status: pending
      Reported: 2025-08-07 14:30:00

   2. Error ID: 550e8400-e29b-41d4-a716-446655440001
      Original: The patient are feeling better today...
      Corrected: The patient is feeling better today...
      Categories: grammar
      Severity: medium
      Status: pending
      Reported: 2025-08-07 14:30:01

🔥 High Severity Errors:
   Found: 1 high severity errors

💊 Medical Terminology Errors:
   Found: 1 medical terminology errors

📊 Summary:
   Total Errors: 4
   High Severity: 1
   Medical Terms: 1
```

### 7.3 Switch Between Database Adapters

**Step 1**: Test with in-memory database
```bash
# Set environment variable for in-memory database
export DB_TYPE=in_memory  # Linux/macOS
# or
set DB_TYPE=in_memory     # Windows

# Run health check to verify
python health_check.py
```

**Expected Output:**
```
📊 Database Health:
   Status: ✅ HEALTHY
   Type: in_memory
   Records: 0
```

**Step 2**: Switch back to PostgreSQL
```bash
# Set environment variable for PostgreSQL
export DB_TYPE=postgresql  # Linux/macOS
# or
set DB_TYPE=postgresql     # Windows

# Run health check to verify
python health_check.py
```

**Expected Output:**
```
📊 Database Health:
   Status: ✅ HEALTHY
   Type: postgresql
   Pool Size: 10
   Active Connections: 0
```

### 7.4 Clear Test Data

**Step 1**: Create data cleanup script
```bash
cat > clear_test_data.py << 'EOF'
import asyncio

from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.infrastructure.adapters.messaging.factory import EventBusAdapterFactory
from src.error_reporting_service.infrastructure.config.settings import settings

async def clear_test_data():
    print("🧹 Clearing Test Data")
    print("=" * 25)

    # Clear database
    print("\n📊 Clearing Database...")
    db_adapter = await DatabaseAdapterFactory.create(settings.database)

    if hasattr(db_adapter, 'clear_all_data'):
        db_adapter.clear_all_data()
        print("   ✅ In-memory database cleared")
    else:
        # For PostgreSQL, we'd need to implement a clear method
        # For now, just show what would be cleared
        all_errors = await db_adapter.search_errors({})
        print(f"   Found {len(all_errors)} error reports")

        for error in all_errors:
            deleted = await db_adapter.delete_error_report(error.error_id)
            if deleted:
                print(f"   ✅ Deleted error {error.error_id}")

    # Clear events
    print("\n📡 Clearing Events...")
    event_adapter = await EventBusAdapterFactory.create(settings.event_bus)

    if hasattr(event_adapter, 'clear_all_events'):
        event_adapter.clear_all_events()
        print("   ✅ All events cleared")
    else:
        print("   ℹ️ Event clearing not supported for this adapter")

    # Verify cleanup
    print("\n🔍 Verifying Cleanup...")
    remaining_errors = await db_adapter.search_errors({})
    print(f"   Remaining errors: {len(remaining_errors)}")

    if hasattr(event_adapter, 'get_connection_info'):
        event_info = event_adapter.get_connection_info()
        total_events = event_info.get('total_events', 0)
        print(f"   Remaining events: {total_events}")

    print("\n✅ Cleanup completed!")

if __name__ == "__main__":
    asyncio.run(clear_test_data())
EOF
```

**Step 2**: Run the cleanup script
```bash
python clear_test_data.py
```

**Expected Output:**
```
🧹 Clearing Test Data
=========================

📊 Clearing Database...
   Found 4 error reports
   ✅ Deleted error 550e8400-e29b-41d4-a716-446655440000
   ✅ Deleted error 550e8400-e29b-41d4-a716-446655440001
   ✅ Deleted error 550e8400-e29b-41d4-a716-446655440002
   ✅ Deleted error 550e8400-e29b-41d4-a716-446655440003

📡 Clearing Events...
   ✅ All events cleared

🔍 Verifying Cleanup...
   Remaining errors: 0
   Remaining events: 0

✅ Cleanup completed!
```

**✅ Validation**: After cleanup, queries should return no error reports and event counts should be zero.

---

## 8. Troubleshooting Guide

### 8.1 Common Error Messages and Solutions

#### 8.1.1 Python/Installation Issues

**Error**: `python: command not found`
```
Solution:
1. Install Python from python.org
2. Add Python to your system PATH
3. Restart your terminal/command prompt
4. Verify with: python --version
```

**Error**: `ModuleNotFoundError: No module named 'src'`
```
Solution:
1. Ensure you're in the correct directory: cd /path/to/rag-interface
2. Activate virtual environment: source ers_env/bin/activate
3. Install dependencies: pip install -r requirements.txt
4. Check PYTHONPATH: export PYTHONPATH=$PYTHONPATH:.
```

**Error**: `pip: command not found`
```
Solution:
1. Python installation may be incomplete
2. Try: python -m pip instead of pip
3. On some systems, use pip3 instead of pip
```

#### 8.1.2 Database Connection Issues

**Error**: `psycopg2.OperationalError: could not connect to server`
```
Solution:
1. Check if PostgreSQL is running:
   - Windows: net start postgresql-x64-14
   - macOS: brew services start postgresql
   - Linux: sudo systemctl start postgresql

2. Verify connection details in .env file:
   - DB_HOST=localhost
   - DB_PORT=5432
   - DB_USERNAME=ers_user
   - DB_PASSWORD=ers_password

3. Test connection manually:
   psql -U ers_user -d error_reporting -h localhost
```

**Error**: `FATAL: database "error_reporting" does not exist`
```
Solution:
1. Connect to PostgreSQL as admin: psql -U postgres
2. Create database: CREATE DATABASE error_reporting;
3. Create user: CREATE USER ers_user WITH PASSWORD 'ers_password';
4. Grant permissions: GRANT ALL PRIVILEGES ON DATABASE error_reporting TO ers_user;
```

**Error**: `FATAL: password authentication failed for user "ers_user"`
```
Solution:
1. Reset password in PostgreSQL:
   psql -U postgres
   ALTER USER ers_user PASSWORD 'ers_password';

2. Check .env file has correct password:
   DB_PASSWORD=ers_password

3. For development, you can use in-memory database:
   DB_TYPE=in_memory
```

#### 8.1.3 Configuration Issues

**Error**: `ValueError: Unsupported database type`
```
Solution:
1. Check DB_TYPE in .env file
2. Supported values: postgresql, mongodb, sqlserver, in_memory
3. Use in_memory for testing: DB_TYPE=in_memory
```

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: '.env'`
```
Solution:
1. Create .env file in project root directory
2. Copy configuration from Section 3.1
3. Ensure file is named exactly ".env" (with dot)
```

#### 8.1.4 Test Failures

**Error**: `ImportError: attempted relative import with no known parent package`
```
Solution:
1. Run tests from project root: cd /path/to/rag-interface
2. Use module syntax: python -m pytest tests/
3. Check PYTHONPATH: export PYTHONPATH=$PYTHONPATH:.
```

**Error**: `asyncio.TimeoutError` during tests
```
Solution:
1. Database may be slow - increase timeout
2. Check database connection
3. Use in-memory database for faster tests: DB_TYPE=in_memory
```

### 8.2 Performance Issues

#### 8.2.1 Slow Response Times

**Symptoms**: Error submission takes > 1 second
```
Diagnosis Steps:
1. Run performance test: python performance_test.py
2. Check database health: python health_check.py
3. Monitor system resources (CPU, memory)

Solutions:
1. Use in-memory database for testing
2. Check PostgreSQL connection pool settings
3. Ensure database has proper indexes
4. Restart PostgreSQL service
```

#### 8.2.2 Memory Usage Issues

**Symptoms**: High memory consumption
```
Diagnosis Steps:
1. Check number of stored error reports
2. Monitor Python process memory usage
3. Check for memory leaks in long-running tests

Solutions:
1. Clear test data regularly: python clear_test_data.py
2. Use smaller test datasets
3. Restart the application periodically
```

### 8.3 Environment-Specific Issues

#### 8.3.1 Windows-Specific Issues

**Error**: `'source' is not recognized as an internal or external command`
```
Solution:
Use Windows activation syntax:
ers_env\Scripts\activate
```

**Error**: PostgreSQL service won't start
```
Solution:
1. Run Command Prompt as Administrator
2. Start service: net start postgresql-x64-14
3. Check Windows Services for PostgreSQL
```

#### 8.3.2 macOS-Specific Issues

**Error**: `psql: command not found`
```
Solution:
1. Install PostgreSQL: brew install postgresql
2. Add to PATH: echo 'export PATH="/usr/local/opt/postgresql/bin:$PATH"' >> ~/.zshrc
3. Reload shell: source ~/.zshrc
```

#### 8.3.3 Linux-Specific Issues

**Error**: Permission denied when accessing PostgreSQL
```
Solution:
1. Switch to postgres user: sudo -u postgres psql
2. Or configure peer authentication in pg_hba.conf
3. Restart PostgreSQL: sudo systemctl restart postgresql
```

### 8.4 When to Escalate to Technical Support

**Escalate immediately if:**
- ✅ You've followed all troubleshooting steps
- ✅ Error persists after trying multiple solutions
- ✅ System security is compromised
- ✅ Data corruption is suspected
- ✅ Production system is affected

**Before escalating, collect:**
1. **Error Messages**: Full error text and stack traces
2. **Environment Info**: OS, Python version, database type
3. **Configuration**: Contents of .env file (remove passwords)
4. **Steps to Reproduce**: Exact commands that cause the issue
5. **Health Check Output**: Results from python health_check.py
6. **Log Files**: Any relevant log output

**Contact Information:**
- **Technical Support**: [Insert your support contact]
- **Emergency**: [Insert emergency contact for production issues]
- **Documentation**: [Insert link to additional technical docs]

### 8.5 Quick Diagnostic Commands

**System Health Check:**
```bash
# Check all components
python health_check.py

# Check Python environment
python --version
pip list | grep -E "(asyncio|sqlalchemy|psycopg2)"

# Check database connectivity
python -c "
import asyncio
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.infrastructure.config.settings import settings
async def test():
    adapter = await DatabaseAdapterFactory.create(settings.database)
    print(f'DB Health: {await adapter.health_check()}')
asyncio.run(test())
"

# Check configuration
python -c "
from src.error_reporting_service.infrastructure.config.settings import settings
print(f'DB Type: {settings.database.type}')
print(f'Event Bus: {settings.event_bus.type}')
print(f'Debug: {settings.debug}')
"
```

**Reset to Known Good State:**
```bash
# Clear all test data
python clear_test_data.py

# Reset to in-memory mode
export DB_TYPE=in_memory
export EVENT_BUS_TYPE=in_memory

# Run basic test
python test_ers.py

# Verify health
python health_check.py
```

---

## 🎉 Congratulations!

You have successfully set up and tested the Error Reporting Service (ERS). The system is now ready to:

- ✅ Accept error reports from QA personnel
- ✅ Store error data in your chosen database
- ✅ Publish events for downstream processing
- ✅ Provide health monitoring and performance metrics
- ✅ Support multiple database and messaging adapters

**Next Steps:**
1. Integrate with your existing ASR system
2. Configure production database and messaging
3. Set up monitoring and alerting
4. Train QA personnel on error reporting procedures

**Support:**
- For technical issues, refer to the troubleshooting guide above
- For feature requests or enhancements, contact the development team
- For urgent production issues, follow your organization's escalation procedures

**Happy Error Reporting! 🚀**
