/**
 * Global Error Handler Service
 * 
 * Centralized error handling service that captures all types of errors
 * in the application and transforms them into standardized AppError objects.
 * Provides comprehensive error context collection and integration with Redux state.
 */

import { store } from '@/app/store';
import { addError, addNotification } from '@shared/slices/ui-slice';
import {
  AppError,
  ErrorType,
  ErrorContext,
  ErrorHandlerConfig,
  CreateErrorInput,
  DEFAULT_ERROR_SEVERITY,
  DEFAULT_USER_FRIENDLY_MESSAGES,
} from '@shared/types/error.types';

class GlobalErrorHandler {
  private config: ErrorHandlerConfig;
  private userActions: string[] = [];
  private isInitialized = false;

  constructor(config: Partial<ErrorHandlerConfig> = {}) {
    this.config = {
      captureWindowErrors: true,
      captureUnhandledRejections: true,
      captureConsoleErrors: false,
      maxErrorQueueSize: 50,
      logToConsole: true,
      ...config,
    };
  }

  /**
   * Initialize the global error handler
   */
  initialize(): void {
    if (this.isInitialized) {
      return;
    }

    if (this.config.captureWindowErrors) {
      this.setupWindowErrorHandler();
    }

    if (this.config.captureUnhandledRejections) {
      this.setupUnhandledRejectionHandler();
    }

    if (this.config.captureConsoleErrors) {
      this.setupConsoleErrorHandler();
    }

    this.isInitialized = true;
    console.log('GlobalErrorHandler initialized');
  }

  /**
   * Manually report an error
   */
  reportError(
    error: Error | string,
    type: ErrorType = 'runtime',
    context: Partial<ErrorContext> = {}
  ): void {
    const errorObj = typeof error === 'string' ? new Error(error) : error;
    const appError = this.createAppError(errorObj, type, context);
    this.handleError(appError);
  }

  /**
   * Track user actions for error context
   */
  trackUserAction(action: string, data?: any): void {
    const timestamp = new Date().toISOString();
    const actionString = data 
      ? `${timestamp}: ${action} - ${JSON.stringify(data)}`
      : `${timestamp}: ${action}`;
    
    this.userActions.push(actionString);
    
    // Keep only recent actions
    if (this.userActions.length > 20) {
      this.userActions = this.userActions.slice(-20);
    }
  }

  /**
   * Get recent user actions
   */
  getRecentUserActions(limit: number = 10): string[] {
    return this.userActions.slice(-limit);
  }

  /**
   * Clear user action history
   */
  clearUserActions(): void {
    this.userActions = [];
  }

  /**
   * Create standardized AppError from Error object
   */
  private createAppError(
    error: Error,
    type: ErrorType,
    contextOverrides: Partial<ErrorContext> = {}
  ): AppError {
    const context = this.collectErrorContext(contextOverrides);
    const severity = DEFAULT_ERROR_SEVERITY[type];
    const userFriendlyMessage = this.getUserFriendlyMessage(error, type);

    const appError: AppError = {
      id: this.generateErrorId(),
      type,
      message: error.message || 'Unknown error',
      userFriendlyMessage,
      stack: error.stack,
      timestamp: new Date(),
      context,
      severity,
      acknowledged: false,
      detailsVisible: false,
      originalError: error,
    };

    // Apply custom transformation if configured
    if (this.config.transformError) {
      const transformed = this.config.transformError(error, context);
      Object.assign(appError, transformed);
    }

    return appError;
  }

  /**
   * Collect comprehensive error context
   */
  private collectErrorContext(overrides: Partial<ErrorContext> = {}): ErrorContext {
    const baseContext: ErrorContext = {
      url: window.location.href,
      userAgent: navigator.userAgent,
      userActions: this.getRecentUserActions(),
      environment: {
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
        platform: navigator.platform,
        language: navigator.language,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine,
      },
      ...overrides,
    };

    // Add user ID if available from auth state
    try {
      const state = store.getState();
      if (state.auth?.user?.id) {
        baseContext.userId = state.auth.user.id;
      }
    } catch (err) {
      // Ignore auth state errors
    }

    return baseContext;
  }

  /**
   * Generate user-friendly error message
   */
  private getUserFriendlyMessage(error: Error, type: ErrorType): string {
    // Check for specific error patterns
    if (error.message.includes('fetch')) {
      return DEFAULT_USER_FRIENDLY_MESSAGES.network;
    }
    
    if (error.message.includes('401') || error.message.includes('unauthorized')) {
      return 'Your session has expired. Please log in again.';
    }
    
    if (error.message.includes('403') || error.message.includes('forbidden')) {
      return 'You do not have permission to perform this action.';
    }
    
    if (error.message.includes('404') || error.message.includes('not found')) {
      return 'The requested resource was not found.';
    }
    
    if (error.message.includes('500') || error.message.includes('internal server')) {
      return 'Our servers are experiencing issues. Please try again later.';
    }

    return DEFAULT_USER_FRIENDLY_MESSAGES[type] || DEFAULT_USER_FRIENDLY_MESSAGES.runtime;
  }

  /**
   * Handle the error by dispatching to Redux store
   */
  private handleError(appError: AppError): void {
    // Apply error filtering if configured
    if (this.config.filterError && this.config.filterError(appError.originalError!)) {
      return;
    }

    // Log to console if enabled
    if (this.config.logToConsole) {
      console.group(`🚨 GlobalErrorHandler: ${appError.type} error`);
      console.error('Error:', appError.originalError);
      console.error('AppError:', appError);
      console.groupEnd();
    }

    // Dispatch to Redux store
    store.dispatch(addError(appError));

    // For low severity errors, also show as notification
    if (appError.severity === 'low') {
      store.dispatch(addNotification({
        type: 'error',
        title: 'Error',
        message: appError.userFriendlyMessage,
        duration: 5000,
      }));
    }
  }

  /**
   * Setup window error handler
   */
  private setupWindowErrorHandler(): void {
    window.addEventListener('error', (event) => {
      const error = event.error || new Error(event.message);
      const context: Partial<ErrorContext> = {
        additionalData: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
        },
      };
      
      const appError = this.createAppError(error, 'runtime', context);
      this.handleError(appError);
    });
  }

  /**
   * Setup unhandled promise rejection handler
   */
  private setupUnhandledRejectionHandler(): void {
    window.addEventListener('unhandledrejection', (event) => {
      const error = event.reason instanceof Error 
        ? event.reason 
        : new Error(String(event.reason));
      
      const context: Partial<ErrorContext> = {
        additionalData: {
          reason: event.reason,
          promise: 'Promise rejection',
        },
      };
      
      const appError = this.createAppError(error, 'runtime', context);
      this.handleError(appError);
    });
  }

  /**
   * Setup console error handler
   */
  private setupConsoleErrorHandler(): void {
    const originalError = console.error;
    console.error = (...args: any[]) => {
      // Call original console.error
      originalError.apply(console, args);
      
      // Create error from console arguments
      const message = args.map(arg => String(arg)).join(' ');
      const error = new Error(message);
      
      const context: Partial<ErrorContext> = {
        additionalData: {
          consoleArgs: args,
        },
      };
      
      const appError = this.createAppError(error, 'runtime', context);
      this.handleError(appError);
    };
  }

  /**
   * Generate unique error ID
   */
  private generateErrorId(): string {
    return `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Create singleton instance
export const globalErrorHandler = new GlobalErrorHandler();

// Export types and utilities
export { GlobalErrorHandler };
export type { ErrorHandlerConfig };
