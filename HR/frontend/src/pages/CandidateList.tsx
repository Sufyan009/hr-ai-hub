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
  Briefcase,
  ChevronDown,
  SortAsc,
  SortDesc,
  User,
  Link2,
  X,
  Upload
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
import api from '@/services/api';
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { useToast } from '@/hooks/use-toast';
import { useLocation, useNavigate } from 'react-router-dom';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useDebounce } from '@/hooks/useDebounce';
import { DeleteConfirmationModal } from '@/components/DeleteConfirmationModal';
import BulkUploadModal from '../components/BulkUploadModal';

interface Candidate {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  job_title_detail?: { name: string };
  candidate_stage: string;
  current_salary: number;
  expected_salary: number;
  years_of_experience: number;
  communication_skills_detail?: { name: string };
  city_detail?: { name: string };
  source_detail?: { name: string };
  notes: string;
  resume?: string;
  avatar?: string;
}

const PAGE_SIZE = 15;

const CandidateList: React.FC = () => {
  const { toast } = useToast();
  const location = useLocation();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 400);
  const [selectedStage, setSelectedStage] = useState('all');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest' | 'az' | 'za' | 'most_exp' | 'least_exp'>('newest');

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
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [candidateToDelete, setCandidateToDelete] = useState<Candidate | null>(null);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const sessionId = 'candidate-list-session'; // Placeholder, ideally from context or props
  const authToken = 'dummy-token'; // Placeholder, ideally from context or props

  const handlePendingFilterChange = (field: string, value: string) => {
    setPendingFilters(prev => ({ ...prev, [field]: value }));
    setCustomFilters(prev => {
      const filtered = prev.filter(f => f.field !== field);
      if (!value) return filtered;
      return [...filtered, { field, value }];
    });
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

  const getOrderingParam = () => {
    switch (sortOrder) {
      case 'newest': return '-id';
      case 'oldest': return 'id';
      case 'az': return 'first_name';
      case 'za': return '-first_name';
      case 'most_exp': return '-years_of_experience';
      case 'least_exp': return 'years_of_experience';
      default: return '-id';
    }
  };

  useEffect(() => {
    setFiltersLoading(true);
    const fetchFilterOptions = async () => {
      try {
        const [jtRes, cityRes, sourceRes, commRes] = await Promise.all([
          api.get('/jobtitles/'),
          api.get('/cities/'),
          api.get('/sources/'),
          api.get('/communicationskills/'),
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
        if (debouncedSearch) params.append('search', debouncedSearch);
        customFilters.forEach(f => params.append(f.field, f.value));
        params.append('ordering', getOrderingParam());
        const res = await api.get(`/candidates/?${params.toString()}`);
        setCandidates(res.data.results);
        setCount(res.data.count);
      } catch (err) {
        setError('Failed to load candidates.');
      } finally {
        setLoading(false);
      }
    };
    fetchCandidates();
  }, [page, debouncedSearch, customFilters, sortOrder]);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const stage = params.get('stage');
    if (stage) setSelectedStage(stage);
  }, [location.search]);

  const getStageColor = (stage: string) => {
    switch (stage.toLowerCase()) {
      case 'applied': return 'bg-gray-100 text-gray-800';
      case 'screening': return 'bg-blue-100 text-blue-800';
      case 'technical': return 'bg-purple-100 text-purple-800';
      case 'interview': return 'bg-orange-100 text-orange-800';
      case 'offer': return 'bg-green-100 text-green-800';
      case 'hired': return 'bg-teal-100 text-teal-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const totalPages = Math.ceil(count / PAGE_SIZE);

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
    return pages.filter((v, i, arr) => v !== '...' || arr[i - 1] !== '...');
  };

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      await api.delete(`/candidates/${id}/`);
      setCandidates(candidates.filter(c => c.id !== id));
      setCount(count - 1);
      toast({ title: 'Candidate deleted', description: 'The candidate has been removed.' });
    } catch (err) {
      toast({ title: 'Error', description: 'Failed to delete candidate.', variant: 'destructive' });
    } finally {
      setDeletingId(null);
      setShowDeleteModal(false);
      setCandidateToDelete(null);
    }
  };

  const handleExport = async () => {
    try {
      const params = new URLSearchParams();
      customFilters.forEach(f => params.append(f.field, f.value));
      params.append('ordering', getOrderingParam());
      const res = await api.get(`/candidates/export/csv/?${params.toString()}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'candidates.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch {
      toast({ title: 'Export Failed', description: 'Could not export candidates.', variant: 'destructive' });
    }
  };

  const handleView = (id: number) => {
    navigate(`/candidates/${id}`);
  };

  const handleEdit = (id: number) => {
    navigate(`/candidates/${id}/edit`);
  };

  // Implement handleRemoveFilter
  const handleRemoveFilter = (idx: number) => {
    setCustomFilters(prev => prev.filter((_, i) => i !== idx));
  };

  // Function to refresh candidate list (replace with your actual refresh logic)
  const refreshCandidates = () => {
    // This function will be called when bulk upload is successful to refresh the candidate list
    // For now, we'll just re-fetch the current page data
    setLoading(true);
    const fetchCandidates = async () => {
      try {
        const params = new URLSearchParams();
        params.append('page', String(page));
        if (debouncedSearch) params.append('search', debouncedSearch);
        customFilters.forEach(f => params.append(f.field, f.value));
        params.append('ordering', getOrderingParam());
        const res = await api.get(`/candidates/?${params.toString()}`);
        setCandidates(res.data.results);
        setCount(res.data.count);
      } catch (err) {
        setError('Failed to load candidates.');
      } finally {
        setLoading(false);
      }
    };
    fetchCandidates();
  };

  // Handle bulk upload success
  const handleBulkSuccess = (summary) => {
    refreshCandidates();
    toast({
      title: 'Bulk Upload Successful',
      description: `Added: ${summary.total - summary.failedCount}, Errors: ${summary.failedCount}, Duplicates: ${summary.duplicates}`,
    });
    setShowBulkModal(false);
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-10 bg-gray-50 dark:bg-gray-900 rounded-lg">
        <div className="text-red-600 dark:text-red-400 font-medium mb-4 text-lg">{error}</div>
        <Button
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg px-6 py-2"
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <Card className="shadow-xl border-0">
        <CardHeader className="border-b bg-gray-50 dark:bg-gray-800">
          <CardTitle className="text-2xl font-semibold text-gray-800 dark:text-gray-100">
            Candidate Management
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {/* Header Row */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <div className="flex items-center w-full sm:w-auto">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  className="pl-10 pr-10 py-2 rounded-lg border-gray-300 focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
          placeholder="Search candidates..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
                {searchTerm && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 hover:bg-gray-100 dark:hover:bg-gray-600"
                    onClick={() => { setSearchTerm(''); }}
                    aria-label="Clear search"
                  >
                    <X className="h-4 w-4 text-gray-500" />
                  </Button>
                )}
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
          <Popover open={filterPopoverOpen} onOpenChange={setFilterPopoverOpen}>
            <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="h-10 px-4 text-sm font-medium flex items-center gap-2 border-gray-300 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700"
                  >
                <Filter className="h-4 w-4" />
                Filters
              </Button>
            </PopoverTrigger>
                <PopoverContent className="w-80 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Filter Candidates</h3>
                    {filtersLoading ? (
              <div className="space-y-3">
                        {[...Array(5)].map((_, i) => (
                          <div key={i} className="h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
                        ))}
                  </div>
                ) : (
                  <>
                        {filterFields.map(field => (
                          <div key={field.value}>
                            <label className="text-sm font-medium text-gray-700 dark:text-gray-200">{field.label}</label>
                            <select
                              className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 py-2 px-3 text-sm"
                              value={pendingFilters[field.value as keyof typeof pendingFilters]}
                              onChange={e => handlePendingFilterChange(field.value, e.target.value)}
                              title={field.label}
                            >
                              <option value="">All {field.label}s</option>
                              {field.options.map(option => (
                                <option key={option} value={option}>{option}</option>
                              ))}
                        </select>
                            {field.options[0]?.includes('No') && (
                              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                No {field.label.toLowerCase()}s found in the system.
                              </div>
                            )}
                          </div>
                        ))}
                        <div className="flex gap-2 pt-2">
                          <Button
                            variant="outline"
                            className="flex-1 text-sm"
                            onClick={handleClearAllFilters}
                            disabled={filtersLoading}
                          >
                            Clear All
                          </Button>
                          <Button
                            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm"
                            onClick={handleApplyFilters}
                            disabled={filtersLoading}
                          >
                            Apply
                          </Button>
                        </div>
                  </>
                )}
              </div>
            </PopoverContent>
          </Popover>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    className="h-10 px-4 text-sm font-medium flex items-center gap-2 border-gray-300 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700"
                  >
                    <SortAsc className="h-4 w-4" />
                    Sort
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="bg-white dark:bg-gray-800 shadow-lg rounded-lg">
                  <DropdownMenuItem
                    onClick={() => setSortOrder('newest')}
                    className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <SortDesc className="h-4 w-4" /> Newest First
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => setSortOrder('oldest')}
                    className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <SortAsc className="h-4 w-4" /> Oldest First
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => setSortOrder('az')}
                    className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <User className="h-4 w-4" /> A-Z (First Name)
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => setSortOrder('za')}
                    className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <User className="h-4 w-4" /> Z-A (First Name)
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => setSortOrder('most_exp')}
                    className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <User className="h-4 w-4" /> Most Experience
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => setSortOrder('least_exp')}
                    className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <User className="h-4 w-4" /> Least Experience
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <Button
                variant="outline"
                className="h-10 px-4 text-sm font-medium flex items-center gap-2 border-gray-300 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700"
                onClick={handleExport}
              >
                <Download className="h-4 w-4" /> Export
        </Button>
        <Button 
                className="h-10 px-4 text-sm font-semibold flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
                onClick={() => navigate('/candidates/new')}
        >
                <Plus className="h-4 w-4" /> Add Candidate
        </Button>
        <Button 
                className="h-10 px-4 text-sm font-semibold flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white"
                onClick={() => setShowBulkModal(true)}
        >
                <Upload className="h-4 w-4" /> Bulk Upload
        </Button>
      </div>
          </div>

          {/* Filters Display */}
          {customFilters.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {customFilters.map((filter, idx) => (
                <Badge
                  key={idx}
                  className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-3 py-1"
                >
                  {filterFields.find(f => f.value === filter.field)?.label}: {filter.value}
                  <button
                    onClick={() => handleRemoveFilter(idx)}
                    className="ml-2 hover:text-blue-600"
                    title={`Remove ${filterFields.find(f => f.value === filter.field)?.label} filter`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}

          {/* Table */}
          <div className="overflow-x-auto rounded-lg border bg-white dark:bg-gray-800">
            {loading ? (
              <div className="p-6 space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <Table className="min-w-full">
                <TableHeader className="bg-gray-50 dark:bg-gray-700">
                  <TableRow>
                    <TableHead className="px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-100">Name</TableHead>
                    <TableHead className="px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-100">Position</TableHead>
                    <TableHead className="px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-100">Stage</TableHead>
                    <TableHead className="px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-100">Experience</TableHead>
                    <TableHead className="px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-100">Location</TableHead>
                    <TableHead className="px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-100">Source</TableHead>
                    <TableHead className="px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-100">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {candidates.map(candidate => (
                    <TableRow
                      key={candidate.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                >
                      <TableCell className="px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-semibold text-lg uppercase">
                            {((candidate.first_name || '')[0] || '') + ((candidate.last_name || '')[0] || '') || <User className="h-5 w-5" />}
                    </div>
                          <div className="flex flex-col">
                            <span className="font-medium text-gray-800 dark:text-gray-100">{`${candidate.first_name || ''} ${candidate.last_name || ''}`.trim()}</span>
                            <span className="text-sm text-gray-500 dark:text-gray-400">{candidate.email}</span>
                            <span className="text-sm text-gray-500 dark:text-gray-400">{candidate.phone_number}</span>
                      </div>
                    </div>
                      </TableCell>
                      <TableCell className="px-4 py-4">
                        <Badge variant="secondary" className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-100">
                          <Briefcase className="h-3 w-3 mr-1 text-blue-500" />
                          {candidate.job_title_detail?.name || '—'}
                        </Badge>
                      </TableCell>
                      <TableCell className="px-4 py-4">
                    <Badge className={getStageColor(candidate.candidate_stage)}>
                      {candidate.candidate_stage}
                    </Badge>
                      </TableCell>
                      <TableCell className="px-4 py-4">
                        <span className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-300">
                          <Briefcase className="h-3 w-3" />
                          {candidate.years_of_experience ? `${candidate.years_of_experience} years` : '—'}
                        </span>
                      </TableCell>
                      <TableCell className="px-4 py-4">
                        <span className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-300">
                      <MapPin className="h-3 w-3" />
                          {candidate.city_detail?.name || '—'}
                        </span>
                      </TableCell>
                      <TableCell className="px-4 py-4">
                        <span className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-300">
                          <Link2 className="h-3 w-3" />
                          {candidate.source_detail?.name || '—'}
                        </span>
                      </TableCell>
                      <TableCell className="px-4 py-4">
                        <div className="flex gap-2">
                          <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleView(candidate.id)}
                                  className="hover:bg-blue-100 dark:hover:bg-blue-900"
                                >
                                  <Eye className="h-4 w-4 text-blue-600" />
                                </Button>
                      </TooltipTrigger>
                      <TooltipContent>View</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleEdit(candidate.id)}
                                  className="hover:bg-blue-100 dark:hover:bg-blue-900"
                                >
                                  <Edit className="h-4 w-4 text-blue-600" />
                                </Button>
                      </TooltipTrigger>
                      <TooltipContent>Edit</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                      <TooltipTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                          onClick={() => { setCandidateToDelete(candidate); setShowDeleteModal(true); }}
                                  className="hover:bg-red-100 dark:hover:bg-red-900"
                          disabled={deletingId === candidate.id}
                        >
                                  <Trash2 className="h-4 w-4 text-red-600" />
                                </Button>
                      </TooltipTrigger>
                      <TooltipContent>Delete</TooltipContent>
                    </Tooltip>
                          </TooltipProvider>
                        </div>
                      </TableCell>
                    </TableRow>
              ))}
                </TableBody>
              </Table>
        )}
      </div>

          {/* Pagination */}
          <div className="flex justify-center mt-6 gap-2 flex-wrap">
            <Button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
              className="px-4 py-2 text-sm font-medium bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
        >
          Previous
            </Button>
        {getPageNumbers().map((p, idx) =>
              p === '...' ? (
                <span key={`ellipsis-${idx}`} className="px-3 py-2 text-gray-500 dark:text-gray-400">...</span>
              ) : (
                <Button
                key={`page-${p}-${idx}`}
                onClick={() => setPage(Number(p))}
                  className={`px-4 py-2 text-sm font-medium ${
                    page === p
                      ? 'bg-blue-600 text-white'
                      : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
              >
                {p}
                </Button>
              )
        )}
            <Button
          disabled={page === totalPages}
          onClick={() => setPage(page + 1)}
              className="px-4 py-2 text-sm font-medium bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
        >
          Next
            </Button>
      </div>
        </CardContent>
      </Card>
      {showDeleteModal && candidateToDelete && (
  <DeleteConfirmationModal
    open={showDeleteModal}
    onOpenChange={setShowDeleteModal}
    onConfirm={() => handleDelete(candidateToDelete.id)}
    jobTitle={`${candidateToDelete.first_name} ${candidateToDelete.last_name}`}
    isDeleting={deletingId === candidateToDelete.id}
  />
)}
      <BulkUploadModal
        open={showBulkModal}
        onClose={() => setShowBulkModal(false)}
        onSuccess={handleBulkSuccess}
        sessionId={sessionId}
        authToken={authToken}
      />
    </div>
  );
};

export default CandidateList;