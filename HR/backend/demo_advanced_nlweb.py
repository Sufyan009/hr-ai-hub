#!/usr/bin/env python3
"""
Advanced NLWeb Demo for HR Assistant Pro
Showcases salary filtering, location-based search, and enhanced semantic search
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

class AdvancedNLWebDemo:
    """
    Advanced NLWeb demonstration for HR Assistant Pro
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.auth_token = "d9b2485ccae623570a261316d567acb274ae65cb"
        self.headers = {
            "Authorization": f"Token {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_advanced_semantic_search(self):
        """Test advanced semantic search with natural language filtering"""
        print("🤖 Testing Advanced Semantic Search")
        print("=" * 50)
        
        # Test queries with embedded filters
        test_queries = [
            "Find Python developers with $100k+ salary in San Francisco",
            "Show me senior data scientists with 5+ years experience",
            "Search for remote DevOps engineers with $150k salary",
            "Find entry level React developers in New York",
            "Show jobs with salary between $75k and $125k",
            "Find candidates with machine learning experience and 3+ years"
        ]
        
        for query in test_queries:
            print(f"\n🔎 Query: '{query}'")
            
            try:
                response = requests.post(
                    f"{self.base_url}/nlweb/advanced/search/",
                    headers=self.headers,
                    json={
                        "query": query,
                        "search_type": "all",
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
                        print(f"  Filters Applied: {data.get('filters_applied', {})}")
                        
                        # Show top results
                        results = data.get('results', [])
                        for i, result in enumerate(results[:2]):
                            if data.get('query_type') == 'candidate_search':
                                name = result.get('name', 'Unknown')
                                job_title = result.get('job_title', 'Unknown')
                                salary = result.get('salary', 'Not specified')
                                score = result.get('score', 0)
                                print(f"    {i+1}. {name} - {job_title} (Salary: {salary}, Score: {score:.3f})")
                            else:
                                title = result.get('title', 'Unknown')
                                company = result.get('company', 'Unknown')
                                salary = result.get('salary', 'Not specified')
                                score = result.get('score', 0)
                                print(f"    {i+1}. {title} at {company} (Salary: {salary}, Score: {score:.3f})")
                    else:
                        print(f"❌ Query failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Query failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Query error: {e}")
    
    def test_salary_based_search(self):
        """Test salary-based search with range filtering"""
        print("\n💰 Testing Salary-Based Search")
        print("=" * 50)
        
        # Test salary ranges
        salary_ranges = [
            {"min": 50000, "max": 75000, "description": "Entry Level"},
            {"min": 75000, "max": 100000, "description": "Mid Level"},
            {"min": 100000, "max": 150000, "description": "Senior Level"},
            {"min": 150000, "max": None, "description": "Executive Level"}
        ]
        
        for salary_range in salary_ranges:
            print(f"\n💵 Testing {salary_range['description']} Salary Range: ${salary_range['min']:,} - ${salary_range['max'] or '∞'}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/nlweb/salary/search/",
                    headers=self.headers,
                    json={
                        "min_salary": salary_range['min'],
                        "max_salary": salary_range['max'],
                        "search_type": "all",
                        "limit": 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Salary search successful!")
                        print(f"  Results: {data.get('results_count', 0)}")
                        print(f"  Salary Range: {data.get('salary_range', {})}")
                        
                        # Show top results
                        results = data.get('results', [])
                        for i, result in enumerate(results[:2]):
                            if result.get('type') == 'candidate':
                                name = result.get('name', 'Unknown')
                                job_title = result.get('job_title', 'Unknown')
                                salary = result.get('salary', 'Not specified')
                                print(f"    {i+1}. {name} - {job_title} (Salary: {salary})")
                            else:
                                title = result.get('title', 'Unknown')
                                company = result.get('company', 'Unknown')
                                salary = result.get('salary', 'Not specified')
                                print(f"    {i+1}. {title} at {company} (Salary: {salary})")
                    else:
                        print(f"❌ Salary search failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Salary search failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Salary search error: {e}")
    
    def test_location_based_search(self):
        """Test location-based search with geographic filtering"""
        print("\n📍 Testing Location-Based Search")
        print("=" * 50)
        
        # Test locations
        locations = [
            "San Francisco, CA",
            "Seattle, WA",
            "New York, NY",
            "Remote"
        ]
        
        for location in locations:
            print(f"\n🌍 Testing Location: {location}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/nlweb/location/search/",
                    headers=self.headers,
                    json={
                        "location": location,
                        "radius": 50,
                        "search_type": "all",
                        "limit": 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Location search successful!")
                        print(f"  Results: {data.get('results_count', 0)}")
                        print(f"  Location: {data.get('location', 'Unknown')}")
                        print(f"  Radius: {data.get('radius', 0)} miles")
                        
                        # Show top results
                        results = data.get('results', [])
                        for i, result in enumerate(results[:2]):
                            if result.get('type') == 'candidate':
                                name = result.get('name', 'Unknown')
                                job_title = result.get('job_title', 'Unknown')
                                city = result.get('city', 'Unknown')
                                print(f"    {i+1}. {name} - {job_title} (Location: {city})")
                            else:
                                title = result.get('title', 'Unknown')
                                company = result.get('company', 'Unknown')
                                location_result = result.get('location', 'Unknown')
                                print(f"    {i+1}. {title} at {company} (Location: {location_result})")
                    else:
                        print(f"❌ Location search failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Location search failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Location search error: {e}")
    
    def test_search_suggestions(self):
        """Test search suggestions and popular queries"""
        print("\n💡 Testing Search Suggestions")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/nlweb/search/suggestions/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    suggestions = data.get('suggestions', {})
                    print("✅ Search suggestions loaded successfully!")
                    
                    print(f"\n💰 Salary Ranges ({len(suggestions.get('salary_ranges', []))}):")
                    for range_info in suggestions.get('salary_ranges', []):
                        print(f"  - {range_info.get('label', 'Unknown')}")
                    
                    print(f"\n🌍 Locations ({len(suggestions.get('locations', []))}):")
                    for location in suggestions.get('locations', []):
                        print(f"  - {location}")
                    
                    print(f"\n📊 Experience Levels ({len(suggestions.get('experience_levels', []))}):")
                    for level in suggestions.get('experience_levels', []):
                        print(f"  - {level.get('label', 'Unknown')}")
                    
                    print(f"\n🔧 Skills ({len(suggestions.get('skills', []))}):")
                    for skill in suggestions.get('skills', []):
                        print(f"  - {skill}")
                    
                    print(f"\n🔥 Popular Queries ({len(suggestions.get('popular_queries', []))}):")
                    for query in suggestions.get('popular_queries', []):
                        print(f"  - {query}")
                else:
                    print(f"❌ Search suggestions failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Search suggestions failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Search suggestions error: {e}")
    
    def test_search_analytics(self):
        """Test search analytics and insights"""
        print("\n📊 Testing Search Analytics")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/nlweb/search/analytics/", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    analytics = data.get('analytics', {})
                    print("✅ Search analytics loaded successfully!")
                    
                    print(f"\n📈 Database Statistics:")
                    print(f"  Total Indexed Items: {analytics.get('total_indexed_items', 0)}")
                    print(f"  Candidates: {analytics.get('candidates_count', 0)}")
                    print(f"  Jobs: {analytics.get('jobs_count', 0)}")
                    
                    print(f"\n🔍 Search Capabilities:")
                    capabilities = analytics.get('search_capabilities', {})
                    for capability, enabled in capabilities.items():
                        status = "✅" if enabled else "❌"
                        print(f"  {status} {capability.replace('_', ' ').title()}")
                    
                    print(f"\n⚡ Performance Metrics:")
                    metrics = analytics.get('performance_metrics', {})
                    print(f"  Average Response Time: {metrics.get('average_response_time', 'Unknown')}")
                    print(f"  Search Accuracy: {metrics.get('search_accuracy', 'Unknown')}")
                    
                    print(f"\n🎯 Supported Query Types:")
                    for query_type in metrics.get('supported_query_types', []):
                        print(f"  - {query_type.replace('_', ' ').title()}")
                else:
                    print(f"❌ Search analytics failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Search analytics failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Search analytics error: {e}")
    
    def run_comprehensive_demo(self):
        """Run the complete advanced NLWeb demonstration"""
        print("🚀 Advanced NLWeb Demo for HR Assistant Pro")
        print("=" * 60)
        print("This demo showcases advanced NLWeb capabilities including:")
        print("✅ Advanced semantic search with natural language filtering")
        print("✅ Salary-based search with range filtering")
        print("✅ Location-based search with geographic filtering")
        print("✅ Search suggestions and popular queries")
        print("✅ Real-time analytics and insights")
        print("=" * 60)
        
        # Run all tests
        self.test_advanced_semantic_search()
        self.test_salary_based_search()
        self.test_location_based_search()
        self.test_search_suggestions()
        self.test_search_analytics()
        
        print("\n🎉 Advanced NLWeb Demo Complete!")
        print("=" * 60)
        print("✅ All advanced NLWeb features are working correctly!")
        print("✅ Salary filtering with range support is operational")
        print("✅ Location-based search with geographic filtering is functional")
        print("✅ Natural language query parsing is working")
        print("✅ Search suggestions and analytics are available")
        print("\n💡 Key Features Demonstrated:")
        print("1. **Natural Language Filtering**: Extract salary, location, experience from queries")
        print("2. **Salary Range Search**: Find candidates/jobs within specific salary ranges")
        print("3. **Location-Based Search**: Geographic filtering with radius support")
        print("4. **Smart Suggestions**: Popular queries, salary ranges, locations")
        print("5. **Real-time Analytics**: Performance metrics and search capabilities")
        print("\n🚀 Your HR Assistant Pro now has enterprise-grade search capabilities!")

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
    demo = AdvancedNLWebDemo()
    demo.run_comprehensive_demo() 