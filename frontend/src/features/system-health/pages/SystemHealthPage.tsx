/**
 * System Health Page Component
 * Provides real-time monitoring and diagnostics for all backend services
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  IconButton,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Tooltip,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
  Timeline as TimelineIcon,
  BugReport as DiagnosticsIcon,
} from '@mui/icons-material';
import { useHealthMonitoring } from '../hooks/useHealthMonitoring';
import { HealthOverview } from '../components/HealthOverview';
import { ServiceStatusCard } from '../components/ServiceStatusCard';
import { DiagnosticsPanel } from '../components/DiagnosticsPanel';
import { TroubleshootingPanel } from '../components/TroubleshootingPanel';
import { SERVICE_CONFIGS } from '@infrastructure/api/health-api';
import { generateTroubleshootingSuggestions, exportHealthReport } from '../utils/troubleshooting';
import type { DiagnosticInfo, TroubleshootingSuggestion } from '../types/health-types';

const SystemHealthPage: React.FC = () => {
  const {
    services,
    overview,
    loading,
    error,
    refresh,
    toggleAutoRefresh,
    exportReport,
  } = useHealthMonitoring();

  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [showTroubleshooting, setShowTroubleshooting] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [diagnosticsData, setDiagnosticsData] = useState<DiagnosticInfo | null>(null);
  const [troubleshootingSuggestions, setTroubleshootingSuggestions] = useState<TroubleshootingSuggestion[]>([]);

  // Auto-refresh effect
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        refresh();
      }, 30000); // 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh, refresh]);

  const handleRefresh = () => {
    refresh();
  };

  const handleToggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
    toggleAutoRefresh();
  };

  const handleExportReport = async (type: 'summary' | 'detailed' | 'historical') => {
    try {
      await exportHealthReport(type, services, overview, 'json');
    } catch (error) {
      console.error('Failed to export report:', error);
    }
  };

  const handleViewDiagnostics = async (serviceName: string) => {
    setSelectedService(serviceName);
    setShowDiagnostics(true);
    
    // In a real implementation, this would call the diagnostics API
    // For now, we'll simulate diagnostics data
    const mockDiagnostics: DiagnosticInfo = {
      service: serviceName,
      connectivity: {
        can_reach: services[serviceName]?.status !== 'error',
        dns_resolution: true,
        port_open: services[serviceName]?.status !== 'error',
      },
      performance: {
        response_time: services[serviceName]?.responseTime || 0,
        error_rate: services[serviceName]?.status === 'error' ? 100 : 0,
      },
      dependencies: {
        database: services[serviceName]?.status === 'healthy' ? 'healthy' : 'error',
        cache: 'healthy',
      },
      system_info: {
        version: services[serviceName]?.data?.version || '1.0.0',
        uptime: '99.9%',
        environment: 'production',
      },
    };
    
    setDiagnosticsData(mockDiagnostics);
  };

  const handleShowTroubleshooting = () => {
    setShowTroubleshooting(true);

    // Generate troubleshooting suggestions based on current issues
    const suggestions = generateTroubleshootingSuggestions(services);
    setTroubleshootingSuggestions(suggestions);
  };

  const getOverallStatusColor = () => {
    if (!overview) return 'default';
    switch (overview.overall_status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getOverallStatusText = () => {
    if (!overview) return 'Unknown';
    switch (overview.overall_status) {
      case 'healthy': return 'All Systems Operational';
      case 'degraded': return 'Some Issues Detected';
      case 'error': return 'Critical Issues';
      default: return 'Status Unknown';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            System Health
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={handleToggleAutoRefresh}
                  size="small"
                />
              }
              label="Auto-refresh"
              sx={{ mr: 2 }}
            />
            
            <Tooltip title="Refresh Now">
              <IconButton onClick={handleRefresh} disabled={loading}>
                {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
              </IconButton>
            </Tooltip>
            
            <Tooltip title="View Troubleshooting">
              <IconButton onClick={handleShowTroubleshooting}>
                <DiagnosticsIcon />
              </IconButton>
            </Tooltip>
            
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleExportReport('summary')}
              size="small"
            >
              Export Report
            </Button>
          </Box>
        </Box>

        {/* Overall Status */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                label={getOverallStatusText()}
                color={getOverallStatusColor() as any}
                variant="filled"
                size="medium"
              />
              
              {overview && (
                <>
                  <Typography variant="body2" color="text.secondary">
                    {overview.healthy_services}/{overview.total_services} services healthy
                  </Typography>
                  
                  <Divider orientation="vertical" flexItem />
                  
                  <Typography variant="body2" color="text.secondary">
                    Avg Response: {overview.average_response_time}ms
                  </Typography>
                  
                  <Divider orientation="vertical" flexItem />
                  
                  <Typography variant="body2" color="text.secondary">
                    Uptime: {overview.overall_uptime}%
                  </Typography>
                  
                  <Divider orientation="vertical" flexItem />
                  
                  <Typography variant="body2" color="text.secondary">
                    Last Updated: {new Date(overview.last_updated).toLocaleTimeString()}
                  </Typography>
                </>
              )}
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Health Overview */}
      {overview && (
        <Box sx={{ mb: 4 }}>
          <HealthOverview overview={overview} onRefresh={handleRefresh} loading={loading} />
        </Box>
      )}

      {/* Service Status Cards */}
      <Typography variant="h5" component="h2" gutterBottom>
        Service Status
      </Typography>
      
      <Grid container spacing={3}>
        {Object.entries(SERVICE_CONFIGS).map(([serviceName, config]) => {
          const health = services[serviceName];
          
          return (
            <Grid item xs={12} md={6} lg={4} key={serviceName}>
              <ServiceStatusCard
                service={serviceName}
                health={health || {
                  service: serviceName,
                  status: 'unknown',
                  responseTime: 0,
                  timestamp: new Date().toISOString(),
                }}
                onRefresh={() => refresh()}
                onViewDiagnostics={() => handleViewDiagnostics(serviceName)}
              />
            </Grid>
          );
        })}
      </Grid>

      {/* Diagnostics Panel */}
      {showDiagnostics && selectedService && diagnosticsData && (
        <DiagnosticsPanel
          service={selectedService}
          diagnostics={diagnosticsData}
          onClose={() => {
            setShowDiagnostics(false);
            setSelectedService(null);
            setDiagnosticsData(null);
          }}
        />
      )}

      {/* Troubleshooting Panel */}
      {showTroubleshooting && (
        <TroubleshootingPanel
          suggestions={troubleshootingSuggestions}
          onClose={() => setShowTroubleshooting(false)}
        />
      )}
    </Container>
  );
};

export default SystemHealthPage;
