"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create error_reports table
    op.create_table('error_reports',
        sa.Column('error_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('speaker_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reported_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('corrected_text', sa.Text(), nullable=False),
        sa.Column('error_categories', sa.JSON(), nullable=False),
        sa.Column('severity_level', sa.String(length=20), nullable=False),
        sa.Column('start_position', sa.Integer(), nullable=False),
        sa.Column('end_position', sa.Integer(), nullable=False),
        sa.Column('context_notes', sa.Text(), nullable=True),
        sa.Column('error_timestamp', sa.DateTime(), nullable=False),
        sa.Column('reported_at', sa.DateTime(), nullable=False),
        sa.Column('bucket_type', sa.String(length=20), nullable=False),
        sa.Column('audio_quality', sa.String(length=20), nullable=False),
        sa.Column('speaker_clarity', sa.String(length=30), nullable=False),
        sa.Column('background_noise', sa.String(length=20), nullable=False),
        sa.Column('number_of_speakers', sa.String(length=10), nullable=False),
        sa.Column('overlapping_speech', sa.Boolean(), nullable=False),
        sa.Column('requires_specialized_knowledge', sa.Boolean(), nullable=False),
        sa.Column('additional_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('error_id')
    )
    
    # Create indexes for error_reports
    op.create_index('ix_error_reports_job_id', 'error_reports', ['job_id'])
    op.create_index('ix_error_reports_speaker_id', 'error_reports', ['speaker_id'])
    op.create_index('ix_error_reports_client_id', 'error_reports', ['client_id'])
    op.create_index('ix_error_reports_reported_by', 'error_reports', ['reported_by'])
    op.create_index('ix_error_reports_severity_level', 'error_reports', ['severity_level'])
    op.create_index('ix_error_reports_bucket_type', 'error_reports', ['bucket_type'])
    op.create_index('ix_error_reports_error_timestamp', 'error_reports', ['error_timestamp'])
    
    # Create speaker_bucket_history table
    op.create_table('speaker_bucket_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('speaker_id', sa.String(length=255), nullable=False),
        sa.Column('bucket_name', sa.String(length=255), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for speaker_bucket_history
    op.create_index('ix_speaker_bucket_history_speaker_id', 'speaker_bucket_history', ['speaker_id'])
    op.create_index('ix_speaker_bucket_history_bucket_name', 'speaker_bucket_history', ['bucket_name'])
    op.create_index('ix_speaker_bucket_history_timestamp', 'speaker_bucket_history', ['timestamp'])
    op.create_index('ix_speaker_bucket_history_user_id', 'speaker_bucket_history', ['user_id'])
    
    # Create speaker_performance_metrics table
    op.create_table('speaker_performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('speaker_id', sa.String(length=255), nullable=False),
        sa.Column('accuracy_score', sa.String(length=50), nullable=True),
        sa.Column('error_rate', sa.String(length=50), nullable=True),
        sa.Column('processing_time', sa.String(length=50), nullable=True),
        sa.Column('measurement_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metrics_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for speaker_performance_metrics
    op.create_index('ix_speaker_performance_metrics_speaker_id', 'speaker_performance_metrics', ['speaker_id'])
    op.create_index('ix_speaker_performance_metrics_measurement_date', 'speaker_performance_metrics', ['measurement_date'])
    
    # Create verification_jobs table
    op.create_table('verification_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_name', sa.String(length=255), nullable=False),
        sa.Column('job_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('progress_percentage', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for verification_jobs
    op.create_index('ix_verification_jobs_job_type', 'verification_jobs', ['job_type'])
    op.create_index('ix_verification_jobs_status', 'verification_jobs', ['status'])
    op.create_index('ix_verification_jobs_started_at', 'verification_jobs', ['started_at'])
    op.create_index('ix_verification_jobs_created_by', 'verification_jobs', ['created_by'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('verification_jobs')
    op.drop_table('speaker_performance_metrics')
    op.drop_table('speaker_bucket_history')
    op.drop_table('error_reports')
