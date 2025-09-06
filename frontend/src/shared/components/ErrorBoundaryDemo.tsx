/**
 * Error Boundary Demo Component
 * 
 * A test component to demonstrate the ErrorBoundary functionality.
 * This component can trigger various types of errors for testing purposes.
 * Only available in development mode.
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Stack,
  Alert,
  AlertTitle,
  Divider,
} from '@mui/material';
import {
  BugReport as BugReportIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

interface ErrorDemoProps {
  onClose?: () => void;
}

const ErrorBoundaryDemo: React.FC<ErrorDemoProps> = ({ onClose }) => {
  const [shouldThrowError, setShouldThrowError] = useState(false);

  // Only show in development
  if (!import.meta.env.DEV) {
    return null;
  }

  // Component that throws an error when shouldThrowError is true
  const ErrorThrowingComponent: React.FC = () => {
    if (shouldThrowError) {
      throw new Error('This is a test error thrown by ErrorBoundaryDemo component');
    }
    return <Typography>No error thrown yet.</Typography>;
  };

  const handleThrowError = () => {
    setShouldThrowError(true);
  };

  const handleThrowAsyncError = () => {
    // Simulate an async error (these won't be caught by error boundaries)
    setTimeout(() => {
      throw new Error('This is an async error that won\'t be caught by ErrorBoundary');
    }, 100);
  };

  const handleThrowPromiseRejection = () => {
    // Simulate a promise rejection
    Promise.reject(new Error('This is a promise rejection that won\'t be caught by ErrorBoundary'));
  };

  const handleThrowTypeError = () => {
    // This will be caught by the error boundary
    const obj: any = null;
    // This will throw a TypeError
    console.log(obj.someProperty.nestedProperty);
  };

  const handleThrowReferenceError = () => {
    // This will be caught by the error boundary
    // @ts-ignore - Intentionally accessing undefined variable
    console.log(undefinedVariable.someProperty);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        m: 2,
        backgroundColor: '#fff3e0',
        border: '2px solid #ff9800',
      }}
    >
      <Stack spacing={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <BugReportIcon color="warning" />
          <Typography variant="h6" color="warning.main">
            Error Boundary Demo (Development Only)
          </Typography>
        </Box>

        <Alert severity="info">
          <AlertTitle>Testing Error Boundary</AlertTitle>
          Use the buttons below to test different types of errors and see how the ErrorBoundary handles them.
        </Alert>

        <Divider />

        <Typography variant="subtitle2" color="text.secondary">
          Errors that WILL be caught by ErrorBoundary:
        </Typography>

        <Stack direction="row" spacing={2} flexWrap="wrap">
          <Button
            variant="contained"
            color="error"
            startIcon={<ErrorIcon />}
            onClick={handleThrowError}
          >
            Throw Render Error
          </Button>

          <Button
            variant="contained"
            color="error"
            startIcon={<ErrorIcon />}
            onClick={handleThrowTypeError}
          >
            Throw TypeError
          </Button>

          <Button
            variant="contained"
            color="error"
            startIcon={<ErrorIcon />}
            onClick={handleThrowReferenceError}
          >
            Throw ReferenceError
          </Button>
        </Stack>

        <Typography variant="subtitle2" color="text.secondary">
          Errors that will NOT be caught by ErrorBoundary:
        </Typography>

        <Stack direction="row" spacing={2} flexWrap="wrap">
          <Button
            variant="outlined"
            color="warning"
            startIcon={<WarningIcon />}
            onClick={handleThrowAsyncError}
          >
            Throw Async Error
          </Button>

          <Button
            variant="outlined"
            color="warning"
            startIcon={<WarningIcon />}
            onClick={handleThrowPromiseRejection}
          >
            Promise Rejection
          </Button>
        </Stack>

        <Divider />

        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Error Component Status:
          </Typography>
          <Box
            sx={{
              p: 2,
              backgroundColor: shouldThrowError ? '#ffebee' : '#e8f5e8',
              borderRadius: 1,
              border: shouldThrowError ? '1px solid #f44336' : '1px solid #4caf50',
            }}
          >
            <ErrorThrowingComponent />
          </Box>
        </Box>

        {onClose && (
          <Box display="flex" justifyContent="flex-end">
            <Button variant="outlined" onClick={onClose}>
              Close Demo
            </Button>
          </Box>
        )}

        <Alert severity="warning">
          <AlertTitle>Note</AlertTitle>
          <Typography variant="body2">
            • React Error Boundaries only catch errors during rendering, in lifecycle methods, and in constructors.
            <br />
            • They do NOT catch errors in event handlers, async code, or errors thrown during server-side rendering.
            <br />
            • Check the browser console for async errors and promise rejections.
          </Typography>
        </Alert>
      </Stack>
    </Paper>
  );
};

export default ErrorBoundaryDemo;
