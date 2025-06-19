/**
 * Task Display Panel Component
 * Displays generated tasks in organized, expandable panels with management functionality
 */

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { taskMasterService } from '../../services/taskMasterService';
import { projectFilesService } from '../../services/projectFiles';

interface Task {
  id: number;
  title: string;
  description: string;
  details?: string;
  testStrategy?: string;
  priority: 'high' | 'medium' | 'low';
  status: string;
  dependencies?: number[];
  subtasks?: any[];
}

interface TaskFile {
  filename: string;
  task_id: string;
  content: string;
  file_path: string;
}

interface TaskDisplayPanelProps {
  projectId: string;
  tasks?: any;
  onTaskUpdate?: (taskId: number, updates: Partial<Task>) => void;
}

const TaskDisplayPanel: React.FC<TaskDisplayPanelProps> = ({
  projectId,
  tasks: initialTasks,
  onTaskUpdate: _onTaskUpdate
}) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [taskFiles, setTaskFiles] = useState<TaskFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [sortBy, setSortBy] = useState<'id' | 'priority' | 'status'>('id');
  const [expandedTasks, setExpandedTasks] = useState<Set<number>>(new Set());
  const [showMarkdown, setShowMarkdown] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (initialTasks?.master?.tasks) {
      setTasks(initialTasks.master.tasks);
    } else {
      loadTasks();
    }
    loadTaskFiles();
  }, [projectId, initialTasks]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await taskMasterService.getProjectTasks(projectId);
      if (response.success && response.tasks?.master?.tasks) {
        setTasks(response.tasks.master.tasks);
      }
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTaskFiles = async () => {
    try {
      const response = await taskMasterService.getTaskMarkdownFiles(projectId);
      if (response.success) {
        setTaskFiles(response.markdown_files);
      }
    } catch (error) {
      console.error('Failed to load task files:', error);
    }
  };

  const filteredAndSortedTasks = tasks
    .filter(task => filter === 'all' || task.priority === filter)
    .sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        case 'status':
          return a.status.localeCompare(b.status);
        default:
          return a.id - b.id;
      }
    });

  const toggleTaskExpansion = (taskId: number) => {
    const newExpanded = new Set(expandedTasks);
    if (newExpanded.has(taskId)) {
      newExpanded.delete(taskId);
    } else {
      newExpanded.add(taskId);
    }
    setExpandedTasks(newExpanded);
  };

  const toggleMarkdownView = (taskId: number) => {
    const newShowMarkdown = new Set(showMarkdown);
    if (newShowMarkdown.has(taskId)) {
      newShowMarkdown.delete(taskId);
    } else {
      newShowMarkdown.add(taskId);
    }
    setShowMarkdown(newShowMarkdown);
  };

  const getTaskFile = (taskId: number): TaskFile | undefined => {
    return taskFiles.find(file => file.task_id === taskId.toString());
  };

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'badge-error';
      case 'medium':
        return 'badge-warning';
      case 'low':
        return 'badge-info';
      default:
        return 'badge-neutral';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'done':
      case 'completed':
        return 'badge-success';
      case 'in-progress':
      case 'in_progress':
        return 'badge-warning';
      case 'blocked':
        return 'badge-error';
      default:
        return 'badge-neutral';
    }
  };

  const getTaskStats = () => {
    const total = tasks.length;
    const byPriority = {
      high: tasks.filter(t => t.priority === 'high').length,
      medium: tasks.filter(t => t.priority === 'medium').length,
      low: tasks.filter(t => t.priority === 'low').length
    };
    const byStatus = {
      pending: tasks.filter(t => t.status === 'pending').length,
      inProgress: tasks.filter(t => t.status === 'in-progress').length,
      done: tasks.filter(t => t.status === 'done').length
    };
    return { total, byPriority, byStatus };
  };

  const stats = getTaskStats();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-base-content/50 mb-4">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2">No Tasks Generated</h3>
        <p className="text-base-content/70">Generate tasks from your PRD to see them here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Task Statistics */}
      <div className="stats shadow w-full">
        <div className="stat">
          <div className="stat-title">Total Tasks</div>
          <div className="stat-value text-primary">{stats.total}</div>
        </div>
        
        <div className="stat">
          <div className="stat-title">High Priority</div>
          <div className="stat-value text-error">{stats.byPriority.high}</div>
        </div>
        
        <div className="stat">
          <div className="stat-title">Medium Priority</div>
          <div className="stat-value text-warning">{stats.byPriority.medium}</div>
        </div>
        
        <div className="stat">
          <div className="stat-title">Low Priority</div>
          <div className="stat-value text-info">{stats.byPriority.low}</div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          <div className="flex flex-wrap items-center gap-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Filter by Priority</span>
              </label>
              <select 
                className="select select-bordered select-sm"
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
              >
                <option value="all">All Priorities</option>
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="low">Low Priority</option>
              </select>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Sort by</span>
              </label>
              <select 
                className="select select-bordered select-sm"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="id">Task ID</option>
                <option value="priority">Priority</option>
                <option value="status">Status</option>
              </select>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Actions</span>
              </label>
              <div className="flex gap-2">
                <button 
                  className="btn btn-sm btn-outline"
                  onClick={() => setExpandedTasks(new Set(tasks.map(t => t.id)))}
                >
                  Expand All
                </button>
                <button 
                  className="btn btn-sm btn-outline"
                  onClick={() => setExpandedTasks(new Set())}
                >
                  Collapse All
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {filteredAndSortedTasks.map((task) => (
          <div key={task.id} className="card bg-base-100 shadow-lg">
            <div className="card-body p-4">
              {/* Task Header */}
              <div 
                className="flex items-center justify-between cursor-pointer"
                onClick={() => toggleTaskExpansion(task.id)}
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="badge badge-neutral">#{task.id}</span>
                  <h3 className="font-semibold text-lg">{task.title}</h3>
                  <div className="flex gap-2">
                    <span className={`badge badge-sm ${getPriorityBadgeClass(task.priority)}`}>
                      {task.priority}
                    </span>
                    <span className={`badge badge-sm ${getStatusBadgeClass(task.status)}`}>
                      {task.status}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {task.dependencies && task.dependencies.length > 0 && (
                    <div className="tooltip" data-tip={`Depends on: ${task.dependencies.join(', ')}`}>
                      <span className="badge badge-outline badge-sm">
                        {task.dependencies.length} deps
                      </span>
                    </div>
                  )}

                  {getTaskFile(task.id) && (
                    <button
                      className={`btn btn-sm ${showMarkdown.has(task.id) ? 'btn-primary' : 'btn-outline'}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMarkdownView(task.id);
                      }}
                      title="View detailed markdown"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </button>
                  )}

                  <button className="btn btn-ghost btn-sm">
                    {expandedTasks.has(task.id) ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Task Description */}
              <p className="text-base-content/80 mt-2">{task.description}</p>

              {/* Expanded Content */}
              {expandedTasks.has(task.id) && (
                <div className="mt-4 space-y-4 border-t border-base-300 pt-4">
                  {task.details && (
                    <div>
                      <h4 className="font-medium text-sm mb-2">Implementation Details</h4>
                      <div className="bg-base-200 rounded-lg p-3">
                        <p className="text-sm whitespace-pre-wrap">{task.details}</p>
                      </div>
                    </div>
                  )}
                  
                  {task.testStrategy && (
                    <div>
                      <h4 className="font-medium text-sm mb-2">Test Strategy</h4>
                      <div className="bg-base-200 rounded-lg p-3">
                        <p className="text-sm whitespace-pre-wrap">{task.testStrategy}</p>
                      </div>
                    </div>
                  )}
                  
                  {task.dependencies && task.dependencies.length > 0 && (
                    <div>
                      <h4 className="font-medium text-sm mb-2">Dependencies</h4>
                      <div className="flex gap-2 flex-wrap">
                        {task.dependencies.map((depId) => (
                          <span key={depId} className="badge badge-outline">
                            Task #{depId}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {task.subtasks && task.subtasks.length > 0 && (
                    <div>
                      <h4 className="font-medium text-sm mb-2">Subtasks</h4>
                      <div className="space-y-1">
                        {task.subtasks.map((subtask, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <input type="checkbox" className="checkbox checkbox-sm" />
                            <span className="text-sm">{subtask.title || subtask}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Markdown Content */}
              {showMarkdown.has(task.id) && getTaskFile(task.id) && (
                <div className="mt-4 border-t border-base-300 pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-sm">Detailed Task Documentation</h4>
                    <span className="text-xs text-base-content/60">
                      Generated markdown with checklists
                    </span>
                  </div>
                  <div className="bg-base-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          // Custom styling for markdown elements
                          h1: ({ children }) => <h1 className="text-xl font-bold mb-3 text-primary">{children}</h1>,
                          h2: ({ children }) => <h2 className="text-lg font-semibold mb-2 text-secondary">{children}</h2>,
                          h3: ({ children }) => <h3 className="text-base font-medium mb-2">{children}</h3>,
                          p: ({ children }) => <p className="mb-2 leading-relaxed text-sm">{children}</p>,
                          ul: ({ children }) => <ul className="list-none mb-3 space-y-1">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                          li: ({ children }) => {
                            const content = String(children);
                            if (content.includes('[ ]') || content.includes('[x]')) {
                              const isChecked = content.includes('[x]');
                              const text = content.replace(/\[[ x]\]\s*/, '');
                              return (
                                <li className="flex items-start gap-2 text-sm">
                                  <input
                                    type="checkbox"
                                    checked={isChecked}
                                    className="checkbox checkbox-sm mt-0.5 flex-shrink-0"
                                    readOnly
                                  />
                                  <span className={isChecked ? 'line-through text-base-content/60' : ''}>{text}</span>
                                </li>
                              );
                            }
                            return <li className="text-sm">{children}</li>;
                          },
                          code: ({ children, className }) => {
                            const isInline = !className;
                            return isInline ? (
                              <code className="bg-base-200 px-1 py-0.5 rounded text-xs font-mono">{children}</code>
                            ) : (
                              <code className="block bg-base-200 p-2 rounded text-xs font-mono overflow-x-auto">{children}</code>
                            );
                          },
                          blockquote: ({ children }) => (
                            <blockquote className="border-l-4 border-primary pl-3 italic text-base-content/80 mb-2 text-sm">
                              {children}
                            </blockquote>
                          ),
                          table: ({ children }) => (
                            <div className="overflow-x-auto mb-2">
                              <table className="table table-zebra table-xs w-full">{children}</table>
                            </div>
                          ),
                          th: ({ children }) => <th className="font-semibold text-xs">{children}</th>,
                          td: ({ children }) => <td className="text-xs">{children}</td>,
                        }}
                      >
                        {getTaskFile(task.id)?.content || ''}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskDisplayPanel;
