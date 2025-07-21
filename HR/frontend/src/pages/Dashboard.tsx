import React, { useEffect, useState } from 'react';
import {
  Users,
  UserPlus,
  Clock,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Calendar,
  FileText
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<any>(null);
  const [recentActivities, setRecentActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('authToken');
        const [metricsRes, activitiesRes] = await Promise.all([
          fetch('http://localhost:8000/api/metrics/', {
            headers: { 'Authorization': `Token ${token}` }
          }),
          fetch('http://localhost:8000/api/recent-activities/', {
            headers: { 'Authorization': `Token ${token}` }
          })
        ]);
        if (!metricsRes.ok || !activitiesRes.ok) throw new Error('Failed to fetch dashboard data');
        const metricsData = await metricsRes.json();
        const activitiesData = await activitiesRes.json();
        setMetrics(metricsData);
        setRecentActivities(activitiesData);
      } catch (err) {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Map backend metrics to UI cards
  const metricCards = metrics ? [
    {
      title: 'Total Candidates',
      value: metrics.total_candidates ?? '—',
      change: metrics.total_candidates_change ?? '+0%',
      trend: metrics.total_candidates_trend ?? 'up',
      icon: Users,
      color: 'bg-primary'
    },
    {
      title: 'Active Positions',
      value: metrics.active_positions ?? '—',
      change: metrics.active_positions_change ?? '+0',
      trend: metrics.active_positions_trend ?? 'up',
      icon: FileText,
      color: 'bg-secondary'
    },
    {
      title: 'Hired This Month',
      value: metrics.hired_this_month ?? '—',
      change: metrics.hired_this_month_change ?? '+0%',
      trend: metrics.hired_this_month_trend ?? 'up',
      icon: CheckCircle,
      color: 'bg-success'
    },
    {
      title: 'Pending Reviews',
      value: metrics.pending_reviews ?? '—',
      change: metrics.pending_reviews_change ?? '+0%',
      trend: metrics.pending_reviews_trend ?? 'down',
      icon: Clock,
      color: 'bg-warning'
    }
  ] : [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'new':
        return <Badge variant="secondary">New</Badge>;
      case 'scheduled':
        return <Badge className="bg-primary text-primary-foreground">Scheduled</Badge>;
      case 'hired':
        return <Badge className="bg-success text-success-foreground">Hired</Badge>;
      case 'rejected':
        return <Badge variant="destructive">Rejected</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  if (loading) return <div className="text-center py-10">Loading...</div>;
  if (error) return <div className="text-center text-red-500 py-10">{error}</div>;

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold text-foreground">Welcome back, {user?.first_name || 'User'}!</h1>
        <p className="text-muted-foreground">
          Here's an overview of your recruitment activities and performance.
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((metric, index) => (
          <Card key={index} className="relative overflow-hidden bg-gradient-card border-0 shadow-soft hover:shadow-medium transition-all duration-300 animate-scale-in" style={{ animationDelay: `${index * 100}ms` }}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-muted-foreground">
                    {metric.title}
                  </p>
                  <p className="text-2xl font-bold text-foreground">
                    {metric.value}
                  </p>
                  <div className="flex items-center space-x-1">
                    <TrendingUp
                      className={`h-4 w-4 ${metric.trend === 'up' ? 'text-success' : 'text-destructive'}`}
                    />
                    <span className={`text-sm font-medium ${metric.trend === 'up' ? 'text-success' : 'text-destructive'}`}>
                      {metric.change}
                    </span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${metric.color}`}>
                  <metric.icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <Card className="lg:col-span-2 shadow-soft border-0 bg-gradient-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Recent Activities
            </CardTitle>
            <CardDescription>
              Latest candidate interactions and updates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.map((activity, idx) => (
                <div
                  key={activity.id || idx}
                  className="flex items-center justify-between p-4 rounded-lg bg-background/50 hover:bg-background/80 transition-colors duration-200"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-medium text-foreground">
                        {activity.action}
                      </span>
                      {getStatusBadge(activity.status)}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      <span className="font-medium">{activity.candidate}</span> • {activity.position}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="shadow-soft border-0 bg-gradient-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserPlus className="h-5 w-5 text-primary" />
              Quick Actions
            </CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              className="w-full justify-start gap-3 bg-gradient-primary hover:shadow-glow transition-all duration-300"
              size="lg"
              onClick={() => window.location.href = '/candidates/new'}
            >
              <UserPlus className="h-4 w-4" />
              Add New Candidate
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-3 hover:bg-secondary/10 border-border"
              size="lg"
              onClick={() => window.location.href = '/candidates'}
            >
              <Calendar className="h-4 w-4" />
              View All Candidates
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-3 hover:bg-secondary/10 border-border"
              size="lg"
              onClick={() => window.location.href = '/chat'}
            >
              <FileText className="h-4 w-4" />
              AI Assistant
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-3 hover:bg-secondary/10 border-border"
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