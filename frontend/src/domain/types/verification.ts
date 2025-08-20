/**
 * Verification domain types based on Verification Service schemas
 */

export enum VerificationStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  NEEDS_REVIEW = 'needs_review',
}

export enum ReportFormat {
  PDF = 'pdf',
  EXCEL = 'excel',
  CSV = 'csv',
  JSON = 'json',
}

export interface VerificationItem {
  id: string;
  correctionId: string;
  originalText: string;
  correctedText: string;
  confidenceScore: number;
  errorCategories: string[];
  speakerId: string;
  jobId: string;
  createdAt: string;
  priority: string;
}

export interface VerificationRequest {
  status: VerificationStatus;
  feedback?: string;
  qualityScore: number; // 1-5 scale
  notes?: string;
}

export interface VerificationResponse {
  id: string;
  correctionId: string;
  status: VerificationStatus;
  feedback?: string;
  qualityScore?: number;
  notes?: string;
  verifiedBy: string;
  verifiedAt: string;
  createdAt: string;
}

export interface QualityMetrics {
  totalVerifications: number;
  approvalRate: number;
  rejectionRate: number;
  averageQualityScore: number;
  averageProcessingTime: number;
  accuracyTrend: Array<{
    date: string;
    accuracy: number;
  }>;
}

export interface DashboardSummary {
  period: string;
  qualityMetrics: QualityMetrics;
  topErrorCategories: Array<{
    category: string;
    count: number;
    percentage: number;
  }>;
  speakerPerformance: Array<{
    speakerId: string;
    speakerName: string;
    accuracy: number;
    totalJobs: number;
  }>;
  recentActivity: Array<{
    id: string;
    type: string;
    description: string;
    timestamp: string;
    user: string;
  }>;
  alerts: Array<{
    id: string;
    type: 'warning' | 'error' | 'info';
    message: string;
    timestamp: string;
    isRead: boolean;
  }>;
}

export interface VerificationFilters {
  statuses?: VerificationStatus[];
  speakerIds?: string[];
  jobIds?: string[];
  errorCategories?: string[];
  qualityScoreRange?: {
    min: number;
    max: number;
  };
  confidenceScoreRange?: {
    min: number;
    max: number;
  };
  dateRange?: {
    startDate: string;
    endDate: string;
  };
  verifiedBy?: string[];
}

export interface BulkVerificationRequest {
  verificationIds: string[];
  action: VerificationStatus;
  feedback?: string;
  qualityScore?: number;
  notes?: string;
}

export interface ComparisonView {
  before: {
    text: string;
    highlights: Array<{
      start: number;
      end: number;
      type: 'error' | 'correction';
    }>;
  };
  after: {
    text: string;
    highlights: Array<{
      start: number;
      end: number;
      type: 'error' | 'correction';
    }>;
  };
  changes: Array<{
    type: 'addition' | 'deletion' | 'modification';
    position: number;
    originalText: string;
    newText: string;
  }>;
}
