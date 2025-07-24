import React, { useEffect, useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  Users,
  UserPlus,
  LayoutDashboard,
  MessageCircle,
  Settings,
  Building,
  Briefcase,
  Menu,
  X,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';
import { useSidebar } from '@/components/ui/sidebar';

const MAIN_SIDEBAR_COLLAPSED_KEY = 'mainSidebarCollapsed';

const navigationItems = [
  {
    title: 'Dashboard',
    url: '/',
    icon: LayoutDashboard,
    description: 'Overview & Analytics',
    badge: null,
  },
  {
    title: 'Candidates',
    url: '/candidates',
    icon: Users,
    description: 'Manage All Candidates',
    badge: null,
  },
  {
    title: 'Jobs',
    url: '/jobs',
    icon: Briefcase,
    description: 'Job Postings',
    badge: null,
  },
  {
    title: 'Add Candidate',
    url: '/candidates/new',
    icon: UserPlus,
    description: 'Add New Candidate',
    badge: null,
  },
  {
    title: 'AI Assistant',
    url: '/chat',
    icon: MessageCircle,
    description: 'Chat with AI',
    badge: { count: 'New', variant: 'destructive' },
  },
];

const secondaryItems = [
  {
    title: 'Settings',
    url: '/settings',
    icon: Settings,
    description: 'App Configuration',
    badge: null,
  },
  {
    title: 'Logout',
    url: '/logout',
    icon: LogOut,
    description: 'Sign Out',
    badge: null,
  },
];

const badgeVariantClass = {
  destructive: 'bg-red-500 text-white hover:bg-red-600',
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'bg-gray-500 text-white hover:bg-gray-600',
};

const AppSidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === 'collapsed';
  const [candidateCount, setCandidateCount] = useState(null);

  useEffect(() => {
    localStorage.setItem(MAIN_SIDEBAR_COLLAPSED_KEY, isCollapsed ? 'true' : 'false');
  }, [isCollapsed]);

  useEffect(() => {
    const fetchCount = async () => {
      try {
        const res = await api.get('/metrics/');
        setCandidateCount(res.data.total_candidates ?? null);
      } catch {
        setCandidateCount(null);
      }
    };
    fetchCount();
  }, []);

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const getVisibleNavigationItems = () => {
    if (!user) return [];
    return navigationItems.filter(item => {
      if (item.title === 'Add Candidate' || item.title === 'Jobs') {
        return user.role === 'admin' || user.role === 'recruiter';
      }
      return true;
    });
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Skip to navigation link for accessibility */}
      <a
        href="#sidebar-navigation"
        className="sr-only focus:not-sr-only absolute top-2 left-2 z-50 bg-blue-600 text-white px-4 py-2 rounded shadow focus:outline-none focus:ring-2 focus:ring-blue-400"
        tabIndex={0}
      >
        Skip to navigation
      </a>
      
      {/* Mobile menu button */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white dark:bg-gray-800 rounded-full shadow-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-300"
        onClick={() => setMobileOpen((v) => !v)}
        aria-label={mobileOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {mobileOpen ? (
          <X className="h-6 w-6 text-gray-700 dark:text-gray-200" />
        ) : (
          <Menu className="h-6 w-6 text-gray-700 dark:text-gray-200" />
        )}
      </button>

      {/* Sidebar */}
      <aside
        id="sidebar-navigation"
        tabIndex={0}
        className={`fixed inset-y-0 left-0 z-40 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-all duration-300 ease-in-out md:sticky md:top-0 md:translate-x-0 ${
          mobileOpen ? 'translate-x-0 shadow-2xl w-64' : '-translate-x-full md:translate-x-0'
        } ${isCollapsed ? 'md:w-16' : 'md:w-64'}`}
        aria-label="Sidebar navigation"
      >
        <div className="flex flex-col h-full">
          {/* Brand */}
          <div className={`flex items-center gap-3 px-6 py-5 border-b border-gray-100 dark:border-gray-800 bg-gradient-to-r from-blue-50 to-white dark:from-gray-900 dark:to-gray-900 ${
            isCollapsed ? 'justify-center px-3' : ''
          }`}>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 dark:bg-blue-500 shadow-md transform transition-all duration-300 hover:scale-110 hover:rotate-3">
              <Building className="h-5 w-5 text-white" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                  TalentHub
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                  Recruitment Dashboard
                </span>
              </div>
            )}
          </div>

          {/* Main Navigation */}
          <nav className="flex-1 py-4 overflow-y-auto sidebar-scroll">
            {!isCollapsed && (
              <div className="px-6 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                Navigation
              </div>
            )}
            <ul className="space-y-1">
              {getVisibleNavigationItems().map((item) => (
                <li key={item.title}>
                  <NavLink
                    to={item.url}
                    end={true}
                    className={({ isActive }) =>
                      `flex items-center gap-3 mx-2 rounded-xl transition-all duration-300 ease-in-out group relative ${
                        isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
                      } ${
                        isActive
                          ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-200 font-semibold shadow-md'
                          : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-blue-600 dark:group-hover:text-blue-300'
                      } focus:outline-none focus:ring-2 focus:ring-blue-500/30 transform hover:-translate-y-0.5`
                    }
                    title={isCollapsed ? item.title : undefined}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0 transition-transform duration-300 group-hover:scale-110" />
                    {!isCollapsed && (
                      <>
                        <div className="flex flex-col flex-1 min-w-0">
                          <span className="text-sm font-medium truncate">{item.title}</span>
                          <span className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-300 transition-colors duration-300 truncate">
                            {item.description}
                          </span>
                        </div>
                        {item.title === 'Candidates' && candidateCount && candidateCount > 0 && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-600 dark:bg-blue-500 text-white group-hover:bg-blue-700 transition-colors duration-300">
                            {candidateCount}
                          </span>
                        )}
                        {item.title !== 'Candidates' && item.badge && (
                          <span
                            className={`ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${badgeVariantClass[item.badge.variant]} transition-colors duration-300`}
                          >
                            {item.badge.count}
                          </span>
                        )}
                      </>
                    )}
                    
                    {/* Tooltip for collapsed state */}
                    {isCollapsed && (
                      <div className="absolute left-full ml-2 px-3 py-2 bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                        <div className="font-medium">{item.title}</div>
                        <div className="text-xs text-gray-300 dark:text-gray-400">{item.description}</div>
                        <div className="absolute top-1/2 -left-1 -translate-y-1/2 w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45"></div>
                      </div>
                    )}
                    
                    {/* Badge indicator for collapsed state */}
                    {isCollapsed && (item.badge || (item.title === 'Candidates' && candidateCount && candidateCount > 0)) && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
                    )}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>

          {/* Secondary Navigation */}
          <nav className="mt-auto border-t border-gray-100 dark:border-gray-800 py-4">
            {!isCollapsed && (
              <div className="px-6 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                Account
              </div>
            )}
            <ul className="space-y-1">
              {secondaryItems.map((item) => (
                <li key={item.title}>
                  <NavLink
                    to={item.url}
                    className={({ isActive }) =>
                      `flex items-center gap-3 mx-2 rounded-xl transition-all duration-300 ease-in-out group relative ${
                        isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3'
                      } ${
                        isActive
                          ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-200 font-semibold shadow-md'
                          : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-300'
                      } focus:outline-none focus:ring-2 focus:ring-blue-500/30 transform hover:-translate-y-0.5`
                    }
                    onClick={item.title === 'Logout' ? handleLogout : undefined}
                    title={isCollapsed ? item.title : undefined}
                    aria-current={isActive(item.url) ? 'page' : undefined}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0 transition-transform duration-300 group-hover:scale-110" />
                    {!isCollapsed && (
                      <div className="flex flex-col flex-1 min-w-0">
                        <span className="text-sm font-medium truncate">{item.title}</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-300 transition-colors duration-300 truncate">
                          {item.description}
                        </span>
                      </div>
                    )}
                    
                    {/* Tooltip for collapsed state */}
                    {isCollapsed && (
                      <div className="absolute left-full ml-2 px-3 py-2 bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                        <div className="font-medium">{item.title}</div>
                        <div className="text-xs text-gray-300 dark:text-gray-400">{item.description}</div>
                        <div className="absolute top-1/2 -left-1 -translate-y-1/2 w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45"></div>
                      </div>
                    )}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {/* Mobile overlay */}
        {mobileOpen && (
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 md:hidden"
            onClick={() => setMobileOpen(false)}
            aria-label="Close sidebar overlay"
          />
        )}
      </aside>
    </>
  );
};

export default AppSidebar;