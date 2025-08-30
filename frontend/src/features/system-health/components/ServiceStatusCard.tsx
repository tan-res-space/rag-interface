/**
 * Service Status Card Component
 * Displays individual service health status with detailed metrics
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  IconButton,
  Button,
  LinearProgress,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  CheckCircle as HealthyIcon,
  Warning as DegradedIcon,
  Error as ErrorIcon,
  Help as UnknownIcon,
  Refresh as RefreshIcon,
  Timeline as DiagnosticsIcon,
  AccessTime as TimeIcon,
  Speed as ResponseIcon,
} from '@mui/icons-material';
import { SERVICE_CONFIGS } from '@infrastructure/api/health-api';
import type { ServiceStatusCardProps, HealthStatus } from '../types/health-types';

const ServiceStatusCard: React.FC<ServiceStatusCardProps> = ({
  service,
  health,
  onRefresh,
  onViewDiagnostics,
}) => {
  const config = SERVICE_CONFIGS[service];
  
  if (!config) {
    return null;
  }

  const getStatusIcon = (status: HealthStatus) => {
    switch (status) {
      case 'healthy':
        return <HealthyIcon color="success" />;
      case 'degraded':
        return <DegradedIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <UnknownIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: HealthStatus) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: HealthStatus) => {
    switch (status) {
      case 'healthy':
        return 'Healthy';
      case 'degraded':
        return 'Degraded';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  const getResponseTimeColor = (responseTime: number) => {
    if (responseTime <= config.expectedResponseTime) return 'success';
    if (responseTime <= config.criticalResponseTime) return 'warning';
    return 'error';
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatUptime = (uptime?: number) => {
    if (uptime === undefined) return 'N/A';
    return `${uptime.toFixed(2)}%`;
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: health.status === 'error' ? 2 : 1,
        borderColor: health.status === 'error' ? 'error.main' : 'divider',
      }}
    >
      <CardContent>
        {/* Service Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getStatusIcon(health.status)}
            <Typography variant="h6" component="h3" noWrap>
              {config.displayName}
            </Typography>
          </Box>
          
          <Chip
            label={getStatusText(health.status)}
            color={getStatusColor(health.status) as any}
            size="small"
            variant="filled"
          />
        </Box>

        {/* Service Details */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {config.url}:{config.port}
          </Typography>
          
          {health.error && (
            <Typography variant="body2" color="error" sx={{ mt: 1 }}>
              Error: {health.error}
            </Typography>
          )}
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Metrics */}
        <Box sx={{ space: 2 }}>
          {/* Response Time */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <ResponseIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                Response Time
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body1" fontWeight="medium">
                {health.responseTime}ms
              </Typography>
              <Chip
                label={health.responseTime <= config.expectedResponseTime ? 'Fast' : 
                       health.responseTime <= config.criticalResponseTime ? 'Slow' : 'Critical'}
                color={getResponseTimeColor(health.responseTime) as any}
                size="small"
                variant="outlined"
              />
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min((health.responseTime / config.criticalResponseTime) * 100, 100)}
              color={getResponseTimeColor(health.responseTime) as any}
              sx={{ mt: 1, height: 4, borderRadius: 2 }}
            />
          </Box>

          {/* Uptime */}
          {health.data?.uptime_percentage !== undefined && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <TimeIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  Uptime
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">
                {formatUptime(health.data.uptime_percentage)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={health.data.uptime_percentage}
                color={health.data.uptime_percentage > 99 ? 'success' : 
                       health.data.uptime_percentage > 95 ? 'warning' : 'error'}
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
              />
            </Box>
          )}

          {/* Version */}
          {health.data?.version && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Version: {health.data.version}
              </Typography>
            </Box>
          )}

          {/* Last Check */}
          <Box>
            <Typography variant="caption" color="text.secondary">
              Last checked: {formatTimestamp(health.timestamp)}
            </Typography>
          </Box>
        </Box>

        {/* Additional Details */}
        {health.data?.details && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                System Resources
              </Typography>
              
              {health.data.details.cpu_usage !== undefined && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="caption">
                    CPU: {health.data.details.cpu_usage}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={health.data.details.cpu_usage}
                    color={health.data.details.cpu_usage > 80 ? 'error' : 
                           health.data.details.cpu_usage > 60 ? 'warning' : 'success'}
                    sx={{ height: 3, borderRadius: 1 }}
                  />
                </Box>
              )}
              
              {health.data.details.memory_usage !== undefined && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="caption">
                    Memory: {health.data.details.memory_usage}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={health.data.details.memory_usage}
                    color={health.data.details.memory_usage > 80 ? 'error' : 
                           health.data.details.memory_usage > 60 ? 'warning' : 'success'}
                    sx={{ height: 3, borderRadius: 1 }}
                  />
                </Box>
              )}
              
              {health.data.details.active_connections !== undefined && (
                <Typography variant="caption" display="block">
                  Active Connections: {health.data.details.active_connections}
                </Typography>
              )}
            </Box>
          </>
        )}
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        <Button
          size="small"
          startIcon={<DiagnosticsIcon />}
          onClick={() => onViewDiagnostics?.()}
          variant="outlined"
        >
          Diagnostics
        </Button>
        
        <Tooltip title="Refresh Status">
          <IconButton size="small" onClick={() => onRefresh?.()}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  );
};

export default ServiceStatusCard;
