/**
 * API-specific type definitions.
 */

/**
 * API endpoint paths.
 */
export interface ApiEndpoints {
  health: string;
  api: {
    v1: string;
    info: string;
    status: string;
  };
  projects: string;
  sessions: string;
  templates: string;
}

/**
 * API request configuration.
 */
export interface ApiRequestConfig {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  cache?: boolean;
  cacheKey?: string;
  cacheTTL?: number;
}

/**
 * API client configuration.
 */
export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
  retries: number;
  retryDelay: number;
}

/**
 * Health check response.
 */
export interface HealthResponse {
  status: string;
  timestamp: number;
  version: string;
  service: string;
  uptime?: number;
  database?: {
    status: string;
    projects_count: number;
    sessions_count: number;
    templates_count: number;
  };
  services?: {
    gemini_api: string;
    crewai: string;
  };
}

/**
 * API info response.
 */
export interface ApiInfoResponse {
  api_version: string;
  service: string;
  version: string;
  timestamp: number;
  endpoints: {
    projects: string;
    sessions: string;
    templates: string;
    agents: string;
  };
}

/**
 * API status response.
 */
export interface ApiStatusResponse {
  status: string;
  timestamp: number;
  database: {
    status: string;
    projects_count: number;
    sessions_count: number;
    templates_count: number;
  };
  services: {
    gemini_api: string;
    crewai: string;
  };
}

/**
 * Error response details.
 */
export interface ApiErrorDetails {
  field?: string;
  code?: string;
  message?: string;
  value?: any;
}

/**
 * API error response.
 */
export interface ApiErrorResponse {
  status: 'error';
  message: string;
  error_code?: string;
  error_details?: ApiErrorDetails;
  timestamp: string;
  request_id?: string;
}

/**
 * API validation error response.
 */
export interface ApiValidationErrorResponse extends ApiErrorResponse {
  error_code: 'VALIDATION_ERROR';
  validation_errors: Array<{
    field: string;
    message: string;
    value?: any;
  }>;
}

/**
 * Rate limit error response.
 */
export interface RateLimitErrorResponse extends ApiErrorResponse {
  error_code: 'RATE_LIMIT_EXCEEDED';
  retry_after?: number;
}

/**
 * Authentication error response.
 */
export interface AuthErrorResponse extends ApiErrorResponse {
  error_code: 'UNAUTHORIZED' | 'FORBIDDEN';
}

/**
 * Not found error response.
 */
export interface NotFoundErrorResponse extends ApiErrorResponse {
  error_code: 'NOT_FOUND';
  resource_type?: string;
  resource_id?: string;
}

/**
 * Server error response.
 */
export interface ServerErrorResponse extends ApiErrorResponse {
  error_code: 'INTERNAL_SERVER_ERROR' | 'SERVICE_UNAVAILABLE';
  incident_id?: string;
}

/**
 * API request metadata.
 */
export interface RequestMetadata {
  startTime: number;
  endTime?: number;
  duration?: number;
  requestId?: string;
  retryCount?: number;
}

/**
 * API response metadata.
 */
export interface ResponseMetadata {
  requestId?: string;
  duration: number;
  cached?: boolean;
  retryCount?: number;
}

/**
 * Pagination request parameters.
 */
export interface PaginationParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * Search request parameters.
 */
export interface ApiSearchParams extends PaginationParams {
  query?: string;
  filters?: Record<string, any>;
}

/**
 * Bulk operation request.
 */
export interface BulkOperationRequest<T> {
  operation: 'create' | 'update' | 'delete';
  items: T[];
  options?: {
    validate?: boolean;
    stop_on_error?: boolean;
    return_results?: boolean;
  };
}

/**
 * Bulk operation response.
 */
export interface BulkOperationResponse<T> {
  total: number;
  successful: number;
  failed: number;
  results?: Array<{
    index: number;
    status: 'success' | 'error';
    data?: T;
    error?: string;
  }>;
  errors?: Array<{
    index: number;
    error: string;
    details?: any;
  }>;
}

/**
 * File upload request.
 */
export interface FileUploadRequest {
  file: File;
  filename?: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

/**
 * File upload response.
 */
export interface FileUploadResponse {
  id: string;
  filename: string;
  size: number;
  mime_type: string;
  url: string;
  thumbnail_url?: string;
  metadata?: Record<string, any>;
  uploaded_at: string;
}

/**
 * Export request parameters.
 */
export interface ExportParams {
  format: 'json' | 'csv' | 'xlsx' | 'pdf';
  filters?: Record<string, any>;
  fields?: string[];
  options?: Record<string, any>;
}

/**
 * Export response.
 */
export interface ExportResponse {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  format: string;
  download_url?: string;
  expires_at?: string;
  created_at: string;
  progress?: number;
  error?: string;
}

/**
 * WebSocket message types.
 */
export interface WebSocketMessage<T = any> {
  type: string;
  data: T;
  timestamp: string;
  id?: string;
}

/**
 * Real-time update message.
 */
export interface RealtimeUpdateMessage extends WebSocketMessage {
  type: 'update' | 'create' | 'delete';
  resource_type: string;
  resource_id: string;
  data: any;
}

/**
 * Notification message.
 */
export interface NotificationMessage extends WebSocketMessage {
  type: 'notification';
  data: {
    title: string;
    message: string;
    level: 'info' | 'success' | 'warning' | 'error';
    action?: {
      label: string;
      url: string;
    };
  };
}

/**
 * Progress update message.
 */
export interface ProgressUpdateMessage extends WebSocketMessage {
  type: 'progress';
  data: {
    operation_id: string;
    progress: number;
    status: string;
    message?: string;
    eta?: number;
  };
}

/**
 * API cache configuration.
 */
export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live in seconds
  maxSize: number; // Maximum cache size in MB
  strategy: 'lru' | 'fifo' | 'ttl';
}

/**
 * API retry configuration.
 */
export interface RetryConfig {
  enabled: boolean;
  maxRetries: number;
  baseDelay: number; // Base delay in milliseconds
  maxDelay: number; // Maximum delay in milliseconds
  backoffFactor: number;
  retryCondition: (error: any) => boolean;
}
