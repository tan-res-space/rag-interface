/**
 * Services Health Panel Component
 * 
 * Comprehensive health monitoring for all microservices
 * with status indicators and performance metrics.
 */

import React from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  Skeleton,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Help as UnknownIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { ServicesHealthStatus, ServiceHealth } from '@/domain/types/dashboard';

interface ServicesHealthPanelProps {
  data?: ServicesHealthStatus;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

interface ServiceHealthCardProps {
  serviceName: string;
  health: ServiceHealth;
}

const ServiceHealthCard: React.FC<ServiceHealthCardProps> = ({ serviceName, health }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <HealthyIcon color="success" />;
      case 'degraded': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <UnknownIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const formatServiceName = (name: string) => {
    return name.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const formatLastCheck = (timestamp: string) => {
    const now = new Date();
    const lastCheck = new Date(timestamp);
    const diffMs = now.getTime() - lastCheck.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    return lastCheck.toLocaleDateString();
  };

  return (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          {getStatusIcon(health.status)}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" fontWeight="medium">
              {formatServiceName(serviceName)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Last check: {formatLastCheck(health.last_check)}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={health.status.toUpperCase()}
              color={getStatusColor(health.status)}
              size="small"
              variant="outlined"
            />
            <Chip
              label={`${health.response_time_ms}ms`}
              size="small"
              variant="outlined"
            />
          </Box>
        </Box>
      </AccordionSummary>
      
      <AccordionDetails>
        <Grid container spacing={2}>
          {/* Basic Metrics */}
          <Grid item xs={12} sm={6}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Response Time
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SpeedIcon fontSize="small" color="action" />
                <Typography variant="body1" fontWeight="medium">
                  {health.response_time_ms}ms
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Uptime
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body1" fontWeight="medium">
                  {health.uptime_percentage.toFixed(2)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={health.uptime_percentage}
                color={health.uptime_percentage > 99 ? 'success' : health.uptime_percentage > 95 ? 'warning' : 'error'}
                sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
              />
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Error Rate
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {health.error_rate.toFixed(2)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min(health.error_rate * 10, 100)} // Scale for visibility
                color={health.error_rate < 1 ? 'success' : health.error_rate < 5 ? 'warning' : 'error'}
                sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
              />
            </Box>
          </Grid>

          {/* Detailed Metrics */}
          {health.details && (
            <Grid item xs={12} sm={6}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  CPU Usage
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {health.details.cpu_usage.toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={health.details.cpu_usage}
                  color={health.details.cpu_usage < 70 ? 'success' : health.details.cpu_usage < 90 ? 'warning' : 'error'}
                  sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Memory Usage
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MemoryIcon fontSize="small" color="action" />
                  <Typography variant="body1" fontWeight="medium">
                    {health.details.memory_usage.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={health.details.memory_usage}
                  color={health.details.memory_usage < 70 ? 'success' : health.details.memory_usage < 90 ? 'warning' : 'error'}
                  sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Disk Usage
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <StorageIcon fontSize="small" color="action" />
                  <Typography variant="body1" fontWeight="medium">
                    {health.details.disk_usage.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={health.details.disk_usage}
                  color={health.details.disk_usage < 80 ? 'success' : health.details.disk_usage < 95 ? 'warning' : 'error'}
                  sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
                />
              </Box>
              
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Active Connections
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {health.details.active_connections.toLocaleString()}
                </Typography>
              </Box>
            </Grid>
          )}
        </Grid>
      </AccordionDetails>
    </Accordion>
  );
};

export const ServicesHealthPanel: React.FC<ServicesHealthPanelProps> = ({
  data,
  loading = false,
  error,
  onRefresh,
}) => {
  if (loading) {
    return (
      <Card>
        <CardHeader
          title={<Skeleton variant="text" width={200} />}
          action={<Skeleton variant="circular" width={40} height={40} />}
        />
        <CardContent>
          {[1, 2, 3, 4].map((i) => (
            <Box key={i} sx={{ mb: 2 }}>
              <Skeleton variant="rectangular" width="100%" height={60} />
            </Box>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader title="Services Health" />
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader title="Services Health" />
        <CardContent>
          <Alert severity="info">No services health data available</Alert>
        </CardContent>
      </Card>
    );
  }

  // Calculate overall health status
  const services = Object.entries(data);
  const healthyServices = services.filter(([_, health]) => health.status === 'healthy').length;
  const totalServices = services.length;
  const overallHealthPercentage = (healthyServices / totalServices) * 100;

  const getOverallStatus = () => {
    if (overallHealthPercentage === 100) return { status: 'All systems operational', color: 'success' };
    if (overallHealthPercentage >= 75) return { status: 'Minor issues detected', color: 'warning' };
    return { status: 'Critical issues detected', color: 'error' };
  };

  const overallStatus = getOverallStatus();

  return (
    <Card>
      <CardHeader
        title="Services Health"
        subheader={`${healthyServices}/${totalServices} services healthy`}
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={overallStatus.status}
              color={overallStatus.color as any}
              variant="outlined"
              size="small"
            />
            {onRefresh && (
              <Tooltip title="Refresh">
                <IconButton onClick={onRefresh} size="small">
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        }
      />
      
      <CardContent>
        {/* Overall Health Indicator */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Overall System Health
          </Typography>
          <LinearProgress
            variant="determinate"
            value={overallHealthPercentage}
            color={overallStatus.color as any}
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            {overallHealthPercentage.toFixed(1)}% of services are healthy
          </Typography>
        </Box>

        {/* Individual Service Health */}
        <Box>
          {services.map(([serviceName, health]) => (
            <ServiceHealthCard
              key={serviceName}
              serviceName={serviceName}
              health={health}
            />
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ServicesHealthPanel;
