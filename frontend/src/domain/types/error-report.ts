/**
 * Error Report domain types based on Error Reporting Service schemas
 */

export enum SeverityLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum ErrorStatus {
  PENDING = 'pending',
  PROCESSED = 'processed',
  ARCHIVED = 'archived',
}

export enum BucketType {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export interface ErrorReport {
  id: string;
  job_id: string;
  speaker_id: string;
  client_id: string;
  bucket_type: BucketType;
  reported_by: string;
  original_text: string;
  corrected_text: string;
  error_categories: string[];
  severity_level: SeverityLevel;
  start_position: number;
  end_position: number;
  context_notes?: string;
  error_timestamp: string;
  created_at: string;
  updated_at: string;
  status: ErrorStatus;
  metadata?: Record<string, any>;
}

export interface SubmitErrorReportRequest {
  jobId: string;
  speakerId: string;
  clientId: string;
  bucketType: BucketType;
  textSelections: TextSelection[];
  selectedCategories: ErrorCategory[];
  correctionText: string;
  metadata: ErrorMetadata;
}

export interface ErrorFilters {
  jobIds?: string[];
  speakerIds?: string[];
  errorCategories?: string[];
  severityLevels?: SeverityLevel[];
  statuses?: ErrorStatus[];
  reportedBy?: string[];
  dateRange?: {
    startDate: string;
    endDate: string;
  };
}

export interface SearchErrorsRequest {
  page?: number;
  size?: number;
  status?: string;
  speaker_id?: string;
  client_id?: string;
  bucket_type?: string;
  job_id?: string;
  search?: string;
  date_from?: string;
  date_to?: string;
  severity_level?: string;
  categories?: string;
}

export interface UpdateErrorReportRequest {
  errorId: string;
  updatedBy: string;
  updates: Partial<Pick<ErrorReport, 'correctedText' | 'errorCategories' | 'severityLevel' | 'contextNotes' | 'status'>>;
}

// Text selection types for the UI
export interface TextSelection {
  text: string;
  startPosition: number;
  endPosition: number;
  selectionId: string;
  confidence?: number;
  timestamp?: number;
}

export interface NonContiguousSelection {
  selections: TextSelection[];
  combinedText: string;
}

// Error categorization types
export interface ErrorCategory {
  id: string;
  name: string;
  description: string;
  parentCategory?: string;
  isActive: boolean;
}

// Audio quality and metadata types
export type AudioQualityIndicator = 'excellent' | 'good' | 'fair' | 'poor';
export type NoiseLevel = 'none' | 'low' | 'medium' | 'high';
export type ClarityLevel = 'clear' | 'somewhat_clear' | 'unclear' | 'very_unclear';
export type UrgencyLevel = 'low' | 'medium' | 'high';

export interface ErrorMetadata {
  audioQuality: AudioQualityIndicator;
  backgroundNoise: NoiseLevel;
  speakerClarity: ClarityLevel;
  contextualNotes: string;
  urgencyLevel: UrgencyLevel;
  speechRate?: number;
  confidenceRating?: number;
  contextualTags?: string[];
  hasMultipleSpeakers?: boolean;
  hasOverlappingSpeech?: boolean;
  requiresSpecializedKnowledge?: boolean;
}

// Vector similarity types
export interface SimilarityResult {
  patternId: string;
  similarText: string;
  confidence: number;
  frequency: number;
  suggestedCorrection: string;
  speakerIds: string[];
  category: string;
}

export interface ErrorPattern {
  patternId: string;
  originalText: string;
  correctedText: string;
  frequency: number;
  confidence: number;
  category: string;
  speakerIds: string[];
}

// Validation types
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// Analytics types for error reporting
export interface ErrorAnalytics {
  totalErrors: number;
  errorsByCategory: Record<string, number>;
  errorsBySeverity: Record<SeverityLevel, number>;
  errorsByStatus: Record<ErrorStatus, number>;
  trendsOverTime: Array<{
    date: string;
    count: number;
  }>;
}

// Speaker Profile and Bucket Progression Types
export interface SpeakerProfile {
  speaker_id: string;
  current_bucket: BucketType;
  bucket_info: BucketInfo;
  statistics: SpeakerStatistics;
  timestamps: SpeakerTimestamps;
  metadata: Record<string, any>;
}

export interface BucketInfo {
  label: string;
  description: string;
  color: string;
  icon: string;
  level: number;
}

export interface SpeakerStatistics {
  total_reports: number;
  total_errors_found: number;
  total_corrections_made: number;
  average_error_rate: number;
  average_correction_accuracy: number;
  days_in_current_bucket: number;
  bucket_change_count: number;
}

export interface SpeakerTimestamps {
  created_at: string;
  updated_at: string;
  last_report_date?: string;
}

export interface BucketChangeLog {
  change_id: string;
  old_bucket: BucketInfo;
  new_bucket: BucketInfo;
  change_reason: string;
  changed_at: string;
  metrics_at_change: SpeakerMetrics;
  metadata: Record<string, any>;
}

export interface SpeakerMetrics {
  total_reports: number;
  total_errors_found: number;
  total_corrections_made: number;
  average_error_rate: number;
  average_correction_accuracy: number;
  last_report_date?: string;
  reports_last_30_days: number;
  errors_last_30_days: number;
  corrections_last_30_days: number;
  consistency_score: number;
  improvement_trend: number;
}

export interface BucketProgressionRecommendation {
  recommended_bucket?: BucketType;
  direction: 'promotion' | 'demotion' | 'stable';
  confidence_score: number;
  reason: string;
}

export interface BucketProgressionResponse {
  speaker_id: string;
  evaluation_performed: boolean;
  bucket_changed: boolean;
  old_bucket?: BucketType;
  new_bucket?: BucketType;
  change_reason?: string;
  recommendation?: BucketProgressionRecommendation;
  evaluation_timestamp: string;
}

export interface BucketStatistics {
  total_profiles: number;
  bucket_distribution: Record<string, BucketDistribution>;
  change_statistics: ChangeStatistics;
  generated_at: string;
}

export interface BucketDistribution {
  count: number;
  percentage: number;
  info: BucketInfo;
}

export interface ChangeStatistics {
  total_bucket_changes: number;
  recent_bucket_changes: number;
  average_changes_per_profile: number;
}

export interface BucketProgressionNotification {
  type: 'promotion' | 'demotion';
  old_bucket: BucketType;
  new_bucket: BucketType;
  reason: string;
  timestamp: string;
}
