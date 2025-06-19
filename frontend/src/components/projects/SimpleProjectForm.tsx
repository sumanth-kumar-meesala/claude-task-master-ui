/**
 * Simple Project Creation Form
 * 
 * A single-page form for creating projects with core fields only.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  TagIcon,
  CogIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { ProjectCreate, ProjectStatus } from '@/types/common';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { projectsService } from '@/services/projects';

interface SimpleProjectFormProps {
  onComplete?: (projectId: string) => void;
  onCancel?: () => void;
}

interface ProjectFormData {
  name: string;
  description: string;
  requirements: string;
  status: ProjectStatus;
  tags: string[];
  tech_stack: string[];
}

export const SimpleProjectForm: React.FC<SimpleProjectFormProps> = ({
  onComplete,
  onCancel
}) => {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    requirements: '',
    status: ProjectStatus.DRAFT,
    tags: [],
    tech_stack: []
  });

  const [tagInput, setTagInput] = useState('');
  const [techStackInput, setTechStackInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Create project mutation
  const createProjectMutation = useMutation({
    mutationFn: async (data: ProjectFormData) => {
      const apiData: ProjectCreate = {
        name: data.name,
        description: data.description,
        requirements: data.requirements,
        status: data.status,
        tags: data.tags,
        tech_stack: data.tech_stack,
        metadata: {}
      };

      return projectsService.createProject(apiData);
    },
    onSuccess: (response) => {
      toast.success('Project created successfully!');
      if (onComplete) {
        onComplete(response.project.id);
      } else {
        navigate(`/dashboard/projects/${response.project.id}`);
      }
    },
    onError: (error: Error) => {
      toast.error(`Failed to create project: ${error.message}`);
    }
  });

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required';
    } else if (formData.name.trim().length < 3) {
      newErrors.name = 'Project name must be at least 3 characters';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Project description is required';
    } else if (formData.description.trim().length < 20) {
      newErrors.description = 'Project description must be at least 20 characters';
    }

    if (!formData.requirements.trim()) {
      newErrors.requirements = 'Project requirements are required';
    } else if (formData.requirements.trim().length < 20) {
      newErrors.requirements = 'Project requirements must be at least 20 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    createProjectMutation.mutate(formData);
  };

  const updateFormData = (updates: Partial<ProjectFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim().toLowerCase())) {
      updateFormData({
        tags: [...formData.tags, tagInput.trim().toLowerCase()]
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    updateFormData({
      tags: formData.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const handleAddTechStack = () => {
    if (techStackInput.trim() && !formData.tech_stack.includes(techStackInput.trim())) {
      updateFormData({
        tech_stack: [...formData.tech_stack, techStackInput.trim()]
      });
      setTechStackInput('');
    }
  };

  const handleRemoveTechStack = (techToRemove: string) => {
    updateFormData({
      tech_stack: formData.tech_stack.filter(tech => tech !== techToRemove)
    });
  };

  const isLoading = createProjectMutation.isPending;

  return (
    <div className="min-h-screen bg-base-200 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <DocumentTextIcon className="w-12 h-12 text-primary mr-3" />
              <h1 className="text-4xl font-bold text-base-content">Create New Project</h1>
            </div>
            <p className="text-lg text-base-content/70 max-w-2xl mx-auto">
              Fill in the details below to create your project. All required fields are marked with an asterisk (*).
            </p>
          </div>

          {/* Main Form Card */}
          <div className="card bg-base-100 shadow-2xl border border-base-300">
            <div className="card-body p-8">

              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Basic Information Section */}
                <div className="space-y-6">
                  <div className="divider divider-start">
                    <span className="text-lg font-semibold text-base-content">Basic Information</span>
                  </div>

                  {/* Project Name */}
                  <div className="form-control w-full">
                    <label className="label">
                      <span className="label-text text-base font-semibold">
                        Project Name <span className="text-error">*</span>
                      </span>
                    </label>
                    <input
                      type="text"
                      placeholder="Enter a descriptive project name"
                      className={`input input-bordered input-lg w-full ${errors.name ? 'input-error' : 'focus:input-primary'}`}
                      value={formData.name}
                      onChange={(e) => updateFormData({ name: e.target.value })}
                      disabled={isLoading}
                    />
                    {errors.name && (
                      <label className="label">
                        <span className="label-text-alt text-error font-medium flex items-center">
                          <XMarkIcon className="w-4 h-4 mr-1" />
                          {errors.name}
                        </span>
                      </label>
                    )}
                    {!errors.name && formData.name.length >= 3 && (
                      <label className="label">
                        <span className="label-text-alt text-success font-medium flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          Good project name
                        </span>
                      </label>
                    )}
                  </div>

                  {/* Project Description */}
                  <div className="form-control w-full">
                    <label className="label">
                      <span className="label-text text-base font-semibold">
                        Project Description <span className="text-error">*</span>
                      </span>
                      <span className="label-text-alt text-base-content/60">
                        Minimum 20 characters
                      </span>
                    </label>
                    <textarea
                      placeholder="Provide a detailed description of your project, its goals, and what you want to achieve..."
                      className={`textarea textarea-bordered textarea-lg h-28 w-full resize-none ${errors.description ? 'textarea-error' : 'focus:textarea-primary'}`}
                      value={formData.description}
                      onChange={(e) => updateFormData({ description: e.target.value })}
                      disabled={isLoading}
                    />
                    {errors.description && (
                      <label className="label">
                        <span className="label-text-alt text-error font-medium flex items-center">
                          <XMarkIcon className="w-4 h-4 mr-1" />
                          {errors.description}
                        </span>
                      </label>
                    )}
                    {!errors.description && formData.description.length >= 20 && (
                      <label className="label">
                        <span className="label-text-alt text-success font-medium flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          Description looks good ({formData.description.length} characters)
                        </span>
                      </label>
                    )}
                  </div>

                  {/* Project Requirements */}
                  <div className="form-control w-full">
                    <label className="label">
                      <span className="label-text text-base font-semibold">
                        Core Requirements <span className="text-error">*</span>
                      </span>
                      <span className="label-text-alt text-base-content/60">
                        Minimum 20 characters
                      </span>
                    </label>
                    <textarea
                      placeholder="List all project requirements, features, specifications, and any constraints or special considerations..."
                      className={`textarea textarea-bordered textarea-lg h-36 w-full resize-none ${errors.requirements ? 'textarea-error' : 'focus:textarea-primary'}`}
                      value={formData.requirements}
                      onChange={(e) => updateFormData({ requirements: e.target.value })}
                      disabled={isLoading}
                    />
                    {errors.requirements && (
                      <label className="label">
                        <span className="label-text-alt text-error font-medium flex items-center">
                          <XMarkIcon className="w-4 h-4 mr-1" />
                          {errors.requirements}
                        </span>
                      </label>
                    )}
                    {!errors.requirements && formData.requirements.length >= 20 && (
                      <label className="label">
                        <span className="label-text-alt text-success font-medium flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          Requirements are detailed ({formData.requirements.length} characters)
                        </span>
                      </label>
                    )}
                  </div>
                </div>

                {/* Project Configuration Section */}
                <div className="space-y-6">
                  <div className="divider divider-start">
                    <span className="text-lg font-semibold text-base-content">Project Configuration</span>
                  </div>

                  {/* Project Status */}
                  <div className="form-control w-full max-w-md">
                    <label className="label">
                      <span className="label-text text-base font-semibold">Project Status</span>
                    </label>
                    <select
                      className="select select-bordered select-lg w-full focus:select-primary"
                      value={formData.status}
                      onChange={(e) => updateFormData({ status: e.target.value as ProjectStatus })}
                      disabled={isLoading}
                    >
                      <option value={ProjectStatus.DRAFT}>📝 Draft</option>
                      <option value={ProjectStatus.ACTIVE}>🚀 Active</option>
                      <option value={ProjectStatus.COMPLETED}>✅ Completed</option>
                      <option value={ProjectStatus.ARCHIVED}>📦 Archived</option>
                    </select>
                  </div>
                </div>

                {/* Tags and Technology Section */}
                <div className="space-y-6">
                  <div className="divider divider-start">
                    <span className="text-lg font-semibold text-base-content">Tags & Technology</span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Tags */}
                    <div className="form-control w-full">
                      <label className="label">
                        <span className="label-text text-base font-semibold">Project Tags</span>
                        <span className="label-text-alt text-base-content/60">
                          Help categorize your project
                        </span>
                      </label>
                      <div className="join w-full">
                        <input
                          type="text"
                          placeholder="e.g., web, mobile, ai"
                          className="input input-bordered input-lg join-item flex-1 focus:input-primary"
                          value={tagInput}
                          onChange={(e) => setTagInput(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                          disabled={isLoading}
                        />
                        <button
                          type="button"
                          onClick={handleAddTag}
                          className="btn btn-primary btn-lg join-item"
                          disabled={isLoading || !tagInput.trim()}
                        >
                          <TagIcon className="w-5 h-5" />
                          Add
                        </button>
                      </div>
                      {formData.tags.length > 0 && (
                        <div className="mt-3">
                          <div className="flex flex-wrap gap-2">
                            {formData.tags.map((tag) => (
                              <div key={tag} className="badge badge-primary badge-lg gap-2 py-3">
                                <span className="font-medium">{tag}</span>
                                <button
                                  type="button"
                                  onClick={() => handleRemoveTag(tag)}
                                  className="btn btn-ghost btn-xs text-primary-content hover:text-error"
                                  disabled={isLoading}
                                >
                                  <XMarkIcon className="w-4 h-4" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Tech Stack */}
                    <div className="form-control w-full">
                      <label className="label">
                        <span className="label-text text-base font-semibold">Technology Stack</span>
                        <span className="label-text-alt text-base-content/60">
                          Technologies you'll use
                        </span>
                      </label>
                      <div className="join w-full">
                        <input
                          type="text"
                          placeholder="e.g., React, Node.js, Python"
                          className="input input-bordered input-lg join-item flex-1 focus:input-primary"
                          value={techStackInput}
                          onChange={(e) => setTechStackInput(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTechStack())}
                          disabled={isLoading}
                        />
                        <button
                          type="button"
                          onClick={handleAddTechStack}
                          className="btn btn-secondary btn-lg join-item"
                          disabled={isLoading || !techStackInput.trim()}
                        >
                          <CogIcon className="w-5 h-5" />
                          Add
                        </button>
                      </div>
                      {formData.tech_stack.length > 0 && (
                        <div className="mt-3">
                          <div className="flex flex-wrap gap-2">
                            {formData.tech_stack.map((tech) => (
                              <div key={tech} className="badge badge-secondary badge-lg gap-2 py-3">
                                <span className="font-medium">{tech}</span>
                                <button
                                  type="button"
                                  onClick={() => handleRemoveTechStack(tech)}
                                  className="btn btn-ghost btn-xs text-secondary-content hover:text-error"
                                  disabled={isLoading}
                                >
                                  <XMarkIcon className="w-4 h-4" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="divider"></div>
                <div className="flex flex-col sm:flex-row gap-4 justify-end pt-4">
                  {onCancel && (
                    <button
                      type="button"
                      onClick={onCancel}
                      className="btn btn-ghost btn-lg order-2 sm:order-1"
                      disabled={isLoading}
                    >
                      <XMarkIcon className="w-5 h-5 mr-2" />
                      Cancel
                    </button>
                  )}
                  <button
                    type="submit"
                    className="btn btn-primary btn-lg order-1 sm:order-2 min-w-48"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <LoadingSpinner size="sm" />
                        <span className="ml-2">Creating Project...</span>
                      </>
                    ) : (
                      <>
                        <DocumentTextIcon className="w-5 h-5 mr-2" />
                        Create Project
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
