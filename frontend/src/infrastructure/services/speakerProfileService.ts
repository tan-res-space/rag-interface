/**
 * Speaker Profile Service
 * Handles API calls for speaker profile management and bucket progression
 */

import { apiClient } from './apiClient';
import type {
  SpeakerProfile,
  BucketChangeLog,
  BucketProgressionResponse,
  BucketStatistics,
  BucketType
} from '@domain/types';

export interface SpeakerProfileService {
  getSpeakerProfile(speakerId: string): Promise<SpeakerProfile>;
  getBucketChangeHistory(speakerId: string, limit?: number): Promise<{ speaker_id: string; total_changes: number; history: BucketChangeLog[] }>;
  evaluateSpeakerProgression(speakerId: string, forceEvaluation?: boolean): Promise<BucketProgressionResponse>;
  batchEvaluateProgression(maxProfiles?: number, forceEvaluation?: boolean): Promise<{
    total_profiles_evaluated: number;
    bucket_changes_applied: number;
    evaluation_timestamp: string;
    results_summary: Array<{
      speaker_id: string;
      bucket_changed: boolean;
      old_bucket?: string;
      new_bucket?: string;
      confidence_score: number;
    }>;
  }>;
  getBucketStatistics(): Promise<BucketStatistics>;
  getBucketTypes(): Promise<{
    bucket_types: Record<string, {
      label: string;
      description: string;
      color: string;
      icon: string;
    }>;
    progression_order: string[];
    total_levels: number;
  }>;
}

class SpeakerProfileServiceImpl implements SpeakerProfileService {
  private readonly baseUrl = '/api/v1/speakers';

  async getSpeakerProfile(speakerId: string): Promise<SpeakerProfile> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${speakerId}/profile`);
      return response.data;
    } catch (error) {
      console.error('Error fetching speaker profile:', error);
      throw new Error('Failed to fetch speaker profile');
    }
  }

  async getBucketChangeHistory(
    speakerId: string, 
    limit: number = 50
  ): Promise<{ speaker_id: string; total_changes: number; history: BucketChangeLog[] }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${speakerId}/bucket-history`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching bucket change history:', error);
      throw new Error('Failed to fetch bucket change history');
    }
  }

  async evaluateSpeakerProgression(
    speakerId: string, 
    forceEvaluation: boolean = false
  ): Promise<BucketProgressionResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/${speakerId}/evaluate-progression`, null, {
        params: { force_evaluation: forceEvaluation }
      });
      return response.data;
    } catch (error) {
      console.error('Error evaluating speaker progression:', error);
      throw new Error('Failed to evaluate speaker progression');
    }
  }

  async batchEvaluateProgression(
    maxProfiles: number = 100, 
    forceEvaluation: boolean = false
  ): Promise<{
    total_profiles_evaluated: number;
    bucket_changes_applied: number;
    evaluation_timestamp: string;
    results_summary: Array<{
      speaker_id: string;
      bucket_changed: boolean;
      old_bucket?: string;
      new_bucket?: string;
      confidence_score: number;
    }>;
  }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/batch-evaluate`, null, {
        params: { 
          max_profiles: maxProfiles,
          force_evaluation: forceEvaluation 
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error during batch evaluation:', error);
      throw new Error('Failed to perform batch evaluation');
    }
  }

  async getBucketStatistics(): Promise<BucketStatistics> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/bucket-statistics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching bucket statistics:', error);
      throw new Error('Failed to fetch bucket statistics');
    }
  }

  async getBucketTypes(): Promise<{
    bucket_types: Record<string, {
      label: string;
      description: string;
      color: string;
      icon: string;
    }>;
    progression_order: string[];
    total_levels: number;
  }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/bucket-types`);
      return response.data;
    } catch (error) {
      console.error('Error fetching bucket types:', error);
      throw new Error('Failed to fetch bucket types');
    }
  }
}

// Create and export service instance
export const speakerProfileService: SpeakerProfileService = new SpeakerProfileServiceImpl();

// Helper functions for bucket progression
export const bucketProgressionHelpers = {
  /**
   * Get bucket color for UI display
   */
  getBucketColor(bucketType: BucketType): string {
    const colors = {
      beginner: '#f44336',    // Red
      intermediate: '#ff9800', // Orange
      advanced: '#2196f3',    // Blue
      expert: '#4caf50'       // Green
    };
    return colors[bucketType] || '#757575';
  },

  /**
   * Get bucket icon for UI display
   */
  getBucketIcon(bucketType: BucketType): string {
    const icons = {
      beginner: '🌱',
      intermediate: '🌿',
      advanced: '🌳',
      expert: '🏆'
    };
    return icons[bucketType] || '📊';
  },

  /**
   * Get bucket display name
   */
  getBucketDisplayName(bucketType: BucketType): string {
    const names = {
      beginner: 'Beginner',
      intermediate: 'Intermediate',
      advanced: 'Advanced',
      expert: 'Expert'
    };
    return names[bucketType] || bucketType;
  },

  /**
   * Get bucket level (0-3) for comparison
   */
  getBucketLevel(bucketType: BucketType): number {
    const levels = {
      beginner: 0,
      intermediate: 1,
      advanced: 2,
      expert: 3
    };
    return levels[bucketType] || 0;
  },

  /**
   * Check if bucket change is a promotion
   */
  isPromotion(oldBucket: BucketType, newBucket: BucketType): boolean {
    return this.getBucketLevel(newBucket) > this.getBucketLevel(oldBucket);
  },

  /**
   * Check if bucket change is a demotion
   */
  isDemotion(oldBucket: BucketType, newBucket: BucketType): boolean {
    return this.getBucketLevel(newBucket) < this.getBucketLevel(oldBucket);
  },

  /**
   * Format bucket progression message
   */
  formatProgressionMessage(oldBucket: BucketType, newBucket: BucketType, reason: string): string {
    const isPromotion = this.isPromotion(oldBucket, newBucket);
    const action = isPromotion ? 'promoted to' : 'moved to';
    const oldName = this.getBucketDisplayName(oldBucket);
    const newName = this.getBucketDisplayName(newBucket);
    
    return `You've been ${action} ${newName} level from ${oldName}. ${reason}`;
  },

  /**
   * Get next bucket level for progression display
   */
  getNextBucket(currentBucket: BucketType): BucketType | null {
    const progression = {
      beginner: 'intermediate' as BucketType,
      intermediate: 'advanced' as BucketType,
      advanced: 'expert' as BucketType,
      expert: null
    };
    return progression[currentBucket] || null;
  },

  /**
   * Calculate progress percentage to next level
   */
  calculateProgressPercentage(
    currentLevel: number,
    currentErrorRate: number,
    targetErrorRate: number
  ): number {
    if (currentErrorRate <= targetErrorRate) {
      return 100;
    }
    
    // Simple calculation based on error rate improvement needed
    const maxErrorRate = 0.2; // Assume 20% is the starting point
    const progress = Math.max(0, (maxErrorRate - currentErrorRate) / (maxErrorRate - targetErrorRate) * 100);
    return Math.min(100, progress);
  }
};
