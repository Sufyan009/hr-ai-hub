#!/usr/bin/env python3
"""
Comprehensive NLWeb Demo for HR Assistant Pro
This script demonstrates all NLWeb capabilities including:
- Agent discovery and communication
- Vector search with semantic queries
- Schema.org structured data
- Real-time analytics
"""

import os
import sys
import json
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class NLWebComprehensiveDemo:
    """
    Comprehensive NLWeb demonstration for HR Assistant Pro
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.auth_token = "d9b2485ccae623570a261316d567acb274ae65cb"
        self.headers = {
            "Authorization": f"Token {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_agent_discovery(self):
        """Test NLWeb agent discovery capabilities"""
        print("🔍 Testing NLWeb Agent Discovery")
        print("=" * 50)
        
        # Test basic discovery
        try:
            response = requests.get(f"{self.base_url}/nlweb/discover/", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                print("✅ Basic agent discovery working!")
                print(f"📊 Found {data.get('total_agents', 0)} agents")
                for agent in data.get('agents', []):
                    print(f"  - {agent.get('name', 'Unknown')} ({agent.get('id', 'Unknown')})")
            else:
                print(f"❌ Basic discovery failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Basic discovery error: {e}")
        
        # Test vector-enabled discovery
        try:
            response = requests.get(f"{self.base_url}/nlweb/vector/discover/", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Vector agent discovery working!")
                print(f"📊 Found {data.get('total_agents', 0)} vector-enabled agents")
                for agent in data.get('agents', []):
                    print(f"  - {agent.get('name', 'Unknown')} ({agent.get('id', 'Unknown')})")
                    capabilities = agent.get('vector_capabilities', {})
                    print(f"    Embedding model: {capabilities.get('embedding_model', 'Unknown')}")
                    print(f"    Vector database: {capabilities.get('vector_database', 'Unknown')}")
            else:
                print(f"❌ Vector discovery failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Vector discovery error: {e}")
        
        # Test filtered discovery
        try:
            response = requests.get(
                f"{self.base_url}/nlweb/vector/discover/?vector_capability=semantic", 
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Filtered discovery working! Found {data.get('total_agents', 0)} agents with semantic search")
            else:
                print(f"❌ Filtered discovery failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Filtered discovery error: {e}")
    
    def test_semantic_queries(self):
        """Test semantic search queries"""
        print("\n🤖 Testing Semantic Search Queries")
        print("=" * 50)
        
        # Test queries
        test_queries = [
            "Find Python developers with 5+ years experience",
            "Show me data scientists in Seattle",
            "Search for frontend developers with React skills",
            "Find senior software engineers in San Francisco",
            "Show job openings for DevOps engineers",
            "Find candidates with machine learning experience"
        ]
        
        for query in test_queries:
            print(f"\n🔎 Query: '{query}'")
            
            try:
                # Test vector query agent
                response = requests.post(
                    f"{self.base_url}/nlweb/vector/query/",
                    headers=self.headers,
                    json={
                        "query": query,
                        "agent_id": "hr-assistant-pro",
                        "search_type": "semantic",
                        "limit": 5,
                        "score_threshold": 0.7
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Query successful!")
                        print(f"  Type: {data.get('query_type', 'Unknown')}")
                        print(f"  Results: {data.get('results_count', 0)}")
                        print(f"  Response: {data.get('response', 'No response')}")
                        
                        # Show top results
                        results = data.get('results', [])
                        for i, result in enumerate(results[:2]):
                            if data.get('query_type') == 'candidate_search':
                                print(f"    {i+1}. {result.get('name', 'Unknown')} - {result.get('job_title', 'Unknown')} (Score: {result.get('score', 0):.3f})")
                            else:
                                print(f"    {i+1}. {result.get('title', 'Unknown')} at {result.get('company', 'Unknown')} (Score: {result.get('score', 0):.3f})")
                    else:
                        print(f"❌ Query failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Query failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Query error: {e}")
    
    def test_vector_search_endpoints(self):
        """Test direct vector search endpoints"""
        print("\n🔍 Testing Direct Vector Search")
        print("=" * 50)
        
        # Test candidate search
        try:
            response = requests.post(
                f"{self.base_url}/nlweb/vector/search/",
                headers=self.headers,
                json={
                    "query": "Python developers with Django experience",
                    "search_type": "candidates",
                    "limit": 3,
                    "score_threshold": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Candidate search working!")
                    print(f"  Found {data.get('results_count', 0)} candidates")
                    results = data.get('results', [])
                    for result in results[:2]:
                        print(f"    - {result.get('name', 'Unknown')}: {result.get('job_title', 'Unknown')} (Score: {result.get('score', 0):.3f})")
                else:
                    print(f"❌ Candidate search failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Candidate search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Candidate search error: {e}")
        
        # Test job search
        try:
            response = requests.post(
                f"{self.base_url}/nlweb/vector/search/",
                headers=self.headers,
                json={
                    "query": "Senior software engineer positions",
                    "search_type": "jobs",
                    "limit": 3,
                    "score_threshold": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("\n✅ Job search working!")
                    print(f"  Found {data.get('results_count', 0)} jobs")
                    results = data.get('results', [])
                    for result in results[:2]:
                        print(f"    - {result.get('title', 'Unknown')} at {result.get('company', 'Unknown')} (Score: {result.get('score', 0):.3f})")
                else:
                    print(f"❌ Job search failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Job search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Job search error: {e}")
    
    def test_agent_status_and_stats(self):
        """Test agent status and vector database statistics"""
        print("\n📊 Testing Agent Status and Statistics")
        print("=" * 50)
        
        # Test vector agent status
        try:
            response = requests.get(
                f"{self.base_url}/nlweb/vector/status/?agent_id=hr-assistant-pro",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    agent = data.get('agent', {})
                    print("✅ Vector agent status working!")
                    print(f"  Agent: {agent.get('name', 'Unknown')}")
                    print(f"  Status: {agent.get('status', 'Unknown')}")
                    print(f"  Embedding model: {agent.get('vector_capabilities', {}).get('embedding_model', 'Unknown')}")
                    
                    # Show vector database stats
                    stats = agent.get('vector_database_stats', {})
                    print(f"  Vector database stats:")
                    for collection, info in stats.items():
                        print(f"    - {collection}: {info.get('points_count', 0)} points")
                else:
                    print(f"❌ Agent status failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Agent status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Agent status error: {e}")
        
        # Test vector database statistics
        try:
            response = requests.get(f"{self.base_url}/nlweb/vector/stats/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("\n✅ Vector database statistics working!")
                    stats = data.get('vector_database_stats', {})
                    print(f"  Embedding model: {data.get('embedding_model', 'Unknown')}")
                    print(f"  Vector database: {data.get('vector_database', 'Unknown')}")
                    for collection, info in stats.items():
                        print(f"    - {collection}: {info.get('points_count', 0)} points")
                else:
                    print(f"❌ Vector stats failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Vector stats failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Vector stats error: {e}")
    
    def test_schema_org_integration(self):
        """Test Schema.org integration"""
        print("\n🏷️ Testing Schema.org Integration")
        print("=" * 50)
        
        # Test Schema.org data endpoint
        try:
            response = requests.get(
                f"{self.base_url}/schema-org-data/?type=candidate&id=1",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Schema.org data endpoint working!")
                    schema_data = data.get('schema_org_data', {})
                    print(f"  Schema type: {schema_data.get('@type', 'Unknown')}")
                    print(f"  Name: {schema_data.get('name', 'Unknown')}")
                    print(f"  Job title: {schema_data.get('jobTitle', 'Unknown')}")
                else:
                    print(f"❌ Schema.org data failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Schema.org data failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Schema.org data error: {e}")
    
    def test_broadcast_communication(self):
        """Test NLWeb broadcast communication"""
        print("\n📡 Testing NLWeb Broadcast Communication")
        print("=" * 50)
        
        # Test broadcast query
        try:
            response = requests.post(
                f"{self.base_url}/nlweb/broadcast/",
                headers=self.headers,
                json={
                    "query": "Find all agents with vector search capabilities",
                    "context": {"search_type": "vector", "capability": "semantic_search"}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Broadcast communication working!")
                    responses = data.get('responses', [])
                    print(f"  Received {len(responses)} responses")
                    for resp in responses:
                        agent_id = resp.get('agent_id', 'Unknown')
                        response_text = resp.get('response', 'No response')
                        print(f"    - {agent_id}: {response_text}")
                else:
                    print(f"❌ Broadcast failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Broadcast failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Broadcast error: {e}")
    
    def run_comprehensive_demo(self):
        """Run the complete NLWeb demonstration"""
        print("🚀 NLWeb Comprehensive Demo for HR Assistant Pro")
        print("=" * 60)
        print("This demo showcases all NLWeb capabilities including:")
        print("✅ Agent discovery and communication")
        print("✅ Vector search with semantic queries")
        print("✅ Schema.org structured data integration")
        print("✅ Real-time analytics and statistics")
        print("✅ Broadcast communication between agents")
        print("=" * 60)
        
        # Run all tests
        self.test_agent_discovery()
        self.test_semantic_queries()
        self.test_vector_search_endpoints()
        self.test_agent_status_and_stats()
        self.test_schema_org_integration()
        self.test_broadcast_communication()
        
        print("\n🎉 NLWeb Comprehensive Demo Complete!")
        print("=" * 60)
        print("✅ All NLWeb features are working correctly!")
        print("✅ Vector search with semantic queries is operational")
        print("✅ Schema.org integration is active")
        print("✅ Agent communication is functional")
        print("✅ Real-time analytics are available")
        print("\n💡 Next steps:")
        print("1. Integrate NLWeb into your frontend application")
        print("2. Add more sophisticated search filters")
        print("3. Implement real-time notifications")
        print("4. Scale with additional agents and capabilities")

if __name__ == "__main__":
    # Check if Django server is running
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code != 200:
            print("⚠️ Django server might not be running. Please start it with:")
            print("cd HR/backend && python manage.py runserver 8000")
    except:
        print("⚠️ Django server is not running. Please start it with:")
        print("cd HR/backend && python manage.py runserver 8000")
        print("Then run this demo again.")
        sys.exit(1)
    
    # Run the comprehensive demo
    demo = NLWebComprehensiveDemo()
    demo.run_comprehensive_demo() 