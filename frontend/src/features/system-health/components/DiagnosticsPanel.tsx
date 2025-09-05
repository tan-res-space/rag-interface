/**
 * Diagnostics Panel Component
 * Displays detailed diagnostic information for a specific service
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  NetworkCheck as NetworkIcon,
  Speed as PerformanceIcon,
  Storage as DependencyIcon,
  Info as InfoIcon,
  Dns as DnsIcon,
  Router as PortIcon,
  Security as SslIcon,
} from '@mui/icons-material';
import { SERVICE_CONFIGS } from '@infrastructure/api/health-api';
import type { DiagnosticsPanelProps, HealthStatus } from '../types/health-types';

const DiagnosticsPanel: React.FC<DiagnosticsPanelProps> = ({
  service,
  diagnostics,
  onClose,
}) => {
  const config = SERVICE_CONFIGS[service];

  const getStatusIcon = (status: boolean | HealthStatus) => {
    if (typeof status === 'boolean') {
      return status ? <SuccessIcon color="success" /> : <ErrorIcon color="error" />;
    }
    
    switch (status) {
      case 'healthy':
        return <SuccessIcon color="success" />;
      case 'degraded':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <WarningIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: boolean | HealthStatus) => {
    if (typeof status === 'boolean') {
      return status ? 'success' : 'error';
    }
    
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

  const getStatusText = (status: boolean | HealthStatus) => {
    if (typeof status === 'boolean') {
      return status ? 'OK' : 'Failed';
    }
    
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

  const getPerformanceRating = (responseTime: number) => {
    if (!config) return 'Unknown';
    
    if (responseTime <= config.expectedResponseTime) return 'Excellent';
    if (responseTime <= config.criticalResponseTime) return 'Good';
    return 'Poor';
  };

  const getPerformanceColor = (responseTime: number) => {
    if (!config) return 'default';
    
    if (responseTime <= config.expectedResponseTime) return 'success';
    if (responseTime <= config.criticalResponseTime) return 'warning';
    return 'error';
  };

  return (
    <Dialog
      open={true}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Diagnostics: {config?.displayName || service}
          </Typography>
          
          <Tooltip title="Close">
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Grid container spacing={3}>
          {/* Connectivity Tests */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <NetworkIcon color="primary" />
                  <Typography variant="h6">Connectivity</Typography>
                </Box>

                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(diagnostics.connectivity.can_reach)}
                    </ListItemIcon>
                    <ListItemText
                      primary="Service Reachable"
                      secondary={diagnostics.connectivity.can_reach ? 
                        'Service is responding to requests' : 
                        'Cannot connect to service'}
                    />
                    <Chip
                      label={getStatusText(diagnostics.connectivity.can_reach)}
                      color={getStatusColor(diagnostics.connectivity.can_reach) as any}
                      size="small"
                    />
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <DnsIcon color={diagnostics.connectivity.dns_resolution ? 'success' : 'error'} />
                    </ListItemIcon>
                    <ListItemText
                      primary="DNS Resolution"
                      secondary={diagnostics.connectivity.dns_resolution ? 
                        'Hostname resolves correctly' : 
                        'DNS resolution failed'}
                    />
                    <Chip
                      label={getStatusText(diagnostics.connectivity.dns_resolution)}
                      color={getStatusColor(diagnostics.connectivity.dns_resolution) as any}
                      size="small"
                    />
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <PortIcon color={diagnostics.connectivity.port_open ? 'success' : 'error'} />
                    </ListItemIcon>
                    <ListItemText
                      primary="Port Accessible"
                      secondary={diagnostics.connectivity.port_open ? 
                        `Port ${config?.port} is open and accessible` : 
                        `Port ${config?.port} is not accessible`}
                    />
                    <Chip
                      label={getStatusText(diagnostics.connectivity.port_open)}
                      color={getStatusColor(diagnostics.connectivity.port_open) as any}
                      size="small"
                    />
                  </ListItem>

                  {diagnostics.connectivity.ssl_valid !== undefined && (
                    <ListItem>
                      <ListItemIcon>
                        <SslIcon color={diagnostics.connectivity.ssl_valid ? 'success' : 'error'} />
                      </ListItemIcon>
                      <ListItemText
                        primary="SSL Certificate"
                        secondary={diagnostics.connectivity.ssl_valid ? 
                          'SSL certificate is valid' : 
                          'SSL certificate is invalid or expired'}
                      />
                      <Chip
                        label={getStatusText(diagnostics.connectivity.ssl_valid)}
                        color={getStatusColor(diagnostics.connectivity.ssl_valid) as any}
                        size="small"
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <PerformanceIcon color="primary" />
                  <Typography variant="h6">Performance</Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Response Time
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h5">
                      {diagnostics.performance.response_time}ms
                    </Typography>
                    <Chip
                      label={getPerformanceRating(diagnostics.performance.response_time)}
                      color={getPerformanceColor(diagnostics.performance.response_time) as any}
                      size="small"
                    />
                  </Box>
                  
                  {config && (
                    <Typography variant="caption" color="text.secondary">
                      Expected: ≤{config.expectedResponseTime}ms, Critical: ≤{config.criticalResponseTime}ms
                    </Typography>
                  )}
                </Box>

                <Divider sx={{ my: 2 }} />

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Error Rate
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h5">
                      {diagnostics.performance.error_rate.toFixed(1)}%
                    </Typography>
                    <Chip
                      label={diagnostics.performance.error_rate === 0 ? 'Excellent' : 
                             diagnostics.performance.error_rate < 5 ? 'Good' : 'High'}
                      color={diagnostics.performance.error_rate === 0 ? 'success' : 
                             diagnostics.performance.error_rate < 5 ? 'warning' : 'error'}
                      size="small"
                    />
                  </Box>
                </Box>

                {diagnostics.performance.throughput && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Throughput
                    </Typography>
                    <Typography variant="h6">
                      {diagnostics.performance.throughput} req/sec
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Dependencies */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <DependencyIcon color="primary" />
                  <Typography variant="h6">Dependencies</Typography>
                </Box>

                <Grid container spacing={2}>
                  {diagnostics.dependencies.database && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(diagnostics.dependencies.database)}
                        <Typography variant="body1">Database</Typography>
                        <Chip
                          label={getStatusText(diagnostics.dependencies.database)}
                          color={getStatusColor(diagnostics.dependencies.database) as any}
                          size="small"
                        />
                      </Box>
                    </Grid>
                  )}

                  {diagnostics.dependencies.cache && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(diagnostics.dependencies.cache)}
                        <Typography variant="body1">Cache</Typography>
                        <Chip
                          label={getStatusText(diagnostics.dependencies.cache)}
                          color={getStatusColor(diagnostics.dependencies.cache) as any}
                          size="small"
                        />
                      </Box>
                    </Grid>
                  )}

                  {diagnostics.dependencies.external_apis && 
                    Object.entries(diagnostics.dependencies.external_apis).map(([api, status]) => (
                      <Grid item xs={12} sm={6} md={4} key={api}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(status)}
                          <Typography variant="body1">{api}</Typography>
                          <Chip
                            label={getStatusText(status)}
                            color={getStatusColor(status) as any}
                            size="small"
                          />
                        </Box>
                      </Grid>
                    ))
                  }
                </Grid>

                {!diagnostics.dependencies.database && 
                 !diagnostics.dependencies.cache && 
                 !diagnostics.dependencies.external_apis && (
                  <Typography variant="body2" color="text.secondary">
                    No dependency information available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* System Information */}
          {diagnostics.system_info && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <InfoIcon color="primary" />
                    <Typography variant="h6">System Information</Typography>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2" color="text.secondary">
                        Version
                      </Typography>
                      <Typography variant="body1">
                        {diagnostics.system_info.version}
                      </Typography>
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2" color="text.secondary">
                        Uptime
                      </Typography>
                      <Typography variant="body1">
                        {diagnostics.system_info.uptime}
                      </Typography>
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2" color="text.secondary">
                        Environment
                      </Typography>
                      <Typography variant="body1">
                        {diagnostics.system_info.environment}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export { DiagnosticsPanel };
export default DiagnosticsPanel;
