/**
 * Comprehensive Error Handling Types
 * 
 * Defines types for the global error handling system that covers
 * all error types in the application with rich context and user-friendly messaging.
 */

export type ErrorType = 'api' | 'runtime' | 'component' | 'validation' | 'network';

export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface ErrorContext {
  /** Current URL where error occurred */
  url: string;
  
  /** User agent string */
  userAgent: string;
  
  /** Current user ID if authenticated */
  userId?: string;
  
  /** React component stack trace (for component errors) */
  componentStack?: string;
  
  /** API endpoint that failed (for API errors) */
  apiEndpoint?: string;
  
  /** HTTP status code (for API/network errors) */
  statusCode?: number;
  
  /** Recent user actions leading to error */
  userActions?: string[];
  
  /** Additional context data */
  additionalData?: Record<string, any>;
  
  /** Browser/environment information */
  environment?: {
    viewport: { width: number; height: number };
    platform: string;
    language: string;
    cookieEnabled: boolean;
    onLine: boolean;
  };
}

export interface AppError {
  /** Unique error identifier */
  id: string;
  
  /** Type of error for categorization */
  type: ErrorType;
  
  /** Technical error message */
  message: string;
  
  /** User-friendly error message */
  userFriendlyMessage: string;
  
  /** JavaScript stack trace */
  stack?: string;
  
  /** When the error occurred */
  timestamp: Date;
  
  /** Rich context about the error */
  context: ErrorContext;
  
  /** Error severity level */
  severity: ErrorSeverity;
  
  /** Whether error has been acknowledged by user */
  acknowledged?: boolean;
  
  /** Whether error details are currently shown */
  detailsVisible?: boolean;
  
  /** Original error object if available */
  originalError?: Error;
}

export interface ErrorState {
  /** Queue of all errors */
  errors: AppError[];
  
  /** Currently active/displayed error */
  activeError: AppError | null;
  
  /** Whether error details panel is shown */
  showErrorDetails: boolean;
  
  /** Whether error details panel is expanded */
  errorDetailsExpanded: boolean;
  
  /** Global error handling enabled */
  errorHandlingEnabled: boolean;
  
  /** Error display preferences */
  displayPreferences: {
    /** Show technical details in production */
    showTechnicalDetailsInProduction: boolean;
    
    /** Auto-dismiss low severity errors */
    autoDismissLowSeverity: boolean;
    
    /** Auto-dismiss timeout in milliseconds */
    autoDismissTimeout: number;
  };
}

export interface ErrorDisplayProps {
  /** Error to display */
  error: AppError;
  
  /** Whether to show the "Show Details" button */
  showDetailsButton?: boolean;
  
  /** Custom action buttons */
  actions?: React.ReactNode;
  
  /** Callback when error is dismissed */
  onDismiss?: (errorId: string) => void;
  
  /** Callback when details are toggled */
  onToggleDetails?: (errorId: string) => void;
}

export interface ErrorDetailsPanelProps {
  /** Error to show details for */
  error: AppError | null;
  
  /** Whether panel is open */
  open: boolean;
  
  /** Whether panel is expanded */
  expanded: boolean;
  
  /** Callback when panel is closed */
  onClose: () => void;
  
  /** Callback when panel expansion is toggled */
  onToggleExpanded: () => void;
  
  /** Callback when error details are copied */
  onCopyDetails?: (error: AppError) => void;
}

export interface ErrorHandlerConfig {
  /** Whether to capture window errors */
  captureWindowErrors: boolean;
  
  /** Whether to capture unhandled promise rejections */
  captureUnhandledRejections: boolean;
  
  /** Whether to capture console errors */
  captureConsoleErrors: boolean;
  
  /** Maximum number of errors to keep in queue */
  maxErrorQueueSize: number;
  
  /** Whether to log errors to console */
  logToConsole: boolean;
  
  /** Custom error transformation function */
  transformError?: (error: Error, context: Partial<ErrorContext>) => Partial<AppError>;
  
  /** Custom error filtering function */
  filterError?: (error: Error) => boolean;
}

export interface UserActionTracker {
  /** Track a user action */
  trackAction: (action: string, data?: any) => void;
  
  /** Get recent actions */
  getRecentActions: (limit?: number) => string[];
  
  /** Clear action history */
  clearActions: () => void;
}

// Utility types for error creation
export type CreateErrorInput = Omit<AppError, 'id' | 'timestamp' | 'context'> & {
  context?: Partial<ErrorContext>;
};

export type ErrorTransformer = (error: Error, type: ErrorType, context?: Partial<ErrorContext>) => AppError;

// Error severity mapping for different error types
export const DEFAULT_ERROR_SEVERITY: Record<ErrorType, ErrorSeverity> = {
  validation: 'low',
  api: 'medium',
  network: 'medium',
  runtime: 'high',
  component: 'high',
};

// User-friendly error messages by type
export const DEFAULT_USER_FRIENDLY_MESSAGES: Record<ErrorType, string> = {
  validation: 'Please check your input and try again.',
  api: 'We encountered an issue while processing your request. Please try again.',
  network: 'Unable to connect to our servers. Please check your internet connection.',
  runtime: 'An unexpected error occurred. Please refresh the page.',
  component: 'A component failed to load properly. Please refresh the page.',
};
