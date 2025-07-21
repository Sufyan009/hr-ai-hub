import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, Search, User, LogOut, Moon, Sun } from 'lucide-react';
import axios from 'axios';
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

  const fetchNotifications = async () => {
    const token = localStorage.getItem('authToken');
    const res = await axios.get('http://localhost:8000/api/notifications/', {
      headers: { 'Authorization': `Token ${token}` }
    });
    const data = Array.isArray(res.data) ? res.data : [];
    setNotifications(data);
    setUnreadCount(data.filter((n: any) => !n.is_read).length);
  };

  useEffect(() => {
    if (open) fetchNotifications();
  }, [open]);

  const markAsRead = async (id: number) => {
    const token = localStorage.getItem('authToken');
    await axios.patch(`http://localhost:8000/api/notifications/${id}/`, { is_read: true }, {
      headers: { 'Authorization': `Token ${token}` }
    });
    fetchNotifications();
  };

  return (
    <div className="relative">
      <button className="relative" onClick={() => setOpen(!open)}>
        <Bell className="h-6 w-6 text-muted-foreground" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full text-xs px-1.5 py-0.5">{unreadCount}</span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white border rounded shadow-lg z-50 max-h-96 overflow-y-auto">
          <div className="p-3 border-b font-semibold">Notifications</div>
          {Array.isArray(notifications) && notifications.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">No notifications</div>
          ) : Array.isArray(notifications) && notifications.map((n) => (
            <div
              key={n.id}
              className={`p-3 border-b last:border-b-0 cursor-pointer hover:bg-muted ${!n.is_read ? 'bg-blue-50' : ''}`}
              onClick={() => markAsRead(n.id)}
            >
              <div className="text-sm">{n.message}</div>
              <div className="text-xs text-muted-foreground mt-1">{new Date(n.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const AppHeader: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
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
    <header className="sticky top-0 z-40 bg-white/90 dark:bg-background shadow flex items-center justify-between px-4 sm:px-8 py-3 font-sans backdrop-blur">
      <div className="flex flex-col gap-0.5">
        <span className="text-lg sm:text-2xl font-bold text-primary tracking-tight leading-tight">{title}</span>
        <span className="text-xs sm:text-sm text-muted-foreground">{description}</span>
      </div>
      <div className="flex items-center gap-3 sm:gap-4">
        <NotificationDropdown />
        <Button variant="outline" size="icon" className="ml-1" onClick={toggleTheme} aria-label="Toggle theme">
          {isDark ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-primary" />}
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 bg-gradient-to-r from-primary to-secondary rounded-full px-3 py-1 shadow text-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all">
              <div className="h-8 w-8 rounded-full bg-white/20 flex items-center justify-center font-bold text-lg uppercase overflow-hidden">
                {user?.avatar ? (
                  <img src={`http://localhost:8000${user.avatar}`} alt="Avatar" className="h-full w-full rounded-full object-cover" />
                ) : (
                  user?.first_name ? user.first_name[0] : (localStorage.getItem('userName') || 'U')[0]
                )}
              </div>
              <span className="font-medium truncate max-w-[100px] text-white text-base">{user?.first_name || localStorage.getItem('userName') || 'User'}</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="rounded-xl shadow-2xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 p-0 w-72 overflow-hidden">
            {/* Banner */}
            <div className="h-16 w-full bg-gradient-to-r from-primary to-secondary flex items-end justify-center relative">
              <div className="absolute left-1/2 -bottom-8 -translate-x-1/2">
                <div className="h-16 w-16 rounded-full bg-white border-4 border-white dark:border-gray-900 flex items-center justify-center font-bold text-3xl uppercase overflow-hidden shadow-lg">
                  {user?.avatar ? (
                    <img src={`http://localhost:8000${user.avatar}`} alt="Avatar" className="h-full w-full rounded-full object-cover" />
                  ) : (
                    user?.first_name ? user.first_name[0] : (localStorage.getItem('userName') || 'U')[0]
                  )}
                </div>
              </div>
            </div>
            <div className="pt-12 pb-4 flex flex-col items-center">
              <span className="font-semibold text-lg text-gray-900 dark:text-white">{user?.first_name || localStorage.getItem('userName') || 'User'}</span>
              <span className="text-xs text-gray-500 dark:text-gray-300">{user?.email || ''}</span>
            </div>
            <div className="border-t border-gray-100 dark:border-gray-800">
              <DropdownMenuItem onClick={() => navigate('/settings')} className="rounded-none px-5 py-3 hover:bg-primary/10 dark:hover:bg-primary/20 cursor-pointer text-base">
                My profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/settings')} className="rounded-none px-5 py-3 hover:bg-primary/10 dark:hover:bg-primary/20 cursor-pointer text-base">
                Account settings
              </DropdownMenuItem>
              <DropdownMenuItem onClick={logout} className="rounded-none px-5 py-3 hover:bg-red-100 dark:hover:bg-red-900/40 text-red-600 cursor-pointer text-base">
                Sign out
              </DropdownMenuItem>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};