/**
 * Dashboard API client for comprehensive system metrics
 */

import { BaseApi } from './base-api';
import {
  DashboardMetrics,
  SpeakerBucketStats,
  SERMetricsSummary,
  RAGProcessingSummary,
  MTValidationSummary,
  TransitionStatisticsSummary,
  ServicesHealthStatus,
  DashboardFilters,
  DashboardLayout,
  DashboardWidget,
  DashboardReport,
  DashboardAlert,
  PerformanceMetrics,
  TimeSeriesData,
  PieChartData,
  BarChartData,
} from '@/domain/types/dashboard';

export class DashboardApi extends BaseApi {
  private readonly basePath = '/api/v1/speaker-bucket-management/dashboard';

  /**
   * Get comprehensive dashboard overview
   * Falls back to direct service calls if API Gateway is unavailable
   */
  async getDashboardOverview(filters?: DashboardFilters): Promise<DashboardMetrics> {
    try {
      // Try API Gateway first
      const params = new URLSearchParams();

      if (filters) {
        if (filters.dateRange) {
          params.append('start_date', filters.dateRange.start);
          params.append('end_date', filters.dateRange.end);
        }
        if (filters.speakers?.length) {
          params.append('speakers', filters.speakers.join(','));
        }
        if (filters.buckets?.length) {
          params.append('buckets', filters.buckets.join(','));
        }
      }

      return await this.get<DashboardMetrics>(`${this.basePath}/overview?${params.toString()}`);
    } catch (error) {
      // Fallback to direct service calls
      console.warn('API Gateway unavailable, using direct service calls:', error);
      return await this.getDashboardOverviewDirect(filters);
    }
  }

  /**
   * Get dashboard overview by calling services directly
   */
  private async getDashboardOverviewDirect(filters?: DashboardFilters): Promise<DashboardMetrics> {
    try {
      // Call services directly and aggregate the data
      const [speakerStats, serMetrics, ragProcessing, mtValidation, transitionStats] = await Promise.allSettled([
        this.getSpeakerBucketStats(filters),
        this.getSERMetricsSummary(filters),
        this.getRAGProcessingSummary(filters),
        this.getMTValidationSummary(filters),
        this.getTransitionStatistics(filters),
      ]);

      // Build dashboard metrics from individual service responses
      const dashboardData: DashboardMetrics = {
        timestamp: new Date().toISOString(),
        speaker_statistics: speakerStats.status === 'fulfilled' ? speakerStats.value : null,
        ser_metrics: serMetrics.status === 'fulfilled' ? serMetrics.value : null,
        rag_processing: ragProcessing.status === 'fulfilled' ? ragProcessing.value : null,
        mt_validation: mtValidation.status === 'fulfilled' ? mtValidation.value : null,
        transition_statistics: transitionStats.status === 'fulfilled' ? transitionStats.value : null,
        services_status: {
          user_management: speakerStats.status === 'fulfilled' ? 'healthy' : 'error',
          verification: serMetrics.status === 'fulfilled' ? 'healthy' : 'error',
          rag_integration: ragProcessing.status === 'fulfilled' ? 'healthy' : 'error',
          mt_validation: mtValidation.status === 'fulfilled' ? 'healthy' : 'error',
        }
      };

      return dashboardData;
    } catch (error) {
      console.error('Failed to get dashboard overview from direct services:', error);
      throw error;
    }
  }

  /**
   * Get speaker bucket statistics
   */
  async getSpeakerBucketStats(filters?: DashboardFilters): Promise<SpeakerBucketStats> {
    try {
      // Try API Gateway first
      const params = this.buildFilterParams(filters);
      return await this.get<SpeakerBucketStats>(`${this.basePath}/speaker-statistics?${params.toString()}`);
    } catch (error) {
      // Fallback to direct service call via proxy
      return await this.get<SpeakerBucketStats>('/api/v1/speakers/statistics/buckets');
    }
  }

  /**
   * Get SER metrics summary
   */
  async getSERMetricsSummary(filters?: DashboardFilters): Promise<SERMetricsSummary> {
    try {
      // Try API Gateway first
      const params = this.buildFilterParams(filters);
      return await this.get<SERMetricsSummary>(`${this.basePath}/ser-metrics?${params.toString()}`);
    } catch (error) {
      // Fallback to direct service call via proxy (note the double prefix due to router configuration)
      return await this.get<SERMetricsSummary>('/api/v1/api/v1/ser/metrics/summary');
    }
  }

  /**
   * Get RAG processing summary
   */
  async getRAGProcessingSummary(filters?: DashboardFilters): Promise<RAGProcessingSummary> {
    try {
      // Try API Gateway first
      const params = this.buildFilterParams(filters);
      return await this.get<RAGProcessingSummary>(`${this.basePath}/rag-processing?${params.toString()}`);
    } catch (error) {
      // Fallback to direct service call via proxy (note the double prefix due to router configuration)
      return await this.get<RAGProcessingSummary>('/api/v1/api/v1/speaker-rag/statistics/summary');
    }
  }

  /**
   * Get MT validation summary
   */
  async getMTValidationSummary(filters?: DashboardFilters): Promise<MTValidationSummary> {
    try {
      // Try API Gateway first
      const params = this.buildFilterParams(filters);
      return await this.get<MTValidationSummary>(`${this.basePath}/mt-validation?${params.toString()}`);
    } catch (error) {
      // Fallback to direct service call via proxy (note the double prefix due to router configuration)
      return await this.get<MTValidationSummary>('/api/v1/api/v1/mt-validation/statistics/summary');
    }
  }

  /**
   * Get transition statistics
   */
  async getTransitionStatistics(filters?: DashboardFilters): Promise<TransitionStatisticsSummary> {
    try {
      // Try API Gateway first
      const params = this.buildFilterParams(filters);
      return await this.get<TransitionStatisticsSummary>(`${this.basePath}/transition-statistics?${params.toString()}`);
    } catch (error) {
      // Fallback to direct service call via proxy
      return await this.get<TransitionStatisticsSummary>('/api/v1/bucket-transitions/statistics/summary');
    }
  }

  /**
   * Get services health status
   */
  async getServicesHealth(): Promise<ServicesHealthStatus> {
    // Align with backend router path in src/api_gateway/speaker_bucket_management_router.py
    // The comprehensive health endpoint is exposed directly under
    // /api/v1/speaker-bucket-management/health/comprehensive
    const rootPath = '/api/v1/speaker-bucket-management';
    return this.get<ServicesHealthStatus>(`${rootPath}/health/comprehensive`);
  }

  /**
   * Get time series data for charts
   */
  async getTimeSeriesData(
    metric: string,
    filters?: DashboardFilters & {
      granularity?: 'hour' | 'day' | 'week' | 'month';
      aggregation?: 'sum' | 'avg' | 'min' | 'max' | 'count';
    }
  ): Promise<TimeSeriesData> {
    const params = this.buildFilterParams(filters);
    
    if (filters?.granularity) {
      params.append('granularity', filters.granularity);
    }
    if (filters?.aggregation) {
      params.append('aggregation', filters.aggregation);
    }

    return this.get<TimeSeriesData>(`${this.basePath}/charts/timeseries/${metric}?${params.toString()}`);
  }

  /**
   * Get pie chart data
   */
  async getPieChartData(
    metric: string,
    filters?: DashboardFilters
  ): Promise<PieChartData> {
    const params = this.buildFilterParams(filters);
    return this.get<PieChartData>(`${this.basePath}/charts/pie/${metric}?${params.toString()}`);
  }

  /**
   * Get bar chart data
   */
  async getBarChartData(
    metric: string,
    filters?: DashboardFilters & {
      groupBy?: string;
      limit?: number;
    }
  ): Promise<BarChartData> {
    const params = this.buildFilterParams(filters);
    
    if (filters?.groupBy) {
      params.append('group_by', filters.groupBy);
    }
    if (filters?.limit) {
      params.append('limit', filters.limit.toString());
    }

    return this.get<BarChartData>(`${this.basePath}/charts/bar/${metric}?${params.toString()}`);
  }

  /**
   * Get dashboard layouts
   */
  async getDashboardLayouts(): Promise<DashboardLayout[]> {
    return this.get<DashboardLayout[]>(`${this.basePath}/layouts`);
  }

  /**
   * Get specific dashboard layout
   */
  async getDashboardLayout(layoutId: string): Promise<DashboardLayout> {
    return this.get<DashboardLayout>(`${this.basePath}/layouts/${layoutId}`);
  }

  /**
   * Save dashboard layout
   */
  async saveDashboardLayout(layout: Omit<DashboardLayout, 'id' | 'createdAt' | 'updatedAt'>): Promise<DashboardLayout> {
    return this.post<DashboardLayout>(`${this.basePath}/layouts`, layout);
  }

  /**
   * Update dashboard layout
   */
  async updateDashboardLayout(layoutId: string, layout: Partial<DashboardLayout>): Promise<DashboardLayout> {
    return this.put<DashboardLayout>(`${this.basePath}/layouts/${layoutId}`, layout);
  }

  /**
   * Delete dashboard layout
   */
  async deleteDashboardLayout(layoutId: string): Promise<void> {
    await this.delete(`${this.basePath}/layouts/${layoutId}`);
  }

  /**
   * Get dashboard alerts
   */
  async getDashboardAlerts(filters?: {
    severity?: string;
    acknowledged?: boolean;
    limit?: number;
  }): Promise<DashboardAlert[]> {
    const params = new URLSearchParams();
    
    if (filters?.severity) {
      params.append('severity', filters.severity);
    }
    if (filters?.acknowledged !== undefined) {
      params.append('acknowledged', filters.acknowledged.toString());
    }
    if (filters?.limit) {
      params.append('limit', filters.limit.toString());
    }

    return this.get<DashboardAlert[]>(`${this.basePath}/alerts?${params.toString()}`);
  }

  /**
   * Acknowledge dashboard alert
   */
  async acknowledgeAlert(alertId: string): Promise<DashboardAlert> {
    return this.post<DashboardAlert>(`${this.basePath}/alerts/${alertId}/acknowledge`);
  }

  /**
   * Get performance metrics
   */
  async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    return this.get<PerformanceMetrics>(`${this.basePath}/performance`);
  }

  /**
   * Generate dashboard report
   */
  async generateReport(reportConfig: {
    title: string;
    filters: DashboardFilters;
    widgets: string[];
    format: 'pdf' | 'excel' | 'csv';
  }): Promise<Blob> {
    const response = await fetch(
      `${this.baseURL}${this.basePath}/reports/generate`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(reportConfig),
      }
    );

    if (!response.ok) {
      throw new Error(`Report generation failed: ${response.statusText}`);
    }

    return response.blob();
  }

  /**
   * Get saved reports
   */
  async getSavedReports(): Promise<DashboardReport[]> {
    return this.get<DashboardReport[]>(`${this.basePath}/reports`);
  }

  /**
   * Save report configuration
   */
  async saveReportConfig(report: Omit<DashboardReport, 'id' | 'createdAt'>): Promise<DashboardReport> {
    return this.post<DashboardReport>(`${this.basePath}/reports`, report);
  }

  /**
   * Get drill-down data
   */
  async getDrillDownData(
    widget: string,
    filters: Record<string, any>
  ): Promise<any> {
    return this.post<any>(`${this.basePath}/drill-down/${widget}`, { filters });
  }

  /**
   * Get real-time updates (WebSocket simulation)
   */
  async subscribeToUpdates(
    callback: (update: any) => void,
    filters?: DashboardFilters
  ): Promise<() => void> {
    // In a real implementation, this would establish a WebSocket connection
    // For now, we'll simulate with polling
    const interval = setInterval(async () => {
      try {
        const metrics = await this.getDashboardOverview(filters);
        callback({
          type: 'dashboard_update',
          data: metrics,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        // Handle error silently or call error callback
      }
    }, 30000); // Poll every 30 seconds

    // Return unsubscribe function
    return () => clearInterval(interval);
  }

  /**
   * Export dashboard data
   */
  async exportDashboardData(
    format: 'json' | 'csv' | 'excel',
    filters?: DashboardFilters
  ): Promise<Blob> {
    const params = this.buildFilterParams(filters);
    params.append('format', format);

    const response = await fetch(
      `${this.baseURL}${this.basePath}/export?${params.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    return response.blob();
  }

  /**
   * Get dashboard configuration
   */
  async getDashboardConfig(): Promise<{
    refresh_intervals: number[];
    available_metrics: string[];
    chart_types: string[];
    export_formats: string[];
  }> {
    return this.get(`${this.basePath}/config`);
  }

  /**
   * Helper method to build filter parameters
   */
  private buildFilterParams(filters?: DashboardFilters): URLSearchParams {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.dateRange) {
        params.append('start_date', filters.dateRange.start);
        params.append('end_date', filters.dateRange.end);
        if (filters.dateRange.preset) {
          params.append('date_preset', filters.dateRange.preset);
        }
      }
      if (filters.speakers?.length) {
        params.append('speakers', filters.speakers.join(','));
      }
      if (filters.buckets?.length) {
        params.append('buckets', filters.buckets.join(','));
      }
      if (filters.services?.length) {
        params.append('services', filters.services.join(','));
      }
      if (filters.mtUsers?.length) {
        params.append('mt_users', filters.mtUsers.join(','));
      }
    }

    return params;
  }
}

// Create singleton instance
export const dashboardApi = new DashboardApi();
