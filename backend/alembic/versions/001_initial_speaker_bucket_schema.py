"""Initial speaker bucket management schema

Revision ID: 001_speaker_bucket_init
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_speaker_bucket_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial speaker bucket management schema."""
    
    # Create enum types
    op.execute("CREATE TYPE speaker_bucket AS ENUM ('NO_TOUCH', 'LOW_TOUCH', 'MEDIUM_TOUCH', 'HIGH_TOUCH')")
    op.execute("CREATE TYPE quality_trend AS ENUM ('IMPROVING', 'STABLE', 'DECLINING')")
    op.execute("CREATE TYPE session_status AS ENUM ('active', 'paused', 'completed', 'cancelled')")
    op.execute("CREATE TYPE improvement_assessment AS ENUM ('SIGNIFICANT', 'MODERATE', 'MINIMAL', 'NONE', 'NEGATIVE')")
    op.execute("CREATE TYPE job_status AS ENUM ('queued', 'running', 'completed', 'failed', 'cancelled')")
    op.execute("CREATE TYPE transition_status AS ENUM ('pending', 'approved', 'rejected')")
    
    # Create speakers table
    op.create_table(
        'speakers',
        sa.Column('speaker_id', sa.String(36), primary_key=True),
        sa.Column('speaker_identifier', sa.String(50), nullable=False, unique=True),
        sa.Column('speaker_name', sa.String(255), nullable=False),
        sa.Column('current_bucket', postgresql.ENUM('NO_TOUCH', 'LOW_TOUCH', 'MEDIUM_TOUCH', 'HIGH_TOUCH', name='speaker_bucket'), nullable=False),
        sa.Column('note_count', sa.Integer, nullable=False, default=0),
        sa.Column('average_ser_score', sa.Float, nullable=False, default=0.0),
        sa.Column('quality_trend', postgresql.ENUM('IMPROVING', 'STABLE', 'DECLINING', name='quality_trend'), nullable=False, default='STABLE'),
        sa.Column('should_transition', sa.Boolean, nullable=False, default=False),
        sa.Column('has_sufficient_data', sa.Boolean, nullable=False, default=False),
        sa.Column('metadata_', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for speakers
    op.create_index('idx_speakers_identifier', 'speakers', ['speaker_identifier'])
    op.create_index('idx_speakers_bucket', 'speakers', ['current_bucket'])
    op.create_index('idx_speakers_trend', 'speakers', ['quality_trend'])
    op.create_index('idx_speakers_transition', 'speakers', ['should_transition'])
    op.create_index('idx_speakers_name', 'speakers', ['speaker_name'])
    
    # Create historical_asr_data table
    op.create_table(
        'historical_asr_data',
        sa.Column('data_id', sa.String(36), primary_key=True),
        sa.Column('speaker_id', sa.String(36), sa.ForeignKey('speakers.speaker_id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_asr_text', sa.Text, nullable=False),
        sa.Column('final_reference_text', sa.Text, nullable=False),
        sa.Column('ser_score', sa.Float, nullable=False),
        sa.Column('edit_distance', sa.Integer, nullable=False),
        sa.Column('insertions', sa.Integer, nullable=False, default=0),
        sa.Column('deletions', sa.Integer, nullable=False, default=0),
        sa.Column('substitutions', sa.Integer, nullable=False, default=0),
        sa.Column('moves', sa.Integer, nullable=False, default=0),
        sa.Column('quality_level', sa.String(20), nullable=False),
        sa.Column('is_acceptable_quality', sa.Boolean, nullable=False, default=False),
        sa.Column('metadata_', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for historical_asr_data
    op.create_index('idx_historical_asr_speaker', 'historical_asr_data', ['speaker_id'])
    op.create_index('idx_historical_asr_quality', 'historical_asr_data', ['quality_level'])
    op.create_index('idx_historical_asr_ser_score', 'historical_asr_data', ['ser_score'])
    op.create_index('idx_historical_asr_created', 'historical_asr_data', ['created_at'])
    
    # Create validation_test_data table
    op.create_table(
        'validation_test_data',
        sa.Column('data_id', sa.String(36), primary_key=True),
        sa.Column('speaker_id', sa.String(36), sa.ForeignKey('speakers.speaker_id', ondelete='CASCADE'), nullable=False),
        sa.Column('historical_data_id', sa.String(36), sa.ForeignKey('historical_asr_data.data_id', ondelete='CASCADE'), nullable=True),
        sa.Column('original_asr_text', sa.Text, nullable=False),
        sa.Column('rag_corrected_text', sa.Text, nullable=False),
        sa.Column('final_reference_text', sa.Text, nullable=False),
        sa.Column('original_ser_metrics', sa.JSON, nullable=False),
        sa.Column('corrected_ser_metrics', sa.JSON, nullable=False),
        sa.Column('improvement_metrics', sa.JSON, nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, default='medium'),
        sa.Column('is_used', sa.Boolean, nullable=False, default=False),
        sa.Column('metadata_', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for validation_test_data
    op.create_index('idx_validation_test_speaker', 'validation_test_data', ['speaker_id'])
    op.create_index('idx_validation_test_priority', 'validation_test_data', ['priority'])
    op.create_index('idx_validation_test_used', 'validation_test_data', ['is_used'])
    op.create_index('idx_validation_test_created', 'validation_test_data', ['created_at'])
    
    # Create mt_validation_sessions table
    op.create_table(
        'mt_validation_sessions',
        sa.Column('session_id', sa.String(36), primary_key=True),
        sa.Column('speaker_id', sa.String(36), sa.ForeignKey('speakers.speaker_id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_name', sa.String(255), nullable=False),
        sa.Column('test_data_ids', postgresql.ARRAY(sa.String(36)), nullable=False),
        sa.Column('mt_user_id', sa.String(36), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'paused', 'completed', 'cancelled', name='session_status'), nullable=False, default='active'),
        sa.Column('progress_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('current_item_index', sa.Integer, nullable=False, default=0),
        sa.Column('total_items', sa.Integer, nullable=False),
        sa.Column('session_metadata', sa.JSON, nullable=True),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completion_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for mt_validation_sessions
    op.create_index('idx_mt_sessions_speaker', 'mt_validation_sessions', ['speaker_id'])
    op.create_index('idx_mt_sessions_user', 'mt_validation_sessions', ['mt_user_id'])
    op.create_index('idx_mt_sessions_status', 'mt_validation_sessions', ['status'])
    op.create_index('idx_mt_sessions_created', 'mt_validation_sessions', ['created_at'])
    
    # Create mt_feedback table
    op.create_table(
        'mt_feedback',
        sa.Column('feedback_id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('mt_validation_sessions.session_id', ondelete='CASCADE'), nullable=False),
        sa.Column('historical_data_id', sa.String(36), sa.ForeignKey('historical_asr_data.data_id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_asr_text', sa.Text, nullable=False),
        sa.Column('rag_corrected_text', sa.Text, nullable=False),
        sa.Column('final_reference_text', sa.Text, nullable=False),
        sa.Column('mt_feedback_rating', sa.Integer, nullable=False),
        sa.Column('mt_comments', sa.Text, nullable=True),
        sa.Column('improvement_assessment', postgresql.ENUM('SIGNIFICANT', 'MODERATE', 'MINIMAL', 'NONE', 'NEGATIVE', name='improvement_assessment'), nullable=False),
        sa.Column('recommended_for_bucket_change', sa.Boolean, nullable=False, default=False),
        sa.Column('feedback_metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for mt_feedback
    op.create_index('idx_mt_feedback_session', 'mt_feedback', ['session_id'])
    op.create_index('idx_mt_feedback_rating', 'mt_feedback', ['mt_feedback_rating'])
    op.create_index('idx_mt_feedback_assessment', 'mt_feedback', ['improvement_assessment'])
    op.create_index('idx_mt_feedback_bucket_rec', 'mt_feedback', ['recommended_for_bucket_change'])
    op.create_index('idx_mt_feedback_created', 'mt_feedback', ['created_at'])
    
    # Create bucket_transition_requests table
    op.create_table(
        'bucket_transition_requests',
        sa.Column('request_id', sa.String(36), primary_key=True),
        sa.Column('speaker_id', sa.String(36), sa.ForeignKey('speakers.speaker_id', ondelete='CASCADE'), nullable=False),
        sa.Column('current_bucket', postgresql.ENUM('NO_TOUCH', 'LOW_TOUCH', 'MEDIUM_TOUCH', 'HIGH_TOUCH', name='speaker_bucket'), nullable=False),
        sa.Column('proposed_bucket', postgresql.ENUM('NO_TOUCH', 'LOW_TOUCH', 'MEDIUM_TOUCH', 'HIGH_TOUCH', name='speaker_bucket'), nullable=False),
        sa.Column('justification', sa.Text, nullable=False),
        sa.Column('supporting_data', sa.JSON, nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', name='transition_status'), nullable=False, default='pending'),
        sa.Column('reviewer_id', sa.String(36), nullable=True),
        sa.Column('reviewer_comments', sa.Text, nullable=True),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('effective_date', sa.Date, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for bucket_transition_requests
    op.create_index('idx_transition_speaker', 'bucket_transition_requests', ['speaker_id'])
    op.create_index('idx_transition_status', 'bucket_transition_requests', ['status'])
    op.create_index('idx_transition_reviewer', 'bucket_transition_requests', ['reviewer_id'])
    op.create_index('idx_transition_created', 'bucket_transition_requests', ['created_at'])
    
    # Create rag_processing_jobs table
    op.create_table(
        'rag_processing_jobs',
        sa.Column('job_id', sa.String(36), primary_key=True),
        sa.Column('speaker_id', sa.String(36), sa.ForeignKey('speakers.speaker_id', ondelete='CASCADE'), nullable=True),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('status', postgresql.ENUM('queued', 'running', 'completed', 'failed', 'cancelled', name='job_status'), nullable=False, default='queued'),
        sa.Column('parameters', sa.JSON, nullable=True),
        sa.Column('progress_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('processing_results', sa.JSON, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for rag_processing_jobs
    op.create_index('idx_rag_jobs_speaker', 'rag_processing_jobs', ['speaker_id'])
    op.create_index('idx_rag_jobs_type', 'rag_processing_jobs', ['job_type'])
    op.create_index('idx_rag_jobs_status', 'rag_processing_jobs', ['status'])
    op.create_index('idx_rag_jobs_created', 'rag_processing_jobs', ['created_at'])
    
    # Create error_correction_pairs table
    op.create_table(
        'error_correction_pairs',
        sa.Column('pair_id', sa.String(36), primary_key=True),
        sa.Column('speaker_id', sa.String(36), sa.ForeignKey('speakers.speaker_id', ondelete='CASCADE'), nullable=False),
        sa.Column('error_text', sa.Text, nullable=False),
        sa.Column('correction_text', sa.Text, nullable=False),
        sa.Column('frequency', sa.Integer, nullable=False, default=1),
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('context_metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for error_correction_pairs
    op.create_index('idx_error_pairs_speaker', 'error_correction_pairs', ['speaker_id'])
    op.create_index('idx_error_pairs_frequency', 'error_correction_pairs', ['frequency'])
    op.create_index('idx_error_pairs_confidence', 'error_correction_pairs', ['confidence_score'])
    op.create_index('idx_error_pairs_created', 'error_correction_pairs', ['created_at'])
    
    # Create triggers for updated_at columns
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Add triggers to tables with updated_at columns
    for table in ['speakers', 'mt_validation_sessions', 'bucket_transition_requests', 'rag_processing_jobs', 'error_correction_pairs']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    """Drop speaker bucket management schema."""
    
    # Drop triggers
    for table in ['speakers', 'mt_validation_sessions', 'bucket_transition_requests', 'rag_processing_jobs', 'error_correction_pairs']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop tables in reverse order of dependencies
    op.drop_table('error_correction_pairs')
    op.drop_table('rag_processing_jobs')
    op.drop_table('bucket_transition_requests')
    op.drop_table('mt_feedback')
    op.drop_table('mt_validation_sessions')
    op.drop_table('validation_test_data')
    op.drop_table('historical_asr_data')
    op.drop_table('speakers')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS transition_status")
    op.execute("DROP TYPE IF EXISTS job_status")
    op.execute("DROP TYPE IF EXISTS improvement_assessment")
    op.execute("DROP TYPE IF EXISTS session_status")
    op.execute("DROP TYPE IF EXISTS quality_trend")
    op.execute("DROP TYPE IF EXISTS speaker_bucket")
