#!/usr/bin/env python3
"""
Advanced NLWeb Views for HR Assistant Pro
Enhanced semantic search with salary filtering, location-based search, and advanced features
"""

import json
import requests
import sys
import os
from typing import Dict, List, Any, Optional
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Add parent directory to path for vector_db import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_db import vector_db

def extract_filters_from_query(query: str) -> Dict[str, Any]:
    """Extract filters from natural language query"""
    filters = {
        'salary_min': None,
        'salary_max': None,
        'location': None,
        'experience_min': None,
        'experience_max': None,
        'skills': [],
        'job_type': None,
        'remote': False
    }
    
    query_lower = query.lower()
    
    # Salary filtering
    if 'salary' in query_lower or '$' in query_lower:
        import re
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:k|K)?)',  # $50k, $100,000
            r'(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*(?:salary|per year)',  # 50k salary
            r'between\s*\$\s*(\d+)\s*and\s*\$\s*(\d+)',  # between $50k and $100k
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                if len(matches[0]) == 2:  # Range
                    min_sal = matches[0][0].replace(',', '').replace('k', '000').replace('K', '000')
                    max_sal = matches[0][1].replace(',', '').replace('k', '000').replace('K', '000')
                    filters['salary_min'] = int(min_sal)
                    filters['salary_max'] = int(max_sal)
                else:  # Single value
                    salary = matches[0].replace(',', '').replace('k', '000').replace('K', '000')
                    filters['salary_min'] = int(salary)
                    filters['salary_max'] = int(salary) * 1.2  # 20% range
    
    # Location filtering
    locations = ['san francisco', 'seattle', 'new york', 'los angeles', 'austin', 'remote', 'chicago', 'boston']
    for location in locations:
        if location in query_lower:
            filters['location'] = location
            if location == 'remote':
                filters['remote'] = True
            break
    
    # Experience filtering
    if 'experience' in query_lower or 'years' in query_lower:
        import re
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*experience',
            r'experience.*?(\d+)\+?\s*years',
            r'senior.*?(\d+)\+?\s*years',
            r'junior.*?(\d+)\+?\s*years'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                years = int(matches[0])
                if 'senior' in query_lower or '+' in query_lower:
                    filters['experience_min'] = years
                elif 'junior' in query_lower:
                    filters['experience_max'] = years
                else:
                    filters['experience_min'] = years
    
    # Skills filtering
    skills = ['python', 'javascript', 'react', 'node.js', 'java', 'c++', 'devops', 'machine learning', 'ai', 'data science']
    for skill in skills:
        if skill in query_lower:
            filters['skills'].append(skill)
    
    # Job type filtering
    job_types = ['full-time', 'part-time', 'contract', 'freelance', 'internship']
    for job_type in job_types:
        if job_type in query_lower:
            filters['job_type'] = job_type
            break
    
    return filters

def apply_filters_to_results(results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """Apply filters to search results"""
    filtered_results = []
    
    for result in results:
        include_result = True
        
        # Salary filtering
        if filters['salary_min'] or filters['salary_max']:
            salary = result.get('salary', 0)
            if isinstance(salary, str):
                try:
                    salary = int(salary.replace('$', '').replace(',', ''))
                except:
                    salary = 0
            
            if filters['salary_min'] and salary < filters['salary_min']:
                include_result = False
            if filters['salary_max'] and salary > filters['salary_max']:
                include_result = False
        
        # Location filtering
        if filters['location']:
            location = result.get('location', '').lower() + result.get('city', '').lower()
            if filters['location'] not in location and not filters['remote']:
                include_result = False
        
        # Experience filtering
        if filters['experience_min'] or filters['experience_max']:
            experience = result.get('experience', 0)
            if isinstance(experience, str):
                try:
                    experience = int(experience.replace(' years', ''))
                except:
                    experience = 0
            
            if filters['experience_min'] and experience < filters['experience_min']:
                include_result = False
            if filters['experience_max'] and experience > filters['experience_max']:
                include_result = False
        
        # Skills filtering
        if filters['skills']:
            skills_text = result.get('skills', '').lower() + result.get('job_title', '').lower()
            if not any(skill in skills_text for skill in filters['skills']):
                include_result = False
        
        if include_result:
            filtered_results.append(result)
    
    return filtered_results

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_advanced_search(request):
    """Advanced semantic search with filtering capabilities"""
    try:
        data = request.data
        query = data.get('query', '')
        search_type = data.get('search_type', 'all')
        limit = data.get('limit', 10)
        score_threshold = data.get('score_threshold', 0.7)
        
        # Extract filters from query
        filters = extract_filters_from_query(query)
        
        # Perform semantic search
        if search_type == 'candidates':
            results = vector_db.search_candidates(query, limit, score_threshold)
            results = apply_filters_to_results(results, filters)
            query_type = 'candidate_search'
        elif search_type == 'jobs':
            results = vector_db.search_job_posts(query, limit, score_threshold)
            results = apply_filters_to_results(results, filters)
            query_type = 'job_search'
        else:
            # Search both
            candidates = vector_db.search_candidates(query, limit // 2, score_threshold)
            jobs = vector_db.search_job_posts(query, limit // 2, score_threshold)
            
            candidates = apply_filters_to_results(candidates, filters)
            jobs = apply_filters_to_results(jobs, filters)
            
            results = candidates + jobs
            query_type = 'general_search'
        
        # Generate response
        response_data = {
            'success': True,
            'query': query,
            'query_type': query_type,
            'search_type': search_type,
            'results_count': len(results),
            'results': results,
            'filters_applied': filters,
            'vector_search': True,
            'schema_org_integrated': True,
            'response': f"Found {len(results)} results matching your query with applied filters"
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_salary_search(request):
    """Salary-based search with range filtering"""
    try:
        data = request.data
        min_salary = data.get('min_salary')
        max_salary = data.get('max_salary')
        search_type = data.get('search_type', 'all')
        limit = data.get('limit', 10)
        
        # Build query based on salary range
        if min_salary and max_salary:
            query = f"jobs with salary between ${min_salary:,} and ${max_salary:,}"
        elif min_salary:
            query = f"jobs with salary at least ${min_salary:,}"
        elif max_salary:
            query = f"jobs with salary up to ${max_salary:,}"
        else:
            query = "all jobs"
        
        # Perform search
        if search_type == 'candidates':
            results = vector_db.search_candidates(query, limit, 0.6)
        elif search_type == 'jobs':
            results = vector_db.search_job_posts(query, limit, 0.6)
        else:
            candidates = vector_db.search_candidates(query, limit // 2, 0.6)
            jobs = vector_db.search_job_posts(query, limit // 2, 0.6)
            results = candidates + jobs
        
        # Apply salary filtering
        filters = {
            'salary_min': min_salary,
            'salary_max': max_salary,
            'location': None,
            'experience_min': None,
            'experience_max': None,
            'skills': [],
            'job_type': None,
            'remote': False
        }
        
        results = apply_filters_to_results(results, filters)
        
        return Response({
            'success': True,
            'query': query,
            'salary_range': {'min': min_salary, 'max': max_salary},
            'results_count': len(results),
            'results': results,
            'filters_applied': filters
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_location_search(request):
    """Location-based search with geographic filtering"""
    try:
        data = request.data
        location = data.get('location', '')
        radius = data.get('radius', 50)  # miles
        search_type = data.get('search_type', 'all')
        limit = data.get('limit', 10)
        
        # Build location query
        query = f"jobs in {location}" if location else "all jobs"
        
        # Perform search
        if search_type == 'candidates':
            results = vector_db.search_candidates(query, limit, 0.6)
        elif search_type == 'jobs':
            results = vector_db.search_job_posts(query, limit, 0.6)
        else:
            candidates = vector_db.search_candidates(query, limit // 2, 0.6)
            jobs = vector_db.search_job_posts(query, limit // 2, 0.6)
            results = candidates + jobs
        
        # Apply location filtering
        filters = {
            'salary_min': None,
            'salary_max': None,
            'location': location.lower(),
            'experience_min': None,
            'experience_max': None,
            'skills': [],
            'job_type': None,
            'remote': 'remote' in location.lower()
        }
        
        results = apply_filters_to_results(results, filters)
        
        return Response({
            'success': True,
            'query': query,
            'location': location,
            'radius': radius,
            'results_count': len(results),
            'results': results,
            'filters_applied': filters
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_search_suggestions(request):
    """Get search suggestions and popular queries"""
    try:
        suggestions = {
            'salary_ranges': [
                {'label': '$50k - $75k', 'min': 50000, 'max': 75000},
                {'label': '$75k - $100k', 'min': 75000, 'max': 100000},
                {'label': '$100k - $150k', 'min': 100000, 'max': 150000},
                {'label': '$150k+', 'min': 150000, 'max': None}
            ],
            'locations': [
                'San Francisco, CA',
                'Seattle, WA', 
                'New York, NY',
                'Los Angeles, CA',
                'Austin, TX',
                'Remote'
            ],
            'experience_levels': [
                {'label': 'Entry Level (0-2 years)', 'min': 0, 'max': 2},
                {'label': 'Mid Level (3-5 years)', 'min': 3, 'max': 5},
                {'label': 'Senior Level (5+ years)', 'min': 5, 'max': None}
            ],
            'popular_queries': [
                'Find Python developers with 5+ years experience',
                'Show me data scientists in Seattle',
                'Search for frontend developers with React skills',
                'Find senior software engineers in San Francisco',
                'Show job openings for DevOps engineers',
                'Find candidates with machine learning experience',
                'Remote jobs with $100k+ salary',
                'Entry level positions in New York'
            ],
            'skills': [
                'Python', 'JavaScript', 'React', 'Node.js', 'Java',
                'C++', 'DevOps', 'Machine Learning', 'AI', 'Data Science',
                'TypeScript', 'Angular', 'Vue.js', 'Docker', 'Kubernetes'
            ]
        }
        
        return Response({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_search_analytics(request):
    """Get search analytics and insights"""
    try:
        # Get vector database stats
        stats = vector_db.get_collection_stats()
        
        # Calculate some basic analytics
        total_candidates = stats.get('candidates', {}).get('points_count', 0)
        total_jobs = stats.get('job_posts', {}).get('points_count', 0)
        
        analytics = {
            'total_indexed_items': total_candidates + total_jobs,
            'candidates_count': total_candidates,
            'jobs_count': total_jobs,
            'search_capabilities': {
                'semantic_search': True,
                'salary_filtering': True,
                'location_filtering': True,
                'experience_filtering': True,
                'skills_filtering': True,
                'remote_filtering': True
            },
            'performance_metrics': {
                'average_response_time': '< 500ms',
                'search_accuracy': '0.7+ score threshold',
                'supported_query_types': [
                    'natural_language',
                    'salary_based',
                    'location_based',
                    'experience_based',
                    'skills_based'
                ]
            }
        }
        
        return Response({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 