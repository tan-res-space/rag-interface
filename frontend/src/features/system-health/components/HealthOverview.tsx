/**
 * Health Overview Component
 * Displays system-wide health metrics and summary
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Speed as SpeedIcon,
  Timeline as UptimeIcon,
  Storage as ServicesIcon,
} from '@mui/icons-material';
import type { HealthOverviewProps, HealthStatus } from '../types/health-types';

const HealthOverview: React.FC<HealthOverviewProps> = ({
  overview,
  onRefresh,
  loading = false,
}) => {
  const getOverallStatusIcon = (status: HealthStatus) => {
    switch (status) {
      case 'healthy':
        return <HealthyIcon color="success" sx={{ fontSize: 32 }} />;
      case 'degraded':
        return <WarningIcon color="warning" sx={{ fontSize: 32 }} />;
      case 'error':
        return <ErrorIcon color="error" sx={{ fontSize: 32 }} />;
      default:
        return <ServicesIcon color="disabled" sx={{ fontSize: 32 }} />;
    }
  };

  const getOverallStatusColor = (status: HealthStatus) => {
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

  const getOverallStatusText = (status: HealthStatus) => {
    switch (status) {
      case 'healthy':
        return 'All Systems Operational';
      case 'degraded':
        return 'Some Issues Detected';
      case 'error':
        return 'Critical Issues Present';
      default:
        return 'Status Unknown';
    }
  };

  const getHealthPercentage = () => {
    if (overview.total_services === 0) return 0;
    return (overview.healthy_services / overview.total_services) * 100;
  };

  const getUptimeColor = (uptime: number) => {
    if (uptime >= 99.9) return 'success';
    if (uptime >= 99.0) return 'warning';
    return 'error';
  };

  const getResponseTimeColor = (responseTime: number) => {
    if (responseTime <= 200) return 'success';
    if (responseTime <= 500) return 'warning';
    return 'error';
  };

  const formatLastUpdated = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    
    if (diffSeconds < 60) {
      return `${diffSeconds} seconds ago`;
    } else if (diffSeconds < 3600) {
      return `${Math.floor(diffSeconds / 60)} minutes ago`;
    } else {
      return date.toLocaleTimeString();
    }
  };

  return (
    <Card>
      <CardHeader
        title="System Health Overview"
        action={
          onRefresh && (
            <Tooltip title="Refresh">
              <IconButton onClick={onRefresh} disabled={loading}>
                {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
              </IconButton>
            </Tooltip>
          )
        }
      />
      
      <CardContent>
        {/* Overall Status */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          {getOverallStatusIcon(overview.overall_status)}
          
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h5" component="h3" gutterBottom>
              {getOverallStatusText(overview.overall_status)}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                label={`${overview.healthy_services}/${overview.total_services} Services Healthy`}
                color={getOverallStatusColor(overview.overall_status) as any}
                variant="outlined"
              />
              
              <Typography variant="body2" color="text.secondary">
                Last updated: {formatLastUpdated(overview.last_updated)}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Health Progress Bar */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              System Health
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {getHealthPercentage().toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={getHealthPercentage()}
            color={getOverallStatusColor(overview.overall_status) as any}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Metrics Grid */}
        <Grid container spacing={3}>
          {/* Service Status Breakdown */}
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <ServicesIcon color="action" sx={{ fontSize: 24, mb: 1 }} />
              <Typography variant="h6" component="div">
                {overview.total_services}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Services
              </Typography>
              
              <Box sx={{ mt: 2, space: 1 }}>
                {overview.healthy_services > 0 && (
                  <Chip
                    label={`${overview.healthy_services} Healthy`}
                    color="success"
                    size="small"
                    variant="outlined"
                    sx={{ mb: 0.5, mr: 0.5 }}
                  />
                )}
                
                {overview.degraded_services > 0 && (
                  <Chip
                    label={`${overview.degraded_services} Degraded`}
                    color="warning"
                    size="small"
                    variant="outlined"
                    sx={{ mb: 0.5, mr: 0.5 }}
                  />
                )}
                
                {overview.error_services > 0 && (
                  <Chip
                    label={`${overview.error_services} Error`}
                    color="error"
                    size="small"
                    variant="outlined"
                    sx={{ mb: 0.5, mr: 0.5 }}
                  />
                )}
                
                {overview.unknown_services > 0 && (
                  <Chip
                    label={`${overview.unknown_services} Unknown`}
                    color="default"
                    size="small"
                    variant="outlined"
                    sx={{ mb: 0.5, mr: 0.5 }}
                  />
                )}
              </Box>
            </Box>
          </Grid>

          {/* Average Response Time */}
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <SpeedIcon 
                color={getResponseTimeColor(overview.average_response_time) as any} 
                sx={{ fontSize: 24, mb: 1 }} 
              />
              <Typography variant="h6" component="div">
                {overview.average_response_time}ms
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Response Time
              </Typography>
              
              <Box sx={{ mt: 1 }}>
                <Chip
                  label={overview.average_response_time <= 200 ? 'Excellent' : 
                         overview.average_response_time <= 500 ? 'Good' : 'Slow'}
                  color={getResponseTimeColor(overview.average_response_time) as any}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>
          </Grid>

          {/* Overall Uptime */}
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <UptimeIcon 
                color={getUptimeColor(overview.overall_uptime) as any} 
                sx={{ fontSize: 24, mb: 1 }} 
              />
              <Typography variant="h6" component="div">
                {overview.overall_uptime.toFixed(2)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Overall Uptime
              </Typography>
              
              <Box sx={{ mt: 1 }}>
                <Chip
                  label={overview.overall_uptime >= 99.9 ? 'Excellent' : 
                         overview.overall_uptime >= 99.0 ? 'Good' : 'Poor'}
                  color={getUptimeColor(overview.overall_uptime) as any}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>
          </Grid>

          {/* System Status */}
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              {getOverallStatusIcon(overview.overall_status)}
              <Typography variant="h6" component="div" sx={{ mt: 1 }}>
                {overview.overall_status.charAt(0).toUpperCase() + overview.overall_status.slice(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                System Status
              </Typography>
              
              <Box sx={{ mt: 1 }}>
                <Chip
                  label={getOverallStatusText(overview.overall_status)}
                  color={getOverallStatusColor(overview.overall_status) as any}
                  size="small"
                  variant="filled"
                />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export { HealthOverview };
export default HealthOverview;
