/**
 * ErrorProvider Component
 * 
 * Provides comprehensive error handling UI that displays user-friendly error messages
 * and detailed error information. Integrates ErrorDisplay and ErrorDetailsPanel
 * components with the global error handling system.
 */

import React, { useEffect } from 'react';
import { Box, Portal } from '@mui/material';
import { useAppDispatch } from '@/app/hooks';
import { useErrorHandler } from '@shared/hooks/useErrorHandler';
import { globalErrorHandler } from '@shared/services/GlobalErrorHandler';
import ErrorDisplay from './ErrorDisplay';
import ErrorDetailsPanel from './ErrorDetailsPanel';
import { removeError, setShowErrorDetails, setErrorDetailsExpanded } from '@shared/slices/ui-slice';

interface ErrorProviderProps {
  children: React.ReactNode;
}

export const ErrorProvider: React.FC<ErrorProviderProps> = ({ children }) => {
  const dispatch = useAppDispatch();
  const {
    errors,
    activeError,
    showErrorDetails,
    errorDetailsExpanded,
    displayPreferences,
    dismissError,
    toggleErrorDetails,
    acknowledgeError,
  } = useErrorHandler();

  // Initialize global error handler
  useEffect(() => {
    globalErrorHandler.initialize();
  }, []);

  // Auto-dismiss low severity errors
  useEffect(() => {
    if (displayPreferences.autoDismissLowSeverity) {
      const timer = setTimeout(() => {
        errors
          .filter(error => error.severity === 'low' && !error.acknowledged)
          .forEach(error => {
            acknowledgeError(error.id);
            if (displayPreferences.autoDismissTimeout > 0) {
              setTimeout(() => dismissError(error.id), 1000);
            }
          });
      }, displayPreferences.autoDismissTimeout);

      return () => clearTimeout(timer);
    }
  }, [errors, displayPreferences, acknowledgeError, dismissError]);

  const handleDismissError = (errorId: string) => {
    dismissError(errorId);
  };

  const handleToggleDetails = (errorId: string) => {
    toggleErrorDetails(errorId);
  };

  const handleCloseDetailsPanel = () => {
    dispatch(setShowErrorDetails(false));
  };

  const handleToggleExpanded = () => {
    dispatch(setErrorDetailsExpanded(!errorDetailsExpanded));
  };

  const handleCopyDetails = (error: any) => {
    // Optional: Show a notification that details were copied
    console.log('Error details copied for error:', error.id);
  };

  // Get errors to display (unacknowledged errors with medium+ severity)
  const errorsToDisplay = errors.filter(error => 
    !error.acknowledged && 
    (error.severity === 'medium' || error.severity === 'high' || error.severity === 'critical')
  );

  // Get the most recent high-priority error for the details panel
  const detailsError = activeError || errorsToDisplay[errorsToDisplay.length - 1] || null;

  return (
    <>
      {children}
      
      {/* Error Display Messages */}
      {errorsToDisplay.length > 0 && (
        <Portal>
          <Box
            sx={{
              position: 'fixed',
              top: 16,
              right: 16,
              zIndex: 1400,
              maxWidth: 500,
              width: '100%',
              maxHeight: '50vh',
              overflow: 'auto',
            }}
          >
            {errorsToDisplay.slice(-3).map((error) => (
              <ErrorDisplay
                key={error.id}
                error={error}
                showDetailsButton={true}
                onDismiss={handleDismissError}
                onToggleDetails={handleToggleDetails}
              />
            ))}
            
            {/* Show count if more errors exist */}
            {errorsToDisplay.length > 3 && (
              <Box
                sx={{
                  p: 1,
                  textAlign: 'center',
                  backgroundColor: 'rgba(0, 0, 0, 0.1)',
                  borderRadius: 1,
                  fontSize: '0.875rem',
                  color: 'text.secondary',
                }}
              >
                +{errorsToDisplay.length - 3} more errors
              </Box>
            )}
          </Box>
        </Portal>
      )}

      {/* Error Details Panel */}
      <ErrorDetailsPanel
        error={detailsError}
        open={showErrorDetails && detailsError !== null}
        expanded={errorDetailsExpanded}
        onClose={handleCloseDetailsPanel}
        onToggleExpanded={handleToggleExpanded}
        onCopyDetails={handleCopyDetails}
      />
    </>
  );
};

export default ErrorProvider;
