from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent
import requests
import os
from typing import List, Optional, Dict
import re
from tools import get_candidate, list_candidates, get_candidate_metrics, format_candidate, format_candidate_list, add_candidate, add_note, list_notes, delete_note, list_job_titles, list_cities, list_sources, list_communication_skills, export_candidates_csv, get_recent_activities, get_overall_metrics, list_job_posts, add_job_post, update_job_post, delete_job_post, get_job_post_title_choices, search_candidates, bulk_update_candidates, bulk_delete_candidates, get_job_post, format_job_post

app = FastAPI()

# Session context to track conversation state
session_context = {}
pending_actions = {}

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
    if session_id not in session_context:
        return ""
    
    context = session_context[session_id]
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
    session_id = body.session_id or 'default'  # fallback if session_id is not provided
    model = body.model
    auth_token = body.authToken
    page = body.page
    
    # Initialize session context if not exists
    if session_id not in session_context:
        session_context[session_id] = {
            'last_candidate': None,
            'last_job_post': None,
            'last_action': None
        }
    # Check for pending confirmation
    if session_id in pending_actions:
        action = pending_actions[session_id]  # Don't pop yet
        if user_message.strip().lower() in ['yes', 'y', 'confirm', 'sure']:
            if action['type'] == 'bulk_delete' and len(action['candidate_ids']) > 10:
                # Extra confirmation for large bulk actions
                return {'response': f"⚠️ You are about to delete {len(action['candidate_ids'])} candidates. This action cannot be undone. Please reply 'yes' again to confirm or 'cancel' to abort."}
            if action['type'] == 'bulk_delete':
                from tools import delete_candidate
                results = [delete_candidate(cid, auth_token=auth_token) for cid in action['candidate_ids']]
                success = [r for r in results if r.get('success')]
                fail = [r for r in results if not r.get('success')]
                msg = f"✅ Deleted {len(success)} candidates."
                if fail:
                    msg += f"\n❌ Failed to delete the following IDs: {', '.join(action['candidate_ids'][i] for i, r in enumerate(results) if not r.get('success'))}."
                msg += f"\n\n{generate_suggestions(session_id, 'bulk_operation')}"
                pending_actions.pop(session_id)  # Remove after processing
                return {'response': msg}
            elif action['type'] == 'bulk_update' and len(action['candidate_ids']) > 10:
                return {'response': f"⚠️ You are about to update {len(action['candidate_ids'])} candidates. Please reply 'yes' again to confirm or 'cancel' to abort."}
            elif action['type'] == 'bulk_update':
                from tools import update_candidate
                results = [update_candidate(cid, action['field'], action['value'], auth_token=auth_token) for cid in action['candidate_ids']]
                success = [r for r in results if r.get('success')]
                fail = [r for r in results if not r.get('success')]
                msg = f"✅ Updated {len(success)} candidates to {action['value']}."
                if fail:
                    msg += f"\n❌ Failed to update the following IDs: {', '.join(action['candidate_ids'][i] for i, r in enumerate(results) if not r.get('success'))}."
                msg += f"\n\n{generate_suggestions(session_id, 'bulk_operation')}"
                pending_actions.pop(session_id)  # Remove after processing
                return {'response': msg}
            elif action['type'] == 'delete':
                from tools import delete_candidate
                delete_result = delete_candidate(action['candidate_id'], auth_token=auth_token)
                pending_actions.pop(session_id)  # Remove after processing
                if delete_result.get('success'):
                    return {'response': f"✅ Candidate {action['candidate_id']} deleted successfully!\nWould you like to add a note or notify someone? (Reply 'add note' or 'notify')"}
                else:
                    return {'response': f"❌ {delete_result.get('message', 'Failed to delete candidate.')}"}
            elif action['type'] == 'update':
                from tools import update_candidate
                update_result = update_candidate(action['candidate_id'], action['field'], action['value'], auth_token=auth_token)
                pending_actions.pop(session_id)  # Remove after processing
                if update_result.get('success'):
                    return {'response': f"✅ Candidate {action['candidate_id']} {action['field']} updated to {action['value']}!\nWould you like to add a note or notify someone? (Reply 'add note' or 'notify')"}
                else:
                    return {'response': f"❌ {update_result.get('message', f'Failed to update candidate {action['field']}.')}"}
            elif action['type'] == 'add_candidate':
                # Create the candidate
                from tools import add_candidate
                result = add_candidate(action['data'], auth_token=auth_token)
                pending_actions.pop(session_id)  # Remove after processing
                if result.get('success'):
                    return {'response': f"✅ Candidate {action['data']['first_name']} {action['data'].get('last_name','')} added successfully!"}
                else:
                    error_msg = result.get('message', '')
                    if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                        return {'response': f"❌ A candidate with email '{action['data']['email']}' already exists.\n\n💡 **Suggestions:**\n- View the existing candidate: 'Show me candidate {action['data']['email']}'\n- Update the existing candidate: 'Update candidate {action['data']['email']}'\n- Try adding with a different email"}
                    else:
                        return {'response': f"❌ Failed to add candidate. {error_msg}"}
        elif user_message.strip().lower() in ['cancel', 'no', 'n', 'abort', 'stop']:
            pending_actions.pop(session_id)  # Remove after cancelling
            return {'response': '👍 No worries! The action has been cancelled. Let me know if you need anything else.'}
        elif action['type'] == 'add_candidate' and user_message.strip().lower().startswith('update '):
            # Handle field updates
            update_parts = user_message.strip().split(' ', 2)
            if len(update_parts) >= 3:
                field = update_parts[1].lower()
                value = update_parts[2]
                
                # Map field names to data keys
                field_mapping = {
                    'name': 'first_name',
                    'email': 'email',
                    'phone': 'phone_number',
                    'status': 'candidate_stage',
                    'experience': 'years_of_experience',
                    'salary': 'expected_salary',
                    'current_salary': 'current_salary',
                    'job_title': 'job_title',
                    'city': 'city',
                    'skills': 'communication_skills',
                    'source': 'source'
                }
                
                if field in field_mapping:
                    data_key = field_mapping[field]
                    
                    # Handle special cases
                    if field == 'name':
                        # Split name into first and last
                        name_parts = value.split(' ', 1)
                        action['data']['first_name'] = name_parts[0]
                        action['data']['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                    elif field == 'experience':
                        try:
                            action['data'][data_key] = float(value)
                        except ValueError:
                            return {'response': "❌ Experience must be a number (e.g., 'update experience 5')"}
                    elif field in ['salary', 'current_salary']:
                        try:
                            action['data'][data_key] = float(value)
                        except ValueError:
                            return {'response': f"❌ {field.replace('_', ' ').title()} must be a number (e.g., 'update {field} 150000')"}
                    elif field in ['job_title', 'city', 'skills', 'source']:
                        # Handle foreign key fields
                        if field == 'job_title':
                            items = list_job_titles(auth_token=auth_token)
                            item_key = 'job_titles'
                        elif field == 'city':
                            items = list_cities(auth_token=auth_token)
                            item_key = 'cities'
                        elif field == 'skills':
                            items = list_communication_skills(auth_token=auth_token)
                            item_key = 'communication_skills'
                        elif field == 'source':
                            items = list_sources(auth_token=auth_token)
                            item_key = 'sources'
                        
                        if items.get('success'):
                            found = False
                            for item in items.get(item_key, []):
                                if item.get('name', '').lower() == value.lower():
                                    action['data'][data_key] = item['id']
                                    found = True
                                    break
                            if not found:
                                return {'response': f"❌ {field.replace('_', ' ').title()} '{value}' not found. Please use an existing {field.replace('_', ' ')}."}
                    else:
                        action['data'][data_key] = value
                    
                    # Show updated confirmation
                    display_data = {}
                    display_data['Name'] = f"{action['data'].get('first_name', '')} {action['data'].get('last_name', '')}".strip()
                    display_data['Email'] = action['data'].get('email', '')
                    display_data['Phone'] = action['data'].get('phone_number', '')
                    
                    # Get readable names for foreign keys
                    if action['data'].get('job_title'):
                        job_titles = list_job_titles(auth_token=auth_token)
                        if job_titles.get('success'):
                            for job_title in job_titles.get('job_titles', []):
                                if job_title.get('id') == action['data']['job_title']:
                                    display_data['Job Title'] = job_title.get('name', '')
                                    break
                    
                    if action['data'].get('city'):
                        cities = list_cities(auth_token=auth_token)
                        if cities.get('success'):
                            for city in cities.get('cities', []):
                                if city.get('id') == action['data']['city']:
                                    display_data['City'] = city.get('name', '')
                                    break
                    
                    if action['data'].get('communication_skills'):
                        skills_data = list_communication_skills(auth_token=auth_token)
                        if skills_data.get('success'):
                            for skill in skills_data.get('communication_skills', []):
                                if skill.get('id') == action['data']['communication_skills']:
                                    display_data['Skills'] = skill.get('name', '')
                                    break
                    
                    if action['data'].get('source'):
                        sources = list_sources(auth_token=auth_token)
                        if sources.get('success'):
                            for source in sources.get('sources', []):
                                if source.get('id') == action['data']['source']:
                                    display_data['Source'] = source.get('name', '')
                                    break
                    
                    display_data['Status'] = action['data'].get('candidate_stage', '')
                    display_data['Experience'] = f"{action['data'].get('years_of_experience', '')} years"
                    display_data['Expected Salary'] = f"${action['data'].get('expected_salary', '')}"
                    display_data['Current Salary'] = f"${action['data'].get('current_salary', '')}"
                    
                    confirmation_msg = "**📋 Updated Candidate Details - Please Confirm**\n\n"
                    for key, value in display_data.items():
                        if value:
                            confirmation_msg += f"**{key}:** {value}\n"
                    
                    confirmation_msg += "\n**💡 Options:**\n"
                    confirmation_msg += "- Reply 'yes' to confirm and create the candidate\n"
                    confirmation_msg += "- Reply 'update [field] [value]' to modify another field\n"
                    confirmation_msg += "- Reply 'cancel' to abort\n\n"
                    confirmation_msg += "**Example updates:**\n"
                    confirmation_msg += "- 'update email newemail@example.com'\n"
                    confirmation_msg += "- 'update phone 9876543210'\n"
                    confirmation_msg += "- 'update salary 150000'"
                    
                    return {'response': confirmation_msg}
                else:
                    return {'response': f"❌ Unknown field '{field}'. Available fields: name, email, phone, status, experience, salary, job_title, city, skills, source"}
            else:
                return {'response': "❌ Please specify a field and value. Example: 'update email newemail@example.com'"}
        else:
            return {'response': "Please reply 'yes' to confirm, 'update [field] [value]' to modify, or 'cancel' to abort."}
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
    # Hybrid tool-calling logic for non-function-calling models and Azure models
    if model not in FUNCTION_CALLING_MODELS or (model and model.startswith("azure/")):
        # Bulk delete
        bulk_delete_ids = extract_bulk_delete_candidates(user_message)
        if bulk_delete_ids:
            # Fetch and show all candidates for confirmation
            candidates = [get_candidate(cid, auth_token=auth_token) for cid in bulk_delete_ids]
            found = [c for c in candidates if c and c.get('id')]
            if found:
                pending_actions[session_id] = {'type': 'bulk_delete', 'candidate_ids': bulk_delete_ids}
                details = '\n---\n'.join([format_candidate(c) for c in found])
                return {'response': f"You requested to delete the following candidates:\n\n{details}\n\nAre you sure you want to delete these candidates? Reply 'yes' to confirm or 'cancel' to abort."}
            else:
                return {'response': 'No valid candidates found for deletion.'}
        # Bulk update
        from_status, to_status = extract_bulk_update_candidates(user_message)
        if from_status and to_status:
            # List all candidates, filter by status
            all_candidates = list_candidates(page=1, auth_token=auth_token)
            filtered = [c for c in all_candidates.get('results', []) if str(c.get('candidate_stage', '')).lower() == from_status.lower()]
            if filtered:
                ids = [str(c['id']) for c in filtered]
                pending_actions[session_id] = {'type': 'bulk_update', 'candidate_ids': ids, 'field': 'candidate_stage', 'value': to_status}
                details = '\n---\n'.join([format_candidate(c) for c in filtered])
                return {'response': f"You requested to update the following candidates from status '{from_status}' to '{to_status}':\n\n{details}\n\nAre you sure you want to update these candidates? Reply 'yes' to confirm or 'cancel' to abort."}
            else:
                return {'response': f'No candidates found with status "{from_status}".'}
        # Check for delete candidate command first
        delete_id = extract_delete_candidate(user_message)
        if delete_id:
            candidate = get_candidate(delete_id, auth_token=auth_token)
            if candidate and candidate.get('id') and not candidate.get('success') == False:
                pending_actions[session_id] = {'type': 'delete', 'candidate_id': delete_id}
                return {'response': f"You requested to delete the following candidate.\n\n{format_candidate(candidate)}\n\nAre you sure you want to delete this candidate? Reply 'yes' to confirm."}
            else:
                # List available IDs for user guidance
                all_candidates = list_candidates(page=1, auth_token=auth_token)
                ids = ', '.join(str(c.get('id')) for c in all_candidates.get('results', []) if c.get('id'))
                msg = f'❌ No candidate found with ID {delete_id}.'
                if ids:
                    msg += f' Available candidate IDs: {ids}.'
                else:
                    msg += ' No candidates found in the system.'
                return {'response': msg}
        # Check for update candidate status
        update_id, new_status = extract_update_candidate_status(user_message)
        if update_id and new_status:
            candidate = get_candidate(update_id, auth_token=auth_token)
            if candidate and candidate.get('id') and not candidate.get('success') == False:
                pending_actions[session_id] = {'type': 'update', 'candidate_id': update_id, 'field': 'candidate_stage', 'value': new_status}
                return {'response': f"You requested to update the following candidate's status.\n\n{format_candidate(candidate)}\n\nAre you sure you want to update this candidate's status to '{new_status}'? Reply 'yes' to confirm."}
            else:
                all_candidates = list_candidates(page=1, auth_token=auth_token)
                ids = ', '.join(str(c.get('id')) for c in all_candidates.get('results', []) if c.get('id'))
                msg = f'❌ No candidate found with ID {update_id}.'
                if ids:
                    msg += f' Available candidate IDs: {ids}.'
                else:
                    msg += ' No candidates found in the system.'
                return {'response': msg}
        update_id, field, value = extract_update_candidate_field(user_message)
        if update_id and field and value:
            candidate = get_candidate(update_id, auth_token=auth_token)
            if candidate and candidate.get('id') and not candidate.get('success') == False:
                pending_actions[session_id] = {'type': 'update', 'candidate_id': update_id, 'field': field, 'value': value}
                return {'response': f"You requested to update the following candidate's {field}.\n\n{format_candidate(candidate)}\n\nAre you sure you want to update this candidate's {field} to '{value}'? Reply 'yes' to confirm."}
            else:
                all_candidates = list_candidates(page=1, auth_token=auth_token)
                ids = ', '.join(str(c.get('id')) for c in all_candidates.get('results', []) if c.get('id'))
                msg = f'❌ No candidate found with ID {update_id}.'
                if ids:
                    msg += f' Available candidate IDs: {ids}.'
                else:
                    msg += ' No candidates found in the system.'
                return {'response': msg}
        # Add candidate via natural language
        if re.search(r'add.*candidate', user_message.lower()):
            data = {}
            name_match = re.search(r'named ([a-zA-Z ]+)', user_message)
            if name_match:
                full_name = name_match.group(1).strip().split()
                data['first_name'] = full_name[0]
                if len(full_name) > 1:
                    data['last_name'] = ' '.join(full_name[1:])
            email_match = re.search(r'email ([\w\.-]+@[\w\.-]+)', user_message)
            if email_match:
                data['email'] = email_match.group(1)
            phone_match = re.search(r'phone (\d+)', user_message)
            if phone_match:
                data['phone_number'] = phone_match.group(1)
            city_match = re.search(r'city ([a-zA-Z ]+)', user_message)
            if city_match:
                city_name = city_match.group(1).strip()
                # Get city ID
                cities = list_cities(auth_token=auth_token)
                if cities.get('success'):
                    city_found = None
                    for city in cities.get('cities', []):
                        if city.get('name', '').lower() == city_name.lower():
                            city_found = city
                            break
                    if city_found:
                        data['city'] = city_found['id']
                    else:
                        # Use first available city as default
                        if cities.get('cities'):
                            data['city'] = cities['cities'][0]['id']
            status_match = re.search(r'status ([a-zA-Z ]+)', user_message)
            if status_match:
                data['candidate_stage'] = status_match.group(1).strip()
            skills_match = re.search(r'skills ([a-zA-Z, ]+)', user_message)
            if skills_match:
                skills_names = [s.strip() for s in skills_match.group(1).split(',')]
                # Get communication skills IDs
                skills_data = list_communication_skills(auth_token=auth_token)
                if skills_data.get('success'):
                    # Find the first matching skill (since it's a ForeignKey, we can only use one)
                    for skill_name in skills_names:
                        for skill in skills_data.get('communication_skills', []):
                            if skill.get('name', '').lower() == skill_name.lower():
                                data['communication_skills'] = skill['id']
                                break
                        if 'communication_skills' in data:
                            break
            exp_match = re.search(r'experience (\d+)', user_message)
            if exp_match:
                data['years_of_experience'] = float(exp_match.group(1))
            salary_match = re.search(r'expected salary (\d+)', user_message)
            if salary_match:
                data['expected_salary'] = float(salary_match.group(1))
            job_title_match = re.search(r'for the ([a-zA-Z ]+) position', user_message)
            if job_title_match:
                job_title_name = job_title_match.group(1).strip()
                # Get job title ID
                job_titles = list_job_titles(auth_token=auth_token)
                if job_titles.get('success'):
                    job_title_found = None
                    for job_title in job_titles.get('job_titles', []):
                        if job_title.get('name', '').lower() == job_title_name.lower():
                            job_title_found = job_title
                            break
                    if job_title_found:
                        data['job_title'] = job_title_found['id']
                    else:
                        # Use first available job title as default
                        if job_titles.get('job_titles'):
                            data['job_title'] = job_titles['job_titles'][0]['id']
            
            # Add default values for required fields
            if 'city' not in data:
                cities = list_cities(auth_token=auth_token)
                if cities.get('success') and cities.get('cities'):
                    data['city'] = cities['cities'][0]['id']
            
            if 'job_title' not in data:
                job_titles = list_job_titles(auth_token=auth_token)
                if job_titles.get('success') and job_titles.get('job_titles'):
                    data['job_title'] = job_titles['job_titles'][0]['id']
            
            if 'communication_skills' not in data:
                skills_data = list_communication_skills(auth_token=auth_token)
                if skills_data.get('success') and skills_data.get('communication_skills'):
                    data['communication_skills'] = skills_data['communication_skills'][0]['id']
            
            if 'source' not in data:
                sources = list_sources(auth_token=auth_token)
                if sources.get('success') and sources.get('sources'):
                    data['source'] = sources['sources'][0]['id']
            
            # Add default current salary if not provided
            if 'current_salary' not in data and 'expected_salary' in data:
                data['current_salary'] = data['expected_salary'] * 0.8  # 80% of expected salary
            
            # If we have at least name and email, show confirmation
            if data.get('first_name') and data.get('email'):
                # Check if candidate already exists
                if check_candidate_exists(data['email'], auth_token=auth_token):
                    return {'response': f"❌ A candidate with email '{data['email']}' already exists.\n\n💡 **Suggestions:**\n- View the existing candidate: 'Show me candidate {data['email']}'\n- Update the existing candidate: 'Update candidate {data['email']}'\n- Try adding with a different email"}
                
                # Format the candidate data for display
                display_data = {}
                display_data['Name'] = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                display_data['Email'] = data.get('email', '')
                display_data['Phone'] = data.get('phone_number', '')
                
                # Get readable names for foreign keys
                if data.get('job_title'):
                    job_titles = list_job_titles(auth_token=auth_token)
                    if job_titles.get('success'):
                        for job_title in job_titles.get('job_titles', []):
                            if job_title.get('id') == data['job_title']:
                                display_data['Job Title'] = job_title.get('name', '')
                                break
                
                if data.get('city'):
                    cities = list_cities(auth_token=auth_token)
                    if cities.get('success'):
                        for city in cities.get('cities', []):
                            if city.get('id') == data['city']:
                                display_data['City'] = city.get('name', '')
                                break
                
                if data.get('communication_skills'):
                    skills_data = list_communication_skills(auth_token=auth_token)
                    if skills_data.get('success'):
                        for skill in skills_data.get('communication_skills', []):
                            if skill.get('id') == data['communication_skills']:
                                display_data['Skills'] = skill.get('name', '')
                                break
                
                if data.get('source'):
                    sources = list_sources(auth_token=auth_token)
                    if sources.get('success'):
                        for source in sources.get('sources', []):
                            if source.get('id') == data['source']:
                                display_data['Source'] = source.get('name', '')
                                break
                
                display_data['Status'] = data.get('candidate_stage', '')
                display_data['Experience'] = f"{data.get('years_of_experience', '')} years"
                display_data['Expected Salary'] = f"${data.get('expected_salary', '')}"
                display_data['Current Salary'] = f"${data.get('current_salary', '')}"
                
                # Create confirmation message
                confirmation_msg = "**📋 Candidate Details - Please Confirm**\n\n"
                for key, value in display_data.items():
                    if value:
                        confirmation_msg += f"**{key}:** {value}\n"
                
                confirmation_msg += "\n**💡 Options:**\n"
                confirmation_msg += "- Reply 'yes' to confirm and create the candidate\n"
                confirmation_msg += "- Reply 'update [field] [value]' to modify a field\n"
                confirmation_msg += "- Reply 'cancel' to abort\n\n"
                confirmation_msg += "**Example updates:**\n"
                confirmation_msg += "- 'update email newemail@example.com'\n"
                confirmation_msg += "- 'update phone 9876543210'\n"
                confirmation_msg += "- 'update salary 150000'"
                
                # Store the data in session for later use
                if session_id not in pending_actions:
                    pending_actions[session_id] = {}
                pending_actions[session_id]['type'] = 'add_candidate'
                pending_actions[session_id]['data'] = data
                
                return {'response': confirmation_msg}
            else:
                return {'response': "Please provide at least the candidate's name and email."}
        # Now check for candidate ID lookup
        candidate_id = extract_candidate_id(user_message)
        if candidate_id:
            result = get_candidate(candidate_id, auth_token=auth_token)
            if result and result.get('id') and not result.get('success') == False:
                # Track this candidate in session context
                if session_id not in session_context:
                    session_context[session_id] = {'last_candidate': None, 'last_job_post': None, 'last_action': None}
                session_context[session_id]['last_candidate'] = candidate_id
                response = format_candidate(result)
                response += f"\n\n{generate_suggestions(session_id, 'candidate')}"
                return {'response': response}
            else:
                all_candidates = list_candidates(page=1, auth_token=auth_token)
                ids = ', '.join(str(c.get('id')) for c in all_candidates.get('results', []) if c.get('id'))
                msg = f"❌ No candidate found with ID {candidate_id}."
                if ids:
                    msg += f' Available candidate IDs: {ids}.'
                else:
                    msg += ' No candidates found in the system.'
                msg += " Would you like to list all candidates or try another ID?"
                return {'response': msg}
        candidate_name_or_email = extract_candidate_name_or_email(user_message)
        if candidate_name_or_email:
            all_candidates = list_candidates(page=1, auth_token=auth_token)
            filtered = [c for c in all_candidates.get('results', []) if candidate_name_or_email.lower() in (c.get('first_name', '').lower() + ' ' + c.get('last_name', '').lower() + c.get('email', '').lower())]
            if filtered:
                # Track the first candidate found in session context
                if filtered and session_id not in session_context:
                    session_context[session_id] = {'last_candidate': None, 'last_job_post': None, 'last_action': None}
                if filtered:
                    session_context[session_id]['last_candidate'] = str(filtered[0].get('id'))
                return {'response': format_candidate_list(filtered)}
            else:
                ids = ', '.join(str(c.get('id')) for c in all_candidates.get('results', []) if c.get('id'))
                msg = f'❌ No candidate found matching "{candidate_name_or_email}".'
                if ids:
                    msg += f' Available candidate IDs: {ids}.'
                else:
                    msg += ' No candidates found in the system.'
                msg += " You can say 'list all candidates' to see available candidates."
                return {'response': msg}
        if is_list_candidates_query(user_message):
            result = list_candidates(page=1, auth_token=auth_token)
            if result and result.get('results'):
                return {'response': format_candidate_list(result.get('results', []))}
            else:
                return {'response': 'No candidates found. You can add a new candidate or try again later.'}
        # Analytics queries
        if is_analytics_query(user_message):
            metrics = get_candidate_metrics(auth_token=auth_token)
            if not metrics or metrics.get('success') == False:
                return {'response': f"No analytics data found. Reason: {metrics.get('message', 'Unknown error.')}"}
            # Example: "How many candidates were hired this month?"
            if re.search(r'hired this month', user_message.lower()):
                hired = metrics.get('hired_this_month', 'N/A')
                return {'response': f"📊 Candidates hired this month: **{hired}**\nWould you like to see more analytics or details for a specific candidate?"}
            # Example: "Show me the top sources for successful candidates."
            if re.search(r'top sources|most common source|top source', user_message.lower()):
                top_source = metrics.get('top_source', 'N/A')
                return {'response': f"📊 Top source for successful candidates: **{top_source}**\nWould you like to see more analytics or details for a specific candidate?"}
            # Fallback: show all metrics
            return {'response': format_analytics(metrics) + "\nWould you like to see more analytics or details for a specific candidate?"}
        
        # Follow-up commands for last candidate
        if re.search(r'(show|tell|get) (me )?(more|details|info) (about )?(the )?(last|previous) candidate', user_message.lower()):
            if session_id in session_context and session_context[session_id].get('last_candidate'):
                candidate_id = session_context[session_id]['last_candidate']
                result = get_candidate(candidate_id, auth_token=auth_token)
                if result and result.get('id'):
                    response = format_candidate(result)
                    response += "\n\n💡 **Suggested Actions:**\n- Update candidate details\n- Add a note\n- Schedule interview\n- Delete candidate"
                    return {'response': response}
                else:
                    return {'response': "Sorry, the last candidate is no longer available."}
            else:
                return {'response': "No candidate has been shown yet. Try searching for a specific candidate first."}
        
        # Follow-up commands for last job post
        if re.search(r'(show|tell|get) (me )?(more|details|info) (about )?(the )?(last|previous) job post', user_message.lower()):
            if session_id in session_context and session_context[session_id].get('last_job_post'):
                job_post_id = session_context[session_id]['last_job_post']
                result = get_job_post(job_post_id, auth_token=auth_token)
                if result and result.get('id'):
                    response = format_job_post(result)
                    response += "\n\n💡 **Suggested Actions:**\n- Update job post details\n- Delete job post\n- View candidates for this position"
                    return {'response': response}
                else:
                    return {'response': "Sorry, the last job post is no longer available."}
            else:
                return {'response': "No job post has been shown yet. Try listing job posts first."}
        
        # Add note to last candidate
        if re.search(r'add (a )?note (to|for) (the )?(last|previous) candidate', user_message.lower()):
            if session_id in session_context and session_context[session_id].get('last_candidate'):
                candidate_id = session_context[session_id]['last_candidate']
                # Extract note content from message
                note_match = re.search(r'add (a )?note (to|for) (the )?(last|previous) candidate[:\s]+(.+)', user_message, re.IGNORECASE)
                if note_match:
                    note_content = note_match.group(4).strip()
                    result = add_note(candidate_id, note_content, auth_token=auth_token)
                    if result.get('success'):
                        return {'response': f"✅ Note added to candidate {candidate_id}: {note_content}"}
                    else:
                        return {'response': f"❌ Failed to add note: {result.get('message', '')}"}
                else:
                    return {'response': "Please provide the note content. Example: 'Add note to last candidate: Excellent communication skills'"}
            else:
                return {'response': "No candidate has been shown yet. Try searching for a specific candidate first."}
        # Job post CRUD and listing
        if re.search(r'(list|show|display) job posts?', user_message.lower()):
            result = list_job_posts(auth_token=auth_token)
            if result.get('success') and result.get('job_posts'):
                posts = result['job_posts']
                if not posts:
                    return {'response': 'No job posts found.'}
                # Track the first job post in session context
                if posts and session_id not in session_context:
                    session_context[session_id] = {'last_candidate': None, 'last_job_post': None, 'last_action': None}
                if posts:
                    session_context[session_id]['last_job_post'] = str(posts[0].get('id'))
                md = '| ID | Title | Status | Department | Location | Created At |\n|---|---|---|---|---|---|\n'
                for p in posts:
                    md += f"| {p.get('id','')} | {p.get('title','')} | {p.get('status','')} | {p.get('department','')} | {p.get('location','')} | {p.get('created_at','')} |\n"
                md += f"\n\n{generate_suggestions(session_id, 'job_post')}"
                return {'response': md}
            else:
                return {'response': f"Failed to fetch job posts. {result.get('message','')}"}
        if re.search(r'(add|create) job post', user_message.lower()):
            # Example: "Add job post for Data Scientist in Engineering"
            # For demo, require user to provide all fields in a follow-up
            return {'response': "Please provide job post details as a JSON object (e.g., {\"title\": \"Data Scientist\", \"department\": \"Engineering\", ...})."}
        if user_message.strip().startswith('{') and user_message.strip().endswith('}') and 'title' in user_message:
            # Try to parse as job post creation
            import json
            try:
                data = json.loads(user_message)
                result = add_job_post(data, auth_token=auth_token)
                if result.get('success'):
                    return {'response': f"✅ Job post added: {result['job_post'].get('title','')} (ID: {result['job_post'].get('id','')})"}
                else:
                    return {'response': f"❌ Failed to add job post. {result.get('message','')}"}
            except Exception as e:
                return {'response': f"Invalid job post data. Please provide a valid JSON object. Error: {e}"}
        if re.search(r'(update|edit) job post (\d+)', user_message.lower()):
            m = re.search(r'(update|edit) job post (\d+)', user_message.lower())
            job_post_id = m.group(2)
            return {'response': f"Please provide updated job post fields as a JSON object for job post ID {job_post_id}."}
        if re.search(r'(delete|remove) job post (\d+)', user_message.lower()):
            m = re.search(r'(delete|remove) job post (\d+)', user_message.lower())
            job_post_id = m.group(2)
            result = delete_job_post(job_post_id, auth_token=auth_token)
            if result.get('success'):
                return {'response': f"✅ Job post {job_post_id} deleted successfully."}
            else:
                return {'response': f"❌ Failed to delete job post {job_post_id}. {result.get('message','')}"}
        if re.search(r'job post title choices', user_message.lower()):
            result = get_job_post_title_choices(auth_token=auth_token)
            if result.get('success'):
                choices = result['choices']
                return {'response': f"Available job post titles: {', '.join(str(c) for c in choices)}"}
            else:
                return {'response': f"Failed to fetch job post title choices. {result.get('message','')}"}
        # Analytics: overall and candidate
        if re.search(r'(overall|company|organization) (analytics|metrics|statistics|summary|report|overview)', user_message.lower()):
            result = get_overall_metrics(auth_token=auth_token)
            if result.get('success'):
                metrics = result['metrics']
                md = '\n'.join([f"- {k.replace('_',' ').capitalize()}: {v}" for k,v in metrics.items()])
                return {'response': f"**Overall HR Analytics**\n{md}"}
            else:
                return {'response': f"Failed to fetch overall analytics. {result.get('message','')}"}
        if re.search(r'(candidate|talent) (analytics|metrics|statistics|summary|report|overview)', user_message.lower()):
            result = get_candidate_metrics(auth_token=auth_token)
            if result.get('success'):
                metrics = result['metrics']
                md = '\n'.join([f"- {k.replace('_',' ').capitalize()}: {v}" for k,v in metrics.items()])
                return {'response': f"**Candidate Analytics**\n{md}"}
            else:
                return {'response': f"Failed to fetch candidate analytics. {result.get('message','')}"}
        # Advanced search/filtering for candidates
        if re.search(r'(candidates?|talent|applicants?) (in|from) [a-zA-Z ]+', user_message.lower()) or re.search(r'(with|having) [a-zA-Z ]+', user_message.lower()) or re.search(r'(more than|less than|above|below|over|under) [0-9]+ (years|year|yr|yrs|experience|salary)', user_message.lower()):
            # Parse filters from message (simple demo: city, skills, years_of_experience, expected_salary)
            filters = {}
            city_match = re.search(r'(?:in|from) ([a-zA-Z ]+)', user_message.lower())
            if city_match:
                filters['city__name'] = city_match.group(1).strip()
            skill_match = re.search(r'(?:with|having) ([a-zA-Z ]+)', user_message.lower())
            if skill_match:
                filters['communication_skills__name'] = skill_match.group(1).strip()
            exp_match = re.search(r'(more than|over|above) (\d+(?:\.\d+)?) (years|year|yr|yrs|experience)', user_message.lower())
            if exp_match:
                filters['years_of_experience__gt'] = exp_match.group(2)
            exp_match2 = re.search(r'(less than|under|below) (\d+(?:\.\d+)?) (years|year|yr|yrs|experience)', user_message.lower())
            if exp_match2:
                filters['years_of_experience__lt'] = exp_match2.group(2)
            salary_match = re.search(r'(more than|over|above) (\d+(?:\.\d+)?) (salary|expected salary)', user_message.lower())
            if salary_match:
                filters['expected_salary__gt'] = salary_match.group(2)
            salary_match2 = re.search(r'(less than|under|below) (\d+(?:\.\d+)?) (salary|expected salary)', user_message.lower())
            if salary_match2:
                filters['expected_salary__lt'] = salary_match2.group(2)
            result = search_candidates(filters, auth_token=auth_token)
            if result.get('success') and result.get('candidates'):
                return {'response': format_candidate_list(result['candidates'])}
            else:
                return {'response': f"No candidates found matching your criteria. {result.get('message','')}"}
        # Bulk delete candidates
        if re.search(r'delete candidates? ([\d, ]+)', user_message.lower()):
            ids = re.findall(r'\d+', user_message)
            if ids:
                pending_actions[session_id] = {'type': 'bulk_delete', 'candidate_ids': ids}
                return {'response': f"You are about to delete candidates with IDs: {', '.join(ids)}. Reply 'yes' to confirm or 'cancel' to abort."}
        # Bulk update candidates (e.g., move all candidates in Screening to Interview Scheduled)
        m = re.search(r'update all candidates in status ([\w ]+) to ([\w ]+)', user_message.lower())
        if m:
            from_status = m.group(1).strip()
            to_status = m.group(2).strip()
            all_candidates = list_candidates(page=1, auth_token=auth_token)
            filtered = [c for c in all_candidates.get('results', []) if str(c.get('candidate_stage', '')).lower() == from_status.lower()]
            if filtered:
                ids = [str(c['id']) for c in filtered]
                pending_actions[session_id] = {'type': 'bulk_update', 'candidate_ids': ids, 'field': 'candidate_stage', 'value': to_status}
                details = '\n---\n'.join([format_candidate(c) for c in filtered])
                return {'response': f"You are about to update the following candidates from status '{from_status}' to '{to_status}':\n\n{details}\n\nReply 'yes' to confirm or 'cancel' to abort."}
            else:
                return {'response': f'No candidates found with status "{from_status}".'}
        # Conversational context: remember last candidate/job post shown (simple demo)
        # (You can expand this with a context/session store for more advanced follow-ups)
        
        # Handle "Delete it" or "Delete the last candidate" commands
        if re.search(r'delete (it|the last candidate|this candidate)', user_message.lower()):
            if session_id in session_context and session_context[session_id].get('last_candidate'):
                candidate_id = session_context[session_id]['last_candidate']
                result = get_candidate(candidate_id, auth_token=auth_token)
                if result and result.get('id'):
                    pending_actions[session_id] = {'type': 'delete', 'candidate_id': candidate_id}
                    return {'response': f"You requested to delete the following candidate.\n\n{format_candidate(result)}\n\nAre you sure you want to delete this candidate? Reply 'yes' to confirm."}
                else:
                    return {'response': "Sorry, the last candidate is no longer available."}
            else:
                return {'response': "No candidate has been shown yet. Try searching for a specific candidate first."}
        
        # Handle "Update it" or "Update the last candidate" commands
        if re.search(r'update (it|the last candidate|this candidate)', user_message.lower()):
            if session_id in session_context and session_context[session_id].get('last_candidate'):
                candidate_id = session_context[session_id]['last_candidate']
                result = get_candidate(candidate_id, auth_token=auth_token)
                if result and result.get('id'):
                    return {'response': f"Please specify what you want to update for the last candidate. Example: 'Update the last candidate's status to Interview Scheduled' or 'Update the last candidate's email to new@email.com'"}
                else:
                    return {'response': "Sorry, the last candidate is no longer available."}
            else:
                return {'response': "No candidate has been shown yet. Try searching for a specific candidate first."}
    else:
        # For function-calling models, use the agent directly
        response = run_agent(messages, session_id=session_id, model=model, auth_token=auth_token, page=page, prompt=prompt, pending_actions=pending_actions)
        return {'response': response}
    
    # LLM fallback for intent
    # If no pattern matched, use the LLM agent to try to understand intent
    response = run_agent(messages, session_id=session_id, model=model, auth_token=auth_token, page=page, prompt=prompt, pending_actions=pending_actions)
    return {'response': response}

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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HR Assistant Pro MCP Server...")
    print("📡 Server will be available at: http://localhost:8001")
    print("🔧 Available endpoints:")
    print("   - POST /chat - Chat with HR Assistant")
    print("   - GET  /models - List available models")
    print("   - All Django API endpoints via proxy")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 