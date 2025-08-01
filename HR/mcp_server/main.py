from fastapi import FastAPI, Request, APIRouter, Depends, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from agent import run_agent
import requests
import os
import time
import re
import json
from typing import List, Optional, Dict
import asyncio
import pandas as pd
import numpy as np
from tools import get_candidate, list_candidates, get_candidate_metrics, format_candidate, format_candidate_list, add_candidate, add_note, list_notes, delete_note, list_job_titles, list_cities, list_sources, list_communication_skills, export_candidates_csv, get_recent_activities, get_overall_metrics, list_job_posts, add_job_post, update_job_post, delete_job_post, get_job_post_title_choices, search_candidates, bulk_update_candidates, bulk_delete_candidates, get_job_post, format_job_post, bulk_add_candidates
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enhanced session management with comprehensive memory
pending_actions = {}
session_timeouts = {}
conversation_memory = {}  # Enhanced memory storage
user_preferences = {}     # Store user preferences
query_patterns = {}       # Track query patterns for learning
running_tasks = {}        # Track running tasks for cancellation
cancellation_requests = {}  # Track cancellation requests

def cleanup_expired_sessions():
    """Clean up expired sessions to prevent memory leaks"""
    current_time = time.time()
    expired_sessions = []
    
    for session_id, timeout in session_timeouts.items():
        if current_time - timeout > 7200:  # 2 hour timeout for better memory
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        if session_id in pending_actions:
            del pending_actions[session_id]
        if session_id in session_timeouts:
            del session_timeouts[session_id]
        if session_id in conversation_memory:
            del conversation_memory[session_id]
        if session_id in user_preferences:
            del user_preferences[session_id]

def update_session_timeout(session_id: str):
    """Update session timeout to keep it active"""
    session_timeouts[session_id] = time.time()

def store_conversation_memory(session_id: str, user_message: str, ai_response: str, context: dict = None):
    """Store comprehensive conversation memory"""
    if session_id not in conversation_memory:
        conversation_memory[session_id] = {
            'messages': [],
            'file_context': [],
            'user_preferences': {},
            'query_patterns': [],
            'last_interaction': None,
            'conversation_summary': '',
            'action_history': []
        }
    
    memory = conversation_memory[session_id]
    memory['messages'].append({
        'user': user_message,
        'ai': ai_response,
        'timestamp': time.time(),
        'context': context or {}
    })
    
    # Keep last 50 messages for context
    if len(memory['messages']) > 50:
        memory['messages'] = memory['messages'][-50:]
    
    memory['last_interaction'] = time.time()
    
    # Update query patterns for learning
    update_query_patterns(session_id, user_message)

def update_query_patterns(session_id: str, user_message: str):
    """Track and learn from user query patterns"""
    if session_id not in query_patterns:
        query_patterns[session_id] = []
    
    # Extract key patterns from user message
    patterns = extract_query_patterns(user_message)
    query_patterns[session_id].extend(patterns)
    
    # Keep last 100 patterns
    if len(query_patterns[session_id]) > 100:
        query_patterns[session_id] = query_patterns[session_id][-100:]

def extract_query_patterns(message: str):
    """Extract meaningful patterns from user messages"""
    import re
    
    patterns = []
    message_lower = message.lower()
    
    # File-related patterns
    if any(word in message_lower for word in ['upload', 'file', 'resume', 'csv', 'excel']):
        patterns.append('file_upload')
    
    # Candidate-related patterns
    if any(word in message_lower for word in ['candidate', 'add', 'create', 'new']):
        patterns.append('candidate_management')
    
    # Search patterns
    if any(word in message_lower for word in ['find', 'search', 'look', 'show']):
        patterns.append('search_query')
    
    # Analytics patterns
    if any(word in message_lower for word in ['analytics', 'metrics', 'report', 'data']):
        patterns.append('analytics_request')
    
    # Update patterns
    if any(word in message_lower for word in ['update', 'change', 'modify', 'edit']):
        patterns.append('update_request')
    
    # Delete patterns
    if any(word in message_lower for word in ['delete', 'remove', 'clear']):
        patterns.append('delete_request')
    
    return patterns

def generate_comprehensive_context(session_id: str, user_message: str) -> dict:
    """Generate comprehensive context for AI responses"""
    context = {
        'session_id': session_id,
        'current_message': user_message,
        'conversation_history': [],
        'file_context': [],
        'user_preferences': {},
        'query_patterns': [],
        'suggestions': [],
        'available_actions': []
    }
    
    # Add conversation history
    if session_id in conversation_memory:
        memory = conversation_memory[session_id]
        context['conversation_history'] = memory['messages'][-10:]  # Last 10 messages
        context['user_preferences'] = memory.get('user_preferences', {})
        context['query_patterns'] = query_patterns.get(session_id, [])
    
    # Add file context
    if session_id in pending_actions and 'uploaded_files' in pending_actions[session_id]:
        context['file_context'] = pending_actions[session_id]['uploaded_files']
    
    # Generate smart suggestions based on context
    context['suggestions'] = generate_smart_suggestions(context)
    context['available_actions'] = get_available_actions(context)
    
    return context

def generate_smart_suggestions(context: dict) -> list:
    """Generate intelligent suggestions based on context"""
    suggestions = []
    
    # File-related suggestions
    if context['file_context']:
        suggestions.extend([
            "💡 Process uploaded files for candidate import",
            "📊 Analyze file data for insights",
            "🔍 Check for duplicate candidates",
            "✅ Add candidates to the system"
        ])
    
    # Pattern-based suggestions
    patterns = context.get('query_patterns', [])
    if 'candidate_management' in patterns:
        suggestions.extend([
            "👥 List all candidates",
            "🔍 Search for specific candidates",
            "📝 Add new candidates",
            "✏️ Update candidate information"
        ])
    
    if 'analytics_request' in patterns:
        suggestions.extend([
            "📊 View hiring metrics",
            "📈 Generate reports",
            "📋 Recent activities",
            "🎯 Performance insights"
        ])
    
    # General suggestions
    suggestions.extend([
        "❓ Ask me anything about HR processes",
        "🛠️ Use available tools and commands",
        "📁 Upload files for processing",
            "📋 Download templates for data import"
    ])
    
    return suggestions

def get_available_actions(context: dict) -> list:
    """Get available actions based on current context"""
    actions = [
        "get_candidate", "add_candidate", "update_candidate", "delete_candidate",
        "list_candidates", "search_candidates", "get_analytics", "export_data",
        "upload_file", "process_file", "download_template", "get_reports"
    ]
    
    # Add file-specific actions
    if context['file_context']:
        actions.extend([
            "import_candidates", "validate_data", "check_duplicates",
            "extract_info", "analyze_file"
        ])
    
    return actions

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    cleanup_expired_sessions()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    pending_actions.clear()
    session_timeouts.clear()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: Optional[str] = ''
    messages: Optional[List[Message]] = None
    model: Optional[str] = None
    authToken: Optional[str] = None
    page: int = 1
    session_id: Optional[str] = None
    prompt: Optional[str] = None

GREETINGS = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"}

def is_greeting(message: str) -> bool:
    return message.strip().lower() in GREETINGS



# List of models that support OpenAI-style function calling
FUNCTION_CALLING_MODELS = {
    # Azure OpenAI
    "azure/gpt-35-turbo",
    "azure/gpt-4",
    "azure/gpt-4-turbo",
    "azure/gpt-4o",
    "azure/gpt-4o-mini",
    # OpenAI
    "openai/gpt-3.5-turbo",
    "openai/gpt-3.5-turbo-0125",
    "openai/gpt-3.5-turbo-1106",
    "openai/gpt-4-turbo",
    "openai/gpt-4-0125-preview",
    "openai/gpt-4-1106-preview",
    "openai/gpt-4o",
    "openai/gpt-4",
    # Qwen
    "qwen/qwen1.5-110b-chat",
    "qwen/qwen1.5-72b-chat",
    "qwen/qwen1.5-32b-chat",
    "qwen/qwen1.5-14b-chat",
    "qwen/qwen1.5-7b-chat",
    # Claude (Anthropic)
    "anthropic/claude-3-opus-20240229",
    "anthropic/claude-3-sonnet-20240229",
    "anthropic/claude-3-haiku-20240307",
    "anthropic/claude-2.1",
    "anthropic/claude-2.0",
    # Mistral (some variants)
    "mistralai/mistral-large-latest",
    "mistralai/mistral-medium",
    "mistralai/mistral-small",
    # Google Gemini (if available)
    "google/gemini-pro",
    # Cohere (if available)
    "cohere/command-r",
    # Add more as OpenRouter adds support
}

def extract_candidate_id(message):
    # Match patterns like 'candidate 78', 'candidate id 78', 'show candidate id 78', etc.
    match = re.search(r'(?:candidate\s*(?:id)?\s*)(\d+)', message.lower())
    if match:
        return match.group(1)
    return None

# Enhanced: extract candidate name or email from message
def extract_candidate_name_or_email(message):
    # Example: 'Show me candidate Jane Smith' or 'Find candidate janesmith@example.com'
    match = re.search(r'candidate(?: named| called)? ([a-zA-Z ]+)', message.lower())
    if match:
        return match.group(1).strip()
    email_match = re.search(r'candidate.*?([\w\.-]+@[\w\.-]+)', message)
    if email_match:
        return email_match.group(1)
    return None

# Detect list candidates queries
def is_list_candidates_query(message):
    return bool(re.search(r'list( all)? candidates|show( me)? candidates|display( all)? candidates|find( all)? candidates', message.lower()))

# Detect analytics/metrics queries
def is_analytics_query(message):
    # Support more variations and synonyms
    return bool(re.search(r'(analytics|metrics|statistics|summary|report|overview|how many|top sources|most common|count|number of)', message.lower()))

# Detect update candidate status queries
UPDATE_STATUS_PATTERNS = [
    r'update (?:the )?stage of candidate (\d+) to ([a-zA-Z ]+)',
    r'update candidate (\d+) stage to ([a-zA-Z ]+)',
    r'set candidate (\d+) stage as ([a-zA-Z ]+)',
    r'change stage of candidate (\d+) to ([a-zA-Z ]+)',
    r'update candidate (\d+) status to ([a-zA-Z ]+)',
    r'set candidate (\d+) status as ([a-zA-Z ]+)',
    r'change status of candidate (\d+) to ([a-zA-Z ]+)',
    r'move candidate (\d+) to ([a-zA-Z ]+)',
    r'promote candidate (\d+) to ([a-zA-Z ]+)',
    r'advance candidate (\d+) to ([a-zA-Z ]+)',
    r'progress candidate (\d+) to ([a-zA-Z ]+)',
]
def extract_update_candidate_status(message):
    for pat in UPDATE_STATUS_PATTERNS:
        match = re.search(pat, message.lower())
        if match:
            return match.group(1), match.group(2).strip()
    # Tool-style: update_candidate 15 status hired or update_candidate 15 stage hired
    match = re.search(r'update_candidate[ _]?(\d+)[ _]?(?:status|stage)[ _]?([a-zA-Z ]+)', message.lower())
    if match:
        return match.group(1), match.group(2).strip()
    return None, None

# Detect delete candidate queries
def extract_delete_candidate(message):
    # Match 'delete candidate 5', 'delete_candidate 5', etc.
    match = re.search(r'delete[ _]?candidate[ _]?(\d+)', message.lower())
    if match:
        return match.group(1)
    return None

# Detect update candidate email/phone queries
def extract_update_candidate_field(message):
    # Example: 'update candidate 12 email to new@email.com'
    match = re.search(r'update candidate (\d+) (email|phone) to ([^ ]+)', message.lower())
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None

def extract_bulk_delete_candidates(message):
    # Match 'delete candidates 5, 6, 7' or 'delete candidates 5 6 7'
    match = re.search(r'delete candidates? ([\d, ]+)', message.lower())
    if match:
        ids = re.findall(r'\d+', match.group(1))
        return ids if ids else None
    return None

def extract_bulk_update_candidates(message):
    # Match 'update all candidates in status Screening to Interview Scheduled'
    match = re.search(r'update all candidates in status ([\w ]+) to ([\w ]+)', message.lower())
    if match:
        from_status = match.group(1).strip()
        to_status = match.group(2).strip()
        return from_status, to_status
    return None, None

router = APIRouter()

DJANGO_API = 'http://localhost:8000/api'

@router.get('/chatsessions/')
def proxy_get_chat_sessions(request: Request):
    token = request.headers.get('Authorization')
    r = requests.get(f'{DJANGO_API}/chatsessions/', headers={'Authorization': token} if token else {})
    return r.json()

@router.post('/chatsessions/')
async def proxy_create_chat_session(request: Request):
    token = request.headers.get('Authorization')
    data = await request.json()
    r = requests.post(f'{DJANGO_API}/chatsessions/', json=data, headers={'Authorization': token} if token else {})
    return r.json()

@router.delete('/chatsessions/{session_id}/')
def proxy_delete_chat_session(session_id: int, request: Request):
    token = request.headers.get('Authorization')
    r = requests.delete(f'{DJANGO_API}/chatsessions/{session_id}/', headers={'Authorization': token} if token else {})
    return r.json()

@router.get('/chatmessages/')
def proxy_get_chat_messages(session: int, request: Request):
    token = request.headers.get('Authorization')
    r = requests.get(f'{DJANGO_API}/chatmessages/?session={session}', headers={'Authorization': token} if token else {})
    return r.json()

@router.post('/chatmessages/')
async def proxy_create_chat_message(request: Request):
    token = request.headers.get('Authorization')
    data = await request.json()
    r = requests.post(f'{DJANGO_API}/chatmessages/', json=data, headers={'Authorization': token} if token else {})
    return r.json()

@router.delete('/chatmessages/{msg_id}/')
def proxy_delete_chat_message(msg_id: int, request: Request):
    token = request.headers.get('Authorization')
    r = requests.delete(f'{DJANGO_API}/chatmessages/{msg_id}/', headers={'Authorization': token} if token else {})
    return r.json()

# In your FastAPI app, include these routes:
# app.include_router(router, prefix="/proxy")

# Helper for analytics formatting

def format_analytics(metrics):
    return (
        f"**Candidate Analytics**\n"
        f"- Total candidates: {metrics.get('total', 'N/A')}\n"
        f"- Hired: {metrics.get('hired', 'N/A')}\n"
        f"- Rejected: {metrics.get('rejected', 'N/A')}\n"
        f"- Hired this month: {metrics.get('hired_this_month', 'N/A')}\n"
        f"- Pending reviews: {metrics.get('pending_reviews', 'N/A')}\n"
        f"- Most common stage: {metrics.get('most_common_stage', 'N/A')}\n"
        f"- Top source: {metrics.get('top_source', 'N/A')}\n"
    )

def generate_suggestions(session_id, context_type="general"):
    """Generate smart suggestions based on session context"""
    if session_id not in pending_actions:
        return ""
    
    context = pending_actions[session_id]
    suggestions = []
    
    if context_type == "candidate" and context.get('last_candidate'):
        suggestions.extend([
            "💡 **Suggested Actions:**",
            "- Show me more about the last candidate",
            "- Add a note to the last candidate",
            "- Update candidate status",
            "- Delete candidate",
            "- View candidate analytics"
        ])
    elif context_type == "job_post" and context.get('last_job_post'):
        suggestions.extend([
            "💡 **Suggested Actions:**",
            "- Show me more about the last job post",
            "- Update job post details",
            "- Delete job post",
            "- View candidates for this position"
        ])
    elif context_type == "bulk_operation":
        suggestions.extend([
            "💡 **Next Steps:**",
            "- Add notes to updated candidates",
            "- View recent activities",
            "- Export candidate data",
            "- Check analytics"
        ])
    else:
        suggestions.extend([
            "💡 **Quick Actions:**",
            "- List all candidates",
            "- Show candidate analytics",
            "- List job posts",
            "- View recent activities",
            "- Export data"
        ])
    
    return "\n".join(suggestions)

def check_candidate_exists(email, auth_token=None):
    """Check if a candidate with the given email already exists"""
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    r = requests.get(f'{DJANGO_API}/candidates/', headers=headers, params={'email': email})
    if r.status_code == 200:
        candidates = r.json().get('results', [])
        return len(candidates) > 0
    return False

@app.post('/chat')
async def chat_endpoint(body: ChatRequest):
    """Enhanced chat endpoint with comprehensive intelligence and memory"""
    try:
        user_message = body.message or ""
        messages = body.messages or []
        model = body.model or "openai/gpt-3.5-turbo"
        auth_token = body.authToken
        session_id = body.session_id or "default"
        
        # Check for cancellation request
        if session_id in cancellation_requests:
            del cancellation_requests[session_id]
            return {
                "success": False,
                "message": "Task was cancelled by user",
                "response": "⏹️ Task cancelled successfully. You can start a new conversation.",
                "cancelled": True
            }
        
        # Mark task as running
        running_tasks[session_id] = {
            "started_at": time.time(),
            "model": model,
            "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message
        }
        
        # Debug: Log the entire request body
        print(f"[DEBUG] Chat endpoint - Full request body: {body}")
        print(f"[DEBUG] Chat endpoint - session_id: {session_id}")
        print(f"[DEBUG] pending_actions keys: {list(pending_actions.keys()) if pending_actions else 'None'}")
        if session_id in pending_actions:
            print(f"[DEBUG] session_data keys: {list(pending_actions[session_id].keys())}")
            if 'uploaded_files' in pending_actions[session_id]:
                print(f"[DEBUG] Found {len(pending_actions[session_id]['uploaded_files'])} uploaded files")
        
        # Get comprehensive file context
        file_context = ""
        if session_id in pending_actions and 'uploaded_files' in pending_actions[session_id]:
            uploaded_files = pending_actions[session_id]['uploaded_files']
            if uploaded_files:
                file_context = "\n\n**UPLOADED FILES CONTEXT:**\n"
                for file_info in uploaded_files:
                    file_context += f"- File: {file_info['original_name']}\n"
                    if 'extracted_data' in file_info and 'candidate_info' in file_info['extracted_data']:
                        candidate_info = file_info['extracted_data']['candidate_info']
                        if candidate_info:
                            file_context += f"  Extracted Info: {candidate_info}\n"
                    if 'extracted_data' in file_info and 'data' in file_info['extracted_data']:
                        file_context += f"  Data Preview: {len(file_info['extracted_data']['data'])} rows available\n"
                    if 'extracted_data' in file_info and 'candidate_fields' in file_info['extracted_data']:
                        fields = file_info['extracted_data']['candidate_fields']
                        if fields:
                            file_context += f"  Identified Fields: {fields}\n"
                    if 'extracted_data' in file_info and 'quality_metrics' in file_info['extracted_data']:
                        metrics = file_info['extracted_data']['quality_metrics']
                        file_context += f"  Quality Score: {metrics.get('data_quality_score', 'N/A')}%\n"
                file_context += "\nYou can reference this file data in your responses and help users process it.\n"
        
        # Generate intelligent system prompt
        system_prompt = generate_dynamic_prompt(session_id, file_context, user_message)
        
        # Prepare messages with enhanced context
        chat_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in messages:
            chat_messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        if user_message:
            chat_messages.append({"role": "user", "content": user_message})
        
        # Check if this is a simple greeting
        is_greeting = any(word in user_message.lower() for word in ['hello', 'hi', 'hey', 'hy', 'good morning', 'good afternoon', 'good evening'])
        is_capability_query = any(word in user_message.lower() for word in ['what can you do', 'capabilities', 'features', 'help', 'assist', 'support', 'ask anything'])
        
        # Quick file detection for common queries
        file_queries = ['add', 'upload', 'candidate', 'data', 'file', 'uploaded']
        is_file_query = any(word in user_message.lower() for word in file_queries)
        
        # Quick name search detection
        name_search_queries = ['find candidate', 'search candidate', 'show candidate', 'get candidate', 'candidate named', 'candidate called']
        is_name_search = any(phrase in user_message.lower() for phrase in name_search_queries)
        
        # Vector search detection for semantic queries
        vector_search_queries = ['candidate with', 'candidates who', 'find candidates with', 'search for candidates', 'candidates that have', 'candidates skilled in']
        is_vector_search = any(phrase in user_message.lower() for phrase in vector_search_queries)
        
        # Handle simple greetings directly without calling the agent
        if is_greeting and not is_capability_query:
            agent_response = "Hello! 👋 How can I help you with HR today?"
        elif is_vector_search:
            # Quick response for vector searches - let the agent handle it efficiently
            agent_response = "🔍 I'll perform a semantic search for candidates matching your criteria. Let me check the database..."
        elif is_name_search:
            # Quick response for name searches - let the agent handle it efficiently
            agent_response = "🔍 I'll search for that candidate for you. Let me check the database..."
        elif is_file_query and session_id in pending_actions and pending_actions[session_id] and 'uploaded_files' in pending_actions[session_id]:
            # Quick response for file-related queries
            files = pending_actions[session_id]['uploaded_files']
            print(f"[DEBUG] Found {len(files)} files in session {session_id}")
            print(f"[DEBUG] File info: {files[0].get('original_name', 'Unknown')}")
            print(f"[DEBUG] Has extracted_data: {'extracted_data' in files[0]}")
            if 'extracted_data' in files[0]:
                print(f"[DEBUG] Has data: {'data' in files[0]['extracted_data']}")
                if 'data' in files[0]['extracted_data']:
                    print(f"[DEBUG] Data count: {len(files[0]['extracted_data']['data'])}")
            if files:
                file_info = files[0]
                
                # Check if user wants to add candidates immediately
                add_queries = ['add these', 'add candidates', 'add data', 'add them', 'proceed', 'add that data', 'add that', 'add the data', 'add to system', 'add into system']
                is_add_request = any(phrase in user_message.lower() for phrase in add_queries)
                
                if is_add_request and 'extracted_data' in file_info and 'data' in file_info['extracted_data']:
                    # Quick add candidates
                    try:
                        candidates_data = file_info['extracted_data']['data']
                        from tools import bulk_add_candidates
                        
                        # Check for cancellation before starting bulk add
                        if session_id in cancellation_requests:
                            del cancellation_requests[session_id]
                            return {
                                "success": False,
                                "message": "Task was cancelled by user",
                                "response": "⏹️ Bulk add operation cancelled.",
                                "cancelled": True
                            }
                        
                        print(f"[BULK ADD] Starting bulk add for {len(candidates_data)} candidates")
                        result = bulk_add_candidates(candidates_data, auth_token)
                        
                        if result.get('success'):
                            added_count = result.get('added_count', 0)
                            skipped_count = result.get('skipped_count', 0)
                            failed_count = result.get('failed_count', 0)
                            
                            agent_response = f"✅ Successfully processed {len(candidates_data)} candidates:\n"
                            agent_response += f"• Added: {added_count}\n"
                            agent_response += f"• Skipped (duplicates): {skipped_count}\n"
                            agent_response += f"• Failed: {failed_count}\n\n"
                            agent_response += "The candidates have been added to your system!"
                        else:
                            agent_response = f"❌ Failed to add candidates: {result.get('message', 'Unknown error')}"
                    except Exception as e:
                        agent_response = f"❌ Error during bulk add: {str(e)}"
                else:
                    # Show file info
                    agent_response = f"I've processed the candidate data from \"{file_info['original_name']}\". "
                    if 'extracted_data' in file_info:
                        extracted_data = file_info['extracted_data']
                        if 'candidate_fields' in extracted_data:
                            fields = extracted_data['candidate_fields']
                            agent_response += f"**Identified Fields:** {fields}\n"
                        if 'quality_metrics' in extracted_data:
                            metrics = extracted_data['quality_metrics']
                            agent_response += f"**Data Quality:** {metrics.get('data_quality_score', 'N/A')}% ({metrics.get('mapped_fields', 'N/A')})\n\n"
                        if 'data' in extracted_data:
                            agent_response += f"**Available Actions:**\n"
                            agent_response += f"• Add these candidates to the system\n"
                            agent_response += f"• Analyze the data for insights\n"
                            agent_response += f"• Check for duplicates\n"
                            agent_response += f"• Export or modify the data\n"
                            agent_response += f"• Map fields to system requirements"
            else:
                print(f"[DEBUG] Session {session_id} not found in pending_actions or no uploaded files")
                print(f"[DEBUG] pending_actions keys: {list(pending_actions.keys()) if pending_actions else 'None'}")
                if session_id in pending_actions:
                    print(f"[DEBUG] Session data keys: {list(pending_actions[session_id].keys())}")
                agent_response = "I don't see any uploaded files in this session. Please upload a file first."
        else:
            # Check for cancellation before calling the agent
            if session_id in cancellation_requests:
                del cancellation_requests[session_id]
                return {
                    "success": False,
                    "message": "Task was cancelled by user",
                    "response": "⏹️ Task cancelled successfully. You can start a new conversation.",
                    "cancelled": True
                }
            
            # Call the AI agent with cancellation support
            agent_response = await run_agent_with_cancellation(chat_messages, model, auth_token, session_id)
        
        # Clean up running task
        if session_id in running_tasks:
            del running_tasks[session_id]
        
        # Store conversation memory
        store_conversation_memory(session_id, user_message, agent_response)
        
        # Update session timeout
        update_session_timeout(session_id)
        
        return {
            "success": True,
            "response": agent_response,
            "session_id": session_id,
            "model": model
        }
        
    except Exception as e:
        # Clean up running task on error
        if session_id in running_tasks:
            del running_tasks[session_id]
        
        print(f"[ERROR] Chat endpoint error: {e}")
        return {
            "success": False,
            "message": f"Error processing chat: {str(e)}",
            "session_id": session_id
        }

async def call_ai_model(messages, model, auth_token):
    """Enhanced AI model calling with better error handling and fallback"""
    try:
        # Use the existing model calling logic but with enhanced context
        if "azure" in model.lower():
            # Azure OpenAI
            headers = {
                "api-key": os.getenv("AZURE_OPENAI_API_KEY"),
                "Content-Type": "application/json"
            }
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '').rstrip('/')
            # Use AZURE_OPENAI_CHAT_DEPLOYMENT for chat, fallback to AZURE_OPENAI_DEPLOYMENT, then default to gpt-4o
            deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT') or os.getenv('AZURE_OPENAI_DEPLOYMENT') or 'gpt-4o'
            
            if not endpoint:
                raise Exception("Azure OpenAI endpoint not configured")
                
            url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2023-05-15"
            
            payload = {
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.7
            }
        else:
            # OpenRouter
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.7
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
            
    except Exception as e:
        # If Azure fails, try OpenRouter as fallback
        if "azure" in model.lower():
            try:
                print(f"Azure OpenAI failed: {str(e)}. Trying OpenRouter fallback...")
                headers = {
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                }
                url = "https://openrouter.ai/api/v1/chat/completions"
                
                payload = {
                    "model": "openai/gpt-4o",  # Use a reliable OpenRouter model
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                    response.raise_for_status()
                    result = response.json()
                    
                    return result["choices"][0]["message"]["content"]
                    
            except Exception as fallback_error:
                error_msg = f"I apologize, but I encountered an error while processing your request.\n\n"
                error_msg += f"🔧 **Azure OpenAI Error:** {str(e)}\n"
                error_msg += f"🔄 **OpenRouter Fallback Error:** {str(fallback_error)}\n\n"
                error_msg += f"💡 **Troubleshooting Tips:**\n"
                error_msg += f"- Check your Azure OpenAI API key and endpoint configuration\n"
                error_msg += f"- Ensure your OpenRouter API key is valid and has billing set up\n"
                error_msg += f"- Verify the chat deployment name is correct (should be 'gpt-4o' not 'text-embedding-ada-002')\n"
                error_msg += f"- Set AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o for chat completions\n"
                error_msg += f"- Set AZURE_OPENAI_DEPLOYMENT=text-embedding-ada-002 for embeddings\n\n"
                error_msg += f"Please check your configuration and try again."
                return error_msg
        
        return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or contact support if the issue persists."

@app.post('/chat/upload')
async def upload_candidates_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    import pandas as pd
    import numpy as np
    from datetime import datetime
    import os
    import uuid
    
    print(f"[DEBUG] Bulk upload - session_id: {session_id}")
    print(f"[DEBUG] File name: {file.filename}")
    
    filename = file.filename.lower()
    if filename.endswith('.csv'):
        df = pd.read_csv(file.file)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(file.file)
    else:
        return {"success": False, "message": "Unsupported file type."}
    
    # Drop index column if present
    if df.columns[0].lower().startswith('unnamed') or df.columns[0] == '':
        df = df.iloc[:, 1:]
    
    # Replace NaN and infinite values with empty string for JSON serialization
    df = df.replace([np.nan, np.inf, -np.inf], '')
    
    # Process the data using the same logic as extract_spreadsheet_content
    # Standardize column names
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
    
    # Enhanced field mapping
    standard_fields = {
        'first_name': ['first_name', 'firstname', 'first name', 'fname', 'given_name'],
        'last_name': ['last_name', 'lastname', 'last name', 'lname', 'family_name'],
        'email': ['email', 'e-mail', 'email_address', 'emailaddress'],
        'phone_number': ['phone_number', 'phone', 'phone number', 'mobile', 'cell', 'telephone'],
        'job_title': ['job_title', 'job title', 'position', 'role', 'title', 'job_position'],
        'candidate_stage': ['candidate_stage', 'stage', 'status', 'application_status', 'hiring_stage'],
        'communication_skills': ['communication_skills', 'communication', 'communication_skill', 'comm_skills'],
        'years_of_experience': ['years_of_experience', 'experience', 'years_experience', 'exp', 'experience_years'],
        'expected_salary': ['expected_salary', 'salary', 'desired_salary', 'target_salary', 'salary_expectation'],
        'current_salary': ['current_salary', 'current_salary_amount', 'present_salary'],
        'city': ['city', 'location', 'address', 'location_city'],
        'source': ['source', 'application_source', 'referral_source', 'how_did_they_find_us'],
        'notes': ['notes', 'comment', 'comments', 'additional_notes', 'description']
    }
    
    # Map columns to standard fields
    mapped_fields = {}
    unmapped_columns = []
    
    for standard_field, possible_names in standard_fields.items():
        found = False
        for col in df.columns:
            if any(name in col.lower() for name in possible_names):
                mapped_fields[standard_field] = col
                found = True
                break
        if not found:
            unmapped_columns.append(standard_field)
    
    # Validate data quality
    validation_results = validate_candidate_data(df, mapped_fields)
    
    # Convert to records
    records = df.to_dict('records')
    
    # Quality metrics
    quality_metrics = {
        'total_rows': len(records),
        'mapped_fields': len(mapped_fields),
        'unmapped_fields': len(unmapped_columns),
        'data_quality_score': validation_results['quality_score'],
        'missing_required_fields': validation_results['missing_required']
    }
    
    # Store file info in session (same as upload_single_file)
    if session_id not in pending_actions:
        pending_actions[session_id] = {}
    
    pending_actions[session_id]['uploaded_files'] = pending_actions[session_id].get('uploaded_files', [])
    pending_actions[session_id]['uploaded_files'].append({
        'original_name': file.filename,
        'saved_name': f"{uuid.uuid4()}_{file.filename}",
        'file_path': f"uploads/{uuid.uuid4()}_{file.filename}",
        'file_size': len(df),
        'upload_time': datetime.now().isoformat(),
        'file_type': os.path.splitext(file.filename)[1],
        'extracted_data': {
            "content": f"Spreadsheet processed successfully with {len(records)} rows",
            "data": records[:10],  # First 10 rows for preview
            "columns": df.columns.tolist(),
            "mapped_fields": mapped_fields,
            "unmapped_columns": unmapped_columns,
            "quality_metrics": quality_metrics,
            "validation_results": validation_results,
            "total_rows": len(records),
            "candidate_fields": mapped_fields
        }
    })
    
    print(f"[DEBUG] Bulk file stored in session {session_id}")
    print(f"[DEBUG] pending_actions keys after bulk upload: {list(pending_actions.keys())}")
    print(f"[DEBUG] session_data keys after bulk upload: {list(pending_actions[session_id].keys())}")
    print(f"[DEBUG] uploaded_files count: {len(pending_actions[session_id]['uploaded_files'])}")
    
    preview = df.head(3).to_dict(orient='records')
    columns = list(df.columns)
    
    return {
        "success": True,
        "preview": preview,
        "columns": columns,
        "total": len(df),
        "extracted_data": {
            "content": f"Spreadsheet processed successfully with {len(records)} rows",
            "data": records[:10],
            "columns": df.columns.tolist(),
            "mapped_fields": mapped_fields,
            "unmapped_columns": unmapped_columns,
            "quality_metrics": quality_metrics,
            "validation_results": validation_results,
            "total_rows": len(records),
            "candidate_fields": mapped_fields
        }
    }

# Strict validation and actual upload should be done in /chat/upload/confirm (not shown here)

@app.post('/chat/upload/confirm')
async def confirm_bulk_upload(
    body: dict = Body(...)
):
    session_id = body.get('session_id')
    candidates = body.get('candidates', [])
    duplicate_mode = body.get('duplicate_mode')
    confirm = body.get('confirm')
    auth_token = body.get('authToken') or body.get('auth_token')
    # Actually add candidates to the backend
    result = bulk_add_candidates(candidates, auth_token=auth_token)
    return {
        "success": result['success'],
        "added": result['added'],
        "failedCount": result['failed'],
        "duplicates": 0,  # You can implement duplicate logic if needed
        "errors": [r for r in result['results'] if not r['success']],
        "message": "Bulk upload processed.",
        "results": result['results']
    }

@app.get('/chat/upload/failed-rows')
def download_failed_rows(session_id: str):
    """Download a CSV of failed rows for a given session_id."""
    import io
    import csv
    failed_rows = pending_actions.get(session_id, {}).get('failed_rows', [])
    if not failed_rows:
        return {"success": False, "message": "No failed rows found for this session."}
    # Get all columns used in failed rows
    all_cols = set()
    for row in failed_rows:
        all_cols.update(row.keys())
    all_cols = list(all_cols)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=all_cols)
    writer.writeheader()
    for row in failed_rows:
        writer.writerow(row)
    output.seek(0)
    return StreamingResponse(output, media_type='text/csv', headers={
        'Content-Disposition': f'attachment; filename="failed_rows_{session_id}.csv"'
    })

@app.post('/chat/upload/file')
async def upload_single_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    auth_token: str = Form(None),
):
    """Upload a single file (resume, document) for processing"""
    import os
    import uuid
    from datetime import datetime
    
    print(f"[DEBUG] File upload - session_id: {session_id}")
    print(f"[DEBUG] File name: {file.filename}")
    
    try:
        # Validate file type
        filename = file.filename.lower()
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.xls']
        file_extension = os.path.splitext(filename)[1]
        
        if file_extension not in allowed_extensions:
            return {
                "success": False, 
                "message": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            }
        
        # Validate file size (10MB limit for better processing)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return {
                "success": False,
                "message": "File size too large. Maximum 10MB allowed."
            }
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Process file content based on type
        extracted_data = await process_file_content(file_path, file_extension, content)
        
        # Store file info in session
        if session_id not in pending_actions:
            pending_actions[session_id] = {}
        
        pending_actions[session_id]['uploaded_files'] = pending_actions[session_id].get('uploaded_files', [])
        pending_actions[session_id]['uploaded_files'].append({
            'original_name': filename,
            'saved_name': unique_filename,
            'file_path': file_path,
            'file_size': file_size,
            'upload_time': datetime.now().isoformat(),
            'file_type': file_extension,
            'extracted_data': extracted_data
        })
        
        print(f"[DEBUG] File stored in session {session_id}")
        print(f"[DEBUG] pending_actions keys after upload: {list(pending_actions.keys())}")
        print(f"[DEBUG] session_data keys after upload: {list(pending_actions[session_id].keys())}")
        print(f"[DEBUG] uploaded_files count: {len(pending_actions[session_id]['uploaded_files'])}")
        
        # Prepare response based on file type and extracted data
        response_data = {
            "success": True,
            "message": f"File '{filename}' uploaded and processed successfully",
            "file_info": {
                "original_name": filename,
                "saved_name": unique_filename,
                "file_size": file_size,
                "file_type": file_extension
            },
            "extracted_data": extracted_data
        }
        
        # Add specific information based on file type
        if file_extension in ['.csv', '.xlsx', '.xls']:
            if 'data' in extracted_data and not 'error' in extracted_data:
                data_count = len(extracted_data['data'])
                quality_score = extracted_data.get('quality_metrics', {}).get('data_quality_score', 0)
                response_data["message"] = f"File '{filename}' uploaded successfully with {data_count} candidate records (Quality Score: {quality_score}%)"
            elif 'error' in extracted_data:
                response_data["success"] = False
                response_data["message"] = f"File uploaded but processing failed: {extracted_data['error']}"
        elif file_extension in ['.pdf', '.doc', '.docx', '.txt']:
            if 'candidate_info' in extracted_data and not 'error' in extracted_data:
                candidate_info = extracted_data['candidate_info']
                if candidate_info:
                    response_data["message"] = f"File '{filename}' uploaded successfully. Extracted candidate information available."
                else:
                    response_data["message"] = f"File '{filename}' uploaded successfully but no candidate information was extracted."
            elif 'error' in extracted_data:
                response_data["success"] = False
                response_data["message"] = f"File uploaded but processing failed: {extracted_data['error']}"
        
        return response_data
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error uploading file: {str(e)}"
        }

async def process_file_content(file_path: str, file_extension: str, content: bytes):
    """Process file content and extract relevant information with improved error handling"""
    try:
        print(f"[DEBUG] Processing file: {file_path} with extension: {file_extension}")
        
        if file_extension == '.pdf':
            return await extract_pdf_content(file_path)
        elif file_extension in ['.doc', '.docx']:
            return await extract_doc_content(file_path)
        elif file_extension == '.txt':
            return extract_text_content(content)
        elif file_extension in ['.csv', '.xlsx', '.xls']:
            return extract_spreadsheet_content(file_path, file_extension)
        else:
            return {"error": f"Unsupported file type: {file_extension}. Supported types: .pdf, .doc, .docx, .txt, .csv, .xlsx, .xls"}
    except Exception as e:
        print(f"[DEBUG] Error processing file {file_path}: {str(e)}")
        return {"error": f"Failed to extract content: {str(e)}"}

async def extract_pdf_content(file_path: str):
    """Extract text content from PDF files with improved error handling"""
    try:
        import PyPDF2
        import io
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            if not text_content.strip():
                return {"error": "No text content found in PDF file"}
            
            # Extract candidate information using regex patterns
            candidate_info = extract_candidate_info_from_text(text_content)
            
            return {
                "content": text_content,
                "pages": len(pdf_reader.pages),
                "candidate_info": candidate_info,
                "text_length": len(text_content)
            }
    except ImportError:
        return {"error": "PyPDF2 not installed. Install with: pip install PyPDF2"}
    except Exception as e:
        return {"error": f"PDF extraction failed: {str(e)}"}

async def extract_doc_content(file_path: str):
    """Extract text content from DOC/DOCX files with improved error handling"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        text_content = ""
        
        for paragraph in doc.paragraphs:
            text_content += paragraph.text + "\n"
        
        if not text_content.strip():
            return {"error": "No text content found in DOC/DOCX file"}
        
        # Extract candidate information
        candidate_info = extract_candidate_info_from_text(text_content)
        
        return {
            "content": text_content,
            "candidate_info": candidate_info,
            "text_length": len(text_content)
        }
    except ImportError:
        return {"error": "python-docx not installed. Install with: pip install python-docx"}
    except Exception as e:
        return {"error": f"DOC extraction failed: {str(e)}"}

def extract_text_content(content: bytes):
    """Extract text content from TXT files with improved error handling"""
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            # If all encodings fail, use utf-8 with errors='ignore'
            text_content = content.decode('utf-8', errors='ignore')
        
        if not text_content.strip():
            return {"error": "No text content found in TXT file"}
        
        candidate_info = extract_candidate_info_from_text(text_content)
        
        return {
            "content": text_content,
            "candidate_info": candidate_info,
            "text_length": len(text_content)
        }
    except Exception as e:
        return {"error": f"Text extraction failed: {str(e)}"}

def extract_spreadsheet_content(file_path: str, file_extension: str):
    """Extract data from CSV/Excel files with enhanced processing and error handling"""
    try:
        import pandas as pd
        import numpy as np
        
        print(f"[DEBUG] Reading spreadsheet: {file_path}")
        
        # Read file based on type
        if file_extension == '.csv':
            # Try different encodings for better compatibility
            df = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    print(f"[DEBUG] Successfully read CSV with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"[DEBUG] Failed to read with encoding {encoding}: {e}")
                    continue
            
            if df is None:
                # If all encodings fail, use default with error handling
                df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
        else:
            # Excel files
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except Exception as e:
                # Try with xlrd engine for older Excel files
                try:
                    df = pd.read_excel(file_path, engine='xlrd')
                except Exception as e2:
                    return {"error": f"Failed to read Excel file: {str(e)} and {str(e2)}"}
        
        if df.empty:
            return {"error": "Spreadsheet is empty or contains no data"}
        
        print(f"[DEBUG] DataFrame shape: {df.shape}")
        print(f"[DEBUG] DataFrame columns: {df.columns.tolist()}")
        
        # Clean the data
        df = df.fillna('')
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        if df.empty:
            return {"error": "No data rows found after cleaning"}
        
        # Standardize column names (lowercase, remove spaces, special chars)
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
        
        print(f"[DEBUG] Cleaned columns: {df.columns.tolist()}")
        
        # Enhanced field mapping with standardized template format
        standard_fields = {
            'first_name': ['first_name', 'firstname', 'first name', 'fname', 'given_name'],
            'last_name': ['last_name', 'lastname', 'last name', 'lname', 'family_name'],
            'email': ['email', 'e-mail', 'email_address', 'emailaddress'],
            'phone_number': ['phone_number', 'phone', 'phone number', 'mobile', 'cell', 'telephone'],
            'job_title': ['job_title', 'job title', 'position', 'role', 'title', 'job_position'],
            'candidate_stage': ['candidate_stage', 'stage', 'status', 'application_status', 'hiring_stage'],
            'communication_skills': ['communication_skills', 'communication', 'communication_skill', 'comm_skills'],
            'years_of_experience': ['years_of_experience', 'experience', 'years_experience', 'exp', 'experience_years'],
            'expected_salary': ['expected_salary', 'salary', 'desired_salary', 'target_salary', 'salary_expectation'],
            'current_salary': ['current_salary', 'current_salary_amount', 'present_salary'],
            'city': ['city', 'location', 'address', 'location_city'],
            'source': ['source', 'application_source', 'referral_source', 'how_did_they_find_us'],
            'notes': ['notes', 'comment', 'comments', 'additional_notes', 'description']
        }
        
        # Map columns to standard fields
        mapped_fields = {}
        unmapped_columns = []
        
        for standard_field, possible_names in standard_fields.items():
            found = False
            for col in df.columns:
                if any(name in col.lower() for name in possible_names):
                    mapped_fields[standard_field] = col
                    found = True
                    break
            if not found:
                unmapped_columns.append(standard_field)
        
        print(f"[DEBUG] Mapped fields: {mapped_fields}")
        print(f"[DEBUG] Unmapped fields: {unmapped_columns}")
        
        # Validate data quality
        validation_results = validate_candidate_data(df, mapped_fields)
        
        # Convert to records for easier processing
        records = df.to_dict('records')
        
        # Add data quality metrics
        quality_metrics = {
            'total_rows': len(records),
            'mapped_fields': len(mapped_fields),
            'unmapped_fields': len(unmapped_columns),
            'data_quality_score': validation_results['quality_score'],
            'missing_required_fields': validation_results['missing_required']
        }
        
        return {
            "content": f"Spreadsheet processed successfully with {len(records)} rows",
            "data": records[:10],  # First 10 rows for preview
            "columns": df.columns.tolist(),
            "mapped_fields": mapped_fields,
            "unmapped_columns": unmapped_columns,
            "quality_metrics": quality_metrics,
            "validation_results": validation_results,
            "total_rows": len(records),
            "candidate_fields": mapped_fields
        }
        
    except Exception as e:
        print(f"[DEBUG] Spreadsheet extraction error: {str(e)}")
        return {"error": f"Spreadsheet extraction failed: {str(e)}"}

def validate_candidate_data(df, mapped_fields):
    """Validate candidate data quality and completeness"""
    validation_results = {
        'quality_score': 0,
        'missing_required': [],
        'data_issues': [],
        'suggestions': []
    }
    
    # Required fields for candidate creation
    required_fields = ['first_name', 'last_name', 'email']
    optional_fields = ['phone_number', 'job_title', 'candidate_stage', 'communication_skills', 
                      'years_of_experience', 'expected_salary', 'current_salary', 'city', 'source', 'notes']
    
    # Check required fields
    missing_required = []
    for field in required_fields:
        if field not in mapped_fields:
            missing_required.append(field)
    
    validation_results['missing_required'] = missing_required
    
    # Calculate quality score
    total_fields = len(required_fields) + len(optional_fields)
    mapped_count = len(mapped_fields)
    quality_score = (mapped_count / total_fields) * 100
    
    # Adjust score based on required fields
    if missing_required:
        quality_score *= 0.5  # Reduce score if required fields are missing
    
    validation_results['quality_score'] = round(quality_score, 1)
    
    # Check for data quality issues
    if 'email' in mapped_fields:
        email_col = mapped_fields['email']
        valid_emails = df[email_col].str.contains(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', na=False)
        invalid_email_count = (~valid_emails).sum()
        if invalid_email_count > 0:
            validation_results['data_issues'].append(f"{invalid_email_count} invalid email addresses")
    
    # Check for duplicate emails
    if 'email' in mapped_fields:
        email_col = mapped_fields['email']
        duplicates = df[email_col].duplicated().sum()
        if duplicates > 0:
            validation_results['data_issues'].append(f"{duplicates} duplicate email addresses")
    
    # Generate suggestions
    if missing_required:
        validation_results['suggestions'].append("Add missing required fields: " + ", ".join(missing_required))
    
    if quality_score < 70:
        validation_results['suggestions'].append("Consider adding more optional fields for better data quality")
    
    if validation_results['data_issues']:
        validation_results['suggestions'].append("Review and fix data quality issues before importing")
    
    return validation_results

def extract_candidate_info_from_text(text: str):
    """Extract candidate information from text using enhanced regex patterns"""
    import re
    
    candidate_info = {}
    
    # Email pattern - more comprehensive
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        candidate_info['email'] = emails[0]
    
    # Phone pattern - multiple formats
    phone_patterns = [
        r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  # Standard US format
        r'(\+?[0-9]{1,3}[-.\s]?)?([0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4})',  # International
        r'Phone[:\s]+([0-9+\-\(\)\s]+)',  # "Phone: 123-456-7890"
        r'Tel[:\s]+([0-9+\-\(\)\s]+)',    # "Tel: 123-456-7890"
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text, re.IGNORECASE)
        if phones:
            if isinstance(phones[0], tuple):
                candidate_info['phone'] = ''.join(phones[0])
            else:
                candidate_info['phone'] = phones[0].strip()
            break
    
    # Name patterns - multiple approaches
    name_patterns = [
        r'([A-Z][a-z]+)\s+([A-Z][a-z]+)',  # Standard name format
        r'Name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "Name: John Doe"
        r'([A-Z][a-z]+)\s+([A-Z][a-z]+)\s*[-–—]',  # Name followed by dash
        r'RESUME[:\s-]+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "RESUME - John Doe"
    ]
    
    for pattern in name_patterns:
        names = re.findall(pattern, text)
        if names:
            if isinstance(names[0], tuple):
                candidate_info['name'] = f"{names[0][0]} {names[0][1]}"
            else:
                candidate_info['name'] = names[0].strip()
            break
    
    # Experience patterns
    exp_patterns = [
        r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
        r'experience[:\s]+(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\s*(?:years?|yrs?)\s*exp',
    ]
    
    for pattern in exp_patterns:
        exp_match = re.search(pattern, text, re.IGNORECASE)
        if exp_match:
            candidate_info['experience'] = exp_match.group(1)
            break
    
    # Skills patterns - more comprehensive
    skills_patterns = [
        r'(?:skills?|technologies?|technologies?):\s*([^.\n]+)',
        r'(?:skills?|technologies?|technologies?)\s*[-–—]\s*([^.\n]+)',
        r'([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*)',  # Capitalized skills list
    ]
    
    for pattern in skills_patterns:
        skills_match = re.search(pattern, text, re.IGNORECASE)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            # Clean up the skills text
            skills_text = re.sub(r'[^\w\s,.-]', '', skills_text)
            candidate_info['skills'] = skills_text
            break
    
    # Job title patterns
    job_title_patterns = [
        r'(?:position|role|title|job)[:\s]+([A-Z][a-z\s]+)',
        r'([A-Z][a-z\s]+(?:Engineer|Manager|Developer|Designer|Analyst|Specialist))',
    ]
    
    for pattern in job_title_patterns:
        job_match = re.search(pattern, text, re.IGNORECASE)
        if job_match:
            candidate_info['job_title'] = job_match.group(1).strip()
            break
    
    # Education patterns
    education_patterns = [
        r'(?:education|degree)[:\s]+([^.\n]+)',
        r'([A-Z][A-Z\s]+(?:University|College|School))',
    ]
    
    for pattern in education_patterns:
        edu_match = re.search(pattern, text, re.IGNORECASE)
        if edu_match:
            candidate_info['education'] = edu_match.group(1).strip()
            break
    
    # Location patterns
    location_patterns = [
        r'(?:location|address|city)[:\s]+([A-Z][a-z\s,]+)',
        r'([A-Z][a-z\s]+(?:City|Town|State))',
    ]
    
    for pattern in location_patterns:
        loc_match = re.search(pattern, text, re.IGNORECASE)
        if loc_match:
            candidate_info['location'] = loc_match.group(1).strip()
            break
    
    print(f"[DEBUG] Extracted candidate info: {candidate_info}")
    return candidate_info

def identify_candidate_fields(columns):
    """Identify which columns correspond to candidate fields"""
    field_mapping = {
        'first_name': ['first_name', 'firstname', 'first name', 'fname'],
        'last_name': ['last_name', 'lastname', 'last name', 'lname'],
        'email': ['email', 'e-mail', 'email_address'],
        'phone': ['phone', 'phone_number', 'phone number', 'mobile', 'cell'],
        'job_title': ['job_title', 'job title', 'position', 'role', 'title'],
        'experience': ['experience', 'years_experience', 'years of experience', 'exp'],
        'skills': ['skills', 'skill', 'technologies', 'technology'],
        'city': ['city', 'location', 'address'],
        'salary': ['salary', 'expected_salary', 'current_salary', 'compensation']
    }
    
    identified_fields = {}
    for field, possible_names in field_mapping.items():
        for col in columns:
            if any(name.lower() in col.lower() for name in possible_names):
                identified_fields[field] = col
                break
    
    return identified_fields

@app.post('/chat/process/file')
async def process_uploaded_file(
    body: dict = Body(...)
):
    """Process an uploaded file to extract candidate information"""
    session_id = body.get('session_id')
    file_name = body.get('file_name')
    auth_token = body.get('auth_token')
    
    try:
        if session_id not in pending_actions or 'uploaded_files' not in pending_actions[session_id]:
            return {
                "success": False,
                "message": "No uploaded files found for this session"
            }
        
        # Find the file
        uploaded_file = None
        for file_info in pending_actions[session_id]['uploaded_files']:
            if file_info['original_name'] == file_name:
                uploaded_file = file_info
                break
        
        if not uploaded_file:
            return {
                "success": False,
                "message": f"File '{file_name}' not found in session"
            }
        
        # For now, return basic file info
        # In a real implementation, you would:
        # 1. Extract text from PDF/DOC files
        # 2. Use AI to parse candidate information
        # 3. Return structured candidate data
        
        return {
            "success": True,
            "message": f"File '{file_name}' processed successfully",
            "file_info": uploaded_file,
            "extracted_data": {
                "candidate_name": "Extracted from file",
                "email": "Extracted from file", 
                "phone": "Extracted from file",
                "experience": "Extracted from file",
                "skills": "Extracted from file"
            },
            "suggestions": [
                "Add this candidate to the system",
                "Extract more details from the resume",
                "Compare with existing candidates"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing file: {str(e)}"
        }

@app.get('/health')
def health_check():
    """Health check endpoint for the MCP server"""
    return {"status": "healthy", "service": "HR Assistant Pro MCP Server"}

@app.get('/config/test')
def test_configuration():
    """Test the configuration and return status"""
    azure_key = os.getenv('AZURE_OPENAI_API_KEY')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_chat_deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT')
    azure_embedding_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'text-embedding-ada-002')
    
    config_status = {
        "azure_openai": {
            "endpoint": azure_endpoint or 'Not set',
            "chat_deployment": azure_chat_deployment or 'Not set (will use gpt-4o)',
            "embedding_deployment": azure_embedding_deployment,
            "api_key": "Set" if azure_key else "Not set"
        },
        "openrouter": {
            "api_key": "Set" if os.getenv('OPENROUTER_API_KEY') else "Not set"
        }
    }
    
    # Test if Azure config is complete (need endpoint, key, and either chat deployment or default will be used)
    azure_ready = all([
        azure_endpoint,
        azure_key
    ])
    
    # Add debugging information
    debug_info = {
        "azure_key_length": len(azure_key) if azure_key else 0,
        "azure_endpoint": azure_endpoint,
        "azure_chat_deployment": azure_chat_deployment,
        "azure_embedding_deployment": azure_embedding_deployment,
        "env_vars": {k: v for k, v in os.environ.items() if "AZURE" in k or "OPENROUTER" in k}
    }
    
    return {
        "success": True,
        "configuration": config_status,
        "azure_ready": azure_ready,
        "openrouter_ready": bool(os.getenv('OPENROUTER_API_KEY')),
        "debug_info": debug_info,
        "recommendation": "Use OpenRouter" if not azure_ready else "Azure OpenAI configured"
    }

@app.get('/models')
def get_models():
    r = requests.get("https://openrouter.ai/api/v1/models")
    # OpenRouter returns models under the 'data' key
    openrouter_models = r.json().get('data', [])
    
    # Add our custom Azure models to the list
    azure_models = [
        {
            "id": "azure/gpt-35-turbo",
            "name": "Azure OpenAI: GPT-3.5 Turbo",
            "description": "Azure OpenAI GPT-3.5 Turbo model",
            "pricing": {"prompt": "0.0015", "completion": "0.002"},
            "context_length": 4096,
            "architecture": {"modality": "text", "tokenizer": "gpt2", "instruct_type": "chat"}
        },
        {
            "id": "azure/gpt-4",
            "name": "Azure OpenAI: GPT-4",
            "description": "Azure OpenAI GPT-4 model",
            "pricing": {"prompt": "0.03", "completion": "0.06"},
            "context_length": 8192,
            "architecture": {"modality": "text", "tokenizer": "gpt2", "instruct_type": "chat"}
        },
        {
            "id": "azure/gpt-4-turbo",
            "name": "Azure OpenAI: GPT-4 Turbo",
            "description": "Azure OpenAI GPT-4 Turbo model",
            "pricing": {"prompt": "0.01", "completion": "0.03"},
            "context_length": 128000,
            "architecture": {"modality": "text", "tokenizer": "gpt2", "instruct_type": "chat"}
        },
        {
            "id": "azure/gpt-4o",
            "name": "Azure OpenAI: GPT-4o",
            "description": "Azure OpenAI GPT-4o model",
            "pricing": {"prompt": "0.005", "completion": "0.015"},
            "context_length": 128000,
            "architecture": {"modality": "text", "tokenizer": "gpt2", "instruct_type": "chat"}
        },
        {
            "id": "azure/gpt-4o-mini",
            "name": "Azure OpenAI: GPT-4o Mini",
            "description": "Azure OpenAI GPT-4o Mini model",
            "pricing": {"prompt": "0.00015", "completion": "0.0006"},
            "context_length": 128000,
            "architecture": {"modality": "text", "tokenizer": "gpt2", "instruct_type": "chat"}
        }
    ]
    
    # Combine OpenRouter models with our Azure models
    all_models = azure_models + openrouter_models
    return {'models': all_models} 

@app.get('/chat/template/candidates')
def download_candidate_template():
    """Serve a standardized candidate upload template CSV file"""
    import io
    import csv
    
    # Create a StringIO object to write the CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Define the standardized column headers
    headers = [
        'first_name',
        'last_name', 
        'email',
        'phone_number',
        'job_title',
        'candidate_stage',
        'communication_skills',
        'years_of_experience',
        'expected_salary',
        'current_salary',
        'city',
        'source',
        'notes'
    ]
    
    # Write the header row
    writer.writerow(headers)
    
    # Write example data rows
    example_rows = [
        ['John', 'Doe', 'john.doe@example.com', '+1-555-123-4567', 'Software Engineer', 'Screening', 'Excellent', '5', '80000', '75000', 'New York', 'LinkedIn', 'Strong Python skills'],
        ['Jane', 'Smith', 'jane.smith@example.com', '+1-555-987-6543', 'Product Manager', 'Interview', 'Good', '3', '90000', '85000', 'San Francisco', 'Company Website', 'Experience with Agile'],
        ['Mike', 'Johnson', 'mike.johnson@example.com', '+1-555-456-7890', 'UX Designer', 'Hired', 'Excellent', '4', '75000', '70000', 'Chicago', 'Referral', 'Portfolio available']
    ]
    
    for row in example_rows:
        writer.writerow(row)
    
    # Reset the pointer to the beginning
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="candidates_template.csv"'}
    )

def generate_dynamic_prompt(session_id: str, file_context: str, user_message: str = "") -> str:
    """Generate highly intelligent and context-aware system prompt"""
    
    # Generate comprehensive context
    context = generate_comprehensive_context(session_id, user_message)
    
    # Check if this is a simple greeting
    is_greeting = any(word in user_message.lower() for word in ['hello', 'hi', 'hey', 'hy', 'good morning', 'good afternoon', 'good evening'])
    is_capability_query = any(word in user_message.lower() for word in ['what can you do', 'capabilities', 'features', 'help', 'assist', 'support', 'ask anything'])
    
    # Use different prompts for greetings vs other queries
    if is_greeting and not is_capability_query:
        # Simple, natural greeting prompt
        base_prompt = f"""You are HR Assistant Pro, a friendly and helpful AI HR assistant.

**CONVERSATION STYLE:**
- Respond naturally and conversationally to greetings
- Be warm and welcoming
- Don't list capabilities unless specifically asked
- Keep responses simple and friendly

**AVAILABLE CONTEXT:**
{file_context}

**CONVERSATION HISTORY:**
{format_conversation_history(context['conversation_history'])}

Respond naturally to greetings without overwhelming the user with information."""
    else:
        # Full intelligent prompt for other queries
        base_prompt = f"""You are HR Assistant Pro, an exceptionally intelligent and proactive AI HR assistant with advanced capabilities.

**CORE INTELLIGENCE:**
🧠 **Advanced Understanding**
- Comprehend complex HR queries and workflows
- Understand context from conversation history
- Learn from user interaction patterns
- Provide personalized responses based on user preferences

🎯 **Comprehensive Capabilities**
- File Processing & Analysis (PDF, DOC, CSV, Excel)
- Candidate Management (CRUD operations, search, analytics)
- Data Validation & Quality Assessment
- Process Automation & Workflow Optimization
- Advanced Analytics & Reporting

**CONVERSATION CONTEXT:**
📝 **Current Session:** {session_id}
💬 **Message History:** {len(context['conversation_history'])} recent messages
📁 **Active Files:** {len(context['file_context'])} uploaded files
🎯 **Query Patterns:** {', '.join(context['query_patterns'][-5:]) if context['query_patterns'] else 'None detected'}

**INTELLIGENT BEHAVIORS:**
🤖 **Proactive Intelligence**
- Anticipate user needs based on conversation patterns
- Offer relevant suggestions before being asked
- Provide step-by-step guidance for complex tasks
- Learn and adapt to user preferences

🎯 **Context Awareness**
- Remember all uploaded files and their content
- Maintain conversation context across messages
- Reference previous actions and decisions
- Build on previous processing results

💡 **Smart Decision Making**
- Analyze data quality and provide recommendations
- Suggest optimal workflows based on context
- Identify potential issues before they occur
- Offer multiple solution approaches

**FILE PROCESSING INTELLIGENCE:**
📄 **Resume Analysis**
- Extract: Name, Email, Phone, Experience, Skills, Education
- Analyze: Skill relevance, experience level, qualifications
- Suggest: Job matches, interview questions, candidate fit
- Validate: Data completeness and quality

📊 **Spreadsheet Intelligence**
- Smart field mapping with multiple naming conventions
- Data quality assessment and validation
- Duplicate detection and handling
- Bulk processing optimization

**QUERY HANDLING CAPABILITIES:**
🔍 **Search & Discovery**
- Natural language candidate search
- Advanced filtering and sorting
- Pattern-based query understanding
- Context-aware search suggestions

📊 **Analytics & Insights**
- Real-time hiring metrics
- Trend analysis and predictions
- Performance benchmarking
- Custom report generation

🛠️ **Process Automation**
- Streamlined candidate workflows
- Automated data validation
- Bulk operation optimization
- Error handling and recovery

**RESPONSE INTELLIGENCE:**
1. **Understand Intent**: Analyze user message for underlying intent
2. **Context Integration**: Use all available context for responses
3. **Proactive Suggestions**: Offer relevant actions and next steps
4. **Error Prevention**: Identify potential issues and suggest solutions
5. **Learning Adaptation**: Adapt responses based on user patterns

**CONVERSATION STYLE:**
- Be exceptionally helpful, professional, and intelligent
- Use clear, concise, and actionable language
- Provide comprehensive explanations when needed
- Ask clarifying questions when necessary
- Confirm actions and provide feedback
- For simple greetings, respond naturally without listing capabilities unless specifically asked

**AVAILABLE CONTEXT:**
{file_context}

**SMART SUGGESTIONS:**
{chr(10).join(f"- {suggestion}" for suggestion in context['suggestions'])}

**AVAILABLE ACTIONS:**
{', '.join(context['available_actions'])}

**CONVERSATION HISTORY:**
{format_conversation_history(context['conversation_history'])}

Always be proactive, intelligent, and maintain comprehensive context throughout the conversation. Use all available information to provide the most helpful and accurate responses."""
    
    return base_prompt

def format_conversation_history(history: list) -> str:
    """Format conversation history for prompt inclusion"""
    if not history:
        return "No previous conversation history."
    
    formatted = []
    for i, msg in enumerate(history[-5:], 1):  # Last 5 messages
        formatted.append(f"{i}. User: {msg['user'][:100]}...")
        formatted.append(f"   AI: {msg['ai'][:100]}...")
    
    return "\n".join(formatted)

def enhance_response_with_context(response: str, session_id: str, user_message: str) -> str:
    """Enhance AI response with intelligent context-aware suggestions and follow-ups"""
    
    enhanced_response = response
    
    # Get comprehensive context
    context = generate_comprehensive_context(session_id, user_message)
    
    # Only add enhancements for specific types of queries, not for simple greetings
    is_greeting = any(word in user_message.lower() for word in ['hello', 'hi', 'hey', 'hy', 'good morning', 'good afternoon', 'good evening'])
    is_capability_query = any(word in user_message.lower() for word in ['what can you do', 'capabilities', 'features', 'help', 'assist', 'support', 'ask anything'])
    
    # Skip enhancements for simple greetings unless specifically asked about capabilities
    if is_greeting and not is_capability_query:
        return enhanced_response
    
    # Add intelligent context-aware suggestions only when relevant
    if session_id in pending_actions:
        session_data = pending_actions[session_id]
        
        # File-related intelligent suggestions
        if 'uploaded_files' in session_data and session_data['uploaded_files']:
            files = session_data['uploaded_files']
            
            # Check if this is a file processing conversation
            if any(keyword in user_message.lower() for keyword in ['upload', 'file', 'resume', 'candidate', 'add', 'process']):
                enhanced_response += "\n\n💡 **Intelligent Next Steps:**"
                
                for file_info in files:
                    if file_info['file_type'] in ['.pdf', '.doc', '.docx', '.txt']:
                        enhanced_response += f"\n- 🎯 Add the candidate from '{file_info['original_name']}' to the system"
                        enhanced_response += f"\n- 🔍 Extract more detailed information from the resume"
                        enhanced_response += f"\n- 🔄 Compare with existing candidates for duplicates"
                        enhanced_response += f"\n- 📊 Analyze candidate qualifications and skills"
                    elif file_info['file_type'] in ['.csv', '.xlsx', '.xls']:
                        enhanced_response += f"\n- 📥 Import all candidates from '{file_info['original_name']}'"
                        enhanced_response += f"\n- ✅ Review and validate the data quality"
                        enhanced_response += f"\n- 🔍 Check for duplicate candidates before importing"
                        enhanced_response += f"\n- 📊 Analyze bulk data for insights and trends"
                
                enhanced_response += "\n\n🎯 **Smart Actions Available:**"
                enhanced_response += "\n- Use 'add_candidate' to add individual candidates"
                enhanced_response += "\n- Use 'bulk_import' for spreadsheet data"
                enhanced_response += "\n- Use 'check_duplicates' to verify data integrity"
                enhanced_response += "\n- Use 'analyze_data' for insights and reporting"
        
        # Pattern-based intelligent suggestions
        patterns = context.get('query_patterns', [])
        if 'candidate_management' in patterns:
            enhanced_response += "\n\n👥 **Candidate Management Actions:**"
            enhanced_response += "\n- 📋 List all candidates with 'list_candidates'"
            enhanced_response += "\n- 🔍 Search for specific candidates with 'search_candidates'"
            enhanced_response += "\n- ➕ Add new candidates with 'add_candidate'"
            enhanced_response += "\n- ✏️ Update candidate information with 'update_candidate'"
            enhanced_response += "\n- 📊 Get candidate analytics with 'get_candidate_metrics'"
        
        if 'analytics_request' in patterns:
            enhanced_response += "\n\n📊 **Analytics & Insights:**"
            enhanced_response += "\n- 📈 View overall hiring metrics with 'get_overall_metrics'"
            enhanced_response += "\n- 📋 Check recent activities with 'get_recent_activities'"
            enhanced_response += "\n- 🎯 Use 'generate_reports' for detailed insights"
            enhanced_response += "\n- 📊 Analyze candidate pipeline with 'analyze_pipeline'"
        
        if 'search_query' in patterns:
            enhanced_response += "\n\n🔍 **Advanced Search Options:**"
            enhanced_response += "\n- 🔎 Search by name, email, or skills"
            enhanced_response += "\n- 🏷️ Filter by status, location, or experience"
            enhanced_response += "\n- 📅 Search by date ranges or time periods"
            enhanced_response += "\n- 🎯 Use natural language search queries"
        
        if 'update_request' in patterns:
            enhanced_response += "\n\n✏️ **Update Operations:**"
            enhanced_response += "\n- 📝 Update candidate status and information"
            enhanced_response += "\n- 🔄 Bulk update multiple candidates"
            enhanced_response += "\n- 📊 Update analytics and metrics"
            enhanced_response += "\n- ⚙️ Update system settings and preferences"
        
        if 'delete_request' in patterns:
            enhanced_response += "\n\n🗑️ **Delete Operations:**"
            enhanced_response += "\n- ❌ Delete individual candidates"
            enhanced_response += "\n- 🗂️ Bulk delete multiple candidates"
            enhanced_response += "\n- 📝 Delete notes and comments"
            enhanced_response += "\n- 🧹 Clean up duplicate or invalid data"
    
    # Only add memory info for non-greeting queries (removed AI Assistant Capabilities section)
    if not is_greeting or is_capability_query:
        # Add memory context if available
        if context['conversation_history']:
            enhanced_response += f"\n\n💭 **Conversation Memory:** {len(context['conversation_history'])} recent interactions tracked"
        
        if context['query_patterns']:
            enhanced_response += f"\n\n🎯 **Learning Patterns:** {len(context['query_patterns'])} query patterns analyzed"
    
    return enhanced_response

def understand_query_intent(user_message: str, context: dict) -> dict:
    """Comprehensive query understanding and intent analysis"""
    import re
    
    message_lower = user_message.lower()
    intent = {
        'primary_action': None,
        'secondary_actions': [],
        'entities': {},
        'confidence': 0.0,
        'suggestions': [],
        'requires_clarification': False
    }
    
    # File upload and processing intents
    if any(word in message_lower for word in ['upload', 'file', 'resume', 'csv', 'excel']):
        intent['primary_action'] = 'file_upload'
        intent['confidence'] = 0.9
        
        # Extract file type mentions
        if any(word in message_lower for word in ['pdf', 'resume', 'cv']):
            intent['entities']['file_type'] = 'resume'
        elif any(word in message_lower for word in ['csv', 'excel', 'spreadsheet']):
            intent['entities']['file_type'] = 'bulk_data'
    
    # Candidate management intents
    elif any(word in message_lower for word in ['add', 'create', 'new candidate']):
        intent['primary_action'] = 'add_candidate'
        intent['confidence'] = 0.85
    elif any(word in message_lower for word in ['find', 'search', 'look for', 'show']):
        intent['primary_action'] = 'search_candidates'
        intent['confidence'] = 0.8
    elif any(word in message_lower for word in ['list', 'show all', 'get all']):
        intent['primary_action'] = 'list_candidates'
        intent['confidence'] = 0.8
    elif any(word in message_lower for word in ['update', 'change', 'modify']):
        intent['primary_action'] = 'update_candidate'
        intent['confidence'] = 0.8
    elif any(word in message_lower for word in ['delete', 'remove']):
        intent['primary_action'] = 'delete_candidate'
        intent['confidence'] = 0.8
    
    # Analytics and reporting intents
    elif any(word in message_lower for word in ['analytics', 'metrics', 'report', 'data', 'insights']):
        intent['primary_action'] = 'get_analytics'
        intent['confidence'] = 0.85
    elif any(word in message_lower for word in ['dashboard', 'overview', 'summary']):
        intent['primary_action'] = 'get_dashboard'
        intent['confidence'] = 0.8
    
    # Template and data management intents
    elif any(word in message_lower for word in ['template', 'download', 'format']):
        intent['primary_action'] = 'download_template'
        intent['confidence'] = 0.9
    elif any(word in message_lower for word in ['import', 'bulk', 'multiple']):
        intent['primary_action'] = 'bulk_import'
        intent['confidence'] = 0.8
    
    # Help and guidance intents
    elif any(word in message_lower for word in ['help', 'how', 'what can', 'guide']):
        intent['primary_action'] = 'provide_help'
        intent['confidence'] = 0.9
    
    # General conversation intents
    else:
        intent['primary_action'] = 'general_conversation'
        intent['confidence'] = 0.6
    
    # Extract entities (names, emails, IDs, etc.)
    intent['entities'].update(extract_entities(user_message))
    
    # Generate context-aware suggestions
    intent['suggestions'] = generate_intent_suggestions(intent, context)
    
    # Check if clarification is needed
    if intent['confidence'] < 0.7:
        intent['requires_clarification'] = True
    
    return intent

def extract_entities(message: str) -> dict:
    """Extract entities from user message"""
    import re
    
    entities = {}
    
    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, message)
    if emails:
        entities['email'] = emails[0]
    
    # Extract candidate IDs
    id_pattern = r'candidate\s+(\d+)'
    id_match = re.search(id_pattern, message, re.IGNORECASE)
    if id_match:
        entities['candidate_id'] = id_match.group(1)
    
    # Extract names
    name_pattern = r'(\b[A-Z][a-z]+\s+[A-Z][a-z]+\b)'
    names = re.findall(name_pattern, message)
    if names:
        entities['name'] = names[0]
    
    # Extract phone numbers
    phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phone_match = re.search(phone_pattern, message)
    if phone_match:
        entities['phone'] = ''.join(phone_match.groups())
    
    # Extract job titles
    job_titles = ['engineer', 'manager', 'developer', 'designer', 'analyst', 'specialist']
    for title in job_titles:
        if title in message.lower():
            entities['job_title'] = title
            break
    
    return entities

def generate_intent_suggestions(intent: dict, context: dict) -> list:
    """Generate intelligent suggestions based on intent and context"""
    suggestions = []
    
    if intent['primary_action'] == 'file_upload':
        suggestions.extend([
            "📁 Upload your file using the file upload button",
            "📋 Download the template first for consistent formatting",
            "🔍 I can help you process and analyze the uploaded data"
        ])
    
    elif intent['primary_action'] == 'add_candidate':
        suggestions.extend([
            "👤 Use 'add_candidate' command with candidate details",
            "📁 Upload a resume file for automatic candidate creation",
            "📋 Use the template for bulk candidate addition"
        ])
    
    elif intent['primary_action'] == 'search_candidates':
        suggestions.extend([
            "🔍 Use 'search_candidates' with name, email, or skills",
            "🏷️ Filter by status, location, or experience level",
            "📅 Search by date ranges or time periods"
        ])
    
    elif intent['primary_action'] == 'get_analytics':
        suggestions.extend([
            "📊 Use 'get_overall_metrics' for hiring analytics",
            "📈 Use 'get_recent_activities' for recent data",
            "🎯 Use 'generate_reports' for detailed insights"
        ])
    
    # Add context-specific suggestions
    if context.get('file_context'):
        suggestions.append("💡 I can help you process the uploaded files")
    
    if context.get('query_patterns'):
        suggestions.append("🎯 I'm learning from your query patterns to provide better assistance")
    
    return suggestions

@app.post('/chat/cancel')
async def cancel_chat_task(session_id: str = None):
    """Cancel a running chat task"""
    try:
        if not session_id:
            return {
                "success": False,
                "message": "Session ID is required",
                "session_id": None
            }
            
        if session_id in running_tasks:
            # Mark the task for cancellation
            cancellation_requests[session_id] = True
            print(f"[CANCEL] Cancellation requested for session {session_id}")
            
            # Clean up the running task
            if session_id in running_tasks:
                del running_tasks[session_id]
            
            return {
                "success": True,
                "message": "Task cancellation requested successfully",
                "session_id": session_id
            }
        else:
            return {
                "success": False,
                "message": "No running task found for this session",
                "session_id": session_id
            }
    except Exception as e:
        print(f"[CANCEL] Error cancelling task: {e}")
        return {
            "success": False,
            "message": f"Error cancelling task: {str(e)}",
            "session_id": session_id
        }

@app.get('/chat/status/{session_id}')
async def get_chat_status(session_id: str):
    """Get the status of a chat task"""
    try:
        is_running = session_id in running_tasks
        is_cancelled = session_id in cancellation_requests
        
        return {
            "success": True,
            "session_id": session_id,
            "is_running": is_running,
            "is_cancelled": is_cancelled,
            "task_info": running_tasks.get(session_id, {})
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting status: {str(e)}",
            "session_id": session_id
        }

async def run_agent_with_cancellation(chat_messages, model, auth_token, session_id):
    """Run the AI agent with cancellation support"""
    try:
        # Check for cancellation before starting
        if session_id in cancellation_requests:
            return "⏹️ Task cancelled by user."
        
        # Convert messages to the format expected by run_agent
        agent_messages = []
        for msg in chat_messages:
            agent_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Run the agent which can use tools to perform actual actions
        agent_response = run_agent(
            messages=agent_messages,
            session_id=session_id,
            model=model,
            auth_token=auth_token,
            page=1,
            prompt=None,
            pending_actions=pending_actions
        )
        
        # Check for cancellation after processing
        if session_id in cancellation_requests:
            return "⏹️ Task cancelled by user."
        
        return agent_response
        
    except Exception as e:
        print(f"[ERROR] run_agent_with_cancellation error: {e}")
        return f"❌ Error during processing: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HR Assistant Pro MCP Server...")
    print("📡 Server will be available at: http://localhost:8001")
    print("🔧 Available endpoints:")
    print("   - POST /chat - Chat with HR Assistant")
    print("   - GET  /models - List available models")
    print("   - GET  /chat/template/candidates - Download candidate upload template")
    print("   - All Django API endpoints via proxy")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 