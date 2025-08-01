import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { Lock, User, Eye, EyeOff } from 'lucide-react';

const LoginForm: React.FC<{ onLogin: (username: string, password: string) => Promise<void>; loading: boolean; fieldErrors: any; }>
  = ({ onLogin, loading, fieldErrors }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localErrors, setLocalErrors] = useState<any>({});

  useEffect(() => {
    setLocalErrors(fieldErrors);
  }, [fieldErrors]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalErrors({});
    
    // Add null checks to prevent external script conflicts
    if (!username || !password) {
      setLocalErrors({
        username: !username ? 'Username is required.' : '',
        password: !password ? 'Password is required.' : '',
      });
      return;
    }
    
    // Validate form data before submission
    const formData = {
      username: username?.trim() || '',
      password: password || ''
    };
    
    if (!formData.username || !formData.password) {
      setLocalErrors({
        username: !formData.username ? 'Username is required.' : '',
        password: !formData.password ? 'Password is required.' : '',
      });
      return;
    }
    
    await onLogin(formData.username, formData.password);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 w-full max-w-sm mx-auto animate-fade-in">
      <div className="space-y-2">
        <Label htmlFor="username">Username</Label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="username"
            name="username"
            placeholder="Enter your username"
            className="pl-10"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            aria-required="true"
            autoFocus
            aria-invalid={!!localErrors.username}
            autoComplete="username"
            data-form-type="username"
          />
        </div>
        {localErrors.username && <p className="text-xs text-red-500">{localErrors.username}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Enter your password"
            className="pl-10 pr-10"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            aria-required="true"
            aria-invalid={!!localErrors.password}
            autoComplete="current-password"
            data-form-type="password"
          />
          <button
            type="button"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground focus:outline-none"
            onClick={() => setShowPassword(v => !v)}
            tabIndex={0}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {localErrors.password && <p className="text-xs text-red-500">{localErrors.password}</p>}
      </div>
      <div className="flex justify-between items-center mt-2">
        <Link to="/forgot-password" className="text-sm text-blue-600 hover:underline">Forgot Password?</Link>
        <span className="text-sm">Don't have an account? <Link to="/register" className="text-blue-600 hover:underline">Register</Link></span>
      </div>
      <Button type="submit" className="w-full mt-2 transition-all duration-200 hover:bg-primary/90 focus:ring-2 focus:ring-primary/40" aria-label="Login">
        {loading ? 'Signing in...' : 'Sign in'}
      </Button>
    </form>
  );
};

const BrandingImage: React.FC = () => {
  return (
    <img
      src="/images.png"
      alt="HR branding illustration"
      className="w-64 h-64 object-contain"
      draggable={false}
    />
  );
};

const Login: React.FC = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const { login, role } = useAuth();
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});
  const [error, setError] = useState('');

  const handleLogin = async (username: string, password: string) => {
    setFieldErrors({});
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/token/', { username, password });
      await login(response.data.token);
      // Redirect all users to dashboard after login
      navigate('/');
      toast({ title: 'Login successful', description: 'You have been logged in successfully.' });
    } catch (err: any) {
      setError('Invalid username or password.');
      setFieldErrors({});
      toast({ title: 'Login failed', description: 'Invalid username or password.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 dark:from-gray-900 dark:to-gray-800">
      {/* Left branding / image section (hidden on mobile) */}
      <div className="hidden md:flex flex-col items-center justify-center w-1/2 h-full bg-gradient-to-br from-primary to-secondary text-white p-12 rounded-r-3xl shadow-lg min-h-[600px] animate-fade-in-slow">
        <div className="flex-1 flex flex-col justify-center items-center w-full">
          <div className="text-4xl font-extrabold mb-2 tracking-tight">TalentHub</div>
          <div className="text-lg font-medium opacity-80 mb-2">Candidate Management Platform</div>
          <div className="text-base font-light opacity-90 mb-8 text-center max-w-xs">Empowering HR teams to find, manage, and hire the best talent with ease.</div>
          <div className="rounded-2xl shadow-2xl bg-white/10 backdrop-blur-md p-4 flex items-center justify-center" style={{ minHeight: '180px' }}>
            <BrandingImage />
          </div>
        </div>
      </div>
      {/* Right login form section */}
      <div className="flex-1 flex flex-col items-center justify-center w-full h-full p-4 animate-slide-in-right">
        <Card className="w-full max-w-md shadow-2xl border-0 bg-white/60 dark:bg-gray-900/80 animate-fade-in px-2 py-4 md:px-8 md:py-8 rounded-3xl backdrop-blur-md">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
            <CardDescription>Sign in to your account to continue</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="w-full max-w-sm mx-auto">
              <LoginForm onLogin={handleLogin} loading={loading} fieldErrors={fieldErrors} />
              {error && <div className="text-center text-red-500 mt-2" role="alert">{error}</div>}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;