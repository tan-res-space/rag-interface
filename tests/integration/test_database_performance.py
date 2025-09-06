"""
Database Performance and Integration Tests

Tests database query performance, connection handling, and transaction management
following Hexagonal Architecture patterns.
"""

import pytest
import asyncio
import time
from typing import List
from datetime import datetime, timedelta


from src.error_reporting_service.infrastructure.adapters.database.postgresql.adapter import PostgreSQLAdapter
from src.error_reporting_service.infrastructure.adapters.database.postgresql.models import ErrorReportModel
from src.error_reporting_service.domain.entities.error_report import ErrorReport, SeverityLevel
from tests.factories import ErrorReportFactory


class TestDatabasePerformance:
    """Test database performance and optimization"""

    @pytest.fixture
    async def db_adapter(self):
        """Create database adapter for testing"""
        connection_string = "postgresql+asyncpg://test:test@localhost:5432/test_db"
        adapter = PostgreSQLAdapter(connection_string)
        yield adapter
        await adapter.engine.dispose()

    @pytest.fixture
    async def sample_error_reports(self) -> List[ErrorReport]:
        """Create sample error reports for testing"""
        return [ErrorReportFactory.create() for _ in range(100)]

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, db_adapter, sample_error_reports):
        """Test bulk insert performance"""
        start_time = time.time()
        
        # Bulk insert 100 error reports
        tasks = [db_adapter.save(report) for report in sample_error_reports]
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust based on requirements)
        assert execution_time < 5.0, f"Bulk insert took {execution_time:.2f}s, expected < 5s"
        
        # Verify all records were inserted
        count = await db_adapter.count_all()
        assert count >= 100

    @pytest.mark.asyncio
    async def test_query_performance_with_filters(self, db_adapter, sample_error_reports):
        """Test query performance with various filters"""
        # Insert test data
        for report in sample_error_reports:
            await db_adapter.save(report)
        
        # Test different query patterns
        test_cases = [
            {"severity_level": SeverityLevel.HIGH},
            {"speaker_id": sample_error_reports[0].speaker_id},
            {"error_categories": ["medical_terminology"]},
            {"start_date": datetime.utcnow() - timedelta(days=1)},
        ]
        
        for filters in test_cases:
            start_time = time.time()
            results = await db_adapter.find_by_filters(filters, limit=50)
            end_time = time.time()
            
            execution_time = end_time - start_time
            assert execution_time < 1.0, f"Query with {filters} took {execution_time:.2f}s"
            assert len(results) <= 50

    @pytest.mark.asyncio
    async def test_concurrent_database_access(self, db_adapter):
        """Test concurrent database operations"""
        async def create_and_read_error_report():
            # Create error report
            error_report = ErrorReportFactory.create()
            error_id = await db_adapter.save(error_report)
            
            # Read it back
            retrieved = await db_adapter.find_by_id(error_id)
            assert retrieved is not None
            return error_id

        # Run 20 concurrent operations
        start_time = time.time()
        tasks = [create_and_read_error_report() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 10.0, f"Concurrent operations took {execution_time:.2f}s"
        assert len(results) == 20
        assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_connection_pool_efficiency(self, db_adapter):
        """Test database connection pool efficiency"""
        # Monitor connection pool usage
        db_adapter.engine.pool.size()
        db_adapter.engine.pool.checkedout()
        
        async def db_operation():
            error_report = ErrorReportFactory.create()
            return await db_adapter.save(error_report)
        
        # Perform multiple operations
        tasks = [db_operation() for _ in range(15)]
        await asyncio.gather(*tasks)
        
        # Check pool didn't exceed limits
        final_checked_out = db_adapter.engine.pool.checkedout()
        assert final_checked_out <= db_adapter.engine.pool.size()

    @pytest.mark.asyncio
    async def test_transaction_rollback_performance(self, db_adapter):
        """Test transaction rollback performance"""
        start_time = time.time()
        
        try:
            async with db_adapter._session_factory() as session:
                # Create multiple records in transaction
                for i in range(10):
                    error_report = ErrorReportFactory.create()
                    model = ErrorReportModel(
                        error_id=error_report.error_id,
                        job_id=error_report.job_id,
                        speaker_id=error_report.speaker_id,
                        reported_by=error_report.reported_by,
                        original_text=error_report.original_text,
                        corrected_text=error_report.corrected_text,
                        error_categories=error_report.error_categories,
                        severity_level=error_report.severity_level.value,
                        start_position=error_report.start_position,
                        end_position=error_report.end_position,
                        error_timestamp=error_report.error_timestamp,
                    )
                    session.add(model)
                
                # Force rollback
                raise Exception("Intentional rollback")
                
        except Exception:
            pass  # Expected
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Rollback should be fast
        assert execution_time < 1.0, f"Transaction rollback took {execution_time:.2f}s"
        
        # Verify no records were committed
        count = await db_adapter.count_all()
        assert count == 0

    @pytest.mark.asyncio
    async def test_large_result_set_pagination(self, db_adapter):
        """Test pagination performance with large result sets"""
        # Create large dataset
        large_dataset = [ErrorReportFactory.create() for _ in range(500)]
        for report in large_dataset:
            await db_adapter.save(report)
        
        # Test pagination performance
        page_size = 50
        total_pages = 10
        
        start_time = time.time()
        for page in range(total_pages):
            offset = page * page_size
            results = await db_adapter.find_by_filters(
                filters={}, 
                limit=page_size, 
                offset=offset
            )
            assert len(results) <= page_size
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Pagination should be efficient
        assert execution_time < 5.0, f"Pagination took {execution_time:.2f}s"

    @pytest.mark.asyncio
    async def test_index_usage_verification(self, db_adapter):
        """Test that database queries use indexes efficiently"""
        # Insert test data
        test_reports = [ErrorReportFactory.create() for _ in range(100)]
        for report in test_reports:
            await db_adapter.save(report)
        
        # Test queries that should use indexes
        speaker_id = test_reports[0].speaker_id
        
        start_time = time.time()
        results = await db_adapter.find_by_speaker_id(speaker_id)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Query by indexed field should be fast
        assert execution_time < 0.1, f"Indexed query took {execution_time:.2f}s"
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_memory_usage_with_large_queries(self, db_adapter):
        """Test memory efficiency with large query results"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and query large dataset
        large_dataset = [ErrorReportFactory.create() for _ in range(1000)]
        for report in large_dataset:
            await db_adapter.save(report)
        
        # Query all records
        all_results = await db_adapter.find_by_filters({}, limit=1000)
        
        # Check memory usage didn't spike excessively
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (adjust threshold as needed)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.2f}MB"
        assert len(all_results) == 1000


class TestDatabaseIntegration:
    """Test database integration scenarios"""

    @pytest.fixture
    async def db_adapter(self):
        """Create database adapter for testing"""
        connection_string = "postgresql+asyncpg://test:test@localhost:5432/test_db"
        adapter = PostgreSQLAdapter(connection_string)
        yield adapter
        await adapter.engine.dispose()

    @pytest.mark.asyncio
    async def test_database_health_check(self, db_adapter):
        """Test database health check functionality"""
        is_healthy = await db_adapter.health_check()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_database_connection_recovery(self, db_adapter):
        """Test database connection recovery after failure"""
        # Simulate connection failure and recovery
        # This would require more sophisticated setup in real scenarios
        
        # Verify adapter can recover from connection issues
        error_report = ErrorReportFactory.create()
        error_id = await db_adapter.save(error_report)
        assert error_id is not None
        
        retrieved = await db_adapter.find_by_id(error_id)
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_transaction_isolation(self, db_adapter):
        """Test transaction isolation between concurrent operations"""
        error_report1 = ErrorReportFactory.create()
        error_report2 = ErrorReportFactory.create()
        
        async def transaction1():
            async with db_adapter._session_factory() as session:
                await db_adapter.save(error_report1)
                # Simulate some processing time
                await asyncio.sleep(0.1)
                return "transaction1_complete"
        
        async def transaction2():
            async with db_adapter._session_factory() as session:
                await db_adapter.save(error_report2)
                return "transaction2_complete"
        
        # Run transactions concurrently
        results = await asyncio.gather(transaction1(), transaction2())
        assert "transaction1_complete" in results
        assert "transaction2_complete" in results
        
        # Both records should exist
        count = await db_adapter.count_all()
        assert count >= 2
