/**
 * Service Health Hook
 * Provides individual service health monitoring and diagnostics functionality
 */

import { useState, useCallback } from 'react';
import { 
  useCheckServiceHealthQuery,
  healthApiClient,
} from '@infrastructure/api/health-api';
import type { 
  UseServiceHealthReturn,
  HealthCheckResult,
  DiagnosticInfo,
} from '../types/health-types';

export const useServiceHealth = (serviceName: string): UseServiceHealthReturn => {
  const [diagnostics, setDiagnostics] = useState<DiagnosticInfo | null>(null);
  const [diagnosticsLoading, setDiagnosticsLoading] = useState(false);
  const [diagnosticsError, setDiagnosticsError] = useState<string | null>(null);

  // RTK Query hook for service health
  const {
    data: healthData,
    error: healthError,
    isLoading: healthLoading,
    refetch: refetchHealth,
  } = useCheckServiceHealthQuery(serviceName, {
    refetchOnMountOrArgChange: true,
    refetchOnFocus: true,
  });

  // Combine error states
  const error = healthError || diagnosticsError;
  const errorMessage = error ? 
    (typeof error === 'string' ? error : 
     'data' in error ? (error.data as any)?.message : 
     'message' in error ? error.message : 'Unknown error') : 
    null;

  // Manual refresh function
  const refresh = useCallback(async () => {
    try {
      await refetchHealth();
    } catch (error) {
      console.error(`Failed to refresh health data for ${serviceName}:`, error);
    }
  }, [refetchHealth, serviceName]);

  // Run diagnostics function
  const runDiagnostics = useCallback(async () => {
    setDiagnosticsLoading(true);
    setDiagnosticsError(null);
    
    try {
      const diagnosticsResult = await healthApiClient.runDiagnostics(serviceName);
      setDiagnostics(diagnosticsResult);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to run diagnostics';
      setDiagnosticsError(errorMessage);
      console.error(`Failed to run diagnostics for ${serviceName}:`, error);
    } finally {
      setDiagnosticsLoading(false);
    }
  }, [serviceName]);

  return {
    health: healthData || null,
    diagnostics,
    loading: healthLoading || diagnosticsLoading,
    error: errorMessage,
    refresh,
    runDiagnostics,
  };
};
