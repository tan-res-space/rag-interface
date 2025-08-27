/**
 * Dashboard domain types for comprehensive system overview
 */

import { SpeakerBucket, QualityTrend } from './speaker';
import { ImprovementAssessment, SessionStatus } from './mt-validation';

export interface DashboardMetrics {
  speaker_statistics: SpeakerBucketStats;
  ser_metrics: SERMetricsSummary;
  rag_processing: RAGProcessingSummary;
  mt_validation: MTValidationSummary;
  transition_statistics: TransitionStatisticsSummary;
  services_status: ServicesHealthStatus;
  timestamp: string;
}

export interface SpeakerBucketStats {
  bucket_distribution: Record<SpeakerBucket, number>;
  total_speakers: number;
  quality_metrics: {
    average_ser_score: number;
    quality_distribution: Record<string, number>;
    improvement_trends: Record<QualityTrend, number>;
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

export interface SERMetricsSummary {
  summary: {
    total_calculations: number;
    average_ser_score: number;
    quality_distribution: Record<string, number>;
    improvement_rate: number;
  };
  trends: {
    daily_calculations: Array<{
      date: string;
      count: number;
      average_score: number;
    }>;
    quality_improvement_over_time: Array<{
      date: string;
      improvement_percentage: number;
    }>;
  };
  performance: {
    calculation_speed_ms: number;
    batch_processing_efficiency: number;
    error_rate: number;
  };
}

export interface RAGProcessingSummary {
  summary: {
    total_speakers_processed: number;
    total_error_correction_pairs: number;
    processing_performance: Record<string, number>;
    active_jobs: number;
  };
  quality_metrics: {
    correction_accuracy: number;
    confidence_scores: {
      high_confidence: number;
      medium_confidence: number;
      low_confidence: number;
    };
    error_pattern_coverage: number;
  };
  processing_stats: {
    average_processing_time_minutes: number;
    successful_jobs: number;
    failed_jobs: number;
    queue_length: number;
  };
}

export interface MTValidationSummary {
  statistics: {
    total_sessions: number;
    active_sessions: number;
    completed_sessions: number;
    total_feedback_items: number;
  };
  quality_metrics: {
    average_rating: number;
    improvement_distribution: Record<ImprovementAssessment, number>;
    bucket_change_recommendations: number;
    validation_accuracy: number;
  };
  productivity: {
    average_session_duration_minutes: number;
    items_per_hour: number;
    mt_user_count: number;
    efficiency_score: number;
  };
}

export interface TransitionStatisticsSummary {
  statistics: {
    total_requests: number;
    pending_requests: number;
    approved_requests: number;
    rejected_requests: number;
    approval_rate: number;
  };
  trends: {
    requests_over_time: Array<{
      date: string;
      count: number;
      approval_rate: number;
    }>;
    bucket_transition_patterns: Record<string, number>;
  };
  impact: {
    speakers_promoted: number;
    speakers_demoted: number;
    quality_improvement_correlation: number;
    cost_savings_estimate: number;
  };
}

export interface ServicesHealthStatus {
  user_management: ServiceHealth;
  verification: ServiceHealth;
  rag_integration: ServiceHealth;
  api_gateway: ServiceHealth;
}

export interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'error' | 'unknown';
  response_time_ms: number;
  uptime_percentage: number;
  last_check: string;
  error_rate: number;
  details?: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    active_connections: number;
  };
}

// Chart and visualization types
export interface ChartDataPoint {
  x: string | number;
  y: number;
  label?: string;
  color?: string;
  metadata?: Record<string, any>;
}

export interface TimeSeriesData {
  series: Array<{
    name: string;
    data: ChartDataPoint[];
    color?: string;
  }>;
  xAxis: {
    type: 'datetime' | 'category';
    title: string;
  };
  yAxis: {
    title: string;
    format?: string;
  };
}

export interface PieChartData {
  data: Array<{
    name: string;
    value: number;
    color?: string;
    percentage?: number;
  }>;
  total: number;
}

export interface BarChartData {
  categories: string[];
  series: Array<{
    name: string;
    data: number[];
    color?: string;
  }>;
}

// Dashboard widget types
export interface DashboardWidget {
  id: string;
  type: 'metric' | 'chart' | 'table' | 'status' | 'progress';
  title: string;
  size: 'small' | 'medium' | 'large' | 'full';
  position: { x: number; y: number; w: number; h: number };
  data: any;
  config?: Record<string, any>;
  refreshInterval?: number;
  lastUpdated?: string;
}

export interface DashboardLayout {
  id: string;
  name: string;
  description?: string;
  widgets: DashboardWidget[];
  isDefault: boolean;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

// Real-time update types
export interface DashboardUpdate {
  type: 'metric_update' | 'status_change' | 'alert' | 'refresh';
  widget_id?: string;
  data: any;
  timestamp: string;
}

// Alert and notification types
export interface DashboardAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  timestamp: string;
  acknowledged: boolean;
  actions?: Array<{
    label: string;
    action: string;
    primary?: boolean;
  }>;
}

// Filter and time range types
export interface DashboardFilters {
  dateRange: {
    start: string;
    end: string;
    preset?: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom';
  };
  speakers?: string[];
  buckets?: SpeakerBucket[];
  services?: string[];
  mtUsers?: string[];
}

export interface QuickMetric {
  label: string;
  value: number | string;
  unit?: string;
  trend?: {
    direction: 'up' | 'down' | 'stable';
    percentage: number;
    period: string;
  };
  status?: 'good' | 'warning' | 'critical';
  icon?: string;
  color?: string;
}

// Export and reporting types
export interface DashboardReport {
  id: string;
  title: string;
  description?: string;
  filters: DashboardFilters;
  widgets: string[];
  format: 'pdf' | 'excel' | 'csv' | 'json';
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly';
    time: string;
    recipients: string[];
  };
  createdAt: string;
  lastGenerated?: string;
}

// Performance monitoring types
export interface PerformanceMetrics {
  page_load_time: number;
  api_response_times: Record<string, number>;
  chart_render_times: Record<string, number>;
  memory_usage: number;
  error_count: number;
  user_interactions: number;
}

// User preferences for dashboard
export interface DashboardPreferences {
  default_layout: string;
  refresh_interval: number;
  theme: 'light' | 'dark' | 'auto';
  timezone: string;
  number_format: 'US' | 'EU' | 'custom';
  chart_animations: boolean;
  auto_refresh: boolean;
  notification_settings: {
    alerts: boolean;
    email_reports: boolean;
    push_notifications: boolean;
  };
}

// Drill-down and navigation types
export interface DrillDownContext {
  source_widget: string;
  source_data: any;
  filters: Record<string, any>;
  breadcrumb: Array<{
    label: string;
    filters: Record<string, any>;
  }>;
}

export interface NavigationAction {
  type: 'drill_down' | 'filter' | 'navigate' | 'export';
  target?: string;
  data?: any;
  context?: DrillDownContext;
}
