/**
 * Task Master Service
 * API service for task generation using claude-task-master integration
 */

import axios from 'axios';

const API_BASE_URL = '/api/v1/task-generation';

export interface PRDParseRequest {
  project_id: string;
  prd_content: string;
  num_tasks?: number;
  research?: boolean;
  force?: boolean;
  append?: boolean;
}

export interface TaskGenerationResponse {
  success: boolean;
  message: string;
  project_id?: string;
  tasks_count?: number;
  tasks?: any;
  error?: string;
}

export interface ProjectInitRequest {
  project_id: string;
  project_name?: string;
}

export interface ProjectStatus {
  success: boolean;
  project_id: string;
  task_master_initialized: boolean;
  tasks_generated: boolean;
  tasks_count: number;
  last_task_generation?: string;
  task_master_path?: string;
}

export interface PRDGenerationResponse {
  success: boolean;
  project_id: string;
  prd_content: string;
  project_name: string;
  has_existing_overview: boolean;
  generated_at: string;
  suggestions: string[];
  completeness_score: number;
  message: string;
}

class TaskMasterService {
  /**
   * Initialize a task-master project
   */
  async initializeProject(request: ProjectInitRequest): Promise<TaskGenerationResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/initialize-project`, request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to initialize project');
    }
  }

  /**
   * Parse PRD and generate tasks
   */
  async parsePRD(request: PRDParseRequest): Promise<TaskGenerationResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/parse-prd`, request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to parse PRD');
    }
  }

  /**
   * Get all tasks for a project
   */
  async getProjectTasks(projectId: string): Promise<TaskGenerationResponse> {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/${projectId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get tasks');
    }
  }

  /**
   * Get task markdown files
   */
  async getTaskMarkdownFiles(projectId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/task-markdown-files/${projectId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get task markdown files');
    }
  }

  /**
   * Get the next task to work on
   */
  async getNextTask(projectId: string): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL}/next-task/${projectId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get next task');
    }
  }

  /**
   * Get project status
   */
  async getProjectStatus(projectId: string): Promise<ProjectStatus> {
    try {
      const response = await axios.get(`${API_BASE_URL}/project-status/${projectId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get project status');
    }
  }

  /**
   * Generate PRD content from existing project data
   */
  async generatePRDContent(projectId: string): Promise<PRDGenerationResponse> {
    try {
      const response = await axios.get(`${API_BASE_URL}/generate-prd/${projectId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to generate PRD content');
    }
  }

  /**
   * Parse PRD with streaming progress updates
   */
  async parsePRDStream(
    projectId: string, 
    request: PRDParseRequest,
    onProgress: (data: any) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/parse-prd-stream/${projectId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Failed to get response reader');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete lines
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onProgress(data);
            } catch (e) {
              console.warn('Failed to parse SSE data:', line);
            }
          }
        }
      }
    } catch (error: any) {
      throw new Error(error.message || 'Failed to stream PRD parsing');
    }
  }
}

export const taskMasterService = new TaskMasterService();
export default taskMasterService;
