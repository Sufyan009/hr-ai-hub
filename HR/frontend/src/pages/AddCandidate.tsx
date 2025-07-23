import React, { useState, useEffect } from 'react';
import { Save, Upload, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import api from '@/services/api';

const AddCandidate: React.FC = () => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [candidateStage, setCandidateStage] = useState('applied');
  const [currentSalary, setCurrentSalary] = useState('');
  const [expectedSalary, setExpectedSalary] = useState('');
  const [yearsOfExperience, setYearsOfExperience] = useState('');
  const [communicationSkills, setCommunicationSkills] = useState('');
  const [city, setCity] = useState('');
  const [source, setSource] = useState('');
  const [notes, setNotes] = useState('');
  const [resume, setResume] = useState<File | null>(null);
  const [avatar, setAvatar] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});
  const navigate = useNavigate();
  const { toast } = useToast();

  const [jobTitles, setJobTitles] = useState<{id: number, name: string}[]>([]);
  const [cities, setCities] = useState<{id: number, name: string}[]>([]);
  const [sources, setSources] = useState<{id: number, name: string}[]>([]);
  const [commSkills, setCommSkills] = useState<{id: number, name: string}[]>([]);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [jtRes, cityRes, sourceRes, commRes] = await Promise.all([
          api.get('/jobtitles/'),
          api.get('/cities/'),
          api.get('/sources/'),
          api.get('/communicationskills/'),
        ]);
        setJobTitles(jtRes.data);
        setCities(cityRes.data);
        setSources(sourceRes.data);
        setCommSkills(commRes.data);
      } catch (error) {
        toast({ title: 'Error', description: 'Failed to load options.', variant: 'destructive' });
      }
    };
    fetchOptions();
  }, [toast]);

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
        setError('Resume must be a PDF or Word document.');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('Resume file size must be less than 5MB.');
        return;
      }
      setResume(file);
      setError('');
    }
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.type.startsWith('image/')) {
        setError('Avatar must be an image file.');
        return;
      }
      if (file.size > 2 * 1024 * 1024) {
        setError('Avatar file size must be less than 2MB.');
        return;
      }
      setAvatar(file);
      setError('');
    }
  };

  const validateEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const validatePhone = (phone: string) => /^\+?[0-9\-\s]{7,15}$/.test(phone);
  const validateSalary = (salary: string) => !salary || (!isNaN(Number(salary)) && Number(salary) >= 0);
  const validateExperience = (exp: string) => !exp || (!isNaN(Number(exp)) && Number(exp) >= 0 && Number(exp) < 100);

  useEffect(() => {
    const errors: {[key: string]: string} = {};
    if (email && !validateEmail(email)) errors.email = 'Invalid email format.';
    if (phoneNumber && !validatePhone(phoneNumber)) errors.phone_number = 'Invalid phone number.';
    if (currentSalary && !validateSalary(currentSalary)) errors.current_salary = 'Invalid salary.';
    if (expectedSalary && !validateSalary(expectedSalary)) errors.expected_salary = 'Invalid salary.';
    if (yearsOfExperience && !validateExperience(yearsOfExperience)) errors.years_of_experience = 'Invalid experience.';
    setFieldErrors(errors);
  }, [email, phoneNumber, currentSalary, expectedSalary, yearsOfExperience]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});
    const errors: {[key: string]: string} = {
      first_name: !firstName ? 'This field is required.' : '',
      last_name: !lastName ? 'This field is required.' : '',
      email: !email ? 'This field is required.' : '',
      job_title: !jobTitle ? 'This field is required.' : '',
      city: !city ? 'This field is required.' : '',
      source: !source ? 'This field is required.' : '',
      communication_skills: !communicationSkills ? 'This field is required.' : '',
    };
    setFieldErrors(errors);
    if (Object.values(errors).some(Boolean)) {
      setError('Please fill in all required fields.');
      return;
    }
    if (!validateEmail(email)) {
      setError('Invalid email format.');
      setFieldErrors({ ...errors, email: 'Invalid email format.' });
      return;
    }
    if (phoneNumber && !validatePhone(phoneNumber)) {
      setError('Invalid phone number.');
      setFieldErrors({ ...errors, phone_number: 'Invalid phone number.' });
      return;
    }
    if (currentSalary && !validateSalary(currentSalary)) {
      setError('Invalid current salary.');
      setFieldErrors({ ...errors, current_salary: 'Invalid salary.' });
      return;
    }
    if (expectedSalary && !validateSalary(expectedSalary)) {
      setError('Invalid expected salary.');
      setFieldErrors({ ...errors, expected_salary: 'Invalid salary.' });
      return;
    }
    if (yearsOfExperience && !validateExperience(yearsOfExperience)) {
      setError('Invalid years of experience.');
      setFieldErrors({ ...errors, years_of_experience: 'Invalid experience.' });
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('first_name', firstName);
      formData.append('last_name', lastName);
      formData.append('email', email);
      formData.append('phone_number', phoneNumber);
      formData.append('job_title', jobTitle);
      formData.append('candidate_stage', candidateStage);
      formData.append('current_salary', currentSalary ? String(Number(currentSalary)) : '0');
      formData.append('expected_salary', expectedSalary ? String(Number(expectedSalary)) : '0');
      formData.append('years_of_experience', yearsOfExperience && !isNaN(Number(yearsOfExperience)) ? String(Number(yearsOfExperience)) : '');
      formData.append('communication_skills', communicationSkills);
      formData.append('city', city);
      formData.append('source', source);
      formData.append('notes', notes);
      if (resume) formData.append('resume', resume);
      if (avatar) formData.append('avatar', avatar);
      const response = await api.post('/candidates/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSuccess(true);
      toast({ title: 'Candidate Added', description: 'Candidate was added successfully!', variant: 'default' });
      const candidateId = response.data.id;
      setTimeout(() => {
        navigate(`/candidates/${candidateId}`);
      }, 1000);
    } catch (err: any) {
      if (err.response && err.response.data) {
        setFieldErrors(err.response.data);
        setError('Please correct the highlighted errors.');
      } else {
        setError('Failed to add candidate.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveDraft = () => {
    setCandidateStage('draft');
    handleSubmit({ preventDefault: () => {} } as React.FormEvent);
  };

  const handleCancel = () => {
    navigate('/candidates');
  };

  return (
    <form onSubmit={handleSubmit} aria-label="Add Candidate Form" className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="h-10 w-10 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={handleCancel}
            aria-label="Go back"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          </Button>
          <div>
            <h1 className="text-2xl font-semibold text-gray-800 dark:text-gray-100">
              Add New Candidate
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Enter candidate information to add them to your database
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
            <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
              <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                Personal Information
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    First Name <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="firstName"
                    placeholder="Enter first name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                    aria-required="true"
                    aria-invalid={!!fieldErrors.first_name}
                  />
                  {fieldErrors.first_name && <p className="text-xs text-red-500">{fieldErrors.first_name}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Last Name <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="lastName"
                    placeholder="Enter last name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                    aria-required="true"
                    aria-invalid={!!fieldErrors.last_name}
                  />
                  {fieldErrors.last_name && <p className="text-xs text-red-500">{fieldErrors.last_name}</p>}
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Email Address <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="candidate@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                    aria-required="true"
                    aria-invalid={!!fieldErrors.email}
                  />
                  {fieldErrors.email && <p className="text-xs text-red-500">{fieldErrors.email}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Phone Number
                  </Label>
                  <Input
                    id="phone"
                    placeholder="+1 (555) 123-4567"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                    aria-invalid={!!fieldErrors.phone_number}
                  />
                  {fieldErrors.phone_number && <p className="text-xs text-red-500">{fieldErrors.phone_number}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="location" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  Location <span className="text-red-500">*</span>
                </Label>
                <Select value={city} onValueChange={setCity}>
                  <SelectTrigger className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500">
                    <SelectValue placeholder="Select city" />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-gray-800">
                    {cities.map(c => (
                      <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {fieldErrors.city && <p className="text-xs text-red-500">{fieldErrors.city}</p>}
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
            <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
              <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                Professional Information
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="position" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  Position Applied For <span className="text-red-500">*</span>
                </Label>
                <Select value={jobTitle} onValueChange={setJobTitle}>
                  <SelectTrigger className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500">
                    <SelectValue placeholder="Select job title" />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-gray-800">
                    {jobTitles.map(jt => (
                      <SelectItem key={jt.id} value={String(jt.id)}>{jt.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {fieldErrors.job_title && <p className="text-xs text-red-500">{fieldErrors.job_title}</p>}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="yearsOfExperience" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Years of Experience
                  </Label>
                  <Input
                    id="yearsOfExperience"
                    type="number"
                    placeholder="e.g., 5"
                    value={yearsOfExperience}
                    onChange={(e) => setYearsOfExperience(e.target.value)}
                    min={0}
                    step={1}
                    className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                    aria-invalid={!!fieldErrors.years_of_experience}
                  />
                  {fieldErrors.years_of_experience && <p className="text-xs text-red-500">{fieldErrors.years_of_experience}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salary" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Expected Salary
                  </Label>
                  <Input
                    id="salary"
                    placeholder="e.g., $80,000"
                    value={expectedSalary}
                    onChange={(e) => setExpectedSalary(e.target.value)}
                    className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                    aria-invalid={!!fieldErrors.expected_salary}
                  />
                  {fieldErrors.expected_salary && <p className="text-xs text-red-500">{fieldErrors.expected_salary}</p>}
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="currentSalary" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Current Salary
                  </Label>
                  <Input
                    id="currentSalary"
                    type="number"
                    placeholder="e.g., 80000"
                    value={currentSalary}
                    onChange={(e) => setCurrentSalary(e.target.value)}
                    className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                    aria-invalid={!!fieldErrors.current_salary}
                  />
                  {fieldErrors.current_salary && <p className="text-xs text-red-500">{fieldErrors.current_salary}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="source" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Source <span className="text-red-500">*</span>
                  </Label>
                  <Select value={source} onValueChange={setSource}>
                    <SelectTrigger className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500">
                      <SelectValue placeholder="Select source" />
                    </SelectTrigger>
                    <SelectContent className="bg-white dark:bg-gray-800">
                      {sources.map(s => (
                        <SelectItem key={s.id} value={String(s.id)}>{s.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {fieldErrors.source && <p className="text-xs text-red-500">{fieldErrors.source}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="skills" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  Key Skills <span className="text-red-500">*</span>
                </Label>
                <Select value={communicationSkills} onValueChange={setCommunicationSkills}>
                  <SelectTrigger className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500">
                    <SelectValue placeholder="Select communication skill" />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-gray-800">
                    {commSkills.map(cs => (
                      <SelectItem key={cs.id} value={String(cs.id)}>{cs.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {fieldErrors.communication_skills && <p className="text-xs text-red-500">{fieldErrors.communication_skills}</p>}
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
            <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
              <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                Additional Information
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="notes" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  Notes
                </Label>
                <Textarea 
                  id="notes" 
                  placeholder="Add any additional notes about the candidate..."
                  className="min-h-[120px] rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  aria-invalid={!!fieldErrors.notes}
                />
                {fieldErrors.notes && <p className="text-xs text-red-500">{fieldErrors.notes}</p>}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
            <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
              <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                Documents
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="resume" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  Resume
                </Label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors duration-200">
                  <Upload className="h-8 w-8 text-gray-400 dark:text-gray-500 mx-auto mb-2" />
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    Drag & drop resume here, or click to browse
                  </p>
                  <input
                    type="file"
                    id="resume"
                    onChange={handleResumeChange}
                    className="hidden"
                    title="Upload resume file"
                    accept=".pdf,.doc,.docx"
                    aria-describedby="resume-desc"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => document.getElementById('resume')?.click()}
                    type="button"
                    className="border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Browse Files
                  </Button>
                  {resume && <div className="mt-2 text-xs text-teal-600 dark:text-teal-400">Selected: {resume.name}</div>}
                  {fieldErrors.resume && <div className="mt-2 text-xs text-red-500">{fieldErrors.resume}</div>}
                </div>
                <span id="resume-desc" className="text-xs text-gray-500 dark:text-gray-400">
                  Accepted: PDF, DOC, DOCX. Max 5MB.
                </span>
              </div>
              <div className="space-y-2">
                <Label htmlFor="avatar" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  Avatar (Optional)
                </Label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors duration-200">
                  <Upload className="h-6 w-6 text-gray-400 dark:text-gray-500 mx-auto mb-2" />
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    Upload avatar
                  </p>
                  <input
                    type="file"
                    id="avatar"
                    onChange={handleAvatarChange}
                    className="hidden"
                    title="Upload avatar image"
                    accept="image/*"
                    aria-describedby="avatar-desc"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => document.getElementById('avatar')?.click()}
                    type="button"
                    className="border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Browse
                  </Button>
                  {avatar && <div className="mt-2 text-xs text-teal-600 dark:text-teal-400">Selected: {avatar.name}</div>}
                  {fieldErrors.avatar && <div className="mt-2 text-xs text-red-500">{fieldErrors.avatar}</div>}
                </div>
                <span id="avatar-desc" className="text-xs text-gray-500 dark:text-gray-400">
                  Accepted: Images only. Max 2MB.
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
            <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
              <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                Initial Stage
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-2">
                <Label htmlFor="stage" className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  Recruitment Stage
                </Label>
                <Select value={candidateStage} onValueChange={setCandidateStage}>
                  <SelectTrigger className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:ring-2 focus:ring-blue-500">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-gray-800">
                    <SelectItem value="applied">Applied</SelectItem>
                    <SelectItem value="screening">Screening</SelectItem>
                    <SelectItem value="technical">Technical Interview</SelectItem>
                    <SelectItem value="interview">Final Interview</SelectItem>
                    <SelectItem value="offer">Offer</SelectItem>
                    <SelectItem value="hired">Hired</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
            <CardContent className="p-6 space-y-3">
              <Button
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-200"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <svg
                      className="animate-spin h-4 w-4 mr-2 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Candidate
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                className="w-full border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-100"
                onClick={handleSaveDraft}
                disabled={loading}
              >
                Save as Draft
              </Button>
              <Button
                variant="ghost"
                className="w-full text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700"
                onClick={handleCancel}
                disabled={loading}
              >
                Cancel
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
      {error && (
        <div className="mt-6 text-center">
          <p className="text-sm text-red-600 dark:text-red-400" role="alert">{error}</p>
        </div>
      )}
      {success && (
        <div className="mt-6 text-center">
          <p className="text-sm text-teal-600 dark:text-teal-400">Candidate added! Redirecting...</p>
        </div>
      )}
    </form>
  );
};

export default AddCandidate;