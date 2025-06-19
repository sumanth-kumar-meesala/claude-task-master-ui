/**
 * Health check service for monitoring API status.
 */

import { BaseApiService, API_ENDPOINTS } from './api';
import { HealthResponse, ApiInfoResponse, ApiStatusResponse } from '@/types/api';

/**
 * Health service for checking API status and connectivity.
 */
export class HealthService extends BaseApiService {
  constructor() {
    super('');
  }

  /**
   * Check basic health status.
   */
  async checkHealth(): Promise<HealthResponse> {
    return this.get<HealthResponse>(API_ENDPOINTS.health);
  }

  /**
   * Get API information.
   */
  async getApiInfo(): Promise<ApiInfoResponse> {
    return this.get<ApiInfoResponse>(API_ENDPOINTS.api.info);
  }

  /**
   * Get detailed API status.
   */
  async getApiStatus(): Promise<ApiStatusResponse> {
    return this.get<ApiStatusResponse>(API_ENDPOINTS.api.status);
  }

  /**
   * Perform comprehensive health check.
   */
  async performHealthCheck(): Promise<{
    overall: 'healthy' | 'degraded' | 'unhealthy';
    checks: {
      api: { status: string; response_time: number; error?: string };
      database: { status: string; error?: string };
      services: { status: string; details: Record<string, string>; error?: string };
    };
    timestamp: string;
  }> {
    const startTime = Date.now();
    const checks = {
      api: { status: 'unknown', response_time: 0, error: undefined as string | undefined },
      database: { status: 'unknown', error: undefined as string | undefined },
      services: { status: 'unknown', details: {}, error: undefined as string | undefined },
    };

    try {
      // Check API health
      const healthResponse = await this.checkHealth();
      checks.api.status = healthResponse.status;
      checks.api.response_time = Date.now() - startTime;

      // Check database status
      if (healthResponse.database) {
        checks.database.status = healthResponse.database.status;
      }

      // Check services status
      if (healthResponse.services) {
        checks.services.status = 'healthy';
        checks.services.details = healthResponse.services;
      }
    } catch (error: any) {
      checks.api.status = 'unhealthy';
      checks.api.error = error.message;
      checks.api.response_time = Date.now() - startTime;
    }

    // Determine overall health
    let overall: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    
    if (checks.api.status === 'unhealthy') {
      overall = 'unhealthy';
    } else if (
      checks.database.status !== 'connected' ||
      checks.api.response_time > 5000
    ) {
      overall = 'degraded';
    }

    return {
      overall,
      checks,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Monitor health status with periodic checks.
   */
  startHealthMonitoring(
    interval: number = 30000,
    onStatusChange?: (status: any) => void
  ): () => void {
    let lastStatus: string | null = null;
    
    const checkAndNotify = async () => {
      try {
        const health = await this.performHealthCheck();
        
        if (health.overall !== lastStatus) {
          lastStatus = health.overall;
          onStatusChange?.(health);
        }
      } catch (error) {
        console.error('Health monitoring error:', error);
        
        if (lastStatus !== 'unhealthy') {
          lastStatus = 'unhealthy';
          onStatusChange?.({
            overall: 'unhealthy',
            error: error instanceof Error ? error.message : 'Unknown error',
            timestamp: new Date().toISOString(),
          });
        }
      }
    };

    // Initial check
    checkAndNotify();

    // Set up periodic checks
    const intervalId = setInterval(checkAndNotify, interval);

    // Return cleanup function
    return () => {
      clearInterval(intervalId);
    };
  }

  /**
   * Test connectivity with timeout.
   */
  async testConnectivity(timeout: number = 5000): Promise<{
    connected: boolean;
    responseTime: number;
    error?: string;
  }> {
    const startTime = Date.now();
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      await this.checkHealth();
      clearTimeout(timeoutId);
      
      return {
        connected: true,
        responseTime: Date.now() - startTime,
      };
    } catch (error: any) {
      return {
        connected: false,
        responseTime: Date.now() - startTime,
        error: error.message,
      };
    }
  }

  /**
   * Get service dependencies status.
   */
  async getDependenciesStatus(): Promise<Record<string, {
    status: 'available' | 'unavailable' | 'degraded';
    details?: any;
    last_check?: string;
  }>> {
    try {
      const status = await this.getApiStatus();
      const dependencies: Record<string, any> = {};
      
      if (status.services) {
        Object.entries(status.services).forEach(([service, serviceStatus]) => {
          dependencies[service] = {
            status: serviceStatus === 'configured' || serviceStatus === 'enabled' 
              ? 'available' 
              : 'unavailable',
            details: { raw_status: serviceStatus },
            last_check: new Date().toISOString(),
          };
        });
      }
      
      return dependencies;
    } catch (error) {
      console.error('Failed to get dependencies status:', error);
      return {};
    }
  }

  /**
   * Get system metrics.
   */
  async getSystemMetrics(): Promise<{
    uptime?: number;
    memory?: {
      used: number;
      total: number;
      percentage: number;
    };
    database?: {
      connections: number;
      queries_per_second: number;
      storage_used: number;
    };
    api?: {
      requests_per_minute: number;
      average_response_time: number;
      error_rate: number;
    };
  }> {
    try {
      const health = await this.checkHealth();
      
      return {
        uptime: health.uptime,
        database: health.database ? {
          connections: 1, // TinyDB is file-based
          queries_per_second: 0, // Not tracked
          storage_used: 0, // Not tracked
        } : undefined,
        api: {
          requests_per_minute: 0, // Not tracked yet
          average_response_time: 0, // Not tracked yet
          error_rate: 0, // Not tracked yet
        },
      };
    } catch (error) {
      console.error('Failed to get system metrics:', error);
      return {};
    }
  }
}

/**
 * Global health service instance.
 */
export const healthService = new HealthService();

/**
 * Health check utilities.
 */
export const healthUtils = {
  /**
   * Format response time for display.
   */
  formatResponseTime(ms: number): string {
    if (ms < 1000) {
      return `${ms}ms`;
    } else if (ms < 60000) {
      return `${(ms / 1000).toFixed(1)}s`;
    } else {
      return `${(ms / 60000).toFixed(1)}m`;
    }
  },

  /**
   * Get status color for UI.
   */
  getStatusColor(status: string): string {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'available':
        return 'green';
      case 'degraded':
      case 'warning':
        return 'yellow';
      case 'unhealthy':
      case 'disconnected':
      case 'unavailable':
      case 'error':
        return 'red';
      default:
        return 'gray';
    }
  },

  /**
   * Get status icon for UI.
   */
  getStatusIcon(status: string): string {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'available':
        return '✅';
      case 'degraded':
      case 'warning':
        return '⚠️';
      case 'unhealthy':
      case 'disconnected':
      case 'unavailable':
      case 'error':
        return '❌';
      default:
        return '❓';
    }
  },
};
