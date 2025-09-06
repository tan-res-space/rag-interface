/**
 * ErrorDetailsPanel Component
 * 
 * Bottom-positioned panel that displays comprehensive error details including
 * stack traces, context information, and debugging data. Provides copy functionality
 * and collapsible interface for technical error information.
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Collapse,
  Chip,
  Divider,
  Button,
  Stack,
  useTheme,
} from '@mui/material';
import {
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Close as CloseIcon,
  ContentCopy as CopyIcon,
  BugReport as BugReportIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { ErrorDetailsPanelProps } from '@shared/types/error.types';

const ErrorDetailsPanel: React.FC<ErrorDetailsPanelProps> = ({
  error,
  open,
  expanded,
  onClose,
  onToggleExpanded,
  onCopyDetails,
}) => {
  const theme = useTheme();

  if (!error || !open) {
    return null;
  }

  const handleCopyDetails = async () => {
    const errorReport = generateErrorReport(error);
    
    try {
      await navigator.clipboard.writeText(errorReport);
      console.log('Error details copied to clipboard');
      if (onCopyDetails) {
        onCopyDetails(error);
      }
    } catch (err) {
      console.error('Failed to copy error details:', err);
      // Fallback: create a text area and select the text
      const textArea = document.createElement('textarea');
      textArea.value = errorReport;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  const formatStackTrace = (stack: string): string[] => {
    return stack
      .split('\n')
      .filter(line => line.trim())
      .map(line => line.trim());
  };

  const formatContextData = (data: any): string => {
    try {
      return JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  };

  return (
    <Paper
      elevation={8}
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: theme.zIndex.modal,
        backgroundColor: theme.palette.error.dark,
        color: theme.palette.error.contrastText,
        maxHeight: '60vh',
        overflow: 'hidden',
        borderRadius: '8px 8px 0 0',
      }}
    >
      {/* Panel Header */}
      <Box
        sx={{
          p: 2,
          backgroundColor: theme.palette.error.main,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
        }}
        onClick={onToggleExpanded}
      >
        <Stack direction="row" alignItems="center" spacing={2}>
          <BugReportIcon />
          <Typography variant="h6" component="div">
            Error Details
          </Typography>
          <Chip
            label={error.id}
            size="small"
            sx={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              fontFamily: 'monospace',
            }}
          />
          <Chip
            label={error.type.toUpperCase()}
            size="small"
            sx={{
              backgroundColor: 'rgba(255,255,255,0.1)',
              color: 'white',
            }}
          />
        </Stack>
        
        <Stack direction="row" spacing={1}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleCopyDetails();
            }}
            sx={{ color: 'white' }}
            title="Copy Error Details"
          >
            <CopyIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleRefresh();
            }}
            sx={{ color: 'white' }}
            title="Refresh Page"
          >
            <RefreshIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={onToggleExpanded}
            sx={{ color: 'white' }}
            title={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            sx={{ color: 'white' }}
            title="Close"
          >
            <CloseIcon />
          </IconButton>
        </Stack>
      </Box>

      {/* Collapsed Summary */}
      {!expanded && (
        <Box sx={{ p: 2, backgroundColor: 'rgba(0,0,0,0.1)' }}>
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
            {error.message}
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            {error.timestamp.toLocaleString()} • Click to expand details
          </Typography>
        </Box>
      )}

      {/* Expanded Error Details */}
      <Collapse in={expanded}>
        <Box
          sx={{
            maxHeight: '50vh',
            overflow: 'auto',
            backgroundColor: 'rgba(0,0,0,0.1)',
          }}
        >
          {/* Error Summary */}
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Error Summary
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                <strong>Type:</strong> {error.type}
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                <strong>Severity:</strong> {error.severity}
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                <strong>Message:</strong> {error.message}
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                <strong>User Message:</strong> {error.userFriendlyMessage}
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                <strong>Timestamp:</strong> {error.timestamp.toISOString()}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)' }} />

          {/* Context Information */}
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Context Information
            </Typography>
            <Box
              sx={{
                backgroundColor: 'rgba(0,0,0,0.3)',
                p: 1,
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: '0.75rem',
                lineHeight: 1.4,
                overflow: 'auto',
                maxHeight: '150px',
              }}
            >
              <div><strong>URL:</strong> {error.context.url}</div>
              <div><strong>User Agent:</strong> {error.context.userAgent}</div>
              {error.context.userId && <div><strong>User ID:</strong> {error.context.userId}</div>}
              {error.context.apiEndpoint && <div><strong>API Endpoint:</strong> {error.context.apiEndpoint}</div>}
              {error.context.statusCode && <div><strong>Status Code:</strong> {error.context.statusCode}</div>}
              {error.context.environment && (
                <div><strong>Environment:</strong> {formatContextData(error.context.environment)}</div>
              )}
            </Box>
          </Box>

          {/* Stack Trace */}
          {error.stack && (
            <>
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)' }} />
              <Box sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Stack Trace
                </Typography>
                <Box
                  sx={{
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    p: 1,
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    lineHeight: 1.4,
                    overflow: 'auto',
                    maxHeight: '200px',
                  }}
                >
                  {formatStackTrace(error.stack).map((line, index) => (
                    <div key={index} style={{ marginBottom: '2px' }}>
                      {line}
                    </div>
                  ))}
                </Box>
              </Box>
            </>
          )}

          {/* Component Stack */}
          {error.context.componentStack && (
            <>
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)' }} />
              <Box sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Component Stack
                </Typography>
                <Box
                  sx={{
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    p: 1,
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    lineHeight: 1.4,
                    overflow: 'auto',
                    maxHeight: '200px',
                  }}
                >
                  {formatStackTrace(error.context.componentStack).map((line, index) => (
                    <div key={index} style={{ marginBottom: '2px' }}>
                      {line}
                    </div>
                  ))}
                </Box>
              </Box>
            </>
          )}

          {/* User Actions */}
          {error.context.userActions && error.context.userActions.length > 0 && (
            <>
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)' }} />
              <Box sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Recent User Actions
                </Typography>
                <Box
                  sx={{
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    p: 1,
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    lineHeight: 1.4,
                    overflow: 'auto',
                    maxHeight: '150px',
                  }}
                >
                  {error.context.userActions.map((action, index) => (
                    <div key={index} style={{ marginBottom: '2px' }}>
                      {action}
                    </div>
                  ))}
                </Box>
              </Box>
            </>
          )}

          {/* Additional Data */}
          {error.context.additionalData && Object.keys(error.context.additionalData).length > 0 && (
            <>
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)' }} />
              <Box sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Additional Data
                </Typography>
                <Box
                  sx={{
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    p: 1,
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    lineHeight: 1.4,
                    overflow: 'auto',
                    maxHeight: '200px',
                  }}
                >
                  <pre>{formatContextData(error.context.additionalData)}</pre>
                </Box>
              </Box>
            </>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

// Helper function to generate comprehensive error report
function generateErrorReport(error: any): string {
  return `
=== Error Report ===
Error ID: ${error.id}
Type: ${error.type}
Severity: ${error.severity}
Timestamp: ${error.timestamp.toISOString()}

=== Messages ===
Technical: ${error.message}
User-Friendly: ${error.userFriendlyMessage}

=== Context ===
URL: ${error.context.url}
User Agent: ${error.context.userAgent}
${error.context.userId ? `User ID: ${error.context.userId}` : ''}
${error.context.apiEndpoint ? `API Endpoint: ${error.context.apiEndpoint}` : ''}
${error.context.statusCode ? `Status Code: ${error.context.statusCode}` : ''}

=== Stack Trace ===
${error.stack || 'No stack trace available'}

=== Component Stack ===
${error.context.componentStack || 'No component stack available'}

=== User Actions ===
${error.context.userActions ? error.context.userActions.join('\n') : 'No user actions recorded'}

=== Additional Data ===
${error.context.additionalData ? JSON.stringify(error.context.additionalData, null, 2) : 'No additional data'}

=== Environment ===
${error.context.environment ? JSON.stringify(error.context.environment, null, 2) : 'No environment data'}
  `.trim();
}

export default ErrorDetailsPanel;
