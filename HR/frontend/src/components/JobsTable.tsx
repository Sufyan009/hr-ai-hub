import { useState } from "react";
import { Trash2, Edit, ChevronUp, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export interface Job {
  id: string;
  title: string;
  description: string;
  status: 'Active' | 'Inactive';
  created_at: string; // Use snake_case to match backend
}

interface JobsTableProps {
  jobs: Job[];
  onDelete: (id: string) => void;
  onEdit?: (job: Job) => void;
  sortBy: 'title' | 'status' | 'createdAt';
  sortOrder: 'asc' | 'desc';
  onSort: (field: 'title' | 'status' | 'createdAt') => void;
}

const StatusBadge = ({ status }: { status: 'Active' | 'Inactive' }) => {
  return (
    <Badge 
      variant={status === 'Active' ? 'default' : 'secondary'}
      className={status === 'Active' 
        ? 'bg-success text-success-foreground hover:bg-success/80' 
        : 'bg-muted text-muted-foreground hover:bg-muted/80'
      }
    >
      {status}
    </Badge>
  );
};

const getStatusLabel = (status: string) => {
  if (status === 'open') return 'Active';
  if (status === 'closed') return 'Inactive';
  return status;
};

export const JobsTable = ({ 
  jobs, 
  onDelete, 
  onEdit, 
  sortBy, 
  sortOrder, 
  onSort 
}: JobsTableProps) => {
  const SortIcon = ({ field }: { field: 'title' | 'status' | 'createdAt' }) => {
    if (sortBy !== field) return <ChevronUp className="h-4 w-4 opacity-30" />;
    return sortOrder === 'asc' 
      ? <ChevronUp className="h-4 w-4" />
      : <ChevronDown className="h-4 w-4" />;
  };

  const formatDate = (date: any) => {
    if (!date) return '';
    let d = date;
    if (typeof date === 'string') {
      d = new Date(date);
    }
    if (!(d instanceof Date) || isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-admin-surface border-admin-border hover:bg-admin-surface">
            <TableHead className="w-[200px]">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSort('title')}
                className="h-auto p-0 font-semibold text-foreground hover:text-primary"
              >
                Job Title
                <SortIcon field="title" />
              </Button>
            </TableHead>
            <TableHead className="min-w-[300px]">Description</TableHead>
            <TableHead className="w-[120px]">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSort('status')}
                className="h-auto p-0 font-semibold text-foreground hover:text-primary"
              >
                Status
                <SortIcon field="status" />
              </Button>
            </TableHead>
            <TableHead className="w-[120px]">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSort('created_at')}
                className="h-auto p-0 font-semibold text-foreground hover:text-primary"
              >
                Created
                <SortIcon field="createdAt" />
              </Button>
            </TableHead>
            <TableHead className="w-[120px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobs.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                No jobs found
              </TableCell>
            </TableRow>
          ) : (
            jobs.map((job) => (
              <TableRow 
                key={job.id} 
                className="border-admin-border hover:bg-admin-surface/30 transition-colors"
              >
                <TableCell className="font-medium">{job.title}</TableCell>
                <TableCell className="text-muted-foreground">
                  <div className="max-w-xs truncate">
                    {job.description || 'No description'}
                  </div>
                </TableCell>
                <TableCell>
                  <StatusBadge status={getStatusLabel(job.status)} />
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {formatDate(job.created_at)}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    {onEdit && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onEdit(job)}
                        className="h-8 w-8 p-0 hover:bg-info/10 hover:text-info"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(job.id)}
                      className="h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
};