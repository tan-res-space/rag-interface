/**
 * Enhanced Error Boundary Component
 *
 * Integrates with the global error handling system to provide consistent
 * error display and reporting. Handles React component errors and integrates
 * with the comprehensive error management system.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Alert,
  AlertTitle,
  Button,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { store } from '@/app/store';
import { globalErrorHandler } from '@shared/services/GlobalErrorHandler';
import { ErrorContext } from '@shared/types/error.types';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);

    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Generate unique error ID for tracking
    const errorId = `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    return {
      hasError: true,
      error,
      errorId,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Report error to global error handler
    const context: Partial<ErrorContext> = {
      componentStack: errorInfo.componentStack,
      additionalData: {
        errorBoundary: true,
        errorInfo,
      },
    };

    globalErrorHandler.reportError(error, 'component', context);

    // Log error to console in development
    if (import.meta.env.DEV) {
      console.group('🚨 React Error Boundary Caught Error');
      console.error('Error:', error);
      console.error('Error Info:', errorInfo);
      console.error('Component Stack:', errorInfo.componentStack);
      console.groupEnd();
    }
  }

  handleRefresh = () => {
    // Reset error state and reload
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    });

    // Reload the page
    window.location.reload();
  };



  render() {
    const { hasError, error } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // If custom fallback is provided, use it
      if (fallback) {
        return fallback;
      }

      // Show minimal error message and let ErrorProvider handle the details
      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="400px"
          p={4}
        >
          <Alert severity="error" sx={{ maxWidth: 600 }}>
            <AlertTitle>Component Error</AlertTitle>
            A component failed to render properly. The error has been reported and detailed information is available.
            <Box mt={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={this.handleRefresh}
                startIcon={<RefreshIcon />}
              >
                Refresh Page
              </Button>
            </Box>
          </Alert>
        </Box>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
