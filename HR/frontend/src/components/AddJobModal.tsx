import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Job } from "./JobsTable";
import api from '@/services/api';
import { Loader2 } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

interface AddJobModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (job: any) => void;
  editJob?: Job | null;
}

export const AddJobModal = ({ open, onOpenChange, onSave, editJob }: AddJobModalProps) => {
  // Form state
  const [formData, setFormData] = useState({
    title: editJob?.title || "",
    description: editJob?.description || "",
    status: editJob?.status || 'Active',
  });

  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [backendError, setBackendError] = useState('');
  // Remove all job_title and jobTitles logic
  // In handleSave, remove finalJobTitleId and related logic

  // Reset form when editJob changes
  useEffect(() => {
    if (editJob) {
      setFormData({
        title: editJob.title || "",
        description: editJob.description || "",
        status: editJob.status || 'Active',
      });
    }
  }, [editJob]);

  const handleChange = (field: keyof typeof formData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSave = async () => {
    // Validate required fields
    const newErrors: Record<string, string> = {};
    
    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    }
    if (!formData.description.trim()) {
      newErrors.description = "Description is required";
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setBackendError('');
      return;
    }

    setIsSubmitting(true);
    setErrors({});
    setBackendError('');

    try {
      // Prepare data for API
      const jobData = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        status: formData.status === 'Active' ? 'open' : 
               formData.status === 'Inactive' ? 'closed' : 'draft'
      };

      await onSave(jobData);
      
      // Reset form if this was a new job
      if (!editJob) {
        setFormData({
          title: "",
          description: "",
          status: 'Active'
        });
      }
      
      onOpenChange(false);
    } catch (error: any) {
      setBackendError(
        error?.response?.data?.detail || 
        error?.response?.data?.message || 
        'Failed to save job. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (editJob) {
      setFormData({
        title: editJob.title || "",
        description: editJob.description || "",
        status: editJob.status || 'Active',
      });
    }
    setErrors({});
    setBackendError('');
    onOpenChange(false);
  };

  const statusVariant = {
    Active: "default",
    Inactive: "secondary",
    Draft: "outline"
  } as const;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-gray-900 dark:text-white">
            {editJob ? 'Edit Job Posting' : 'Create New Job Posting'}
          </DialogTitle>
          <DialogDescription className="text-gray-600 dark:text-gray-400">
            {editJob 
              ? 'Update the details below to modify this job posting.' 
              : 'Fill in the required information to create a new job posting.'
            }
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6 py-2">
          {/* Main Information Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <h3 className="font-medium text-gray-900 dark:text-white">Job Information</h3>
              <Separator className="flex-1" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Position Title */}
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="title" className="text-gray-700 dark:text-gray-300">
                  Position Title <span className="text-red-500">*</span>
            </Label>
            <Input
              id="title"
                  placeholder="e.g. Senior Software Engineer"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  className={`bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 ${
                    errors.title ? 'border-red-500' : ''
                  }`}
            />
            {errors.title && (
                  <p className="text-sm text-red-500">{errors.title}</p>
            )}
          </div>

              {/* Description */}
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="description" className="text-gray-700 dark:text-gray-300">
                  Description <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="description"
                  placeholder="Describe the role, responsibilities, and impact..."
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
              rows={4}
                  className={`bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 min-h-[120px] ${
                    errors.description ? 'border-red-500' : ''
                  }`}
            />
                {errors.description && (
                  <p className="text-sm text-red-500">{errors.description}</p>
                )}
              </div>
            </div>
          </div>

          {/* Job Details Section */}
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 space-y-4">
            <div className="flex items-center gap-3">
              <h3 className="font-medium text-gray-900 dark:text-white">Position Details</h3>
              <Separator className="flex-1" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Status */}
          <div className="space-y-2">
                <Label htmlFor="status" className="text-gray-700 dark:text-gray-300">
                  Status <span className="text-red-500">*</span>
            </Label>
                <Select 
                  value={formData.status} 
                  onValueChange={(value) => handleChange('status', value)}
                >
                  <SelectTrigger className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600">
                    <SelectValue>
                      <Badge variant={statusVariant[formData.status as keyof typeof statusVariant]}>
                        {formData.status}
                      </Badge>
                    </SelectValue>
              </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600">
                    <SelectItem value="Active" className="hover:bg-gray-100 dark:hover:bg-gray-700">
                      <Badge variant="default">Active</Badge>
                    </SelectItem>
                    <SelectItem value="Inactive" className="hover:bg-gray-100 dark:hover:bg-gray-700">
                      <Badge variant="secondary">Inactive</Badge>
                    </SelectItem>
                    <SelectItem value="Draft" className="hover:bg-gray-100 dark:hover:bg-gray-700">
                      <Badge variant="outline">Draft</Badge>
                    </SelectItem>
              </SelectContent>
            </Select>
              </div>
            </div>
          </div>

          {/* Error message */}
          {backendError && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg text-red-600 dark:text-red-400 text-sm">
              {backendError}
            </div>
          )}
        </div>

        {/* Dialog Footer */}
        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-4">
          <Button 
            type="button" 
            variant="outline" 
            onClick={handleCancel}
            disabled={isSubmitting}
            className="border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            Cancel
          </Button>
          <Button 
            type="button" 
            onClick={handleSave}
            disabled={isSubmitting}
            className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {editJob ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              editJob ? 'Update Job' : 'Create Job'
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};