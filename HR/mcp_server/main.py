from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent
import requests
import os
from typing import List, Optional, Dict
import re
from tools import get_candidate, list_candidates, get_candidate_metrics, format_candidate, format_candidate_list

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:8080"] for more security
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
    match = re.search(r'candidate\s*(\d+)', message.lower())
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
    return bool(re.search(r'analytics|metrics|statistics|summary|report|overview', message.lower()))

# Detect update candidate status queries
UPDATE_STATUS_PATTERNS = [
    r'update (?:the )?stage of candidate (\d+) to ([a-zA-Z ]+)',
    r'update candidate (\d+) stage to ([a-zA-Z ]+)',
    r'set candidate (\d+) stage as ([a-zA-Z ]+)',
    r'change stage of candidate (\d+) to ([a-zA-Z ]+)',
    r'update candidate (\d+) status to ([a-zA-Z ]+)',
    r'set candidate (\d+) status as ([a-zA-Z ]+)',
    r'change status of candidate (\d+) to ([a-zA-Z ]+)',
]
def extract_update_candidate_status(message):
    for pat in UPDATE_STATUS_PATTERNS:
        match = re.search(pat, message.lower())
        if match:
            return match.group(1), match.group(2).strip()
    return None, None

# Detect delete candidate queries
def extract_delete_candidate(message):
    match = re.search(r'delete candidate (\d+)', message.lower())
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

@app.post('/chat')
async def chat_endpoint(body: ChatRequest):
    print("[MCP /chat] Full request body:", body)
    user_message = body.message or ''
    if body.messages:
        for m in reversed(body.messages):
            if m.role == 'user' and m.content:
                user_message = m.content
                break
    if not user_message:
        return {"response": {"success": False, "message": "No message provided."}}
    # Rule-based greeting
    if is_greeting(user_message):
        return {'response': "Hello! How can I help you today?"}
    session_id = body.session_id
    model = body.model
    auth_token = body.authToken
    page = body.page
    # Enhanced system prompt for strict tool use, greetings, and proactive behavior
    prompt = body.prompt or (
        "You are HR Assistant Pro, a friendly, proactive, and highly capable AI HR assistant.\n"
        "- Absolutely never list example topics, bullet points, or suggestions in your greeting or first message. Only greet and offer help, nothing else.\n"
        "- If the user greets you (e.g., says 'hi', 'hello', 'hey'), reply with a warm, simple greeting.\n"
        "- When greeting the user, do NOT list example topics or suggestions (such as candidate evaluation frameworks, interview questions, job description templates, compliance, onboarding, etc.). Only greet and offer help.\n"
        "- If the user asks for candidate details, analytics, or CRUD actions (e.g., 'Show me candidate 123', 'List all candidates', 'Update candidate status'), you MUST use your available tools to fetch or update data.\n"
        "- NEVER make up candidate details or analytics.\n"
        "- If the tool returns no result, say so clearly (e.g., 'No candidate found with that ID.').\n"
        "- If the user asks for analytics or metrics, use your analytics tools.\n"
        "- If the user asks a general HR question, answer conversationally and helpfully.\n"
        "- If a tool fails or returns an error, explain the issue clearly and suggest next steps.\n"
        "- Always be clear, concise, and supportive.\n"
        "- If you need more information to complete a tool call, ask the user for clarification.\n"
        "- Example: If the user says 'Show me candidate 123', call the get_candidate tool with ID 123 and return the result.\n"
        "- Example: If the user says 'List all candidates', call the list_candidates tool and return the list.\n"
        "- Example: If the user says 'hi', reply with 'Hello! How can I help you today?'\n"
        "- If the user asks for something you cannot do, politely explain the limitation."
    )
    print("[MCP /chat] Auth token received:", auth_token)
    # Convert Pydantic Message objects to dicts
    messages = []
    if body.messages:
        for m in body.messages:
            if hasattr(m, 'dict'):
                messages.append(m.dict())
            else:
                messages.append(m)
    else:
        messages = []
    # Hybrid tool-calling logic for non-function-calling models
    if model not in FUNCTION_CALLING_MODELS:
        candidate_id = extract_candidate_id(user_message)
        if candidate_id:
            result = get_candidate(candidate_id, auth_token=auth_token)
            if result:
                return {'response': format_candidate(result)}
            else:
                return {'response': f'No candidate found with ID {candidate_id}.'}
        candidate_name_or_email = extract_candidate_name_or_email(user_message)
        if candidate_name_or_email:
            all_candidates = list_candidates(page=1, auth_token=auth_token)
            filtered = [c for c in all_candidates.get('results', []) if candidate_name_or_email.lower() in (c.get('first_name', '').lower() + ' ' + c.get('last_name', '').lower() + c.get('email', '').lower())]
            if filtered:
                return {'response': format_candidate_list(filtered)}
            else:
                return {'response': f'No candidate found matching "{candidate_name_or_email}".'}
        if is_list_candidates_query(user_message):
            result = list_candidates(page=1, auth_token=auth_token)
            if result:
                return {'response': format_candidate_list(result.get('results', []))}
            else:
                return {'response': 'No candidates found.'}
        if is_analytics_query(user_message):
            result = get_candidate_metrics(auth_token=auth_token)
            if result:
                return {'response': str(result)}
            else:
                return {'response': 'No analytics data found.'}
        update_id, new_status = extract_update_candidate_status(user_message)
        if update_id and new_status:
            # Always update the 'candidate_stage' field for stage/status updates
            from tools import update_candidate
            update_result = update_candidate(update_id, 'candidate_stage', new_status, auth_token=auth_token)
            if update_result.get('success'):
                return {'response': f'Candidate {update_id} stage updated to {new_status}.'}
            else:
                return {'response': update_result.get('message', 'Failed to update candidate stage.')}
        delete_id = extract_delete_candidate(user_message)
        if delete_id:
            from tools import delete_candidate
            delete_result = delete_candidate(delete_id, auth_token=auth_token)
            if delete_result.get('success'):
                return {'response': f'Candidate {delete_id} deleted successfully.'}
            else:
                return {'response': delete_result.get('message', 'Failed to delete candidate.')}
        update_id, field, value = extract_update_candidate_field(user_message)
        if update_id and field and value:
            from tools import update_candidate
            update_result = update_candidate(update_id, field, value, auth_token=auth_token)
            if update_result.get('success'):
                return {'response': f'Candidate {update_id} {field} updated to {value}.'}
            else:
                return {'response': update_result.get('message', f'Failed to update candidate {field}.')}
    # Otherwise, use the LLM agent as before
    response = run_agent(messages, session_id, model, auth_token=auth_token, page=page, prompt=prompt)
    return {'response': response}

@app.get('/models')
def get_models():
    r = requests.get("https://openrouter.ai/api/v1/models")
    # OpenRouter returns models under the 'data' key
    return {'models': r.json().get('data', [])} 