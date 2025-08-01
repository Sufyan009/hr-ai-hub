import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Progress } from './ui/progress';
import { 
  Search, Users, Briefcase, Brain, Database, Globe, 
  TrendingUp, Activity, Workflow, Network, BarChart3,
  Zap, Target, ArrowRight, CheckCircle, Clock, AlertCircle
} from 'lucide-react';

interface SearchResult {
  id: string;
  name?: string;
  title?: string;
  company?: string;
  job_title?: string;
  location?: string;
  score: number;
  type: 'candidate' | 'job';
}

interface AgentInfo {
  agent_id: string;
  name: string;
  description: string;
  capabilities: string[];
  schema_types: string[];
  is_active: boolean;
  version?: string;
  api_version?: string;
}

interface WorkflowStep {
  step_id: string;
  agent_id: string;
  query: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  result?: any;
}

interface WorkflowExecution {
  workflow_id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  overall_status: string;
  completion_percentage: number;
}

interface NLWebSearchProps {
  authToken: string;
}

const NLWebSearch: React.FC<NLWebSearchProps> = ({ authToken }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'all' | 'candidates' | 'jobs'>('all');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [agentStatus, setAgentStatus] = useState<any>(null);
  const [vectorStats, setVectorStats] = useState<any>(null);
  const [discoveredAgents, setDiscoveredAgents] = useState<AgentInfo[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [workflows, setWorkflows] = useState<WorkflowExecution[]>([]);
  const [activeTab, setActiveTab] = useState('search');

  const headers = {
    'Authorization': `Token ${authToken}`,
    'Content-Type': 'application/json'
  };

  // Check agent status on component mount
  useEffect(() => {
    checkAgentStatus();
    getVectorStats();
    discoverAgents();
    getAnalytics();
  }, []);

  const checkAgentStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/vector/status/?agent_id=hr-assistant-pro', {
        headers
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAgentStatus(data.agent);
        }
      }
    } catch (error) {
      console.error('Error checking agent status:', error);
    }
  };

  const getVectorStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/vector/stats/', {
        headers
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setVectorStats(data);
        }
      }
    } catch (error) {
      console.error('Error getting vector stats:', error);
    }
  };

  const discoverAgents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/discover/?include_external=true', {
        headers
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setDiscoveredAgents(data.agents);
        }
      }
    } catch (error) {
      console.error('Error discovering agents:', error);
    }
  };

  const getAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/analytics/', {
        headers
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAnalytics(data.analytics);
        }
      }
    } catch (error) {
      console.error('Error getting analytics:', error);
    }
  };

  const performSemanticSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/vector/query/', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query: query,
          agent_id: 'hr-assistant-pro',
          search_type: 'semantic',
          limit: 10,
          score_threshold: 0.7
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Process results based on query type
          let processedResults: SearchResult[] = [];
          
          if (data.query_type === 'candidate_search') {
            processedResults = data.results.map((result: any) => ({
              id: result.id,
              name: result.name,
              job_title: result.job_title,
              location: result.city,
              score: result.score,
              type: 'candidate' as const
            }));
          } else if (data.query_type === 'job_search') {
            processedResults = data.results.map((result: any) => ({
              id: result.id,
              title: result.title,
              company: result.company,
              location: result.location,
              score: result.score,
              type: 'job' as const
            }));
          } else {
            // General search - combine both
            const candidates = data.candidates?.map((result: any) => ({
              id: result.id,
              name: result.name,
              job_title: result.job_title,
              location: result.city,
              score: result.score,
              type: 'candidate' as const
            })) || [];
            
            const jobs = data.job_posts?.map((result: any) => ({
              id: result.id,
              title: result.title,
              company: result.company,
              location: result.location,
              score: result.score,
              type: 'job' as const
            })) || [];
            
            processedResults = [...candidates, ...jobs];
          }
          
          setResults(processedResults);
        }
      }
    } catch (error) {
      console.error('Error performing semantic search:', error);
    } finally {
      setLoading(false);
    }
  };

  const executeWorkflow = async (workflowData: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/orchestrate/', {
        method: 'POST',
        headers,
        body: JSON.stringify(workflowData)
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Add to workflows list
          setWorkflows(prev => [...prev, {
            workflow_id: data.workflow_id,
            name: workflowData.name || 'HR Workflow',
            description: workflowData.description || '',
            steps: workflowData.steps,
            overall_status: data.status,
            completion_percentage: 100
          }]);
        }
      }
    } catch (error) {
      console.error('Error executing workflow:', error);
    }
  };

  const handleSearch = () => {
    performSemanticSearch();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      performSemanticSearch();
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-2">
        <Brain className="h-6 w-6 text-blue-600" />
        <h2 className="text-2xl font-bold">NLWeb Enhanced Search</h2>
        <Badge variant="secondary" className="ml-2">
          AI-Powered v2.0
        </Badge>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="search">Search</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Search Tab */}
        <TabsContent value="search" className="space-y-6">
          {/* Agent Status */}
          {agentStatus && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="h-5 w-5" />
                  <span>Agent Status</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium">Agent: {agentStatus.name}</p>
                    <p className="text-sm text-gray-600">Status: {agentStatus.status}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Embedding Model</p>
                    <p className="text-sm text-gray-600">{agentStatus.vector_capabilities?.embedding_model}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Vector Database Stats */}
          {vectorStats && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Globe className="h-5 w-5" />
                  <span>Vector Database Stats</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  {Object.entries(vectorStats.vector_database_stats).map(([key, value]: [string, any]) => (
                    <div key={key}>
                      <p className="text-sm font-medium capitalize">{key}</p>
                      <p className="text-sm text-gray-600">{value.points_count} points</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Search Interface */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="h-5 w-5" />
                <span>Semantic Search</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex space-x-2">
                  <Input
                    placeholder="Try: 'Find Python developers with 5+ years experience'"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="flex-1"
                  />
                  <Button onClick={handleSearch} disabled={loading}>
                    {loading ? 'Searching...' : 'Search'}
                  </Button>
                </div>
                
                <div className="flex space-x-2">
                  <Button
                    variant={searchType === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSearchType('all')}
                  >
                    All
                  </Button>
                  <Button
                    variant={searchType === 'candidates' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSearchType('candidates')}
                  >
                    <Users className="h-4 w-4 mr-1" />
                    Candidates
                  </Button>
                  <Button
                    variant={searchType === 'jobs' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSearchType('jobs')}
                  >
                    <Briefcase className="h-4 w-4 mr-1" />
                    Jobs
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {results.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Search Results ({results.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96">
                  <div className="space-y-4">
                    {results
                      .filter(result => 
                        searchType === 'all' || 
                        (searchType === 'candidates' && result.type === 'candidate') ||
                        (searchType === 'jobs' && result.type === 'job')
                      )
                      .map((result, index) => (
                        <div key={`${result.id}-${index}`} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              {result.type === 'candidate' ? (
                                <div>
                                  <h3 className="font-semibold">{result.name || 'Unknown'}</h3>
                                  <p className="text-sm text-gray-600">{result.job_title || 'Unknown Position'}</p>
                                  {result.location && (
                                    <p className="text-sm text-gray-500">{result.location}</p>
                                  )}
                                </div>
                              ) : (
                                <div>
                                  <h3 className="font-semibold">{result.title || 'Unknown'}</h3>
                                  <p className="text-sm text-gray-600">{result.company || 'Unknown Company'}</p>
                                  {result.location && (
                                    <p className="text-sm text-gray-500">{result.location}</p>
                                  )}
                                </div>
                              )}
                            </div>
                            <Badge className={getScoreColor(result.score)}>
                              {(result.score * 100).toFixed(1)}%
                            </Badge>
                          </div>
                        </div>
                      ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}

          {/* Example Queries */}
          <Card>
            <CardHeader>
              <CardTitle>Example Queries</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {[
                  'Find Python developers with 5+ years experience',
                  'Show me data scientists in Seattle',
                  'Search for frontend developers with React skills',
                  'Find senior software engineers in San Francisco',
                  'Show job openings for DevOps engineers',
                  'Find candidates with machine learning experience'
                ].map((exampleQuery, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setQuery(exampleQuery);
                      performSemanticSearch();
                    }}
                    className="text-left justify-start h-auto p-2"
                  >
                    <span className="text-xs">{exampleQuery}</span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Network className="h-5 w-5" />
                <span>Discovered Agents</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {discoveredAgents.map((agent) => (
                  <div key={agent.agent_id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold">{agent.name}</h3>
                        <p className="text-sm text-gray-600">{agent.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {agent.capabilities.map((capability) => (
                            <Badge key={capability} variant="outline" className="text-xs">
                              {capability}
                            </Badge>
                          ))}
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {agent.schema_types.map((schema) => (
                            <Badge key={schema} variant="secondary" className="text-xs">
                              {schema}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={agent.is_active ? "default" : "secondary"}>
                          {agent.is_active ? "Active" : "Inactive"}
                        </Badge>
                        {agent.version && (
                          <Badge variant="outline" className="text-xs">
                            v{agent.version}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Workflow className="h-5 w-5" />
                <span>Workflow Orchestration</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button
                  onClick={() => executeWorkflow({
                    name: "HR Candidate Processing",
                    description: "Complete candidate processing workflow",
                    steps: [
                      {
                        step_id: "get_candidate",
                        agent_id: "hr-assistant-pro",
                        query: "Get candidate profile"
                      },
                      {
                        step_id: "find_job_matches",
                        agent_id: "job-board-agent",
                        query: "Find matching job opportunities"
                      },
                      {
                        step_id: "salary_benchmark",
                        agent_id: "salary-benchmark-agent",
                        query: "Get salary benchmark"
                      }
                    ]
                  })}
                  className="w-full"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Execute Sample Workflow
                </Button>

                {workflows.map((workflow) => (
                  <div key={workflow.workflow_id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-semibold">{workflow.name}</h3>
                        <p className="text-sm text-gray-600">{workflow.description}</p>
                      </div>
                      <Badge variant="outline">
                        {workflow.overall_status}
                      </Badge>
                    </div>
                    
                    <Progress value={workflow.completion_percentage} className="mb-4" />
                    
                    <div className="space-y-2">
                      {workflow.steps.map((step) => (
                        <div key={step.step_id} className="flex items-center space-x-2">
                          {getStatusIcon(step.status)}
                          <span className="text-sm font-medium">{step.step_id}</span>
                          <span className="text-sm text-gray-500">-</span>
                          <span className="text-sm text-gray-600">{step.agent_id}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>NLWeb Analytics</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analytics ? (
                <div className="space-y-6">
                  {/* Overview Stats */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {analytics.total_interactions}
                      </div>
                      <div className="text-sm text-gray-600">Total Interactions</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {analytics.total_workflows}
                      </div>
                      <div className="text-sm text-gray-600">Workflows</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600">
                        {(analytics.average_response_time * 1000).toFixed(0)}ms
                      </div>
                      <div className="text-sm text-gray-600">Avg Response</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {(analytics.workflow_success_rate * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Success Rate</div>
                    </div>
                  </div>

                  {/* Most Active Agents */}
                  <div>
                    <h4 className="font-semibold mb-2">Most Active Agents</h4>
                    <div className="space-y-2">
                      {analytics.most_active_agents?.map(([agent, count]: [string, number]) => (
                        <div key={agent} className="flex justify-between items-center">
                          <span className="text-sm">{agent}</span>
                          <Badge variant="outline">{count} queries</Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Most Used Schemas */}
                  <div>
                    <h4 className="font-semibold mb-2">Most Used Schema Types</h4>
                    <div className="space-y-2">
                      {analytics.most_used_schemas?.map(([schema, count]: [string, number]) => (
                        <div key={schema} className="flex justify-between items-center">
                          <span className="text-sm">{schema}</span>
                          <Badge variant="outline">{count} uses</Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500">
                  <Activity className="h-8 w-8 mx-auto mb-2" />
                  <p>Loading analytics...</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default NLWebSearch; 