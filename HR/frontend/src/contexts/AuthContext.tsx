import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  role: string | null;
  login: (token: string) => void;
  logout: () => void;
  loading: boolean;
  hasRole: (role: string) => boolean;
  setUser: (user: any) => void;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  role: null,
  login: () => {},
  logout: () => {},
  loading: true,
  hasRole: () => false,
  setUser: () => {},
});

export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<any | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Check if user is authenticated on initial load
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('authToken');
      
      if (token) {
        try {
          // Set the auth header
          axios.defaults.headers.common['Authorization'] = `Token ${token}`;
          
          // Fetch user profile
          const response = await axios.get('http://localhost:8000/api/user-settings/');
          
          setUser(response.data);
          setRole(response.data.role || null);
          setIsAuthenticated(true);
        } catch (error) {
          // If token is invalid or expired
          localStorage.removeItem('authToken');
          delete axios.defaults.headers.common['Authorization'];
          setRole(null);
        }
      } else {
        setRole(null);
      }
      
      setLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = async (token: string) => {
    localStorage.setItem('authToken', token);
    axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    setIsAuthenticated(true);
    
    // Fetch user profile after login
    try {
      const response = await axios.get('http://localhost:8000/api/user-settings/');
      setUser(response.data);
      setRole(response.data.role || null);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      setRole(null);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    setRole(null);
  };

  const hasRole = (requiredRole: string) => {
    return role === requiredRole;
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, role, login, logout, loading, hasRole, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};