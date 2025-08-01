from dotenv import load_dotenv
import os
import sys
import traceback
import requests
load_dotenv()
# Debug: Print the loaded API keys (masked for security)
openai_key = os.getenv('OPENAI_API_KEY')
azure_key = os.getenv('AZURE_OPENAI_API_KEY')
azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

if openai_key:
    print(f"Loaded OPENAI_API_KEY: {openai_key[:6]}...{'*' * (len(openai_key)-10)}...{openai_key[-4:]}")
else:
    print("OPENAI_API_KEY not found or empty!")

if azure_key:
    print(f"Loaded AZURE_OPENAI_API_KEY: {azure_key[:6]}...{'*' * (len(azure_key)-10)}...{azure_key[-4:]}")
    print(f"Azure Endpoint: {azure_endpoint}")
else:
    print("AZURE_OPENAI_API_KEY not found or empty!")
# Remove or comment out debug prints for API keys and tokens
# openai_key = os.getenv('OPENAI_API_KEY')
# openrouter_key = os.getenv('OPENROUTER_API_KEY')
# if not openai_key:
#     print('OPENAI_API_KEY not found in environment!', file=sys.stderr)
# else:
#     print(f'OPENAI_API_KEY loaded: {openai_key[:6]}... (length: {len(openai_key)})', file=sys.stderr)
# if not openrouter_key:
#     print('OPENROUTER_API_KEY not found in environment!', file=sys.stderr)
# else:
#     print(f'OPENROUTER_API_KEY loaded: {openrouter_key[:6]}... (length: {len(openrouter_key)})', file=sys.stderr)
# hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
# if not hf_token:
#     print('HUGGINGFACE_API_TOKEN not found in environment!', file=sys.stderr)
# else:
#     print(f'HUGGINGFACE_API_TOKEN loaded: {hf_token[:6]}... (length: {len(hf_token)})', file=sys.stderr)
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI, AzureChatOpenAI  # Updated import for chat models
from tools import (
    get_candidate, delete_candidate, update_candidate, get_candidate_metrics, list_candidates,
    format_candidate, format_candidate_list, add_candidate, add_note, list_notes, delete_note,
    list_job_titles, export_candidates_csv, get_recent_activities, get_overall_metrics,
    list_job_posts, add_job_post, update_job_post, delete_job_post, get_job_post_title_choices,
    search_candidates, bulk_update_candidates, bulk_delete_candidates, get_job_post, format_job_post,
    bulk_add_candidates, get_schema_org_data, get_all_candidates, search_candidate_by_name, vector_search_candidates
)


from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- Memory and Summaries ---
session_summaries = {}  # In-memory dict for session summaries (replace with DB for production)

# Set your API keys as environment variables
OPENROUTER_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-...')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

# Minimal state schema for LangGraph
@dataclass
class AgentState:
    messages: list

# Fallback: Call Hugging Face Inference API for a public model (e.g., GPT-2)
def call_hf_fallback(prompt):
    api_url = "https://api-inference.huggingface.co/models/gpt2"  # Public model for fallback
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    data = {"inputs": prompt}
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        try:
            result = response.json()
        except Exception as json_err:
            # print(f'HF raw response: {response.text}', file=sys.stderr)
            return {"role": "assistant", "content": "Sorry, I couldn't get a valid response from the backup AI service. Please try again later or check your Hugging Face API token."}
        # Extract text from result
        if isinstance(result, dict) and "generated_text" in result:
            return {"role": "assistant", "content": result["generated_text"]}
        elif isinstance(result, list) and result and "generated_text" in result[0]:
            return {"role": "assistant", "content": result[0]["generated_text"]}
        elif isinstance(result, dict) and "error" in result:
            # print(f'HF error: {result["error"]}', file=sys.stderr)
            return {"role": "assistant", "content": f"Sorry, the backup AI service returned an error: {result['error']}"}
        else:
            return {"role": "assistant", "content": "Sorry, the backup AI service returned an unexpected response. Please try again later."}
    except Exception as e:
        # print(f'HF fallback exception: {e}', file=sys.stderr)
        return {"role": "assistant", "content": "Sorry, there was a problem contacting the backup AI service. Please try again later."}

def convert_to_lc_messages(messages):
    lc_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                # fallback to HumanMessage for unknown roles
                lc_messages.append(HumanMessage(content=content))
        else:
            # fallback: pass through if already a message object
            lc_messages.append(msg)
    return lc_messages

def create_azure_llm(model_name="gpt-35-turbo"):
    """Create an Azure OpenAI LLM instance"""
    if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
        print("Azure OpenAI credentials not found!")
        return None
    
    try:
        # Map model names to Azure deployment names
        model_mapping = {
            "gpt-35-turbo": "gpt-35-turbo",
            "gpt-4": "gpt-4",
            "gpt-4-turbo": "gpt-4-turbo",
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini"
        }
        
        deployment_name = model_mapping.get(model_name, model_name)
        
        # Clean up the endpoint URL (remove any trailing slashes and chat/completions)
        endpoint = AZURE_OPENAI_ENDPOINT.rstrip('/')
        if '/openai/deployments/' in endpoint:
            # Extract the base endpoint
            endpoint = endpoint.split('/openai/deployments/')[0]
        
        print(f"Using Azure endpoint: {endpoint}")
        print(f"Using Azure deployment: {deployment_name}")
        
        llm = AzureChatOpenAI(
            azure_deployment=deployment_name,
            openai_api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=endpoint,
            api_key=AZURE_OPENAI_API_KEY,
            temperature=0.7
        )
        return llm
    except Exception as e:
        print(f"Error creating Azure LLM: {e}")
        return None

def create_llm_instance(model=None):
    """Create LLM instance based on model type"""
    print(f"[DEBUG] Creating LLM instance for model: {model}")
    if model and model.startswith("azure/"):
        # Extract model name from "azure/gpt-35-turbo" format
        azure_model = model.replace("azure/", "")
        print(f"[DEBUG] Creating Azure LLM with model: {azure_model}")
        llm = create_azure_llm(azure_model)
        print(f"[DEBUG] Azure LLM created: {llm is not None}")
        return llm
    else:
        # Fallback to OpenAI/OpenRouter
        print(f"[DEBUG] Creating OpenAI/OpenRouter LLM with model: {model}")
        return ChatOpenAI(
            model=model or "gpt-3.5-turbo",
            openai_api_key=OPENROUTER_API_KEY,
            temperature=0.7
        )

# --- LangGraph agent setup ---
def get_langgraph_agent(model=None, auth_token=None, page=None):
    llm = create_llm_instance(model)
    if not llm:
        # Fallback to OpenAI if Azure is not configured
        llm = ChatOpenAI(
            model=model or "qwen/qwen3-235b-a22b-07-25:free",
            temperature=0,
            streaming=False,
            default_headers={"X-Title": "HR Assistant Pro MCP"},
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    # Create tools for LangGraph agent
    def get_candidate_tool(cid):
        return get_candidate(cid, auth_token=auth_token)
    def delete_candidate_tool(cid):
        return delete_candidate(cid, auth_token=auth_token)
    def update_candidate_tool(args):
        return update_candidate(args[0], args[1], args[2], auth_token=auth_token)
    def get_candidate_metrics_tool(params=None):
        return get_candidate_metrics(params, auth_token=auth_token)
    def list_candidates_tool(page_arg=None):
        # If no page specified, get all candidates
        if page_arg is None:
            return list_candidates(all_candidates=True, auth_token=auth_token)
        return list_candidates(page=page_arg or page or 1, auth_token=auth_token)
    def add_candidate_tool(data):
        return add_candidate(data, auth_token=auth_token)
    def add_note_tool(candidate_id, content):
        return add_note(candidate_id, content, auth_token=auth_token)
    def list_notes_tool(candidate_id):
        return list_notes(candidate_id, auth_token=auth_token)
    def delete_note_tool(note_id):
        return delete_note(note_id, auth_token=auth_token)
    def list_job_titles_tool(input_text=None):
        return list_job_titles(auth_token=auth_token)
    def export_candidates_csv_tool(input_text=None):
        return export_candidates_csv(auth_token=auth_token)
    def get_recent_activities_tool(input_text=None):
        return get_recent_activities(auth_token=auth_token)
    def get_overall_metrics_tool(input_text=None):
        return get_overall_metrics(auth_token=auth_token)
    def list_job_posts_tool(input_text=None):
        return list_job_posts(auth_token=auth_token)
    def add_job_post_tool(data):
        return add_job_post(data, auth_token=auth_token)
    def update_job_post_tool(job_post_id, data):
        return update_job_post(job_post_id, data, auth_token=auth_token)
    def delete_job_post_tool(job_post_id):
        return delete_job_post(job_post_id, auth_token=auth_token)
    def get_job_post_title_choices_tool(input_text=None):
        return get_job_post_title_choices(auth_token=auth_token)
    def search_candidates_tool(filters):
        return search_candidates(filters, auth_token=auth_token)
    def bulk_update_candidates_tool(ids, field, value):
        return bulk_update_candidates(ids, field, value, auth_token=auth_token)
    def bulk_delete_candidates_tool(ids):
        return bulk_delete_candidates(ids, auth_token=auth_token)
    def get_job_post_tool(job_post_id):
        return get_job_post(job_post_id, auth_token=auth_token)
    def bulk_add_candidates_tool(candidates):
        return bulk_add_candidates(candidates, auth_token=auth_token)
    def get_uploaded_file_data_tool(file_name=None):
        """Get data from uploaded files in the current session"""
        if not pending_actions or session_id not in pending_actions:
            return {"success": False, "message": "No uploaded files found"}
        
        session_data = pending_actions[session_id]
        if 'uploaded_files' not in session_data:
            return {"success": False, "message": "No uploaded files found"}
        
        files = session_data['uploaded_files']
        if file_name:
            # Return specific file data
            for file_info in files:
                if file_info['original_name'] == file_name:
                    return {"success": True, "file_data": file_info}
            return {"success": False, "message": f"File '{file_name}' not found"}
        else:
            # Return all file data
            return {"success": True, "files": files}
    
    def get_schema_org_data_tool(data_type='candidates', candidate_id=None, job_post_id=None):
        return get_schema_org_data(data_type, candidate_id, job_post_id, auth_token=auth_token)
    def get_all_candidates_tool(input_text=None):
        """Get all candidates without pagination for comprehensive search"""
        return get_all_candidates(auth_token=auth_token)
    
    tools = [
        Tool(name='get_candidate', func=get_candidate_tool, description='Get candidate details by ID'),
        Tool(name='delete_candidate', func=delete_candidate_tool, description='Delete candidate by ID'),
        Tool(name='update_candidate', func=update_candidate_tool, description='Update candidate field by ID'),
        Tool(name='get_candidate_metrics', func=get_candidate_metrics_tool, description='Get candidate analytics/metrics'),
        Tool(name='list_candidates', func=list_candidates_tool, description='Show all candidates, list all candidates, display all candidates'),
        Tool(name='add_candidate', func=add_candidate_tool, description='Add a new candidate'),
        Tool(name='add_note', func=add_note_tool, description='Add a note to a candidate'),
        Tool(name='list_notes', func=list_notes_tool, description='List notes for a candidate'),
        Tool(name='delete_note', func=delete_note_tool, description='Delete a note'),
        Tool(name='list_job_titles', func=list_job_titles_tool, description='List all job titles'),
        Tool(name='export_candidates_csv', func=export_candidates_csv_tool, description='Export candidates to CSV'),
        Tool(name='get_recent_activities', func=get_recent_activities_tool, description='Get recent activities'),
        Tool(name='get_overall_metrics', func=get_overall_metrics_tool, description='Get overall HR metrics'),
        Tool(name='list_job_posts', func=list_job_posts_tool, description='List all job posts'),
        Tool(name='add_job_post', func=add_job_post_tool, description='Add a new job post'),
        Tool(name='update_job_post', func=update_job_post_tool, description='Update a job post'),
        Tool(name='delete_job_post', func=delete_job_post_tool, description='Delete a job post'),
        Tool(name='get_job_post_title_choices', func=get_job_post_title_choices_tool, description='Get job post title choices'),
        Tool(name='search_candidates', func=search_candidates_tool, description='Search candidates with filters'),
        Tool(name='bulk_update_candidates', func=bulk_update_candidates_tool, description='Bulk update candidates'),
        Tool(name='bulk_delete_candidates', func=bulk_delete_candidates_tool, description='Bulk delete candidates'),
        Tool(name='get_job_post', func=get_job_post_tool, description='Get job post details by ID'),
        Tool(name='bulk_add_candidates', func=bulk_add_candidates_tool, description='Add multiple candidates at once. Input: a list of candidate dicts with fields like first_name, last_name, email, etc.'),
        Tool(name='get_uploaded_file_data', func=get_uploaded_file_data_tool, description='Get data from uploaded files in the current session. Use this to access candidate data from uploaded CSV/Excel files.'),
        Tool(name='get_schema_org_data', func=get_schema_org_data_tool, description='Get Schema.org structured data for better AI understanding. Input: {"data_type": "candidates"|"job_posts", "candidate_id": int (optional), "job_post_id": int (optional)}'),
        Tool(name='get_all_candidates', func=get_all_candidates_tool, description='Get all candidates without pagination for comprehensive search'),
    ]
    
    # Use the regular agent instead of LangGraph for now since it has proper tool support
    return get_agent(model, auth_token=auth_token, page=page, pending_actions=None, session_id=None)

def get_agent(model=None, auth_token=None, page=None, pending_actions=None, session_id=None):
    llm = create_llm_instance(model)
    if not llm:
        # Fallback to OpenAI if Azure is not configured
        llm = ChatOpenAI(
            model=model or "qwen/qwen3-235b-a22b-07-25:free",
            default_headers={"X-Title": "HR Assistant Pro MCP"},
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def get_candidate_tool(cid):
        return get_candidate(cid, auth_token=auth_token)
    def delete_candidate_tool(cid):
        return delete_candidate(cid, auth_token=auth_token)
    def update_candidate_tool(args):
        return update_candidate(args[0], args[1], args[2], auth_token=auth_token)
    def get_candidate_metrics_tool(input_text=None):
        return get_candidate_metrics(auth_token=auth_token)
    def list_candidates_tool(page_arg=None):
        # If no page specified, get all candidates
        if page_arg is None:
            return list_candidates(all_candidates=True, auth_token=auth_token)
        return list_candidates(page=page_arg or page or 1, auth_token=auth_token)
    def add_candidate_tool(data):
        return add_candidate(data, auth_token=auth_token)
    def add_note_tool(candidate_id, content):
        return add_note(candidate_id, content, auth_token=auth_token)
    def list_notes_tool(candidate_id):
        return list_notes(candidate_id, auth_token=auth_token)
    def delete_note_tool(note_id):
        return delete_note(note_id, auth_token=auth_token)
    def list_job_titles_tool(input_text=None):
        return list_job_titles(auth_token=auth_token)
    def export_candidates_csv_tool(input_text=None):
        return export_candidates_csv(auth_token=auth_token)
    def get_recent_activities_tool(input_text=None):
        return get_recent_activities(auth_token=auth_token)
    def get_overall_metrics_tool(input_text=None):
        return get_overall_metrics(auth_token=auth_token)
    def list_job_posts_tool(input_text=None):
        return list_job_posts(auth_token=auth_token)
    def add_job_post_tool(data):
        return add_job_post(data, auth_token=auth_token)
    def update_job_post_tool(job_post_id, data):
        return update_job_post(job_post_id, data, auth_token=auth_token)
    def delete_job_post_tool(job_post_id):
        return delete_job_post(job_post_id, auth_token=auth_token)
    def get_job_post_title_choices_tool(input_text=None):
        return get_job_post_title_choices(auth_token=auth_token)
    def search_candidates_tool(filters):
        return search_candidates(filters, auth_token=auth_token)
    def bulk_update_candidates_tool(ids, field, value):
        return bulk_update_candidates(ids, field, value, auth_token=auth_token)
    def bulk_delete_candidates_tool(ids):
        return bulk_delete_candidates(ids, auth_token=auth_token)
    def get_job_post_tool(job_post_id):
        return get_job_post(job_post_id, auth_token=auth_token)
    def bulk_add_candidates_tool(candidates):
        """Add multiple candidates to the system"""
        # If candidates is a string, try to parse it as JSON
        if isinstance(candidates, str):
            try:
                import json
                candidates = json.loads(candidates)
            except:
                return {"success": False, "message": "Invalid candidates data format"}
        
        # If candidates is not a list, try to get it from uploaded files
        if not isinstance(candidates, list):
            # Get uploaded file data
            file_data = get_uploaded_file_data_tool()
            if not file_data.get('success'):
                return {"success": False, "message": "No uploaded file data found"}
            
            # Extract candidate data from the uploaded file
            files = file_data.get('files', [])
            if not files:
                return {"success": False, "message": "No files found in session"}
            
            # Get the first file's data
            file_info = files[0]
            print(f"[DEBUG] File info keys: {list(file_info.keys())}")
            print(f"[DEBUG] Has extracted_data: {'extracted_data' in file_info}")
            
            if 'extracted_data' not in file_info:
                return {"success": False, "message": "No extracted data found in uploaded file"}
            
            extracted_data = file_info['extracted_data']
            print(f"[DEBUG] Extracted data keys: {list(extracted_data.keys())}")
            
            if 'data' not in extracted_data:
                return {"success": False, "message": "No candidate data found in extracted data"}
            
            candidates = extracted_data['data']
            print(f"[DEBUG] Extracted {len(candidates)} candidates from uploaded file")
            print(f"[DEBUG] First candidate: {candidates[0] if candidates else 'None'}")
        
        return bulk_add_candidates(candidates, auth_token=auth_token)
    def get_uploaded_file_data_tool(file_name=None):
        """Get data from uploaded files in the current session"""
        print(f"[DEBUG] get_uploaded_file_data_tool called with file_name: {file_name}")
        print(f"[DEBUG] session_id: {session_id}")
        print(f"[DEBUG] pending_actions keys: {list(pending_actions.keys()) if pending_actions else 'None'}")
        
        if not pending_actions or session_id not in pending_actions:
            print(f"[DEBUG] No pending_actions or session_id not found")
            return {"success": False, "message": "No uploaded files found"}
        
        session_data = pending_actions[session_id]
        print(f"[DEBUG] session_data keys: {list(session_data.keys())}")
        
        if 'uploaded_files' not in session_data:
            print(f"[DEBUG] No uploaded_files in session_data")
            return {"success": False, "message": "No uploaded files found"}
        
        files = session_data['uploaded_files']
        print(f"[DEBUG] Found {len(files)} files in session")
        
        if file_name:
            # Return specific file data
            for file_info in files:
                if file_info['original_name'] == file_name:
                    print(f"[DEBUG] Found specific file: {file_name}")
                    return {"success": True, "file_data": file_info}
            print(f"[DEBUG] File '{file_name}' not found")
            return {"success": False, "message": f"File '{file_name}' not found"}
        else:
            # Return all file data
            print(f"[DEBUG] Returning all files data")
            return {"success": True, "files": files}
    
    def get_schema_org_data_tool(input_text):
        # Parse input to extract parameters
        try:
            if isinstance(input_text, str):
                # Try to parse as JSON
                import json
                data = json.loads(input_text)
            else:
                data = input_text
        except:
            # Default to candidates if parsing fails
            data = {"data_type": "candidates"}
        
        data_type = data.get("data_type", "candidates")
        candidate_id = data.get("candidate_id")
        job_post_id = data.get("job_post_id")
        
        return get_schema_org_data(data_type, candidate_id, job_post_id, auth_token=auth_token)
    
    def get_all_candidates_tool(input_text=None):
        """Get all candidates without pagination for comprehensive search"""
        return get_all_candidates(auth_token=auth_token)
    
    def vector_search_candidates_tool(query):
        """Perform semantic vector search for candidates"""
        return vector_search_candidates(query, auth_token=auth_token)
    
    tools = [
        Tool(name='get_candidate', func=get_candidate_tool, description='Get candidate details by ID'),
        Tool(name='delete_candidate', func=delete_candidate_tool, description='Delete candidate by ID'),
        Tool(name='update_candidate', func=update_candidate_tool, description='Update candidate field by ID'),
        Tool(name='get_candidate_metrics', func=get_candidate_metrics_tool, description='Get candidate analytics/metrics'),
        Tool(name='list_candidates', func=list_candidates_tool, description='Show all candidates, list all candidates, display all candidates'),
        Tool(name='add_candidate', func=add_candidate_tool, description='Add a new candidate'),
        Tool(name='add_note', func=add_note_tool, description='Add a note to a candidate'),
        Tool(name='list_notes', func=list_notes_tool, description='List notes for a candidate'),
        Tool(name='delete_note', func=delete_note_tool, description='Delete a note'),
        Tool(name='list_job_titles', func=list_job_titles_tool, description='List all job titles'),
        Tool(name='export_candidates_csv', func=export_candidates_csv_tool, description='Export candidates to CSV'),
        Tool(name='get_recent_activities', func=get_recent_activities_tool, description='Get recent activities'),
        Tool(name='get_overall_metrics', func=get_overall_metrics_tool, description='Get overall HR metrics'),
        Tool(name='list_job_posts', func=list_job_posts_tool, description='List all job posts'),
        Tool(name='add_job_post', func=add_job_post_tool, description='Add a new job post'),
        Tool(name='update_job_post', func=update_job_post_tool, description='Update a job post'),
        Tool(name='delete_job_post', func=delete_job_post_tool, description='Delete a job post'),
        Tool(name='get_job_post_title_choices', func=get_job_post_title_choices_tool, description='Get job post title choices'),
        Tool(name='search_candidates', func=search_candidates_tool, description='Search candidates with filters'),
        Tool(name='vector_search_candidates', func=vector_search_candidates_tool, description='Perform semantic vector search for candidates. Use this for natural language queries like "find candidates with Python skills" or "show me experienced developers"'),
        Tool(name='bulk_update_candidates', func=bulk_update_candidates_tool, description='Bulk update candidates'),
        Tool(name='bulk_delete_candidates', func=bulk_delete_candidates_tool, description='Bulk delete candidates'),
        Tool(name='get_job_post', func=get_job_post_tool, description='Get job post details by ID'),
        Tool(name='bulk_add_candidates', func=bulk_add_candidates_tool, description='Add multiple candidates at once. Use this tool when you need to add several candidates in bulk.'),
        Tool(name='get_uploaded_file_data', func=get_uploaded_file_data_tool, description='Get data from uploaded files in the current session. Use this to access candidate data from uploaded CSV/Excel files.'),
        Tool(name='get_schema_org_data', func=get_schema_org_data_tool, description='Get Schema.org structured data for better AI understanding. Use this tool when you need structured data about candidates or job posts.'),
        Tool(name='get_all_candidates', func=get_all_candidates_tool, description='Get all candidates without pagination for comprehensive search'),
    ]
    
    # Always use function calling agent for better tool usage
    print(f"[DEBUG] Using function calling agent for model: {model}")
    
    # Create a system prompt that forces tool usage
    system_prompt = """You are HR Assistant Pro, an intelligent AI assistant for HR operations. 

CRITICAL INSTRUCTIONS:
1. You MUST use tools to perform actions. NEVER respond with just text explanations.
2. For semantic/natural language searches, ALWAYS use vector_search_candidates tool first.
3. For specific candidate lookups by ID, use get_candidate tool.
4. For filtered searches, use search_candidates tool.
5. When users say "add that data", "add these to the system", "add these data into system", "add these candidates to the system", or "add these to candidate data", you MUST:
   - First use get_uploaded_file_data to get the file data
   - Then use bulk_add_candidates to add the candidates
   - Report the results
   - NEVER respond with text explanations about data format or debugging

SEARCH STRATEGY:
- Natural language queries like "find candidates with Python skills" → use vector_search_candidates
- Specific searches like "candidate ID 123" → use get_candidate
- Filtered searches like "candidates in New York" → use search_candidates
- List all candidates → use list_candidates

BULK ADD STRATEGY:
- When user wants to add uploaded file data → use get_uploaded_file_data THEN bulk_add_candidates
- NEVER respond with text explanations for bulk add - ALWAYS use the tools
- NEVER say "I need to review the data structure" or "debugging the data structure"
- ALWAYS call the tools directly

Available tools:
- vector_search_candidates: For semantic/natural language candidate searches
- get_candidate: Get specific candidate by ID
- search_candidates: Filtered candidate search
- list_candidates: List all candidates
- get_uploaded_file_data: Gets data from uploaded CSV/Excel files
- bulk_add_candidates: Adds multiple candidates from file data
- add_candidate: Adds individual candidates

Remember: ALWAYS use tools first, then provide results. Never just explain what you would do. For bulk add operations, ALWAYS use get_uploaded_file_data followed by bulk_add_candidates. NEVER respond with debugging text."""
    
    return initialize_agent(
        tools, llm, agent_type='openai-functions',
        handle_parsing_errors=True,
        max_iterations=5,
        early_stopping_method="generate",
        verbose=False,
        agent_kwargs={"system_message": system_prompt}
    )

def format_candidate(candidate):
    # Format a single candidate dict as markdown
    return f"""
**{candidate.get('name', candidate.get('first_name', ''))}**
- Email: {candidate.get('email', '')}
- Status: {candidate.get('status', candidate.get('candidate_stage', ''))}
- Skills: {', '.join(candidate.get('skills', candidate.get('communication_skills', [])))}
- Experience: {candidate.get('experience', candidate.get('years_of_experience', ''))} years
- Location: {candidate.get('location', candidate.get('city', ''))}
"""

def format_candidate_list(candidates):
    # Format a list of candidates as a markdown table
    if not candidates:
        return 'No candidates found.'
    headers = ['ID', 'Name', 'Email', 'Status', 'Skills', 'Experience', 'Location']
    rows = []
    for c in candidates:
        rows.append([
            c.get('id', ''),
            c.get('name', c.get('first_name', '')),
            c.get('email', ''),
            c.get('status', c.get('candidate_stage', '')),
            ', '.join(c.get('skills', c.get('communication_skills', []))),
            str(c.get('experience', c.get('years_of_experience', ''))),
            c.get('location', c.get('city', '')),
        ])
    # Build markdown table
    md = '| ' + ' | '.join(headers) + ' |\n'
    md += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    for row in rows:
        md += '| ' + ' | '.join(row) + ' |\n'
    return md

def run_agent(messages: List[Dict[str, Any]], session_id=None, model=None, auth_token=None, page=None, prompt=None, user_profile=None, pending_actions=None):
    # --- Memory: keep only the last 10 messages ---
    short_history = messages[-10:] if messages else []
    # --- Summarization: prepend a session summary if available ---
    summary = session_summaries.get(session_id) if session_id else None
    if summary:
        short_history = [{"role": "system", "content": summary}] + short_history
    try:
        print(f"[DEBUG] run_agent called with model: {model}")
        
        # Check if this is a simple greeting or conversational message
        last_message = short_history[-1] if short_history else {"role": "user", "content": ""}
        input_text = last_message.get('content', '').strip().lower()
        
        # Handle simple greetings and conversational messages directly
        if input_text in ['hi', 'hello', 'hey', 'hy', 'good morning', 'good afternoon', 'good evening']:
            return "Hello! 👋 How can I help you with HR today? I can assist with candidate management, job postings, analytics, and more!"
        
        # Handle confirmation responses
        if input_text in ['yes', 'y', 'confirm', 'sure', 'ok', 'okay']:
            # Check if there's a pending action in the session context
            if session_id and pending_actions and session_id in pending_actions:
                action = pending_actions[session_id]
                if action['type'] == 'add_candidate':
                    # Create the candidate
                    from tools import add_candidate
                    result = add_candidate(action['data'], auth_token=auth_token)
                    if result.get('success'):
                        # Remove the pending action
                        pending_actions.pop(session_id, None)
                        return f"✅ Candidate {action['data']['first_name']} {action['data'].get('last_name','')} added successfully!"
                    else:
                        error_msg = result.get('message', '')
                        if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                            return f"❌ A candidate with email '{action['data']['email']}' already exists.\n\n💡 **Suggestions:**\n- View the existing candidate: 'Show me candidate {action['data']['email']}'\n- Update the existing candidate: 'Update candidate {action['data']['email']}'\n- Try adding with a different email"
                        else:
                            return f"❌ Failed to add candidate. {error_msg}"
                else:
                    return "I understand you want to confirm, but I don't have a pending action to confirm. Could you please try your request again?"
            else:
                return "I understand you want to confirm, but I don't have a pending action to confirm. Could you please try your request again?"
        
        # Use agent for complex requests
        print(f"[DEBUG] Creating agent with session_id: {session_id}")
        print(f"[DEBUG] pending_actions keys: {list(pending_actions.keys()) if pending_actions else 'None'}")
        if pending_actions and session_id in pending_actions:
            print(f"[DEBUG] session_data keys: {list(pending_actions[session_id].keys())}")
        
        agent = get_agent(model, auth_token=auth_token, page=page, pending_actions=pending_actions, session_id=session_id)
        print(f"[DEBUG] Agent created successfully")
        
        # Add context about uploaded files if available
        input_text = last_message.get('content', '')
        if pending_actions and session_id in pending_actions:
            session_data = pending_actions[session_id]
            if 'uploaded_files' in session_data and session_data['uploaded_files']:
                files_info = []
                for file_info in session_data['uploaded_files']:
                    files_info.append(f"File: {file_info['original_name']}")
                    if 'extracted_data' in file_info:
                        extracted = file_info['extracted_data']
                        if 'data' in extracted:
                            files_info.append(f"  - Contains {len(extracted['data'])} candidate records")
                        if 'candidate_info' in extracted:
                            files_info.append(f"  - Extracted candidate info available")
                
                if files_info:
                    input_text += f"\n\n**Available uploaded files:**\n" + "\n".join(files_info)
        
        try:
            result = agent.invoke({"input": input_text})
            print(f"[DEBUG] Agent invoke completed")
            
            # Handle different response formats
            if isinstance(result, dict):
                if 'output' in result:
                    output = result['output']
                    # Check if agent stopped due to limits
                    if "Agent stopped due to iteration limit" in output or "time limit" in output:
                        return "I'm having trouble processing that request. Could you please rephrase your question or try a simpler request?"
                    return output
                elif 'result' in result:
                    return result['result']
                else:
                    return str(result)
            elif hasattr(result, 'content'):
                content = result.content
                if "Agent stopped due to iteration limit" in content or "time limit" in content:
                    return "I'm having trouble processing that request. Could you please rephrase your question or try a simpler request?"
                return content
            else:
                result_str = str(result)
                if "Agent stopped due to iteration limit" in result_str or "time limit" in result_str:
                    return "I'm having trouble processing that request. Could you please rephrase your question or try a simpler request?"
                return result_str
        except Exception as agent_error:
            print(f"[DEBUG] Agent failed, trying direct tool calls: {str(agent_error)}")
            
            # Fallback: Try direct tool calls for file operations
            if any(keyword in input_text.lower() for keyword in ['add', 'upload', 'candidate', 'data']):
                try:
                    print(f"[DEBUG] Attempting direct tool calls for file operation")
                    
                    # Check if we have uploaded files in the session
                    if not pending_actions or session_id not in pending_actions:
                        return "❌ No uploaded files found in the current session."
                    
                    session_data = pending_actions[session_id]
                    if 'uploaded_files' not in session_data:
                        return "❌ No uploaded files found in the current session."
                    
                    files = session_data['uploaded_files']
                    if not files:
                        return "❌ No uploaded files found in the current session."
                    
                    print(f"[DEBUG] Found {len(files)} files")
                    
                    # Get the first file's data
                    file_info = files[0]
                    print(f"[DEBUG] Processing file: {file_info.get('original_name', 'Unknown')}")
                    
                    if 'extracted_data' in file_info and 'data' in file_info['extracted_data']:
                        candidates_data = file_info['extracted_data']['data']
                        print(f"[DEBUG] Found {len(candidates_data)} candidates to add")
                        
                        # Add candidates using bulk_add_candidates from tools module
                        from tools import bulk_add_candidates
                        result = bulk_add_candidates(candidates_data, auth_token=auth_token)
                        print(f"[DEBUG] bulk_add_candidates result: {result}")
                        
                        if result.get('success'):
                            return f"✅ Successfully added {len(candidates_data)} candidates to the system!"
                        else:
                            return f"❌ Failed to add candidates: {result.get('message', 'Unknown error')}"
                    else:
                        return "❌ No candidate data found in the uploaded file."
                except Exception as tool_error:
                    print(f"[DEBUG] Direct tool call failed: {str(tool_error)}")
                    return f"❌ Error processing file data: {str(tool_error)}"
            
            # If not a file operation, re-raise the original error
            raise agent_error
    except Exception as e:
        print(f"[DEBUG] Error in run_agent: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a friendly error message for parsing errors
        if "Could not parse LLM output" in str(e):
            return "I'm trying to process your request but need to use the right tools. Let me try a different approach to add the candidates from your uploaded file."
        elif "Missing some input keys" in str(e):
            return "I'm having trouble understanding your request. Could you please try again?"
        elif 'rate limit' in str(e).lower() or '429' in str(e) or 'limit exceeded' in str(e):
            return "⚠️ Sorry, our AI service is temporarily unavailable due to usage limits. Please try again later or contact support if this issue persists."
        else:
            return "Sorry, I couldn't complete your request due to an internal error. Please try again or contact support if the issue persists." 