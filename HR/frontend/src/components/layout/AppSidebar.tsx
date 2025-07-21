import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Users, 
  UserPlus, 
  LayoutDashboard, 
  MessageCircle, 
  Settings,
  Building,
  TrendingUp,
  ChevronRight,
  Activity,
  Zap,
  User,
  LogOut,
  Menu
} from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from '@/components/ui/sidebar';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useNavigate } from 'react-router-dom';
import clsx from 'clsx';

const navigationItems = [
  {
    title: 'Dashboard',
    url: '/',
    icon: LayoutDashboard,
    description: 'Overview & Analytics',
    badge: null
  },
  {
    title: 'Candidates',
    url: '/candidates',
    icon: Users,
    description: 'Manage All Candidates',
    badge: { count: 25, variant: 'primary' as const }
  },
  {
    title: 'Add Candidate',
    url: '/candidates/new',
    icon: UserPlus,
    description: 'Add New Candidate',
    badge: null
  },
  {
    title: 'AI Assistant',
    url: '/chat',
    icon: MessageCircle,
    description: 'Chat with AI',
    badge: { count: 'New', variant: 'destructive' as const }
  }
];

const secondaryItems = [
  {
    title: 'Settings',
    url: '/settings',
    icon: Settings,
    description: 'App Configuration',
    badge: null
  }
];

export const AppSidebar: React.FC = () => {
  const { state, setState } = useSidebar();
  const location = useLocation();
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const isCollapsed = state === "collapsed";
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 bg-white/90 rounded-full p-2 shadow-lg border border-gray-200"
        onClick={() => setMobileOpen((v) => !v)}
        aria-label="Open sidebar"
      >
        <Menu className="h-6 w-6 text-primary" />
      </button>
      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed md:static z-40 transition-transform duration-300 flex flex-col h-full min-h-screen bg-gradient-to-b from-white to-gray-50 border-r border-gray-200 w-64 md:w-64',
          'dark:bg-gray-900 dark:text-gray-100 dark:border-gray-800',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
          'md:translate-x-0'
        )}
        style={{ minWidth: 0 }}
      >
        {/* Brand */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-100 bg-white/80 backdrop-blur sticky top-0 z-10 dark:bg-gray-900 dark:border-gray-800">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-primary shadow">
            <Building className="h-5 w-5 text-primary-foreground" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold text-gray-900 tracking-tight leading-tight dark:text-white">TalentHub</span>
            <span className="text-xs text-gray-500 dark:text-gray-300">Candidate Management</span>
          </div>
        </div>
        {/* Main Navigation */}
        <nav className="flex-1 flex flex-col gap-2 px-2 py-4">
          <div className="text-xs font-semibold text-gray-400 mb-2 px-2 dark:text-gray-500">Main Navigation</div>
          {navigationItems.map((item) => (
            <NavLink
              key={item.title}
              to={item.url}
              end={item.url === '/candidates/new'} // Only exact match for Add Candidate
              className={({ isActive: navActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-xl px-4 py-3 text-base font-medium transition-all duration-200 relative group',
                  navActive
                    ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg scale-[1.03]'
                    : 'text-gray-700 hover:bg-primary/10 hover:text-primary hover:shadow-md',
                  'focus:outline-none focus:ring-2 focus:ring-primary/40'
                )
              }
              title={item.title}
              onMouseEnter={() => setHoveredItem(item.title)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <item.icon className="h-6 w-6 flex-shrink-0" />
              <div className="flex flex-col flex-1 min-w-0">
                <span className="truncate">{item.title}</span>
                <span className="text-xs opacity-60 truncate">{item.description}</span>
              </div>
              {item.badge && (
                <span className={clsx(
                  'ml-2 px-2 py-0.5 rounded-full text-xs font-semibold',
                  item.badge.variant === 'primary' && 'bg-primary text-white',
                  item.badge.variant === 'destructive' && 'bg-red-500 text-white',
                  item.badge.variant === 'secondary' && 'bg-gray-500 text-white'
                )}>
                  {item.badge.count}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
        {/* Secondary Navigation */}
        <nav className="flex flex-col gap-2 px-2 py-4 mt-auto border-t border-gray-100 dark:border-gray-800">
          <div className="text-xs font-semibold text-gray-400 mb-2 px-2 dark:text-gray-500">Settings</div>
          {secondaryItems.map((item) => (
            <NavLink
              key={item.title}
              to={item.url}
              className={({ isActive: navActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-xl px-4 py-3 text-base font-medium transition-all duration-200 relative group',
                  navActive || isActive(item.url)
                    ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg scale-[1.03]'
                    : 'text-gray-700 hover:bg-primary/10 hover:text-primary hover:shadow-md',
                  'focus:outline-none focus:ring-2 focus:ring-primary/40'
                )
              }
              title={item.title}
            >
              <item.icon className="h-6 w-6 flex-shrink-0" />
              <div className="flex flex-col flex-1 min-w-0">
                <span className="truncate">{item.title}</span>
                <span className="text-xs opacity-60 truncate">{item.description}</span>
              </div>
            </NavLink>
          ))}
        </nav>
        {/* Overlay for mobile */}
        {mobileOpen && (
          <div
            className="fixed inset-0 bg-black/30 z-30 md:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </aside>
    </>
  );
};