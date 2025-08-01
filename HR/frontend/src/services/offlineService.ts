import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface OfflineMessage {
  id: string;
  sessionId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  isOffline: boolean;
  syncStatus: 'pending' | 'synced' | 'failed';
}

interface OfflineSession {
  id: string;
  sessionId: number;
  sessionName: string;
  createdAt: Date;
  lastUpdated: Date;
  isOffline: boolean;
  syncStatus: 'pending' | 'synced' | 'failed';
}

interface HRDatabase extends DBSchema {
  messages: {
    key: string;
    value: OfflineMessage;
    indexes: { 'by-session': number; 'by-sync-status': string };
  };
  sessions: {
    key: string;
    value: OfflineSession;
    indexes: { 'by-sync-status': string };
  };
  candidates: {
    key: string;
    value: any;
    indexes: { 'by-sync-status': string };
  };
}

class OfflineService {
  private db: IDBPDatabase<HRDatabase> | null = null;
  private isOnline = navigator.onLine;
  private syncQueue: Array<() => Promise<void>> = [];

  constructor() {
    this.initDatabase();
    this.setupNetworkListeners();
  }

  private async initDatabase() {
    try {
      this.db = await openDB<HRDatabase>('hr-offline-db', 1, {
        upgrade(db) {
          // Messages store
          const messageStore = db.createObjectStore('messages', { keyPath: 'id' });
          messageStore.createIndex('by-session', 'sessionId');
          messageStore.createIndex('by-sync-status', 'syncStatus');

          // Sessions store
          const sessionStore = db.createObjectStore('sessions', { keyPath: 'id' });
          sessionStore.createIndex('by-sync-status', 'syncStatus');

          // Candidates store
          const candidateStore = db.createObjectStore('candidates', { keyPath: 'id' });
          candidateStore.createIndex('by-sync-status', 'syncStatus');
        },
      });
    } catch (error) {
      console.error('Failed to initialize offline database:', error);
    }
  }

  private setupNetworkListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.syncOfflineData();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  async saveMessageOffline(message: OfflineMessage): Promise<void> {
    if (!this.db) return;

    try {
      await this.db.add('messages', {
        ...message,
        isOffline: true,
        syncStatus: 'pending',
      });
    } catch (error) {
      console.error('Failed to save message offline:', error);
    }
  }

  async saveSessionOffline(session: OfflineSession): Promise<void> {
    if (!this.db) return;

    try {
      await this.db.add('sessions', {
        ...session,
        isOffline: true,
        syncStatus: 'pending',
      });
    } catch (error) {
      console.error('Failed to save session offline:', error);
    }
  }

  async getOfflineMessages(sessionId: number): Promise<OfflineMessage[]> {
    if (!this.db) return [];

    try {
      const messages = await this.db.getAllFromIndex('messages', 'by-session', sessionId);
      return messages.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    } catch (error) {
      console.error('Failed to get offline messages:', error);
      return [];
    }
  }

  async getOfflineSessions(): Promise<OfflineSession[]> {
    if (!this.db) return [];

    try {
      return await this.db.getAll('sessions');
    } catch (error) {
      console.error('Failed to get offline sessions:', error);
      return [];
    }
  }

  async syncOfflineData(): Promise<void> {
    if (!this.isOnline || !this.db) return;

    try {
      // Sync pending messages
      const pendingMessages = await this.db.getAllFromIndex('messages', 'by-sync-status', 'pending');
      for (const message of pendingMessages) {
        await this.syncMessage(message);
      }

      // Sync pending sessions
      const pendingSessions = await this.db.getAllFromIndex('sessions', 'by-sync-status', 'pending');
      for (const session of pendingSessions) {
        await this.syncSession(session);
      }

      console.log('Offline data sync completed');
    } catch (error) {
      console.error('Failed to sync offline data:', error);
    }
  }

  private async syncMessage(message: OfflineMessage): Promise<void> {
    try {
      // Import the API service
      const { createChatMessage } = await import('./chatService');
      
      const response = await createChatMessage({
        session: message.sessionId,
        role: message.role,
        content: message.content,
      });

      if (response) {
        // Mark as synced
        await this.db?.put('messages', {
          ...message,
          syncStatus: 'synced',
          isOffline: false,
        });
      }
    } catch (error) {
      console.error('Failed to sync message:', error);
      // Mark as failed
      await this.db?.put('messages', {
        ...message,
        syncStatus: 'failed',
      });
    }
  }

  private async syncSession(session: OfflineSession): Promise<void> {
    try {
      // Import the API service
      const { createChatSession } = await import('./chatService');
      
      const response = await createChatSession({
        session_name: session.sessionName,
      });

      if (response) {
        // Mark as synced
        await this.db?.put('sessions', {
          ...session,
          syncStatus: 'synced',
          isOffline: false,
        });
      }
    } catch (error) {
      console.error('Failed to sync session:', error);
      // Mark as failed
      await this.db?.put('sessions', {
        ...session,
        syncStatus: 'failed',
      });
    }
  }

  async isNetworkAvailable(): Promise<boolean> {
    try {
      const response = await fetch('/api/health', { method: 'HEAD' });
      return response.ok;
    } catch {
      return false;
    }
  }

  async getSyncStatus(): Promise<{
    pendingMessages: number;
    pendingSessions: number;
    failedMessages: number;
    failedSessions: number;
  }> {
    if (!this.db) {
      return {
        pendingMessages: 0,
        pendingSessions: 0,
        failedMessages: 0,
        failedSessions: 0,
      };
    }

    try {
      const pendingMessages = await this.db.countFromIndex('messages', 'by-sync-status', 'pending');
      const pendingSessions = await this.db.countFromIndex('sessions', 'by-sync-status', 'pending');
      const failedMessages = await this.db.countFromIndex('messages', 'by-sync-status', 'failed');
      const failedSessions = await this.db.countFromIndex('sessions', 'by-sync-status', 'failed');

      return {
        pendingMessages,
        pendingSessions,
        failedMessages,
        failedSessions,
      };
    } catch (error) {
      console.error('Failed to get sync status:', error);
      return {
        pendingMessages: 0,
        pendingSessions: 0,
        failedMessages: 0,
        failedSessions: 0,
      };
    }
  }

  async clearFailedItems(): Promise<void> {
    if (!this.db) return;

    try {
      const failedMessages = await this.db.getAllFromIndex('messages', 'by-sync-status', 'failed');
      const failedSessions = await this.db.getAllFromIndex('sessions', 'by-sync-status', 'failed');

      for (const message of failedMessages) {
        await this.db.delete('messages', message.id);
      }

      for (const session of failedSessions) {
        await this.db.delete('sessions', session.id);
      }
    } catch (error) {
      console.error('Failed to clear failed items:', error);
    }
  }
}

// Create singleton instance
export const offlineService = new OfflineService();

// Export types for use in other files
export type { OfflineMessage, OfflineSession }; 