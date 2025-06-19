/**
 * Common type definitions.
 */

/**
 * Generic API response wrapper.
 */
export interface ApiResponse<T = any> {
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  data?: T;
  timestamp: string;
  request_id?: string;
}

/**
 * Error response with additional details.
 */
export interface ErrorResponse extends ApiResponse<null> {
  status: 'error';
  error_code?: string;
  error_details?: Record<string, any>;
}

/**
 * Validation error details.
 */
export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

/**
 * Validation error response.
 */
export interface ValidationErrorResponse extends ErrorResponse {
  error_code: 'VALIDATION_ERROR';
  validation_errors: ValidationError[];
}

/**
 * Pagination metadata.
 */
export interface PaginationMeta {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

/**
 * Paginated response.
 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  meta: PaginationMeta;
}

/**
 * Health check response.
 */
export interface HealthCheckResponse {
  status: string;
  version: string;
  timestamp: string;
  uptime?: number;
  database: Record<string, any>;
  dependencies: Record<string, any>;
}

/**
 * Loading state.
 */
export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

/**
 * Async operation state.
 */
export interface AsyncState<T> extends LoadingState {
  data?: T | null;
}

/**
 * Form field state.
 */
export interface FieldState {
  value: string;
  error?: string;
  touched: boolean;
  dirty: boolean;
}

/**
 * Form state.
 */
export interface FormState<T extends Record<string, any>> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  dirty: boolean;
  isValid: boolean;
  isSubmitting: boolean;
}

/**
 * Sort direction.
 */
export type SortDirection = 'asc' | 'desc';

/**
 * Sort configuration.
 */
export interface SortConfig {
  field: string;
  direction: SortDirection;
}

/**
 * Filter configuration.
 */
export interface FilterConfig {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'startsWith' | 'endsWith';
  value: any;
}

/**
 * Search parameters.
 */
export interface SearchParams {
  query?: string;
  sort?: SortConfig;
  filters?: FilterConfig[];
  page?: number;
  per_page?: number;
}

/**
 * Theme configuration.
 */
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'system';
  primaryColor: string;
  accentColor: string;
}

/**
 * User preferences.
 */
export interface UserPreferences {
  theme: ThemeConfig;
  sidebarCollapsed: boolean;
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
  };
}

/**
 * Navigation item.
 */
export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon?: React.ComponentType<any>;
  badge?: string | number;
  children?: NavItem[];
  disabled?: boolean;
}

/**
 * Breadcrumb item.
 */
export interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}

/**
 * Toast notification.
 */
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * Modal configuration.
 */
export interface ModalConfig {
  id: string;
  title: string;
  content: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closable?: boolean;
  onClose?: () => void;
}

/**
 * File upload state.
 */
export interface FileUploadState {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

/**
 * Key-value pair.
 */
export interface KeyValuePair<T = string> {
  key: string;
  value: T;
}

/**
 * Option for select components.
 */
export interface SelectOption<T = string> {
  label: string;
  value: T;
  disabled?: boolean;
  description?: string;
}

/**
 * Tab configuration.
 */
export interface TabConfig {
  id: string;
  label: string;
  content: React.ReactNode;
  disabled?: boolean;
  badge?: string | number;
}

/**
 * Chart data point.
 */
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

/**
 * Time range.
 */
export interface TimeRange {
  start: Date;
  end: Date;
}

/**
 * Coordinate point.
 */
export interface Point {
  x: number;
  y: number;
}

/**
 * Dimensions.
 */
export interface Dimensions {
  width: number;
  height: number;
}

/**
 * Rectangle.
 */
export interface Rectangle extends Point, Dimensions {}

/**
 * Color palette.
 */
export interface ColorPalette {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  neutral: string;
}

/**
 * Project status enumeration.
 */
export const ProjectStatus = {
  DRAFT: 'draft',
  ACTIVE: 'active',
  COMPLETED: 'completed',
  ARCHIVED: 'archived',
  CANCELLED: 'cancelled'
} as const;

export type ProjectStatus = typeof ProjectStatus[keyof typeof ProjectStatus];

/**
 * Base project interface.
 */
export interface ProjectBase {
  name: string;
  description: string;
  requirements: string;
  status: ProjectStatus;
  tags: string[];
  tech_stack: string[];
  metadata?: Record<string, any>;
}

/**
 * Project creation interface.
 */
export interface ProjectCreate extends ProjectBase {
  // All fields from ProjectBase are required for creation
}



/**
 * Full project interface with system fields.
 */
export interface Project extends ProjectBase {
  id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Project list response.
 */
export interface ProjectsResponse {
  projects: Project[];
  count: number;
  timestamp: number;
}

/**
 * Project creation response.
 */
export interface ProjectCreateResponse {
  message: string;
  project: Project;
  doc_id: number;
  timestamp: number;
  analysis_triggered: boolean;
}

/**
 * Project analysis status enumeration.
 */
export const AnalysisStatus = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const;

export type AnalysisStatus = typeof AnalysisStatus[keyof typeof AnalysisStatus];



/**
 * Project analysis workflow stage.
 */
export interface AnalysisWorkflowStage {
  stage_id: string;
  name: string;
  description: string;
  required_agents: string[];
  optional_agents: string[];
  status: AnalysisStatus;
  started_at?: string;
  completed_at?: string;
  estimated_duration: number;
  actual_duration?: number;
  dependencies: string[]; // Other stage IDs this stage depends on
  outputs: Record<string, any>;
  quality_score?: number;
}





/**
 * Project overview generation request.
 */
export interface ProjectOverviewRequest {
  project_id: string;
  selected_agents: string[];
  generation_options: {
    include_technical_details: boolean;
    include_timeline: boolean;
    include_risk_assessment: boolean;
    include_resource_requirements: boolean;
    detail_level: 'basic' | 'detailed' | 'comprehensive';
    output_format: 'markdown' | 'json' | 'pdf' | 'html';
  };
  user_preferences?: {
    focus_areas: string[];
    excluded_sections: string[];
    custom_requirements: string[];
  };
}



/**
 * Project file type enumeration.
 */
export const ProjectFileType = {
  PROJECT_OVERVIEW: 'project_overview',
  TASK_FILE: 'task_file',
  TASKS_INDEX: 'tasks_index',
  GENERATED_FILE: 'generated_file'
} as const;

export type ProjectFileType = typeof ProjectFileType[keyof typeof ProjectFileType];

/**
 * Project file status enumeration.
 */
export const ProjectFileStatus = {
  GENERATED: 'generated',
  REVIEWED: 'reviewed',
  APPROVED: 'approved',
  ARCHIVED: 'archived'
} as const;

export type ProjectFileStatus = typeof ProjectFileStatus[keyof typeof ProjectFileStatus];

/**
 * Project file metadata.
 */
export interface ProjectFileMetadata {
  agents_used: string[];
  generation_context: Record<string, any>;
  file_size?: number;
  task_number?: number;
  is_primary: boolean;
}

/**
 * Base project file interface.
 */
export interface ProjectFileBase {
  project_id: string;
  orchestration_id?: string;
  session_id?: string;
  file_type: ProjectFileType;
  file_name: string;
  content: string;
  metadata: ProjectFileMetadata;
  status: ProjectFileStatus;
}

/**
 * Project file creation interface.
 */
export interface ProjectFileCreate extends ProjectFileBase {
  // All fields from ProjectFileBase are required for creation
}

/**
 * Project file update interface.
 */
export interface ProjectFileUpdate {
  file_name?: string;
  content?: string;
  metadata?: ProjectFileMetadata;
  status?: ProjectFileStatus;
}

/**
 * Full project file interface with system fields.
 */
export interface ProjectFile extends ProjectFileBase {
  id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Project files response.
 */
export interface ProjectFilesResponse {
  files: ProjectFile[];
  count: number;
  timestamp: number;
}

/**
 * Project overview and tasks response.
 */
export interface ProjectOverviewAndTasksResponse {
  overview?: ProjectFile;
  tasks: ProjectFile[];
  total_files: number;
  last_updated?: string;
}
