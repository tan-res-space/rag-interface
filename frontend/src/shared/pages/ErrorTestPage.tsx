/**
 * Error Test Page
 * 
 * Standalone page for testing the comprehensive error handling system
 * without requiring authentication. Accessible at /error-test route.
 */

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import ErrorTestComponent from '@shared/components/ErrorTestComponent';

const ErrorTestPage: React.FC = () => {
  return (
    <Box sx={{ minHeight: '100vh', py: 4, backgroundColor: '#f5f5f5' }}>
      <Container maxWidth="lg">
        <Paper sx={{ p: 4, mb: 4 }}>
          <Typography variant="h3" gutterBottom align="center">
            Error Handling System Test
          </Typography>
          
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
            This page allows you to test the comprehensive error handling system
            implemented in the frontend application.
          </Typography>

          <Alert severity="info" sx={{ mb: 4 }}>
            <Typography variant="body2">
              <strong>How to test:</strong>
              <br />
              1. Click any error button below to trigger different types of errors
              <br />
              2. Observe the user-friendly error messages that appear
              <br />
              3. Click "Show Details" to see the comprehensive error information panel
              <br />
              4. Test the copy, expand, and dismiss functionality
            </Typography>
          </Alert>
        </Paper>

        <ErrorTestComponent />
      </Container>
    </Box>
  );
};

export default ErrorTestPage;
