import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, ArrowLeft, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import api from '@/services/api'; // Add this import
import { useToast } from '@/hooks/use-toast';

const EditCandidate: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // State for each field
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [candidateStage, setCandidateStage] = useState('');
  const [currentSalary, setCurrentSalary] = useState('');
  const [expectedSalary, setExpectedSalary] = useState('');
  const [yearsOfExperience, setYearsOfExperience] = useState('');
  const [communicationSkills, setCommunicationSkills] = useState('');
  const [city, setCity] = useState('');
  const [source, setSource] = useState('');
  const [notes, setNotes] = useState('');
  const [resume, setResume] = useState<File | null>(null);
  const [avatar, setAvatar] = useState<File | null>(null);
  const [existingResume, setExistingResume] = useState('');
  const [existingAvatar, setExistingAvatar] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});

  // Option lists for selects
  const [jobTitles, setJobTitles] = useState<{id: number, name: string}[]>([]);
  const [cities, setCities] = useState<{id: number, name: string}[]>([]);
  const [sources, setSources] = useState<{id: number, name: string}[]>([]);
  const [commSkills, setCommSkills] = useState<{id: number, name: string}[]>([]);
  const { toast } = useToast();

  // Fetch options for selects
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
        // handle error
      }
    };
    fetchOptions();
  }, []);

  // Fetch candidate data on mount
  useEffect(() => {
    const fetchCandidate = async () => {
      setLoading(true);
      try {
        const res = await api.get(`http://localhost:8000/api/candidates/${id}/`);
        const c = res.data;
        setFirstName(c.first_name || '');
        setLastName(c.last_name || '');
        setEmail(c.email || '');
        setPhoneNumber(c.phone_number || '');
        setJobTitle(c.job_title || c.job_title_detail?.id?.toString() || '');
        setCandidateStage(c.candidate_stage || '');
        setCurrentSalary(c.current_salary ? String(c.current_salary) : '');
        setExpectedSalary(c.expected_salary ? String(c.expected_salary) : '');
        setYearsOfExperience(c.years_of_experience ? String(c.years_of_experience) : '');
        setCommunicationSkills(c.communication_skills || c.communication_skills_detail?.id?.toString() || '');
        setCity(c.city || c.city_detail?.id?.toString() || '');
        setSource(c.source || c.source_detail?.id?.toString() || '');
        setNotes(c.notes || '');
        setExistingResume(c.resume || '');
        setExistingAvatar(c.avatar || '');
      } catch (err) {
        setError('Failed to load candidate data.');
      } finally {
        setLoading(false);
      }
    };
    fetchCandidate();
    // eslint-disable-next-line
  }, [id]);

  // Validation helpers
  const validateEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const validatePhone = (phone: string) => /^\+?[0-9\-\s]{7,15}$/.test(phone);
  const validateSalary = (salary: string) => !salary || (!isNaN(Number(salary)) && Number(salary) >= 0);
  const validateExperience = (exp: string) => !exp || (!isNaN(Number(exp)) && Number(exp) >= 0 && Number(exp) < 100);

  // Inline validation as user types
  useEffect(() => {
    const errors: {[key: string]: string} = {};
    if (email && !validateEmail(email)) errors.email = 'Invalid email format.';
    if (phoneNumber && !validatePhone(phoneNumber)) errors.phone_number = 'Invalid phone number.';
    if (currentSalary && !validateSalary(currentSalary)) errors.current_salary = 'Invalid salary.';
    if (expectedSalary && !validateSalary(expectedSalary)) errors.expected_salary = 'Invalid salary.';
    if (yearsOfExperience && !validateExperience(yearsOfExperience)) errors.years_of_experience = 'Invalid experience.';
    setFieldErrors(errors);
  }, [email, phoneNumber, currentSalary, expectedSalary, yearsOfExperience]);

  // File handlers
  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
        setError('Resume must be a PDF or Word document.');
        return;
      }
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setError('Resume file size must be less than 5MB.');
        return;
      }
      setResume(file);
    }
  };
  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.type.startsWith('image/')) {
        setError('Avatar must be an image file.');
        return;
      }
      if (file.size > 2 * 1024 * 1024) { // 2MB limit
        setError('Avatar file size must be less than 2MB.');
        return;
      }
      setAvatar(file);
    }
  };

  // Save changes
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});
    // Basic validation
    if (!firstName || !lastName || !email || !jobTitle) {
      setError('Please fill in all required fields.');
      setFieldErrors({
        firstName: !firstName ? 'Required' : '',
        lastName: !lastName ? 'Required' : '',
        email: !email ? 'Required' : '',
        jobTitle: !jobTitle ? 'Required' : '',
      });
      setLoading(false);
      return;
    }
    // Stricter validation
    if (!validateEmail(email)) {
      setError('Invalid email format.');
      setFieldErrors({ email: 'Invalid email format.' });
      setLoading(false);
      return;
    }
    if (phoneNumber && !validatePhone(phoneNumber)) {
      setError('Invalid phone number.');
      setFieldErrors({ phone_number: 'Invalid phone number.' });
      setLoading(false);
      return;
    }
    if (currentSalary && !validateSalary(currentSalary)) {
      setError('Invalid current salary.');
      setFieldErrors({ current_salary: 'Invalid salary.' });
      setLoading(false);
      return;
    }
    if (expectedSalary && !validateSalary(expectedSalary)) {
      setError('Invalid expected salary.');
      setFieldErrors({ expected_salary: 'Invalid salary.' });
      setLoading(false);
      return;
    }
    if (yearsOfExperience && !validateExperience(yearsOfExperience)) {
      setError('Invalid years of experience.');
      setFieldErrors({ years_of_experience: 'Invalid experience.' });
      setLoading(false);
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
      formData.append('current_salary', currentSalary ? String(Number(currentSalary)) : '');
      formData.append('expected_salary', expectedSalary ? String(Number(expectedSalary)) : '');
      formData.append('years_of_experience', yearsOfExperience && !isNaN(Number(yearsOfExperience)) ? String(Number(yearsOfExperience)) : '');
      formData.append('communication_skills', communicationSkills);
      formData.append('city', city);
      formData.append('source', source);
      formData.append('notes', notes);
      if (resume) formData.append('resume', resume);
      if (avatar) formData.append('avatar', avatar);
      await api.patch(`http://localhost:8000/api/candidates/${id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSuccess(true);
      toast({ title: 'Candidate Updated', description: 'Candidate was updated successfully!' });
      setTimeout(() => {
        navigate(`/candidates/${id}`);
      }, 1000);
    } catch (err: any) {
      setError('Failed to save changes.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-10">Loading...</div>;

  return (
    <form onSubmit={handleSave} aria-label="Edit Candidate Form" className="w-full px-2 sm:px-4 md:px-6 lg:px-8 xl:px-12 2xl:px-20 md:max-w-6xl lg:max-w-7xl xl:max-w-8xl 2xl:max-w-screen-2xl md:mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon" 
          className="h-10 w-10"
          onClick={() => navigate(`/candidates/${id}`)}
          type="button"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-foreground">Edit Candidate</h1>
          <p className="text-muted-foreground">
            Update candidate information
          </p>
        </div>
      </div>
      {/* Main form grid: more columns and gap on xl+ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6 xl:gap-8">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal Information */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in">
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input id="firstName" value={firstName} onChange={e => setFirstName(e.target.value)} aria-required="true" />
                  {fieldErrors.firstName && <p className="text-xs text-red-500">{fieldErrors.firstName}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input id="lastName" value={lastName} onChange={e => setLastName(e.target.value)} aria-required="true" />
                  {fieldErrors.lastName && <p className="text-xs text-red-500">{fieldErrors.lastName}</p>}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} aria-required="true" />
                  {fieldErrors.email && <p className="text-xs text-red-500">{fieldErrors.email}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input id="phone" value={phoneNumber} onChange={e => setPhoneNumber(e.target.value)} />
                  {fieldErrors.phone_number && <p className="text-xs text-red-500">{fieldErrors.phone_number}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Select value={city} onValueChange={setCity}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select city" />
                  </SelectTrigger>
                  <SelectContent>
                    {cities.map(c => (
                      <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
          {/* Professional Information */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '100ms' }}>
            <CardHeader>
              <CardTitle>Professional Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="position">Position Applied For</Label>
                <Select value={jobTitle} onValueChange={setJobTitle}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select job title" />
                  </SelectTrigger>
                  <SelectContent>
                    {jobTitles.map(jt => (
                      <SelectItem key={jt.id} value={String(jt.id)}>{jt.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {fieldErrors.jobTitle && <p className="text-xs text-red-500">{fieldErrors.jobTitle}</p>}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="yearsOfExperience">Years of Experience</Label>
                  <Input id="yearsOfExperience" type="number" placeholder="e.g., 5" value={yearsOfExperience} onChange={e => setYearsOfExperience(e.target.value)} min={0} step={1} />
                  {fieldErrors.years_of_experience && <p className="text-xs text-red-500">{fieldErrors.years_of_experience}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salary">Expected Salary</Label>
                  <Input id="salary" value={expectedSalary} onChange={e => setExpectedSalary(e.target.value)} />
                  {fieldErrors.expected_salary && <p className="text-xs text-red-500">{fieldErrors.expected_salary}</p>}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="currentSalary">Current Salary</Label>
                  <Input id="currentSalary" value={currentSalary} onChange={e => setCurrentSalary(e.target.value)} />
                  {fieldErrors.current_salary && <p className="text-xs text-red-500">{fieldErrors.current_salary}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="source">Source</Label>
                  <Select value={source} onValueChange={setSource}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select source" />
                    </SelectTrigger>
                    <SelectContent>
                      {sources.map(s => (
                        <SelectItem key={s.id} value={String(s.id)}>{s.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="skills">Communication Skills</Label>
                <Select value={communicationSkills} onValueChange={setCommunicationSkills}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select communication skill" />
                  </SelectTrigger>
                  <SelectContent>
                    {commSkills.map(cs => (
                      <SelectItem key={cs.id} value={String(cs.id)}>{cs.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
          {/* Additional Information */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '200ms' }}>
            <CardHeader>
              <CardTitle>Additional Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea id="notes" value={notes} onChange={e => setNotes(e.target.value)} className="min-h-[100px]" />
              </div>
            </CardContent>
          </Card>
        </div>
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Stage Management */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '300ms' }}>
            <CardHeader>
              <CardTitle>Stage Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="stage">Current Stage</Label>
                <Select value={candidateStage} onValueChange={setCandidateStage}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="applied">Applied</SelectItem>
                    <SelectItem value="screening">Screening</SelectItem>
                    <SelectItem value="technical">Technical Interview</SelectItem>
                    <SelectItem value="interview">Final Interview</SelectItem>
                    <SelectItem value="offer">Offer Extended</SelectItem>
                    <SelectItem value="hired">Hired</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
          {/* Document Management */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '400ms' }}>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Current Resume</Label>
                {existingResume ? (
                  <div className="p-3 border border-border rounded-lg bg-background/50">
                    <a href={existingResume} target="_blank" rel="noopener noreferrer" className="text-sm font-medium underline">View Resume</a>
                  </div>
                ) : (
                  <div className="p-3 border border-border rounded-lg bg-background/50 text-xs text-muted-foreground">No resume uploaded.</div>
                )}
                <input type="file" id="resume" onChange={handleResumeChange} className="hidden" title="Upload resume file" aria-describedby="resume-desc" />
                <span id="resume-desc">Accepted: PDF, DOC, DOCX. Max 5MB.</span>
                <Button variant="outline" size="sm" className="w-full" type="button" onClick={() => document.getElementById('resume')?.click()}>
                  <Upload className="h-4 w-4 mr-2" />
                  Replace Resume
                </Button>
                {resume && <div className="mt-2 text-xs text-green-600">Selected: {resume.name}</div>}
              </div>
              <div className="space-y-2">
                <Label>Avatar</Label>
                {existingAvatar ? (
                  <div className="p-3 border border-border rounded-lg bg-background/50">
                    <a href={existingAvatar} target="_blank" rel="noopener noreferrer" className="text-sm font-medium underline">View Avatar</a>
                  </div>
                ) : (
                  <div className="p-3 border border-border rounded-lg bg-background/50 text-xs text-muted-foreground">No avatar uploaded.</div>
                )}
                <input type="file" id="avatar" onChange={handleAvatarChange} className="hidden" title="Upload avatar image" aria-describedby="avatar-desc" />
                <span id="avatar-desc">Accepted: Images only. Max 2MB.</span>
                <Button variant="outline" size="sm" className="w-full" type="button" onClick={() => document.getElementById('avatar')?.click()}>
                  <Upload className="h-4 w-4 mr-2" />
                  Replace Avatar
                </Button>
                {avatar && <div className="mt-2 text-xs text-green-600">Selected: {avatar.name}</div>}
              </div>
            </CardContent>
          </Card>
          {/* Action Buttons */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '500ms' }}>
            <CardContent className="pt-6">
              <div className="space-y-3">
                <Button className="w-full bg-gradient-primary hover:shadow-glow transition-all duration-300" type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <svg className="animate-spin h-4 w-4 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
                <Button variant="outline" className="w-full" type="button" onClick={() => navigate(`/candidates/${id}`)}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
          {error && <div className="text-center text-red-500 mt-4" role="alert">{error}</div>}
          {success && <div className="text-center text-green-500 mt-4">Changes saved! Redirecting...</div>}
        </div>
      </div>
    </form>
  );
};

export default EditCandidate;