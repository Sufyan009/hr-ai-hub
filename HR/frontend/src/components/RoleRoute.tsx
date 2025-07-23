import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { NotAuthorized } from '@/pages/NotFound';

interface RoleRouteProps {
  requiredRole: string;
  redirectTo?: string;
}

export const RoleRoute: React.FC<RoleRouteProps> = ({ requiredRole, redirectTo = '/login' }) => {
  const { isAuthenticated, loading, hasRole } = useAuth();

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} />;
  }

  if (!hasRole(requiredRole)) {
    // Show Not Authorized page
    return <NotAuthorized />;
  }

  return <Outlet />;
}; 