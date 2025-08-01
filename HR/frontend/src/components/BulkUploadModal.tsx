import React, { useState, useRef, useEffect } from 'react';
import { Upload, X, File, AlertTriangle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ScrollArea } from '@/components/ui/scroll-area';
import axios from 'axios';

interface BulkUploadModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (summary: { total: number; failedCount: number; duplicates: number }) => void;
  sessionId: string;
  authToken: string;
}

interface UploadSummary {
  success: boolean;
  message?: string;
  preview?: any[];
  columns?: string[];
  missing_columns?: string[];
  duplicates?: number;
  failedCount?: number;
  errors?: { row: number; errors: string[] }[];
  added?: number;
}

const fieldOptions: Record<string, string[]> = {
  candidate_stage: ['Screening', 'Interview', 'Hired', 'Rejected'],
  communication_skills: ['Excellent', 'Good', 'Average', 'Poor'],
  city: ['New York', 'San Francisco', 'Lahore', 'Karachi', 'Faisalabad'],
  source: ['Company Website', 'Referral', 'LinkedIn', 'Other'],
  job_title: ['Software Engineer', 'Product Manager', 'Designer', 'HR Manager'],
};

const systemFields = [
  'ignore', // for Ignore
  'first_name', 'last_name', 'email', 'phone_number', 'job_title',
  'city', 'candidate_stage', 'communication_skills', 'years_of_experience',
  'expected_salary', 'source',
];
const requiredFields = ['first_name', 'last_name', 'email'];
const knownFields = [
  'first_name', 'last_name', 'email', 'phone_number', 'job_title',
  'city', 'candidate_stage', 'communication_skills', 'years_of_experience',
  'expected_salary', 'source',
];

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const DJANGO_API_URL = import.meta.env.VITE_DJANGO_API_URL || 'http://localhost:8000/api'; // Industry best practice: use env var for Django backend

const BulkUploadModal: React.FC<BulkUploadModalProps> = ({ open, onClose, onSuccess, sessionId, authToken }) => {
  const { toast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadSummary, setUploadSummary] = useState<UploadSummary | null>(null);
  const [duplicateMode, setDuplicateMode] = useState<'skip' | 'update' | 'flag'>('skip');
  const [preview, setPreview] = useState<any[] | null>(null);
  const [editedPreview, setEditedPreview] = useState<any[] | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({});
  const [cellErrors, setCellErrors] = useState<Record<string, string>>({});
  const [loadingPreview, setLoadingPreview] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [jobTitleOptions, setJobTitleOptions] = useState<{ id: number; name: string }[]>([]);
  const [cityOptions, setCityOptions] = useState<{ id: number; name: string }[]>([]);
  const [sourceOptions, setSourceOptions] = useState<{ id: number; name: string }[]>([]);
  const [commSkillOptions, setCommSkillOptions] = useState<{ id: number; name: string }[]>([]);

  useEffect(() => {
    if (!open) return;
    const fetchOptions = async () => {
      try {
        const [jt, ct, so, cs] = await Promise.all([
          axios.get(`${DJANGO_API_URL}/jobtitles/`, { headers: { Authorization: `Token ${authToken}` } }),
          axios.get(`${DJANGO_API_URL}/cities/`, { headers: { Authorization: `Token ${authToken}` } }),
          axios.get(`${DJANGO_API_URL}/sources/`, { headers: { Authorization: `Token ${authToken}` } }),
          axios.get(`${DJANGO_API_URL}/communicationskills/`, { headers: { Authorization: `Token ${authToken}` } }),
        ]);
        setJobTitleOptions(jt.data);
        setCityOptions(ct.data);
        setSourceOptions(so.data);
        setCommSkillOptions(cs.data);
      } catch (err) {
        // Optionally show a toast or error
      }
    };
    fetchOptions();
  }, [open, authToken]);

  const getIdByName = (options, name) => {
    const found = options.find(opt => opt.name.toLowerCase() === String(name).toLowerCase());
    return found ? found.id : null;
  };

  const requiredBackendFields = [
    'first_name', 'last_name', 'email', 'phone_number', 'job_title',
    'candidate_stage', 'current_salary', 'expected_salary', 'years_of_experience',
    'communication_skills', 'city', 'source',
  ];

  const validateCell = (col: string, value: string, rowIdx: number): string => {
    if (requiredFields.includes(col) && !value) return `${col.split('_').join(' ')} is required`;
    if (col === 'email' && value && !/^[^@]+@[^@]+\.[^@]+$/.test(value)) return 'Invalid email format';
    if (col === 'years_of_experience' && value && (isNaN(Number(value)) || Number(value) < 0)) return 'Must be a non-negative number';
    if (col === 'expected_salary' && value && (isNaN(Number(value)) || Number(value) <= 0)) return 'Must be a positive number';
    if (fieldOptions[col] && value && !fieldOptions[col].includes(value)) return `Must be one of: ${fieldOptions[col].join(', ')}`;
    return '';
  };

  const validatePreview = (data: any[]) => {
    const newErrors: Record<string, string> = {};
    data.forEach((row, rowIdx) => {
      Object.entries(row).forEach(([col, value]) => {
        const mappedCol = Object.keys(columnMapping).find(key => columnMapping[key] === col) || col;
        const error = validateCell(mappedCol, value as string, rowIdx);
        if (error) newErrors[`${rowIdx}-${col}`] = error;
      });
    });
    setCellErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const ext = selectedFile.name.split('.').pop()?.toLowerCase();
      if (ext !== 'csv' && ext !== 'xlsx') {
        setError('Please upload a valid CSV or Excel (.xlsx) file.');
        return;
      }
      if (selectedFile.size === 0) {
        setError('The selected file is empty. Please choose a file with data.');
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit.');
        return;
      }
      setFile(selectedFile);
      setError(null);
      setUploadSummary(null);
      setPreview(null);
      setEditedPreview(null);
      setColumns([]);
      setColumnMapping({});
      setCellErrors({});
      setLoadingPreview(true);
      handleUpload(selectedFile);
    }
  };

  const handleUpload = async (selectedFile: File) => {
    if (!selectedFile || selectedFile.size === 0) {
      setError('Please select a file to upload.');
      setLoadingPreview(false);
      return;
    }
    setUploading(true);
    setLoadingPreview(true);
    setError(null);
    setUploadSummary(null);
    setPreview(null);
    setEditedPreview(null);
    setColumns([]);
    setCellErrors({});
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('session_id', sessionId);
      formData.append('duplicate_mode', duplicateMode);
      formData.append('column_mapping', JSON.stringify(columnMapping));
      const response = await axios.post(`${API_URL}/chat/upload`, formData, {
        headers: { Authorization: `Token ${authToken}` },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(percent);
          }
        },
      });
      const summary: UploadSummary = response.data;
      setUploadSummary(summary);
      if (!summary.success) {
        setError(summary.message || 'Upload failed.');
        setLoadingPreview(false);
        return;
      }
      const allRows = summary.preview || [];
      setPreview(allRows);
      setEditedPreview(allRows ? JSON.parse(JSON.stringify(allRows)) : null);
      setColumns(summary.columns || (allRows.length > 0 ? Object.keys(allRows[0]) : []));
      setLoadingPreview(false);
      if (summary.missing_columns && summary.missing_columns.length > 0) {
        toast({
          title: 'Missing Columns',
          description: `The following required columns are missing: ${summary.missing_columns.join(', ')}`,
        });
      }
    } catch (err: any) {
      const errMsg = err.message || 'An error occurred during file upload. Please try again.';
      setError(errMsg);
      setLoadingPreview(false);
    } finally {
      setUploading(false);
      setLoadingPreview(false);
    }
  };

  const handleEditCell = (rowIdx: number, col: string, value: string) => {
    if (!editedPreview) return;
    const updated = editedPreview.map((row, i) =>
      i === rowIdx ? { ...row, [col]: value } : row
    );
    setEditedPreview(updated);
    const errMsg = validateCell(col, value, rowIdx);
    setCellErrors(prev => {
      const key = `${rowIdx}-${col}`;
      if (errMsg) return { ...prev, [key]: errMsg };
      const { [key]: _, ...rest } = prev;
      return rest;
    });
  };

  const handleClear = () => {
    setFile(null);
    setError(null);
    setUploadSummary(null);
    setProgress(0);
    setPreview(null);
    setEditedPreview(null);
    setColumns([]);
    setCellErrors({});
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClose = () => {
    handleClear();
    onClose();
  };

  const handleConfirm = async () => {
    if (editedPreview && uploadSummary && uploadSummary.success && Object.keys(cellErrors).length === 0) {
      // Map each candidate row to backend field names and IDs
      const mappedCandidates = editedPreview.map(row => {
        const mapped = {};
        Object.entries(columnMapping).forEach(([col, systemField]) => {
          if (systemField && systemField !== 'ignore') {
            let value = row[col];
            // Map foreign keys to IDs
            if (systemField === 'job_title') value = getIdByName(jobTitleOptions, value);
            if (systemField === 'city') value = getIdByName(cityOptions, value);
            if (systemField === 'source') value = getIdByName(sourceOptions, value);
            if (systemField === 'communication_skills') value = getIdByName(commSkillOptions, value);
            mapped[systemField] = value;
          }
        });
        // Only include required fields
        const filtered = {};
        requiredBackendFields.forEach(f => { filtered[f] = mapped[f]; });
        return filtered;
      });
      try {
        setUploading(true);
        const response = await axios.post(`${API_URL}/chat/upload/confirm`, {
          session_id: sessionId,
          candidates: mappedCandidates,
          duplicate_mode: duplicateMode,
          confirm: true,
          authToken: authToken,
        }, {
          headers: {
            Authorization: `Token ${authToken}`,
            'Content-Type': 'application/json',
          },
        });
        const summary: UploadSummary = response.data;
        onSuccess({
          total: (summary.added ?? 0) + (summary.failedCount ?? 0) + (summary.duplicates ?? 0),
          failedCount: summary.failedCount ?? 0,
          duplicates: summary.duplicates ?? 0,
        });
        handleClose();
        toast({
          title: 'Bulk Upload Confirmed',
          description: `Added: ${summary.added}, Errors: ${summary.failedCount}, Duplicates: ${summary.duplicates}`,
        });
      } catch (err: any) {
        toast({
          title: 'Confirm Failed',
          description: err.message || 'An error occurred during confirmation.',
          variant: 'destructive',
        });
      } finally {
        setUploading(false);
      }
    }
  };

  const isPreviewMode = !!preview && columns.length > 0;
  // Update isConfirmDisabled and required fields logic to treat 'ignore' as unmapped
  const isConfirmDisabled = uploading || Object.keys(cellErrors).length > 0 || !uploadSummary || !uploadSummary.success || requiredFields.some(f => !Object.values(columnMapping).includes(f));

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent
        className={
          isPreviewMode
            ? 'w-screen h-screen max-w-none max-h-none rounded-none p-0 flex flex-col overflow-y-auto'
            : 'sm:max-w-[600px] bg-white dark:bg-gray-800 rounded-lg shadow-xl'
        }
        aria-describedby="bulk-upload-desc"
      >
        <div className={isPreviewMode ? 'flex-1 flex flex-col p-6 min-h-0 overflow-y-auto' : 'p-6'}>
          <div className="flex justify-between items-center mb-4">
            <DialogTitle className="text-2xl font-semibold text-gray-800 dark:text-gray-100">
              Bulk Upload Candidates
            </DialogTitle>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-2xl font-bold focus:outline-none"
              aria-label="Close"
            >
              ×
            </button>
          </div>
          {/* Always render the description for accessibility, even if empty */}
          <DialogDescription id="bulk-upload-desc">
            Upload a CSV or Excel (.xlsx) file containing candidate data. Map columns to system fields and review data before confirming.
          </DialogDescription>
          <div className="space-y-6">
            <div className="text-sm text-gray-600 dark:text-gray-300">
              <p>Upload a CSV or Excel (.xlsx) file containing candidate data. The file should follow the template format.</p>
              <a
                href="/chat/template/candidates"
                className="text-blue-600 hover:underline flex items-center gap-1 mt-2"
                download
              >
                <File className="h-4 w-4" />
                Download Template
              </a>
            </div>
            <div className="flex items-center gap-3">
              <Input
                type="file"
                accept=".csv,.xlsx"
                onChange={handleFileChange}
                ref={fileInputRef}
                className="flex-1 dark:bg-gray-700 dark:border-gray-600"
                disabled={uploading}
              />
              {file && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleClear}
                  disabled={uploading}
                  className="hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <X className="h-4 w-4 text-gray-500" />
                </Button>
              )}
            </div>
            <div>
              <label htmlFor="bulk-duplicate-mode-modal" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                Duplicate Handling:
              </label>
              <Select
                value={duplicateMode}
                onValueChange={(value: 'skip' | 'update' | 'flag') => setDuplicateMode(value)}
                disabled={uploading}
              >
                <SelectTrigger id="bulk-duplicate-mode-modal" className="mt-1">
                  <SelectValue placeholder="Select duplicate handling mode" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="skip">Skip duplicates</SelectItem>
                  <SelectItem value="update">Update existing</SelectItem>
                  <SelectItem value="flag">Flag for review</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {file && (
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                <File className="h-4 w-4" />
                <span>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
              </div>
            )}
            {uploading && (
              <div className="space-y-2">
                <Progress value={progress} className="w-full" />
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                  Uploading... {progress}%
                </p>
              </div>
            )}
            {loadingPreview && !error && (
              <div className="text-center text-gray-500 dark:text-gray-400 flex flex-col items-center justify-center py-8">
                <svg
                  className="animate-spin h-8 w-8 text-blue-600 mb-2"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                </svg>
                Loading preview...
              </div>
            )}
            {error && (
              <Alert variant="destructive" className="my-4">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            {uploadSummary?.missing_columns && uploadSummary.missing_columns.length > 0 && (
              <Alert variant="default" className="bg-yellow-50 dark:bg-yellow-900">
                <AlertTitle>Missing Columns</AlertTitle>
                <AlertDescription>
                  The following required columns are missing: {uploadSummary.missing_columns.join(', ')}
                </AlertDescription>
              </Alert>
            )}
            {isPreviewMode && preview && columns.length > 0 && (
              <div className="flex-1 min-h-0 overflow-y-auto mt-4">
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Data Preview ({preview.length} candidates)
                  </h3>
                  <div
                    className="overflow-x-auto rounded-lg border bg-white dark:bg-gray-800 p-1 shadow-md resize-x w-full"
                    style={{ maxWidth: '100vw' }}
                  >
                    <div className="max-h-[350px] overflow-y-auto">
                      <table
                        className="w-full text-[11px] border-collapse border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
                        aria-label="Candidate data preview"
                      >
                        <thead className="sticky top-0 bg-gray-50 dark:bg-gray-700 z-10">
                          <tr>
                            {columns.map(col => (
                              <th
                                key={col}
                                scope="col"
                                className="px-1 py-1 font-semibold text-gray-800 dark:text-gray-100 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 sticky top-0 z-20 text-[11px]"
                              >
                                {col}
                              </th>
                            ))}
                          </tr>
                          <tr className="bg-blue-50 dark:bg-blue-900 sticky top-8 z-10">
                            {columns.map(col => (
                              <th key={col} className="px-1 py-1 border-b border-gray-200 dark:border-gray-700">
                                <Select
                                  value={columnMapping[col] || ''}
                                  onValueChange={value => setColumnMapping(prev => ({ ...prev, [col]: value }))}
                                  disabled={uploading}
                                >
                                  <SelectTrigger className="w-full text-xs">
                                    <SelectValue placeholder="Ignore" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {systemFields.map(f => (
                                      <SelectItem
                                        key={f}
                                        value={f}
                                        disabled={f !== 'ignore' && Object.values(columnMapping).includes(f) && columnMapping[col] !== f}
                                      >
                                        {f === 'ignore'
                                          ? 'Ignore'
                                          : f.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {preview && preview.map((row, i) => (
                            <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                              {columns.map(col => (
                                <td key={col} className="px-1 py-1 border-b border-gray-100 dark:border-gray-700">
                                  {editedPreview ? (
                                    <>
                                      <input
                                        type="text"
                                        value={editedPreview[i][col] || ''}
                                        onChange={e => handleEditCell(i, col, e.target.value)}
                                        className="w-full text-xs border-none bg-transparent"
                                        placeholder={col}
                                      />
                                      {cellErrors[`${i}-${col}`] && (
                                        <span className="text-red-500 text-xs">{cellErrors[`${i}-${col}`]}</span>
                                      )}
                                    </>
                                  ) : (
                                    row[col]
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Scroll horizontally to see all columns.</div>
                  </div>
                  {requiredFields.some(f => !Object.values(columnMapping).includes(f)) && (
                    <Alert variant="default" className="bg-yellow-50 dark:bg-yellow-900 mt-2">
                      <AlertTitle>Missing Required Fields</AlertTitle>
                      <AlertDescription>
                        Please map the following required fields: {requiredFields.filter(f => !Object.values(columnMapping).includes(f)).join(', ')}
                      </AlertDescription>
                    </Alert>
                  )}
                  {(uploadSummary?.duplicates || 0 > 0 || uploadSummary?.failedCount || 0 > 0) && (
                    <div style={{ marginTop: 8 }}>
                      {uploadSummary?.duplicates || 0 > 0 && (
                        <div style={{ color: 'orange' }}>
                          ⚠️ {uploadSummary?.duplicates || 0} duplicate(s) detected.
                        </div>
                      )}
                      {uploadSummary?.failedCount || 0 > 0 && (
                        <div style={{ color: 'red' }}>
                          ❌ {uploadSummary?.failedCount || 0} row(s) have errors.{' '}
                          <a href={`/chat/upload/failed-rows?session_id=${sessionId}`} target="_blank" rel="noopener noreferrer">
                            Download Errors (CSV)
                          </a>
                        </div>
                      )}
                    </div>
                  )}
                  {uploadSummary?.errors && uploadSummary.errors.length > 0 && (
                    <div style={{ marginTop: 8, color: 'red', fontSize: 12 }}>
                      <b>Errors:</b>
                      <ul>
                        {uploadSummary.errors.slice(0, 5).map((err, i) => (
                          <li key={i}>Row {err.row}: {err.errors.join(', ')}</li>
                        ))}
                        {uploadSummary.errors.length > 5 && <li>...and {uploadSummary.errors.length - 5} more</li>}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
        <DialogFooter
          className={
            isPreviewMode
              ? 'sticky bottom-0 bg-white dark:bg-gray-800 p-4 border-t border-gray-200 dark:border-gray-700 z-20 flex justify-end'
              : ''
          }
        >
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={isConfirmDisabled}>
            Confirm Upload
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default BulkUploadModal;