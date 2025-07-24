# MCP Server (Model Context Protocol)

This is a Python-based agent server that connects your HR Django backend to an LLM (OpenRouter.ai) and exposes a /chat endpoint for conversational, tool-using AI.

## Features
- Receives chat messages from your client (ChatPage)
- Uses OpenRouter.ai LLM for reasoning
- Calls your Django backend as tools (get, update, delete candidate, analytics)
- Returns rich, grounded responses

## Setup

1. **Clone this directory** and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenRouter API key** (get one from https://openrouter.ai):
   ```bash
   export OPENROUTER_API_KEY=sk-...
   ```

3. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Ensure your Django HR backend is running** at `http://localhost:8000/api/`

## Usage

- POST to `/chat` with `{ "message": "Show me candidates added this month" }`
- The server will use the LLM and tools to answer, calling your Django backend as needed

## Integration

- Point your ChatPage or any client to `http://localhost:8000/chat` (or wherever this server runs)
- The agent will handle context, tool calls, and return conversational answers

## Extending
- Add more tools in `tools.py`
- Customize agent logic in `agent.py`

---

**This is a starting scaffold. You can extend it with more tools, memory, advanced context, or multi-turn workflows as needed!** 