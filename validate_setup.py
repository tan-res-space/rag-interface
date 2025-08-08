#!/usr/bin/env python3
"""
ERS Setup Validation Script

This script validates that the Error Reporting Service is properly installed
and configured. Run this after following the user manual setup instructions.

Usage: python validate_setup.py
"""

import sys
import asyncio
import traceback
from datetime import datetime


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")


def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}. {description}")


def print_success(message):
    """Print a success message"""
    print(f"   ✅ {message}")


def print_error(message):
    """Print an error message"""
    print(f"   ❌ {message}")


def print_warning(message):
    """Print a warning message"""
    print(f"   ⚠️ {message}")


def print_info(message):
    """Print an info message"""
    print(f"   ℹ️ {message}")


async def validate_setup():
    """Main validation function"""
    print_header("ERS Setup Validation")
    print(f"Validation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    validation_passed = True
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    try:
        python_version = sys.version_info
        if python_version >= (3, 11):
            print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print_error(f"Python {python_version.major}.{python_version.minor} is too old. Need 3.11+")
            validation_passed = False
    except Exception as e:
        print_error(f"Failed to check Python version: {e}")
        validation_passed = False
    
    # Step 2: Check required modules
    print_step(2, "Checking Required Modules")
    required_modules = [
        'asyncio',
        'uuid', 
        'datetime',
        'dataclasses',
        'typing',
        'enum'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print_success(f"Module '{module}' available")
        except ImportError:
            print_error(f"Module '{module}' not available")
            validation_passed = False
    
    # Step 3: Check ERS modules
    print_step(3, "Checking ERS Modules")
    ers_modules = [
        'src.error_reporting_service.domain.entities.error_report',
        'src.error_reporting_service.domain.services.validation_service',
        'src.error_reporting_service.application.use_cases.submit_error_report',
        'src.error_reporting_service.infrastructure.config.settings',
        'src.error_reporting_service.infrastructure.adapters.database.factory',
        'src.error_reporting_service.infrastructure.adapters.messaging.factory'
    ]
    
    for module in ers_modules:
        try:
            __import__(module)
            print_success(f"ERS module '{module.split('.')[-1]}' available")
        except ImportError as e:
            print_error(f"ERS module '{module.split('.')[-1]}' not available: {e}")
            validation_passed = False
    
    # Step 4: Check configuration
    print_step(4, "Checking Configuration")
    try:
        from src.error_reporting_service.infrastructure.config.settings import settings
        print_success(f"App Name: {settings.app_name}")
        print_success(f"Database Type: {settings.database.type}")
        print_success(f"Event Bus Type: {settings.event_bus.type}")
        print_success(f"Debug Mode: {settings.debug}")
        print_success(f"Log Level: {settings.log_level}")
    except Exception as e:
        print_error(f"Configuration error: {e}")
        validation_passed = False
    
    # Step 5: Check database adapter
    print_step(5, "Checking Database Adapter")
    try:
        from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
        from src.error_reporting_service.infrastructure.config.settings import settings
        
        db_adapter = await DatabaseAdapterFactory.create(settings.database)
        print_success(f"Database adapter created: {type(db_adapter).__name__}")
        
        # Test health check
        health = await db_adapter.health_check()
        if health:
            print_success("Database health check passed")
        else:
            print_error("Database health check failed")
            validation_passed = False
        
        # Get connection info
        info = db_adapter.get_connection_info()
        print_success(f"Database type: {info['adapter_type']}")
        
    except Exception as e:
        print_error(f"Database adapter error: {e}")
        print_info("Try setting DB_TYPE=in_memory for testing")
        validation_passed = False
    
    # Step 6: Check event bus adapter
    print_step(6, "Checking Event Bus Adapter")
    try:
        from src.error_reporting_service.infrastructure.adapters.messaging.factory import EventBusAdapterFactory
        from src.error_reporting_service.infrastructure.config.settings import settings
        
        event_adapter = await EventBusAdapterFactory.create(settings.event_bus)
        print_success(f"Event bus adapter created: {type(event_adapter).__name__}")
        
        # Test health check
        health = await event_adapter.health_check()
        if health:
            print_success("Event bus health check passed")
        else:
            print_error("Event bus health check failed")
            validation_passed = False
        
        # Get connection info
        info = event_adapter.get_connection_info()
        print_success(f"Event bus type: {info['adapter_type']}")
        
    except Exception as e:
        print_error(f"Event bus adapter error: {e}")
        validation_passed = False
    
    # Step 7: Test basic functionality
    print_step(7, "Testing Basic Functionality")
    try:
        from uuid import uuid4
        from src.error_reporting_service.domain.services.validation_service import ErrorValidationService
        from src.error_reporting_service.domain.services.categorization_service import ErrorCategorizationService
        from src.error_reporting_service.application.use_cases.submit_error_report import SubmitErrorReportUseCase
        from src.error_reporting_service.application.dto.requests import SubmitErrorReportRequest
        
        # Create bridge classes (simplified)
        class TestRepository:
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
        
        class TestEventPublisher:
            def __init__(self, event_adapter):
                self._event_adapter = event_adapter
            async def publish_error_reported(self, event):
                await self._event_adapter.publish_event("error.reported", event)
            async def publish_error_updated(self, event):
                await self._event_adapter.publish_event("error.updated", event)
            async def publish_error_deleted(self, event):
                await self._event_adapter.publish_event("error.deleted", event)
        
        # Create components
        repository = TestRepository(db_adapter)
        event_publisher = TestEventPublisher(event_adapter)
        validation_service = ErrorValidationService()
        categorization_service = ErrorCategorizationService()
        
        use_case = SubmitErrorReportUseCase(
            repository=repository,
            event_publisher=event_publisher,
            validation_service=validation_service,
            categorization_service=categorization_service
        )
        
        # Test error submission
        request = SubmitErrorReportRequest(
            job_id=str(uuid4()),
            speaker_id=str(uuid4()),
            original_text="Test error for validation",
            corrected_text="Test correction for validation",
            error_categories=["grammar"],
            severity_level="low",
            start_position=0,
            end_position=10,
            context_notes="Validation test",
            reported_by=str(uuid4()),
            metadata={"validation": True}
        )
        
        response = await use_case.execute(request)
        
        if response.status == "success":
            print_success("Error submission test passed")
            print_success(f"Generated Error ID: {response.error_id}")
        else:
            print_error(f"Error submission test failed: {response.message}")
            validation_passed = False
        
    except Exception as e:
        print_error(f"Functionality test error: {e}")
        print_info("Check that all ERS modules are properly installed")
        validation_passed = False
    
    # Final result
    print_header("Validation Results")
    if validation_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ ERS is properly installed and configured")
        print("✅ Ready for production use")
        print("\nNext steps:")
        print("   1. Run: python test_ers.py")
        print("   2. Run: python health_check.py")
        print("   3. Submit test error reports")
        return 0
    else:
        print("❌ VALIDATION FAILED!")
        print("⚠️ Please fix the issues above before using ERS")
        print("\nTroubleshooting:")
        print("   1. Check Python version (need 3.11+)")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Set PYTHONPATH: export PYTHONPATH=$PYTHONPATH:.")
        print("   4. Use in-memory mode: export DB_TYPE=in_memory")
        print("   5. Check the user manual for detailed instructions")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(validate_setup())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation failed with unexpected error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
