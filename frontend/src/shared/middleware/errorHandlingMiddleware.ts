/**
 * Error Handling Middleware
 * 
 * Redux middleware that intercepts RTK Query errors and other Redux actions
 * to provide comprehensive error handling and reporting through the global
 * error handling system.
 */

import { Middleware, isRejectedWithValue } from '@reduxjs/toolkit';
import { globalErrorHandler } from '@shared/services/GlobalErrorHandler';
import { ErrorContext } from '@shared/types/error.types';

/**
 * RTK Query error handling middleware
 * Intercepts rejected RTK Query actions and reports them to the global error handler
 */
export const rtkQueryErrorMiddleware: Middleware = (api) => (next) => (action) => {
  // Handle RTK Query rejected actions
  if (isRejectedWithValue(action)) {
    const error = action.payload;
    const meta = action.meta;
    
    // Extract error information
    const errorMessage = getErrorMessage(error);
    const statusCode = getStatusCode(error);
    const endpoint = getEndpoint(meta);
    
    // Create error context
    const context: Partial<ErrorContext> = {
      apiEndpoint: endpoint,
      statusCode,
      additionalData: {
        rtkQuery: true,
        originalError: error,
        meta,
        actionType: action.type,
      },
    };

    // Determine error type
    const errorType = statusCode && statusCode >= 400 && statusCode < 500 ? 'api' : 'network';
    
    // Create Error object
    const errorObj = new Error(errorMessage);
    
    // Report to global error handler
    globalErrorHandler.reportError(errorObj, errorType, context);
    
    // Track user action
    globalErrorHandler.trackUserAction(`API Error: ${endpoint}`, {
      status: statusCode,
      message: errorMessage,
      type: errorType,
    });
  }

  return next(action);
};

/**
 * General error action middleware
 * Intercepts actions with error patterns and reports them
 */
export const generalErrorMiddleware: Middleware = (api) => (next) => (action) => {
  // Handle actions that end with '/rejected'
  if (action.type.endsWith('/rejected') && action.error) {
    const error = action.error;
    const payload = action.payload;
    
    // Skip if already handled by RTK Query middleware
    if (action.meta?.rejectedWithValue) {
      return next(action);
    }
    
    // Create error context
    const context: Partial<ErrorContext> = {
      additionalData: {
        reduxAction: true,
        actionType: action.type,
        payload,
        meta: action.meta,
      },
    };
    
    // Create Error object
    const errorObj = new Error(error.message || 'Redux action failed');
    
    // Report to global error handler
    globalErrorHandler.reportError(errorObj, 'runtime', context);
  }

  return next(action);
};

/**
 * Extract error message from RTK Query error payload
 */
function getErrorMessage(error: any): string {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.data?.message) {
    return error.data.message;
  }
  
  if (error?.data?.error) {
    return error.data.error;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  if (error?.status) {
    return `HTTP ${error.status}: ${getStatusText(error.status)}`;
  }
  
  return 'An unknown error occurred';
}

/**
 * Extract status code from RTK Query error payload
 */
function getStatusCode(error: any): number | undefined {
  if (error?.status && typeof error.status === 'number') {
    return error.status;
  }
  
  if (error?.data?.status && typeof error.data.status === 'number') {
    return error.data.status;
  }
  
  return undefined;
}

/**
 * Extract endpoint from RTK Query meta
 */
function getEndpoint(meta: any): string {
  if (meta?.arg?.originalArgs) {
    const args = meta.arg.originalArgs;
    if (typeof args === 'string') {
      return args;
    }
    if (args?.url) {
      return args.url;
    }
  }
  
  if (meta?.arg?.endpointName) {
    return meta.arg.endpointName;
  }
  
  return 'Unknown endpoint';
}

/**
 * Get status text for HTTP status codes
 */
function getStatusText(status: number): string {
  const statusTexts: Record<number, string> = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    408: 'Request Timeout',
    409: 'Conflict',
    422: 'Unprocessable Entity',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
  };
  
  return statusTexts[status] || 'Unknown Error';
}

/**
 * Combined error handling middleware
 */
export const errorHandlingMiddleware = [
  rtkQueryErrorMiddleware,
  generalErrorMiddleware,
];
