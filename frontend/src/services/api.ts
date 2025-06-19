/**
 * Base API service configuration and utilities.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, ErrorResponse } from '@/types/common';
import { getErrorMessage, isNetworkError, isTimeoutError } from '@utils/api';

/**
 * API configuration.
 */
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : 'http://localhost:8001'),
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '120000'), // 2 minutes default
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Create axios instance with default configuration.
 */
const createApiInstance = (): AxiosInstance => {
  const instance = axios.create(API_CONFIG);

  // Request interceptor
  instance.interceptors.request.use(
    (config) => {
      // Add request timestamp
      config.metadata = { startTime: Date.now() };
      
      // Add request ID for tracking
      config.headers['X-Request-ID'] = generateRequestId();
      
      // Log request in development
      if (import.meta.env.DEV) {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      }
      
      return config;
    },
    (error) => {
      console.error('❌ Request Error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      // Calculate request duration
      const duration = Date.now() - (response.config.metadata?.startTime || 0);
      
      // Log response in development
      if (import.meta.env.DEV) {
        console.log(
          `✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`
        );
      }
      
      return response;
    },
    (error) => {
      // Calculate request duration
      const duration = error.config?.metadata?.startTime 
        ? Date.now() - error.config.metadata.startTime 
        : 0;
      
      // Log error in development
      if (import.meta.env.DEV) {
        console.error(
          `❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`,
          error
        );
      }
      
      // Transform error for consistent handling
      const transformedError = transformApiError(error);
      return Promise.reject(transformedError);
    }
  );

  return instance;
};

/**
 * Generate a unique request ID.
 */
function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Transform API errors to a consistent format.
 */
function transformApiError(error: any): ApiError {
  const apiError = new ApiError(
    getErrorMessage(error),
    error.response?.status || 0,
    error.response?.data || null,
    error.config?.url || '',
    error.config?.method || ''
  );

  // Add error type classification
  if (isNetworkError(error)) {
    apiError.type = 'network';
  } else if (isTimeoutError(error)) {
    apiError.type = 'timeout';
  } else if (error.response?.status >= 400 && error.response?.status < 500) {
    apiError.type = 'client';
  } else if (error.response?.status >= 500) {
    apiError.type = 'server';
  } else {
    apiError.type = 'unknown';
  }

  return apiError;
}

/**
 * Custom API error class.
 */
export class ApiError extends Error {
  public type: 'network' | 'timeout' | 'client' | 'server' | 'unknown' = 'unknown';
  public status: number;
  public data: any;
  public url: string;
  public method: string;

  constructor(
    message: string,
    status: number = 0,
    data: any = null,
    url: string = '',
    method: string = ''
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.url = url;
    this.method = method;
  }

  /**
   * Check if error is a specific HTTP status.
   */
  isStatus(status: number): boolean {
    return this.status === status;
  }

  /**
   * Check if error is a client error (4xx).
   */
  isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  /**
   * Check if error is a server error (5xx).
   */
  isServerError(): boolean {
    return this.status >= 500;
  }

  /**
   * Get error details for debugging.
   */
  getDetails(): Record<string, any> {
    return {
      message: this.message,
      type: this.type,
      status: this.status,
      url: this.url,
      method: this.method,
      data: this.data,
    };
  }
}

/**
 * API client instance.
 */
export const apiClient = createApiInstance();

/**
 * Base API service class.
 */
export class BaseApiService {
  protected client: AxiosInstance;
  protected baseEndpoint: string;

  constructor(baseEndpoint: string, client: AxiosInstance = apiClient) {
    this.client = client;
    this.baseEndpoint = baseEndpoint;
  }

  /**
   * Build full endpoint URL.
   */
  protected buildUrl(path: string = ''): string {
    const cleanBase = this.baseEndpoint.replace(/\/$/, '');
    const cleanPath = path.replace(/^\//, '');
    return cleanPath ? `${cleanBase}/${cleanPath}` : cleanBase;
  }

  /**
   * Generic GET request.
   */
  protected async get<T>(
    path: string = '',
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.get<T>(this.buildUrl(path), config);
    return response.data;
  }

  /**
   * Generic POST request.
   */
  protected async post<T>(
    path: string = '',
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.post<T>(this.buildUrl(path), data, config);
    return response.data;
  }

  /**
   * Generic PUT request.
   */
  protected async put<T>(
    path: string = '',
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.put<T>(this.buildUrl(path), data, config);
    return response.data;
  }

  /**
   * Generic PATCH request.
   */
  protected async patch<T>(
    path: string = '',
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.patch<T>(this.buildUrl(path), data, config);
    return response.data;
  }

  /**
   * Generic DELETE request.
   */
  protected async delete<T>(
    path: string = '',
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.delete<T>(this.buildUrl(path), config);
    return response.data;
  }
}

/**
 * API endpoints configuration.
 */
export const API_ENDPOINTS = {
  health: '/health',
  api: {
    v1: '/api/v1',
    info: '/api/v1',
    status: '/api/v1/status',
  },
  projects: '/api/v1/projects',
  templates: '/api/v1/templates',
} as const;

/**
 * API response type guards.
 */
export function isApiResponse<T>(data: any): data is ApiResponse<T> {
  return (
    typeof data === 'object' &&
    data !== null &&
    'status' in data &&
    'message' in data &&
    'timestamp' in data
  );
}

export function isErrorResponse(data: any): data is ErrorResponse {
  return isApiResponse(data) && data.status === 'error';
}

/**
 * Environment configuration.
 */
export const API_ENV = {
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  baseUrl: import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : 'http://localhost:8001'),
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
} as const;

// Extend AxiosRequestConfig to include metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}
