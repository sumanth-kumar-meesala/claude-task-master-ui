/**
 * Breadcrumbs navigation component.
 */

import { Link } from 'react-router-dom';
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline';
import { cn } from '@/utils/cn';
import { BreadcrumbItem } from '@/types/common';

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

/**
 * Breadcrumbs navigation component.
 */
const Breadcrumbs = ({ items, className }: BreadcrumbsProps) => {
  if (items.length <= 1) {
    return null;
  }

  return (
    <nav className={cn('flex', className)} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {items.map((item, index) => {
          const isFirst = index === 0;
          const isLast = index === items.length - 1;

          return (
            <li key={index} className="flex items-center">
              {/* Separator */}
              {!isFirst && (
                <ChevronRightIcon className="h-4 w-4 text-gray-400 mx-2" />
              )}

              {/* Breadcrumb item */}
              {item.href && !isLast ? (
                <Link
                  to={item.href}
                  className={cn(
                    'flex items-center text-sm font-medium transition-colors',
                    isFirst
                      ? 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                      : 'text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200'
                  )}
                >
                  {isFirst && <HomeIcon className="h-4 w-4 mr-1" />}
                  {item.label}
                </Link>
              ) : (
                <span
                  className={cn(
                    'flex items-center text-sm font-medium',
                    isLast
                      ? 'text-gray-900 dark:text-white'
                      : 'text-gray-500 dark:text-gray-400'
                  )}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {isFirst && <HomeIcon className="h-4 w-4 mr-1" />}
                  {item.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
