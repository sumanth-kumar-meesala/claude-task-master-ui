/**
 * Enhanced Projects page component with wizard-based project creation.
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  PlusIcon,
  FolderIcon,
  CalendarIcon,
  MagnifyingGlassIcon,
  TrashIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';

import { projectsService } from '@/services/projects';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ConfirmationDialog } from '@/components/ui/ConfirmationDialog';
import { SimpleProjectForm } from '@/components/projects/SimpleProjectForm';
import toast from 'react-hot-toast';

const ProjectsPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showCreateWizard, setShowCreateWizard] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [deleteProjectId, setDeleteProjectId] = useState<string | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // React to URL parameter changes
  useEffect(() => {
    setShowCreateWizard(searchParams.get('create') === 'true');
  }, [searchParams]);

  // Get projects
  const { data: projectsData, isLoading, refetch } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsService.getProjects(),
  });

  // Delete project mutation
  const deleteProjectMutation = useMutation({
    mutationFn: (projectId: string) => projectsService.deleteProject(projectId),
    onSuccess: () => {
      toast.success('Project deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setShowDeleteDialog(false);
      setDeleteProjectId(null);
    },
    onError: (error: any) => {
      toast.error(`Failed to delete project: ${error.message || 'Unknown error'}`);
    },
  });



  const projects = projectsData?.projects || [];

  // Filter projects
  const filteredProjects = projects.filter(project => {
    const matchesSearch = !searchQuery ||
      project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const handleCreateProject = () => {
    setShowCreateWizard(true);
    setSearchParams({ create: 'true' });
  };

  const handleFormComplete = (projectId: string) => {
    setShowCreateWizard(false);
    setSearchParams({});
    navigate(`/dashboard/projects/${projectId}`);
    refetch();
  };

  const handleFormCancel = () => {
    setShowCreateWizard(false);
    setSearchParams({});
  };

  const handleDeleteProject = (e: React.MouseEvent, projectId: string) => {
    e.stopPropagation(); // Prevent card click navigation
    setDeleteProjectId(projectId);
    setShowDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    if (deleteProjectId) {
      deleteProjectMutation.mutate(deleteProjectId);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteDialog(false);
    setDeleteProjectId(null);
  };





  if (showCreateWizard) {
    return (
      <SimpleProjectForm
        onComplete={handleFormComplete}
        onCancel={handleFormCancel}
      />
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Projects</h1>
          <p className="text-base-content/70">
            Manage your AI-powered project analysis and planning
          </p>
        </div>

        <button
          onClick={handleCreateProject}
          className="btn btn-primary mt-4 sm:mt-0"
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          New Project
        </button>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-base-content/50" />
            <input
              type="text"
              className="input input-bordered w-full pl-10"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="sm:w-48">
          <select
            className="select select-bordered w-full"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="card bg-base-100 border border-base-300 hover:border-primary/50 transition-colors cursor-pointer"
              onClick={() => navigate(`/dashboard/projects/${project.id}`)}
            >
              <div className="card-body">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="card-title text-lg">{project.name}</h3>
                  <div className="flex items-center gap-2">
                    <div className={`badge ${
                      project.status === 'active' ? 'badge-success' :
                      project.status === 'completed' ? 'badge-primary' :
                      project.status === 'draft' ? 'badge-warning' :
                      'badge-ghost'
                    }`}>
                      {project.status}
                    </div>

                    {/* Delete Button */}
                    <div className="dropdown dropdown-end">
                      <label tabIndex={0} className="btn btn-ghost btn-xs">
                        <EllipsisVerticalIcon className="w-4 h-4" />
                      </label>
                      <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-40">
                        <li>
                          <button
                            onClick={(e) => handleDeleteProject(e, project.id)}
                            className="text-error hover:bg-error hover:text-error-content text-sm"
                            disabled={deleteProjectMutation.isPending}
                          >
                            <TrashIcon className="w-4 h-4" />
                            Delete
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                <p className="text-base-content/70 text-sm mb-4 line-clamp-3">
                  {project.description}
                </p>

                <div className="space-y-2">
                  {project.metadata?.project_type && (
                    <div className="flex items-center gap-2 text-sm">
                      <FolderIcon className="w-4 h-4 text-base-content/50" />
                      <span className="text-base-content/70">
                        {project.metadata.project_type.replace('_', ' ')}
                      </span>
                    </div>
                  )}



                  <div className="flex items-center gap-2 text-sm">
                    <CalendarIcon className="w-4 h-4 text-base-content/50" />
                    <span className="text-base-content/70">
                      {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {project.tags && project.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3">
                    {project.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="badge badge-ghost badge-sm">
                        {tag}
                      </span>
                    ))}
                    {project.tags.length > 3 && (
                      <span className="badge badge-ghost badge-sm">
                        +{project.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}


              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <FolderIcon className="w-16 h-16 mx-auto text-base-content/30 mb-4" />
          <h3 className="text-xl font-semibold mb-2">
            {searchQuery || statusFilter !== 'all' ? 'No projects found' : 'No projects yet'}
          </h3>
          <p className="text-base-content/70 mb-6">
            {searchQuery || statusFilter !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Create your first project to get started with AI-powered project analysis'
            }
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <button
              onClick={handleCreateProject}
              className="btn btn-primary"
            >
              <PlusIcon className="w-5 h-5 mr-2" />
              Create Your First Project
            </button>
          )}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showDeleteDialog}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="Delete Project"
        message={`Are you sure you want to delete "${projects.find(p => p.id === deleteProjectId)?.name}"? This action will permanently delete the project and all its related data including sessions, overviews, and chat history. This action cannot be undone.`}
        confirmText="Delete Project"
        cancelText="Cancel"
        type="danger"
        isLoading={deleteProjectMutation.isPending}
      />
    </div>
  );
};

export default ProjectsPage;
