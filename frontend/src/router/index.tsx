/**
 * React Router configuration for the Project Overview Agent.
 */

import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Suspense, lazy } from 'react';

// Layout components
import RootLayout from '@/components/layouts/RootLayout';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import AuthLayout from '@/components/layouts/AuthLayout';

// Loading component
import LoadingSpinner from '@/components/ui/LoadingSpinner';

// Lazy load pages for code splitting
const HomePage = lazy(() => import('@/pages/HomePage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const ProjectsPage = lazy(() => import('@/pages/ProjectsPage'));
const ProjectDetailPage = lazy(() => import('@/pages/ProjectDetailPage'));

const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));
const ErrorPage = lazy(() => import('@/pages/ErrorPage'));

/**
 * Wrapper component for lazy-loaded pages with loading state.
 */
const PageWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<LoadingSpinner />}>
    {children}
  </Suspense>
);

/**
 * Router configuration.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <PageWrapper><ErrorPage /></PageWrapper>,
    children: [
      {
        index: true,
        element: <PageWrapper><HomePage /></PageWrapper>,
      },
      {
        path: 'dashboard',
        element: <DashboardLayout />,
        children: [
          {
            index: true,
            element: <PageWrapper><DashboardPage /></PageWrapper>,
          },
          {
            path: 'projects',
            children: [
              {
                index: true,
                element: <PageWrapper><ProjectsPage /></PageWrapper>,
              },
              {
                path: 'new',
                element: <PageWrapper><ProjectsPage /></PageWrapper>,
              },
              {
                path: ':projectId',
                children: [
                  {
                    index: true,
                    element: <PageWrapper><ProjectDetailPage /></PageWrapper>,
                  },

                ],
              },
            ],
          },


         

        ],
      },
      {
        path: 'auth',
        element: <AuthLayout />,
        children: [
          // Future authentication routes can be added here
        ],
      },
    ],
  },
  {
    path: '*',
    element: <PageWrapper><NotFoundPage /></PageWrapper>,
  },
]);

/**
 * Router provider component.
 */
export const AppRouter = () => {
  return <RouterProvider router={router} />;
};

/**
 * Route paths constants for type-safe navigation.
 */
export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  PROJECTS: '/dashboard/projects',
  PROJECT_NEW: '/dashboard/projects/new',
  PROJECT_DETAIL: (id: string) => `/dashboard/projects/${id}`,



  AUTH: '/auth',
} as const;

/**
 * Navigation utilities.
 */
export const navigationUtils = {
  /**
   * Check if a path is active.
   */
  isActivePath: (currentPath: string, targetPath: string): boolean => {
    if (targetPath === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(targetPath);
  },

  /**
   * Get breadcrumb items for a path.
   */
  getBreadcrumbs: (pathname: string): Array<{ label: string; href?: string }> => {
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs: Array<{ label: string; href?: string }> = [
      { label: 'Home', href: '/' },
    ];

    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLast = index === segments.length - 1;
      
      let label = segment.charAt(0).toUpperCase() + segment.slice(1);
      
      // Handle special cases
      if (segment === 'dashboard') {
        label = 'Dashboard';
      } else if (segment.length > 20) {
        // Truncate long IDs
        label = `${segment.substring(0, 8)}...`;
      }

      breadcrumbs.push({
        label,
        href: isLast ? undefined : currentPath,
      });
    });

    return breadcrumbs;
  },

  /**
   * Get page title for a path.
   */
  getPageTitle: (pathname: string): string => {
    const segments = pathname.split('/').filter(Boolean);

    if (pathname === '/') return 'Home';
    if (pathname === '/dashboard') return 'Dashboard';
    if (pathname.startsWith('/dashboard/projects')) {
      if (segments.length === 2) return 'Projects';
      return 'Project Details';
    }

    return 'Page Not Found';
  },
};

/**
 * Route guards and protection utilities.
 */
export const routeGuards = {
  /**
   * Check if user can access a route.
   */
  canAccessRoute: (_pathname: string): boolean => {
    // For now, all routes are accessible
    // This can be extended with authentication logic
    return true;
  },

  /**
   * Get redirect path for unauthorized access.
   */
  getRedirectPath: (_pathname: string): string => {
    // For now, redirect to home
    // This can be extended with authentication logic
    return '/';
  },
};

export default AppRouter;
