/**
 * Authentication layout component.
 */

import { Outlet } from 'react-router-dom';

/**
 * Authentication layout component.
 */
const AuthLayout = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Project Overview Agent
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            AI-powered project analysis and planning
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
