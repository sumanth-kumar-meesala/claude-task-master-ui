/**
 * Project Files Display Component
 * 
 * Displays project overview and task files in a professional, readable format.
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  CalendarIcon,
  EyeIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

import { projectFilesService } from '@/services/projectFiles';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ProjectFile, ProjectFileType } from '@/types/common';
import { cn } from '@/utils/cn';

interface ProjectFilesDisplayProps {
  projectId: string;
  className?: string;
}

interface FileDisplayProps {
  file: ProjectFile;
  isExpanded: boolean;
  onToggle: () => void;
}

const FileDisplay: React.FC<FileDisplayProps> = ({ file, isExpanded, onToggle }) => {
  const getFileIcon = (fileType: ProjectFileType) => {
    switch (fileType) {
      case ProjectFileType.PROJECT_OVERVIEW:
        return DocumentTextIcon;
      case ProjectFileType.TASKS_INDEX:
        return ClipboardDocumentListIcon;
      case ProjectFileType.TASK_FILE:
        return ClipboardDocumentListIcon;
      default:
        return DocumentTextIcon;
    }
  };

  const getFileTypeLabel = (fileType: ProjectFileType) => {
    switch (fileType) {
      case ProjectFileType.PROJECT_OVERVIEW:
        return 'Project Overview';
      case ProjectFileType.TASKS_INDEX:
        return 'Tasks Index';
      case ProjectFileType.TASK_FILE:
        return 'Task';
      default:
        return 'File';
    }
  };

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      generated: 'badge-info',
      reviewed: 'badge-warning',
      approved: 'badge-success',
      archived: 'badge-ghost',
    };
    return statusClasses[status as keyof typeof statusClasses] || 'badge-ghost';
  };

  const Icon = getFileIcon(file.file_type);

  return (
    <div className="card bg-base-100 shadow-sm border border-base-300">
      {/* File Header */}
      <div 
        className="card-body p-4 cursor-pointer hover:bg-base-50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Icon className="w-5 h-5 text-primary" />
            <div>
              <h3 className="font-semibold text-base">{file.file_name}</h3>
              <div className="flex items-center gap-2 text-sm text-base-content/70">
                <span>{getFileTypeLabel(file.file_type)}</span>
                {file.metadata.task_number && (
                  <>
                    <span>•</span>
                    <span>Task #{file.metadata.task_number}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`badge ${getStatusBadge(file.status)} badge-sm`}>
              {file.status}
            </div>
            {isExpanded ? (
              <ChevronDownIcon className="w-4 h-4" />
            ) : (
              <ChevronRightIcon className="w-4 h-4" />
            )}
          </div>
        </div>

        {/* File Metadata */}
        <div className="flex items-center gap-4 text-xs text-base-content/60 mt-2">
          <div className="flex items-center gap-1">
            <CalendarIcon className="w-3 h-3" />
            <span>Updated {new Date(file.updated_at).toLocaleDateString()}</span>
          </div>
          

          
          {file.metadata.file_size && (
            <div className="flex items-center gap-1">
              <EyeIcon className="w-3 h-3" />
              <span>{(file.metadata.file_size / 1024).toFixed(1)}KB</span>
            </div>
          )}
        </div>
      </div>

      {/* File Content */}
      {isExpanded && (
        <div className="border-t border-base-300">
          <div className="p-4">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  // Custom styling for markdown elements
                  h1: ({ children }) => <h1 className="text-2xl font-bold mb-4 text-primary">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-xl font-semibold mb-3 text-secondary">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-lg font-medium mb-2">{children}</h3>,
                  p: ({ children }) => <p className="mb-3 leading-relaxed">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                  li: ({ children }) => <li className="text-sm">{children}</li>,
                  code: ({ children, className }) => {
                    const isInline = !className;
                    return isInline ? (
                      <code className="bg-base-200 px-1 py-0.5 rounded text-sm font-mono">{children}</code>
                    ) : (
                      <code className="block bg-base-200 p-3 rounded-lg text-sm font-mono overflow-x-auto">{children}</code>
                    );
                  },
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-primary pl-4 italic text-base-content/80 mb-3">
                      {children}
                    </blockquote>
                  ),
                  table: ({ children }) => (
                    <div className="overflow-x-auto mb-3">
                      <table className="table table-zebra table-sm w-full">{children}</table>
                    </div>
                  ),
                  th: ({ children }) => <th className="font-semibold">{children}</th>,
                  td: ({ children }) => <td>{children}</td>,
                }}
              >
                {file.content}
              </ReactMarkdown>
            </div>
            

          </div>
        </div>
      )}
    </div>
  );
};

export const ProjectFilesDisplay: React.FC<ProjectFilesDisplayProps> = ({ 
  projectId, 
  className 
}) => {
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set());

  // Fetch project files
  const { data: filesData, isLoading, error } = useQuery({
    queryKey: ['project-files', projectId],
    queryFn: () => projectFilesService.getProjectOverviewAndTasks(projectId),
    enabled: !!projectId,
  });

  const toggleFileExpansion = (fileId: string) => {
    setExpandedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fileId)) {
        newSet.delete(fileId);
      } else {
        newSet.add(fileId);
      }
      return newSet;
    });
  };

  const expandAll = () => {
    if (!filesData) return;
    const allFileIds = new Set<string>();
    if (filesData.overview) allFileIds.add(filesData.overview.id);
    filesData.tasks.forEach(task => allFileIds.add(task.id));
    setExpandedFiles(allFileIds);
  };

  const collapseAll = () => {
    setExpandedFiles(new Set());
  };

  if (isLoading) {
    return (
      <div className={cn("flex items-center justify-center h-64", className)}>
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("alert alert-error", className)}>
        <ExclamationTriangleIcon className="w-6 h-6" />
        <div>
          <h3 className="font-bold">Failed to load project files</h3>
          <div className="text-xs">Please try refreshing the page.</div>
        </div>
      </div>
    );
  }

  if (!filesData || filesData.total_files === 0) {
    return (
      <div className={cn("text-center py-12", className)}>
        <DocumentTextIcon className="w-16 h-16 mx-auto text-base-content/30 mb-4" />
        <h3 className="text-lg font-medium text-base-content/70 mb-2">No Generated Files</h3>
        <p className="text-base-content/50">
          This project doesn't have any generated overview or task files yet.
          <br />
          Project files will appear here when they are generated.
        </p>
      </div>
    );
  }

  const allFiles = [
    ...(filesData.overview ? [filesData.overview] : []),
    ...filesData.tasks
  ];

  return (
    <div className={cn("space-y-4", className)}>
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Generated Project Files</h2>
          <p className="text-sm text-base-content/70">
            {filesData.total_files} file{filesData.total_files !== 1 ? 's' : ''} generated
            {filesData.last_updated && (
              <span> • Last updated {new Date(filesData.last_updated).toLocaleDateString()}</span>
            )}
          </p>
        </div>
        
        <div className="flex gap-2">
          <button 
            onClick={expandAll}
            className="btn btn-sm btn-outline"
            disabled={expandedFiles.size === allFiles.length}
          >
            Expand All
          </button>
          <button 
            onClick={collapseAll}
            className="btn btn-sm btn-outline"
            disabled={expandedFiles.size === 0}
          >
            Collapse All
          </button>
        </div>
      </div>

      {/* Files List */}
      <div className="space-y-3">
        {allFiles.map((file) => (
          <FileDisplay
            key={file.id}
            file={file}
            isExpanded={expandedFiles.has(file.id)}
            onToggle={() => toggleFileExpansion(file.id)}
          />
        ))}
      </div>
    </div>
  );
};
