/**
 * Troubleshooting utilities and common solutions
 * Provides diagnostic suggestions and export functionality
 */

import type { 
  TroubleshootingSuggestion, 
  HealthCheckResult, 
  HealthReportExport,
  SystemHealthOverview,
} from '../types/health-types';
import { SERVICE_CONFIGS } from '@infrastructure/api/health-api';

/**
 * Generate troubleshooting suggestions based on service health status
 */
export const generateTroubleshootingSuggestions = (
  services: Record<string, HealthCheckResult>
): TroubleshootingSuggestion[] => {
  const suggestions: TroubleshootingSuggestion[] = [];

  Object.entries(services).forEach(([serviceName, health]) => {
    const config = SERVICE_CONFIGS[serviceName];
    if (!config) return;

    // Critical issues (service not responding)
    if (health.status === 'error') {
      suggestions.push({
        issue: `${config.displayName} is not responding`,
        severity: 'critical',
        description: `The ${serviceName} service is not reachable or returning errors. This may impact system functionality.`,
        possible_causes: [
          'Service is not running or has crashed',
          'Network connectivity issues between frontend and service',
          'Database connection problems',
          'Resource exhaustion (CPU/Memory/Disk)',
          'Configuration errors in service settings',
          'Port conflicts or firewall blocking access',
        ],
        suggested_actions: [
          'Check if the service process is running',
          'Verify network connectivity to the service endpoint',
          'Check service logs for error messages',
          'Restart the service if it has crashed',
          'Monitor system resources (CPU, memory, disk)',
          'Verify database connectivity if applicable',
          'Check firewall rules and port accessibility',
          'Review service configuration files',
        ],
        documentation_links: [
          `/docs/services/${serviceName}`,
          '/docs/troubleshooting/connectivity',
          '/docs/troubleshooting/service-restart',
        ],
      });
    }

    // Performance issues (slow response times)
    if (health.status === 'degraded' || health.responseTime > config.criticalResponseTime) {
      suggestions.push({
        issue: `${config.displayName} performance degraded`,
        severity: health.responseTime > config.criticalResponseTime * 2 ? 'high' : 'medium',
        description: `The ${serviceName} service is responding slowly (${health.responseTime}ms). Expected response time is under ${config.expectedResponseTime}ms.`,
        possible_causes: [
          'High system load or resource contention',
          'Database performance issues or slow queries',
          'Memory pressure or garbage collection delays',
          'Network latency or bandwidth limitations',
          'Inefficient code paths or algorithms',
          'External API dependencies responding slowly',
        ],
        suggested_actions: [
          'Monitor system metrics (CPU, memory, I/O)',
          'Check database performance and query execution times',
          'Review application logs for performance warnings',
          'Scale resources if needed (horizontal or vertical)',
          'Optimize database queries and indexes',
          'Check external API response times',
          'Consider caching frequently accessed data',
          'Profile application performance bottlenecks',
        ],
        documentation_links: [
          `/docs/services/${serviceName}/performance`,
          '/docs/troubleshooting/performance',
          '/docs/monitoring/metrics',
        ],
      });
    }

    // Warning for response times approaching critical threshold
    if (health.status === 'healthy' && health.responseTime > config.expectedResponseTime) {
      suggestions.push({
        issue: `${config.displayName} response time elevated`,
        severity: 'low',
        description: `The ${serviceName} service response time (${health.responseTime}ms) is above the expected threshold of ${config.expectedResponseTime}ms but still within acceptable limits.`,
        possible_causes: [
          'Increased load or traffic',
          'Background maintenance tasks',
          'Temporary resource constraints',
          'Network congestion',
        ],
        suggested_actions: [
          'Monitor the trend over time',
          'Check for any scheduled maintenance',
          'Review recent changes or deployments',
          'Consider preemptive scaling if trend continues',
        ],
        documentation_links: [
          `/docs/services/${serviceName}/monitoring`,
          '/docs/troubleshooting/performance',
        ],
      });
    }
  });

  // System-wide issues
  const totalServices = Object.keys(services).length;
  const errorServices = Object.values(services).filter(s => s.status === 'error').length;
  const degradedServices = Object.values(services).filter(s => s.status === 'degraded').length;

  if (errorServices > totalServices * 0.5) {
    suggestions.push({
      issue: 'Multiple services are failing',
      severity: 'critical',
      description: `More than half of the services (${errorServices}/${totalServices}) are not responding. This indicates a system-wide issue.`,
      possible_causes: [
        'Infrastructure failure (network, database, shared services)',
        'Resource exhaustion on the host system',
        'Configuration changes affecting multiple services',
        'Security incident or attack',
        'Power or hardware failure',
      ],
      suggested_actions: [
        'Check infrastructure status (network, database, load balancers)',
        'Verify host system resources and health',
        'Review recent configuration or deployment changes',
        'Check security logs for suspicious activity',
        'Contact infrastructure team or hosting provider',
        'Consider activating disaster recovery procedures',
      ],
      documentation_links: [
        '/docs/troubleshooting/system-wide-issues',
        '/docs/incident-response',
        '/docs/disaster-recovery',
      ],
    });
  } else if (degradedServices > totalServices * 0.3) {
    suggestions.push({
      issue: 'Multiple services showing performance issues',
      severity: 'medium',
      description: `Several services (${degradedServices}/${totalServices}) are experiencing performance degradation.`,
      possible_causes: [
        'Increased system load or traffic',
        'Shared resource constraints',
        'Network performance issues',
        'Database performance degradation',
      ],
      suggested_actions: [
        'Monitor system-wide metrics',
        'Check database performance',
        'Review traffic patterns and load',
        'Consider scaling shared resources',
        'Investigate network performance',
      ],
      documentation_links: [
        '/docs/troubleshooting/performance',
        '/docs/monitoring/system-metrics',
      ],
    });
  }

  return suggestions.sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });
};

/**
 * Export health report as downloadable file
 */
export const exportHealthReport = async (
  type: 'summary' | 'detailed' | 'historical',
  services: Record<string, HealthCheckResult>,
  overview: SystemHealthOverview | null,
  format: 'json' | 'csv' = 'json'
): Promise<void> => {
  const timestamp = new Date().toISOString();
  
  if (format === 'json') {
    const report: HealthReportExport = {
      generated_at: timestamp,
      report_type: type,
      system_overview: overview || {
        overall_status: 'unknown',
        total_services: 0,
        healthy_services: 0,
        degraded_services: 0,
        error_services: 0,
        unknown_services: 0,
        last_updated: timestamp,
        average_response_time: 0,
        overall_uptime: 0,
      },
      services: Object.fromEntries(
        Object.entries(services).map(([name, health]) => [
          name,
          health.data || {
            status: health.status,
            version: 'unknown',
            timestamp: health.timestamp,
            service: health.service,
          }
        ])
      ),
      troubleshooting: type === 'detailed' ? generateTroubleshootingSuggestions(services) : undefined,
    };

    downloadFile(
      JSON.stringify(report, null, 2),
      `health-report-${type}-${timestamp.split('T')[0]}.json`,
      'application/json'
    );
  } else if (format === 'csv') {
    const csvContent = generateCSVReport(services, overview);
    downloadFile(
      csvContent,
      `health-report-${type}-${timestamp.split('T')[0]}.csv`,
      'text/csv'
    );
  }
};

/**
 * Generate CSV format report
 */
const generateCSVReport = (
  services: Record<string, HealthCheckResult>,
  overview: SystemHealthOverview | null
): string => {
  const headers = [
    'Service Name',
    'Display Name',
    'Status',
    'Response Time (ms)',
    'Version',
    'Last Check',
    'Error Message',
    'URL',
    'Port'
  ];

  const rows = Object.entries(services).map(([serviceName, health]) => {
    const config = SERVICE_CONFIGS[serviceName];
    return [
      serviceName,
      config?.displayName || serviceName,
      health.status,
      health.responseTime.toString(),
      health.data?.version || 'unknown',
      health.timestamp,
      health.error || '',
      config?.url || '',
      config?.port?.toString() || ''
    ];
  });

  // Add overview as a summary row
  if (overview) {
    rows.unshift([
      'SYSTEM OVERVIEW',
      'Overall System Health',
      overview.overall_status,
      overview.average_response_time.toString(),
      '',
      overview.last_updated,
      '',
      `${overview.healthy_services}/${overview.total_services} healthy`,
      `${overview.overall_uptime}% uptime`
    ]);
  }

  return [headers, ...rows]
    .map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(','))
    .join('\n');
};

/**
 * Download file helper
 */
const downloadFile = (content: string, filename: string, mimeType: string): void => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
};

/**
 * Common troubleshooting steps for different service types
 */
export const COMMON_TROUBLESHOOTING_STEPS = {
  connectivity: [
    'Verify service is running: `systemctl status <service-name>`',
    'Check network connectivity: `ping <service-host>`',
    'Test port accessibility: `telnet <service-host> <port>`',
    'Check firewall rules: `iptables -L` or `ufw status`',
    'Verify DNS resolution: `nslookup <service-host>`',
  ],
  performance: [
    'Monitor system resources: `top`, `htop`, or `systemctl status`',
    'Check disk space: `df -h`',
    'Monitor memory usage: `free -h`',
    'Check I/O wait: `iostat -x 1`',
    'Review application logs for errors or warnings',
  ],
  database: [
    'Check database connectivity: `pg_isready` or equivalent',
    'Monitor database performance: slow query logs',
    'Check database connections: active connection count',
    'Verify database disk space and memory',
    'Review database configuration settings',
  ],
  general: [
    'Check service logs: `journalctl -u <service-name> -f`',
    'Verify configuration files are correct',
    'Check for recent changes or deployments',
    'Monitor system metrics and alerts',
    'Test with minimal configuration if possible',
  ],
};
