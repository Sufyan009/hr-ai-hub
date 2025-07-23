import { Search, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useEffect, useState } from 'react';
import api from '@/services/api';
import { Label } from '@/components/ui/label';

interface JobFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  statusFilter: 'All' | 'Active' | 'Inactive';
  onStatusFilterChange: (value: 'All' | 'Active' | 'Inactive') => void;
  pageSize: number;
  onPageSizeChange: (value: number) => void;
  onAddJob?: () => void;
  jobTitleFilter?: string;
  onJobTitleFilterChange?: (value: string) => void;
}

export const JobFilters = ({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  pageSize,
  onPageSizeChange,
  onAddJob,
  jobTitleFilter = '',
  onJobTitleFilterChange
}: JobFiltersProps) => {
  const [jobTitles, setJobTitles] = useState<{ id: number, name: string }[]>([]);
  useEffect(() => {
    const fetchJobTitles = async () => {
      try {
        const res = await api.get('/jobtitles/');
        setJobTitles(res.data);
      } catch {
        setJobTitles([]);
      }
    };
    fetchJobTitles();
  }, []);
  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center flex-1">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <input
            placeholder="Search by job title or keyword..."
            value={searchTerm}
            onChange={e => onSearchChange(e.target.value)}
            className="pl-10 bg-background border-border w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        {/* Job Title Autocomplete Dropdown */}
        {onJobTitleFilterChange && (
          <div className="flex items-center gap-2">
            <Label htmlFor="jobTitleSelect" className="text-sm text-muted-foreground whitespace-nowrap">Job Title:</Label>
            <select
              id="jobTitleSelect"
              title="Job Title"
              value={jobTitleFilter}
              onChange={e => onJobTitleFilterChange(e.target.value)}
              className="w-48 bg-background border border-border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">All Job Titles</option>
              {jobTitles.map(jt => (
                <option key={jt.id} value={jt.id}>{jt.name}</option>
              ))}
            </select>
          </div>
        )}
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select value={statusFilter} onValueChange={onStatusFilterChange}>
            <SelectTrigger className="w-32 bg-background border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-popover border-border">
              <SelectItem value="All">All Status</SelectItem>
              <SelectItem value="Active">Active</SelectItem>
              <SelectItem value="Inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {/* Page Size */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground whitespace-nowrap">Show:</span>
          <Select value={pageSize.toString()} onValueChange={value => onPageSizeChange(parseInt(value))}>
            <SelectTrigger className="w-20 bg-background border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-popover border-border">
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
              <SelectItem value="500">500</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      {/* Add Job Button */}
      {onAddJob && (
        <Button
          onClick={onAddJob}
          className="bg-primary hover:bg-primary/90 text-primary-foreground whitespace-nowrap"
        >
          Add New Job
        </Button>
      )}
    </div>
  );
};