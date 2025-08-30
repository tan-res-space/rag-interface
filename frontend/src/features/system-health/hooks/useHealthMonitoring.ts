/**
 * Health Monitoring Hook
 * Provides comprehensive health monitoring functionality with auto-refresh and state management
 */

import { useState, useCallback, useEffect } from 'react';
import { 
  useCheckAllServicesHealthQuery,
  useGetSystemHealthOverviewQuery,
  healthApiClient,
} from '@infrastructure/api/health-api';
import type { 
  UseHealthMonitoringReturn,
  HealthCheckResult,
  SystemHealthOverview,
  HealthMonitoringConfig,
} from '../types/health-types';

const DEFAULT_CONFIG: HealthMonitoringConfig = {
  auto_refresh: true,
  refresh_interval: 30, // 30 seconds
  timeout: 10000, // 10 seconds
  retry_attempts: 3,
  alert_thresholds: {
    response_time_warning: 500,
    response_time_critical: 1000,
    uptime_warning: 99.0,
    uptime_critical: 95.0,
    error_rate_warning: 5.0,
    error_rate_critical: 10.0,
  },
};

export const useHealthMonitoring = (
  customConfig?: Partial<HealthMonitoringConfig>
): UseHealthMonitoringReturn => {
  const [config, setConfig] = useState<HealthMonitoringConfig>({
    ...DEFAULT_CONFIG,
    ...customConfig,
  });
  
  const [lastRefresh, setLastRefresh] = useState<string | null>(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(config.auto_refresh);

  // RTK Query hooks for data fetching
  const {
    data: servicesData,
    error: servicesError,
    isLoading: servicesLoading,
    refetch: refetchServices,
  } = useCheckAllServicesHealthQuery(undefined, {
    pollingInterval: autoRefreshEnabled ? config.refresh_interval * 1000 : 0,
    refetchOnMountOrArgChange: true,
    refetchOnFocus: true,
  });

  const {
    data: overviewData,
    error: overviewError,
    isLoading: overviewLoading,
    refetch: refetchOverview,
  } = useGetSystemHealthOverviewQuery(undefined, {
    pollingInterval: autoRefreshEnabled ? config.refresh_interval * 1000 : 0,
    refetchOnMountOrArgChange: true,
    refetchOnFocus: true,
  });

  // Combine loading states
  const loading = servicesLoading || overviewLoading;

  // Combine error states
  const error = servicesError || overviewError;
  const errorMessage = error ? 
    ('data' in error ? (error.data as any)?.message : 'message' in error ? error.message : 'Unknown error') : 
    null;

  // Manual refresh function
  const refresh = useCallback(async () => {
    try {
      await Promise.all([
        refetchServices(),
        refetchOverview(),
      ]);
      setLastRefresh(new Date().toISOString());
    } catch (error) {
      console.error('Failed to refresh health data:', error);
    }
  }, [refetchServices, refetchOverview]);

  // Toggle auto-refresh
  const toggleAutoRefresh = useCallback(() => {
    setAutoRefreshEnabled(prev => {
      const newValue = !prev;
      setConfig(prevConfig => ({
        ...prevConfig,
        auto_refresh: newValue,
      }));
      return newValue;
    });
  }, []);

  // Export report function
  const exportReport = useCallback(async (
    type: 'summary' | 'detailed' | 'historical'
  ): Promise<void> => {
    try {
      const report = await healthApiClient.exportHealthReport(type);
      
      // Create and download the report
      const blob = new Blob([JSON.stringify(report, null, 2)], {
        type: 'application/json',
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `health-report-${type}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export health report:', error);
      throw error;
    }
  }, []);

  // Update last refresh when data changes
  useEffect(() => {
    if (servicesData || overviewData) {
      setLastRefresh(new Date().toISOString());
    }
  }, [servicesData, overviewData]);

  return {
    services: servicesData || {},
    overview: overviewData || null,
    loading,
    error: errorMessage,
    refresh,
    toggleAutoRefresh,
    exportReport,
  };
};
