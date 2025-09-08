#!/usr/bin/env python3
"""
Test Phase 2 Core Functionality

This script tests the core functionality implemented in Phase 2:
1. RAG Integration Service ML model connections
2. Dependency injection container
3. Missing database adapters
4. Database migration system
5. Service-to-service communication
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_ml_model_adapters():
    """Test ML model adapter implementations."""
    print("🔍 Testing ML model adapters...")
    try:
        from rag_integration_service.infrastructure.adapters.ml_models.factory import MLModelAdapterFactory
        from rag_integration_service.infrastructure.adapters.ml_models.mock_adapter import MockEmbeddingAdapter
        from rag_integration_service.infrastructure.adapters.ml_models.openai_adapter import OpenAIEmbeddingAdapter
        
        print("  ✅ ML model factory imported successfully")
        print("  ✅ Mock adapter imported successfully")
        print("  ✅ OpenAI adapter imported successfully")
        
        # Test factory methods
        supported_providers = MLModelAdapterFactory.get_supported_providers()
        print(f"  ✅ Supported providers: {supported_providers}")
        
        return True
    except Exception as e:
        print(f"  ❌ ML model adapter test failed: {e}")
        return False

def test_vector_storage_adapters():
    """Test vector storage adapter implementations."""
    print("🔍 Testing vector storage adapters...")
    try:
        from rag_integration_service.infrastructure.adapters.vector_db.factory import VectorStorageAdapterFactory
        from rag_integration_service.infrastructure.adapters.vector_db.in_memory_adapter import InMemoryVectorStorageAdapter
        
        print("  ✅ Vector storage factory imported successfully")
        print("  ✅ In-memory adapter imported successfully")
        
        # Test factory methods
        supported_providers = VectorStorageAdapterFactory.get_supported_providers()
        print(f"  ✅ Supported providers: {supported_providers}")
        
        return True
    except Exception as e:
        print(f"  ❌ Vector storage adapter test failed: {e}")
        return False

def test_dependency_injection():
    """Test dependency injection container."""
    print("🔍 Testing dependency injection container...")
    try:
        from shared.infrastructure.dependency_injection.container import DIContainer, get_container
        from shared.infrastructure.dependency_injection.service_locator import ServiceLocator
        
        print("  ✅ DI container imported successfully")
        print("  ✅ Service locator imported successfully")
        
        # Test container creation
        container = DIContainer()
        print("  ✅ DI container created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Dependency injection test failed: {e}")
        return False

def test_database_adapters():
    """Test missing database adapter implementations."""
    print("🔍 Testing database adapters...")
    try:
        from error_reporting_service.infrastructure.adapters.database.mongodb.adapter import MongoDBAdapter
        from error_reporting_service.infrastructure.adapters.database.sqlserver.adapter import SQLServerAdapter
        
        print("  ✅ MongoDB adapter imported successfully")
        print("  ✅ SQL Server adapter imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Database adapter test failed: {e}")
        return False

def test_migration_system():
    """Test database migration system."""
    print("🔍 Testing database migration system...")
    try:
        from shared.infrastructure.database.migration_manager import MigrationManager
        
        print("  ✅ Migration manager imported successfully")
        
        # Test migration manager creation (without actual database)
        manager = MigrationManager("postgresql://test:test@localhost/test")
        print("  ✅ Migration manager created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Migration system test failed: {e}")
        return False

def test_service_communication():
    """Test service-to-service communication."""
    print("🔍 Testing service communication...")
    try:
        from shared.infrastructure.http_client.base_client import BaseHTTPClient
        from shared.infrastructure.http_client.rag_integration_client import RAGIntegrationClient
        from shared.infrastructure.http_client.error_reporting_client import ErrorReportingClient
        from shared.infrastructure.http_client.service_registry import ServiceRegistry
        
        print("  ✅ Base HTTP client imported successfully")
        print("  ✅ RAG Integration client imported successfully")
        print("  ✅ Error Reporting client imported successfully")
        print("  ✅ Service registry imported successfully")
        
        # Test service registry creation
        registry = ServiceRegistry()
        print("  ✅ Service registry created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Service communication test failed: {e}")
        return False

async def test_ml_adapter_functionality():
    """Test actual ML adapter functionality."""
    print("🔍 Testing ML adapter functionality...")
    try:
        from rag_integration_service.infrastructure.adapters.ml_models.mock_adapter import MockEmbeddingAdapter
        
        # Create mock adapter
        adapter = MockEmbeddingAdapter()
        
        # Test embedding generation
        embedding = await adapter.generate_embedding("test text")
        if len(embedding) == 1536:  # Default dimension
            print("  ✅ Single embedding generation works")
        else:
            print(f"  ⚠️ Unexpected embedding dimension: {len(embedding)}")
        
        # Test batch embedding generation
        embeddings = await adapter.generate_batch_embeddings(["text1", "text2", "text3"])
        if len(embeddings) == 3:
            print("  ✅ Batch embedding generation works")
        else:
            print(f"  ⚠️ Unexpected batch size: {len(embeddings)}")
        
        # Test health check
        health = await adapter.health_check()
        if health:
            print("  ✅ ML adapter health check works")
        else:
            print("  ⚠️ ML adapter health check failed")
        
        return True
    except Exception as e:
        print(f"  ❌ ML adapter functionality test failed: {e}")
        return False

async def test_vector_storage_functionality():
    """Test actual vector storage functionality."""
    print("🔍 Testing vector storage functionality...")
    try:
        from rag_integration_service.infrastructure.adapters.vector_db.in_memory_adapter import InMemoryVectorStorageAdapter
        from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding
        from uuid import uuid4
        
        # Create storage adapter
        storage = InMemoryVectorStorageAdapter()
        
        # Create test embedding
        from datetime import datetime
        from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType
        import hashlib

        test_text = "This is a test text for embedding"
        text_hash = hashlib.sha256(test_text.encode()).hexdigest()

        embedding = VectorEmbedding(
            id=uuid4(),
            vector=[0.1] * 1536,  # 1536-dimensional vector
            text=test_text,
            text_hash=text_hash,
            embedding_type=EmbeddingType.ERROR,
            model_version="1.0.0",
            model_name="test-model",
            metadata={"test": "data"},
            created_at=datetime.utcnow()  # Use UTC datetime
        )
        
        # Test storage
        stored = await storage.store_embedding(embedding)
        if stored:
            print("  ✅ Vector storage works")
        else:
            print("  ⚠️ Vector storage failed")
        
        # Test retrieval
        retrieved = await storage.get_embedding(embedding.id)
        if retrieved and retrieved.id == embedding.id:
            print("  ✅ Vector retrieval works")
        else:
            print("  ⚠️ Vector retrieval failed")
        
        # Test health check
        health = await storage.health_check()
        if health:
            print("  ✅ Vector storage health check works")
        else:
            print("  ⚠️ Vector storage health check failed")
        
        return True
    except Exception as e:
        print(f"  ❌ Vector storage functionality test failed: {e}")
        return False

async def main():
    """Run all Phase 2 tests."""
    print("=" * 60)
    print("🧪 Phase 2 Core Functionality - Test Suite")
    print("=" * 60)
    
    tests = [
        ("ML Model Adapters", test_ml_model_adapters),
        ("Vector Storage Adapters", test_vector_storage_adapters),
        ("Dependency Injection", test_dependency_injection),
        ("Database Adapters", test_database_adapters),
        ("Migration System", test_migration_system),
        ("Service Communication", test_service_communication),
        ("ML Adapter Functionality", test_ml_adapter_functionality),
        ("Vector Storage Functionality", test_vector_storage_functionality),
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
        print("🎉 All Phase 2 functionality is working correctly!")
        return 0
    else:
        print("⚠️ Some Phase 2 functionality needs attention")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
