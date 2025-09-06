/**
 * useErrorHandler Hook
 * 
 * Custom React hook that provides easy access to error handling functionality
 * and error state management. Integrates with the global error handling system
 * and Redux state.
 */

import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  addError,
  removeError,
  clearAllErrors,
  setActiveError,
  acknowledgeError,
  toggleErrorDetails,
  setShowErrorDetails,
  setErrorDetailsExpanded,
  selectErrors,
  selectActiveError,
  selectShowErrorDetails,
  selectErrorDetailsExpanded,
  selectErrorDisplayPreferences,
} from '@shared/slices/ui-slice';
import { globalErrorHandler } from '@shared/services/GlobalErrorHandler';
import { AppError, ErrorType, ErrorContext } from '@shared/types/error.types';

export interface UseErrorHandlerReturn {
  // Error state
  errors: AppError[];
  activeError: AppError | null;
  showErrorDetails: boolean;
  errorDetailsExpanded: boolean;
  displayPreferences: any;

  // Error actions
  reportError: (error: Error | string, type?: ErrorType, context?: Partial<ErrorContext>) => void;
  dismissError: (errorId: string) => void;
  clearAllErrors: () => void;
  setActiveError: (errorId: string | null) => void;
  acknowledgeError: (errorId: string) => void;
  toggleErrorDetails: (errorId: string) => void;
  showErrorDetailsPanel: (show: boolean) => void;
  expandErrorDetails: (expanded: boolean) => void;

  // User action tracking
  trackUserAction: (action: string, data?: any) => void;

  // Utility functions
  getErrorById: (errorId: string) => AppError | undefined;
  getErrorsByType: (type: ErrorType) => AppError[];
  getUnacknowledgedErrors: () => AppError[];
  hasActiveError: boolean;
  hasUnacknowledgedErrors: boolean;
}

/**
 * Custom hook for error handling
 */
export const useErrorHandler = (): UseErrorHandlerReturn => {
  const dispatch = useAppDispatch();
  
  // Selectors
  const errors = useAppSelector(selectErrors);
  const activeError = useAppSelector(selectActiveError);
  const showErrorDetails = useAppSelector(selectShowErrorDetails);
  const errorDetailsExpanded = useAppSelector(selectErrorDetailsExpanded);
  const displayPreferences = useAppSelector(selectErrorDisplayPreferences);

  // Error reporting
  const reportError = useCallback((
    error: Error | string,
    type: ErrorType = 'runtime',
    context: Partial<ErrorContext> = {}
  ) => {
    globalErrorHandler.reportError(error, type, context);
  }, []);

  // Error management actions
  const dismissError = useCallback((errorId: string) => {
    dispatch(removeError(errorId));
  }, [dispatch]);

  const clearAllErrorsAction = useCallback(() => {
    dispatch(clearAllErrors());
  }, [dispatch]);

  const setActiveErrorAction = useCallback((errorId: string | null) => {
    dispatch(setActiveError(errorId));
  }, [dispatch]);

  const acknowledgeErrorAction = useCallback((errorId: string) => {
    dispatch(acknowledgeError(errorId));
  }, [dispatch]);

  const toggleErrorDetailsAction = useCallback((errorId: string) => {
    dispatch(toggleErrorDetails(errorId));
  }, [dispatch]);

  const showErrorDetailsPanel = useCallback((show: boolean) => {
    dispatch(setShowErrorDetails(show));
  }, [dispatch]);

  const expandErrorDetails = useCallback((expanded: boolean) => {
    dispatch(setErrorDetailsExpanded(expanded));
  }, [dispatch]);

  // User action tracking
  const trackUserAction = useCallback((action: string, data?: any) => {
    globalErrorHandler.trackUserAction(action, data);
  }, []);

  // Utility functions
  const getErrorById = useCallback((errorId: string): AppError | undefined => {
    return errors.find(error => error.id === errorId);
  }, [errors]);

  const getErrorsByType = useCallback((type: ErrorType): AppError[] => {
    return errors.filter(error => error.type === type);
  }, [errors]);

  const getUnacknowledgedErrors = useCallback((): AppError[] => {
    return errors.filter(error => !error.acknowledged);
  }, [errors]);

  // Computed values
  const hasActiveError = activeError !== null;
  const hasUnacknowledgedErrors = getUnacknowledgedErrors().length > 0;

  return {
    // State
    errors,
    activeError,
    showErrorDetails,
    errorDetailsExpanded,
    displayPreferences,

    // Actions
    reportError,
    dismissError,
    clearAllErrors: clearAllErrorsAction,
    setActiveError: setActiveErrorAction,
    acknowledgeError: acknowledgeErrorAction,
    toggleErrorDetails: toggleErrorDetailsAction,
    showErrorDetailsPanel,
    expandErrorDetails,

    // User action tracking
    trackUserAction,

    // Utilities
    getErrorById,
    getErrorsByType,
    getUnacknowledgedErrors,
    hasActiveError,
    hasUnacknowledgedErrors,
  };
};

/**
 * Hook for API error handling
 * Provides specialized error handling for API/network errors
 */
export const useApiErrorHandler = () => {
  const { reportError, trackUserAction } = useErrorHandler();

  const handleApiError = useCallback((
    error: any,
    endpoint?: string,
    method?: string,
    requestData?: any
  ) => {
    const context: Partial<ErrorContext> = {
      apiEndpoint: endpoint,
      statusCode: error?.status || error?.response?.status,
      additionalData: {
        method,
        requestData,
        responseData: error?.data || error?.response?.data,
      },
    };

    // Determine error type based on error characteristics
    let errorType: ErrorType = 'api';
    if (error?.name === 'TypeError' && error?.message?.includes('fetch')) {
      errorType = 'network';
    }

    // Track the API call that failed
    trackUserAction(`API Error: ${method} ${endpoint}`, {
      status: error?.status,
      message: error?.message,
    });

    reportError(error, errorType, context);
  }, [reportError, trackUserAction]);

  return { handleApiError };
};

/**
 * Hook for form validation error handling
 */
export const useValidationErrorHandler = () => {
  const { reportError, trackUserAction } = useErrorHandler();

  const handleValidationError = useCallback((
    errors: Record<string, string> | string[],
    formName?: string,
    formData?: any
  ) => {
    const errorMessage = Array.isArray(errors) 
      ? errors.join(', ')
      : Object.values(errors).join(', ');

    const context: Partial<ErrorContext> = {
      additionalData: {
        formName,
        formData,
        validationErrors: errors,
      },
    };

    trackUserAction(`Validation Error: ${formName}`, { errors });

    reportError(new Error(errorMessage), 'validation', context);
  }, [reportError, trackUserAction]);

  return { handleValidationError };
};

export default useErrorHandler;
