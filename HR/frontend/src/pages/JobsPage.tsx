import { useState, useEffect, useCallback, useMemo } from "react";
import { JobsTable, Job } from "@/components/JobsTable";
import { AddJobModal } from "@/components/AddJobModal";
import { DeleteConfirmationModal } from "@/components/DeleteConfirmationModal";
import { JobFilters } from "@/components/JobFilters";
import { JobsPagination } from "@/components/JobsPagination";
import { useToast } from "@/hooks/use-toast";
import { getJobs, createJob, updateJob, deleteJob } from '@/services/jobService';
import { useAuth } from '@/contexts/AuthContext';

// Define interfaces for better type safety
interface JobFilterParams {
  page: number;
  search?: string;
  status?: string;
  ordering?: string;
  page_size: number;
}

interface User {
  role: 'admin' | 'recruiter' | 'user';
}

// Define constants
const DEFAULT_PAGE_SIZE = 25;
const DEFAULT_SORT_BY = 'createdAt';
const DEFAULT_SORT_ORDER = 'desc';
const STATUS_MAP = {
  All: undefined,
  Active: 'open',
  Inactive: 'closed'
} as const;

const JobsPage = () => {
  const { toast } = useToast();
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<'All' | 'Active' | 'Inactive'>('All');
  const [sortBy, setSortBy] = useState<'title' | 'status' | 'createdAt'>(DEFAULT_SORT_BY);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>(DEFAULT_SORT_ORDER);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [jobToDelete, setJobToDelete] = useState<Job | null>(null);

  // Memoized permissions check
  const hasEditPermissions = useMemo(() => 
    user?.role === 'admin' || user?.role === 'recruiter',
    [user?.role]
  );

  // Fetch jobs with proper error handling
  const fetchJobs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params: JobFilterParams = {
        page: currentPage,
        search: searchTerm || undefined,
        status: STATUS_MAP[statusFilter],
        ordering: sortOrder === 'desc' ? `-${sortBy}` : sortBy,
        page_size: pageSize
      };

      const response = await getJobs(params);
      setJobs(response.data.results || response.data);
      setTotalCount(response.data.count || response.data.length || 0);
    } catch (err) {
      setError('Failed to load job postings. Please try again later.');
      toast({
        title: "Error",
        description: "Unable to fetch job postings",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, searchTerm, statusFilter, sortBy, sortOrder, pageSize, toast]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  // Handlers
  const handleSort = useCallback((field: 'title' | 'status' | 'createdAt') => {
    setSortBy(field);
    setSortOrder(prev => sortBy === field ? (prev === 'asc' ? 'desc' : 'asc') : 'asc');
    setCurrentPage(1);
  }, [sortBy]);

  const handlePageSizeChange = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1);
  }, []);

  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  }, []);

  const handleStatusFilterChange = useCallback((value: 'All' | 'Active' | 'Inactive') => {
    setStatusFilter(value);
    setCurrentPage(1);
  }, []);

  const handleAddJob = useCallback(() => {
    setEditingJob(null);
    setIsAddModalOpen(true);
  }, []);

  const handleEditJob = useCallback((job: Job) => {
    setEditingJob(job);
    setIsAddModalOpen(true);
  }, []);

  const handleSaveJob = useCallback(async (jobData: Omit<Job, 'id' | 'createdAt'>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const action = editingJob ? updateJob(editingJob.id, jobData) : createJob(jobData);
      await action;
      
      toast({
        title: editingJob ? "Job Updated" : "Job Created",
        description: `The job posting has been ${editingJob ? 'updated' : 'created'} successfully.`
      });

      setIsAddModalOpen(false);
      setEditingJob(null);
      await fetchJobs();
    } catch (err) {
      setError('Failed to save job posting. Please check your input.');
      toast({
        title: "Error",
        description: "Failed to save job posting",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  }, [editingJob, toast, fetchJobs]);

  const handleDeleteClick = useCallback((id: string | number) => {
    const job = jobs.find(j => j.id === id);
    if (job) {
      setJobToDelete(job);
      setIsDeleteModalOpen(true);
    }
  }, [jobs]);

  const handleDeleteConfirm = useCallback(async () => {
    if (!jobToDelete) return;
    
    setIsLoading(true);
    try {
      await deleteJob(jobToDelete.id);
      toast({
        title: "Job Deleted",
        description: `"${jobToDelete.title}" has been deleted successfully.`
      });
      setIsDeleteModalOpen(false);
      setJobToDelete(null);
      await fetchJobs();
    } catch (err) {
      setError('Failed to delete job posting.');
      toast({
        title: "Error",
        description: "Failed to delete job posting",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  }, [jobToDelete, toast, fetchJobs]);

  const handleDeleteCancel = useCallback(() => {
    setIsDeleteModalOpen(false);
    setJobToDelete(null);
  }, []);

  const totalPages = useMemo(() => Math.ceil(totalCount / pageSize), [totalCount, pageSize]);

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Job Postings Management</h1>
          <p className="text-muted-foreground">
            Efficiently manage job listings, create new postings, and monitor their status.
          </p>
        </header>

        <section className="mb-6">
          <JobFilters
            searchTerm={searchTerm}
            onSearchChange={handleSearchChange}
            statusFilter={statusFilter}
            onStatusFilterChange={handleStatusFilterChange}
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
            onAddJob={hasEditPermissions ? handleAddJob : undefined}
          />
        </section>

        <section className="mb-4">
          <p className="text-sm text-muted-foreground">
            {totalCount === 0
              ? 'No job postings found.'
              : `Showing ${jobs.length} of ${totalCount} job postings`}
          </p>
        </section>

        <section>
          <JobsTable
            jobs={jobs}
            onDelete={hasEditPermissions ? handleDeleteClick : undefined}
            onEdit={hasEditPermissions ? handleEditJob : undefined}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSort={handleSort}
          />
        </section>

        <section>
          <JobsPagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalCount}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
          />
        </section>

        <AddJobModal
          open={isAddModalOpen}
          onOpenChange={setIsAddModalOpen}
          onSave={handleSaveJob}
          editJob={editingJob}
        />

        {jobToDelete && (
          <DeleteConfirmationModal
            open={isDeleteModalOpen}
            onOpenChange={handleDeleteCancel}
            onConfirm={handleDeleteConfirm}
            jobTitle={jobToDelete.title}
          />
        )}

        {error && (
          <div className="text-red-500 mt-4" role="alert">
            {error}
          </div>
        )}
        
        {isLoading && (
          <div className="text-muted-foreground mt-4" aria-live="polite">
            Loading job postings...
          </div>
        )}
      </div>
    </div>
  );
};

export default JobsPage;