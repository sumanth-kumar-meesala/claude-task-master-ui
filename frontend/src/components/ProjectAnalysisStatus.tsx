/**
 * Project analysis status component.
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  ClockIcon,
  CpuChipIcon,
  PlayIcon
} from '@heroicons/react/24/outline';
import { AnalysisStatus } from '@/types/common';
import { projectsService } from '@/services/projects';
import AnalysisStream from './AnalysisStream';

interface ProjectAnalysisStatusProps {
  projectId: string;
  onAnalysisComplete?: () => void;
  showTriggerButton?: boolean;
}

const ProjectAnalysisStatus: React.FC<ProjectAnalysisStatusProps> = ({
  projectId,
  onAnalysisComplete,
  showTriggerButton = false,
}) => {
  const [isTriggering, setIsTriggering] = useState(false);
  const [showStream, setShowStream] = useState(false);

  // Query analysis status with polling for in-progress analyses
  const { data: analysisProgress, isLoading, refetch } = useQuery({
    queryKey: ['project-analysis', projectId],
    queryFn: () => projectsService.getAnalysisProgress(projectId),
    refetchInterval: (query) => {
      // Poll every 3 seconds if analysis is in progress
      return query.state.data?.status === AnalysisStatus.IN_PROGRESS ? 3000 : false;
    },
    refetchIntervalInBackground: true,
  });

  // Call onAnalysisComplete when analysis finishes
  useEffect(() => {
    if (analysisProgress?.status === AnalysisStatus.COMPLETED && onAnalysisComplete) {
      onAnalysisComplete();
    }
  }, [analysisProgress?.status, onAnalysisComplete]);

  const handleTriggerAnalysis = async () => {
    setIsTriggering(true);
    try {
      await projectsService.triggerProjectAnalysis(projectId);
      // Open the stream to show real-time progress
      setShowStream(true);
      // Refetch to get updated status
      setTimeout(() => refetch(), 1000);
    } catch (error) {
      console.error('Failed to trigger analysis:', error);
    } finally {
      setIsTriggering(false);
    }
  };

  const getStatusIcon = () => {
    if (isLoading) {
      return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />;
    }

    switch (analysisProgress?.status) {
      case AnalysisStatus.COMPLETED:
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case AnalysisStatus.IN_PROGRESS:
        return <CpuChipIcon className="h-5 w-5 text-blue-500 animate-pulse" />;
      case AnalysisStatus.FAILED:
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (analysisProgress?.status) {
      case AnalysisStatus.COMPLETED:
        return 'text-green-600 dark:text-green-400';
      case AnalysisStatus.IN_PROGRESS:
        return 'text-blue-600 dark:text-blue-400';
      case AnalysisStatus.FAILED:
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getProgressBarColor = () => {
    switch (analysisProgress?.status) {
      case AnalysisStatus.COMPLETED:
        return 'bg-green-500';
      case AnalysisStatus.IN_PROGRESS:
        return 'bg-blue-500';
      case AnalysisStatus.FAILED:
        return 'bg-red-500';
      default:
        return 'bg-gray-300';
    }
  };

  if (isLoading && !analysisProgress) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-500">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400" />
        <span>Loading analysis status...</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Status Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {analysisProgress?.message || 'Analysis status unknown'}
          </span>
        </div>
        
        {showTriggerButton && analysisProgress?.status !== AnalysisStatus.IN_PROGRESS && (
          <button
            onClick={handleTriggerAnalysis}
            disabled={isTriggering}
            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isTriggering ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1" />
                Triggering...
              </>
            ) : (
              <>
                <PlayIcon className="h-3 w-3 mr-1" />
                {analysisProgress?.status === AnalysisStatus.FAILED ? 'Retry Analysis' : 'Start Analysis'}
              </>
            )}
          </button>
        )}
      </div>

      {/* Progress Bar */}
      {analysisProgress && (
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor()}`}
            style={{ width: `${analysisProgress.progress}%` }}
          />
        </div>
      )}

      {/* Agents Involved */}
      {analysisProgress?.agents_involved && analysisProgress.agents_involved.length > 0 && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          <span className="font-medium">Agents involved:</span>{' '}
          {analysisProgress.agents_involved.join(', ')}
        </div>
      )}

      {/* Analysis Details */}
      {analysisProgress?.status === AnalysisStatus.COMPLETED && (
        <div className="text-xs text-green-600 dark:text-green-400">
          ✓ Analysis completed successfully. View project details for comprehensive results.
        </div>
      )}

      {analysisProgress?.status === AnalysisStatus.IN_PROGRESS && (
        <div className="flex items-center justify-between">
          <div className="text-xs text-blue-600 dark:text-blue-400">
            🤖 AI agents are working on your project analysis...
          </div>
          <button
            onClick={() => setShowStream(true)}
            className="text-xs text-blue-600 hover:text-blue-800 underline"
          >
            View Live Stream
          </button>
        </div>
      )}

      {/* Analysis Stream Modal */}
      <AnalysisStream
        projectId={projectId}
        isOpen={showStream}
        onClose={() => setShowStream(false)}
      />
    </div>
  );
};

export default ProjectAnalysisStatus;
