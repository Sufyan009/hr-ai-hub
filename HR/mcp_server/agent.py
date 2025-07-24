from dotenv import load_dotenv
import os
import sys
import traceback
import requests
load_dotenv()
# Debug: Print the loaded OpenAI/OpenRouter API key (masked for security)
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"Loaded OPENAI_API_KEY: {api_key[:6]}...{'*' * (len(api_key)-10)}...{api_key[-4:]}")
else:
    print("OPENAI_API_KEY not found or empty!")
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
from langchain_openai import ChatOpenAI  # Updated import for chat models
from tools import get_candidate, delete_candidate, update_candidate, get_candidate_metrics, list_candidates
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- Memory and Summaries ---
session_summaries = {}  # In-memory dict for session summaries (replace with DB for production)

# Set your OpenRouter API key as an environment variable or directly here
OPENROUTER_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-...')

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

# --- LangGraph agent setup ---
def get_langgraph_agent(model=None, auth_token=None, page=None, user_profile=None):
    llm = ChatOpenAI(
        model=model or "qwen/qwen3-235b-a22b-07-25:free",
        temperature=0,
        streaming=False,
        default_headers={"X-Title": "HR Assistant Pro MCP"},
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    def llm_node(state: AgentState):
        try:
            # Convert messages to LangChain message objects
            lc_messages = convert_to_lc_messages(state.messages)
            response = llm.invoke(lc_messages)
            return AgentState(messages=state.messages + [response])
        except Exception as e:
            # Improved error handling: log and surface error details
            print("Primary LLM failed:", str(e))
            msg = str(e).lower()
            if "rate limit" in msg or "429" in msg or "quota" in msg or "limit exceeded" in msg:
                return AgentState(messages=state.messages + [{
                    "role": "assistant",
                    "content": "⚠️ Sorry, our AI service is temporarily unavailable due to usage limits. Please try again later or contact support if this issue persists."
                }])
            else:
                # Return the actual error message for other issues
                return AgentState(messages=state.messages + [{
                    "role": "assistant",
                    "content": f"Sorry, there was an error with the primary AI service: {str(e)}"
                }])
    graph = StateGraph(AgentState)
    graph.add_node("llm", llm_node)
    graph.set_entry_point("llm")
    graph.set_finish_point("llm")
    return graph.compile()

def get_agent(model=None, auth_token=None, page=None, user_profile=None):
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
    def get_candidate_metrics_tool(params=None):
        return get_candidate_metrics(params, auth_token=auth_token)
    def list_candidates_tool(page_arg=None):
        return list_candidates(page=page_arg or page or 1, auth_token=auth_token)
    tools = [
        Tool(name='get_candidate', func=get_candidate_tool, description='Get candidate details by ID'),
        Tool(name='delete_candidate', func=delete_candidate_tool, description='Delete candidate by ID'),
        Tool(name='update_candidate', func=update_candidate_tool, description='Update candidate field by ID'),
        Tool(name='get_candidate_metrics', func=get_candidate_metrics_tool, description='Get candidate analytics/metrics'),
        Tool(
            name='list_candidates',
            func=list_candidates_tool,
            description='Show all candidates, list all candidates, display all candidates, or get a paginated list of all candidates (page=1 by default). Use this tool for queries like "show me all candidates", "list all candidates", "display all candidates".'
        ),
    ]
    # --- Dynamic tool registration example (future):
    # if user_profile and user_profile.get('role') == 'admin':
    #     tools.append(Tool(...))
    return initialize_agent(
        tools, llm, agent_type='openai-functions',
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

def run_agent(messages: List[Dict[str, Any]], session_id=None, model=None, auth_token=None, page=None, prompt=None, user_profile=None):
    # --- Memory: keep only the last 10 messages ---
    short_history = messages[-10:] if messages else []
    # --- Summarization: prepend a session summary if available ---
    summary = session_summaries.get(session_id) if session_id else None
    if summary:
        short_history = [{"role": "system", "content": summary}] + short_history
    try:
        if LANGGRAPH_AVAILABLE:
            agent = get_langgraph_agent(model, auth_token=auth_token, page=page, user_profile=user_profile)
            result = agent.invoke(AgentState(messages=short_history))
        else:
            agent = get_agent(model, auth_token=auth_token, page=page, user_profile=user_profile)
            result = agent.invoke({"messages": short_history})
        # Post-process: always return only the latest assistant message's content
        messages = []
        if not isinstance(result, dict) and hasattr(result, 'messages'):
            messages = result.messages
        elif isinstance(result, dict) and 'messages' in result:
            messages = result['messages']
        if messages:
            # Find the last assistant message
            for msg in reversed(messages):
                # If dict
                if isinstance(msg, dict) and msg.get('role') == 'assistant':
                    return msg.get('content', '')
                # If AIMessage or similar object
                if hasattr(msg, 'content'):
                    return msg.content
        # Fallback: handle candidate dicts or lists as before
        if isinstance(result, dict):
            if 'content' in result:
                return result['content']
            if 'output' in result:
                return result['output']
            if 'email' in result and ('name' in result or 'first_name' in result):
                return format_candidate(result)
            return str(result)
        if isinstance(result, list) and result and ('email' in result[0] or 'first_name' in result[0]):
            return format_candidate_list(result)
        return "Sorry, I couldn't generate a response."
    except Exception as e:
        # print("Exception in run_agent:", file=sys.stderr)
        traceback.print_exc()
        msg = str(e)
        if 'rate limit' in msg.lower() or '429' in msg or 'limit exceeded' in msg:
            return "⚠️ Sorry, our AI service is temporarily unavailable due to usage limits. Please try again later or contact support if this issue persists."
        return "Sorry, I couldn't complete your request due to an internal error. Please try again or contact support if the issue persists." 