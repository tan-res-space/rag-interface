/**
 * Error Test Component
 * 
 * Development component for testing the comprehensive error handling system.
 * Provides buttons to trigger different types of errors to verify the
 * error handling implementation works correctly.
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Stack,
  Divider,
  Alert,
} from '@mui/material';
import { useErrorHandler, useApiErrorHandler, useValidationErrorHandler } from '@shared/hooks/useErrorHandler';

const ErrorTestComponent: React.FC = () => {
  const { reportError, trackUserAction } = useErrorHandler();
  const { handleApiError } = useApiErrorHandler();
  const { handleValidationError } = useValidationErrorHandler();
  const [componentError, setComponentError] = useState(false);

  // Test runtime error
  const triggerRuntimeError = () => {
    trackUserAction('Triggered runtime error test');
    reportError(new Error('This is a test runtime error'), 'runtime');
  };

  // Test API error
  const triggerApiError = () => {
    trackUserAction('Triggered API error test');
    const mockApiError = {
      status: 500,
      data: { message: 'Internal server error occurred' },
      message: 'API request failed',
    };
    handleApiError(mockApiError, '/api/test/endpoint', 'GET');
  };

  // Test network error
  const triggerNetworkError = () => {
    trackUserAction('Triggered network error test');
    const networkError = new Error('Failed to fetch');
    networkError.name = 'TypeError';
    reportError(networkError, 'network');
  };

  // Test validation error
  const triggerValidationError = () => {
    trackUserAction('Triggered validation error test');
    const validationErrors = {
      email: 'Invalid email format',
      password: 'Password must be at least 8 characters',
    };
    handleValidationError(validationErrors, 'loginForm', { email: 'invalid-email', password: '123' });
  };

  // Test component error (React Error Boundary)
  const triggerComponentError = () => {
    trackUserAction('Triggered component error test');
    setComponentError(true);
  };

  // Test unhandled promise rejection
  const triggerUnhandledRejection = () => {
    trackUserAction('Triggered unhandled promise rejection test');
    // This will be caught by the global error handler
    Promise.reject(new Error('This is an unhandled promise rejection'));
  };

  // Test window error
  const triggerWindowError = () => {
    trackUserAction('Triggered window error test');
    // This will be caught by the global error handler
    setTimeout(() => {
      throw new Error('This is a window error');
    }, 100);
  };

  // Test multiple errors
  const triggerMultipleErrors = () => {
    trackUserAction('Triggered multiple errors test');
    
    // Trigger several errors in sequence
    setTimeout(() => reportError(new Error('First error'), 'runtime'), 100);
    setTimeout(() => reportError(new Error('Second error'), 'api'), 200);
    setTimeout(() => reportError(new Error('Third error'), 'validation'), 300);
  };

  // Component that throws an error when componentError is true
  const ErrorThrowingComponent = () => {
    if (componentError) {
      throw new Error('This is a test component error');
    }
    return null;
  };

  if (!import.meta.env.DEV) {
    return (
      <Alert severity="info">
        Error testing component is only available in development mode.
      </Alert>
    );
  }

  return (
    <Card sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Error Handling Test Component
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Use these buttons to test different types of errors and verify the error handling system works correctly.
        </Typography>

        <Stack spacing={2}>
          {/* Runtime Errors */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Runtime Errors
            </Typography>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <Button
                variant="outlined"
                color="error"
                onClick={triggerRuntimeError}
              >
                Runtime Error
              </Button>
              <Button
                variant="outlined"
                color="error"
                onClick={triggerWindowError}
              >
                Window Error
              </Button>
              <Button
                variant="outlined"
                color="error"
                onClick={triggerUnhandledRejection}
              >
                Unhandled Rejection
              </Button>
            </Stack>
          </Box>

          <Divider />

          {/* API/Network Errors */}
          <Box>
            <Typography variant="h6" gutterBottom>
              API & Network Errors
            </Typography>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <Button
                variant="outlined"
                color="warning"
                onClick={triggerApiError}
              >
                API Error
              </Button>
              <Button
                variant="outlined"
                color="warning"
                onClick={triggerNetworkError}
              >
                Network Error
              </Button>
            </Stack>
          </Box>

          <Divider />

          {/* Component Errors */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Component Errors
            </Typography>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <Button
                variant="outlined"
                color="secondary"
                onClick={triggerComponentError}
              >
                Component Error
              </Button>
              <Button
                variant="outlined"
                color="info"
                onClick={triggerValidationError}
              >
                Validation Error
              </Button>
            </Stack>
          </Box>

          <Divider />

          {/* Multiple Errors */}
          <Box>
            <Typography variant="h6" gutterBottom>
              Multiple Errors
            </Typography>
            <Button
              variant="contained"
              color="error"
              onClick={triggerMultipleErrors}
            >
              Trigger Multiple Errors
            </Button>
          </Box>
        </Stack>

        {/* Hidden component that throws error when triggered */}
        <ErrorThrowingComponent />
      </CardContent>
    </Card>
  );
};

export default ErrorTestComponent;
