import gzip
import hashlib
import json
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings
from django.db import models
import logging

logger = logging.getLogger(__name__)

class MessageCompressor:
    """Utility class for compressing and caching chat messages"""
    
    @staticmethod
    def compress_content(content: str) -> bytes:
        """Compress message content using gzip"""
        try:
            return gzip.compress(content.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error compressing content: {e}")
            return content.encode('utf-8')
    
    @staticmethod
    def decompress_content(compressed_content: bytes) -> str:
        """Decompress message content using gzip"""
        try:
            return gzip.decompress(compressed_content).decode('utf-8')
        except Exception as e:
            logger.error(f"Error decompressing content: {e}")
            return compressed_content.decode('utf-8', errors='ignore')
    
    @staticmethod
    def generate_content_hash(content: str) -> str:
        """Generate SHA-256 hash of content for deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def should_compress(content: str, min_size: int = 1000) -> bool:
        """Determine if content should be compressed based on size"""
        return len(content.encode('utf-8')) > min_size

class MessageCache:
    """Cache utility for chat messages and sessions"""
    
    CACHE_PREFIX = "chat_message"
    SESSION_PREFIX = "chat_session"
    USER_SESSIONS_PREFIX = "user_sessions"
    
    @staticmethod
    def get_message_key(message_id: int) -> str:
        """Generate cache key for a message"""
        return f"{MessageCache.CACHE_PREFIX}:{message_id}"
    
    @staticmethod
    def get_session_key(session_id: int) -> str:
        """Generate cache key for a session"""
        return f"{MessageCache.SESSION_PREFIX}:{session_id}"
    
    @staticmethod
    def get_user_sessions_key(user_id: int) -> str:
        """Generate cache key for user sessions"""
        return f"{MessageCache.USER_SESSIONS_PREFIX}:{user_id}"
    
    @staticmethod
    def cache_message(message_data: Dict[str, Any], timeout: int = 3600) -> bool:
        """Cache a message"""
        try:
            key = MessageCache.get_message_key(message_data['id'])
            cache.set(key, message_data, timeout)
            return True
        except Exception as e:
            logger.error(f"Error caching message: {e}")
            return False
    
    @staticmethod
    def get_cached_message(message_id: int) -> Optional[Dict[str, Any]]:
        """Get cached message"""
        try:
            key = MessageCache.get_message_key(message_id)
            return cache.get(key)
        except Exception as e:
            logger.error(f"Error getting cached message: {e}")
            return None
    
    @staticmethod
    def cache_session_messages(session_id: int, messages: list, timeout: int = 1800) -> bool:
        """Cache all messages for a session"""
        try:
            key = f"{MessageCache.SESSION_PREFIX}:messages:{session_id}"
            cache.set(key, messages, timeout)
            return True
        except Exception as e:
            logger.error(f"Error caching session messages: {e}")
            return False
    
    @staticmethod
    def get_cached_session_messages(session_id: int) -> Optional[list]:
        """Get cached messages for a session"""
        try:
            key = f"{MessageCache.SESSION_PREFIX}:messages:{session_id}"
            return cache.get(key)
        except Exception as e:
            logger.error(f"Error getting cached session messages: {e}")
            return None
    
    @staticmethod
    def invalidate_session_cache(session_id: int) -> bool:
        """Invalidate cache for a session"""
        try:
            key = f"{MessageCache.SESSION_PREFIX}:messages:{session_id}"
            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error invalidating session cache: {e}")
            return False

class PerformanceOptimizer:
    """Utility for performance optimizations"""
    
    @staticmethod
    def batch_update_message_counts(session_ids: list) -> None:
        """Batch update message counts for multiple sessions"""
        from .models import ChatSession
        
        for session_id in session_ids:
            try:
                session = ChatSession.objects.get(id=session_id)
                session.update_message_count()
            except ChatSession.DoesNotExist:
                logger.warning(f"Session {session_id} not found for count update")
    
    @staticmethod
    def optimize_message_queries(session_id: int, limit: int = 50) -> list:
        """Optimized message query with caching"""
        from .models import ChatMessage
        
        # Try cache first
        cached_messages = MessageCache.get_cached_session_messages(session_id)
        if cached_messages:
            return cached_messages[:limit]
        
        # Query database with optimization
        messages = ChatMessage.objects.filter(
            session_id=session_id
        ).select_related('session').order_by('timestamp')[:limit]
        
        # Convert to list and cache
        message_list = []
        for msg in messages:
            message_data = {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_compressed': msg.is_compressed,
            }
            message_list.append(message_data)
        
        # Cache the results
        MessageCache.cache_session_messages(session_id, message_list)
        
        return message_list

class AnalyticsHelper:
    """Helper for analytics and metrics"""
    
    @staticmethod
    def get_session_metrics(session_id: int) -> Dict[str, Any]:
        """Get metrics for a chat session"""
        from .models import ChatMessage, ChatSession
        
        try:
            session = ChatSession.objects.get(id=session_id)
            messages = ChatMessage.objects.filter(session=session)
            
            return {
                'total_messages': messages.count(),
                'user_messages': messages.filter(role='user').count(),
                'assistant_messages': messages.filter(role='assistant').count(),
                'system_messages': messages.filter(role='system').count(),
                'avg_message_length': messages.aggregate(
                    avg_length=models.Avg(models.functions.Length('content'))
                )['avg_length'] or 0,
                'session_duration': (session.updated_at - session.created_at).total_seconds(),
                'last_activity': session.updated_at.isoformat(),
            }
        except ChatSession.DoesNotExist:
            return {}
    
    @staticmethod
    def get_user_analytics(user_id: int) -> Dict[str, Any]:
        """Get analytics for a user"""
        from .models import ChatSession, ChatMessage
        
        sessions = ChatSession.objects.filter(user_id=user_id)
        total_messages = ChatMessage.objects.filter(session__user_id=user_id).count()
        
        return {
            'total_sessions': sessions.count(),
            'active_sessions': sessions.filter(is_active=True).count(),
            'total_messages': total_messages,
            'avg_messages_per_session': total_messages / sessions.count() if sessions.count() > 0 else 0,
            'last_session': sessions.order_by('-updated_at').first().updated_at.isoformat() if sessions.exists() else None,
        } 