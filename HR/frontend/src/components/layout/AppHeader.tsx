import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, Search, User, LogOut, Moon, Sun, Settings, Type } from 'lucide-react';
import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { useAuth } from '@/contexts/AuthContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';

const getPageTitle = (pathname: string): string => {
  if (pathname === '/') return 'Dashboard';
  if (pathname === '/candidates') return 'Candidates';
  if (pathname === '/candidates/new') return 'Add Candidate';
  if (pathname.startsWith('/candidates/')) return 'Candidate Details';
  if (pathname === '/chat') return 'AI Assistant';
  if (pathname === '/settings') return 'Settings';
  return 'TalentHub';
};

const getPageDescription = (pathname: string): string => {
  if (pathname === '/') return 'Overview of your recruitment metrics and recent activities';
  if (pathname === '/candidates') return 'Manage and search through your candidate database';
  if (pathname === '/candidates/new') return 'Add a new candidate to your database';
  if (pathname.startsWith('/candidates/')) return 'View and manage candidate information';
  if (pathname === '/chat') return 'Get AI-powered insights about your candidates';
  if (pathname === '/settings') return 'Configure your application settings';
  return 'Professional candidate management platform';
};

const NotificationDropdown: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { toast } = useToast();

  // Fetch notifications and update both list and unread count
  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      const data = Array.isArray(res.data) ? res.data : [];
      setNotifications(data);
      setUnreadCount(data.filter((n: any) => !n.is_read).length);
    } catch (err) {
      console.error('Error fetching notifications:', err);
    }
  };

  useEffect(() => {
    if (open) fetchNotifications();
  }, [open]);

  // Poll for notifications every 30 seconds, but update both list and count
  useEffect(() => {
    const interval = setInterval(() => {
      if (open) {
        fetchNotifications();
      } else {
        // Only update unread count if dropdown is closed
        api.get('/notifications/').then(res => {
          const data = Array.isArray(res.data) ? res.data : [];
          setUnreadCount(data.filter((n: any) => !n.is_read).length);
        }).catch(err => {
          console.error('Error polling notifications:', err);
        });
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [open]);

  const markAsRead = async (id: number) => {
    try {
      await api.patch(`/notifications/${id}/`, { is_read: true });
      fetchNotifications();
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  return (
    <div className="relative">
      <button
        className="relative p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
        onClick={() => setOpen(!open)}
      >
        <Bell className="h-5 w-5 text-gray-600 dark:text-gray-300" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-600 text-white rounded-full text-xs px-1.5 py-0.5 font-medium">{unreadCount}</span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 mt-3 w-96 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-50 max-h-[400px] overflow-y-auto">
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 font-semibold text-gray-800 dark:text-gray-200">Notifications</div>
          {Array.isArray(notifications) && notifications.length === 0 ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400 text-sm">No notifications</div>
          ) : (
            Array.isArray(notifications) &&
            notifications.map((n) => (
              <div
                key={n.id}
                className={`p-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150 ${
                  !n.is_read ? 'bg-blue-50 dark:bg-blue-900/30' : ''
                }`}
                onClick={() => markAsRead(n.id)}
              >
                <div className="text-sm text-gray-800 dark:text-gray-200">{n.message}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export const AppHeader: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();
  const title = getPageTitle(location.pathname);
  const description = getPageDescription(location.pathname);
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark' || document.documentElement.classList.contains('dark');
    }
    return false;
  });

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const isDarkNow = !document.documentElement.classList.contains('dark');
    if (isDarkNow) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
    setIsDark(isDarkNow);
  };

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-800 backdrop-blur-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0 px-4 sm:px-6 md:px-8 py-3 sm:py-4 font-sans transition-all duration-300">
      <div className="flex items-center gap-4">
        <SidebarTrigger className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200">
          {/* Custom sidebar/layout icon as per user screenshot */}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-gray-600 dark:text-gray-300">
            <rect x="3" y="4" width="18" height="16" rx="2" ry="2" />
            <line x1="9" y1="4" x2="9" y2="20" />
          </svg>
        </SidebarTrigger>
        <div className="flex flex-col gap-1">
          <h1 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">{title}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
        </div>
      </div>
      <div className="flex flex-row items-center gap-3 sm:gap-4">
        <div className="relative hidden sm:block">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search candidates..."
            className="pl-10 w-48 sm:w-64 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-sm"
          />
        </div>
        <NotificationDropdown />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full px-3 py-1.5 shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <div className="h-8 w-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center font-medium text-gray-600 dark:text-gray-300 text-sm uppercase overflow-hidden">
                {user?.avatar ? (
                  <img src={`http://localhost:8000${user.avatar}`} alt="Avatar" className="h-full w-full rounded-full object-cover" />
                ) : (
                  user?.first_name ? user.first_name[0] : (localStorage.getItem('userName') || 'U')[0]
                )}
              </div>
              <span className="font-medium text-gray-800 dark:text-gray-200 text-sm truncate max-w-[120px]">
                {user?.first_name || localStorage.getItem('userName') || 'User'}
              </span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-72 p-0 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <div className="px-5 pt-4 pb-2 border-b border-gray-200 dark:border-gray-700 flex flex-col items-start">
              <span className="font-semibold text-base text-gray-900 dark:text-white flex items-center gap-2">
                {user?.first_name || localStorage.getItem('userName') || 'User'}
                {user?.role && (
                  <Badge className="ml-2 bg-blue-600 dark:bg-blue-500 text-white px-2 py-0.5 text-xs font-semibold rounded">
                    {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                  </Badge>
                )}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">{user?.email || ''}</span>
            </div>
            <div className="py-2 flex flex-col gap-1">
              <DropdownMenuItem
                onClick={toggleTheme}
                className="flex items-center gap-2 px-5 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 transition-colors duration-150 cursor-pointer"
              >
                {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                {isDark ? 'Light Mode' : 'Dark Mode'}
              </DropdownMenuItem>
              <DropdownMenuItem className="flex items-center gap-2 px-5 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 transition-colors duration-150 cursor-pointer">
                <Type className="h-4 w-4" />
                Font Size
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => navigate('/settings')}
                className="flex items-center gap-2 px-5 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 transition-colors duration-150 cursor-pointer"
              >
                <Settings className="h-4 w-4" />
                Settings
              </DropdownMenuItem>
            </div>
            <DropdownMenuSeparator className="bg-gray-200 dark:bg-gray-700" />
            <DropdownMenuItem
              onClick={logout}
              className="flex items-center gap-2 px-5 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 focus:bg-red-50 dark:focus:bg-red-900/30 font-semibold transition-colors duration-150 cursor-pointer"
            >
              <LogOut className="h-4 w-4" />
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};