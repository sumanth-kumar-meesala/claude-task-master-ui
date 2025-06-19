/**
 * Projects API service.
 */

import { BaseApiService } from './api';
import {
  ApiResponse,
  Project,
  ProjectCreate,
  ProjectsResponse,
  ProjectCreateResponse,
  ProjectStatus,
  ProjectAnalysis,
  AnalysisStatus,
  SelectedAgent
} from '@/types/common';

/**
 * Project update interface.
 */
export interface ProjectUpdate {
  name?: string;
  description?: string;
  requirements?: string;
  status?: ProjectStatus;
  tags?: string[];
  metadata?: Record<string, any>;
  selected_agents?: SelectedAgent[];
}

/**
 * Project query parameters.
 */
export interface ProjectQueryParams {
  status?: ProjectStatus;
  tags?: string[];
  search?: string;
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

/**
 * Projects service class.
 */
export class ProjectsService extends BaseApiService {
  constructor() {
    super('/api/v1/projects');
  }

  /**
   * Get all projects with optional filtering.
   */
  async getProjects(params?: ProjectQueryParams): Promise<ProjectsResponse> {
    const queryParams = new URLSearchParams();
    
    if (params) {
      if (params.status) queryParams.append('status', params.status);
      if (params.tags?.length) queryParams.append('tags', params.tags.join(','));
      if (params.search) queryParams.append('search', params.search);
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.limit) queryParams.append('limit', params.limit.toString());
      if (params.sort) queryParams.append('sort', params.sort);
      if (params.order) queryParams.append('order', params.order);
    }

    const queryString = queryParams.toString();
    const path = queryString ? `?${queryString}` : '';
    
    return this.get<ProjectsResponse>(path);
  }

  /**
   * Get a specific project by ID.
   */
  async getProject(projectId: string): Promise<ApiResponse<Project>> {
    const response = await this.get<any>(`/${projectId}`);
    // Handle the backend response format where project data is under 'project' key
    if (response.project) {
      return {
        data: response.project,
        status: 'success',
        message: 'Project retrieved successfully',
        timestamp: response.timestamp || Date.now()
      };
    }
    return response;
  }

  /**
   * Create a new project.
   */
  async createProject(projectData: ProjectCreate): Promise<ProjectCreateResponse> {
    // Generate a unique ID for the project
    const projectWithId = {
      ...projectData,
      id: `proj_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      agents_involved: [],
      file_structure: {},
      tasks: [],
      session_data: {}
    };

    return this.post<ProjectCreateResponse>('', projectWithId);
  }

  /**
   * Update an existing project.
   */
  async updateProject(projectId: string, updates: ProjectUpdate): Promise<ApiResponse<Project>> {
    const updateData = {
      ...updates,
      updated_at: new Date().toISOString()
    };

    return this.put<ApiResponse<Project>>(`/${projectId}`, updateData);
  }

  /**
   * Delete a project.
   */
  async deleteProject(projectId: string): Promise<ApiResponse<null>> {
    return this.delete<ApiResponse<null>>(`/${projectId}`);
  }

  /**
   * Archive a project.
   */
  async archiveProject(projectId: string): Promise<ApiResponse<Project>> {
    return this.updateProject(projectId, { status: ProjectStatus.ARCHIVED });
  }

  /**
   * Restore an archived project.
   */
  async restoreProject(projectId: string): Promise<ApiResponse<Project>> {
    return this.updateProject(projectId, { status: ProjectStatus.ACTIVE });
  }

  /**
   * Get project statistics.
   */
  async getProjectStats(): Promise<ApiResponse<{
    total: number;
    by_status: Record<ProjectStatus, number>;
    recent_count: number;
  }>> {
    return this.get<ApiResponse<{
      total: number;
      by_status: Record<ProjectStatus, number>;
      recent_count: number;
    }>>('/stats');
  }

  /**
   * Search projects by name or description.
   */
  async searchProjects(query: string, limit = 10): Promise<ApiResponse<Project[]>> {
    const params = new URLSearchParams({
      search: query,
      limit: limit.toString()
    });

    return this.get<ApiResponse<Project[]>>(`/search?${params.toString()}`);
  }

  /**
   * Get projects by tag.
   */
  async getProjectsByTag(tag: string): Promise<ApiResponse<Project[]>> {
    return this.get<ApiResponse<Project[]>>(`/tags/${encodeURIComponent(tag)}`);
  }

  /**
   * Get all unique tags used in projects.
   */
  async getProjectTags(): Promise<ApiResponse<string[]>> {
    return this.get<ApiResponse<string[]>>('/tags');
  }

  /**
   * Duplicate a project.
   */
  async duplicateProject(projectId: string, newName?: string): Promise<ProjectCreateResponse> {
    const originalProject = await this.getProject(projectId);

    if (originalProject.data) {
      const duplicateData: ProjectCreate = {
        name: newName || `${originalProject.data.name} (Copy)`,
        description: originalProject.data.description,
        requirements: originalProject.data.requirements,
        status: ProjectStatus.DRAFT,
        tags: [...originalProject.data.tags],
        tech_stack: originalProject.data.tech_stack || [],
        metadata: { ...originalProject.data.metadata, duplicated_from: projectId }
      };

      return this.createProject(duplicateData);
    }

    throw new Error('Failed to fetch original project for duplication');
  }

  /**
   * Get project analysis status and results.
   */
  async getProjectAnalysis(projectId: string): Promise<ProjectAnalysis> {
    return this.get<ProjectAnalysis>(`/${projectId}/analysis`);
  }

  /**
   * Trigger manual analysis for a project.
   */
  async triggerProjectAnalysis(projectId: string): Promise<ApiResponse<{
    message: string;
    project_id: string;
    status: string;
    timestamp: number;
  }>> {
    return this.post<ApiResponse<{
      message: string;
      project_id: string;
      status: string;
      timestamp: number;
    }>>(`/${projectId}/analyze`);
  }

  /**
   * Check if project has analysis in progress.
   */
  async isAnalysisInProgress(projectId: string): Promise<boolean> {
    try {
      const analysis = await this.getProjectAnalysis(projectId);
      return analysis.analysis_status === AnalysisStatus.IN_PROGRESS;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get analysis progress for a project.
   */
  async getAnalysisProgress(projectId: string): Promise<{
    status: AnalysisStatus;
    progress: number;
    message: string;
    agents_involved: string[];
  }> {
    const analysis = await this.getProjectAnalysis(projectId);

    let progress = 0;
    let message = '';

    switch (analysis.analysis_status) {
      case AnalysisStatus.NOT_STARTED:
        progress = 0;
        message = 'Analysis not started';
        break;
      case AnalysisStatus.IN_PROGRESS:
        progress = 50; // Approximate progress
        message = 'AI agents are analyzing your project...';
        break;
      case AnalysisStatus.COMPLETED:
        progress = 100;
        message = 'Analysis completed successfully';
        break;
      case AnalysisStatus.FAILED:
        progress = 0;
        message = `Analysis failed: ${analysis.error || 'Unknown error'}`;
        break;
    }

    return {
      status: analysis.analysis_status,
      progress,
      message,
      agents_involved: analysis.agents_involved
    };
  }
}

/**
 * Default projects service instance.
 */
export const projectsService = new ProjectsService();

/**
 * Project validation utilities.
 */
export const projectValidation = {
  /**
   * Validate project name.
   */
  validateName: (name: string): string | null => {
    if (!name || name.trim().length === 0) {
      return 'Project name is required';
    }
    if (name.length > 200) {
      return 'Project name must be less than 200 characters';
    }
    return null;
  },

  /**
   * Validate project description.
   */
  validateDescription: (description?: string): string | null => {
    if (description && description.length > 2000) {
      return 'Description must be less than 2000 characters';
    }
    return null;
  },

  /**
   * Validate project tags.
   */
  validateTags: (tags: string[]): string | null => {
    if (tags.length > 20) {
      return 'Maximum 20 tags allowed';
    }
    
    for (const tag of tags) {
      if (tag.length > 50) {
        return 'Each tag must be less than 50 characters';
      }
    }
    
    return null;
  },

  /**
   * Validate complete project data.
   */
  validateProject: (project: Partial<ProjectCreate>): Record<string, string> => {
    const errors: Record<string, string> = {};

    const nameError = projectValidation.validateName(project.name || '');
    if (nameError) errors.name = nameError;

    const descError = projectValidation.validateDescription(project.description);
    if (descError) errors.description = descError;

    const tagsError = projectValidation.validateTags(project.tags || []);
    if (tagsError) errors.tags = tagsError;

    return errors;
  }
};
