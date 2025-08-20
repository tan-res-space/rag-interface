-- =====================================================
-- RAG Integration Service - PostgreSQL Schema
-- =====================================================
-- This script creates the schema for RAG Integration Service metadata and caching
-- Note: Vector embeddings are stored in external vector databases (Pinecone, Weaviate, etc.)
-- Run this script on the rag_integration_db database as ris_user
-- 
-- Author: RAG Interface Deployment Team
-- Version: 1.0
-- Date: 2025-01-20
-- =====================================================

\c rag_integration_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- EMBEDDING METADATA TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS embedding_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_hash VARCHAR(64) NOT NULL UNIQUE,
    original_text TEXT NOT NULL,
    embedding_type VARCHAR(50) NOT NULL DEFAULT 'text-embedding-ada-002',
    vector_id VARCHAR(255), -- ID in external vector database
    vector_db_type VARCHAR(50) NOT NULL DEFAULT 'pinecone',
    dimensions INTEGER NOT NULL DEFAULT 1536,
    magnitude DECIMAL(10,6),
    speaker_id UUID,
    job_id UUID,
    error_categories JSONB DEFAULT '[]',
    asr_engine VARCHAR(100),
    note_type VARCHAR(100),
    similarity_score DECIMAL(5,4),
    wer_score DECIMAL(5,4),
    ser_score DECIMAL(5,4),
    insert_percent DECIMAL(5,2),
    delete_percent DECIMAL(5,2),
    move_percent DECIMAL(5,2),
    edit_percent DECIMAL(5,2),
    source_document_id UUID,
    error_type_classification VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for embedding_metadata
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_text_hash ON embedding_metadata(text_hash);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_embedding_type ON embedding_metadata(embedding_type);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_vector_id ON embedding_metadata(vector_id);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_speaker_id ON embedding_metadata(speaker_id);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_job_id ON embedding_metadata(job_id);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_asr_engine ON embedding_metadata(asr_engine);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_note_type ON embedding_metadata(note_type);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_source_document_id ON embedding_metadata(source_document_id);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_error_type_classification ON embedding_metadata(error_type_classification);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_created_at ON embedding_metadata(created_at);

-- =====================================================
-- SIMILARITY SEARCH CACHE TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS similarity_search_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) NOT NULL UNIQUE,
    query_text TEXT NOT NULL,
    search_parameters JSONB NOT NULL DEFAULT '{}',
    results JSONB NOT NULL DEFAULT '[]',
    result_count INTEGER NOT NULL DEFAULT 0,
    search_time_ms INTEGER NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for similarity_search_cache
CREATE INDEX IF NOT EXISTS idx_similarity_search_cache_query_hash ON similarity_search_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_similarity_search_cache_expires_at ON similarity_search_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_similarity_search_cache_created_at ON similarity_search_cache(created_at);

-- =====================================================
-- PATTERN ANALYSIS RESULTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS pattern_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_type VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL DEFAULT '{}',
    patterns_found JSONB NOT NULL DEFAULT '[]',
    pattern_count INTEGER NOT NULL DEFAULT 0,
    confidence_scores JSONB DEFAULT '{}',
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for pattern_analysis_results
CREATE INDEX IF NOT EXISTS idx_pattern_analysis_results_analysis_type ON pattern_analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_pattern_analysis_results_pattern_count ON pattern_analysis_results(pattern_count);
CREATE INDEX IF NOT EXISTS idx_pattern_analysis_results_created_at ON pattern_analysis_results(created_at);

-- =====================================================
-- VECTOR DATABASE SYNC STATUS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS vector_db_sync_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vector_db_type VARCHAR(50) NOT NULL,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (sync_status IN ('pending', 'in_progress', 'completed', 'failed')),
    total_vectors INTEGER DEFAULT 0,
    synced_vectors INTEGER DEFAULT 0,
    failed_vectors INTEGER DEFAULT 0,
    error_details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for vector_db_sync_status
CREATE INDEX IF NOT EXISTS idx_vector_db_sync_status_vector_db_type ON vector_db_sync_status(vector_db_type);
CREATE INDEX IF NOT EXISTS idx_vector_db_sync_status_sync_status ON vector_db_sync_status(sync_status);
CREATE INDEX IF NOT EXISTS idx_vector_db_sync_status_last_sync_at ON vector_db_sync_status(last_sync_at);

-- =====================================================
-- ML MODEL PERFORMANCE TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS ml_model_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    operation_type VARCHAR(50) NOT NULL,
    input_size INTEGER,
    processing_time_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for ml_model_performance
CREATE INDEX IF NOT EXISTS idx_ml_model_performance_model_name ON ml_model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_ml_model_performance_operation_type ON ml_model_performance(operation_type);
CREATE INDEX IF NOT EXISTS idx_ml_model_performance_success ON ml_model_performance(success);
CREATE INDEX IF NOT EXISTS idx_ml_model_performance_created_at ON ml_model_performance(created_at);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_embedding_metadata_updated_at 
    BEFORE UPDATE ON embedding_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vector_db_sync_status_updated_at 
    BEFORE UPDATE ON vector_db_sync_status 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to generate text hash for deduplication
CREATE OR REPLACE FUNCTION generate_text_hash(input_text TEXT)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(input_text, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM similarity_search_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get embedding statistics
CREATE OR REPLACE FUNCTION get_embedding_stats()
RETURNS TABLE(
    total_embeddings BIGINT,
    unique_speakers BIGINT,
    unique_jobs BIGINT,
    avg_similarity_score DECIMAL(5,4),
    most_common_asr_engine TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_embeddings,
        COUNT(DISTINCT speaker_id) as unique_speakers,
        COUNT(DISTINCT job_id) as unique_jobs,
        AVG(similarity_score) as avg_similarity_score,
        (SELECT asr_engine FROM embedding_metadata 
         WHERE asr_engine IS NOT NULL 
         GROUP BY asr_engine 
         ORDER BY COUNT(*) DESC 
         LIMIT 1) as most_common_asr_engine
    FROM embedding_metadata;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE embedding_metadata IS 'Metadata for vector embeddings stored in external vector databases';
COMMENT ON TABLE similarity_search_cache IS 'Cache for similarity search results to improve performance';
COMMENT ON TABLE pattern_analysis_results IS 'Results from pattern analysis operations';
COMMENT ON TABLE vector_db_sync_status IS 'Synchronization status with external vector databases';
COMMENT ON TABLE ml_model_performance IS 'Performance metrics for ML model operations';

COMMENT ON COLUMN embedding_metadata.text_hash IS 'SHA256 hash of the original text for deduplication';
COMMENT ON COLUMN embedding_metadata.vector_id IS 'ID of the vector in the external vector database';
COMMENT ON COLUMN embedding_metadata.vector_db_type IS 'Type of vector database (pinecone, weaviate, qdrant)';
COMMENT ON COLUMN embedding_metadata.dimensions IS 'Number of dimensions in the vector embedding';

COMMENT ON FUNCTION generate_text_hash(TEXT) IS 'Generates SHA256 hash for text deduplication';
COMMENT ON FUNCTION cleanup_expired_cache() IS 'Removes expired entries from similarity search cache';
COMMENT ON FUNCTION get_embedding_stats() IS 'Returns statistics about stored embeddings';

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'RAG Integration Service Schema Created Successfully';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - embedding_metadata (with 10 indexes)';
    RAISE NOTICE '  - similarity_search_cache (with 3 indexes)';
    RAISE NOTICE '  - pattern_analysis_results (with 3 indexes)';
    RAISE NOTICE '  - vector_db_sync_status (with 3 indexes)';
    RAISE NOTICE '  - ml_model_performance (with 4 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - generate_text_hash()';
    RAISE NOTICE '  - cleanup_expired_cache()';
    RAISE NOTICE '  - get_embedding_stats()';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created:';
    RAISE NOTICE '  - update_embedding_metadata_updated_at';
    RAISE NOTICE '  - update_vector_db_sync_status_updated_at';
    RAISE NOTICE '=================================================';
END
$$;
