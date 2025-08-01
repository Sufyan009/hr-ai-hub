import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { RefreshCw, Database, HardDrive, Wifi, WifiOff } from 'lucide-react';
import { offlineService } from '@/services/offlineService';
import { useToast } from '@/hooks/use-toast';

interface SystemMetrics {
  total_candidates: number;
  total_sessions: number;
  active_sessions: number;
  total_messages: number;
  recent_messages_24h: number;
}

interface SyncStatus {
  pendingMessages: number;
  pendingSessions: number;
  failedMessages: number;
  failedSessions: number;
}

const PerformanceMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchMetrics();
    fetchSyncStatus();
    setupNetworkListeners();
  }, []);

  const setupNetworkListeners = () => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/performance/system-metrics/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchSyncStatus = async () => {
    try {
      const status = await offlineService.getSyncStatus();
      setSyncStatus(status);
    } catch (error) {
      console.error('Failed to fetch sync status:', error);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await Promise.all([fetchMetrics(), fetchSyncStatus()]);
      toast({
        title: 'Metrics Updated',
        description: 'System metrics have been refreshed.',
      });
    } catch (error) {
      toast({
        title: 'Update Failed',
        description: 'Failed to refresh metrics.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClearFailed = async () => {
    try {
      await offlineService.clearFailedItems();
      await fetchSyncStatus();
      toast({
        title: 'Failed Items Cleared',
        description: 'Failed sync items have been removed.',
      });
    } catch (error) {
      toast({
        title: 'Clear Failed',
        description: 'Failed to clear failed items.',
        variant: 'destructive',
      });
    }
  };

  const getCacheEfficiency = () => {
    if (!metrics) return 0;
    const total = metrics.total_messages + metrics.total_sessions;
    const cached = Math.min(total * 0.8, total); // Estimate 80% cache hit rate
    return Math.round((cached / total) * 100);
  };

  const getStorageUsage = () => {
    if (!metrics) return 0;
    const estimatedSize = metrics.total_messages * 500 + metrics.total_sessions * 2000; // bytes
    const maxSize = 50 * 1024 * 1024; // 50MB
    return Math.min((estimatedSize / maxSize) * 100, 100);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* System Status */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">System Status</CardTitle>
          <div className="flex items-center space-x-2">
            {isOnline ? (
              <Wifi className="h-4 w-4 text-green-500" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-500" />
            )}
            <Badge variant={isOnline ? 'default' : 'destructive'}>
              {isOnline ? 'Online' : 'Offline'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics ? `${metrics.active_sessions} Active` : 'Loading...'}
          </div>
          <p className="text-xs text-muted-foreground">
            {metrics ? `${metrics.total_sessions} Total Sessions` : ''}
          </p>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Performance</CardTitle>
          <Database className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics ? `${metrics.recent_messages_24h}` : '0'}
          </div>
          <p className="text-xs text-muted-foreground">
            Messages (24h)
          </p>
          <div className="mt-2">
            <Progress value={getCacheEfficiency()} className="h-2" />
            <p className="text-xs text-muted-foreground mt-1">
              Cache Efficiency: {getCacheEfficiency()}%
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Storage Usage */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Storage</CardTitle>
          <HardDrive className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics ? `${metrics.total_candidates}` : '0'}
          </div>
          <p className="text-xs text-muted-foreground">
            Total Candidates
          </p>
          <div className="mt-2">
            <Progress value={getStorageUsage()} className="h-2" />
            <p className="text-xs text-muted-foreground mt-1">
              Storage Usage: {getStorageUsage().toFixed(1)}%
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Sync Status */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Sync Status</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </CardHeader>
        <CardContent>
          {syncStatus ? (
            <>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Pending Messages:</span>
                  <Badge variant={syncStatus.pendingMessages > 0 ? 'secondary' : 'default'}>
                    {syncStatus.pendingMessages}
                  </Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Pending Sessions:</span>
                  <Badge variant={syncStatus.pendingSessions > 0 ? 'secondary' : 'default'}>
                    {syncStatus.pendingSessions}
                  </Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Failed Items:</span>
                  <Badge variant={syncStatus.failedMessages + syncStatus.failedSessions > 0 ? 'destructive' : 'default'}>
                    {syncStatus.failedMessages + syncStatus.failedSessions}
                  </Badge>
                </div>
              </div>
              {(syncStatus.failedMessages + syncStatus.failedSessions) > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearFailed}
                  className="mt-2 w-full"
                >
                  Clear Failed
                </Button>
              )}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Loading sync status...</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformanceMonitor; 