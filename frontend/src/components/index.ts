/**
 * Component exports.
 */

// Layout components
export { default as RootLayout } from './layouts/RootLayout';
export { default as DashboardLayout } from './layouts/DashboardLayout';
export { default as AuthLayout } from './layouts/AuthLayout';

// Navigation components
export { default as Sidebar } from './navigation/Sidebar';
export { default as Header } from './navigation/Header';
export { default as Breadcrumbs } from './navigation/Breadcrumbs';

// UI components
export { default as LoadingSpinner } from './ui/LoadingSpinner';
export { default as ErrorBoundary } from './ui/ErrorBoundary';

// Provider components
export { ThemeProvider, useTheme } from './providers/ThemeProvider';
