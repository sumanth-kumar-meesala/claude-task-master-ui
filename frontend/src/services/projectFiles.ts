/**
 * Project Files API service.
 */

import { BaseApiService } from './api';
import {
  ApiResponse,
  ProjectFile,
  ProjectFileCreate,
  ProjectFileUpdate,
  ProjectFileType,
  ProjectFileStatus,
  ProjectOverviewAndTasksResponse
} from '@/types/common';

/**
 * Project files query parameters.
 */
export interface ProjectFilesQueryParams {
  project_id?: string;
  file_type?: ProjectFileType;
  status?: ProjectFileStatus;
  limit?: number;
}

/**
 * Project files service class.
 */
export class ProjectFilesService extends BaseApiService {
  constructor() {
    super('/api/v1/project-files');
  }

  /**
   * Get all project files with optional filtering.
   */
  async getProjectFiles(params?: ProjectFilesQueryParams): Promise<ProjectFile[]> {
    const queryParams = new URLSearchParams();
    
    if (params) {
      if (params.project_id) queryParams.append('project_id', params.project_id);
      if (params.file_type) queryParams.append('file_type', params.file_type);
      if (params.status) queryParams.append('status', params.status);
      if (params.limit) queryParams.append('limit', params.limit.toString());
    }

    const queryString = queryParams.toString();
    const path = queryString ? `?${queryString}` : '';
    
    return this.get<ProjectFile[]>(path);
  }

  /**
   * Get a specific project file by ID.
   */
  async getProjectFile(fileId: string): Promise<ProjectFile> {
    return this.get<ProjectFile>(`/${fileId}`);
  }

  /**
   * Create a new project file.
   */
  async createProjectFile(fileData: ProjectFileCreate): Promise<ProjectFile> {
    return this.post<ProjectFile>('', fileData);
  }

  /**
   * Update an existing project file.
   */
  async updateProjectFile(fileId: string, updates: ProjectFileUpdate): Promise<ProjectFile> {
    return this.put<ProjectFile>(`/${fileId}`, updates);
  }

  /**
   * Delete a project file.
   */
  async deleteProjectFile(fileId: string): Promise<ApiResponse<{ message: string; file_id: string }>> {
    return this.delete<ApiResponse<{ message: string; file_id: string }>>(`/${fileId}`);
  }

  /**
   * Get the primary project overview for a project.
   */
  async getProjectOverview(projectId: string): Promise<ProjectFile | null> {
    try {
      const response = await this.get<ProjectFile>(`/project/${projectId}/overview`);
      return response;
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  /**
   * Get all task files for a project.
   */
  async getProjectTasks(projectId: string): Promise<ProjectFile[]> {
    return this.get<ProjectFile[]>(`/project/${projectId}/tasks`);
  }

  /**
   * Get both overview and tasks for a project.
   */
  async getProjectOverviewAndTasks(projectId: string): Promise<ProjectOverviewAndTasksResponse> {
    try {
      const [overview, tasks] = await Promise.all([
        this.getProjectOverview(projectId),
        this.getProjectTasks(projectId)
      ]);

      const lastUpdated = overview?.updated_at || 
        (tasks.length > 0 ? Math.max(...tasks.map(t => new Date(t.updated_at).getTime())) : undefined);

      return {
        overview: overview || undefined,
        tasks,
        total_files: (overview ? 1 : 0) + tasks.length,
        last_updated: lastUpdated ? new Date(lastUpdated).toISOString() : undefined
      };
    } catch (error) {
      console.error('Failed to get project overview and tasks:', error);
      throw error;
    }
  }

  /**
   * Get files by project ID (convenience method).
   */
  async getFilesByProject(projectId: string): Promise<ProjectFile[]> {
    return this.getProjectFiles({ project_id: projectId });
  }

  /**
   * Get files by type for a project.
   */
  async getFilesByType(projectId: string, fileType: ProjectFileType): Promise<ProjectFile[]> {
    return this.getProjectFiles({ project_id: projectId, file_type: fileType });
  }

  /**
   * Check if a project has any generated files.
   */
  async hasGeneratedFiles(projectId: string): Promise<boolean> {
    try {
      const files = await this.getFilesByProject(projectId);
      return files.length > 0;
    } catch (error) {
      console.error('Failed to check for generated files:', error);
      return false;
    }
  }

  /**
   * Get the latest files for a project (most recently updated).
   */
  async getLatestFiles(projectId: string, limit = 5): Promise<ProjectFile[]> {
    try {
      const files = await this.getFilesByProject(projectId);
      return files
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, limit);
    } catch (error) {
      console.error('Failed to get latest files:', error);
      return [];
    }
  }

  /**
   * Search files by content (client-side search).
   */
  async searchFiles(projectId: string, searchTerm: string): Promise<ProjectFile[]> {
    try {
      const files = await this.getFilesByProject(projectId);
      const lowercaseSearch = searchTerm.toLowerCase();
      
      return files.filter(file => 
        file.file_name.toLowerCase().includes(lowercaseSearch) ||
        file.content.toLowerCase().includes(lowercaseSearch)
      );
    } catch (error) {
      console.error('Failed to search files:', error);
      return [];
    }
  }

  /**
   * Get file statistics for a project.
   */
  async getProjectFileStats(projectId: string): Promise<{
    total_files: number;
    by_type: Record<ProjectFileType, number>;
    by_status: Record<ProjectFileStatus, number>;
    total_size: number;
    last_updated?: string;
  }> {
    try {
      const files = await this.getFilesByProject(projectId);
      
      const stats = {
        total_files: files.length,
        by_type: {} as Record<ProjectFileType, number>,
        by_status: {} as Record<ProjectFileStatus, number>,
        total_size: 0,
        last_updated: undefined as string | undefined
      };

      // Initialize counters
      Object.values(ProjectFileType).forEach(type => {
        stats.by_type[type] = 0;
      });
      Object.values(ProjectFileStatus).forEach(status => {
        stats.by_status[status] = 0;
      });

      // Calculate statistics
      files.forEach(file => {
        stats.by_type[file.file_type]++;
        stats.by_status[file.status]++;
        stats.total_size += file.metadata.file_size || file.content.length;
      });

      // Find most recent update
      if (files.length > 0) {
        const latestUpdate = Math.max(...files.map(f => new Date(f.updated_at).getTime()));
        stats.last_updated = new Date(latestUpdate).toISOString();
      }

      return stats;
    } catch (error) {
      console.error('Failed to get project file stats:', error);
      return {
        total_files: 0,
        by_type: {} as Record<ProjectFileType, number>,
        by_status: {} as Record<ProjectFileStatus, number>,
        total_size: 0
      };
    }
  }
}

/**
 * Default project files service instance.
 */
export const projectFilesService = new ProjectFilesService();

/**
 * Project file validation utilities.
 */
export const projectFileValidation = {
  /**
   * Validate file name.
   */
  validateFileName: (fileName: string): string | null => {
    if (!fileName || fileName.trim().length === 0) {
      return 'File name is required';
    }
    if (fileName.length > 255) {
      return 'File name must be less than 255 characters';
    }
    if (!/^[a-zA-Z0-9._-]+\.(md|txt|json|yaml|yml)$/.test(fileName)) {
      return 'File name must be valid and end with .md, .txt, .json, .yaml, or .yml';
    }
    return null;
  },

  /**
   * Validate file content.
   */
  validateContent: (content: string): string | null => {
    if (!content || content.trim().length === 0) {
      return 'File content is required';
    }
    if (content.length > 1000000) { // 1MB limit
      return 'File content must be less than 1MB';
    }
    return null;
  },

  /**
   * Validate complete project file data.
   */
  validateProjectFile: (file: Partial<ProjectFileCreate>): Record<string, string> => {
    const errors: Record<string, string> = {};

    if (!file.project_id) {
      errors.project_id = 'Project ID is required';
    }

    if (!file.file_type) {
      errors.file_type = 'File type is required';
    }

    const nameError = projectFileValidation.validateFileName(file.file_name || '');
    if (nameError) errors.file_name = nameError;

    const contentError = projectFileValidation.validateContent(file.content || '');
    if (contentError) errors.content = contentError;

    return errors;
  }
};
