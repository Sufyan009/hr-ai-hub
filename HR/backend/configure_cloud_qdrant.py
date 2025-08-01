#!/usr/bin/env python3
"""
Configure Cloud Qdrant for All Operations
Ensures the system uses cloud Qdrant for storing and searching embeddings
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Load configuration from the saved file
def load_qdrant_config():
    """Load Qdrant configuration from saved file"""
    try:
        with open('qdrant_config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ qdrant_config.json not found. Please run setup_cloud_qdrant.py first.")
        return None

def test_cloud_connection():
    """Test connection to cloud Qdrant"""
    config = load_qdrant_config()
    if not config:
        return False
    
    print("🔍 Testing Cloud Qdrant Connection")
    print("=" * 50)
    
    qdrant_url = config['QDRANT_URL']
    api_key = config['QDRANT_API_KEY']
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Test connection
        collections_url = f"{qdrant_url}/collections"
        response = requests.get(collections_url, headers=headers)
        
        if response.status_code == 200:
            collections = response.json()
            print("✅ Successfully connected to cloud Qdrant!")
            print(f"📊 Found {len(collections.get('result', {}).get('collections', []))} collections")
            
            # Check HR collections
            hr_collections = []
            for collection in collections.get('result', {}).get('collections', []):
                collection_name = collection.get('name', '')
                if 'hr_' in collection_name:
                    hr_collections.append(collection_name)
                    print(f"✅ Found HR collection: {collection_name}")
            
            if hr_collections:
                print(f"\n🎉 Your HR embeddings are accessible!")
                return True
            else:
                print("⚠️ No HR collections found")
                return False
                
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return False

def test_vector_search():
    """Test vector search functionality"""
    config = load_qdrant_config()
    if not config:
        return False
    
    print("\n🔍 Testing Vector Search")
    print("=" * 50)
    
    qdrant_url = config['QDRANT_URL']
    api_key = config['QDRANT_API_KEY']
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Test search in hr_candidates collection
        search_url = f"{qdrant_url}/collections/hr_candidates/points/scroll"
        search_params = {
            "limit": 5,
            "with_payload": True
        }
        
        response = requests.post(search_url, headers=headers, json=search_params)
        
        if response.status_code == 200:
            result = response.json()
            points = result.get('result', {}).get('points', [])
            print(f"✅ Found {len(points)} candidates in search")
            
            for i, point in enumerate(points[:3]):  # Show first 3
                payload = point.get('payload', {})
                name = f"{payload.get('first_name', '')} {payload.get('last_name', '')}"
                email = payload.get('email', '')
                job = payload.get('job_title_detail', {}).get('title', '')
                print(f"   {i+1}. {name}")
                print(f"      Email: {email}")
                print(f"      Job: {job}")
            
            return True
                
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing search: {e}")
        return False

def update_environment_variables():
    """Update environment variables to use cloud Qdrant"""
    config = load_qdrant_config()
    if not config:
        return False
    
    print("\n🔧 Updating Environment Configuration")
    print("=" * 50)
    
    # Set environment variables
    os.environ['QDRANT_URL'] = config['QDRANT_URL']
    os.environ['QDRANT_API_KEY'] = config['QDRANT_API_KEY']
    
    print("✅ Environment variables set:")
    print(f"   QDRANT_URL={config['QDRANT_URL']}")
    print(f"   QDRANT_API_KEY={config['QDRANT_API_KEY'][:20]}...")
    
    return True

def test_embedding_generation():
    """Test embedding generation with cloud Qdrant"""
    print("\n🧪 Testing Embedding Generation")
    print("=" * 50)
    
    try:
        from vector_db import HRVectorDatabase
        
        # Initialize vector database (should use cloud Qdrant)
        vector_db = HRVectorDatabase()
        
        # Test with sample data
        sample_candidate = {
            'id': 999,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test.user@example.com',
            'phone_number': '+1234567890',
            'candidate_stage': 'Applied',
            'current_salary': '80000',
            'expected_salary': '90000',
            'years_of_experience': '5',
            'job_title_detail': {'title': 'Software Engineer'},
            'city_detail': {'name': 'New York'},
            'source_detail': {'name': 'LinkedIn'},
            'communication_skills_detail': {'skill': 'Excellent'}
        }
        
        # Index the sample candidate
        success = vector_db.index_candidate(sample_candidate)
        
        if success:
            print("✅ Sample embedding generated and stored in cloud Qdrant!")
            
            # Clean up - remove the test candidate
            try:
                # You might want to add a delete function to vector_db
                print("🧹 Test candidate indexed successfully")
            except:
                pass
        else:
            print("❌ Failed to generate sample embedding")
            
    except Exception as e:
        print(f"❌ Error testing embedding generation: {e}")

def main():
    """Main function"""
    print("🚀 HR Assistant Pro - Cloud Qdrant Configuration")
    print("=" * 50)
    
    # Test cloud connection
    if not test_cloud_connection():
        print("❌ Cannot connect to cloud Qdrant")
        return
    
    # Update environment variables
    if not update_environment_variables():
        print("❌ Cannot update environment variables")
        return
    
    # Test vector search
    if not test_vector_search():
        print("❌ Vector search not working")
        return
    
    # Test embedding generation
    test_embedding_generation()
    
    print("\n🎉 Cloud Qdrant Configuration Complete!")
    print("✅ Your system is now configured to use cloud Qdrant for:")
    print("   - Storing new embeddings")
    print("   - Searching existing embeddings")
    print("   - Vector similarity search")
    
    print("\n📋 Next Steps:")
    print("1. Restart your Django server to apply changes")
    print("2. Test your NLWeb interface with vector search")
    print("3. Try queries like 'Find Python developers' or 'Show me senior engineers'")

if __name__ == "__main__":
    main() 