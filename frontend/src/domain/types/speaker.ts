/**
 * Speaker domain types for bucket management
 */

export enum SpeakerBucket {
  HIGH_TOUCH = 'HIGH_TOUCH',
  MEDIUM_TOUCH = 'MEDIUM_TOUCH',
  LOW_TOUCH = 'LOW_TOUCH',
  NO_TOUCH = 'NO_TOUCH'
}

export enum QualityTrend {
  IMPROVING = 'improving',
  STABLE = 'stable',
  DECLINING = 'declining',
  INSUFFICIENT_DATA = 'insufficient_data'
}

export enum TransitionStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled'
}

export interface Speaker {
  speaker_id: string;
  speaker_identifier: string;
  speaker_name: string;
  current_bucket: SpeakerBucket;
  recommended_bucket?: SpeakerBucket;
  note_count: number;
  average_ser_score: number;
  quality_trend: QualityTrend;
  should_transition: boolean;
  has_sufficient_data: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SpeakerSearchFilters {
  name_pattern?: string;
  bucket?: SpeakerBucket;
  min_ser_score?: number;
  max_ser_score?: number;
  has_sufficient_data?: boolean;
  quality_trend?: QualityTrend;
}

export interface SpeakerSearchParams extends SpeakerSearchFilters {
  page?: number;
  page_size?: number;
}

export interface SpeakerListResponse {
  speakers: Speaker[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface BucketTransitionRequest {
  request_id: string;
  speaker_id: string;
  from_bucket: SpeakerBucket;
  to_bucket: SpeakerBucket;
  transition_type: string;
  transition_reason: string;
  ser_improvement?: number;
  status: TransitionStatus;
  requested_by?: string;
  approved_by?: string;
  approval_notes?: string;
  is_urgent: boolean;
  priority_score: number;
  processing_time_hours?: number;
  created_at: string;
  approved_at?: string;
}

export interface CreateTransitionRequest {
  speaker_id: string;
  from_bucket: SpeakerBucket;
  to_bucket: SpeakerBucket;
  transition_reason: string;
  ser_improvement?: number;
  requested_by: string;
}

export interface SpeakerBucketStats {
  bucket_distribution: Record<SpeakerBucket, number>;
  total_speakers: number;
  quality_metrics: {
    average_ser_score: number;
    quality_distribution: Record<string, number>;
    improvement_trends: Record<string, number>;
  };
  transition_metrics: {
    pending_transitions: number;
    recent_transitions: number;
    success_rate: number;
  };
  data_quality: {
    speakers_with_sufficient_data: number;
    data_coverage_percentage: number;
  };
}

export interface SERMetrics {
  ser_score: number;
  edit_distance: number;
  insertions: number;
  deletions: number;
  substitutions: number;
  moves: number;
  quality_level: 'high' | 'medium' | 'low';
  is_acceptable_quality: boolean;
}

export interface SpeakerSERAnalysis {
  speaker_id: string;
  total_calculations: number;
  average_ser_score: number;
  quality_distribution: Record<string, number>;
  historical_trend: Array<{
    date: string;
    ser_score: number;
    note_count: number;
  }>;
  improvement_metrics: {
    trend_direction: QualityTrend;
    improvement_rate: number;
    consistency_score: number;
  };
  error_pattern_analysis?: {
    common_errors: Array<{
      error_type: string;
      frequency: number;
      examples: string[];
    }>;
    improvement_opportunities: string[];
  };
}

export interface ComprehensiveSpeakerView {
  speaker: Speaker;
  ser_analysis?: SpeakerSERAnalysis;
  error_patterns?: {
    total_pairs: number;
    error_statistics: Record<string, any>;
    error_patterns: Record<string, number>;
    high_confidence_pairs: number;
    training_suitable_pairs: number;
  };
  transition_history?: BucketTransitionRequest[];
  timestamp: string;
}

// UI-specific types
export interface SpeakerTableColumn {
  field: keyof Speaker | 'actions';
  headerName: string;
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  renderCell?: (params: any) => React.ReactNode;
}

export interface SpeakerSelectionState {
  selectedSpeakers: string[];
  searchFilters: SpeakerSearchFilters;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  currentPage: number;
  pageSize: number;
}

export interface BucketVisualizationData {
  bucket: SpeakerBucket;
  count: number;
  percentage: number;
  averageQuality: number;
  trend: QualityTrend;
  color: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: string;
  };
  timestamp: string;
  request_id: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

// Form types
export interface SpeakerFormData {
  speaker_identifier: string;
  speaker_name: string;
  initial_bucket: SpeakerBucket;
  metadata?: Record<string, any>;
}

export interface TransitionRequestFormData {
  speaker_id: string;
  to_bucket: SpeakerBucket;
  transition_reason: string;
  ser_improvement?: number;
}

// Filter and search types
export interface AdvancedSearchFilters extends SpeakerSearchFilters {
  created_date_from?: string;
  created_date_to?: string;
  last_updated_from?: string;
  last_updated_to?: string;
  transition_status?: TransitionStatus;
  has_pending_transitions?: boolean;
}

export interface QuickFilterOption {
  label: string;
  value: string;
  filters: Partial<SpeakerSearchFilters>;
  count?: number;
}

// Dashboard types
export interface DashboardMetrics {
  speaker_statistics: SpeakerBucketStats;
  ser_metrics: {
    summary: {
      total_calculations: number;
      average_ser_score: number;
      quality_distribution: Record<string, number>;
    };
  };
  rag_processing: {
    summary: {
      total_speakers_processed: number;
      total_error_correction_pairs: number;
      processing_performance: Record<string, number>;
    };
  };
  transition_statistics: {
    statistics: {
      total_requests: number;
      pending_requests: number;
      approval_rate: number;
      urgent_requests: number;
    };
  };
  services_status: Record<string, 'healthy' | 'error' | 'degraded'>;
  timestamp: string;
}
