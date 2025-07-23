# HR AI Hub

## Project Overview

**HR AI Hub** is a modern, full-stack platform designed to streamline and enhance human resources operations using AI. The project consists of:
- **MCP Server (Backend):** Handles business logic, AI processing, and data management.
- **ChatPage Client (Frontend):** A responsive, interactive chat interface for HR queries and management, acting as a client to the MCP server.

This architecture enables scalable, secure, and intelligent HR workflows for organizations of any size.

## Features
- AI-powered HR assistant chat interface
- Role-based authentication and user management
- Job posting and candidate management
- Real-time notifications
- Responsive, modern UI/UX
- Integration-ready for advanced AI models (OpenRouter, etc.)

## Tech Stack
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Axios
- **Backend:** Django, Django REST Framework, Python, PostgreSQL (or SQLite for dev)
- **AI Integration:** OpenRouter.ai API (pluggable)
- **Other:** Docker-ready, Git version control

## Getting Started

### Prerequisites
- Node.js & npm
- Python 3.x & pip
- (Optional) Docker

### Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/Sufyan009/talenthub.git
   cd talenthub/HR
   ```
2. **Backend:**
   ```sh
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```
3. **Frontend:**
   ```sh
   cd ../frontend
   npm install
   npm run dev
   ```
4. **Access the app:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## License

This project is licensed under the MIT License. 