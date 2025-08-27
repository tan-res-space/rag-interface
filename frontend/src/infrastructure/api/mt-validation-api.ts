/**
 * MT Validation API client
 */

import { BaseApi } from './base-api';
import {
  ValidationSession,
  ValidationTestData,
  MTFeedback,
  ValidationItem,
  StartValidationSessionRequest,
  SubmitMTFeedbackRequest,
  CompleteValidationSessionRequest,
  ValidationSessionSummary,
  MTUserStatistics,
  MTValidationFilters,
  ValidationAnalytics,
  ValidationExportData,
  SERComparison
} from '@/domain/types/mt-validation';

export class MTValidationApi extends BaseApi {
  private readonly basePath = '/api/v1/mt-validation';

  /**
   * Start a new MT validation session
   */
  async startValidationSession(request: StartValidationSessionRequest): Promise<ValidationSession> {
    return this.post<ValidationSession>(`${this.basePath}/sessions`, request);
  }

  /**
   * Get validation session by ID
   */
  async getValidationSession(sessionId: string): Promise<ValidationSession> {
    return this.get<ValidationSession>(`${this.basePath}/sessions/${sessionId}`);
  }

  /**
   * Get test data for validation session
   */
  async getValidationTestData(
    sessionId: string,
    limit?: number
  ): Promise<ValidationTestData[]> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    
    return this.get<ValidationTestData[]>(
      `${this.basePath}/sessions/${sessionId}/test-data?${params.toString()}`
    );
  }

  /**
   * Submit MT feedback for validation item
   */
  async submitMTFeedback(
    sessionId: string,
    feedback: SubmitMTFeedbackRequest
  ): Promise<MTFeedback> {
    return this.post<MTFeedback>(
      `${this.basePath}/sessions/${sessionId}/feedback`,
      feedback
    );
  }

  /**
   * Complete validation session
   */
  async completeValidationSession(
    sessionId: string,
    request: CompleteValidationSessionRequest
  ): Promise<ValidationSession> {
    return this.post<ValidationSession>(
      `${this.basePath}/sessions/${sessionId}/complete`,
      request
    );
  }

  /**
   * Get validation sessions with filters
   */
  async getValidationSessions(filters: MTValidationFilters = {}): Promise<ValidationSession[]> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    return this.get<ValidationSession[]>(`${this.basePath}/sessions?${params.toString()}`);
  }

  /**
   * Get session feedback
   */
  async getSessionFeedback(sessionId: string): Promise<MTFeedback[]> {
    return this.get<MTFeedback[]>(`${this.basePath}/sessions/${sessionId}/feedback`);
  }

  /**
   * Get SER comparison for speaker
   */
  async getSERComparison(request: {
    speaker_id: string;
    historical_data_ids: string[];
    include_individual_metrics?: boolean;
    include_summary_statistics?: boolean;
  }): Promise<SERComparison> {
    return this.post<SERComparison>(`${this.basePath}/ser-comparison`, request);
  }

  /**
   * Get validation session summary
   */
  async getValidationSessionSummary(sessionId: string): Promise<ValidationSessionSummary> {
    return this.get<ValidationSessionSummary>(`${this.basePath}/sessions/${sessionId}/summary`);
  }

  /**
   * Get MT user statistics
   */
  async getMTUserStatistics(mtUserId: string): Promise<MTUserStatistics> {
    return this.get<MTUserStatistics>(`${this.basePath}/statistics/mt-user/${mtUserId}`);
  }

  /**
   * Get validation analytics for session
   */
  async getValidationAnalytics(sessionId: string): Promise<ValidationAnalytics> {
    return this.get<ValidationAnalytics>(`${this.basePath}/sessions/${sessionId}/analytics`);
  }

  /**
   * Export validation session data
   */
  async exportValidationSession(
    sessionId: string,
    format: 'csv' | 'excel' | 'pdf' | 'json' = 'csv'
  ): Promise<Blob> {
    const response = await fetch(
      `${this.baseURL}${this.basePath}/sessions/${sessionId}/export?format=${format}`,
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
   * Get validation item by ID
   */
  async getValidationItem(sessionId: string, itemId: string): Promise<ValidationItem> {
    return this.get<ValidationItem>(`${this.basePath}/sessions/${sessionId}/items/${itemId}`);
  }

  /**
   * Update validation item status
   */
  async updateValidationItemStatus(
    sessionId: string,
    itemId: string,
    status: string
  ): Promise<ValidationItem> {
    return this.put<ValidationItem>(
      `${this.basePath}/sessions/${sessionId}/items/${itemId}/status`,
      { status }
    );
  }

  /**
   * Skip validation item
   */
  async skipValidationItem(
    sessionId: string,
    itemId: string,
    reason?: string
  ): Promise<ValidationItem> {
    return this.post<ValidationItem>(
      `${this.basePath}/sessions/${sessionId}/items/${itemId}/skip`,
      { reason }
    );
  }

  /**
   * Get validation statistics summary
   */
  async getValidationStatistics(): Promise<any> {
    return this.get<any>(`${this.basePath}/statistics/summary`);
  }

  /**
   * Pause validation session
   */
  async pauseValidationSession(sessionId: string): Promise<ValidationSession> {
    return this.post<ValidationSession>(`${this.basePath}/sessions/${sessionId}/pause`);
  }

  /**
   * Resume validation session
   */
  async resumeValidationSession(sessionId: string): Promise<ValidationSession> {
    return this.post<ValidationSession>(`${this.basePath}/sessions/${sessionId}/resume`);
  }

  /**
   * Cancel validation session
   */
  async cancelValidationSession(
    sessionId: string,
    reason?: string
  ): Promise<ValidationSession> {
    return this.post<ValidationSession>(
      `${this.basePath}/sessions/${sessionId}/cancel`,
      { reason }
    );
  }

  /**
   * Get validation progress
   */
  async getValidationProgress(sessionId: string): Promise<{
    session_id: string;
    total_items: number;
    completed_items: number;
    progress_percentage: number;
    estimated_time_remaining_minutes: number;
    current_item_index: number;
  }> {
    return this.get(`${this.basePath}/sessions/${sessionId}/progress`);
  }

  /**
   * Save validation preferences
   */
  async saveValidationPreferences(
    mtUserId: string,
    preferences: Record<string, any>
  ): Promise<void> {
    await this.post(`${this.basePath}/users/${mtUserId}/preferences`, preferences);
  }

  /**
   * Get validation preferences
   */
  async getValidationPreferences(mtUserId: string): Promise<Record<string, any>> {
    return this.get(`${this.basePath}/users/${mtUserId}/preferences`);
  }

  /**
   * Calculate text differences
   */
  async calculateTextDifferences(
    originalText: string,
    correctedText: string,
    options?: {
      algorithm?: 'myers' | 'patience' | 'histogram';
      context_lines?: number;
      ignore_whitespace?: boolean;
    }
  ): Promise<Array<{
    type: 'equal' | 'insert' | 'delete' | 'replace';
    originalText: string;
    correctedText: string;
    position: { start: number; end: number };
  }>> {
    return this.post(`${this.basePath}/text-differences`, {
      original_text: originalText,
      corrected_text: correctedText,
      options: options || {}
    });
  }

  /**
   * Get validation templates
   */
  async getValidationTemplates(): Promise<Array<{
    template_id: string;
    name: string;
    description: string;
    default_settings: Record<string, any>;
  }>> {
    return this.get(`${this.basePath}/templates`);
  }

  /**
   * Create validation template
   */
  async createValidationTemplate(template: {
    name: string;
    description: string;
    settings: Record<string, any>;
  }): Promise<any> {
    return this.post(`${this.basePath}/templates`, template);
  }

  /**
   * Health check for MT validation service
   */
  async checkHealth(): Promise<any> {
    return this.get(`${this.basePath}/health/check`);
  }

  /**
   * Get real-time session updates (WebSocket simulation)
   */
  async subscribeToSessionUpdates(
    sessionId: string,
    callback: (update: any) => void
  ): Promise<() => void> {
    // In a real implementation, this would establish a WebSocket connection
    // For now, we'll simulate with polling
    const interval = setInterval(async () => {
      try {
        const progress = await this.getValidationProgress(sessionId);
        callback({
          type: 'progress_update',
          data: progress,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        // Handle error silently or call error callback
      }
    }, 5000); // Poll every 5 seconds

    // Return unsubscribe function
    return () => clearInterval(interval);
  }
}

// Create singleton instance
export const mtValidationApi = new MTValidationApi();
