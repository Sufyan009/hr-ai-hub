import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import {
  User,
  Bell,
  Shield,
  Palette,
  Key,
  Mail,
  Globe,
  Save,
  Eye,
  EyeOff,
  RefreshCw,
  Clipboard
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';

const API_URL = 'http://localhost:8000/api/user-settings/';

const Settings: React.FC = () => {
  const { toast } = useToast();
  const { user, isAuthenticated, setUser } = useAuth();
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fieldErrors, setFieldErrors] = useState<any>({});
  // Validation helpers
  const validateEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  // Inline validation as user types
  useEffect(() => {
    const errors: any = {};
    if (settings?.email && !validateEmail(settings.email)) errors.email = 'Invalid email format.';
    setFieldErrors(errors);
  }, [settings?.email]);
  // Avatar file validation
  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setFieldErrors((prev: any) => ({ ...prev, avatar: 'Avatar must be an image file.' }));
        return;
      }
      if (file.size > 2 * 1024 * 1024) {
        setFieldErrors((prev: any) => ({ ...prev, avatar: 'Avatar file size must be less than 2MB.' }));
        return;
      }
      setAvatarPreview(URL.createObjectURL(file));
      setSettings((prev: any) => ({ ...prev, avatar: file }));
      setChangedFields((prev: any) => ({ ...prev, avatar: file }));
      setFieldErrors((prev: any) => ({ ...prev, avatar: undefined }));
    }
  };

  const editableFields = [
    { key: 'first_name', label: 'First Name', type: 'text' },
    { key: 'last_name', label: 'Last Name', type: 'text' },
    { key: 'title', label: 'Job Title', type: 'text' },
    { key: 'company', label: 'Company', type: 'text' },
  ];

  const [changedFields, setChangedFields] = useState<any>({});

  useEffect(() => {
    const fetchSettings = async () => {
      if (!isAuthenticated) return;
      
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(API_URL);
        setSettings(res.data);
      } catch (err) {
        setError('Failed to load settings.');
        toast({ 
          title: 'Error loading settings', 
          description: 'Please try again or contact support.', 
          variant: 'destructive' 
        });
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, [isAuthenticated]);

  const handleSettingChange = (key: string, value: any) => {
    setSettings((prev: any) => ({ ...prev, [key]: value }));
    setChangedFields((prev: any) => ({ ...prev, [key]: value }));
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);
    const formData = new FormData();
    Object.keys(changedFields).forEach(key => {
      if (key === 'avatar' && changedFields[key] instanceof File) {
        formData.append('avatar', changedFields[key]);
      } else {
        formData.append(key, String(changedFields[key]));
      }
    });
    try {
      const res = await axios.patch(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Token ${localStorage.getItem('authToken')}`
        }
      });
      setUser(res.data);
      setSettings(res.data);
      setChangedFields({});
      setSuccess(true);
      toast({ title: 'Success', description: 'Your settings have been updated.' });
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to save settings.');
      toast({ title: 'Error', description: err?.response?.data?.detail || 'Failed to save settings.', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
};

  const handleRegenerateKey = async () => {
    setRegenerating(true);
    setError(null);
    try {
      // Generate a new random API key (in real app, backend should do this)
      const newKey = 'sk-' + Math.random().toString(36).slice(2, 18) + Math.random().toString(36).slice(2, 18);
      await axios.patch(API_URL, { api_key: newKey });
      setSettings((prev: any) => ({ ...prev, api_key: newKey }));
      toast({ title: 'API Key regenerated', description: 'A new API key has been generated.' });
    } catch (err) {
      setError('Failed to regenerate API key.');
      toast({ title: 'Error', description: 'Failed to regenerate API key.', variant: 'destructive' });
    } finally {
      setRegenerating(false);
    }
  };

  const handleCopyKey = () => {
    if (settings?.api_key) {
      navigator.clipboard.writeText(settings.api_key);
      toast({ title: 'Copied', description: 'API key copied to clipboard.' });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 1000);
    }
  };

  if (loading) {
    return <div className="text-center py-10" role="status">Loading settings...</div>;
  }
  if (error) {
    return <div className="text-center text-red-500 py-10" role="alert">{error}</div>;
  }
  if (!settings) {
    return <div className="text-center py-10">No settings found.</div>;
  }

  return (
    <form aria-label="User Settings Form">
      {/* Responsive main container */}
      <div className="w-full px-2 sm:px-4 md:px-6 md:max-w-4xl md:mx-auto space-y-6 animate-fade-in dark:text-gray-100">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground" id="settings-title">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences
          </p>
        </div>

        <Card className="shadow-soft border-0 bg-gradient-card hover:shadow-medium transition-all duration-300 dark:bg-gray-900 dark:border-gray-800">
          <CardContent className="p-0">
            <Tabs defaultValue="profile" className="w-full dark:bg-gray-900">
              <TabsList className="grid w-full grid-cols-5 bg-muted/50 dark:bg-gray-800/80">
                <TabsTrigger value="profile" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-200">Profile</TabsTrigger>
                <TabsTrigger value="notifications" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-200">Notifications</TabsTrigger>
                <TabsTrigger value="privacy" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-200">Privacy</TabsTrigger>
                <TabsTrigger value="appearance" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-200">Appearance</TabsTrigger>
                <TabsTrigger value="security" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-200">Security</TabsTrigger>
              </TabsList>

              {/* Profile Tab */}
              <TabsContent value="profile" className="p-6 space-y-6">
                <div className="flex items-start gap-6">
                  <div className="flex flex-col items-center space-y-3">
                    <div className="relative">
                      <img
                        src={avatarPreview || (settings.avatar ? `http://localhost:8000${settings.avatar}` : '/default-avatar.png')}
                        alt="Avatar"
                        className="h-24 w-24 rounded-full object-cover"
                      />
                      <div className="absolute -bottom-1 -right-1 h-6 w-6 bg-green-500 rounded-full border-2 border-background flex items-center justify-center">
                        <span className="text-xs text-white">✓</span>
                      </div>
                    </div>
                    <input
                      type="file"
                      accept="image/*"
                      ref={fileInputRef}
                      className="hidden"
                      onChange={handleAvatarChange}
                      aria-label="Upload avatar image"
                    />
                    <Button variant="outline" size="sm" onClick={handleAvatarClick}>
                      Change Avatar
                    </Button>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-semibold text-foreground mb-1">
                      {settings.first_name} {settings.last_name}
                    </h3>
                    <p className="text-muted-foreground mb-2">{settings.title || 'No title set'}</p>
                    <p className="text-sm text-muted-foreground">{settings.company || 'No company set'}</p>
                    <div className="flex items-center gap-2 mt-3">
                      <Badge variant="secondary">Active</Badge>
                      <Badge variant="outline">Verified</Badge>
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {editableFields.map(field => (
                    <div key={field.key} className="space-y-2">
                      <Label htmlFor={field.key}>{field.label}</Label>
                      <Input
                        id={field.key}
                        type={field.type}
                        value={settings[field.key] || ''}
                        onChange={e => handleSettingChange(field.key, e.target.value)}
                        aria-required="true"
                        aria-invalid={!!fieldErrors[field.key]}
                      />
                      {fieldErrors[field.key] && <p className="text-xs text-red-500">{fieldErrors[field.key]}</p>}
                    </div>
                  ))}
                  <div className="space-y-2">
                    <Label htmlFor="avatar">Avatar</Label>
                    <Input
                      id="avatar"
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      aria-describedby="avatar-desc"
                      aria-invalid={!!fieldErrors.avatar}
                    />
                    <span id="avatar-desc">Accepted: Images only. Max 2MB.</span>
                    {fieldErrors.avatar && <p className="text-xs text-red-500">{fieldErrors.avatar}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={settings.email || ''}
                      onChange={e => handleSettingChange('email', e.target.value)}
                      className="hover:border-primary/50 focus:border-primary transition-colors duration-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="title">Job Title</Label>
                    <Input
                      id="title"
                      value={settings.title || ''}
                      onChange={e => handleSettingChange('title', e.target.value)}
                      className="hover:border-primary/50 focus:border-primary transition-colors duration-200"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="company">Company</Label>
                  <Input
                    id="company"
                    value={settings.company || ''}
                    onChange={e => handleSettingChange('company', e.target.value)}
                    className="hover:border-primary/50 focus:border-primary transition-colors duration-200"
                  />
                </div>
              </TabsContent>

              {/* Notifications Tab */}
              <TabsContent value="notifications" className="p-6 space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label className="flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        Email Notifications
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications via email
                      </p>
                    </div>
                    <Switch
                      checked={!!settings.email_notifications}
                      onCheckedChange={checked => handleSettingChange('email_notifications', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label className="flex items-center gap-2">
                        <Bell className="h-4 w-4" />
                        Push Notifications
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Receive push notifications in browser
                      </p>
                    </div>
                    <Switch
                      checked={!!settings.push_notifications}
                      onCheckedChange={checked => handleSettingChange('push_notifications', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        Candidate Updates
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Get notified when candidates update their status
                      </p>
                    </div>
                    <Switch
                      checked={!!settings.candidate_updates}
                      onCheckedChange={checked => handleSettingChange('candidate_updates', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Weekly Reports</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive weekly recruitment analytics reports
                      </p>
                    </div>
                    <Switch
                      checked={!!settings.weekly_reports}
                      onCheckedChange={checked => handleSettingChange('weekly_reports', checked)}
                    />
                  </div>
                </div>
              </TabsContent>

              {/* Privacy Tab */}
              <TabsContent value="privacy" className="p-6 space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Profile Visibility</Label>
                    <Select
                      value={settings.profile_visibility || 'team'}
                      onValueChange={value => handleSettingChange('profile_visibility', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="public">Public</SelectItem>
                        <SelectItem value="team">Team Only</SelectItem>
                        <SelectItem value="private">Private</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-muted-foreground">
                      Control who can see your profile information
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label>Data Retention</Label>
                    <Select
                      value={settings.data_retention || '2-years'}
                      onValueChange={value => handleSettingChange('data_retention', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1-year">1 Year</SelectItem>
                        <SelectItem value="2-years">2 Years</SelectItem>
                        <SelectItem value="5-years">5 Years</SelectItem>
                        <SelectItem value="indefinite">Indefinite</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-muted-foreground">
                      How long to keep candidate data after hiring/rejection
                    </p>
                  </div>
                </div>
              </TabsContent>

              {/* Appearance Tab */}
              <TabsContent value="appearance" className="p-6 space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Palette className="h-4 w-4" />
                      Theme
                    </Label>
                    <Select
                      value={settings.theme || 'light'}
                      onValueChange={value => handleSettingChange('theme', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">Light</SelectItem>
                        <SelectItem value="dark">Dark</SelectItem>
                        <SelectItem value="system">System</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Globe className="h-4 w-4" />
                      Language
                    </Label>
                    <Select
                      value={settings.language || 'en'}
                      onValueChange={value => handleSettingChange('language', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="de">German</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Timezone</Label>
                    <Select
                      value={settings.timezone || 'UTC-5'}
                      onValueChange={value => handleSettingChange('timezone', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="UTC-8">Pacific Time (UTC-8)</SelectItem>
                        <SelectItem value="UTC-7">Mountain Time (UTC-7)</SelectItem>
                        <SelectItem value="UTC-6">Central Time (UTC-6)</SelectItem>
                        <SelectItem value="UTC-5">Eastern Time (UTC-5)</SelectItem>
                        <SelectItem value="UTC+0">GMT (UTC+0)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </TabsContent>

              {/* Security Tab */}
              <TabsContent value="security" className="p-6 space-y-6">
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label className="flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        Two-Factor Authentication
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Add an extra layer of security to your account
                      </p>
                    </div>
                    <Switch
                      checked={!!settings.two_factor_enabled}
                      onCheckedChange={checked => handleSettingChange('two_factor_enabled', checked)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Session Timeout</Label>
                    <Select
                      value={settings.session_timeout || '4-hours'}
                      onValueChange={value => handleSettingChange('session_timeout', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1-hour">1 Hour</SelectItem>
                        <SelectItem value="4-hours">4 Hours</SelectItem>
                        <SelectItem value="8-hours">8 Hours</SelectItem>
                        <SelectItem value="24-hours">24 Hours</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-muted-foreground">
                      Automatically sign out after period of inactivity
                    </p>
                  </div>

                  <Separator />

                  <div className="space-y-4">
                    <div>
                      <Label className="flex items-center gap-2 mb-2">
                        <Key className="h-4 w-4" />
                        API Key
                      </Label>
                      <div className="flex gap-2">
                        <Input
                          type={showApiKey ? 'text' : 'password'}
                          value={settings.api_key || ''}
                          readOnly
                          className="flex-1"
                        />
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => setShowApiKey(!showApiKey)}
                          title={showApiKey ? 'Hide Key' : 'Show Key'}
                        >
                          {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={handleCopyKey}
                          title="Copy to Clipboard"
                        >
                          <Clipboard className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={handleRegenerateKey}
                          disabled={regenerating}
                          title="Regenerate Key"
                        >
                          <RefreshCw className={regenerating ? 'animate-spin' : 'h-4 w-4'} />
                        </Button>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        Use this key to access TalentHub API programmatically
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button
            className="bg-gradient-primary hover:shadow-glow transition-all duration-300"
            onClick={handleSave}
            disabled={saving}
            aria-label="Save All Changes"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save All Changes'}
          </Button>
        </div>
      </div>
    </form>
  );
};

export default Settings;