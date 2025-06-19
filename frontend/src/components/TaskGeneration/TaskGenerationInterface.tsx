/**
 * Task Generation Interface Component
 * Main interface for generating tasks from PRD using claude-task-master
 */

import React, { useState, useEffect } from 'react';
import { taskMasterService, PRDParseRequest } from '../../services/taskMasterService';
import TaskDisplayPanel from './TaskDisplayPanel';

interface TaskGenerationInterfaceProps {
  projectId: string;
  projectName?: string;
  onTasksGenerated?: (tasks: any) => void;
}

interface GenerationProgress {
  status: 'idle' | 'starting' | 'progress' | 'complete' | 'error';
  message: string;
  tasks?: any;
  tasks_count?: number;
}

const TaskGenerationInterface: React.FC<TaskGenerationInterfaceProps> = ({
  projectId,
  projectName: _projectName,
  onTasksGenerated
}) => {
  const [prdContent, setPrdContent] = useState('');
  const [numTasks, setNumTasks] = useState(10);
  const [useResearch, setUseResearch] = useState(false);
  const [forceOverwrite, setForceOverwrite] = useState(false);
  const [appendTasks, setAppendTasks] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<GenerationProgress>({
    status: 'idle',
    message: ''
  });
  const [projectStatus, setProjectStatus] = useState<any>(null);
  const [generatedTasks, setGeneratedTasks] = useState<any>(null);
  const [prdGenerated, setPrdGenerated] = useState(false);
  const [prdSuggestions, setPrdSuggestions] = useState<string[]>([]);
  const [completenessScore, setCompletenessScore] = useState(0);
  const [loadingPrd, setLoadingPrd] = useState(false);


  // Load project status on mount
  useEffect(() => {
    loadProjectStatus();
    // Don't auto-load PRD to prevent infinite loops
    // User can click "Generate PRD" button instead
  }, [projectId]);

  const loadProjectStatus = async () => {
    try {
      const status = await taskMasterService.getProjectStatus(projectId);
      setProjectStatus(status);

      // If tasks already exist, load them
      if (status.tasks_generated) {
        const tasksResponse = await taskMasterService.getProjectTasks(projectId);
        if (tasksResponse.success) {
          setGeneratedTasks(tasksResponse.tasks);
        }
      }
    } catch (error) {
      console.error('Failed to load project status:', error);
    }
  };

  const loadPRDContent = async () => {
    if (loadingPrd) return; // Prevent multiple simultaneous calls

    setLoadingPrd(true);

    try {
      console.log('Loading PRD content for project:', projectId);
      const prdResponse = await taskMasterService.generatePRDContent(projectId);
      console.log('PRD response:', prdResponse);

      if (prdResponse.success) {
        setPrdContent(prdResponse.prd_content);
        setPrdSuggestions(prdResponse.suggestions || []);
        setCompletenessScore(prdResponse.completeness_score || 0);
        setPrdGenerated(true);
        console.log('PRD loaded successfully');
      } else {
        console.warn('PRD generation failed:', prdResponse);
        setPrdGenerated(false);
      }
    } catch (error) {
      console.error('Failed to load PRD content:', error);
      setPrdGenerated(false);
      // Don't show error to user, just leave PRD empty for manual input
    } finally {
      setLoadingPrd(false);
    }
  };

  const handleGenerateTasks = async () => {
    if (!prdContent.trim()) {
      alert('Please enter PRD content');
      return;
    }

    setIsGenerating(true);
    setProgress({ status: 'starting', message: 'Starting task generation...' });

    const request: PRDParseRequest = {
      project_id: projectId,
      prd_content: prdContent,
      num_tasks: numTasks,
      research: useResearch,
      force: forceOverwrite,
      append: appendTasks
    };

    try {
      await taskMasterService.parsePRDStream(projectId, request, (data) => {
        setProgress({
          status: data.status,
          message: data.message,
          tasks: data.tasks,
          tasks_count: data.tasks_count
        });

        if (data.status === 'complete') {
          setGeneratedTasks(data.tasks);
          if (onTasksGenerated) {
            onTasksGenerated(data.tasks);
          }
          loadProjectStatus(); // Refresh status
        }
      });
    } catch (error: any) {
      setProgress({
        status: 'error',
        message: error.message || 'Failed to generate tasks'
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'starting':
      case 'progress':
        return 'badge badge-info';
      case 'complete':
        return 'badge badge-success';
      case 'error':
        return 'badge badge-error';
      default:
        return 'badge badge-neutral';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Task Generation</h2>
        {projectStatus && (
          <div className="flex gap-2">
            <div className={`badge ${projectStatus.task_master_initialized ? 'badge-success' : 'badge-warning'}`}>
              {projectStatus.task_master_initialized ? 'Initialized' : 'Not Initialized'}
            </div>
            {projectStatus.tasks_generated && (
              <div className="badge badge-info">
                {projectStatus.tasks_count} tasks
              </div>
            )}
          </div>
        )}
      </div>

      {/* PRD Input */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="flex items-center justify-between mb-4">
            <h3 className="card-title">Product Requirements Document (PRD)</h3>
            {prdGenerated && (
              <div className="flex items-center gap-2">
                <div className="badge badge-success badge-sm">Auto-Generated</div>
                <div className="tooltip" data-tip={`Completeness Score: ${completenessScore}%`}>
                  <div className={`badge badge-sm ${
                    completenessScore >= 80 ? 'badge-success' :
                    completenessScore >= 60 ? 'badge-warning' :
                    'badge-error'
                  }`}>
                    {completenessScore}%
                  </div>
                </div>
              </div>
            )}
          </div>

          {loadingPrd ? (
            <div className="flex items-center gap-2 mb-4">
              <span className="loading loading-spinner loading-sm"></span>
              <span className="text-sm">Generating PRD from project data...</span>
            </div>
          ) : (
            <div className="mb-4">
              {prdGenerated ? (
                <div className="alert alert-info">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <div>
                    <div className="font-bold">PRD Auto-Generated!</div>
                    <div className="text-sm">This PRD was automatically created from your project data. You can edit it before generating tasks.</div>
                  </div>
                </div>
              ) : (
                <div className="alert alert-warning">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <div>
                    <div className="font-bold">Generate PRD from Project Data</div>
                    <div className="text-sm">Click "Generate PRD" to automatically create a PRD from your project information, or enter it manually below.</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* PRD Suggestions */}
          {prdSuggestions.length > 0 && (
            <div className="alert alert-warning mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
              <div>
                <div className="font-bold">Suggestions for Better Task Generation:</div>
                <ul className="text-sm mt-1">
                  {prdSuggestions.map((suggestion, index) => (
                    <li key={index}>• {suggestion}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
          
          <textarea
            className="textarea textarea-bordered w-full h-64"
            placeholder="Enter your PRD content here..."
            value={prdContent}
            onChange={(e) => setPrdContent(e.target.value)}
            disabled={isGenerating}
          />

          {/* Generation Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Number of Tasks</span>
              </label>
              <input
                type="number"
                className="input input-bordered"
                value={numTasks}
                onChange={(e) => setNumTasks(parseInt(e.target.value) || 10)}
                min="1"
                max="50"
                disabled={isGenerating}
              />
            </div>

            <div className="form-control">
              <label className="label cursor-pointer">
                <span className="label-text">Use Research-Backed Generation</span>
                <input
                  type="checkbox"
                  className="checkbox checkbox-primary"
                  checked={useResearch}
                  onChange={(e) => setUseResearch(e.target.checked)}
                  disabled={isGenerating}
                />
              </label>
            </div>

            {projectStatus?.tasks_generated && (
              <>
                <div className="form-control">
                  <label className="label cursor-pointer">
                    <span className="label-text">Force Overwrite Existing Tasks</span>
                    <input
                      type="checkbox"
                      className="checkbox checkbox-warning"
                      checked={forceOverwrite}
                      onChange={(e) => setForceOverwrite(e.target.checked)}
                      disabled={isGenerating}
                    />
                  </label>
                </div>

                <div className="form-control">
                  <label className="label cursor-pointer">
                    <span className="label-text">Append to Existing Tasks</span>
                    <input
                      type="checkbox"
                      className="checkbox checkbox-info"
                      checked={appendTasks}
                      onChange={(e) => setAppendTasks(e.target.checked)}
                      disabled={isGenerating}
                    />
                  </label>
                </div>
              </>
            )}
          </div>

          {/* Action Buttons */}
          <div className="card-actions justify-between mt-6">
            <div className="flex gap-2">
              <button
                className={`btn btn-outline btn-sm ${loadingPrd ? 'loading' : ''}`}
                onClick={() => {
                  loadPRDContent();
                }}
                disabled={loadingPrd || isGenerating}
              >
                {loadingPrd ? 'Generating...' : prdGenerated ? 'Regenerate PRD' : 'Generate PRD'}
              </button>

              <button
                className="btn btn-ghost btn-sm"
                onClick={() => {
                  setPrdContent('');
                  setPrdGenerated(false);
                  setPrdSuggestions([]);
                  setCompletenessScore(0);
                }}
                disabled={isGenerating}
              >
                Clear PRD
              </button>
            </div>

            <button
              className={`btn btn-primary ${isGenerating ? 'loading' : ''}`}
              onClick={handleGenerateTasks}
              disabled={isGenerating || !prdContent.trim()}
            >
              {isGenerating ? 'Generating Tasks...' : 'Generate Tasks'}
            </button>
          </div>
        </div>
      </div>

      {/* Progress Display */}
      {progress.status !== 'idle' && (
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center gap-3">
              <span className={getStatusBadgeClass(progress.status)}>
                {progress.status}
              </span>
              <span className="text-sm">{progress.message}</span>
            </div>
            
            {progress.status === 'progress' && (
              <div className="mt-2">
                <progress className="progress progress-primary w-full"></progress>
              </div>
            )}

            {progress.status === 'complete' && progress.tasks_count && (
              <div className="mt-2">
                <div className="alert alert-success">
                  <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Successfully generated {progress.tasks_count} tasks!</span>
                </div>
              </div>
            )}

            {progress.status === 'error' && (
              <div className="mt-2">
                <div className="alert alert-error">
                  <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Error: {progress.message}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Generated Tasks Display */}
      {generatedTasks && (
        <TaskDisplayPanel
          projectId={projectId}
          tasks={generatedTasks}
          onTaskUpdate={(taskId, updates) => {
            // Handle task updates if needed
            console.log('Task update:', taskId, updates);
          }}
        />
      )}
    </div>
  );
};

export default TaskGenerationInterface;
