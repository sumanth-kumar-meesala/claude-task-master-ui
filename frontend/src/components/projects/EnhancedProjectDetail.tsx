/**
 * Enhanced Project Detail Component with Agent Management
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FolderIcon,
  CalendarIcon,
  TagIcon,
  DocumentTextIcon,
  CogIcon,
  InformationCircleIcon,
  TrashIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';

import { projectsService } from '@/services/projects';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ConfirmationDialog } from '@/components/ui/ConfirmationDialog';
import { ProjectFilesDisplay } from './ProjectFilesDisplay';
import { TaskGenerationInterface } from '@/components/TaskGeneration';

import toast from 'react-hot-toast';

interface EnhancedProjectDetailProps {
  projectId?: string;
}

export const EnhancedProjectDetail: React.FC<EnhancedProjectDetailProps> = ({
  projectId: propProjectId
}) => {
  const { projectId: paramProjectId } = useParams();
  const projectId = propProjectId || paramProjectId;
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<'overview' | 'files' | 'tasks'>('overview');
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Fetch project data
  const { data: projectData, isLoading, error } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsService.getProject(projectId!),
    enabled: !!projectId,
  });

  // Delete project mutation
  const deleteProjectMutation = useMutation({
    mutationFn: () => projectsService.deleteProject(projectId!),
    onSuccess: () => {
      toast.success('Project deleted successfully');
      // Invalidate projects list
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      // Navigate back to projects page
      navigate('/dashboard/projects');
    },
    onError: (error: any) => {
      toast.error(`Failed to delete project: ${error.message || 'Unknown error'}`);
    },
  });

  const project = projectData?.data;

  const tabs = [
    { id: 'overview', name: 'Overview', icon: DocumentTextIcon },
    { id: 'files', name: 'Project Files', icon: DocumentTextIcon },
    { id: 'tasks', name: 'Task Generation', icon: CogIcon },
  ];

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      active: 'badge-success',
      completed: 'badge-primary',
      draft: 'badge-warning',
      archived: 'badge-ghost',
      cancelled: 'badge-error',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'badge-ghost';
  };

  const handleDeleteProject = () => {
    setShowDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    deleteProjectMutation.mutate();
    setShowDeleteDialog(false);
  };

  const handleCancelDelete = () => {
    setShowDeleteDialog(false);
  };



  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="alert alert-error">
        <InformationCircleIcon className="w-6 h-6" />
        <div>
          <h3 className="font-bold">Project Not Found</h3>
          <div className="text-xs">The project could not be loaded.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Project Header */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <FolderIcon className="w-8 h-8 text-primary" />
                <div>
                  <h1 className="text-2xl font-bold">{project.name}</h1>
                  <p className="text-base-content/70">Project ID: {project.id}</p>
                </div>
              </div>

              {project.description && (
                <p className="text-base-content/80 mb-4">{project.description}</p>
              )}

              <div className="flex flex-wrap items-center gap-4">
                <div className={`badge ${getStatusBadge(project.status)}`}>
                  {project.status}
                </div>

                <div className="flex items-center gap-2 text-sm text-base-content/70">
                  <CalendarIcon className="w-4 h-4" />
                  <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
                </div>

                {project.metadata?.project_type && (
                  <div className="badge badge-outline">
                    {project.metadata.project_type.replace('_', ' ')}
                  </div>
                )}


              </div>

              {project.tags && project.tags.length > 0 && (
                <div className="flex items-center gap-2 mt-3">
                  <TagIcon className="w-4 h-4 text-base-content/50" />
                  <div className="flex flex-wrap gap-1">
                    {project.tags.map((tag: string) => (
                      <span key={tag} className="badge badge-ghost badge-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Project Actions */}
            <div className="flex-shrink-0">
              <div className="dropdown dropdown-end">
                <label tabIndex={0} className="btn btn-ghost btn-sm">
                  <EllipsisVerticalIcon className="w-5 h-5" />
                </label>
                <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                  <li>
                    <button
                      onClick={handleDeleteProject}
                      className="text-error hover:bg-error hover:text-error-content"
                      disabled={deleteProjectMutation.isPending}
                    >
                      <TrashIcon className="w-4 h-4" />
                      Delete Project
                    </button>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body p-0">
          {/* Tab Navigation */}
          <div className="tabs tabs-bordered">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`tab tab-lg ${activeTab === tab.id ? 'tab-active' : ''}`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Project Information */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Project Information</h3>
                  <div className="bg-base-200 rounded-lg p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div>
                        <span className="font-medium">Status:</span>
                        <div className={`badge ${getStatusBadge(project.status)} ml-2`}>
                          {project.status}
                        </div>
                      </div>

                      <div>
                        <span className="font-medium">Created:</span>
                        <span className="ml-2 text-base-content/70">
                          {new Date(project.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      <div>
                        <span className="font-medium">Last Updated:</span>
                        <span className="ml-2 text-base-content/70">
                          {new Date(project.updated_at).toLocaleDateString()}
                        </span>
                      </div>

                      {project.metadata?.team_size && (
                        <div>
                          <span className="font-medium">Team Size:</span>
                          <span className="ml-2 text-base-content/70">
                            {project.metadata.team_size}
                          </span>
                        </div>
                      )}

                      {project.metadata?.timeline && (
                        <div>
                          <span className="font-medium">Timeline:</span>
                          <span className="ml-2 text-base-content/70">
                            {project.metadata.timeline.replace('_', ' ')}
                          </span>
                        </div>
                      )}

                      {project.tech_stack && project.tech_stack.length > 0 && (
                        <div className="md:col-span-2 lg:col-span-3">
                          <span className="font-medium">Tech Stack:</span>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {project.tech_stack.map((tech: string) => (
                              <span key={tech} className="badge badge-outline badge-sm">
                                {tech}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Requirements */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Requirements</h3>
                  {project.requirements ? (
                    <div className="bg-base-200 rounded-lg p-6">
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">{project.requirements}</p>
                    </div>
                  ) : (
                    <div className="bg-base-200 rounded-lg p-6">
                      <p className="text-base-content/70 italic">No requirements specified.</p>
                    </div>
                  )}
                </div>

              </div>
            )}



            {activeTab === 'files' && (
              <ProjectFilesDisplay
                projectId={project.id}
              />
            )}

            {activeTab === 'tasks' && (
              <TaskGenerationInterface
                projectId={project.id}
                projectName={project.name}
                onTasksGenerated={(tasks) => {
                  // Optionally handle tasks generated event
                  console.log('Tasks generated:', tasks);
                }}
              />
            )}


          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showDeleteDialog}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="Delete Project"
        message={`Are you sure you want to delete "${project?.name}"? This action will permanently delete the project and all its related data including sessions, overviews, and chat history. This action cannot be undone.`}
        confirmText="Delete Project"
        cancelText="Cancel"
        type="danger"
        isLoading={deleteProjectMutation.isPending}
      />
    </div>
  );
};
