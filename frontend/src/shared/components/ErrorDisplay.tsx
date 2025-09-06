/**
 * ErrorDisplay Component
 * 
 * Displays user-friendly error messages with optional "Show Details" button.
 * Provides consistent error display across the application with appropriate
 * styling and actions based on error severity.
 */

import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  IconButton,
  Stack,
  Typography,
  Chip,
  useTheme,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
  BugReport as BugReportIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { AppError, ErrorDisplayProps } from '@shared/types/error.types';

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  showDetailsButton = true,
  actions,
  onDismiss,
  onToggleDetails,
}) => {
  const theme = useTheme();

  const getSeverityColor = (severity: AppError['severity']) => {
    switch (severity) {
      case 'low':
        return 'info';
      case 'medium':
        return 'warning';
      case 'high':
      case 'critical':
        return 'error';
      default:
        return 'error';
    }
  };

  const getSeverityIcon = (severity: AppError['severity']) => {
    switch (severity) {
      case 'low':
        return <InfoIcon />;
      case 'medium':
        return <WarningIcon />;
      case 'high':
      case 'critical':
        return <ErrorIcon />;
      default:
        return <BugReportIcon />;
    }
  };

  const getErrorTypeLabel = (type: AppError['type']) => {
    switch (type) {
      case 'api':
        return 'API Error';
      case 'network':
        return 'Network Error';
      case 'runtime':
        return 'Runtime Error';
      case 'component':
        return 'Component Error';
      case 'validation':
        return 'Validation Error';
      default:
        return 'Error';
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  const handleToggleDetails = () => {
    if (onToggleDetails) {
      onToggleDetails(error.id);
    }
  };

  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss(error.id);
    }
  };

  return (
    <Alert
      severity={getSeverityColor(error.severity)}
      icon={getSeverityIcon(error.severity)}
      sx={{
        mb: 2,
        '& .MuiAlert-message': {
          width: '100%',
        },
      }}
      action={
        <Stack direction="row" spacing={1} alignItems="center">
          {/* Error Type Chip */}
          <Chip
            label={getErrorTypeLabel(error.type)}
            size="small"
            variant="outlined"
            sx={{
              borderColor: 'currentColor',
              color: 'inherit',
              fontSize: '0.75rem',
            }}
          />
          
          {/* Show Details Button */}
          {showDetailsButton && (
            <Button
              size="small"
              variant="outlined"
              onClick={handleToggleDetails}
              startIcon={error.detailsVisible ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{
                borderColor: 'currentColor',
                color: 'inherit',
                '&:hover': {
                  borderColor: 'currentColor',
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
              }}
            >
              {error.detailsVisible ? 'Hide Details' : 'Show Details'}
            </Button>
          )}
          
          {/* Refresh Button for critical errors */}
          {error.severity === 'critical' && (
            <IconButton
              size="small"
              onClick={handleRefresh}
              sx={{ color: 'inherit' }}
              title="Refresh Page"
            >
              <RefreshIcon />
            </IconButton>
          )}
          
          {/* Custom Actions */}
          {actions}
          
          {/* Dismiss Button */}
          {error.severity !== 'critical' && (
            <IconButton
              size="small"
              onClick={handleDismiss}
              sx={{ color: 'inherit' }}
              title="Dismiss"
            >
              <CloseIcon />
            </IconButton>
          )}
        </Stack>
      }
    >
      <AlertTitle sx={{ fontWeight: 'bold', mb: 1 }}>
        {getErrorTypeLabel(error.type)}
      </AlertTitle>
      
      <Typography variant="body2" sx={{ mb: 1 }}>
        {error.userFriendlyMessage}
      </Typography>
      
      {/* Additional context for high/critical errors */}
      {(error.severity === 'high' || error.severity === 'critical') && (
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Error ID: {error.id} • {error.timestamp.toLocaleString()}
          </Typography>
        </Box>
      )}
      
      {/* Technical message for development or when explicitly requested */}
      {(import.meta.env.DEV || error.detailsVisible) && error.message !== error.userFriendlyMessage && (
        <Box
          sx={{
            mt: 1,
            p: 1,
            backgroundColor: 'rgba(0, 0, 0, 0.05)',
            borderRadius: 1,
            fontFamily: 'monospace',
            fontSize: '0.75rem',
          }}
        >
          <Typography variant="caption" component="div">
            Technical: {error.message}
          </Typography>
        </Box>
      )}
    </Alert>
  );
};

export default ErrorDisplay;
