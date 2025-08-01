#!/usr/bin/env python3
"""
Setup script for NLWeb Vector Database Integration
Helps configure environment variables for Azure OpenAI and Qdrant
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create a .env file in the HR/backend/ directory")
        return False
    
    # Read existing .env file
    env_vars = {}
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    return env_vars

def setup_vector_env():
    """Setup environment variables for vector database integration"""
    print("🚀 Setting up NLWeb Vector Database Integration")
    print("=" * 50)
    
    # Check existing .env file
    env_vars = check_env_file()
    if not env_vars:
        return False
    
    print("\n📋 Current environment variables:")
    for key, value in env_vars.items():
        if 'key' in key.lower() or 'secret' in key.lower():
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")
    
    # Required variables for vector integration
    required_vars = {
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI endpoint URL',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI API key',
        'AZURE_OPENAI_DEPLOYMENT': 'Azure OpenAI deployment name (default: text-embedding-ada-002)',
        'QDRANT_URL': 'Qdrant server URL (default: http://localhost:6333)',
        'QDRANT_API_KEY': 'Qdrant API key (optional)'
    }
    
    print("\n🔧 Required environment variables for vector integration:")
    missing_vars = []
    
    for var, description in required_vars.items():
        if var in env_vars:
            print(f"  ✅ {var}: {description}")
        else:
            print(f"  ❌ {var}: {description} (MISSING)")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing {len(missing_vars)} environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        
        print("\n📝 To add these variables:")
        print("1. Edit the .env file in HR/backend/")
        print("2. Add the missing variables:")
        
        for var in missing_vars:
            if var == 'AZURE_OPENAI_DEPLOYMENT':
                print(f"   {var}=text-embedding-ada-002")
            elif var == 'QDRANT_URL':
                print(f"   {var}=http://localhost:6333")
            elif var == 'QDRANT_API_KEY':
                print(f"   {var}=your_qdrant_api_key_here")
            else:
                print(f"   {var}=your_value_here")
        
        print("\n3. Restart the servers after adding the variables")
        return False
    else:
        print("\n✅ All required environment variables are configured!")
        return True

def check_qdrant_connection():
    """Check if Qdrant is accessible"""
    print("\n🔍 Checking Qdrant connection...")
    
    try:
        import requests
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        qdrant_api_key = os.getenv('QDRANT_API_KEY')
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # Try to get collections
        collections = client.get_collections()
        print(f"✅ Qdrant connection successful!")
        print(f"   URL: {qdrant_url}")
        print(f"   Collections: {len(collections.collections)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        print("\n💡 To start Qdrant locally:")
        print("1. Install Qdrant: pip install qdrant-client")
        print("2. Start Qdrant server: qdrant")
        print("3. Or use Docker: docker run -p 6333:6333 qdrant/qdrant")
        return False

def check_azure_openai_connection():
    """Check if Azure OpenAI is accessible"""
    print("\n🔍 Checking Azure OpenAI connection...")
    
    try:
        import openai
        
        # Set up Azure OpenAI
        openai.api_type = "azure"
        openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
        openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        openai.api_version = "2023-05-15"
        
        # Test with a simple embedding
        test_text = "Hello, world!"
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'text-embedding-ada-002')
        
        response = openai.Embedding.create(
            input=test_text,
            engine=deployment
        )
        
        embedding = response['data'][0]['embedding']
        print(f"✅ Azure OpenAI connection successful!")
        print(f"   Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"   Deployment: {deployment}")
        print(f"   Embedding dimensions: {len(embedding)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI connection failed: {e}")
        print("\n💡 To set up Azure OpenAI:")
        print("1. Create an Azure OpenAI resource")
        print("2. Deploy the text-embedding-ada-002 model")
        print("3. Get your endpoint and API key")
        print("4. Add them to your .env file")
        return False

def main():
    """Main setup function"""
    print("🚀 NLWeb Vector Database Setup")
    print("=" * 40)
    
    # Check environment variables
    env_ok = setup_vector_env()
    if not env_ok:
        print("\n❌ Please configure the missing environment variables first")
        return False
    
    # Check connections
    qdrant_ok = check_qdrant_connection()
    azure_ok = check_azure_openai_connection()
    
    if qdrant_ok and azure_ok:
        print("\n🎉 Vector database setup complete!")
        print("\n✅ Environment variables configured")
        print("✅ Qdrant connection working")
        print("✅ Azure OpenAI connection working")
        print("\n🚀 Ready to run vector NLWeb tests!")
        print("Run: python tests/test_vector_nlweb.py")
        return True
    else:
        print("\n❌ Setup incomplete. Please fix the connection issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 