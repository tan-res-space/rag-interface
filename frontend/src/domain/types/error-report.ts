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

export interface ErrorReport {
  errorId: string;
  jobId: string;
  speakerId: string;
  reportedBy: string;
  originalText: string;
  correctedText: string;
  errorCategories: string[];
  severityLevel: SeverityLevel;
  startPosition: number;
  endPosition: number;
  contextNotes?: string;
  errorTimestamp: string;
  reportedAt: string;
  status: ErrorStatus;
  metadata?: Record<string, any>;
}

export interface SubmitErrorReportRequest {
  jobId: string;
  speakerId: string;
  originalText: string;
  correctedText: string;
  errorCategories: string[];
  severityLevel: SeverityLevel;
  startPosition: number;
  endPosition: number;
  reportedBy: string;
  contextNotes?: string;
  metadata?: Record<string, any>;
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
  requestedBy: string;
  filters: ErrorFilters;
  pagination: {
    page: number;
    pageSize: number;
  };
  sort: {
    field: string;
    direction: 'asc' | 'desc';
  };
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
