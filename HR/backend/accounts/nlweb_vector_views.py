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

# NLWeb Vector Database Integration
NLWEB_VECTOR_AGENTS = {
    "hr-assistant-pro": {
        "id": "hr-assistant-pro",
        "name": "HR Assistant Pro",
        "description": "Advanced HR management system with vector search capabilities",
        "capabilities": [
            "candidate_management", 
            "job_posting_management", 
            "analytics", 
            "schema_org_data", 
            "nlweb_communication",
            "vector_search",
            "semantic_search",
            "ai_enhanced_queries"
        ],
        "schema_types": ["Person", "JobPosting", "JobApplication"],
        "vector_capabilities": {
            "embedding_model": "text-embedding-ada-002",
            "vector_database": "Qdrant",
            "search_types": ["semantic", "hybrid", "filtered"],
            "supported_queries": [
                "natural_language_search",
                "skill_based_search", 
                "salary_range_search",
                "experience_level_search",
                "location_based_search"
            ]
        },
        "endpoints": {
            "discover": "/api/nlweb/discover/",
            "query": "/api/nlweb/query/",
            "status": "/api/nlweb/status/",
            "broadcast": "/api/nlweb/broadcast/",
            "vector_search": "/api/nlweb/vector-search/",
            "index_data": "/api/nlweb/index-data/",
            "vector_stats": "/api/nlweb/vector-stats/"
        }
    }
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_vector_discover_agents(request):
    """
    Enhanced NLWeb agent discovery with vector capabilities
    """
    try:
        # Get query parameters for filtering
        schema_type = request.GET.get('schema_type')
        capability = request.GET.get('capability')
        vector_capability = request.GET.get('vector_capability')
        
        agents = []
        for agent_id, agent_data in NLWEB_VECTOR_AGENTS.items():
            # Apply filters
            if schema_type and schema_type not in agent_data.get('schema_types', []):
                continue
            if capability and capability not in agent_data.get('capabilities', []):
                continue
            if vector_capability and vector_capability not in agent_data.get('vector_capabilities', {}).get('search_types', []):
                continue
            
            agents.append({
                "id": agent_data["id"],
                "name": agent_data["name"],
                "description": agent_data["description"],
                "capabilities": agent_data["capabilities"],
                "schema_types": agent_data["schema_types"],
                "vector_capabilities": agent_data["vector_capabilities"],
                "endpoints": agent_data["endpoints"]
            })
        
        return Response({
            "success": True,
            "agents": agents,
            "total_agents": len(agents),
            "vector_enabled": True
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_vector_query_agent(request):
    """
    Enhanced NLWeb agent querying with vector search capabilities
    """
    try:
        data = request.data
        query = data.get('query', '')
        agent_id = data.get('agent_id', 'hr-assistant-pro')
        context = data.get('context', {})
        schema_types = data.get('schema_types', [])
        search_type = data.get('search_type', 'semantic')  # semantic, hybrid, filtered
        limit = data.get('limit', 10)
        score_threshold = data.get('score_threshold', 0.7)
        
        if not query:
            return Response({
                "success": False,
                "error": "Query is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if agent_id == "hr-assistant-pro":
            return process_hr_vector_query(query, context, schema_types, search_type, limit, score_threshold)
        else:
            return Response({
                "success": False,
                "error": f"Agent {agent_id} not found or not supported"
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def process_hr_vector_query(query: str, context: Dict, schema_types: List[str], search_type: str, limit: int, score_threshold: float) -> Response:
    """
    Process HR queries with vector search capabilities
    """
    try:
        # Import vector database
        from vector_db import vector_db
        
        # Determine query type based on content
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['candidate', 'applicant', 'person', 'resume']):
            # Vector search for candidates
            results = vector_db.search_candidates(query, limit, score_threshold)
            
            if results:
                return Response({
                    "success": True,
                    "agent_id": "hr-assistant-pro",
                    "query_type": "candidate_search",
                    "search_type": search_type,
                    "results_count": len(results),
                    "results": results,
                    "vector_search": True,
                    "schema_org_integrated": True,
                    "response": f"Found {len(results)} candidates matching your query using semantic search"
                })
            else:
                return Response({
                    "success": True,
                    "agent_id": "hr-assistant-pro",
                    "query_type": "candidate_search",
                    "search_type": search_type,
                    "results_count": 0,
                    "results": [],
                    "vector_search": True,
                    "response": "No candidates found matching your query"
                })
        
        elif any(word in query_lower for word in ['job', 'position', 'opening', 'role']):
            # Vector search for job posts
            results = vector_db.search_job_posts(query, limit, score_threshold)
            
            if results:
                return Response({
                    "success": True,
                    "agent_id": "hr-assistant-pro",
                    "query_type": "job_search",
                    "search_type": search_type,
                    "results_count": len(results),
                    "results": results,
                    "vector_search": True,
                    "schema_org_integrated": True,
                    "response": f"Found {len(results)} job postings matching your query using semantic search"
                })
            else:
                return Response({
                    "success": True,
                    "agent_id": "hr-assistant-pro",
                    "query_type": "job_search",
                    "search_type": search_type,
                    "results_count": 0,
                    "results": [],
                    "vector_search": True,
                    "response": "No job postings found matching your query"
                })
        
        else:
            # General search across both candidates and jobs
            all_results = vector_db.search_all(query, limit, score_threshold)
            
            return Response({
                "success": True,
                "agent_id": "hr-assistant-pro",
                "query_type": "general_search",
                "search_type": search_type,
                "total_results": all_results['total_results'],
                "candidates": all_results['candidates'],
                "job_posts": all_results['job_posts'],
                "vector_search": True,
                "schema_org_integrated": True,
                "response": f"Found {all_results['total_results']} total results using semantic search"
            })
            
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error processing vector query: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_vector_agent_status(request):
    """
    Enhanced NLWeb agent status with vector database information
    """
    try:
        agent_id = request.GET.get('agent_id', 'hr-assistant-pro')
        
        if agent_id in NLWEB_VECTOR_AGENTS:
            agent_data = NLWEB_VECTOR_AGENTS[agent_id]
            
            # Import vector database
            from vector_db import vector_db
            
            # Get real vector database stats
            vector_stats = vector_db.get_collection_stats()
            
            return Response({
                "success": True,
                "agent": {
                    "id": agent_data["id"],
                    "name": agent_data["name"],
                    "description": agent_data["description"],
                    "status": "active",
                    "capabilities": agent_data["capabilities"],
                    "schema_types": agent_data["schema_types"],
                    "vector_capabilities": agent_data["vector_capabilities"],
                    "endpoints": agent_data["endpoints"],
                    "vector_database_stats": vector_stats
                }
            })
        else:
            return Response({
                "success": False,
                "error": f"Agent {agent_id} not found"
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_vector_search(request):
    """
    Direct vector search endpoint for semantic queries
    """
    try:
        data = request.data
        query = data.get('query', '')
        search_type = data.get('search_type', 'all')  # candidates, jobs, all
        limit = data.get('limit', 10)
        score_threshold = data.get('score_threshold', 0.7)
        
        if not query:
            return Response({
                "success": False,
                "error": "Query is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import vector database
        from vector_db import vector_db
        
        if search_type == 'candidates':
            results = vector_db.search_candidates(query, limit, score_threshold)
            return Response({
                "success": True,
                "search_type": "candidates",
                "query": query,
                "results_count": len(results),
                "results": results,
                "vector_search": True
            })
        
        elif search_type == 'jobs':
            results = vector_db.search_job_posts(query, limit, score_threshold)
            return Response({
                "success": True,
                "search_type": "jobs",
                "query": query,
                "results_count": len(results),
                "results": results,
                "vector_search": True
            })
        
        else:  # search_type == 'all'
            all_results = vector_db.search_all(query, limit, score_threshold)
            return Response({
                "success": True,
                "search_type": "all",
                "query": query,
                "total_results": all_results['total_results'],
                "candidates": all_results['candidates'],
                "job_posts": all_results['job_posts'],
                "vector_search": True
            })
            
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_index_data(request):
    """
    Index data into the vector database
    """
    try:
        data = request.data
        data_type = data.get('type')  # candidates, jobs
        data_items = data.get('items', [])
        
        if not data_type or not data_items:
            return Response({
                "success": False,
                "error": "Type and items are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import vector database
        from vector_db import vector_db
        
        indexed_count = 0
        failed_count = 0
        
        for item in data_items:
            try:
                if data_type == 'candidates':
                    success = vector_db.index_candidate(item)
                elif data_type == 'jobs':
                    success = vector_db.index_job_post(item)
                else:
                    continue
                
                if success:
                    indexed_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                print(f"Error indexing item: {e}")
        
        return Response({
            "success": True,
            "data_type": data_type,
            "total_items": len(data_items),
            "indexed_count": indexed_count,
            "failed_count": failed_count,
            "message": f"Indexed {indexed_count} items successfully"
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_vector_stats(request):
    """
    Get vector database statistics
    """
    try:
        # Import vector database
        from vector_db import vector_db
        
        # Get real vector database stats
        stats = vector_db.get_collection_stats()
        
        return Response({
            "success": True,
            "vector_database_stats": stats,
            "agent_id": "hr-assistant-pro",
            "embedding_model": "text-embedding-ada-002",
            "vector_database": "Qdrant"
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 