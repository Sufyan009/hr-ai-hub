import React, { useEffect, useState } from 'react';
import {
  Users,
  UserPlus,
  Clock,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Calendar,
  FileText,
  RefreshCw,
  Plus,
  Trash2,
  Briefcase
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<any>(null);
  const [recentActivities, setRecentActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const [metricsRes, activitiesRes] = await Promise.all([
        api.get('/metrics/'),
        api.get('/recent-activities/')
      ]);
      setMetrics(metricsRes.data);
      setRecentActivities(activitiesRes.data);
    } catch {
      setError('Failed to refresh dashboard data.');
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [metricsRes, activitiesRes] = await Promise.all([
          api.get('/metrics/'),
          api.get('/recent-activities/')
        ]);
        setMetrics(metricsRes.data);
        setRecentActivities(activitiesRes.data);
      } catch (err) {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const metricCards = metrics ? [
    {
      title: 'Total Candidates',
      value: metrics.total_candidates ?? '—',
      change: metrics.total_candidates_change ?? '+0%',
      trend: metrics.total_candidates_trend ?? 'up',
      icon: Users,
      color: 'bg-blue-600'
    },
    {
      title: 'Active Positions',
      value: metrics.active_positions ?? '—',
      change: metrics.active_positions_change ?? '+0',
      trend: metrics.active_positions_trend ?? 'up',
      icon: FileText,
      color: 'bg-purple-600'
    },
    {
      title: 'Hired This Month',
      value: metrics.hired_this_month ?? '—',
      change: metrics.hired_this_month_change ?? '+0%',
      trend: metrics.hired_this_month_trend ?? 'up',
      icon: CheckCircle,
      color: 'bg-teal-600'
    },
    {
      title: 'Pending Reviews',
      value: metrics.pending_reviews ?? '—',
      change: metrics.pending_reviews_change ?? '+0%',
      trend: metrics.pending_reviews_trend ?? 'down',
      icon: AlertCircle,
      color: 'bg-orange-600'
    }
  ] : [];

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'new':
        return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100">New</Badge>;
      case 'scheduled':
        return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Scheduled</Badge>;
      case 'hired':
        return <Badge className="bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200">Hired</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Rejected</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100">Unknown</Badge>;
    }
  };

  const activityIcon = (activity: string) => {
    if (!activity) return null;
    if (activity.toLowerCase().includes('added')) return <Plus className="h-5 w-5 text-blue-500" />;
    if (activity.toLowerCase().includes('deleted')) return <Trash2 className="h-5 w-5 text-red-500" />;
    if (activity.toLowerCase().includes('hired')) return <CheckCircle className="h-5 w-5 text-teal-500" />;
    if (activity.toLowerCase().includes('posted')) return <Briefcase className="h-5 w-5 text-purple-500" />;
    return <Clock className="h-5 w-5 text-gray-500 dark:text-gray-400" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full py-10 bg-gray-50 dark:bg-gray-900 rounded-lg">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5 animate-spin text-blue-600" />
          <span className="text-gray-700 dark:text-gray-200">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-10 bg-gray-50 dark:bg-gray-900 rounded-lg">
        <div className="text-red-600 dark:text-red-400 font-medium mb-4 text-lg">{error}</div>
        <Button
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg px-6 py-2"
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Welcome Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold text-gray-800 dark:text-gray-100">
            Welcome back, {user?.first_name || 'User'}!
          </h1>
          <Button
            variant="outline"
            className="flex items-center gap-2 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Here's an overview of your recruitment activities and performance.
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metricCards.map((metric, index) => (
          <Card
            key={index}
            className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white dark:bg-gray-800"
            style={{ animation: `fadeInUp 0.3s ease-out ${index * 100}ms both` }}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {metric.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                    {metric.value}
                  </p>
                  <div className="flex items-center gap-1">
                    <TrendingUp
                      className={`h-4 w-4 ${metric.trend === 'up' ? 'text-teal-500' : 'text-red-500'}`}
                    />
                    <span className={`text-sm font-medium ${metric.trend === 'up' ? 'text-teal-500' : 'text-red-500'}`}>
                      {metric.change}
                    </span>
                  </div>
                </div>
                <div className={`p-3 rounded-full ${metric.color}`}>
                  <metric.icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <Card className="lg:col-span-2 shadow-lg border-0 bg-white dark:bg-gray-800">
          <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
            <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-800 dark:text-gray-100">
              <Clock className="h-5 w-5 text-blue-600" />
              Recent Activities
            </CardTitle>
            <CardDescription className="text-sm text-gray-600 dark:text-gray-400">
              Latest candidate interactions and updates
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-3">
              {recentActivities.map((activity, idx) => (
                <div
                  key={activity.id || idx}
                  className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                >
                  <div className="flex items-center gap-3">
                    {activityIcon(activity.activity)}
                    <div>
                      <span className="font-medium text-gray-800 dark:text-gray-100">
                        {activity.activity || activity.message || 'No details'}
                      </span>
                      <div className="mt-1 flex items-center gap-2">
                        {activity.status && activity.status.trim() !== '' && getStatusBadge(activity.status)}
                        {activity.user && activity.user.role && activity.user.role !== 'Unknown' && (
                          <span className="inline-block px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-xs font-semibold dark:bg-blue-900 dark:text-blue-200 ml-2">
                            {activity.user.role.charAt(0).toUpperCase() + activity.user.role.slice(1)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {activity.timestamp && (new Date(activity.timestamp).toLocaleString())}
                  </span>
                </div>
              ))}
              {recentActivities.length === 0 && (
                <div className="text-center text-gray-500 dark:text-gray-400 py-4">
                  No recent activities.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
          <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
            <CardTitle className="flex items-center gap-2 text-lg font-semibold text-gray-800 dark:text-gray-100">
              <UserPlus className="h-5 w-5 text-blue-600" />
              Quick Actions
            </CardTitle>
            <CardDescription className="text-sm text-gray-600 dark:text-gray-400">
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-3">
            <Button
              className="w-full justify-start gap-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-200"
              size="lg"
              onClick={() => window.location.href = '/candidates/new'}
            >
              <UserPlus className="h-4 w-4" />
              Add New Candidate
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-3 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100"
              size="lg"
              onClick={() => window.location.href = '/candidates'}
            >
              <Calendar className="h-4 w-4" />
              View All Candidates
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-3 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100"
              size="lg"
              onClick={() => window.location.href = '/chat'}
            >
              <FileText className="h-4 w-4" />
              AI Assistant
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-3 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100"
              size="lg"
              onClick={() => window.location.href = '/candidates?stage=screening'}
            >
              <AlertCircle className="h-4 w-4" />
              Review Pending
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;