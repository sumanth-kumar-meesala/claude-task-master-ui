/**
 * Dashboard page component.
 */

import { Link } from 'react-router-dom';
import { PlusIcon, FolderIcon, UserGroupIcon, PlayIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import { healthService } from '@/services/health';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

/**
 * Dashboard page component.
 */
const DashboardPage = () => {
  const { data: status, isLoading } = useQuery({
    queryKey: ['api-status'],
    queryFn: () => healthService.getApiStatus(),
    refetchInterval: 30000,
  });

  const quickActions = [
    {
      title: 'New Project',
      description: 'Create comprehensive project with AI orchestration',
      href: '/dashboard/projects',
      icon: SparklesIcon,
      color: 'btn-primary',
      featured: true,
    },
    {
      title: 'Browse Projects',
      description: 'View all your projects',
      href: '/dashboard/projects',
      icon: FolderIcon,
      color: 'btn-outline',
    },

  ];

  return (
    <div className="space-y-8">
      {/* Hero Section for New Workflow */}
      <div className="hero bg-gradient-to-r from-primary to-secondary rounded-lg text-primary-content">
        <div className="hero-content text-center py-12">
          <div className="max-w-md">
            <SparklesIcon className="w-16 h-16 mx-auto mb-4" />
            <h1 className="text-4xl font-bold mb-4">
              AI-Powered Project Orchestration
            </h1>
            <p className="text-lg mb-6 opacity-90">
              Create comprehensive project documentation with AI agent collaboration.
              Get detailed ProjectOverview.md and 10-20 task files for scalable development.
            </p>
            <Link to="/dashboard/projects" className="btn btn-accent btn-lg gap-2">
              <PlayIcon className="w-6 h-6" />
              Start New Project
            </Link>
          </div>
        </div>
      </div>

      {/* Welcome section */}
      <div className="bg-base-100 shadow-lg rounded-lg p-6">
        <h2 className="text-2xl font-bold text-base-content mb-2">
          Welcome to Project Overview Agent
        </h2>
        <p className="text-base-content/70">
          Transform your project ideas into comprehensive overviews using AI-powered analysis.
        </p>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          return (
            <Link
              key={index}
              to={action.href}
              className={`card bg-base-100 shadow-lg hover:shadow-xl transition-all duration-300 ${
                action.featured ? 'border-2 border-primary' : ''
              }`}
            >
              <div className="card-body items-center text-center">
                <div className={`p-3 rounded-full ${action.featured ? 'bg-primary text-primary-content' : 'bg-base-200'}`}>
                  <Icon className="w-8 h-8" />
                </div>
                <h3 className={`card-title ${action.featured ? 'text-primary' : ''}`}>
                  {action.title}
                </h3>
                <p className="text-base-content/70 text-sm">
                  {action.description}
                </p>
                {action.featured && (
                  <div className="badge badge-primary badge-sm">New Workflow!</div>
                )}
              </div>
            </Link>
          );
        })}
      </div>

      {/* System overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System status */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            System Status
          </h2>
          
          {isLoading ? (
            <LoadingSpinner text="Loading system status..." />
          ) : status ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-300">API Status</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  {status.status}
                </span>
              </div>
              
              {status.database && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Database</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    {status.database.status}
                  </span>
                </div>
              )}
              
              {status.services && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Gemini AI</span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      status.services.gemini_api === 'configured' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}>
                      {status.services.gemini_api}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-300">CrewAI</span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      {status.services.crewai}
                    </span>
                  </div>
                </>
              )}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">Unable to load system status</p>
          )}
        </div>

        {/* Statistics */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Statistics
          </h2>
          
          {status?.database ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-300">Total Projects</span>
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {status.database.projects_count}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-300">Active Sessions</span>
                <span className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {status.database.sessions_count}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-300">Templates</span>
                <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {status.database.templates_count}
                </span>
              </div>
            </div>
          ) : (
            <LoadingSpinner text="Loading statistics..." />
          )}
        </div>
      </div>

      {/* Recent activity placeholder */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Activity
        </h2>
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">
            No recent activity to display. Start by creating a new project!
          </p>
          <Link
            to="/dashboard/projects/new"
            className="inline-flex items-center mt-4 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create Project
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
