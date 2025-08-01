#!/usr/bin/env python3
"""
NLWeb Enhancements for HR Assistant Pro
Implements advanced features for the emerging agentic web
"""

import json
import requests
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Enum for agent capabilities"""
    CANDIDATE_MANAGEMENT = "candidate_management"
    JOB_POSTING_MANAGEMENT = "job_posting_management"
    ANALYTICS = "analytics"
    SCHEMA_ORG_DATA = "schema_org_data"
    NLWEB_COMMUNICATION = "nlweb_communication"
    VECTOR_SEARCH = "vector_search"
    MACHINE_LEARNING = "machine_learning"
    MARKET_ANALYSIS = "market_analysis"
    SALARY_BENCHMARKING = "salary_benchmarking"
    BACKGROUND_CHECKS = "background_checks"

class SchemaType(Enum):
    """Enum for Schema.org types"""
    PERSON = "Person"
    JOB_POSTING = "JobPosting"
    JOB_APPLICATION = "JobApplication"
    ORGANIZATION = "Organization"
    PLACE = "Place"
    QUANTITATIVE_VALUE = "QuantitativeValue"

@dataclass
class NLWebAgent:
    """Represents an NLWeb agent for discovery and communication"""
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    endpoints: Dict[str, str]
    schema_types: List[str]
    last_seen: datetime
    is_active: bool = True
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    external_agents: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    api_version: str = "2024-01-01"

@dataclass
class NLWebQuery:
    """Represents an NLWeb query with context"""
    query: str
    agent_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    schema_types: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    priority: int = 1
    timeout: int = 30
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class NLWebResponse:
    """Represents an NLWeb response"""
    success: bool
    agent_id: str
    query: str
    response: str
    data: Dict[str, Any] = field(default_factory=dict)
    schema_types: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class NLWebRegistry:
    """Enhanced registry for NLWeb agents and their capabilities"""
    
    def __init__(self):
        self.agents: Dict[str, NLWebAgent] = {}
        self.schema_registry: Dict[str, List[str]] = {}
        self.capability_registry: Dict[str, List[str]] = {}
        self.external_agents: Dict[str, Dict[str, Any]] = {}
        self.query_history: List[NLWebQuery] = []
        self.response_history: List[NLWebResponse] = []
    
    def register_agent(self, agent: NLWebAgent):
        """Register an NLWeb agent with enhanced capabilities"""
        self.agents[agent.agent_id] = agent
        
        # Register schema types
        for schema_type in agent.schema_types:
            if schema_type not in self.schema_registry:
                self.schema_registry[schema_type] = []
            if agent.agent_id not in self.schema_registry[schema_type]:
                self.schema_registry[schema_type].append(agent.agent_id)
        
        # Register capabilities
        for capability in agent.capabilities:
            if capability not in self.capability_registry:
                self.capability_registry[capability] = []
            if agent.agent_id not in self.capability_registry[capability]:
                self.capability_registry[capability].append(agent.agent_id)
    
    def register_external_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an external agent for communication"""
        self.external_agents[agent_id] = agent_info
    
    def discover_agents(self, schema_type: str = None, capability: str = None) -> List[NLWebAgent]:
        """Discover agents by schema type, capability, or all agents"""
        if schema_type and capability:
            schema_agents = set(self.schema_registry.get(schema_type, []))
            capability_agents = set(self.capability_registry.get(capability, []))
            agent_ids = schema_agents.intersection(capability_agents)
        elif schema_type:
            agent_ids = self.schema_registry.get(schema_type, [])
        elif capability:
            agent_ids = self.capability_registry.get(capability, [])
        else:
            agent_ids = list(self.agents.keys())
        
        return [self.agents[aid] for aid in agent_ids if aid in self.agents and self.agents[aid].is_active]
    
    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities of a specific agent"""
        agent = self.agents.get(agent_id)
        return agent.capabilities if agent else []
    
    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        # Calculate performance metrics from response history
        agent_responses = [r for r in self.response_history if r.agent_id == agent_id]
        
        if not agent_responses:
            return {"error": "No performance data available"}
        
        success_count = sum(1 for r in agent_responses if r.success)
        total_count = len(agent_responses)
        avg_response_time = sum(
            (r.timestamp - q.timestamp).total_seconds() 
            for r, q in zip(agent_responses, self.query_history[-total_count:])
        ) / total_count if total_count > 0 else 0
        
        return {
            "agent_id": agent_id,
            "total_queries": total_count,
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "avg_response_time": avg_response_time,
            "last_query": agent_responses[-1].timestamp.isoformat() if agent_responses else None,
            "capabilities": agent.capabilities,
            "schema_types": agent.schema_types
        }

class NLWebCommunicator:
    """Enhanced communication between NLWeb agents"""
    
    def __init__(self, registry: NLWebRegistry):
        self.registry = registry
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HR-Assistant-Pro-NLWeb/1.0.0',
            'Content-Type': 'application/json'
        })
    
    async def query_agent(self, agent_id: str, query: str, context: Dict = None) -> NLWebResponse:
        """Query another NLWeb agent with enhanced error handling"""
        agent = self.registry.agents.get(agent_id)
        if not agent:
            return NLWebResponse(
                success=False,
                agent_id=agent_id,
                query=query,
                response="Agent not found",
                data={"error": "Agent not found"}
            )
        
        # Prepare query with enhanced context
        payload = {
            "query": query,
            "context": context or {},
            "schema_types": ["Person", "JobPosting", "JobApplication"],
            "capabilities": agent.capabilities,
            "timestamp": datetime.now().isoformat(),
            "request_id": f"{agent_id}_{datetime.now().timestamp()}"
        }
        
        start_time = datetime.now()
        
        try:
            response = self.session.post(
                f"{agent.endpoints['query']}/nlweb/query",
                json=payload,
                timeout=30
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                return NLWebResponse(
                    success=data.get("success", False),
                    agent_id=agent_id,
                    query=query,
                    response=data.get("response", ""),
                    data=data.get("data", {}),
                    schema_types=data.get("schema_types", []),
                    capabilities=data.get("capabilities", []),
                    performance_metrics={"response_time": response_time},
                    timestamp=datetime.now()
                )
            else:
                return NLWebResponse(
                    success=False,
                    agent_id=agent_id,
                    query=query,
                    response=f"HTTP {response.status_code}: {response.text}",
                    data={"error": f"HTTP {response.status_code}"},
                    performance_metrics={"response_time": response_time},
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error querying agent {agent_id}: {str(e)}")
            return NLWebResponse(
                success=False,
                agent_id=agent_id,
                query=query,
                response=f"Communication failed: {str(e)}",
                data={"error": str(e)},
                performance_metrics={"response_time": response_time},
                timestamp=datetime.now()
            )
    
    async def broadcast_query(self, query: str, schema_types: List[str] = None, 
                            capabilities: List[str] = None) -> List[NLWebResponse]:
        """Broadcast query to multiple agents with filtering"""
        results = []
        
        # Find relevant agents
        if schema_types and capabilities:
            agents = []
            for schema_type in schema_types:
                for capability in capabilities:
                    agents.extend(self.registry.discover_agents(schema_type, capability))
        elif schema_types:
            agents = []
            for schema_type in schema_types:
                agents.extend(self.registry.discover_agents(schema_type))
        elif capabilities:
            agents = []
            for capability in capabilities:
                agents.extend(self.registry.discover_agents(capability=capability))
        else:
            agents = self.registry.discover_agents()
        
        # Remove duplicates
        unique_agents = {agent.agent_id: agent for agent in agents}.values()
        
        # Query each agent concurrently
        tasks = []
        for agent in unique_agents:
            if agent.is_active:
                task = self.query_agent(agent.agent_id, query)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Filter out exceptions
            results = [r for r in results if not isinstance(r, Exception)]
        
        return results
    
    async def orchestrate_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a multi-agent workflow"""
        workflow_id = workflow.get("workflow_id", f"workflow_{datetime.now().timestamp()}")
        steps = workflow.get("steps", [])
        results = {}
        
        for step in steps:
            step_id = step.get("step_id")
            agent_id = step.get("agent_id")
            query = step.get("query")
            dependencies = step.get("dependencies", [])
            
            # Check dependencies
            if dependencies and not all(dep in results for dep in dependencies):
                logger.warning(f"Step {step_id} dependencies not met")
                continue
            
            # Execute step
            if agent_id and query:
                response = await self.query_agent(agent_id, query, step.get("context", {}))
                results[step_id] = response
        
        return {
            "workflow_id": workflow_id,
            "success": all(r.success for r in results.values() if isinstance(r, NLWebResponse)),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

class NLWebSchemaEnhancer:
    """Enhanced Schema.org data for better NLWeb compatibility"""
    
    @staticmethod
    def enhance_candidate_schema(candidate_data: Dict) -> Dict:
        """Enhance candidate Schema.org data for NLWeb"""
        enhanced = candidate_data.copy()
        
        # Add NLWeb-specific metadata
        enhanced["@context"] = "https://schema.org"
        enhanced["@type"] = "Person"
        enhanced["nlweb:agent_id"] = "hr-assistant-pro"
        enhanced["nlweb:capabilities"] = [
            "candidate_management",
            "job_matching",
            "analytics",
            "vector_search"
        ]
        enhanced["nlweb:endpoints"] = {
            "query": "/api/candidates/",
            "schema": "/api/schema-org-data/",
            "nlweb": "/api/nlweb/",
            "vector": "/api/nlweb/vector/"
        }
        enhanced["nlweb:version"] = "1.0.0"
        enhanced["nlweb:last_updated"] = datetime.now().isoformat()
        
        # Add semantic relationships
        if "jobApplication" in enhanced:
            enhanced["jobApplication"]["nlweb:related_agents"] = [
                "job-board-agent",
                "recruitment-agent",
                "analytics-agent",
                "salary-benchmark-agent"
            ]
        
        # Add vector search metadata
        enhanced["nlweb:vector_search"] = {
            "enabled": True,
            "embedding_model": "text-embedding-ada-002",
            "index_name": "candidates"
        }
        
        return enhanced
    
    @staticmethod
    def enhance_job_posting_schema(job_data: Dict) -> Dict:
        """Enhance job posting Schema.org data for NLWeb"""
        enhanced = job_data.copy()
        
        # Add NLWeb-specific metadata
        enhanced["@context"] = "https://schema.org"
        enhanced["@type"] = "JobPosting"
        enhanced["nlweb:agent_id"] = "hr-assistant-pro"
        enhanced["nlweb:capabilities"] = [
            "job_posting_management",
            "candidate_matching",
            "market_analysis",
            "salary_benchmarking"
        ]
        enhanced["nlweb:endpoints"] = {
            "query": "/api/jobposts/",
            "schema": "/api/schema-org-data/",
            "nlweb": "/api/nlweb/",
            "vector": "/api/nlweb/vector/"
        }
        enhanced["nlweb:version"] = "1.0.0"
        enhanced["nlweb:last_updated"] = datetime.now().isoformat()
        
        # Add semantic relationships
        enhanced["nlweb:related_agents"] = [
            "candidate-agent",
            "market-analysis-agent",
            "salary-benchmark-agent",
            "background-check-agent"
        ]
        
        # Add market intelligence
        enhanced["nlweb:market_intelligence"] = {
            "salary_range": job_data.get("salary_range"),
            "market_demand": "high",  # This would be calculated
            "competition_level": "medium",  # This would be calculated
            "trending_skills": ["Python", "React", "AWS"]  # This would be dynamic
        }
        
        # Add vector search metadata
        enhanced["nlweb:vector_search"] = {
            "enabled": True,
            "embedding_model": "text-embedding-ada-002",
            "index_name": "job_postings"
        }
        
        return enhanced
    
    @staticmethod
    def create_workflow_schema(workflow_data: Dict) -> Dict:
        """Create Schema.org data for NLWeb workflows"""
        return {
            "@context": "https://schema.org",
            "@type": "Workflow",
            "name": workflow_data.get("name", "HR Workflow"),
            "description": workflow_data.get("description", ""),
            "nlweb:agent_id": "hr-assistant-pro",
            "nlweb:workflow_id": workflow_data.get("workflow_id"),
            "nlweb:steps": workflow_data.get("steps", []),
            "nlweb:capabilities": [
                "workflow_orchestration",
                "multi_agent_communication",
                "schema_org_integration"
            ],
            "nlweb:endpoints": {
                "orchestrate": "/api/nlweb/orchestrate/",
                "status": "/api/nlweb/workflow/status/"
            },
            "timestamp": datetime.now().isoformat()
        }

class NLWebAnalytics:
    """Enhanced analytics for NLWeb agent interactions"""
    
    def __init__(self):
        self.interaction_log = []
        self.performance_metrics = {}
        self.schema_usage_stats = {}
        self.workflow_analytics = {}
    
    def log_interaction(self, query: NLWebQuery, response: NLWebResponse):
        """Log agent interaction with enhanced metrics"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query.query,
            "agent_id": query.agent_id,
            "response_success": response.success,
            "response_time": response.performance_metrics.get("response_time", 0),
            "schema_types": query.schema_types,
            "capabilities": query.capabilities,
            "context": query.context
        }
        
        self.interaction_log.append(interaction)
        
        # Update performance metrics
        if query.agent_id not in self.performance_metrics:
            self.performance_metrics[query.agent_id] = {
                "total_queries": 0,
                "successful_queries": 0,
                "total_response_time": 0,
                "avg_response_time": 0
            }
        
        metrics = self.performance_metrics[query.agent_id]
        metrics["total_queries"] += 1
        if response.success:
            metrics["successful_queries"] += 1
        metrics["total_response_time"] += response.performance_metrics.get("response_time", 0)
        metrics["avg_response_time"] = metrics["total_response_time"] / metrics["total_queries"]
    
    def get_agent_performance(self, agent_id: str) -> Dict:
        """Get comprehensive performance metrics for an agent"""
        if agent_id not in self.performance_metrics:
            return {"error": "No performance data available"}
        
        metrics = self.performance_metrics[agent_id]
        
        # Get recent interactions
        recent_interactions = [
            log for log in self.interaction_log 
            if log["agent_id"] == agent_id and 
            datetime.fromisoformat(log["timestamp"]) > datetime.now() - timedelta(days=7)
        ]
        
        return {
            "agent_id": agent_id,
            "total_queries": metrics["total_queries"],
            "success_rate": metrics["successful_queries"] / metrics["total_queries"] if metrics["total_queries"] > 0 else 0,
            "avg_response_time": metrics["avg_response_time"],
            "recent_queries_7d": len(recent_interactions),
            "last_interaction": recent_interactions[-1]["timestamp"] if recent_interactions else None,
            "schema_types_used": list(set(
                schema_type for log in recent_interactions 
                for schema_type in log.get("schema_types", [])
            )),
            "capabilities_used": list(set(
                capability for log in recent_interactions 
                for capability in log.get("capabilities", [])
            ))
        }
    
    def get_schema_usage_stats(self) -> Dict:
        """Get comprehensive usage statistics by schema type"""
        stats = {}
        
        for log in self.interaction_log:
            for schema_type in log.get("schema_types", []):
                if schema_type not in stats:
                    stats[schema_type] = {
                        "queries": 0,
                        "successful": 0,
                        "avg_response_time": 0,
                        "total_response_time": 0,
                        "agents_used": set()
                    }
                
                stats[schema_type]["queries"] += 1
                stats[schema_type]["agents_used"].add(log["agent_id"])
                
                if log["response_success"]:
                    stats[schema_type]["successful"] += 1
                
                stats[schema_type]["total_response_time"] += log["response_time"]
                stats[schema_type]["avg_response_time"] = (
                    stats[schema_type]["total_response_time"] / stats[schema_type]["queries"]
                )
        
        # Convert sets to lists for JSON serialization
        for schema_type in stats:
            stats[schema_type]["agents_used"] = list(stats[schema_type]["agents_used"])
        
        return stats
    
    def get_workflow_analytics(self, workflow_id: str) -> Dict:
        """Get analytics for specific workflows"""
        if workflow_id not in self.workflow_analytics:
            return {"error": "Workflow not found"}
        
        return self.workflow_analytics[workflow_id]
    
    def generate_insights(self) -> Dict:
        """Generate insights from analytics data"""
        total_interactions = len(self.interaction_log)
        if total_interactions == 0:
            return {"error": "No data available"}
        
        # Most used schema types
        schema_usage = {}
        for log in self.interaction_log:
            for schema_type in log.get("schema_types", []):
                schema_usage[schema_type] = schema_usage.get(schema_type, 0) + 1
        
        most_used_schemas = sorted(schema_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Most active agents
        agent_usage = {}
        for log in self.interaction_log:
            agent_usage[log["agent_id"]] = agent_usage.get(log["agent_id"], 0) + 1
        
        most_active_agents = sorted(agent_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Average response times
        response_times = [log["response_time"] for log in self.interaction_log if log["response_time"] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_interactions": total_interactions,
            "most_used_schemas": most_used_schemas,
            "most_active_agents": most_active_agents,
            "avg_response_time": avg_response_time,
            "success_rate": sum(1 for log in self.interaction_log if log["response_success"]) / total_interactions,
            "insights_generated": datetime.now().isoformat()
        }

# Initialize enhanced NLWeb components
nlweb_registry = NLWebRegistry()
nlweb_communicator = NLWebCommunicator(nlweb_registry)
nlweb_enhancer = NLWebSchemaEnhancer()
nlweb_analytics = NLWebAnalytics()

# Register our HR Assistant Pro as an enhanced NLWeb agent
hr_agent = NLWebAgent(
    agent_id="hr-assistant-pro",
    name="HR Assistant Pro",
    description="AI-powered HR management platform with advanced NLWeb capabilities",
    capabilities=[
        "candidate_management",
        "job_posting_management", 
        "analytics",
        "schema_org_data",
        "nlweb_communication",
        "vector_search",
        "workflow_orchestration",
        "multi_agent_communication"
    ],
    endpoints={
        "query": "http://localhost:8000/api",
        "schema": "http://localhost:8000/api/schema-org-data/",
        "nlweb": "http://localhost:8000/api/nlweb/",
        "vector": "http://localhost:8000/api/nlweb/vector/"
    },
    schema_types=["Person", "JobPosting", "JobApplication", "Organization"],
    last_seen=datetime.now(),
    version="2.0.0",
    api_version="2024-01-01"
)

nlweb_registry.register_agent(hr_agent)

# Register some external agents for demonstration
external_agents = {
    "job-board-agent": {
        "name": "Job Board Agent",
        "description": "External job board integration",
        "endpoints": {"query": "https://api.jobboard.com/nlweb"},
        "capabilities": ["job_posting_management", "market_analysis"],
        "schema_types": ["JobPosting"]
    },
    "recruitment-agent": {
        "name": "Recruitment Agent", 
        "description": "External recruitment services",
        "endpoints": {"query": "https://api.recruitment.com/nlweb"},
        "capabilities": ["candidate_management", "background_checks"],
        "schema_types": ["Person", "JobApplication"]
    },
    "salary-benchmark-agent": {
        "name": "Salary Benchmark Agent",
        "description": "Salary and compensation data",
        "endpoints": {"query": "https://api.salary.com/nlweb"},
        "capabilities": ["salary_benchmarking", "market_analysis"],
        "schema_types": ["QuantitativeValue"]
    }
}

for agent_id, agent_info in external_agents.items():
    nlweb_registry.register_external_agent(agent_id, agent_info)

def get_nlweb_status() -> Dict:
    """Get comprehensive NLWeb status and capabilities"""
    return {
        "agent_id": hr_agent.agent_id,
        "name": hr_agent.name,
        "version": hr_agent.version,
        "api_version": hr_agent.api_version,
        "capabilities": hr_agent.capabilities,
        "schema_types": hr_agent.schema_types,
        "endpoints": hr_agent.endpoints,
        "registered_agents": len(nlweb_registry.agents),
        "external_agents": len(nlweb_registry.external_agents),
        "discovered_agents": [agent.agent_id for agent in nlweb_registry.discover_agents()],
        "status": "active",
        "last_seen": hr_agent.last_seen.isoformat(),
        "analytics": {
            "total_interactions": len(nlweb_analytics.interaction_log),
            "performance_metrics": nlweb_analytics.performance_metrics
        }
    }

async def orchestrate_hr_workflow(candidate_id: str) -> Dict:
    """Example workflow orchestration"""
    workflow = {
        "workflow_id": f"hr_workflow_{candidate_id}_{datetime.now().timestamp()}",
        "name": "HR Candidate Processing Workflow",
        "description": "Complete candidate processing workflow",
        "steps": [
            {
                "step_id": "get_candidate",
                "agent_id": "hr-assistant-pro",
                "query": f"Get candidate {candidate_id}",
                "context": {"candidate_id": candidate_id}
            },
            {
                "step_id": "find_job_matches",
                "agent_id": "job-board-agent",
                "query": f"Find job matches for candidate {candidate_id}",
                "dependencies": ["get_candidate"],
                "context": {"candidate_id": candidate_id}
            },
            {
                "step_id": "salary_benchmark",
                "agent_id": "salary-benchmark-agent", 
                "query": f"Get salary benchmark for candidate {candidate_id}",
                "dependencies": ["get_candidate"],
                "context": {"candidate_id": candidate_id}
            },
            {
                "step_id": "background_check",
                "agent_id": "recruitment-agent",
                "query": f"Initiate background check for candidate {candidate_id}",
                "dependencies": ["get_candidate"],
                "context": {"candidate_id": candidate_id}
            }
        ]
    }
    
    return await nlweb_communicator.orchestrate_workflow(workflow) 