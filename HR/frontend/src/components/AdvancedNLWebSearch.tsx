import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { 
  Search, Users, Briefcase, Brain, Database, Globe, 
  DollarSign, MapPin, Clock, Code, Filter, TrendingUp,
  Zap, Target, BarChart3
} from 'lucide-react';

interface SearchResult {
  id: string;
  name?: string;
  title?: string;
  company?: string;
  job_title?: string;
  location?: string;
  salary?: string;
  experience?: string;
  score: number;
  type: 'candidate' | 'job';
}

interface SearchFilters {
  salary_min?: number;
  salary_max?: number;
  location?: string;
  experience_min?: number;
  experience_max?: number;
  skills: string[];
  remote: boolean;
  job_type?: string;
}

interface NLWebAdvancedSearchProps {
  authToken: string;
}

const AdvancedNLWebSearch: React.FC<NLWebAdvancedSearchProps> = ({ authToken }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'all' | 'candidates' | 'jobs'>('all');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('semantic');
  const [filters, setFilters] = useState<SearchFilters>({
    salary_min: undefined,
    salary_max: undefined,
    location: '',
    experience_min: undefined,
    experience_max: undefined,
    skills: [],
    remote: false,
    job_type: undefined
  });
  const [suggestions, setSuggestions] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);

  const headers = {
    'Authorization': `Token ${authToken}`,
    'Content-Type': 'application/json'
  };

  useEffect(() => {
    loadSuggestions();
    loadAnalytics();
  }, []);

  const loadSuggestions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/search/suggestions/', {
        headers
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSuggestions(data.suggestions);
        }
      }
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/search/analytics/', {
        headers
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAnalytics(data.analytics);
        }
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const performAdvancedSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/advanced/search/', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query: query,
          search_type: searchType,
          limit: 10,
          score_threshold: 0.7
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setResults(data.results);
        }
      }
    } catch (error) {
      console.error('Error performing advanced search:', error);
    } finally {
      setLoading(false);
    }
  };

  const performSalarySearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/salary/search/', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          min_salary: filters.salary_min,
          max_salary: filters.salary_max,
          search_type: searchType,
          limit: 10
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setResults(data.results);
        }
      }
    } catch (error) {
      console.error('Error performing salary search:', error);
    } finally {
      setLoading(false);
    }
  };

  const performLocationSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/nlweb/location/search/', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          location: filters.location,
          radius: 50,
          search_type: searchType,
          limit: 10
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setResults(data.results);
        }
      }
    } catch (error) {
      console.error('Error performing location search:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (activeTab === 'semantic') {
      performAdvancedSearch();
    } else if (activeTab === 'salary') {
      performSalarySearch();
    } else if (activeTab === 'location') {
      performLocationSearch();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const formatSalary = (salary: string | number) => {
    if (!salary) return 'Not specified';
    const num = typeof salary === 'string' ? parseInt(salary.replace(/[$,]/g, '')) : salary;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-2">
        <Brain className="h-6 w-6 text-blue-600" />
        <h2 className="text-2xl font-bold">Advanced NLWeb Search</h2>
        <Badge variant="secondary" className="ml-2">
          AI-Powered + Filters
        </Badge>
      </div>

      {/* Analytics Dashboard */}
      {analytics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Search Analytics</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{analytics.total_indexed_items}</p>
                <p className="text-sm text-gray-600">Total Items</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{analytics.candidates_count}</p>
                <p className="text-sm text-gray-600">Candidates</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">{analytics.jobs_count}</p>
                <p className="text-sm text-gray-600">Jobs</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">{analytics.performance_metrics.average_response_time}</p>
                <p className="text-sm text-gray-600">Avg Response</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Advanced Search</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="semantic" className="flex items-center space-x-2">
                <Brain className="h-4 w-4" />
                <span>Semantic</span>
              </TabsTrigger>
              <TabsTrigger value="salary" className="flex items-center space-x-2">
                <DollarSign className="h-4 w-4" />
                <span>Salary</span>
              </TabsTrigger>
              <TabsTrigger value="location" className="flex items-center space-x-2">
                <MapPin className="h-4 w-4" />
                <span>Location</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="semantic" className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="Try: 'Find Python developers with $100k+ salary in San Francisco'"
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
            </TabsContent>

            <TabsContent value="salary" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Minimum Salary</Label>
                  <Input
                    type="number"
                    placeholder="50000"
                    value={filters.salary_min || ''}
                    onChange={(e) => setFilters({...filters, salary_min: e.target.value ? parseInt(e.target.value) : undefined})}
                  />
                </div>
                <div>
                  <Label>Maximum Salary</Label>
                  <Input
                    type="number"
                    placeholder="150000"
                    value={filters.salary_max || ''}
                    onChange={(e) => setFilters({...filters, salary_max: e.target.value ? parseInt(e.target.value) : undefined})}
                  />
                </div>
              </div>
              <Button onClick={handleSearch} disabled={loading} className="w-full">
                {loading ? 'Searching...' : 'Search by Salary'}
              </Button>
            </TabsContent>

            <TabsContent value="location" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label>Location</Label>
                  <Select value={filters.location} onValueChange={(value) => setFilters({...filters, location: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select location" />
                    </SelectTrigger>
                    <SelectContent>
                      {suggestions?.locations?.map((location: string) => (
                        <SelectItem key={location} value={location}>
                          {location}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="remote"
                    checked={filters.remote}
                    onCheckedChange={(checked) => setFilters({...filters, remote: checked as boolean})}
                  />
                  <Label htmlFor="remote">Include remote positions</Label>
                </div>
              </div>
              <Button onClick={handleSearch} disabled={loading} className="w-full">
                {loading ? 'Searching...' : 'Search by Location'}
              </Button>
            </TabsContent>
          </Tabs>
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
                {results.map((result, index) => (
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
                            {result.salary && (
                              <p className="text-sm text-green-600">{formatSalary(result.salary)}</p>
                            )}
                            {result.experience && (
                              <p className="text-sm text-blue-600">{result.experience} years experience</p>
                            )}
                          </div>
                        ) : (
                          <div>
                            <h3 className="font-semibold">{result.title || 'Unknown'}</h3>
                            <p className="text-sm text-gray-600">{result.company || 'Unknown Company'}</p>
                            {result.location && (
                              <p className="text-sm text-gray-500">{result.location}</p>
                            )}
                            {result.salary && (
                              <p className="text-sm text-green-600">{formatSalary(result.salary)}</p>
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

      {/* Quick Actions */}
      {suggestions && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5" />
              <span>Quick Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Popular Queries</h4>
                <div className="grid grid-cols-2 gap-2">
                  {suggestions.popular_queries?.slice(0, 6).map((query: string, index: number) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setQuery(query);
                        setActiveTab('semantic');
                        performAdvancedSearch();
                      }}
                      className="text-left justify-start h-auto p-2"
                    >
                      <span className="text-xs">{query}</span>
                    </Button>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">Salary Ranges</h4>
                <div className="grid grid-cols-2 gap-2">
                  {suggestions.salary_ranges?.map((range: any, index: number) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setFilters({
                          ...filters,
                          salary_min: range.min,
                          salary_max: range.max
                        });
                        setActiveTab('salary');
                        performSalarySearch();
                      }}
                      className="text-left justify-start h-auto p-2"
                    >
                      <span className="text-xs">{range.label}</span>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdvancedNLWebSearch; 