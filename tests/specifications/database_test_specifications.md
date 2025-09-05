# Database Test Specifications
## Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**Version:** 2.0  
**Framework:** pytest with asyncpg for PostgreSQL testing  
**Coverage:** Schema validation, migration testing, query performance

---

## Database Test Overview

This document specifies comprehensive database tests for the enhanced schema supporting quality-based speaker bucket management with enhanced metadata fields.

---

## 1. Schema Migration Tests

### 1.1 Enhanced Metadata Schema Migration

#### Test Case: `DB-MIG-001: Enhanced Metadata Fields Migration`

**Objective:** Validate that database schema migrations for enhanced metadata fields execute correctly.

**Test Steps:**
```python
import pytest
import asyncpg
from alembic import command
from alembic.config import Config

class TestSchemaMigration:
    
    @pytest.fixture
    async def db_connection(self):
        """Setup test database connection"""
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="test_user",
            password="test_password",
            database="test_rag_interface"
        )
        yield conn
        await conn.close()
    
    async def test_enhanced_metadata_fields_migration(self, db_connection):
        """Test migration adds enhanced metadata fields to error_reports table"""
        
        # Run migration
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        
        # Verify new columns exist
        columns_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'error_reports'
        AND column_name IN (
            'number_of_speakers',
            'overlapping_speech',
            'requires_specialized_knowledge',
            'additional_notes'
        )
        ORDER BY column_name;
        """
        
        columns = await db_connection.fetch(columns_query)
        
        expected_columns = {
            'additional_notes': ('text', 'YES'),
            'number_of_speakers': ('character varying', 'YES'),
            'overlapping_speech': ('boolean', 'YES'),
            'requires_specialized_knowledge': ('boolean', 'YES')
        }
        
        for column in columns:
            column_name = column['column_name']
            assert column_name in expected_columns
            expected_type, expected_nullable = expected_columns[column_name]
            assert column['data_type'] == expected_type
            assert column['is_nullable'] == expected_nullable
    
    async def test_bucket_type_enum_migration(self, db_connection):
        """Test migration updates bucket type enum values"""
        
        # Check bucket type constraint
        constraint_query = """
        SELECT conname, consrc
        FROM pg_constraint
        WHERE conname LIKE '%bucket_type%'
        AND contype = 'c';
        """
        
        constraints = await db_connection.fetch(constraint_query)
        
        # Verify quality-based bucket types are in constraint
        bucket_constraint = next(c for c in constraints if 'bucket_type' in c['conname'])
        constraint_definition = bucket_constraint['consrc']
        
        assert 'no_touch' in constraint_definition
        assert 'low_touch' in constraint_definition
        assert 'medium_touch' in constraint_definition
        assert 'high_touch' in constraint_definition
        
        # Verify old progression-based types are not in constraint
        assert 'beginner' not in constraint_definition
        assert 'intermediate' not in constraint_definition
        assert 'advanced' not in constraint_definition
        assert 'expert' not in constraint_definition
    
    async def test_new_tables_creation(self, db_connection):
        """Test migration creates new tables for enhanced functionality"""
        
        # Check speaker_bucket_history table
        history_table_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name = 'speaker_bucket_history'
        AND table_schema = 'public';
        """
        
        history_table = await db_connection.fetchval(history_table_query)
        assert history_table == 'speaker_bucket_history'
        
        # Check verification_jobs table
        verification_table_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name = 'verification_jobs'
        AND table_schema = 'public';
        """
        
        verification_table = await db_connection.fetchval(verification_table_query)
        assert verification_table == 'verification_jobs'
        
        # Check speaker_performance_metrics table
        metrics_table_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name = 'speaker_performance_metrics'
        AND table_schema = 'public';
        """
        
        metrics_table = await db_connection.fetchval(metrics_table_query)
        assert metrics_table == 'speaker_performance_metrics'
```

### 1.2 Data Migration and Integrity Tests

#### Test Case: `DB-MIG-002: Bucket Type Data Migration`

**Test Steps:**
```python
async def test_bucket_type_data_migration(self, db_connection):
    """Test that existing bucket type data is migrated correctly"""
    
    # Insert test data with old bucket types (before migration)
    await db_connection.execute("""
        INSERT INTO error_reports (id, job_id, speaker_id, bucket_type, original_text, corrected_text)
        VALUES 
        ('test-1', 'job-1', 'speaker-1', 'beginner', 'test', 'test'),
        ('test-2', 'job-2', 'speaker-2', 'intermediate', 'test', 'test'),
        ('test-3', 'job-3', 'speaker-3', 'advanced', 'test', 'test'),
        ('test-4', 'job-4', 'speaker-4', 'expert', 'test', 'test');
    """)
    
    # Run data migration
    await db_connection.execute("""
        UPDATE error_reports 
        SET bucket_type = CASE 
            WHEN bucket_type = 'beginner' THEN 'high_touch'
            WHEN bucket_type = 'intermediate' THEN 'medium_touch'
            WHEN bucket_type = 'advanced' THEN 'low_touch'
            WHEN bucket_type = 'expert' THEN 'no_touch'
            ELSE bucket_type
        END
        WHERE bucket_type IN ('beginner', 'intermediate', 'advanced', 'expert');
    """)
    
    # Verify migration results
    migrated_data = await db_connection.fetch("""
        SELECT id, bucket_type
        FROM error_reports
        WHERE id IN ('test-1', 'test-2', 'test-3', 'test-4')
        ORDER BY id;
    """)
    
    expected_mappings = {
        'test-1': 'high_touch',
        'test-2': 'medium_touch',
        'test-3': 'low_touch',
        'test-4': 'no_touch'
    }
    
    for record in migrated_data:
        assert record['bucket_type'] == expected_mappings[record['id']]
```

---

## 2. Enhanced Metadata CRUD Tests

### 2.1 Error Reports with Enhanced Metadata

#### Test Case: `DB-CRUD-001: Insert Error Report with Enhanced Metadata`

**Test Steps:**
```python
async def test_insert_error_report_enhanced_metadata(self, db_connection):
    """Test inserting error report with all enhanced metadata fields"""
    
    # Insert error report with enhanced metadata
    insert_query = """
    INSERT INTO error_reports (
        id, job_id, speaker_id, client_id, bucket_type,
        original_text, corrected_text, error_categories,
        audio_quality, speaker_clarity, background_noise,
        number_of_speakers, overlapping_speech, requires_specialized_knowledge,
        additional_notes, reported_by, created_at
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
    )
    """
    
    test_data = (
        'test-error-001',
        'job-123',
        'speaker-456',
        'client-789',
        'medium_touch',
        'The patient has severe hypertension',
        'The patient has severe high blood pressure',
        '["medical_terminology"]',
        'good',
        'clear',
        'low',
        'one',
        False,
        True,
        'Complex medical terminology used throughout the transcript',
        'qa-user-123',
        '2024-12-19 10:00:00'
    )
    
    await db_connection.execute(insert_query, *test_data)
    
    # Verify insertion
    select_query = """
    SELECT * FROM error_reports WHERE id = $1
    """
    
    result = await db_connection.fetchrow(select_query, 'test-error-001')
    
    assert result['id'] == 'test-error-001'
    assert result['bucket_type'] == 'medium_touch'
    assert result['number_of_speakers'] == 'one'
    assert result['overlapping_speech'] is False
    assert result['requires_specialized_knowledge'] is True
    assert result['additional_notes'] == 'Complex medical terminology used throughout the transcript'
```

#### Test Case: `DB-CRUD-002: Query Error Reports with Enhanced Filters`

**Test Steps:**
```python
async def test_query_error_reports_enhanced_filters(self, db_connection):
    """Test querying error reports with enhanced metadata filters"""
    
    # Insert test data
    test_reports = [
        ('report-1', 'medium_touch', 'one', False, True, 'Medical terminology'),
        ('report-2', 'high_touch', 'two', True, False, 'Multiple speakers'),
        ('report-3', 'medium_touch', 'one', False, True, 'Specialized knowledge'),
        ('report-4', 'low_touch', 'three', False, False, 'Clear audio'),
    ]
    
    for report_id, bucket, speakers, overlap, specialized, notes in test_reports:
        await db_connection.execute("""
            INSERT INTO error_reports (
                id, job_id, speaker_id, bucket_type, original_text, corrected_text,
                number_of_speakers, overlapping_speech, requires_specialized_knowledge,
                additional_notes
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, report_id, f'job-{report_id}', f'speaker-{report_id}', bucket, 'test', 'test',
             speakers, overlap, specialized, notes)
    
    # Test complex filter query
    filter_query = """
    SELECT id, bucket_type, number_of_speakers, requires_specialized_knowledge
    FROM error_reports
    WHERE bucket_type = $1
    AND number_of_speakers = $2
    AND requires_specialized_knowledge = $3
    ORDER BY id
    """
    
    results = await db_connection.fetch(filter_query, 'medium_touch', 'one', True)
    
    assert len(results) == 2
    assert results[0]['id'] == 'report-1'
    assert results[1]['id'] == 'report-3'
    
    # Test overlapping speech filter
    overlap_query = """
    SELECT id FROM error_reports
    WHERE overlapping_speech = $1
    ORDER BY id
    """
    
    overlap_results = await db_connection.fetch(overlap_query, True)
    assert len(overlap_results) == 1
    assert overlap_results[0]['id'] == 'report-2'
```

---

## 3. Speaker History and Performance Tests

### 3.1 Speaker Bucket History Tests

#### Test Case: `DB-HIST-001: Speaker Bucket History Tracking`

**Test Steps:**
```python
async def test_speaker_bucket_history_tracking(self, db_connection):
    """Test speaker bucket history tracking functionality"""
    
    speaker_id = 'speaker-123'
    
    # Insert initial bucket assignment
    await db_connection.execute("""
        INSERT INTO speaker_bucket_history (
            id, speaker_id, bucket_type, previous_bucket, assigned_date,
            assigned_by, assignment_reason, assignment_type
        ) VALUES (
            'hist-1', $1, 'high_touch', NULL, '2024-11-01 10:00:00',
            'qa-user-456', 'Initial assessment', 'manual'
        )
    """, speaker_id)
    
    # Insert bucket transition
    await db_connection.execute("""
        INSERT INTO speaker_bucket_history (
            id, speaker_id, bucket_type, previous_bucket, assigned_date,
            assigned_by, assignment_reason, assignment_type
        ) VALUES (
            'hist-2', $1, 'medium_touch', 'high_touch', '2024-12-01 10:00:00',
            'system', 'Quality improvement observed', 'automatic'
        )
    """, speaker_id)
    
    # Query bucket history
    history_query = """
    SELECT bucket_type, previous_bucket, assigned_date, assignment_reason
    FROM speaker_bucket_history
    WHERE speaker_id = $1
    ORDER BY assigned_date
    """
    
    history = await db_connection.fetch(history_query, speaker_id)
    
    assert len(history) == 2
    assert history[0]['bucket_type'] == 'high_touch'
    assert history[0]['previous_bucket'] is None
    assert history[1]['bucket_type'] == 'medium_touch'
    assert history[1]['previous_bucket'] == 'high_touch'
```

### 3.2 Performance Metrics Calculation Tests

#### Test Case: `DB-PERF-001: Performance Metrics Calculation`

**Test Steps:**
```python
async def test_performance_metrics_calculation(self, db_connection):
    """Test performance metrics calculation and storage"""
    
    speaker_id = 'speaker-123'
    
    # Insert test error reports
    error_reports = [
        ('error-1', 'rectified', 'good', 'clear'),
        ('error-2', 'rectified', 'fair', 'clear'),
        ('error-3', 'pending', 'good', 'unclear'),
        ('error-4', 'rectified', 'poor', 'clear'),
    ]
    
    for error_id, status, audio_quality, clarity in error_reports:
        await db_connection.execute("""
            INSERT INTO error_reports (
                id, job_id, speaker_id, bucket_type, original_text, corrected_text,
                status, audio_quality, speaker_clarity
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, error_id, f'job-{error_id}', speaker_id, 'medium_touch', 'test', 'test',
             status, audio_quality, clarity)
    
    # Calculate and insert performance metrics
    await db_connection.execute("""
        INSERT INTO speaker_performance_metrics (
            id, speaker_id, current_bucket, total_errors_reported, errors_rectified,
            rectification_rate, average_audio_quality, calculated_at
        )
        SELECT 
            'metrics-' || $1,
            $1,
            'medium_touch',
            COUNT(*),
            COUNT(CASE WHEN status = 'rectified' THEN 1 END),
            COUNT(CASE WHEN status = 'rectified' THEN 1 END)::DECIMAL / COUNT(*),
            AVG(CASE WHEN audio_quality = 'good' THEN 3 WHEN audio_quality = 'fair' THEN 2 ELSE 1 END),
            NOW()
        FROM error_reports
        WHERE speaker_id = $1
    """, speaker_id)
    
    # Verify calculated metrics
    metrics_query = """
    SELECT total_errors_reported, errors_rectified, rectification_rate, average_audio_quality
    FROM speaker_performance_metrics
    WHERE speaker_id = $1
    """
    
    metrics = await db_connection.fetchrow(metrics_query, speaker_id)
    
    assert metrics['total_errors_reported'] == 4
    assert metrics['errors_rectified'] == 3
    assert metrics['rectification_rate'] == 0.75
    assert abs(metrics['average_audio_quality'] - 2.25) < 0.01  # (3+2+3+1)/4 = 2.25
```

---

## 4. Database Performance Tests

### 4.1 Query Performance with Enhanced Metadata

#### Test Case: `DB-PERF-002: Enhanced Metadata Query Performance`

**Test Steps:**
```python
import time

async def test_enhanced_metadata_query_performance(self, db_connection):
    """Test query performance with enhanced metadata filters"""
    
    # Insert large dataset for performance testing
    batch_size = 1000
    total_records = 10000
    
    for batch_start in range(0, total_records, batch_size):
        batch_data = []
        for i in range(batch_start, min(batch_start + batch_size, total_records)):
            batch_data.append((
                f'perf-test-{i}',
                f'job-{i}',
                f'speaker-{i % 100}',  # 100 unique speakers
                ['no_touch', 'low_touch', 'medium_touch', 'high_touch'][i % 4],
                'test original text',
                'test corrected text',
                ['one', 'two', 'three'][i % 3],
                i % 2 == 0,  # overlapping_speech
                i % 3 == 0,  # requires_specialized_knowledge
                f'Additional notes for record {i}'
            ))
        
        await db_connection.executemany("""
            INSERT INTO error_reports (
                id, job_id, speaker_id, bucket_type, original_text, corrected_text,
                number_of_speakers, overlapping_speech, requires_specialized_knowledge,
                additional_notes
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, batch_data)
    
    # Test complex query performance
    complex_query = """
    SELECT er.id, er.speaker_id, er.bucket_type, er.number_of_speakers
    FROM error_reports er
    WHERE er.bucket_type = $1
    AND er.requires_specialized_knowledge = $2
    AND er.number_of_speakers = $3
    AND er.created_at >= $4
    ORDER BY er.created_at DESC
    LIMIT 50
    """
    
    start_time = time.time()
    results = await db_connection.fetch(
        complex_query,
        'medium_touch',
        True,
        'one',
        '2024-01-01'
    )
    end_time = time.time()
    
    query_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Performance assertion: query should complete in <100ms
    assert query_time < 100, f"Query took {query_time}ms, exceeds 100ms limit"
    assert len(results) > 0, "Query should return results"
```

### 4.2 Index Effectiveness Tests

#### Test Case: `DB-IDX-001: Index Usage Validation`

**Test Steps:**
```python
async def test_index_usage_validation(self, db_connection):
    """Test that queries use appropriate indexes"""
    
    # Test speaker_id index usage
    explain_query = """
    EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
    SELECT * FROM error_reports
    WHERE speaker_id = $1
    """
    
    explain_result = await db_connection.fetchval(explain_query, 'speaker-123')
    execution_plan = explain_result[0]
    
    # Verify index scan is used (not sequential scan)
    plan_node = execution_plan['Plan']
    assert 'Index Scan' in plan_node['Node Type'] or 'Bitmap Index Scan' in plan_node['Node Type']
    
    # Test composite index for enhanced metadata
    composite_explain = """
    EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
    SELECT * FROM error_reports
    WHERE bucket_type = $1 AND requires_specialized_knowledge = $2
    """
    
    composite_result = await db_connection.fetchval(composite_explain, 'medium_touch', True)
    composite_plan = composite_result[0]['Plan']
    
    # Verify efficient execution (low cost)
    assert composite_plan['Total Cost'] < 1000, "Query cost too high, may need better indexing"
```

---

## 5. Data Integrity and Constraint Tests

### 5.1 Constraint Validation Tests

#### Test Case: `DB-CONST-001: Enhanced Metadata Constraints`

**Test Steps:**
```python
async def test_enhanced_metadata_constraints(self, db_connection):
    """Test constraints on enhanced metadata fields"""
    
    # Test number_of_speakers constraint
    with pytest.raises(asyncpg.CheckViolationError):
        await db_connection.execute("""
            INSERT INTO error_reports (
                id, job_id, speaker_id, bucket_type, original_text, corrected_text,
                number_of_speakers
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, 'test-invalid-speakers', 'job-123', 'speaker-456', 'medium_touch',
             'test', 'test', 'invalid_count')
    
    # Test additional_notes length constraint
    long_notes = 'A' * 1001  # Exceeds 1000 character limit
    with pytest.raises(asyncpg.DataError):
        await db_connection.execute("""
            INSERT INTO error_reports (
                id, job_id, speaker_id, bucket_type, original_text, corrected_text,
                additional_notes
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, 'test-long-notes', 'job-123', 'speaker-456', 'medium_touch',
             'test', 'test', long_notes)
    
    # Test bucket_type constraint
    with pytest.raises(asyncpg.CheckViolationError):
        await db_connection.execute("""
            INSERT INTO error_reports (
                id, job_id, speaker_id, bucket_type, original_text, corrected_text
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """, 'test-invalid-bucket', 'job-123', 'speaker-456', 'invalid_bucket',
             'test', 'test')
```

---

## 6. Database Test Configuration

### Test Environment Setup
```python
# conftest.py
import pytest
import asyncpg
import asyncio
from alembic import command
from alembic.config import Config

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_database():
    """Setup test database with schema"""
    
    # Create test database
    admin_conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    
    await admin_conn.execute("DROP DATABASE IF EXISTS test_rag_interface")
    await admin_conn.execute("CREATE DATABASE test_rag_interface")
    await admin_conn.close()
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", "postgresql://postgres:postgres@localhost/test_rag_interface")
    command.upgrade(alembic_cfg, "head")
    
    yield
    
    # Cleanup
    admin_conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    await admin_conn.execute("DROP DATABASE test_rag_interface")
    await admin_conn.close()

@pytest.fixture
async def db_connection(test_database):
    """Provide clean database connection for each test"""
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="test_rag_interface"
    )
    
    yield conn
    
    # Cleanup after each test
    await conn.execute("TRUNCATE TABLE error_reports CASCADE")
    await conn.execute("TRUNCATE TABLE speaker_bucket_history CASCADE")
    await conn.execute("TRUNCATE TABLE verification_jobs CASCADE")
    await conn.execute("TRUNCATE TABLE speaker_performance_metrics CASCADE")
    await conn.close()
```

### Test Execution
```bash
# Run all database tests
pytest tests/database/ -v

# Run specific test categories
pytest tests/database/test_schema_migration.py -v
pytest tests/database/test_enhanced_metadata_crud.py -v
pytest tests/database/test_performance.py -v

# Run with coverage
pytest tests/database/ --cov=src/database --cov-report=html
```
