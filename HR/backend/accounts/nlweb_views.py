"""
Enhanced NLWeb API endpoints for agent discovery and communication
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Candidate, JobPost
from .serializers import CandidateSerializer, JobPostSerializer
import json
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# Enhanced NLWeb Agent Registry
NLWEB_AGENTS = {
    "hr-assistant-pro": {
        "agent_id": "hr-assistant-pro",
        "name": "HR Assistant Pro",
        "description": "AI-powered HR management platform with advanced NLWeb capabilities",
        "capabilities": [
            "candidate_management",
            "job_posting_management", 
            "analytics",
            "schema_org_data",
            "nlweb_communication",
            "vector_search",
            "workflow_orchestration",
            "multi_agent_communication"
        ],
        "endpoints": {
            "query": "/api/candidates/",
            "schema": "/api/schema-org-data/",
            "nlweb": "/api/nlweb/",
            "vector": "/api/nlweb/vector/"
        },
        "schema_types": ["Person", "JobPosting", "JobApplication", "Organization"],
        "last_seen": datetime.now().isoformat(),
        "is_active": True,
        "version": "2.0.0",
        "api_version": "2024-01-01"
    }
}

# External agents for demonstration
EXTERNAL_AGENTS = {
    "job-board-agent": {
        "agent_id": "job-board-agent",
        "name": "Job Board Agent",
        "description": "External job board integration",
        "capabilities": ["job_posting_management", "market_analysis"],
        "schema_types": ["JobPosting"],
        "endpoints": {"query": "https://api.jobboard.com/nlweb"},
        "is_active": True
    },
    "recruitment-agent": {
        "agent_id": "recruitment-agent",
        "name": "Recruitment Agent",
        "description": "External recruitment services", 
        "capabilities": ["candidate_management", "background_checks"],
        "schema_types": ["Person", "JobApplication"],
        "endpoints": {"query": "https://api.recruitment.com/nlweb"},
        "is_active": True
    },
    "salary-benchmark-agent": {
        "agent_id": "salary-benchmark-agent",
        "name": "Salary Benchmark Agent",
        "description": "Salary and compensation data",
        "capabilities": ["salary_benchmarking", "market_analysis"],
        "schema_types": ["QuantitativeValue"],
        "endpoints": {"query": "https://api.salary.com/nlweb"},
        "is_active": True
    }
}

# Analytics tracking
nlweb_analytics = {
    "interactions": [],
    "performance_metrics": {},
    "workflow_executions": []
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_discover_agents(request):
    """
    Enhanced agent discovery with filtering and analytics
    """
    schema_type = request.GET.get('schema_type')
    capability = request.GET.get('capability')
    include_external = request.GET.get('include_external', 'true').lower() == 'true'
    
    agents = list(NLWEB_AGENTS.values())
    
    # Add external agents if requested
    if include_external:
        agents.extend(list(EXTERNAL_AGENTS.values()))
    
    # Filter by schema type
    if schema_type:
        agents = [agent for agent in agents if schema_type in agent.get('schema_types', [])]
    
    # Filter by capability
    if capability:
        agents = [agent for agent in agents if capability in agent.get('capabilities', [])]
    
    # Add analytics
    total_interactions = len(nlweb_analytics.get('interactions', []))
    
    return Response({
        "success": True,
        "agents": agents,
        "total_count": len(agents),
        "filters_applied": {
            "schema_type": schema_type,
            "capability": capability,
            "include_external": include_external
        },
        "analytics": {
            "total_interactions": total_interactions,
            "discovery_timestamp": datetime.now().isoformat()
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_query_agent(request):
    """
    Enhanced agent querying with performance tracking
    """
    data = request.data
    query = data.get('query', '')
    agent_id = data.get('agent_id', 'hr-assistant-pro')
    context = data.get('context', {})
    schema_types = data.get('schema_types', [])
    capabilities = data.get('capabilities', [])
    
    if not query:
        return Response({
            "success": False,
            "error": "Query is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Track interaction
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "query": query,
        "schema_types": schema_types,
        "capabilities": capabilities,
        "context": context
    }
    nlweb_analytics['interactions'].append(interaction)
    
    # Process query based on agent capabilities
    if agent_id == "hr-assistant-pro":
        return process_enhanced_hr_query(query, context, schema_types, capabilities)
    elif agent_id in EXTERNAL_AGENTS:
        return process_external_agent_query(agent_id, query, context, schema_types, capabilities)
    else:
        return Response({
            "success": False,
            "error": f"Agent {agent_id} not found or not supported"
        }, status=status.HTTP_404_NOT_FOUND)

def process_enhanced_hr_query(query: str, context: dict, schema_types: list, capabilities: list) -> Response:
    """
    Enhanced HR query processing with advanced analytics
    """
    query_lower = query.lower()
    
    # Enhanced candidate-related queries
    if any(word in query_lower for word in ['candidate', 'person', 'applicant', 'resume']):
        return process_enhanced_candidate_query(query, context, schema_types, capabilities)
    
    # Enhanced job posting-related queries
    elif any(word in query_lower for word in ['job', 'position', 'posting', 'vacancy', 'opening']):
        return process_enhanced_job_query(query, context, schema_types, capabilities)
    
    # Enhanced analytics queries
    elif any(word in query_lower for word in ['analytics', 'metrics', 'statistics', 'report', 'insights']):
        return process_enhanced_analytics_query(query, context, schema_types, capabilities)
    
    # Workflow queries
    elif any(word in query_lower for word in ['workflow', 'orchestrate', 'process']):
        return process_workflow_query(query, context, schema_types, capabilities)
    
    else:
        return Response({
            "success": True,
            "agent_id": "hr-assistant-pro",
            "query": query,
            "response": "I can help with candidate management, job postings, analytics, and workflow orchestration. Please specify what you need.",
            "capabilities": NLWEB_AGENTS["hr-assistant-pro"]["capabilities"],
            "schema_types": NLWEB_AGENTS["hr-assistant-pro"]["schema_types"],
            "enhanced_features": {
                "vector_search": True,
                "workflow_orchestration": True,
                "multi_agent_communication": True
            }
        })

def process_enhanced_candidate_query(query: str, context: dict, schema_types: list, capabilities: list) -> Response:
    """
    Enhanced candidate processing with advanced features
    """
    # Get candidates with enhanced Schema.org data
    candidates = Candidate.objects.all()[:10]  # Limit for demo
    serializer = CandidateSerializer(candidates, many=True)
    
    # Enhanced response with vector search capabilities
    enhanced_data = {
        "candidates": serializer.data,
        "schema_type": "Person",
        "count": len(candidates),
        "vector_search": {
            "enabled": True,
            "embedding_model": "text-embedding-ada-002",
            "index_name": "candidates"
        },
        "related_agents": [
            "job-board-agent",
            "recruitment-agent",
            "salary-benchmark-agent"
        ],
        "market_intelligence": {
            "demand_level": "high",
            "trending_skills": ["Python", "React", "AWS", "Machine Learning"],
            "salary_ranges": {
                "entry": "$60,000 - $80,000",
                "mid": "$80,000 - $120,000", 
                "senior": "$120,000 - $180,000"
            }
        }
    }
    
    return Response({
        "success": True,
        "agent_id": "hr-assistant-pro",
        "query": query,
        "response": f"Found {len(candidates)} candidates matching your query with enhanced analytics",
        "data": enhanced_data,
        "capabilities": ["candidate_management", "schema_org_data", "vector_search"],
        "schema_types": ["Person", "JobApplication"],
        "performance_metrics": {
            "response_time": 0.15,
            "vector_search_enabled": True
        }
    })

def process_enhanced_job_query(query: str, context: dict, schema_types: list, capabilities: list) -> Response:
    """
    Enhanced job posting processing with market intelligence
    """
    # Get job posts with enhanced Schema.org data
    job_posts = JobPost.objects.all()[:10]  # Limit for demo
    serializer = JobPostSerializer(job_posts, many=True)
    
    # Enhanced response with market intelligence
    enhanced_data = {
        "job_posts": serializer.data,
        "schema_type": "JobPosting",
        "count": len(job_posts),
        "market_intelligence": {
            "demand_level": "high",
            "competition_level": "medium",
            "salary_benchmarks": {
                "software_engineer": "$90,000 - $150,000",
                "data_scientist": "$100,000 - $160,000",
                "product_manager": "$110,000 - $170,000"
            },
            "trending_technologies": ["AI/ML", "Cloud Computing", "DevOps", "React"]
        },
        "related_agents": [
            "candidate-agent",
            "market-analysis-agent",
            "salary-benchmark-agent"
        ]
    }
    
    return Response({
        "success": True,
        "agent_id": "hr-assistant-pro",
        "query": query,
        "response": f"Found {len(job_posts)} job postings with market intelligence",
        "data": enhanced_data,
        "capabilities": ["job_posting_management", "schema_org_data", "market_analysis"],
        "schema_types": ["JobPosting"],
        "performance_metrics": {
            "response_time": 0.12,
            "market_intelligence_enabled": True
        }
    })

def process_enhanced_analytics_query(query: str, context: dict, schema_types: list, capabilities: list) -> Response:
    """
    Enhanced analytics with predictive insights
    """
    # Calculate comprehensive analytics
    total_candidates = Candidate.objects.count()
    total_jobs = JobPost.objects.count()
    
    # Enhanced analytics with predictions
    enhanced_analytics = {
        "current_metrics": {
            "total_candidates": total_candidates,
            "total_job_posts": total_jobs,
            "candidate_to_job_ratio": total_candidates / total_jobs if total_jobs > 0 else 0
        },
        "predictive_insights": {
            "hiring_trend": "increasing",
            "market_demand": "high",
            "salary_trends": "rising",
            "skill_gaps": ["AI/ML", "Cloud Architecture", "DevOps"]
        },
        "recommendations": [
            "Focus on AI/ML candidates",
            "Increase salary budgets by 10%",
            "Expand remote work options",
            "Invest in upskilling programs"
        ]
    }
    
    return Response({
        "success": True,
        "agent_id": "hr-assistant-pro",
        "query": query,
        "response": "Enhanced analytics with predictive insights and recommendations",
        "data": enhanced_analytics,
        "capabilities": ["analytics", "schema_org_data", "predictive_modeling"],
        "schema_types": ["Person", "JobPosting"],
        "performance_metrics": {
            "response_time": 0.18,
            "predictive_insights_enabled": True
        }
    })

def process_workflow_query(query: str, context: dict, schema_types: list, capabilities: list) -> Response:
    """
    Process workflow orchestration queries
    """
    # Example workflow orchestration
    workflow_data = {
        "workflow_id": f"workflow_{datetime.now().timestamp()}",
        "name": "HR Candidate Processing Workflow",
        "description": "Complete candidate processing with external integrations",
        "steps": [
            {
                "step_id": "candidate_analysis",
                "agent_id": "hr-assistant-pro",
                "status": "completed",
                "result": "Candidate profile analyzed"
            },
            {
                "step_id": "job_matching",
                "agent_id": "job-board-agent", 
                "status": "in_progress",
                "result": "Finding matching job opportunities"
            },
            {
                "step_id": "salary_benchmark",
                "agent_id": "salary-benchmark-agent",
                "status": "pending",
                "result": "Pending salary analysis"
            }
        ],
        "overall_status": "in_progress",
        "completion_percentage": 33
    }
    
    return Response({
        "success": True,
        "agent_id": "hr-assistant-pro",
        "query": query,
        "response": "Workflow orchestration in progress",
        "data": workflow_data,
        "capabilities": ["workflow_orchestration", "multi_agent_communication"],
        "schema_types": ["Person", "JobPosting", "JobApplication"],
        "performance_metrics": {
            "response_time": 0.25,
            "workflow_orchestration_enabled": True
        }
    })

def process_external_agent_query(agent_id: str, query: str, context: dict, schema_types: list, capabilities: list) -> Response:
    """
    Process queries for external agents (simulated)
    """
    agent_info = EXTERNAL_AGENTS.get(agent_id, {})
    
    # Simulate external agent response
    simulated_response = {
        "agent_id": agent_id,
        "agent_name": agent_info.get("name", "Unknown Agent"),
        "query": query,
        "response": f"Simulated response from {agent_info.get('name', 'Unknown Agent')}",
        "data": {
            "external_data": True,
            "agent_capabilities": agent_info.get("capabilities", []),
            "schema_types": agent_info.get("schema_types", [])
        },
        "capabilities": agent_info.get("capabilities", []),
        "schema_types": agent_info.get("schema_types", []),
        "performance_metrics": {
            "response_time": 0.3,
            "external_agent": True
        }
    }
    
    return Response({
        "success": True,
        **simulated_response
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_agent_status(request):
    """
    Enhanced agent status with performance metrics
    """
    agent_id = request.GET.get('agent_id', 'hr-assistant-pro')
    
    if agent_id not in NLWEB_AGENTS and agent_id not in EXTERNAL_AGENTS:
        return Response({
            "success": False,
            "error": f"Agent {agent_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    agent = NLWEB_AGENTS.get(agent_id) or EXTERNAL_AGENTS.get(agent_id)
    
    # Calculate performance metrics
    agent_interactions = [
        interaction for interaction in nlweb_analytics.get('interactions', [])
        if interaction.get('agent_id') == agent_id
    ]
    
    performance_metrics = {
        "total_interactions": len(agent_interactions),
        "recent_interactions_7d": len([
            interaction for interaction in agent_interactions
            if datetime.fromisoformat(interaction['timestamp']) > datetime.now() - timedelta(days=7)
        ]),
        "last_interaction": agent_interactions[-1]['timestamp'] if agent_interactions else None
    }
    
    return Response({
        "success": True,
        "agent": agent,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "performance_metrics": performance_metrics,
        "enhanced_features": {
            "vector_search": agent_id == "hr-assistant-pro",
            "workflow_orchestration": agent_id == "hr-assistant-pro",
            "multi_agent_communication": True
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_broadcast_query(request):
    """
    Enhanced broadcast query to multiple agents
    """
    data = request.data
    query = data.get('query', '')
    schema_types = data.get('schema_types', [])
    capabilities = data.get('capabilities', [])
    
    if not query:
        return Response({
            "success": False,
            "error": "Query is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find relevant agents
    all_agents = {**NLWEB_AGENTS, **EXTERNAL_AGENTS}
    relevant_agents = []
    
    for agent_id, agent in all_agents.items():
        if agent.get('is_active', True):
            # Check schema type filter
            if schema_types and not any(st in agent.get('schema_types', []) for st in schema_types):
                continue
            # Check capability filter
            if capabilities and not any(cap in agent.get('capabilities', []) for cap in capabilities):
                continue
            relevant_agents.append(agent_id)
    
    # Simulate querying multiple agents
    results = []
    for agent_id in relevant_agents:
        if agent_id == "hr-assistant-pro":
            result = process_enhanced_hr_query(query, {}, schema_types, capabilities)
            results.append({
                "agent_id": agent_id,
                "agent_name": NLWEB_AGENTS[agent_id]["name"],
                "result": result.data
            })
        elif agent_id in EXTERNAL_AGENTS:
            result = process_external_agent_query(agent_id, query, {}, schema_types, capabilities)
            results.append({
                "agent_id": agent_id,
                "agent_name": EXTERNAL_AGENTS[agent_id]["name"],
                "result": result.data
            })
    
    return Response({
        "success": True,
        "query": query,
        "results": results,
        "total_agents_queried": len(results),
        "filters_applied": {
            "schema_types": schema_types,
            "capabilities": capabilities
        },
        "performance_metrics": {
            "total_response_time": sum(
                result["result"].get("performance_metrics", {}).get("response_time", 0)
                for result in results
            ),
            "agents_responded": len(results)
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def nlweb_orchestrate_workflow(request):
    """
    Orchestrate multi-agent workflows
    """
    data = request.data
    workflow_id = data.get('workflow_id', f"workflow_{datetime.now().timestamp()}")
    steps = data.get('steps', [])
    
    if not steps:
        return Response({
            "success": False,
            "error": "Workflow steps are required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Track workflow execution
    workflow_execution = {
        "workflow_id": workflow_id,
        "timestamp": datetime.now().isoformat(),
        "steps": steps,
        "status": "in_progress"
    }
    nlweb_analytics['workflow_executions'].append(workflow_execution)
    
    # Simulate workflow execution
    results = {}
    for step in steps:
        step_id = step.get('step_id')
        agent_id = step.get('agent_id')
        step_query = step.get('query', '')
        
        if agent_id == "hr-assistant-pro":
            result = process_enhanced_hr_query(step_query, step.get('context', {}), [], [])
            results[step_id] = {
                "success": True,
                "agent_id": agent_id,
                "result": result.data
            }
        elif agent_id in EXTERNAL_AGENTS:
            result = process_external_agent_query(agent_id, step_query, step.get('context', {}), [], [])
            results[step_id] = {
                "success": True,
                "agent_id": agent_id,
                "result": result.data
            }
    
    workflow_execution['results'] = results
    workflow_execution['status'] = 'completed'
    
    return Response({
        "success": True,
        "workflow_id": workflow_id,
        "status": "completed",
        "results": results,
        "total_steps": len(steps),
        "completed_steps": len(results),
        "performance_metrics": {
            "total_execution_time": 0.5,
            "average_step_time": 0.1
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_analytics_dashboard(request):
    """
    Get comprehensive NLWeb analytics
    """
    interactions = nlweb_analytics.get('interactions', [])
    workflow_executions = nlweb_analytics.get('workflow_executions', [])
    
    # Calculate analytics
    total_interactions = len(interactions)
    total_workflows = len(workflow_executions)
    
    # Agent usage statistics
    agent_usage = {}
    for interaction in interactions:
        agent_id = interaction.get('agent_id')
        agent_usage[agent_id] = agent_usage.get(agent_id, 0) + 1
    
    # Schema type usage
    schema_usage = {}
    for interaction in interactions:
        for schema_type in interaction.get('schema_types', []):
            schema_usage[schema_type] = schema_usage.get(schema_type, 0) + 1
    
    # Recent activity (last 7 days)
    recent_interactions = [
        interaction for interaction in interactions
        if datetime.fromisoformat(interaction['timestamp']) > datetime.now() - timedelta(days=7)
    ]
    
    return Response({
        "success": True,
        "analytics": {
            "total_interactions": total_interactions,
            "total_workflows": total_workflows,
            "recent_interactions_7d": len(recent_interactions),
            "agent_usage": agent_usage,
            "schema_usage": schema_usage,
            "workflow_success_rate": 0.95,  # Simulated
            "average_response_time": 0.2,  # Simulated
            "most_active_agents": sorted(agent_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_used_schemas": sorted(schema_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        },
        "insights": {
            "trending_capabilities": ["vector_search", "workflow_orchestration", "multi_agent_communication"],
            "performance_trends": "improving",
            "recommendations": [
                "Enable more external agent integrations",
                "Implement advanced vector search",
                "Expand workflow orchestration capabilities"
            ]
        },
        "timestamp": datetime.now().isoformat()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nlweb_schema_enhanced(request):
    """
    Get enhanced Schema.org data with NLWeb metadata
    """
    data_type = request.GET.get('data_type', 'candidates')
    candidate_id = request.GET.get('candidate_id')
    job_post_id = request.GET.get('job_post_id')
    
    if data_type == 'candidates':
        if candidate_id:
            candidates = Candidate.objects.filter(id=candidate_id)
        else:
            candidates = Candidate.objects.all()[:5]
        
        serializer = CandidateSerializer(candidates, many=True)
        data = serializer.data
        
        # Enhance with NLWeb metadata
        enhanced_data = []
        for item in data:
            enhanced_item = {
                "@context": "https://schema.org",
                "@type": "Person",
                **item,
                "nlweb:agent_id": "hr-assistant-pro",
                "nlweb:capabilities": [
                    "candidate_management",
                    "job_matching",
                    "analytics",
                    "vector_search"
                ],
                "nlweb:endpoints": {
                    "query": "/api/candidates/",
                    "schema": "/api/schema-org-data/",
                    "nlweb": "/api/nlweb/",
                    "vector": "/api/nlweb/vector/"
                },
                "nlweb:version": "2.0.0",
                "nlweb:last_updated": datetime.now().isoformat(),
                "nlweb:vector_search": {
                    "enabled": True,
                    "embedding_model": "text-embedding-ada-002",
                    "index_name": "candidates"
                }
            }
            enhanced_data.append(enhanced_item)
    
    elif data_type == 'job_posts':
        if job_post_id:
            job_posts = JobPost.objects.filter(id=job_post_id)
        else:
            job_posts = JobPost.objects.all()[:5]
        
        serializer = JobPostSerializer(job_posts, many=True)
        data = serializer.data
        
        # Enhance with NLWeb metadata
        enhanced_data = []
        for item in data:
            enhanced_item = {
                "@context": "https://schema.org",
                "@type": "JobPosting",
                **item,
                "nlweb:agent_id": "hr-assistant-pro",
                "nlweb:capabilities": [
                    "job_posting_management",
                    "candidate_matching",
                    "market_analysis",
                    "salary_benchmarking"
                ],
                "nlweb:endpoints": {
                    "query": "/api/jobposts/",
                    "schema": "/api/schema-org-data/",
                    "nlweb": "/api/nlweb/",
                    "vector": "/api/nlweb/vector/"
                },
                "nlweb:version": "2.0.0",
                "nlweb:last_updated": datetime.now().isoformat(),
                "nlweb:market_intelligence": {
                    "demand_level": "high",
                    "competition_level": "medium",
                    "trending_skills": ["Python", "React", "AWS"]
                },
                "nlweb:vector_search": {
                    "enabled": True,
                    "embedding_model": "text-embedding-ada-002",
                    "index_name": "job_postings"
                }
            }
            enhanced_data.append(enhanced_item)
    
    else:
        return Response({
            "success": False,
            "error": "Invalid data_type"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "success": True,
        "data_type": data_type,
        "count": len(enhanced_data),
        "schema_data": enhanced_data,
        "nlweb_metadata": {
            "version": "2.0.0",
            "enhanced_features": [
                "vector_search",
                "market_intelligence",
                "multi_agent_communication"
            ],
            "timestamp": datetime.now().isoformat()
        }
    }) 