/**
 * TypeScript types for System Health monitoring
 * Extends existing patterns from the codebase
 */

import { ApiResponse, LoadingState } from '@domain/types/common';

// Service Health Status
export type HealthStatus = 'healthy' | 'degraded' | 'error' | 'unknown';

// Individual Service Health Response
export interface ServiceHealthResponse {
  status: HealthStatus;
  version: string;
  timestamp: string;
  service: string;
  response_time_ms?: number;
  uptime_percentage?: number;
  last_check?: string;
  error_rate?: number;
  details?: {
    cpu_usage?: number;
    memory_usage?: number;
    disk_usage?: number;
    active_connections?: number;
    database_status?: string;
    cache_status?: string;
  };
  endpoints?: Record<string, string>;
}

// Service Configuration
export interface ServiceConfig {
  name: string;
  displayName: string;
  url: string;
  port: number;
  healthEndpoint: string;
  timeout: number;
  expectedResponseTime: number;
  criticalResponseTime: number;
}

// Health Check Result
export interface HealthCheckResult {
  service: string;
  status: HealthStatus;
  responseTime: number;
  timestamp: string;
  error?: string;
  data?: ServiceHealthResponse;
}

// System Health Overview
export interface SystemHealthOverview {
  overall_status: HealthStatus;
  total_services: number;
  healthy_services: number;
  degraded_services: number;
  error_services: number;
  unknown_services: number;
  last_updated: string;
  average_response_time: number;
  overall_uptime: number;
}

// Historical Health Data
export interface HealthHistoryEntry {
  timestamp: string;
  service: string;
  status: HealthStatus;
  response_time: number;
  uptime_percentage: number;
}

// Diagnostic Information
export interface DiagnosticInfo {
  service: string;
  connectivity: {
    can_reach: boolean;
    dns_resolution: boolean;
    port_open: boolean;
    ssl_valid?: boolean;
  };
  performance: {
    response_time: number;
    throughput?: number;
    error_rate: number;
  };
  dependencies: {
    database?: HealthStatus;
    cache?: HealthStatus;
    external_apis?: Record<string, HealthStatus>;
  };
  system_info?: {
    version: string;
    uptime: string;
    environment: string;
  };
}

// Troubleshooting Suggestion
export interface TroubleshootingSuggestion {
  issue: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  possible_causes: string[];
  suggested_actions: string[];
  documentation_links?: string[];
}

// Health Monitoring Configuration
export interface HealthMonitoringConfig {
  auto_refresh: boolean;
  refresh_interval: number; // in seconds
  timeout: number; // in milliseconds
  retry_attempts: number;
  alert_thresholds: {
    response_time_warning: number;
    response_time_critical: number;
    uptime_warning: number;
    uptime_critical: number;
    error_rate_warning: number;
    error_rate_critical: number;
  };
}

// Export Data
export interface HealthReportExport {
  generated_at: string;
  report_type: 'summary' | 'detailed' | 'historical';
  time_range?: {
    start: string;
    end: string;
  };
  system_overview: SystemHealthOverview;
  services: Record<string, ServiceHealthResponse>;
  diagnostics?: Record<string, DiagnosticInfo>;
  troubleshooting?: TroubleshootingSuggestion[];
}

// API Response Types
export type HealthCheckApiResponse = ApiResponse<HealthCheckResult>;
export type SystemHealthApiResponse = ApiResponse<SystemHealthOverview>;
export type DiagnosticsApiResponse = ApiResponse<DiagnosticInfo>;
export type HealthHistoryApiResponse = ApiResponse<HealthHistoryEntry[]>;

// State Management Types
export interface HealthMonitoringState {
  services: Record<string, HealthCheckResult>;
  overview: SystemHealthOverview | null;
  diagnostics: Record<string, DiagnosticInfo>;
  history: HealthHistoryEntry[];
  config: HealthMonitoringConfig;
  loading: LoadingState;
  error: string | null;
  last_refresh: string | null;
}

// Hook Return Types
export interface UseHealthMonitoringReturn {
  services: Record<string, HealthCheckResult>;
  overview: SystemHealthOverview | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
  toggleAutoRefresh: () => void;
  exportReport: (type: 'summary' | 'detailed' | 'historical') => Promise<void>;
}

export interface UseServiceHealthReturn {
  health: HealthCheckResult | null;
  diagnostics: DiagnosticInfo | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
  runDiagnostics: () => void;
}

// Component Props Types
export interface ServiceStatusCardProps {
  service: string;
  health: HealthCheckResult;
  onRefresh?: () => void;
  onViewDiagnostics?: () => void;
}

export interface HealthOverviewProps {
  overview: SystemHealthOverview;
  onRefresh?: () => void;
  loading?: boolean;
}

export interface DiagnosticsPanelProps {
  service: string;
  diagnostics: DiagnosticInfo;
  onClose?: () => void;
}

export interface TroubleshootingPanelProps {
  suggestions: TroubleshootingSuggestion[];
  service?: string;
}
