/**
 * Dashboard layout component with sidebar navigation.
 */

import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';
import { cn } from '@/utils/cn';
import Sidebar from '@/components/navigation/Sidebar';
import Header from '@/components/navigation/Header';
import Breadcrumbs from '@/components/navigation/Breadcrumbs';
import { navigationUtils } from '@/router';

/**
 * Navigation items configuration.
 */
const navigationItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon,
  },
  {
    id: 'projects',
    label: 'Projects',
    href: '/dashboard/projects',
    icon: FolderIcon,
  },

];

/**
 * Dashboard layout component.
 */
const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const pageTitle = navigationUtils.getPageTitle(location.pathname);
  const breadcrumbs = navigationUtils.getBreadcrumbs(location.pathname);

  return (
    <div className="flex h-screen bg-base-200">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-base-100 shadow-lg transition-transform duration-300 ease-in-out lg:static lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <Sidebar
          navigationItems={navigationItems}
          currentPath={location.pathname}
          onClose={() => setSidebarOpen(false)}
        />
      </div>

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <Header
          title={pageTitle}
          onMenuClick={() => setSidebarOpen(true)}
          showMenuButton={true}
        />

        {/* Breadcrumbs */}
        <div className="border-b border-base-300 bg-base-100 px-4 py-2">
          <Breadcrumbs items={breadcrumbs} />
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-base-200 p-4">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
