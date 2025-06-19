/**
 * Sidebar navigation component.
 */

import { Link } from 'react-router-dom';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { cn } from '@/utils/cn';
import { NavItem } from '@/types/common';

interface SidebarProps {
  navigationItems: NavItem[];
  currentPath: string;
  onClose?: () => void;
}

/**
 * Sidebar navigation component.
 */
const Sidebar = ({ navigationItems, currentPath, onClose }: SidebarProps) => {
  const isActivePath = (href: string) => {
    if (href === '/dashboard') {
      return currentPath === '/dashboard';
    }
    return currentPath.startsWith(href);
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">PA</span>
          </div>
          <span className="text-lg font-semibold text-gray-900 dark:text-white">
            Project Agent
          </span>
        </div>
        
        {/* Close button for mobile */}
        {onClose && (
          <button
            onClick={onClose}
            className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navigationItems.map((item) => {
          const isActive = isActivePath(item.href);
          const Icon = item.icon;

          return (
            <Link
              key={item.id}
              to={item.href}
              onClick={onClose}
              className={cn(
                'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              )}
            >
              {Icon && (
                <Icon
                  className={cn(
                    'mr-3 h-5 w-5',
                    isActive
                      ? 'text-blue-500 dark:text-blue-300'
                      : 'text-gray-400 dark:text-gray-500'
                  )}
                />
              )}
              {item.label}
              {item.badge && (
                <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          <p>Version 0.1.0</p>
          <p className="mt-1">© 2024 Project Overview Agent</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
