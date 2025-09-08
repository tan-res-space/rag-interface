/**
 * Health Check API client
 * Implements Hexagonal Architecture adapter pattern for health monitoring operations
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { BaseApi } from './base-api';
import type {
  ServiceHealthResponse,
  HealthCheckResult,
  SystemHealthOverview,
  DiagnosticInfo,
  HealthHistoryEntry,
  ServiceConfig,
  HealthReportExport,
  HealthCheckApiResponse,
  SystemHealthApiResponse,
  DiagnosticsApiResponse,
  HealthHistoryApiResponse,
} from '@features/system-health/types/health-types';

// Service configurations for all backend services
// Updated to match actual container port mappings from podman-compose.dev.yml
export const SERVICE_CONFIGS: Record<string, ServiceConfig> = {
  'error-reporting': {
    name: 'error-reporting',
    displayName: 'Error Reporting Service',
    url: 'http://localhost:8010',
    port: 8010,
    healthEndpoint: '/health',
    timeout: 5000,
    expectedResponseTime: 200,
    criticalResponseTime: 1000,
  },
  'user-management': {
    name: 'user-management',
    displayName: 'User Management Service',
    url: 'http://localhost:8011',
    port: 8011,
    healthEndpoint: '/health',
    timeout: 5000,
    expectedResponseTime: 200,
    criticalResponseTime: 1000,
  },
  'rag-integration': {
    name: 'rag-integration',
    displayName: 'RAG Integration Service',
    url: 'http://localhost:8012',
    port: 8012,
    healthEndpoint: '/health',
    timeout: 5000,
    expectedResponseTime: 300,
    criticalResponseTime: 1500,
  },
  'correction-engine': {
    name: 'correction-engine',
    displayName: 'Correction Engine Service',
    url: 'http://localhost:8013',
    port: 8013,
    healthEndpoint: '/health',
    timeout: 5000,
    expectedResponseTime: 250,
    criticalResponseTime: 1200,
  },
  'verification': {
    name: 'verification',
    displayName: 'Verification Service',
    url: 'http://localhost:8014',
    port: 8014,
    healthEndpoint: '/health',
    timeout: 5000,
    expectedResponseTime: 200,
    criticalResponseTime: 1000,
  },
};

// Infrastructure service configurations
export const INFRASTRUCTURE_CONFIGS: Record<string, ServiceConfig> = {
  'postgres': {
    name: 'postgres',
    displayName: 'PostgreSQL Database',
    url: 'http://localhost:5433',
    port: 5433,
    healthEndpoint: '/health', // Note: This would need a custom health check
    timeout: 3000,
    expectedResponseTime: 100,
    criticalResponseTime: 500,
  },
  'redis': {
    name: 'redis',
    displayName: 'Redis Cache',
    url: 'http://localhost:6380',
    port: 6380,
    healthEndpoint: '/health', // Note: This would need a custom health check
    timeout: 3000,
    expectedResponseTime: 50,
    criticalResponseTime: 200,
  },
};

// RTK Query API for health monitoring
export const healthApi = createApi({
  reducerPath: 'healthApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '',
    timeout: 10000,
    prepareHeaders: (headers) => {
      headers.set('content-type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Health', 'Diagnostics'],
  endpoints: (builder) => ({
    // Check health of a specific service
    checkServiceHealth: builder.query<HealthCheckResult, string>({
      queryFn: async (serviceName) => {
        const config = SERVICE_CONFIGS[serviceName];
        if (!config) {
          return {
            error: {
              status: 'CUSTOM_ERROR',
              error: `Unknown service: ${serviceName}`,
            },
          };
        }

        const startTime = Date.now();
        try {
          const response = await fetch(`${config.url}${config.healthEndpoint}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            signal: AbortSignal.timeout(config.timeout),
          });

          const responseTime = Date.now() - startTime;
          
          if (!response.ok) {
            return {
              data: {
                service: serviceName,
                status: 'error' as const,
                responseTime,
                timestamp: new Date().toISOString(),
                error: `HTTP ${response.status}: ${response.statusText}`,
              },
            };
          }

          const data: ServiceHealthResponse = await response.json();
          
          // Determine status based on response time and service response
          let status = data.status || 'unknown';
          if (status === 'healthy' && responseTime > config.criticalResponseTime) {
            status = 'degraded';
          }

          return {
            data: {
              service: serviceName,
              status,
              responseTime,
              timestamp: new Date().toISOString(),
              data,
            },
          };
        } catch (error) {
          const responseTime = Date.now() - startTime;
          return {
            data: {
              service: serviceName,
              status: 'error' as const,
              responseTime,
              timestamp: new Date().toISOString(),
              error: error instanceof Error ? error.message : 'Unknown error',
            },
          };
        }
      },
      providesTags: (result, error, serviceName) => [
        { type: 'Health', id: serviceName },
      ],
    }),

    // Check health of all services
    checkAllServicesHealth: builder.query<Record<string, HealthCheckResult>, void>({
      queryFn: async () => {
        const results: Record<string, HealthCheckResult> = {};
        
        // Check all services in parallel
        const healthChecks = Object.keys(SERVICE_CONFIGS).map(async (serviceName) => {
          const config = SERVICE_CONFIGS[serviceName];
          const startTime = Date.now();
          
          try {
            const response = await fetch(`${config.url}${config.healthEndpoint}`, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
              },
              signal: AbortSignal.timeout(config.timeout),
            });

            const responseTime = Date.now() - startTime;
            
            if (!response.ok) {
              results[serviceName] = {
                service: serviceName,
                status: 'error',
                responseTime,
                timestamp: new Date().toISOString(),
                error: `HTTP ${response.status}: ${response.statusText}`,
              };
              return;
            }

            const data: ServiceHealthResponse = await response.json();
            
            let status = data.status || 'unknown';
            if (status === 'healthy' && responseTime > config.criticalResponseTime) {
              status = 'degraded';
            }

            results[serviceName] = {
              service: serviceName,
              status,
              responseTime,
              timestamp: new Date().toISOString(),
              data,
            };
          } catch (error) {
            const responseTime = Date.now() - startTime;
            results[serviceName] = {
              service: serviceName,
              status: 'error',
              responseTime,
              timestamp: new Date().toISOString(),
              error: error instanceof Error ? error.message : 'Unknown error',
            };
          }
        });

        await Promise.all(healthChecks);
        return { data: results };
      },
      providesTags: ['Health'],
    }),

    // Get system health overview
    getSystemHealthOverview: builder.query<SystemHealthOverview, void>({
      queryFn: async (_, { dispatch }) => {
        // Get all services health first
        const healthResult = await dispatch(
          healthApi.endpoints.checkAllServicesHealth.initiate()
        );

        if (healthResult.error) {
          return { error: healthResult.error };
        }

        const services = healthResult.data || {};
        const servicesList = Object.values(services);
        
        const totalServices = servicesList.length;
        const healthyServices = servicesList.filter(s => s.status === 'healthy').length;
        const degradedServices = servicesList.filter(s => s.status === 'degraded').length;
        const errorServices = servicesList.filter(s => s.status === 'error').length;
        const unknownServices = servicesList.filter(s => s.status === 'unknown').length;

        // Calculate overall status
        let overallStatus: 'healthy' | 'degraded' | 'error' | 'unknown' = 'healthy';
        if (errorServices > 0) {
          overallStatus = 'error';
        } else if (degradedServices > 0 || unknownServices > 0) {
          overallStatus = 'degraded';
        }

        // Calculate average response time
        const avgResponseTime = servicesList.length > 0
          ? servicesList.reduce((sum, s) => sum + s.responseTime, 0) / servicesList.length
          : 0;

        // Calculate overall uptime (simplified - in real implementation this would come from historical data)
        const overallUptime = totalServices > 0 ? (healthyServices / totalServices) * 100 : 0;

        return {
          data: {
            overall_status: overallStatus,
            total_services: totalServices,
            healthy_services: healthyServices,
            degraded_services: degradedServices,
            error_services: errorServices,
            unknown_services: unknownServices,
            last_updated: new Date().toISOString(),
            average_response_time: Math.round(avgResponseTime),
            overall_uptime: Math.round(overallUptime * 100) / 100,
          },
        };
      },
      providesTags: ['Health'],
    }),
  }),
});

// Class-based API client for additional functionality
export class HealthApiClient extends BaseApi {
  /**
   * Run comprehensive diagnostics for a service
   */
  async runDiagnostics(serviceName: string): Promise<DiagnosticInfo> {
    const config = SERVICE_CONFIGS[serviceName];
    if (!config) {
      throw new Error(`Unknown service: ${serviceName}`);
    }

    const diagnostics: DiagnosticInfo = {
      service: serviceName,
      connectivity: {
        can_reach: false,
        dns_resolution: false,
        port_open: false,
      },
      performance: {
        response_time: 0,
        error_rate: 0,
      },
      dependencies: {},
    };

    try {
      // Test basic connectivity
      const startTime = Date.now();
      const response = await fetch(`${config.url}${config.healthEndpoint}`, {
        method: 'GET',
        signal: AbortSignal.timeout(config.timeout),
      });
      
      const responseTime = Date.now() - startTime;
      
      diagnostics.connectivity.can_reach = true;
      diagnostics.connectivity.dns_resolution = true;
      diagnostics.connectivity.port_open = response.ok || response.status < 500;
      diagnostics.performance.response_time = responseTime;

      if (response.ok) {
        const healthData: ServiceHealthResponse = await response.json();
        diagnostics.system_info = {
          version: healthData.version,
          uptime: 'N/A', // Would need additional endpoint
          environment: 'production', // Would come from service
        };

        // Extract dependency information if available
        if (healthData.details) {
          // Map service-specific details to dependencies
          if (healthData.details.database_status) {
            diagnostics.dependencies.database = 
              healthData.details.database_status === 'healthy' ? 'healthy' : 'error';
          }
          if (healthData.details.cache_status) {
            diagnostics.dependencies.cache = 
              healthData.details.cache_status === 'healthy' ? 'healthy' : 'error';
          }
        }
      }
    } catch (error) {
      diagnostics.connectivity.can_reach = false;
      if (error instanceof TypeError && error.message.includes('fetch')) {
        diagnostics.connectivity.dns_resolution = false;
      }
    }

    return diagnostics;
  }

  /**
   * Export health report
   */
  async exportHealthReport(
    type: 'summary' | 'detailed' | 'historical',
    timeRange?: { start: string; end: string }
  ): Promise<HealthReportExport> {
    // This would typically call a backend endpoint
    // For now, we'll generate a client-side report
    
    const timestamp = new Date().toISOString();
    
    // Get current health data
    const healthChecks = await Promise.all(
      Object.keys(SERVICE_CONFIGS).map(async (serviceName) => {
        try {
          const result = await this.checkServiceHealth(serviceName);
          return [serviceName, result];
        } catch (error) {
          return [serviceName, {
            service: serviceName,
            status: 'error' as const,
            responseTime: 0,
            timestamp,
            error: error instanceof Error ? error.message : 'Unknown error',
          }];
        }
      })
    );

    const services = Object.fromEntries(healthChecks.map(([name, result]) => [
      name,
      result.data || {
        status: result.status,
        version: 'unknown',
        timestamp: result.timestamp,
        service: result.service,
      }
    ]));

    // Generate overview
    const servicesList = Object.values(healthChecks.map(([_, result]) => result));
    const overview: SystemHealthOverview = {
      overall_status: servicesList.some(s => s.status === 'error') ? 'error' : 
                     servicesList.some(s => s.status === 'degraded') ? 'degraded' : 'healthy',
      total_services: servicesList.length,
      healthy_services: servicesList.filter(s => s.status === 'healthy').length,
      degraded_services: servicesList.filter(s => s.status === 'degraded').length,
      error_services: servicesList.filter(s => s.status === 'error').length,
      unknown_services: servicesList.filter(s => s.status === 'unknown').length,
      last_updated: timestamp,
      average_response_time: servicesList.reduce((sum, s) => sum + s.responseTime, 0) / servicesList.length,
      overall_uptime: 99.5, // Would come from historical data
    };

    return {
      generated_at: timestamp,
      report_type: type,
      time_range: timeRange,
      system_overview: overview,
      services,
      diagnostics: type === 'detailed' ? await this.getAllDiagnostics() : undefined,
    };
  }

  private async checkServiceHealth(serviceName: string): Promise<HealthCheckResult> {
    const config = SERVICE_CONFIGS[serviceName];
    const startTime = Date.now();
    
    try {
      const response = await fetch(`${config.url}${config.healthEndpoint}`, {
        method: 'GET',
        signal: AbortSignal.timeout(config.timeout),
      });

      const responseTime = Date.now() - startTime;
      const data: ServiceHealthResponse = await response.json();

      return {
        service: serviceName,
        status: data.status || 'unknown',
        responseTime,
        timestamp: new Date().toISOString(),
        data,
      };
    } catch (error) {
      return {
        service: serviceName,
        status: 'error',
        responseTime: Date.now() - startTime,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async getAllDiagnostics(): Promise<Record<string, DiagnosticInfo>> {
    const diagnostics: Record<string, DiagnosticInfo> = {};
    
    await Promise.all(
      Object.keys(SERVICE_CONFIGS).map(async (serviceName) => {
        try {
          diagnostics[serviceName] = await this.runDiagnostics(serviceName);
        } catch (error) {
          // Skip failed diagnostics
        }
      })
    );

    return diagnostics;
  }
}

// Export hooks
export const {
  useCheckServiceHealthQuery,
  useCheckAllServicesHealthQuery,
  useGetSystemHealthOverviewQuery,
  useLazyCheckServiceHealthQuery,
  useLazyCheckAllServicesHealthQuery,
  useLazyGetSystemHealthOverviewQuery,
} = healthApi;

// Export singleton instance
export const healthApiClient = new HealthApiClient();
