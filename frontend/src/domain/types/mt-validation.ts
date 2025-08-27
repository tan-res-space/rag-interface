/**
 * MT Validation domain types
 */

export enum SessionStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum ImprovementAssessment {
  SIGNIFICANT = 'significant',
  MODERATE = 'moderate',
  MINIMAL = 'minimal',
  NONE = 'none',
  WORSE = 'worse'
}

export enum ValidationItemStatus {
  PENDING = 'pending',
  IN_REVIEW = 'in_review',
  COMPLETED = 'completed',
  SKIPPED = 'skipped'
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

export interface SERComparison {
  original_ser: SERMetrics;
  corrected_ser: SERMetrics;
  improvement: number;
  improvement_percentage: number;
  is_significant_improvement: boolean;
}

export interface ValidationTestData {
  data_id: string;
  speaker_id: string;
  original_asr_text: string;
  rag_corrected_text: string;
  final_reference_text: string;
  original_ser_metrics: SERMetrics;
  corrected_ser_metrics: SERMetrics;
  improvement_metrics: SERComparison;
  metadata?: Record<string, any>;
}

export interface ValidationSession {
  session_id: string;
  speaker_id: string;
  session_name: string;
  test_data_count: number;
  status: SessionStatus;
  mt_user_id?: string;
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  duration_minutes?: number;
  session_metadata?: Record<string, any>;
  created_at: string;
}

export interface MTFeedback {
  feedback_id: string;
  session_id: string;
  historical_data_id: string;
  original_asr_text: string;
  rag_corrected_text: string;
  final_reference_text: string;
  mt_feedback_rating: number; // 1-5 scale
  mt_comments?: string;
  improvement_assessment: ImprovementAssessment;
  recommended_for_bucket_change: boolean;
  ser_comparison: SERComparison;
  feedback_metadata?: Record<string, any>;
  created_at: string;
}

export interface TextDifference {
  type: 'equal' | 'insert' | 'delete' | 'replace';
  originalText: string;
  correctedText: string;
  position: {
    start: number;
    end: number;
  };
  confidence?: number;
}

export interface ValidationItem {
  item_id: string;
  session_id: string;
  test_data: ValidationTestData;
  status: ValidationItemStatus;
  feedback?: MTFeedback;
  differences: TextDifference[];
  review_time_seconds?: number;
  created_at: string;
  completed_at?: string;
}

// Request/Response types
export interface StartValidationSessionRequest {
  speaker_id: string;
  session_name: string;
  test_data_ids: string[];
  mt_user_id: string;
  session_metadata?: Record<string, any>;
}

export interface SubmitMTFeedbackRequest {
  session_id: string;
  historical_data_id: string;
  original_asr_text: string;
  rag_corrected_text: string;
  final_reference_text: string;
  mt_feedback_rating: number;
  mt_comments?: string;
  improvement_assessment: ImprovementAssessment;
  recommended_for_bucket_change: boolean;
  feedback_metadata?: Record<string, any>;
}

export interface CompleteValidationSessionRequest {
  session_id: string;
  completion_notes?: string;
  session_summary?: string;
}

// UI-specific types
export interface ValidationWorkflowState {
  currentSession: ValidationSession | null;
  currentItem: ValidationItem | null;
  currentItemIndex: number;
  totalItems: number;
  sessionProgress: number;
  isReviewing: boolean;
  showDifferences: boolean;
  showSERMetrics: boolean;
  comparisonMode: 'side-by-side' | 'unified' | 'overlay';
}

export interface MTValidationFilters {
  session_status?: SessionStatus;
  mt_user_id?: string;
  speaker_id?: string;
  date_range_start?: string;
  date_range_end?: string;
  improvement_assessment?: ImprovementAssessment;
  rating_min?: number;
  rating_max?: number;
}

export interface ValidationSessionSummary {
  session: ValidationSession;
  total_feedback_items: number;
  average_rating: number;
  improvement_distribution: Record<ImprovementAssessment, number>;
  bucket_change_recommendations: number;
  average_review_time_minutes: number;
  quality_insights: {
    significant_improvements: number;
    areas_for_improvement: string[];
    overall_assessment: string;
  };
}

export interface MTUserStatistics {
  mt_user_id: string;
  total_sessions: number;
  completed_sessions: number;
  total_feedback_items: number;
  average_session_duration_minutes: number;
  feedback_quality_score: number;
  bucket_change_recommendations: number;
  accuracy_score: number;
  productivity_score: number;
  recent_activity: Array<{
    date: string;
    sessions_completed: number;
    items_reviewed: number;
  }>;
}

export interface DifferenceHighlightOptions {
  showInsertions: boolean;
  showDeletions: boolean;
  showSubstitutions: boolean;
  showMoves: boolean;
  highlightIntensity: 'subtle' | 'medium' | 'strong';
  colorScheme: 'default' | 'colorblind' | 'high-contrast';
}

export interface ValidationKeyboardShortcuts {
  nextItem: string;
  previousItem: string;
  submitFeedback: string;
  toggleDifferences: string;
  toggleSERMetrics: string;
  focusRating: string;
  focusComments: string;
  saveAndNext: string;
}

// Form types
export interface MTFeedbackFormData {
  rating: number;
  comments: string;
  improvement_assessment: ImprovementAssessment;
  recommended_for_bucket_change: boolean;
  confidence_level: number;
  review_notes: string;
}

export interface ValidationPreferences {
  auto_advance: boolean;
  show_ser_metrics_by_default: boolean;
  highlight_differences_by_default: boolean;
  default_comparison_mode: 'side-by-side' | 'unified' | 'overlay';
  keyboard_shortcuts_enabled: boolean;
  auto_save_feedback: boolean;
  review_time_tracking: boolean;
}

// Analytics types
export interface ValidationAnalytics {
  session_id: string;
  total_review_time_minutes: number;
  items_per_minute: number;
  accuracy_metrics: {
    consistent_ratings: number;
    rating_variance: number;
    feedback_quality_score: number;
  };
  improvement_insights: {
    most_common_assessment: ImprovementAssessment;
    bucket_change_rate: number;
    quality_trend: 'improving' | 'stable' | 'declining';
  };
  efficiency_metrics: {
    average_time_per_item: number;
    fastest_review_time: number;
    slowest_review_time: number;
    optimal_review_time_range: [number, number];
  };
}

// Export types
export interface ValidationExportData {
  session_info: ValidationSession;
  feedback_items: MTFeedback[];
  summary_statistics: ValidationSessionSummary;
  export_timestamp: string;
  export_format: 'csv' | 'excel' | 'pdf' | 'json';
}

// Real-time updates
export interface ValidationUpdate {
  type: 'session_progress' | 'item_completed' | 'session_completed' | 'error';
  session_id: string;
  data: any;
  timestamp: string;
}
