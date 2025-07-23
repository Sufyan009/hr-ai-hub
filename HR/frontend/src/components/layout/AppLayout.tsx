import React from 'react';
import { SidebarProvider } from '@/components/ui/sidebar';
import AppSidebar from './AppSidebar';
import { AppHeader } from './AppHeader';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <SidebarProvider>
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only absolute top-2 left-2 z-50 bg-blue-600 text-white px-4 py-2 rounded shadow focus:outline-none focus:ring-2 focus:ring-blue-400"
        tabIndex={0}
      >
        Skip to main content
      </a>
      <div className="min-h-screen w-full flex flex-col md:flex-row bg-background dark:bg-gray-900" lang="en">
        <AppSidebar role="navigation" />
        <div className="flex-1 flex flex-col overflow-hidden">
          <AppHeader role="banner" />
          <main id="main-content" role="main" className="flex-1 overflow-auto p-2 sm:p-4 md:p-6 animate-fade-in bg-white dark:bg-gray-900 dark:text-gray-100">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};