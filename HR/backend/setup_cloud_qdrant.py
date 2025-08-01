#!/usr/bin/env python3
"""
Setup Cloud Qdrant Configuration
Helps configure and verify cloud Qdrant connection
"""

import os
import requests
import json
from dotenv import load_dotenv

# Your Qdrant API key
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.boPvXp6QzxD_QMJNjcvwaytIUNCJyRlbdsXKmsJY1iQ"

def setup_environment():
    """Setup environment variables for cloud Qdrant"""
    print("🔧 Setting up Cloud Qdrant Configuration")
    print("=" * 50)
    
    # Get the cloud URL from user
    print("Please provide your Qdrant cloud URL:")
    print("Common formats:")
    print("- https://your-cluster-id.qdrant.io")
    print("- https://your-cluster.cloud.qdrant.io")
    print("- https://api.qdrant.io")
    
    qdrant_url = input("\nEnter your Qdrant cloud URL: ").strip()
    
    if not qdrant_url:
        print("❌ No URL provided")
        return False
    
    # Test the connection
    print(f"\n🔍 Testing connection to: {qdrant_url}")
    
    headers = {
        "api-key": QDRANT_API_KEY,
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
            
            # Check for HR collections
            hr_collections = []
            for collection in collections.get('result', {}).get('collections', []):
                collection_name = collection.get('name', '')
                if 'hr_' in collection_name:
                    hr_collections.append(collection_name)
                    print(f"✅ Found HR collection: {collection_name}")
            
            if hr_collections:
                print(f"\n🎉 Your HR embeddings are ready!")
                print(f"Found {len(hr_collections)} HR collections: {', '.join(hr_collections)}")
                
                # Show sample data
                show_sample_data(qdrant_url, headers)
                
                # Save configuration
                save_configuration(qdrant_url)
                
                return True
            else:
                print("⚠️ No HR collections found. Your embeddings may be in a different cluster.")
                return False
                
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return False

def show_sample_data(qdrant_url, headers):
    """Show sample data from HR collections"""
    print("\n📋 Sample Data from HR Collections:")
    
    for collection_name in ['hr_candidates', 'hr_job_posts']:
        try:
            sample_url = f"{qdrant_url}/collections/{collection_name}/points/scroll"
            sample_params = {
                "limit": 2,
                "with_payload": True
            }
            
            response = requests.post(sample_url, headers=headers, json=sample_params)
            
            if response.status_code == 200:
                result = response.json()
                points = result.get('result', {}).get('points', [])
                
                if points:
                    print(f"\n📊 {collection_name}:")
                    for i, point in enumerate(points):
                        payload = point.get('payload', {})
                        if collection_name == 'hr_candidates':
                            name = f"{payload.get('first_name', '')} {payload.get('last_name', '')}"
                            email = payload.get('email', '')
                            job = payload.get('job_title_detail', {}).get('title', '')
                            print(f"   {i+1}. {name} - {email} ({job})")
                        elif collection_name == 'hr_job_posts':
                            title = payload.get('title', '')
                            location = payload.get('location', '')
                            print(f"   {i+1}. {title} - {location}")
                            
        except Exception as e:
            print(f"⚠️ Could not fetch sample data from {collection_name}: {e}")

def save_configuration(qdrant_url):
    """Save the configuration to a file"""
    config = {
        "QDRANT_URL": qdrant_url,
        "QDRANT_API_KEY": QDRANT_API_KEY
    }
    
    try:
        with open('qdrant_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n💾 Configuration saved to qdrant_config.json")
        
        print("\n📋 Environment Variables to Add:")
        print(f"QDRANT_URL={qdrant_url}")
        print(f"QDRANT_API_KEY={QDRANT_API_KEY}")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")

def test_vector_search(qdrant_url):
    """Test vector search functionality"""
    print("\n🔍 Testing Vector Search...")
    
    headers = {
        "api-key": QDRANT_API_KEY,
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
            print(f"✅ Found {len(points)} sample candidates")
            
            for i, point in enumerate(points[:3]):  # Show first 3
                payload = point.get('payload', {})
                name = f"{payload.get('first_name', '')} {payload.get('last_name', '')}"
                email = payload.get('email', '')
                job = payload.get('job_title_detail', {}).get('title', '')
                print(f"   {i+1}. {name}")
                print(f"      Email: {email}")
                print(f"      Job: {job}")
                
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing search: {e}")

def main():
    """Main function"""
    print("🚀 HR Assistant Pro - Cloud Qdrant Setup")
    print("=" * 50)
    
    print(f"🔑 Using API Key: {QDRANT_API_KEY[:20]}...")
    
    # Setup cloud Qdrant
    if setup_environment():
        print("\n🎉 Cloud Qdrant setup complete!")
        print("✅ Your embeddings are ready for use!")
        print("🔍 You can now use vector search in your NLWeb interface")
        print("🚀 Test with queries like 'Find Python developers' or 'Show me senior engineers'")
    else:
        print("\n❌ Setup failed. Please check your Qdrant cloud URL and try again.")

if __name__ == "__main__":
    main() 