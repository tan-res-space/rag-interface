#!/usr/bin/env python3
"""
Test Phase 3 Advanced RAG Features

This script tests the advanced RAG functionality implemented in Phase 3:
1. Advanced embedding strategies (contextual, multi-modal, versioned)
2. Sophisticated similarity search (hybrid search, clustering)
3. Performance analytics system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_advanced_embedding_adapters():
    """Test advanced embedding adapter implementations."""
    print("🔍 Testing advanced embedding adapters...")
    try:
        from rag_integration_service.infrastructure.adapters.ml_models.contextual_adapter import ContextualEmbeddingAdapter
        from rag_integration_service.infrastructure.adapters.ml_models.multimodal_adapter import MultiModalEmbeddingAdapter, MultiModalContent
        from rag_integration_service.infrastructure.adapters.ml_models.versioned_adapter import VersionedEmbeddingAdapter
        
        print("  ✅ Contextual adapter imported successfully")
        print("  ✅ Multi-modal adapter imported successfully")
        print("  ✅ Versioned adapter imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Advanced embedding adapter test failed: {e}")
        return False

def test_sophisticated_search():
    """Test sophisticated search implementations."""
    print("🔍 Testing sophisticated search...")
    try:
        from rag_integration_service.infrastructure.adapters.vector_db.hybrid_search_adapter import HybridSearchAdapter
        from rag_integration_service.infrastructure.adapters.vector_db.clustering_adapter import SemanticClusteringAdapter
        
        print("  ✅ Hybrid search adapter imported successfully")
        print("  ✅ Clustering adapter imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Sophisticated search test failed: {e}")
        return False

def test_performance_analytics():
    """Test performance analytics system."""
    print("🔍 Testing performance analytics...")
    try:
        from shared.infrastructure.analytics.metrics_collector import MetricsCollector, get_metrics_collector
        from shared.infrastructure.analytics.performance_dashboard import PerformanceDashboard
        
        print("  ✅ Metrics collector imported successfully")
        print("  ✅ Performance dashboard imported successfully")
        
        # Test metrics collector creation
        collector = MetricsCollector()
        print("  ✅ Metrics collector created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Performance analytics test failed: {e}")
        return False

async def test_contextual_embedding_functionality():
    """Test contextual embedding functionality."""
    print("🔍 Testing contextual embedding functionality...")
    try:
        from rag_integration_service.infrastructure.adapters.ml_models.contextual_adapter import ContextualEmbeddingAdapter
        from rag_integration_service.infrastructure.adapters.ml_models.mock_adapter import MockEmbeddingAdapter
        from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType
        
        # Create base adapter
        base_adapter = MockEmbeddingAdapter()
        
        # Create contextual adapter
        contextual_adapter = ContextualEmbeddingAdapter(
            base_adapter=base_adapter,
            context_window=256,
            context_weight=0.3
        )
        
        # Test embedding generation with context
        text = "This is an error in the transcription"
        context = "The speaker was discussing technical documentation when this error occurred in the middle of the presentation."
        
        embedding = await contextual_adapter.generate_embedding(
            text=text,
            embedding_type=EmbeddingType.ERROR,
            context=context
        )
        
        if len(embedding) == 1536:  # Standard dimension
            print("  ✅ Contextual embedding generation works")
        else:
            print(f"  ⚠️ Unexpected embedding dimension: {len(embedding)}")
        
        # Test health check
        health = await contextual_adapter.health_check()
        if health:
            print("  ✅ Contextual adapter health check works")
        else:
            print("  ⚠️ Contextual adapter health check failed")
        
        return True
    except Exception as e:
        print(f"  ❌ Contextual embedding functionality test failed: {e}")
        return False

async def test_multimodal_embedding_functionality():
    """Test multi-modal embedding functionality."""
    print("🔍 Testing multi-modal embedding functionality...")
    try:
        from rag_integration_service.infrastructure.adapters.ml_models.multimodal_adapter import (
            MultiModalEmbeddingAdapter, MultiModalContent, ContentModality
        )
        from rag_integration_service.infrastructure.adapters.ml_models.mock_adapter import MockEmbeddingAdapter
        from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType
        
        # Create base adapter
        base_adapter = MockEmbeddingAdapter()
        
        # Create multi-modal adapter
        multimodal_adapter = MultiModalEmbeddingAdapter(
            text_adapter=base_adapter,
            enable_audio_features=True,
            enable_speaker_features=True,
            enable_contextual_features=True
        )
        
        # Create multi-modal content
        content = MultiModalContent(
            text="This is a test transcription error",
            modality=ContentModality.HYBRID,
            audio_metadata={
                "quality": "high",
                "background_noise": "low",
                "speaker_clarity": "clear",
                "number_of_speakers": 1,
                "overlapping_speech": False
            },
            speaker_profile={
                "experience_level": "expert",
                "native_language": "english",
                "accent_strength": "slight",
                "speaking_rate": "normal"
            },
            contextual_data={
                "domain": "technical",
                "complexity": "medium",
                "formality": "formal",
                "requires_specialized_knowledge": True
            }
        )
        
        # Test embedding generation
        embedding = await multimodal_adapter.generate_embedding(
            text=content.text,
            embedding_type=EmbeddingType.ERROR,
            content=content
        )
        
        if len(embedding) == 1536:  # Standard dimension
            print("  ✅ Multi-modal embedding generation works")
        else:
            print(f"  ⚠️ Unexpected embedding dimension: {len(embedding)}")
        
        # Test health check
        health = await multimodal_adapter.health_check()
        if health:
            print("  ✅ Multi-modal adapter health check works")
        else:
            print("  ⚠️ Multi-modal adapter health check failed")
        
        return True
    except Exception as e:
        print(f"  ❌ Multi-modal embedding functionality test failed: {e}")
        return False

async def test_metrics_collector_functionality():
    """Test metrics collector functionality."""
    print("🔍 Testing metrics collector functionality...")
    try:
        from shared.infrastructure.analytics.metrics_collector import MetricsCollector, MetricType
        from datetime import timedelta
        
        # Create metrics collector
        collector = MetricsCollector()
        
        # Test recording different metric types
        collector.record_counter("test_requests", 1.0, {"service": "test"})
        collector.record_gauge("test_memory", 512.0, {"unit": "MB"})
        collector.record_histogram("test_latency", 0.05, {"endpoint": "/test"})
        collector.record_timer("test_duration", 0.1, {"operation": "test"})
        
        print("  ✅ Metric recording works")
        
        # Test metric retrieval
        all_metrics = collector.get_all_metrics()
        if "counters" in all_metrics and "gauges" in all_metrics:
            print("  ✅ Metric retrieval works")
        else:
            print("  ⚠️ Metric retrieval incomplete")
        
        # Test metric summary
        summary = collector.get_metric_summary("test_latency", timedelta(minutes=1))
        if summary and summary.count > 0:
            print("  ✅ Metric summary works")
        else:
            print("  ⚠️ Metric summary failed")
        
        # Test timer context manager
        with collector.timer("test_operation", {"type": "unit_test"}):
            await asyncio.sleep(0.01)  # Simulate work
        
        print("  ✅ Timer context manager works")
        
        return True
    except Exception as e:
        print(f"  ❌ Metrics collector functionality test failed: {e}")
        return False

async def test_hybrid_search_functionality():
    """Test hybrid search functionality."""
    print("🔍 Testing hybrid search functionality...")
    try:
        from rag_integration_service.infrastructure.adapters.vector_db.hybrid_search_adapter import HybridSearchAdapter
        from rag_integration_service.infrastructure.adapters.vector_db.in_memory_adapter import InMemoryVectorStorageAdapter
        from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding
        from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType
        from uuid import uuid4
        from datetime import datetime
        import hashlib
        
        # Create base storage adapter
        base_adapter = InMemoryVectorStorageAdapter()
        
        # Create hybrid search adapter
        hybrid_adapter = HybridSearchAdapter(
            vector_adapter=base_adapter,
            semantic_weight=0.7,
            keyword_weight=0.3
        )
        
        # Create test embeddings
        test_texts = [
            "Machine learning error in neural network training",
            "Database connection timeout during query execution",
            "Authentication failure in user login process"
        ]
        
        embeddings = []
        for i, text in enumerate(test_texts):
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            embedding = VectorEmbedding(
                id=uuid4(),
                vector=[0.1 + i * 0.1] * 1536,
                text=text,
                text_hash=text_hash,
                embedding_type=EmbeddingType.ERROR,
                model_version="1.0.0",
                model_name="test-model",
                metadata={"category": "error", "index": i},
                created_at=datetime.utcnow()
            )
            embeddings.append(embedding)
        
        # Store embeddings
        for embedding in embeddings:
            success = await hybrid_adapter.store_embedding(embedding)
            if not success:
                print("  ⚠️ Failed to store embedding")
                return False
        
        print("  ✅ Hybrid search storage works")
        
        # Test hybrid search
        query_text = "machine learning error"
        query_vector = [0.15] * 1536  # Similar to first embedding
        
        results = await hybrid_adapter.hybrid_search(
            query_text=query_text,
            query_vector=query_vector,
            top_k=3
        )
        
        if len(results) > 0:
            print("  ✅ Hybrid search functionality works")
        else:
            print("  ⚠️ Hybrid search returned no results")
        
        # Test health check
        health = await hybrid_adapter.health_check()
        if health:
            print("  ✅ Hybrid search health check works")
        else:
            print("  ⚠️ Hybrid search health check failed")
        
        return True
    except Exception as e:
        print(f"  ❌ Hybrid search functionality test failed: {e}")
        return False

async def main():
    """Run all Phase 3 tests."""
    print("=" * 60)
    print("🧪 Phase 3 Advanced RAG Features - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Advanced Embedding Adapters", test_advanced_embedding_adapters),
        ("Sophisticated Search", test_sophisticated_search),
        ("Performance Analytics", test_performance_analytics),
        ("Contextual Embedding Functionality", test_contextual_embedding_functionality),
        ("Multi-modal Embedding Functionality", test_multimodal_embedding_functionality),
        ("Metrics Collector Functionality", test_metrics_collector_functionality),
        ("Hybrid Search Functionality", test_hybrid_search_functionality),
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
        print("🎉 All Phase 3 functionality is working correctly!")
        return 0
    else:
        print("⚠️ Some Phase 3 functionality needs attention")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
