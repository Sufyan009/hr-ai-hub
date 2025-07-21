import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Plus, 
  Eye, 
  Edit, 
  Trash2, 
  Download,
  Mail,
  Phone,
  MapPin,
  Briefcase
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import {    
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import axios from 'axios';
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { useToast } from '@/hooks/use-toast';
import { useLocation } from 'react-router-dom';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

interface Candidate {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  job_title: { name: string };
  candidate_stage: string;
  current_salary: number;
  expected_salary: number;
  years_of_experience: number;
  communication_skills: { name: string };
  city: { name: string };
  source: { name: string };
  notes: string;
  resume?: string;
  avatar?: string;
}

const PAGE_SIZE = 15;

const CandidateList: React.FC = () => {
  const { toast } = useToast();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStage, setSelectedStage] = useState('all');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const [jobTitles, setJobTitles] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [sources, setSources] = useState<string[]>([]);
  const [commSkills, setCommSkills] = useState<string[]>([]);
  const [filterPopoverOpen, setFilterPopoverOpen] = useState(false);
  const [pendingFilters, setPendingFilters] = useState({
    job_title: '',
    city: '',
    source: '',
    communication_skills: '',
    candidate_stage: '',
  });
  const [filtersLoading, setFiltersLoading] = useState(true);

  const handlePendingFilterChange = (field: string, value: string) => {
    setPendingFilters(prev => ({ ...prev, [field]: value }));
  };
  const handleApplyFilters = () => {
    setCustomFilters(Object.entries(pendingFilters).filter(([_, v]) => v).map(([field, value]) => ({ field, value })));
    setFilterPopoverOpen(false);
  };
  const handleClearAllFilters = () => {
    setCustomFilters([]);
    setPendingFilters({ job_title: '', city: '', source: '', communication_skills: '', candidate_stage: '' });
    setFilterPopoverOpen(false);
  };

  const filterFields = [
    { label: 'Job Title', value: 'job_title', options: jobTitles },
    { label: 'City', value: 'city', options: cities },
    { label: 'Source', value: 'source', options: sources },
    { label: 'Communication Skills', value: 'communication_skills', options: commSkills },
    { label: 'Stage', value: 'candidate_stage', options: ['applied','screening','technical','interview','offer','hired'] },
  ];
  const [customFilters, setCustomFilters] = useState<{ field: string, value: string }[]>([]);
  const [addingFilter, setAddingFilter] = useState(false);
  const [newFilterField, setNewFilterField] = useState('');
  const [newFilterValue, setNewFilterValue] = useState('');

  const handleAddFilter = () => {
    if (newFilterField && newFilterValue) {
      setCustomFilters([...customFilters, { field: newFilterField, value: newFilterValue }]);
      setAddingFilter(false);
      setNewFilterField('');
      setNewFilterValue('');
    }
  };
  const handleRemoveFilter = (idx: number) => {
    setCustomFilters(customFilters.filter((_, i) => i !== idx));
  };

  useEffect(() => {
    setFiltersLoading(true);
    const token = localStorage.getItem('authToken');
    const fetchFilterOptions = async () => {
      try {
        const [jtRes, cityRes, sourceRes, commRes] = await Promise.all([
          axios.get('http://localhost:8000/api/jobtitles/', { headers: { 'Authorization': `Token ${token}` } }),
          axios.get('http://localhost:8000/api/cities/', { headers: { 'Authorization': `Token ${token}` } }),
          axios.get('http://localhost:8000/api/sources/', { headers: { 'Authorization': `Token ${token}` } }),
          axios.get('http://localhost:8000/api/communicationskills/', { headers: { 'Authorization': `Token ${token}` } }),
        ]);
        setJobTitles(jtRes.data.map((jt: any) => jt.name));
        setCities(cityRes.data.map((c: any) => c.name));
        setSources(sourceRes.data.map((s: any) => s.name));
        setCommSkills(commRes.data.map((cs: any) => cs.name));
      } catch (error) {
        toast({ title: 'Error fetching filters', description: 'Could not load filter options.', variant: 'destructive' });
      } finally {
        setFiltersLoading(false);
      }
    };
    fetchFilterOptions();
  }, [toast]);

  useEffect(() => {
    const fetchCandidates = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        params.append('page', String(page));
        if (search) params.append('search', search);
        customFilters.forEach(f => params.append(f.field, f.value));
        const res = await axios.get(`http://localhost:8000/api/candidates/?${params.toString()}`);
        setCandidates(res.data.results);
        setCount(res.data.count);
      } catch (err) {
        setError('Failed to load candidates.');
      } finally {
        setLoading(false);
      }
    };
    fetchCandidates();
  }, [page, search, customFilters]);

  useEffect(() => {
    // On mount, check for ?stage= in the URL
    const params = new URLSearchParams(location.search);
    const stage = params.get('stage');
    if (stage) setSelectedStage(stage);
  }, [location.search]);

  const getStageColor = (stage: string) => {
    switch (stage.toLowerCase()) {
      case 'applied':
        return 'bg-muted text-muted-foreground';
      case 'screening':
        return 'bg-blue-100 text-blue-800';
      case 'technical':
        return 'bg-purple-100 text-purple-800';
      case 'interview':
        return 'bg-orange-100 text-orange-800';
      case 'offer':
        return 'bg-green-100 text-green-800';
      case 'hired':
        return 'bg-success text-success-foreground';
      case 'rejected':
        return 'bg-destructive text-destructive-foreground';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  // Remove filteredCandidates, use candidates directly from backend

  const totalPages = Math.ceil(count / PAGE_SIZE);

  // Smart pagination window
  const getPageNumbers = () => {
    const window = 2;
    let pages = [];
    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 ||
        i === totalPages ||
        (i >= page - window && i <= page + window)
      ) {
        pages.push(i);
      } else if (
        (i === page - window - 1 && page - window - 1 > 1) ||
        (i === page + window + 1 && page + window + 1 < totalPages)
      ) {
        pages.push('...');
      }
    }
    // Remove consecutive '...'
    return pages.filter((v, i, arr) => v !== '...' || arr[i - 1] !== '...');
  };

  // Delete functionality
  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this candidate?')) return;
    setDeletingId(id);
    try {
      await axios.delete(`http://localhost:8000/api/candidates/${id}/`);
      setCandidates(candidates.filter(c => c.id !== id));
      setCount(count - 1);
      toast({ title: 'Candidate deleted', description: 'The candidate has been removed.' });
    } catch (err) {
      toast({ title: 'Error', description: 'Failed to delete candidate.', variant: 'destructive' });
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="flex flex-col sm:flex-row flex-wrap justify-between items-center mb-6 gap-4 sticky top-0 z-30 bg-white dark:bg-gray-900/90 dark:backdrop-blur dark:shadow dark:text-gray-100 rounded animate-fade-in">
        <input
          className="border rounded px-4 py-2 w-full sm:w-1/3 focus:outline-primary"
          placeholder="Search candidates..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
        <div className="flex flex-wrap gap-2 items-center">
          <Popover open={filterPopoverOpen} onOpenChange={setFilterPopoverOpen}>
            <PopoverTrigger asChild>
              <Button variant="outline" className="gap-2">
                <Filter className="h-4 w-4" />
                Filters
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="space-y-3">
                <div className="font-semibold mb-2">Filter Candidates</div>
                {filtersLoading ? (
                  <div className="space-y-2">
                    <div className="h-8 bg-muted rounded animate-pulse" />
                    <div className="h-8 bg-muted rounded animate-pulse" />
                    <div className="h-8 bg-muted rounded animate-pulse" />
                    <div className="h-8 bg-muted rounded animate-pulse" />
                    <div className="h-8 bg-muted rounded animate-pulse" />
                  </div>
                ) : (
                  <>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <select title="Job Title" className="border rounded px-2 py-1 w-full" value={pendingFilters.job_title} onChange={e => handlePendingFilterChange('job_title', e.target.value)}>
                          <option value="">All Job Titles</option>
                          {jobTitles.map(jt => <option key={jt} value={jt}>{jt}</option>)}
                        </select>
                      </TooltipTrigger>
                      <TooltipContent>Select a job title to filter candidates</TooltipContent>
                    </Tooltip>
                    {jobTitles[0] === 'No job titles available' && <div className="text-xs text-muted-foreground">No job titles found in the system.</div>}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <select title="City" className="border rounded px-2 py-1 w-full" value={pendingFilters.city} onChange={e => handlePendingFilterChange('city', e.target.value)}>
                          <option value="">All Cities</option>
                          {cities.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </TooltipTrigger>
                      <TooltipContent>Select a city to filter candidates</TooltipContent>
                    </Tooltip>
                    {cities[0] === 'No cities available' && <div className="text-xs text-muted-foreground">No cities found in the system.</div>}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <select title="Source" className="border rounded px-2 py-1 w-full" value={pendingFilters.source} onChange={e => handlePendingFilterChange('source', e.target.value)}>
                          <option value="">All Sources</option>
                          {sources.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                      </TooltipTrigger>
                      <TooltipContent>Select a source to filter candidates</TooltipContent>
                    </Tooltip>
                    {sources[0] === 'No sources available' && <div className="text-xs text-muted-foreground">No sources found in the system.</div>}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <select title="Communication Skills" className="border rounded px-2 py-1 w-full" value={pendingFilters.communication_skills} onChange={e => handlePendingFilterChange('communication_skills', e.target.value)}>
                          <option value="">All Communication Skills</option>
                          {commSkills.map(cs => <option key={cs} value={cs}>{cs}</option>)}
                        </select>
                      </TooltipTrigger>
                      <TooltipContent>Select communication skills to filter candidates</TooltipContent>
                    </Tooltip>
                    {commSkills[0] === 'No skills available' && <div className="text-xs text-muted-foreground">No communication skills found in the system.</div>}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <select title="Stage" className="border rounded px-2 py-1 w-full" value={pendingFilters.candidate_stage} onChange={e => handlePendingFilterChange('candidate_stage', e.target.value)}>
                          <option value="">All Stages</option>
                          <option value="applied">Applied</option>
                          <option value="screening">Screening</option>
                          <option value="technical">Technical</option>
                          <option value="interview">Interview</option>
                          <option value="offer">Offer</option>
                          <option value="hired">Hired</option>
                        </select>
                      </TooltipTrigger>
                      <TooltipContent>Select a stage to filter candidates</TooltipContent>
                    </Tooltip>
                  </>
                )}
                <div className="flex gap-2 mt-2">
                  <Button size="sm" className="flex-1" onClick={handleApplyFilters} disabled={filtersLoading}>Apply</Button>
                  <Button size="sm" variant="ghost" className="flex-1" onClick={handleClearAllFilters} disabled={filtersLoading}>Clear All</Button>
                </div>
              </div>
            </PopoverContent>
          </Popover>
          {customFilters.map((f, idx) => (
            <span key={f.field + f.value} className="flex items-center gap-1 bg-primary/10 text-primary px-2 py-1 rounded-full text-xs animate-fade-in">
              {filterFields.find(ff => ff.value === f.field)?.label || f.field}: {f.value}
              <button className="ml-1 text-primary hover:text-destructive" onClick={() => handleRemoveFilter(idx)}>&times;</button>
            </span>
          ))}
        </div>
        <Button variant="outline" className="gap-2">
          <Download className="h-4 w-4" />
          Export
        </Button>
        <Button 
          className="bg-gradient-primary hover:shadow-glow transition-all duration-300"
          onClick={() => window.location.href = '/candidates/new'}
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Candidate
        </Button>
      </div>
      <div className="overflow-x-auto rounded-lg shadow border bg-white dark:bg-gray-900 dark:text-gray-100">
        {loading ? (
          <div className="p-8">
            <div className="h-8 bg-muted rounded animate-pulse mb-2" />
            <div className="h-8 bg-muted rounded animate-pulse mb-2" />
            <div className="h-8 bg-muted rounded animate-pulse mb-2" />
            <div className="h-8 bg-muted rounded animate-pulse mb-2" />
            <div className="h-8 bg-muted rounded animate-pulse mb-2" />
          </div>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left">Position</th>
                <th className="px-4 py-3 text-left">Stage</th>
                <th className="px-4 py-3 text-left">Experience</th>
                <th className="px-4 py-3 text-left">Location</th>
                <th className="px-4 py-3 text-left">Source</th>
                <th className="px-4 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((candidate, index) => (
                <tr
                  key={`candidate-${candidate.id}-${index}`}
                  className="hover:bg-primary/5 transition-colors group border-b last:border-b-0 animate-fade-in"
                >
                  <td className="px-4 py-3 font-medium flex items-center gap-2">
                    <div className="h-10 w-10 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground font-medium">
                      {((candidate.first_name || '')[0] || '') + ((candidate.last_name || '')[0] || '')}
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{candidate.first_name} {candidate.last_name}</p>
                      <div className="flex items-center gap-3 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {candidate.email}
                        </span>
                        <span className="flex items-center gap-1">
                          <Phone className="h-3 w-3" />
                          {candidate.phone_number}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-block bg-muted text-muted-foreground rounded px-2 py-1 text-xs">
                      {candidate.job_title.name}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge className={getStageColor(candidate.candidate_stage)}>
                      {candidate.candidate_stage}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">{candidate.years_of_experience ? `${candidate.years_of_experience} years` : '—'}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      {candidate.city.name}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      {candidate.source.name}
                    </div>
                  </td>
                  <td className="px-4 py-3 flex gap-2 items-center">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button className="hover:text-primary transition-colors" onClick={() => window.location.href = `/candidates/${candidate.id}`}>
                          <span className="sr-only">View</span>
                          <Eye className="h-5 w-5" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>View</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button className="hover:text-primary transition-colors" onClick={() => window.location.href = `/candidates/${candidate.id}/edit`}>
                          <span className="sr-only">Edit</span>
                          <Edit className="h-5 w-5" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Edit</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          className={`hover:text-destructive transition-colors ${deletingId === candidate.id ? 'opacity-50 pointer-events-none' : ''}`}
                          onClick={() => handleDelete(candidate.id)}
                          disabled={deletingId === candidate.id}
                        >
                          <span className="sr-only">Delete</span>
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>Delete</TooltipContent>
                    </Tooltip>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      {/* Pagination controls */}
      <div className="flex justify-center mt-6 gap-1 flex-wrap">
        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
          className="px-3 py-1 rounded border bg-white hover:bg-primary/10 disabled:opacity-50"
        >
          Previous
        </button>
        {getPageNumbers().map((p, idx) =>
          p === '...'
            ? <span key={`ellipsis-${idx}`} className="px-2 py-1">...</span>
            : <button
                key={`page-${p}-${idx}`}
                onClick={() => setPage(Number(p))}
                className={`px-3 py-1 rounded border ${page === p ? 'bg-primary text-white' : 'bg-white hover:bg-primary/10'}`}
              >
                {p}
              </button>
        )}
        <button
          disabled={page === totalPages}
          onClick={() => setPage(page + 1)}
          className="px-3 py-1 rounded border bg-white hover:bg-primary/10 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default CandidateList;