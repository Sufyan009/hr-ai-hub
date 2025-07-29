#!/usr/bin/env python3
"""
Setup script for Azure OpenAI integration with HR Assistant Pro
"""

import os
import sys
from pathlib import Path

def create_env_file(env_path, template_content):
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write(template_content)
        print(f"✅ Created {env_path}")
    else:
        print(f"⚠️  {env_path} already exists")

def main():
    print("🚀 Setting up Azure OpenAI integration for HR Assistant Pro")
    print("=" * 60)
    
    # Get Azure credentials from user
    print("\n📝 Please provide your Azure OpenAI credentials:")
    azure_key = input("Azure OpenAI API Key: ").strip()
    azure_endpoint = input("Azure OpenAI Endpoint (e.g., https://your-resource.openai.azure.com/): ").strip()
    
    if not azure_key or not azure_endpoint:
        print("❌ Azure credentials are required!")
        return
    
    # MCP Server .env
    mcp_env_content = f"""# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY={azure_key}
AZURE_OPENAI_ENDPOINT={azure_endpoint}
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Existing OpenAI/OpenRouter (keep for fallback)
OPENAI_API_KEY=your_openai_key_here

# Django Backend URL
DJANGO_BACKEND_URL=http://localhost:8000/api

# Vector Database (Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=candidates

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
"""
    
    # Backend .env
    backend_env_content = f"""# Django Settings
DJANGO_SECRET_KEY=your_django_secret_key_here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY={azure_key}
AZURE_OPENAI_ENDPOINT={azure_endpoint}
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database
DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=media/
"""
    
    # Frontend .env
    frontend_env_content = f"""# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MCP_SERVER_URL=http://localhost:8001

# Azure OpenAI Configuration (for client-side calls if needed)
VITE_AZURE_OPENAI_API_KEY={azure_key}
VITE_AZURE_OPENAI_ENDPOINT={azure_endpoint}
VITE_AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Development Settings
VITE_DEV_MODE=true
"""
    
    # Create .env files
    print("\n📁 Creating environment files...")
    
    create_env_file("mcp_server/.env", mcp_env_content)
    create_env_file("backend/.env", backend_env_content)
    create_env_file("frontend/.env", frontend_env_content)
    
    print("\n✅ Environment files created successfully!")
    print("\n📋 Next steps:")
    print("1. Install dependencies: pip install -r mcp_server/requirements.txt")
    print("2. Start Qdrant vector database")
    print("3. Start Django backend: python backend/manage.py runserver")
    print("4. Start MCP server: uvicorn mcp_server.main:app --reload")
    print("5. Start frontend: npm run dev")
    print("\n🔗 Azure models available:")
    print("- azure/gpt-35-turbo")
    print("- azure/gpt-4")
    print("- azure/gpt-4-turbo")
    print("- azure/gpt-4o")
    print("- azure/gpt-4o-mini")

if __name__ == "__main__":
    main() 