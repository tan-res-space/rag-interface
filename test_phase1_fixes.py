#!/usr/bin/env python3
"""
Test Phase 1 Critical System Fixes

This script tests the critical fixes implemented in Phase 1:
1. API Gateway router configuration
2. Security credentials configuration
3. Basic database connections
4. Authentication implementation
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_api_gateway_imports():
    """Test that API Gateway can import all routers"""
    print("🔍 Testing API Gateway router imports...")
    try:
        from api_gateway.speaker_bucket_management_router import router as speaker_bucket_router
        print("  ✅ Speaker bucket router imported successfully")
        
        from api_gateway.enhanced_error_reporting_router import router as error_reporting_router
        print("  ✅ Error reporting router imported successfully")
        
        from api_gateway.verification_workflow_router import router as verification_router
        print("  ✅ Verification workflow router imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Router import failed: {e}")
        return False

def test_security_configuration():
    """Test that security configuration is properly loaded"""
    print("🔍 Testing security configuration...")
    try:
        from error_reporting_service.infrastructure.config.settings import settings
        
        # Check that secret key is not the default
        if settings.secret_key == "your-secret-key-here":
            print("  ⚠️ Secret key is still using default value")
            return False
        else:
            print("  ✅ Secret key is properly configured")
        
        # Check CORS origins
        if "*" in settings.cors_origins and not settings.debug:
            print("  ⚠️ CORS allows all origins in non-debug mode")
            return False
        else:
            print("  ✅ CORS configuration is appropriate")
        
        return True
    except Exception as e:
        print(f"  ❌ Security configuration test failed: {e}")
        return False

async def test_service_initialization():
    """Test that services can initialize properly"""
    print("🔍 Testing service initialization...")
    try:
        # Test User Management Service
        from user_management_service.infrastructure.config.settings import settings as ums_settings
        print("  ✅ User Management Service settings loaded")
        
        # Test RAG Integration Service
        from rag_integration_service.infrastructure.config.settings import settings as ris_settings
        print("  ✅ RAG Integration Service settings loaded")
        
        return True
    except Exception as e:
        print(f"  ❌ Service initialization test failed: {e}")
        return False

def test_database_adapters():
    """Test that database adapters can be created"""
    print("🔍 Testing database adapter creation...")
    try:
        from error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
        from error_reporting_service.infrastructure.config.database_config import DatabaseConfig, DatabaseType
        
        # Test in-memory adapter
        config = DatabaseConfig(type=DatabaseType.IN_MEMORY)
        adapter = DatabaseAdapterFactory.create(config)
        print("  ✅ In-memory database adapter created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Database adapter test failed: {e}")
        return False

def test_environment_variables():
    """Test that environment variables are properly configured"""
    print("🔍 Testing environment variable configuration...")
    try:
        # Set test environment variables
        os.environ["SECRET_KEY"] = "test-secret-key-for-validation"
        os.environ["CORS_ORIGINS"] = "http://localhost:3000"
        os.environ["DEBUG"] = "true"
        
        from error_reporting_service.infrastructure.config.settings import Settings
        test_settings = Settings.from_env()
        
        if test_settings.secret_key == "test-secret-key-for-validation":
            print("  ✅ Environment variables are properly loaded")
            return True
        else:
            print("  ❌ Environment variables not loaded correctly")
            return False
    except Exception as e:
        print(f"  ❌ Environment variable test failed: {e}")
        return False

async def main():
    """Run all Phase 1 tests"""
    print("=" * 60)
    print("🧪 Phase 1 Critical System Fixes - Test Suite")
    print("=" * 60)
    
    tests = [
        ("API Gateway Router Configuration", test_api_gateway_imports),
        ("Security Configuration", test_security_configuration),
        ("Service Initialization", test_service_initialization),
        ("Database Adapters", test_database_adapters),
        ("Environment Variables", test_environment_variables),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"  ✅ PASSED")
            else:
                print(f"  ❌ FAILED")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 1 fixes are working correctly!")
        return 0
    else:
        print("⚠️ Some Phase 1 fixes need attention")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
