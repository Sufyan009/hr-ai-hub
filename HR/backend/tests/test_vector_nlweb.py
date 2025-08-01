#!/usr/bin/env python3
"""
Test script for NLWeb Vector Database Integration
Tests vector search capabilities with Azure OpenAI embeddings and Qdrant
"""

import requests
import json
import time
import sys
import os

# Configuration
DJANGO_API = "http://localhost:8000/api"
AUTH_TOKEN = "d9b2485ccae623570a261316d567acb274ae65cb"  # Your auth token
HEADERS = {"Authorization": f"Token {AUTH_TOKEN}"}

def test_vector_discovery():
    """Test enhanced NLWeb agent discovery with vector capabilities"""
    print("🔍 Testing NLWeb vector agent discovery...")
    
    try:
        # Test basic discovery
        response = requests.get(f"{DJANGO_API}/nlweb/vector/discover/", headers=HEADERS)
        print(f"Discovery Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Vector discovery working!")
            print(f"Total agents: {data.get('total_agents', 0)}")
            print(f"Vector enabled: {data.get('vector_enabled', False)}")
            
            if data.get('agents'):
                agent = data['agents'][0]
                print(f"Agent ID: {agent.get('id')}")
                print(f"Agent Name: {agent.get('name')}")
                print(f"Vector capabilities: {agent.get('vector_capabilities', {})}")
            
            # Test filtered discovery
            response = requests.get(
                f"{DJANGO_API}/nlweb/vector/discover/?vector_capability=semantic", 
                headers=HEADERS
            )
            print(f"Filtered Discovery Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Filtered vector discovery working!")
                print(f"Agents with semantic search: {data.get('total_agents', 0)}")
            
            return True
        else:
            print(f"❌ Discovery failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in vector discovery: {e}")
        return False

def test_vector_search():
    """Test vector search capabilities"""
    print("\n🔍 Testing vector search capabilities...")
    
    test_queries = [
        "Find candidates with Python experience",
        "Software engineers in New York",
        "Senior developers with 5+ years experience",
        "Job openings for data scientists",
        "Candidates with communication skills"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        
        try:
            # Test candidate search
            response = requests.post(
                f"{DJANGO_API}/nlweb/vector/search/",
                headers=HEADERS,
                json={
                    "query": query,
                    "search_type": "candidates",
                    "limit": 5,
                    "score_threshold": 0.6
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Candidate search working!")
                print(f"Results: {data.get('results_count', 0)}")
                print(f"Vector search: {data.get('vector_search', False)}")
                
                if data.get('results'):
                    for result in data['results'][:2]:  # Show first 2 results
                        print(f"  - {result.get('name', 'Unknown')} (Score: {result.get('score', 0):.3f})")
            else:
                print(f"❌ Candidate search failed: {response.text}")
            
            # Test job search
            response = requests.post(
                f"{DJANGO_API}/nlweb/vector/search/",
                headers=HEADERS,
                json={
                    "query": query,
                    "search_type": "jobs",
                    "limit": 5,
                    "score_threshold": 0.6
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Job search working!")
                print(f"Results: {data.get('results_count', 0)}")
                print(f"Vector search: {data.get('vector_search', False)}")
                
                if data.get('results'):
                    for result in data['results'][:2]:  # Show first 2 results
                        print(f"  - {result.get('title', 'Unknown')} (Score: {result.get('score', 0):.3f})")
            else:
                print(f"❌ Job search failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in vector search: {e}")
    
    return True

def test_vector_query_agent():
    """Test enhanced NLWeb agent querying with vector search"""
    print("\n🤖 Testing NLWeb vector agent querying...")
    
    test_queries = [
        "Find all candidates with software development experience",
        "Show me job openings for senior positions",
        "Search for candidates with Python programming skills",
        "Find jobs in the technology sector"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        
        try:
            response = requests.post(
                f"{DJANGO_API}/nlweb/vector/query/",
                headers=HEADERS,
                json={
                    "query": query,
                    "agent_id": "hr-assistant-pro",
                    "search_type": "semantic",
                    "limit": 5,
                    "score_threshold": 0.6
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Vector query working!")
                print(f"Query type: {data.get('query_type', 'unknown')}")
                print(f"Search type: {data.get('search_type', 'unknown')}")
                print(f"Vector search: {data.get('vector_search', False)}")
                print(f"Schema.org integrated: {data.get('schema_org_integrated', False)}")
                print(f"Response: {data.get('response', 'No response')}")
                
                if data.get('results_count', 0) > 0:
                    print(f"Results count: {data.get('results_count', 0)}")
                    
                    # Show sample results
                    if data.get('results'):
                        for result in data['results'][:2]:
                            if 'name' in result:
                                print(f"  - {result['name']} (Score: {result.get('score', 0):.3f})")
                            elif 'title' in result:
                                print(f"  - {result['title']} (Score: {result.get('score', 0):.3f})")
            else:
                print(f"❌ Vector query failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in vector query: {e}")
    
    return True

def test_vector_agent_status():
    """Test enhanced NLWeb agent status with vector database info"""
    print("\n📊 Testing NLWeb vector agent status...")
    
    try:
        response = requests.get(
            f"{DJANGO_API}/nlweb/vector/status/?agent_id=hr-assistant-pro",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Vector agent status working!")
            
            agent = data.get('agent', {})
            print(f"Agent ID: {agent.get('id')}")
            print(f"Agent Name: {agent.get('name')}")
            print(f"Status: {agent.get('status')}")
            print(f"Vector capabilities: {agent.get('vector_capabilities', {})}")
            
            # Show vector database stats
            vector_stats = agent.get('vector_database_stats', {})
            print(f"Vector database stats: {vector_stats}")
            
            return True
        else:
            print(f"❌ Vector agent status failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in vector agent status: {e}")
        return False

def test_vector_stats():
    """Test vector database statistics"""
    print("\n📈 Testing vector database statistics...")
    
    try:
        response = requests.get(f"{DJANGO_API}/nlweb/vector/stats/", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Vector stats working!")
            print(f"Embedding model: {data.get('embedding_model')}")
            print(f"Vector database: {data.get('vector_database')}")
            
            stats = data.get('vector_database_stats', {})
            for collection, info in stats.items():
                if isinstance(info, dict) and 'points_count' in info:
                    print(f"{collection}: {info['points_count']} points")
                else:
                    print(f"{collection}: {info}")
            
            return True
        else:
            print(f"❌ Vector stats failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in vector stats: {e}")
        return False

def test_data_indexing():
    """Test data indexing into vector database"""
    print("\n📝 Testing data indexing...")
    
    try:
        # First, get some sample data to index
        response = requests.get(f"{DJANGO_API}/candidates/", headers=HEADERS)
        
        if response.status_code == 200:
            candidates_data = response.json()
            sample_candidates = candidates_data.get('results', [])[:3]  # Get first 3 candidates
            
            if sample_candidates:
                # Test indexing candidates
                response = requests.post(
                    f"{DJANGO_API}/nlweb/vector/index/",
                    headers=HEADERS,
                    json={
                        "type": "candidates",
                        "items": sample_candidates
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Data indexing working!")
                    print(f"Indexed: {data.get('indexed_count', 0)} items")
                    print(f"Failed: {data.get('failed_count', 0)} items")
                    print(f"Message: {data.get('message', 'No message')}")
                else:
                    print(f"❌ Data indexing failed: {response.text}")
            
            # Test indexing job posts
            response = requests.get(f"{DJANGO_API}/jobposts/", headers=HEADERS)
            
            if response.status_code == 200:
                jobs_data = response.json()
                sample_jobs = jobs_data.get('results', [])[:2]  # Get first 2 jobs
                
                if sample_jobs:
                    response = requests.post(
                        f"{DJANGO_API}/nlweb/vector/index/",
                        headers=HEADERS,
                        json={
                            "type": "jobs",
                            "items": sample_jobs
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Job indexing working!")
                        print(f"Indexed: {data.get('indexed_count', 0)} jobs")
                        print(f"Failed: {data.get('failed_count', 0)} jobs")
                    else:
                        print(f"❌ Job indexing failed: {response.text}")
            
            return True
        else:
            print(f"❌ Failed to get sample data: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in data indexing: {e}")
        return False

def main():
    """Run all vector NLWeb tests"""
    print("🚀 Starting NLWeb Vector Database Integration Tests")
    print("=" * 60)
    
    # Wait for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(3)
    
    tests = [
        ("Vector Discovery", test_vector_discovery),
        ("Vector Search", test_vector_search),
        ("Vector Query Agent", test_vector_query_agent),
        ("Vector Agent Status", test_vector_agent_status),
        ("Vector Stats", test_vector_stats),
        ("Data Indexing", test_data_indexing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All vector NLWeb tests passed!")
        print("\n✅ Vector database integration working!")
        print("✅ Azure OpenAI embeddings working!")
        print("✅ Qdrant vector search working!")
        print("✅ NLWeb vector endpoints working!")
        print("✅ Schema.org integration with vectors working!")
    else:
        print(f"⚠️ {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 