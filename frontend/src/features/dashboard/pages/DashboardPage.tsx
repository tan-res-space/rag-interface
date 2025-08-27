/**
 * Dashboard Page Component
 *
 * Main dashboard page with comprehensive system overview,
 * real-time metrics, and interactive visualizations.
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Alert,
  Snackbar,
  AppBar,
  Toolbar,
  Chip,
  Badge,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  FilterList as FilterIcon,
  Download as ExportIcon,
  Notifications as NotificationsIcon,
  Dashboard as DashboardIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  fetchDashboardOverview,
  fetchServicesHealth,
  fetchDashboardAlerts,
  setConnectionStatus,
  incrementUpdateCount,
  toggleFullscreen,
  selectDashboardOverview,
  selectServicesHealth,
  selectDashboardAlerts,
  selectUnreadAlerts,
  selectQuickMetrics,
  selectDashboardLoading,
  selectDashboardError,
  selectActiveFilters,
  selectDashboardPreferences,
  selectIsConnected,
  selectLastUpdated,
} from '../dashboard-slice';

// Components
import DashboardHeader from '../components/DashboardHeader';
import QuickMetricsBar from '../components/QuickMetricsBar';
import SpeakerBucketOverview from '../components/SpeakerBucketOverview';
import SERMetricsChart from '../components/SERMetricsChart';
import RAGProcessingStatus from '../components/RAGProcessingStatus';
import MTValidationMetrics from '../components/MTValidationMetrics';
import TransitionStatistics from '../components/TransitionStatistics';
import ServicesHealthPanel from '../components/ServicesHealthPanel';
import DashboardFilters from '../components/DashboardFilters';
import AlertsPanel from '../components/AlertsPanel';
import DashboardSettings from '../components/DashboardSettings';

export const DashboardPage: React.FC = () => {
  const dispatch = useAppDispatch();

  // Redux state
  const overview = useAppSelector(selectDashboardOverview);
  const servicesHealth = useAppSelector(selectServicesHealth);
  const alerts = useAppSelector(selectDashboardAlerts);
  const unreadAlerts = useAppSelector(selectUnreadAlerts);
  const quickMetrics = useAppSelector(selectQuickMetrics);
  const loading = useAppSelector(selectDashboardLoading);
  const error = useAppSelector(selectDashboardError);
  const activeFilters = useAppSelector(selectActiveFilters);
  const preferences = useAppSelector(selectDashboardPreferences);
  const isConnected = useAppSelector(selectIsConnected);
  const lastUpdated = useAppSelector(selectLastUpdated);

  // Local state
  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAlerts, setShowAlerts] = useState(false);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  // Auto-refresh functionality
  useEffect(() => {
    if (!preferences.auto_refresh) return;

    const interval = setInterval(() => {
      handleRefreshData();
    }, preferences.refresh_interval);

    return () => clearInterval(interval);
  }, [preferences.auto_refresh, preferences.refresh_interval, activeFilters]);

  // Initial data load
  useEffect(() => {
    handleRefreshData();
    dispatch(fetchServicesHealth());
    dispatch(fetchDashboardAlerts());

    // Simulate connection status
    dispatch(setConnectionStatus(true));
  }, [dispatch]);

  // Handle data refresh
  const handleRefreshData = useCallback(async () => {
    try {
      await Promise.all([
        dispatch(fetchDashboardOverview(activeFilters)).unwrap(),
        dispatch(fetchServicesHealth()).unwrap(),
      ]);

      dispatch(incrementUpdateCount());

      setNotification({
        open: true,
        message: 'Dashboard data refreshed successfully',
        severity: 'success',
      });
    } catch (error: any) {
      setNotification({
        open: true,
        message: error.message || 'Failed to refresh dashboard data',
        severity: 'error',
      });
    }
  }, [dispatch, activeFilters]);

  // Handle manual refresh
  const handleManualRefresh = () => {
    handleRefreshData();
  };

  // Handle fullscreen toggle
  const handleFullscreenToggle = () => {
    dispatch(toggleFullscreen());

    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  // Handle export
  const handleExport = () => {
    // Export functionality would be implemented here
    setNotification({
      open: true,
      message: 'Export functionality coming soon',
      severity: 'info',
    });
  };

  // Speed dial actions
  const speedDialActions = [
    {
      icon: <FilterIcon />,
      name: 'Filters',
      onClick: () => setShowFilters(true),
    },
    {
      icon: <SettingsIcon />,
      name: 'Settings',
      onClick: () => setShowSettings(true),
    },
    {
      icon: <ExportIcon />,
      name: 'Export',
      onClick: handleExport,
    },
    {
      icon: <RefreshIcon />,
      name: 'Refresh',
      onClick: handleManualRefresh,
    },
  ];

  // Handle notification close
  const handleNotificationClose = () => {
    setNotification({ ...notification, open: false });
  };

  // Format last updated time
  const formatLastUpdated = (timestamp: string | null) => {
    if (!timestamp) return 'Never';

    const now = new Date();
    const updated = new Date(timestamp);
    const diffMs = now.getTime() - updated.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    return updated.toLocaleDateString();
  };

  return (
    <Box sx={{ flexGrow: 1, height: '100vh', overflow: 'hidden' }}>
      {/* Dashboard Header */}
      <DashboardHeader
        title="Speaker Bucket Management Dashboard"
        subtitle="Real-time system overview and analytics"
        lastUpdated={formatLastUpdated(lastUpdated)}
        isConnected={isConnected}
        onRefresh={handleManualRefresh}
        onToggleFullscreen={handleFullscreenToggle}
        loading={loading.overview}
      />

      {/* Quick Metrics Bar */}
      <QuickMetricsBar
        metrics={quickMetrics}
        loading={loading.overview}
      />

      {/* Main Content */}
      <Container maxWidth={false} sx={{ py: 2, height: 'calc(100vh - 140px)', overflow: 'auto' }}>
        {/* Error Alert */}
        {error.general && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error.general}
          </Alert>
        )}

        {/* Services Health Alert */}
        {servicesHealth && Object.values(servicesHealth).some(service => service.status !== 'healthy') && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Some services are experiencing issues. Check the Services Health panel for details.
          </Alert>
        )}

        {/* Dashboard Grid */}
        <Grid container spacing={3}>
          {/* Speaker Bucket Overview */}
          <Grid item xs={12} lg={6}>
            <SpeakerBucketOverview
              data={overview?.speaker_statistics}
              loading={loading.speakerStats}
              error={error.speakerStats}
            />
          </Grid>

          {/* SER Metrics Chart */}
          <Grid item xs={12} lg={6}>
            <SERMetricsChart
              data={overview?.ser_metrics}
              loading={loading.serMetrics}
              error={error.serMetrics}
            />
          </Grid>

          {/* RAG Processing Status */}
          <Grid item xs={12} md={6} lg={4}>
            <RAGProcessingStatus
              data={overview?.rag_processing}
              loading={loading.ragProcessing}
              error={error.ragProcessing}
            />
          </Grid>

          {/* MT Validation Metrics */}
          <Grid item xs={12} md={6} lg={4}>
            <MTValidationMetrics
              data={overview?.mt_validation}
              loading={loading.mtValidation}
              error={error.mtValidation}
            />
          </Grid>

          {/* Transition Statistics */}
          <Grid item xs={12} md={6} lg={4}>
            <TransitionStatistics
              data={overview?.transition_statistics}
              loading={loading.transitionStats}
              error={error.transitionStats}
            />
          </Grid>

          {/* Services Health Panel */}
          <Grid item xs={12}>
            <ServicesHealthPanel
              data={servicesHealth}
              loading={loading.servicesHealth}
              error={error.servicesHealth}
            />
          </Grid>
        </Grid>
      </Container>

      {/* Speed Dial */}
      <SpeedDial
        ariaLabel="Dashboard actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
        onClose={() => setSpeedDialOpen(false)}
        onOpen={() => setSpeedDialOpen(true)}
        open={speedDialOpen}
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={() => {
              action.onClick();
              setSpeedDialOpen(false);
            }}
          />
        ))}
      </SpeedDial>

      {/* Alerts FAB */}
      <Fab
        color="secondary"
        sx={{ position: 'fixed', bottom: 16, left: 16 }}
        onClick={() => setShowAlerts(true)}
      >
        <Badge badgeContent={unreadAlerts} color="error">
          <NotificationsIcon />
        </Badge>
      </Fab>

      {/* Dashboard Filters Dialog */}
      <DashboardFilters
        open={showFilters}
        onClose={() => setShowFilters(false)}
        filters={activeFilters}
      />

      {/* Dashboard Settings Dialog */}
      <DashboardSettings
        open={showSettings}
        onClose={() => setShowSettings(false)}
        preferences={preferences}
      />

      {/* Alerts Panel */}
      <AlertsPanel
        open={showAlerts}
        onClose={() => setShowAlerts(false)}
        alerts={alerts}
      />

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleNotificationClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleNotificationClose}
          severity={notification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DashboardPage;
