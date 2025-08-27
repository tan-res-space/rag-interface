/**
 * Dashboard Feature Exports
 * 
 * Central export file for the dashboard feature
 */

// Pages
export { default as DashboardPage } from './pages/DashboardPage';

// Components
export { default as DashboardHeader } from './components/DashboardHeader';
export { default as QuickMetricsBar } from './components/QuickMetricsBar';
export { default as SpeakerBucketOverview } from './components/SpeakerBucketOverview';
export { default as SERMetricsChart } from './components/SERMetricsChart';
export { default as RAGProcessingStatus } from './components/RAGProcessingStatus';
export { default as MTValidationMetrics } from './components/MTValidationMetrics';
export { default as TransitionStatistics } from './components/TransitionStatistics';
export { default as ServicesHealthPanel } from './components/ServicesHealthPanel';
export { default as DashboardFilters } from './components/DashboardFilters';
export { default as AlertsPanel } from './components/AlertsPanel';
export { default as DashboardSettings } from './components/DashboardSettings';

// Redux
export {
  default as dashboardReducer,
  // Async actions
  fetchDashboardOverview,
  fetchSpeakerBucketStats,
  fetchSERMetricsSummary,
  fetchRAGProcessingSummary,
  fetchMTValidationSummary,
  fetchTransitionStatistics,
  fetchServicesHealth,
  fetchTimeSeriesData,
  fetchDashboardLayouts,
  saveDashboardLayout,
  fetchDashboardAlerts,
  // Sync actions
  setActiveFilters,
  updateDateRange,
  updatePreferences,
  setRefreshInterval,
  toggleAutoRefresh,
  setCurrentLayout,
  updateWidgetPosition,
  addCustomWidget,
  removeCustomWidget,
  markAlertAsRead,
  markAllAlertsAsRead,
  toggleFullscreen,
  setConnectionStatus,
  incrementUpdateCount,
  setTimeSeriesData,
  setPieChartData,
  setBarChartData,
  updateQuickMetrics,
  clearErrors,
  clearError,
  // Selectors
  selectDashboardOverview,
  selectSpeakerStats,
  selectServicesHealth,
  selectActiveFilters,
  selectCurrentLayout,
  selectDashboardAlerts,
  selectUnreadAlerts,
  selectQuickMetrics,
  selectDashboardLoading,
  selectDashboardError,
  selectChartData,
  selectDashboardPreferences,
  selectIsConnected,
  selectLastUpdated,
} from './dashboard-slice';

// API
export { dashboardApi } from '@/infrastructure/api/dashboard-api';

// Types (re-export from domain)
export type {
  DashboardMetrics,
  SpeakerBucketStats,
  SERMetricsSummary,
  RAGProcessingSummary,
  MTValidationSummary,
  TransitionStatisticsSummary,
  ServicesHealthStatus,
  ServiceHealth,
  DashboardFilters,
  DashboardLayout,
  DashboardWidget,
  DashboardAlert,
  DashboardPreferences,
  QuickMetric,
  ChartDataPoint,
  TimeSeriesData,
  PieChartData,
  BarChartData,
  DashboardUpdate,
  DashboardReport,
  PerformanceMetrics,
  DrillDownContext,
  NavigationAction,
} from '@/domain/types/dashboard';
