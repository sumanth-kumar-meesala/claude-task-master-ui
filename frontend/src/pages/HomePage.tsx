/**
 * Home page component.
 */

import { Link } from 'react-router-dom';
import { ArrowRightIcon, SparklesIcon, CpuChipIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import { healthService } from '@/services/health';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

/**
 * Home page component.
 */
const HomePage = () => {
  const { data: health, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: () => healthService.checkHealth(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Analysis',
      description: 'Leverage Google Gemini AI to analyze and understand your project requirements.',
    },
    {
      icon: CpuChipIcon,
      title: 'Multi-Agent System',
      description: 'CrewAI orchestrates multiple specialized agents for comprehensive project planning.',
    },
    {
      icon: DocumentTextIcon,
      title: 'Detailed Reports',
      description: 'Generate comprehensive project overviews with technical specifications and recommendations.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Project Overview
              <span className="text-blue-600 dark:text-blue-400"> Agent</span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
              Transform your project ideas into comprehensive overviews using AI-powered analysis 
              and multi-agent collaboration.
            </p>
            
            {/* Status indicator */}
            <div className="flex items-center justify-center mb-8">
              {isLoading ? (
                <div className="flex items-center space-x-2 text-gray-500">
                  <LoadingSpinner size="sm" />
                  <span>Checking system status...</span>
                </div>
              ) : error ? (
                <div className="flex items-center space-x-2 text-red-500">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span>System offline</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-green-500">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>System online</span>
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/demo"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
              >
                <SparklesIcon className="mr-2 h-5 w-5" />
                Try Demo
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center px-6 py-3 border border-gray-300 dark:border-gray-600 text-base font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Get Started
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Link>
              <Link
                to="/dashboard/projects"
                className="inline-flex items-center px-6 py-3 border border-gray-300 dark:border-gray-600 text-base font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                View Projects
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Features section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Powerful Features
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Everything you need to transform ideas into actionable project plans
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
                >
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg mb-4">
                    <Icon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* System status section */}
      {health && (
        <section className="py-16 bg-white dark:bg-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                System Status
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 text-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  API Status
                </h3>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {health.status}
                </p>
              </div>

              {health.database && (
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 text-center">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Database
                  </h3>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {health.database.status}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {health.database.projects_count} projects
                  </p>
                </div>
              )}

              {health.services && (
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 text-center">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    AI Services
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Gemini: {health.services.gemini_api}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    CrewAI: {health.services.crewai}
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default HomePage;
