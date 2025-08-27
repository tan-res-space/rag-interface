/**
 * Redux slice for dashboard state management
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { dashboardApi } from '@/infrastructure/api/dashboard-api';
import {
  DashboardMetrics,
  SpeakerBucketStats,
  SERMetricsSummary,
  RAGProcessingSummary,
  MTValidationSummary,
  TransitionStatisticsSummary,
  ServicesHealthStatus,
  DashboardFilters,
  DashboardLayout,
  DashboardWidget,
  DashboardAlert,
  TimeSeriesData,
  PieChartData,
  BarChartData,
  DashboardPreferences,
  QuickMetric,
} from '@/domain/types/dashboard';

// Async thunks
export const fetchDashboardOverview = createAsyncThunk(
  'dashboard/fetchOverview',
  async (filters?: DashboardFilters) => {
    return await dashboardApi.getDashboardOverview(filters);
  }
);

export const fetchSpeakerBucketStats = createAsyncThunk(
  'dashboard/fetchSpeakerBucketStats',
  async (filters?: DashboardFilters) => {
    return await dashboardApi.getSpeakerBucketStats(filters);
  }
);

export const fetchSERMetricsSummary = createAsyncThunk(
  'dashboard/fetchSERMetricsSummary',
  async (filters?: DashboardFilters) => {
    return await dashboardApi.getSERMetricsSummary(filters);
  }
);

export const fetchRAGProcessingSummary = createAsyncThunk(
  'dashboard/fetchRAGProcessingSummary',
  async (filters?: DashboardFilters) => {
    return await dashboardApi.getRAGProcessingSummary(filters);
  }
);

export const fetchMTValidationSummary = createAsyncThunk(
  'dashboard/fetchMTValidationSummary',
  async (filters?: DashboardFilters) => {
    return await dashboardApi.getMTValidationSummary(filters);
  }
);

export const fetchTransitionStatistics = createAsyncThunk(
  'dashboard/fetchTransitionStatistics',
  async (filters?: DashboardFilters) => {
    return await dashboardApi.getTransitionStatistics(filters);
  }
);

export const fetchServicesHealth = createAsyncThunk(
  'dashboard/fetchServicesHealth',
  async () => {
    return await dashboardApi.getServicesHealth();
  }
);

export const fetchTimeSeriesData = createAsyncThunk(
  'dashboard/fetchTimeSeriesData',
  async ({ metric, filters }: { metric: string; filters?: any }) => {
    return await dashboardApi.getTimeSeriesData(metric, filters);
  }
);

export const fetchDashboardLayouts = createAsyncThunk(
  'dashboard/fetchLayouts',
  async () => {
    return await dashboardApi.getDashboardLayouts();
  }
);

export const saveDashboardLayout = createAsyncThunk(
  'dashboard/saveLayout',
  async (layout: Omit<DashboardLayout, 'id' | 'createdAt' | 'updatedAt'>) => {
    return await dashboardApi.saveDashboardLayout(layout);
  }
);

export const fetchDashboardAlerts = createAsyncThunk(
  'dashboard/fetchAlerts',
  async (filters?: { severity?: string; acknowledged?: boolean; limit?: number }) => {
    return await dashboardApi.getDashboardAlerts(filters);
  }
);

// State interface
interface DashboardState {
  // Main dashboard data
  overview: DashboardMetrics | null;
  speakerStats: SpeakerBucketStats | null;
  serMetrics: SERMetricsSummary | null;
  ragProcessing: RAGProcessingSummary | null;
  mtValidation: MTValidationSummary | null;
  transitionStats: TransitionStatisticsSummary | null;
  servicesHealth: ServicesHealthStatus | null;
  
  // Chart data
  chartData: {
    timeSeries: Record<string, TimeSeriesData>;
    pieCharts: Record<string, PieChartData>;
    barCharts: Record<string, BarChartData>;
  };
  
  // Layouts and widgets
  layouts: DashboardLayout[];
  currentLayout: DashboardLayout | null;
  customWidgets: DashboardWidget[];
  
  // Alerts and notifications
  alerts: DashboardAlert[];
  unreadAlerts: number;
  
  // Filters and preferences
  activeFilters: DashboardFilters;
  preferences: DashboardPreferences;
  
  // UI state
  selectedDateRange: {
    start: string;
    end: string;
    preset: string;
  };
  refreshInterval: number;
  autoRefresh: boolean;
  isFullscreen: boolean;
  
  // Quick metrics for header
  quickMetrics: QuickMetric[];
  
  // Loading states
  loading: {
    overview: boolean;
    speakerStats: boolean;
    serMetrics: boolean;
    ragProcessing: boolean;
    mtValidation: boolean;
    transitionStats: boolean;
    servicesHealth: boolean;
    charts: boolean;
    layouts: boolean;
    alerts: boolean;
  };
  
  // Error states
  error: {
    overview: string | null;
    speakerStats: string | null;
    serMetrics: string | null;
    ragProcessing: string | null;
    mtValidation: string | null;
    transitionStats: string | null;
    servicesHealth: string | null;
    charts: string | null;
    layouts: string | null;
    alerts: string | null;
    general: string | null;
  };
  
  // Real-time updates
  lastUpdated: string | null;
  isConnected: boolean;
  updateCount: number;
}

// Initial state
const initialState: DashboardState = {
  overview: null,
  speakerStats: null,
  serMetrics: null,
  ragProcessing: null,
  mtValidation: null,
  transitionStats: null,
  servicesHealth: null,
  
  chartData: {
    timeSeries: {},
    pieCharts: {},
    barCharts: {},
  },
  
  layouts: [],
  currentLayout: null,
  customWidgets: [],
  
  alerts: [],
  unreadAlerts: 0,
  
  activeFilters: {
    dateRange: {
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days ago
      end: new Date().toISOString().split('T')[0], // today
      preset: 'week',
    },
  },
  
  preferences: {
    default_layout: 'default',
    refresh_interval: 30000, // 30 seconds
    theme: 'light',
    timezone: 'UTC',
    number_format: 'US',
    chart_animations: true,
    auto_refresh: true,
    notification_settings: {
      alerts: true,
      email_reports: false,
      push_notifications: true,
    },
  },
  
  selectedDateRange: {
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
    preset: 'week',
  },
  refreshInterval: 30000,
  autoRefresh: true,
  isFullscreen: false,
  
  quickMetrics: [],
  
  loading: {
    overview: false,
    speakerStats: false,
    serMetrics: false,
    ragProcessing: false,
    mtValidation: false,
    transitionStats: false,
    servicesHealth: false,
    charts: false,
    layouts: false,
    alerts: false,
  },
  
  error: {
    overview: null,
    speakerStats: null,
    serMetrics: null,
    ragProcessing: null,
    mtValidation: null,
    transitionStats: null,
    servicesHealth: null,
    charts: null,
    layouts: null,
    alerts: null,
    general: null,
  },
  
  lastUpdated: null,
  isConnected: false,
  updateCount: 0,
};

// Slice
const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    // Filters
    setActiveFilters: (state, action: PayloadAction<DashboardFilters>) => {
      state.activeFilters = action.payload;
    },
    
    updateDateRange: (state, action: PayloadAction<{ start: string; end: string; preset?: string }>) => {
      state.selectedDateRange = {
        start: action.payload.start,
        end: action.payload.end,
        preset: action.payload.preset || 'custom',
      };
      state.activeFilters.dateRange = {
        start: action.payload.start,
        end: action.payload.end,
        preset: action.payload.preset,
      };
    },
    
    // Preferences
    updatePreferences: (state, action: PayloadAction<Partial<DashboardPreferences>>) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },
    
    setRefreshInterval: (state, action: PayloadAction<number>) => {
      state.refreshInterval = action.payload;
      state.preferences.refresh_interval = action.payload;
    },
    
    toggleAutoRefresh: (state) => {
      state.autoRefresh = !state.autoRefresh;
      state.preferences.auto_refresh = state.autoRefresh;
    },
    
    // Layout management
    setCurrentLayout: (state, action: PayloadAction<DashboardLayout>) => {
      state.currentLayout = action.payload;
    },
    
    updateWidgetPosition: (state, action: PayloadAction<{ widgetId: string; position: any }>) => {
      if (state.currentLayout) {
        const widget = state.currentLayout.widgets.find(w => w.id === action.payload.widgetId);
        if (widget) {
          widget.position = action.payload.position;
        }
      }
    },
    
    addCustomWidget: (state, action: PayloadAction<DashboardWidget>) => {
      state.customWidgets.push(action.payload);
    },
    
    removeCustomWidget: (state, action: PayloadAction<string>) => {
      state.customWidgets = state.customWidgets.filter(w => w.id !== action.payload);
    },
    
    // Alerts
    markAlertAsRead: (state, action: PayloadAction<string>) => {
      const alert = state.alerts.find(a => a.id === action.payload);
      if (alert && !alert.acknowledged) {
        alert.acknowledged = true;
        state.unreadAlerts = Math.max(0, state.unreadAlerts - 1);
      }
    },
    
    markAllAlertsAsRead: (state) => {
      state.alerts.forEach(alert => {
        alert.acknowledged = true;
      });
      state.unreadAlerts = 0;
    },
    
    // UI state
    toggleFullscreen: (state) => {
      state.isFullscreen = !state.isFullscreen;
    },
    
    // Real-time updates
    setConnectionStatus: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
    
    incrementUpdateCount: (state) => {
      state.updateCount += 1;
      state.lastUpdated = new Date().toISOString();
    },
    
    // Chart data
    setTimeSeriesData: (state, action: PayloadAction<{ key: string; data: TimeSeriesData }>) => {
      state.chartData.timeSeries[action.payload.key] = action.payload.data;
    },
    
    setPieChartData: (state, action: PayloadAction<{ key: string; data: PieChartData }>) => {
      state.chartData.pieCharts[action.payload.key] = action.payload.data;
    },
    
    setBarChartData: (state, action: PayloadAction<{ key: string; data: BarChartData }>) => {
      state.chartData.barCharts[action.payload.key] = action.payload.data;
    },
    
    // Quick metrics
    updateQuickMetrics: (state, action: PayloadAction<QuickMetric[]>) => {
      state.quickMetrics = action.payload;
    },
    
    // Error handling
    clearErrors: (state) => {
      state.error = {
        overview: null,
        speakerStats: null,
        serMetrics: null,
        ragProcessing: null,
        mtValidation: null,
        transitionStats: null,
        servicesHealth: null,
        charts: null,
        layouts: null,
        alerts: null,
        general: null,
      };
    },
    
    clearError: (state, action: PayloadAction<keyof DashboardState['error']>) => {
      state.error[action.payload] = null;
    },
  },
  
  extraReducers: (builder) => {
    // Dashboard overview
    builder
      .addCase(fetchDashboardOverview.pending, (state) => {
        state.loading.overview = true;
        state.error.overview = null;
      })
      .addCase(fetchDashboardOverview.fulfilled, (state, action) => {
        state.loading.overview = false;
        state.overview = action.payload;
        state.lastUpdated = new Date().toISOString();
        
        // Update quick metrics from overview
        if (action.payload) {
          state.quickMetrics = [
            {
              label: 'Total Speakers',
              value: action.payload.speaker_statistics.total_speakers,
              icon: 'people',
              color: 'primary',
            },
            {
              label: 'Avg SER Score',
              value: action.payload.ser_metrics.summary.average_ser_score.toFixed(1),
              unit: '%',
              icon: 'assessment',
              color: 'info',
            },
            {
              label: 'Active Sessions',
              value: action.payload.mt_validation.statistics.active_sessions,
              icon: 'play_arrow',
              color: 'success',
            },
            {
              label: 'Pending Transitions',
              value: action.payload.transition_statistics.statistics.pending_requests,
              icon: 'swap_horiz',
              color: 'warning',
            },
          ];
        }
      })
      .addCase(fetchDashboardOverview.rejected, (state, action) => {
        state.loading.overview = false;
        state.error.overview = action.error.message || 'Failed to fetch dashboard overview';
      });
    
    // Speaker bucket stats
    builder
      .addCase(fetchSpeakerBucketStats.pending, (state) => {
        state.loading.speakerStats = true;
        state.error.speakerStats = null;
      })
      .addCase(fetchSpeakerBucketStats.fulfilled, (state, action) => {
        state.loading.speakerStats = false;
        state.speakerStats = action.payload;
      })
      .addCase(fetchSpeakerBucketStats.rejected, (state, action) => {
        state.loading.speakerStats = false;
        state.error.speakerStats = action.error.message || 'Failed to fetch speaker statistics';
      });
    
    // Services health
    builder
      .addCase(fetchServicesHealth.pending, (state) => {
        state.loading.servicesHealth = true;
        state.error.servicesHealth = null;
      })
      .addCase(fetchServicesHealth.fulfilled, (state, action) => {
        state.loading.servicesHealth = false;
        state.servicesHealth = action.payload;
      })
      .addCase(fetchServicesHealth.rejected, (state, action) => {
        state.loading.servicesHealth = false;
        state.error.servicesHealth = action.error.message || 'Failed to fetch services health';
      });
    
    // Dashboard layouts
    builder
      .addCase(fetchDashboardLayouts.fulfilled, (state, action) => {
        state.layouts = action.payload;
        if (!state.currentLayout && action.payload.length > 0) {
          state.currentLayout = action.payload.find(l => l.isDefault) || action.payload[0];
        }
      });
    
    // Dashboard alerts
    builder
      .addCase(fetchDashboardAlerts.fulfilled, (state, action) => {
        state.alerts = action.payload;
        state.unreadAlerts = action.payload.filter(a => !a.acknowledged).length;
      });
    
    // Time series data
    builder
      .addCase(fetchTimeSeriesData.fulfilled, (state, action) => {
        // The key would be passed in the action meta or payload
        const key = action.meta.arg.metric;
        state.chartData.timeSeries[key] = action.payload;
      });
  },
});

// Export actions
export const {
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
} = dashboardSlice.actions;

// Selectors
export const selectDashboardOverview = (state: { dashboard: DashboardState }) => state.dashboard.overview;
export const selectSpeakerStats = (state: { dashboard: DashboardState }) => state.dashboard.speakerStats;
export const selectServicesHealth = (state: { dashboard: DashboardState }) => state.dashboard.servicesHealth;
export const selectActiveFilters = (state: { dashboard: DashboardState }) => state.dashboard.activeFilters;
export const selectCurrentLayout = (state: { dashboard: DashboardState }) => state.dashboard.currentLayout;
export const selectDashboardAlerts = (state: { dashboard: DashboardState }) => state.dashboard.alerts;
export const selectUnreadAlerts = (state: { dashboard: DashboardState }) => state.dashboard.unreadAlerts;
export const selectQuickMetrics = (state: { dashboard: DashboardState }) => state.dashboard.quickMetrics;
export const selectDashboardLoading = (state: { dashboard: DashboardState }) => state.dashboard.loading;
export const selectDashboardError = (state: { dashboard: DashboardState }) => state.dashboard.error;
export const selectChartData = (state: { dashboard: DashboardState }) => state.dashboard.chartData;
export const selectDashboardPreferences = (state: { dashboard: DashboardState }) => state.dashboard.preferences;
export const selectIsConnected = (state: { dashboard: DashboardState }) => state.dashboard.isConnected;
export const selectLastUpdated = (state: { dashboard: DashboardState }) => state.dashboard.lastUpdated;

export default dashboardSlice.reducer;
