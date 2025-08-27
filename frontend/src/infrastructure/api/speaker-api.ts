/**
 * Speaker management API client
 */

import { BaseApi } from './base-api';
import {
  Speaker,
  SpeakerListResponse,
  SpeakerSearchParams,
  SpeakerFormData,
  BucketTransitionRequest,
  CreateTransitionRequest,
  TransitionRequestFormData,
  SpeakerBucketStats,
  ComprehensiveSpeakerView,
  DashboardMetrics,
  ApiResponse,
  PaginatedResponse
} from '@/domain/types/speaker';

export class SpeakerApi extends BaseApi {
  private readonly basePath = '/api/v1';

  /**
   * Search speakers with filters and pagination
   */
  async searchSpeakers(params: SpeakerSearchParams = {}): Promise<SpeakerListResponse> {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    const response = await this.get<SpeakerListResponse>(
      `${this.basePath}/speakers?${queryParams.toString()}`
    );
    
    return response;
  }

  /**
   * Get speaker by ID
   */
  async getSpeakerById(speakerId: string): Promise<Speaker> {
    return this.get<Speaker>(`${this.basePath}/speakers/${speakerId}`);
  }

  /**
   * Get speaker by external identifier
   */
  async getSpeakerByIdentifier(identifier: string): Promise<Speaker> {
    return this.get<Speaker>(`${this.basePath}/speakers/identifier/${identifier}`);
  }

  /**
   * Create a new speaker
   */
  async createSpeaker(speakerData: SpeakerFormData): Promise<Speaker> {
    return this.post<Speaker>(`${this.basePath}/speakers`, speakerData);
  }

  /**
   * Update speaker information
   */
  async updateSpeaker(speakerId: string, speakerData: Partial<SpeakerFormData>): Promise<Speaker> {
    return this.put<Speaker>(`${this.basePath}/speakers/${speakerId}`, speakerData);
  }

  /**
   * Get speakers by bucket
   */
  async getSpeakersByBucket(bucket: string): Promise<Speaker[]> {
    return this.get<Speaker[]>(`${this.basePath}/speakers/bucket/${bucket}`);
  }

  /**
   * Get speakers needing transition
   */
  async getSpeakersNeedingTransition(): Promise<Speaker[]> {
    return this.get<Speaker[]>(`${this.basePath}/speakers/transitions/needed`);
  }

  /**
   * Update speaker statistics
   */
  async updateSpeakerStatistics(speakerId: string): Promise<Speaker> {
    return this.post<Speaker>(`${this.basePath}/speakers/${speakerId}/statistics/update`);
  }

  /**
   * Get bucket statistics
   */
  async getBucketStatistics(): Promise<SpeakerBucketStats> {
    return this.get<SpeakerBucketStats>(`${this.basePath}/speakers/statistics/buckets`);
  }

  // Bucket Transition Management

  /**
   * Create bucket transition request
   */
  async createTransitionRequest(requestData: CreateTransitionRequest): Promise<BucketTransitionRequest> {
    return this.post<BucketTransitionRequest>(`${this.basePath}/bucket-transitions`, requestData);
  }

  /**
   * Get transition requests with filters
   */
  async getTransitionRequests(params: {
    status?: string;
    speaker_id?: string;
    urgent_only?: boolean;
    limit?: number;
  } = {}): Promise<BucketTransitionRequest[]> {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    return this.get<BucketTransitionRequest[]>(
      `${this.basePath}/bucket-transitions?${queryParams.toString()}`
    );
  }

  /**
   * Get pending transition requests
   */
  async getPendingTransitionRequests(): Promise<BucketTransitionRequest[]> {
    return this.get<BucketTransitionRequest[]>(`${this.basePath}/bucket-transitions/pending`);
  }

  /**
   * Get transition request by ID
   */
  async getTransitionRequestById(requestId: string): Promise<BucketTransitionRequest> {
    return this.get<BucketTransitionRequest>(`${this.basePath}/bucket-transitions/${requestId}`);
  }

  /**
   * Approve transition request
   */
  async approveTransitionRequest(
    requestId: string, 
    approvalData: { approved_by: string; approval_notes?: string }
  ): Promise<BucketTransitionRequest> {
    return this.post<BucketTransitionRequest>(
      `${this.basePath}/bucket-transitions/${requestId}/approve`,
      approvalData
    );
  }

  /**
   * Reject transition request
   */
  async rejectTransitionRequest(
    requestId: string,
    rejectionData: { rejected_by: string; rejection_reason: string }
  ): Promise<BucketTransitionRequest> {
    return this.post<BucketTransitionRequest>(
      `${this.basePath}/bucket-transitions/${requestId}/reject`,
      rejectionData
    );
  }

  /**
   * Get speaker transition history
   */
  async getSpeakerTransitionHistory(speakerId: string, limit: number = 50): Promise<BucketTransitionRequest[]> {
    return this.get<BucketTransitionRequest[]>(
      `${this.basePath}/bucket-transitions/speaker/${speakerId}/history?limit=${limit}`
    );
  }

  /**
   * Get transition statistics
   */
  async getTransitionStatistics(): Promise<any> {
    return this.get<any>(`${this.basePath}/bucket-transitions/statistics/summary`);
  }

  // Comprehensive Views and Analytics

  /**
   * Get comprehensive speaker view (API Gateway)
   */
  async getComprehensiveSpeakerView(
    speakerId: string,
    options: {
      include_ser_analysis?: boolean;
      include_error_patterns?: boolean;
      include_transition_history?: boolean;
    } = {}
  ): Promise<ComprehensiveSpeakerView> {
    const queryParams = new URLSearchParams();
    
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });

    // This would call the API Gateway endpoint
    return this.get<ComprehensiveSpeakerView>(
      `/api/v1/speaker-bucket-management/speakers/${speakerId}/comprehensive?${queryParams.toString()}`
    );
  }

  /**
   * Get dashboard overview (API Gateway)
   */
  async getDashboardOverview(): Promise<DashboardMetrics> {
    return this.get<DashboardMetrics>('/api/v1/speaker-bucket-management/dashboard/overview');
  }

  /**
   * Complete speaker assessment workflow (API Gateway)
   */
  async completeAssessmentWorkflow(
    speakerId: string,
    options: {
      include_mt_validation?: boolean;
      auto_approve_transitions?: boolean;
    } = {}
  ): Promise<any> {
    const queryParams = new URLSearchParams();
    
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });

    return this.post<any>(
      `/api/v1/speaker-bucket-management/workflows/complete-assessment?speaker_id=${speakerId}&${queryParams.toString()}`
    );
  }

  // Health and Status

  /**
   * Check speaker management health
   */
  async checkHealth(): Promise<any> {
    return this.get<any>(`${this.basePath}/speakers/health/check`);
  }

  /**
   * Get comprehensive health check (API Gateway)
   */
  async getComprehensiveHealth(): Promise<any> {
    return this.get<any>('/api/v1/speaker-bucket-management/health/comprehensive');
  }

  // Utility methods

  /**
   * Get quick filter options with counts
   */
  async getQuickFilterOptions(): Promise<Array<{
    label: string;
    value: string;
    count: number;
    filters: any;
  }>> {
    // This could be implemented as a separate endpoint or computed from bucket statistics
    const stats = await this.getBucketStatistics();
    
    return [
      {
        label: 'All Speakers',
        value: 'all',
        count: stats.total_speakers,
        filters: {}
      },
      {
        label: 'High Touch',
        value: 'high_touch',
        count: stats.bucket_distribution.HIGH_TOUCH || 0,
        filters: { bucket: 'HIGH_TOUCH' }
      },
      {
        label: 'Medium Touch',
        value: 'medium_touch',
        count: stats.bucket_distribution.MEDIUM_TOUCH || 0,
        filters: { bucket: 'MEDIUM_TOUCH' }
      },
      {
        label: 'Low Touch',
        value: 'low_touch',
        count: stats.bucket_distribution.LOW_TOUCH || 0,
        filters: { bucket: 'LOW_TOUCH' }
      },
      {
        label: 'No Touch',
        value: 'no_touch',
        count: stats.bucket_distribution.NO_TOUCH || 0,
        filters: { bucket: 'NO_TOUCH' }
      },
      {
        label: 'Needs Transition',
        value: 'needs_transition',
        count: stats.transition_metrics.pending_transitions || 0,
        filters: { should_transition: true }
      },
      {
        label: 'Insufficient Data',
        value: 'insufficient_data',
        count: stats.total_speakers - stats.data_quality.speakers_with_sufficient_data,
        filters: { has_sufficient_data: false }
      }
    ];
  }

  /**
   * Export speakers data
   */
  async exportSpeakers(filters: SpeakerSearchParams = {}): Promise<Blob> {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    // Add export format
    queryParams.append('format', 'csv');

    const response = await fetch(
      `${this.baseURL}${this.basePath}/speakers/export?${queryParams.toString()}`,
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
}

// Create singleton instance
export const speakerApi = new SpeakerApi();
