import React, { useState } from 'react';
import axios from 'axios';
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

const AddCandidate: React.FC = () => {
  // State for all fields
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

  // File handlers
  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setResume(e.target.files[0]);
  };
  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setAvatar(e.target.files[0]);
  };

  // Main submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setFieldErrors({});
    // Validation
    if (!firstName || !lastName || !email || !jobTitle || !resume) {
      setError('Please fill in all required fields.');
      setLoading(false);
      return;
    }
    if (!resume) {
      setError('Resume is required.');
      setLoading(false);
      return;
    }
    if (!avatar) {
      setError('Avatar is required.');
      setLoading(false);
      return;
    }
    if (yearsOfExperience && !/^\d+$/.test(yearsOfExperience)) {
      setError('Years of experience must be a whole number.');
      setLoading(false);
      return;
    }
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

      await axios.post('http://localhost:8000/api/candidates/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/candidates');
      }, 1500);
    } catch (err: any) {
      if (err.response && err.response.data) {
        setFieldErrors(err.response.data);
        setError('Please correct the highlighted errors.');
      } else {
        setError('Failed to add candidate');
      }
    } finally {
      setLoading(false);
    }
  };

  // Save as Draft
  const handleSaveDraft = () => {
    setCandidateStage('draft');
    // Optionally call handleSubmit or similar logic
  };

  // Cancel
  const handleCancel = () => {
    window.location.href = '/candidates';
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="h-10 w-10">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-foreground">Add New Candidate</h1>
          <p className="text-muted-foreground">
            Enter candidate information to add them to your database
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
                  <Input id="firstName" placeholder="Enter first name" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
                  {fieldErrors.first_name && <p className="text-xs text-red-500">{fieldErrors.first_name}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input id="lastName" placeholder="Enter last name" value={lastName} onChange={(e) => setLastName(e.target.value)} />
                  {fieldErrors.last_name && <p className="text-xs text-red-500">{fieldErrors.last_name}</p>}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" placeholder="candidate@email.com" value={email} onChange={(e) => setEmail(e.target.value)} />
                  {fieldErrors.email && <p className="text-xs text-red-500">{fieldErrors.email}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input id="phone" placeholder="+1 (555) 123-4567" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} />
                  {fieldErrors.phone_number && <p className="text-xs text-red-500">{fieldErrors.phone_number}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input id="location" placeholder="City, State/Country" value={city} onChange={(e) => setCity(e.target.value)} />
                {fieldErrors.city && <p className="text-xs text-red-500">{fieldErrors.city}</p>}
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
                <Input id="position" placeholder="e.g., Senior React Developer" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
                {fieldErrors.job_title && <p className="text-xs text-red-500">{fieldErrors.job_title}</p>}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="yearsOfExperience">Years of Experience</Label>
                  <Input
                    id="yearsOfExperience"
                    type="number"
                    placeholder="e.g., 5"
                    value={yearsOfExperience}
                    onChange={(e) => setYearsOfExperience(e.target.value)}
                    min={0}
                    step={1}
                  />
                  {fieldErrors.years_of_experience && <p className="text-xs text-red-500">{fieldErrors.years_of_experience}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salary">Expected Salary</Label>
                  <Input id="salary" placeholder="e.g., $80,000 - $100,000" value={expectedSalary} onChange={(e) => setExpectedSalary(e.target.value)} />
                  {fieldErrors.expected_salary && <p className="text-xs text-red-500">{fieldErrors.expected_salary}</p>}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="currentSalary">Current Salary</Label>
                  <Input
                    id="currentSalary"
                    type="number"
                    placeholder="e.g., 80000"
                    value={currentSalary}
                    onChange={(e) => setCurrentSalary(e.target.value)}
                  />
                  {fieldErrors.current_salary && <p className="text-xs text-red-500">{fieldErrors.current_salary}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="source">Source</Label>
                  <Select value={source} onValueChange={setSource}>
                    <SelectTrigger>
                      <SelectValue placeholder="How did they find us?" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="linkedin">LinkedIn</SelectItem>
                      <SelectItem value="website">Company Website</SelectItem>
                      <SelectItem value="referral">Employee Referral</SelectItem>
                      <SelectItem value="indeed">Indeed</SelectItem>
                      <SelectItem value="glassdoor">Glassdoor</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                  {fieldErrors.source && <p className="text-xs text-red-500">{fieldErrors.source}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="skills">Key Skills</Label>
                <Input id="skills" placeholder="e.g., React, JavaScript, Node.js (comma separated)" value={communicationSkills} onChange={(e) => setCommunicationSkills(e.target.value)} />
                {fieldErrors.communication_skills && <p className="text-xs text-red-500">{fieldErrors.communication_skills}</p>}
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
                <Textarea 
                  id="notes" 
                  placeholder="Add any additional notes about the candidate..."
                  className="min-h-[100px]"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
                {fieldErrors.notes && <p className="text-xs text-red-500">{fieldErrors.notes}</p>}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* File Upload */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '300ms' }}>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="resume">Resume</Label>
                <div className="border-2 border-dashed border-muted rounded-lg p-6 text-center hover:border-primary/50 transition-colors duration-200">
                  <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Drag & drop resume here, or click to browse
                  </p>
                  <input
                    type="file"
                    id="resume"
                    onChange={handleResumeChange}
                    className="hidden"
                    title="Upload resume file"
                  />
                  <Button variant="outline" size="sm" onClick={() => document.getElementById('resume')?.click()} type="button">
                    Browse Files
                  </Button>
                  {resume && <div className="mt-2 text-xs text-green-600">Selected: {resume.name}</div>}
                  {fieldErrors.resume && <div className="text-xs text-red-500">{fieldErrors.resume}</div>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="avatar">Avatar (Optional)</Label>
                <div className="border-2 border-dashed border-muted rounded-lg p-4 text-center hover:border-primary/50 transition-colors duration-200">
                  <Upload className="h-6 w-6 text-muted-foreground mx-auto mb-1" />
                  <p className="text-xs text-muted-foreground mb-2">
                    Upload avatar
                  </p>
                  <input
                    type="file"
                    id="avatar"
                    onChange={handleAvatarChange}
                    className="hidden"
                    title="Upload avatar image"
                  />
                  <Button variant="outline" size="sm" onClick={() => document.getElementById('avatar')?.click()} type="button">
                    Browse
                  </Button>
                  {avatar && <div className="mt-2 text-xs text-green-600">Selected: {avatar.name}</div>}
                  {fieldErrors.avatar && <div className="text-xs text-red-500">{fieldErrors.avatar}</div>}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stage Selection */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '400ms' }}>
            <CardHeader>
              <CardTitle>Initial Stage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="stage">Recruitment Stage</Label>
                <Select defaultValue="applied">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="applied">Applied</SelectItem>
                    <SelectItem value="screening">Screening</SelectItem>
                    <SelectItem value="technical">Technical Interview</SelectItem>
                    <SelectItem value="interview">Final Interview</SelectItem>
                  </SelectContent>
                </Select>
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
                      Save Candidate
                    </>
                  )}
                </Button>
                <Button variant="outline" className="w-full" onClick={handleSaveDraft}>
                  Save as Draft
                </Button>
                <Button variant="ghost" className="w-full" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      {error && <div className="text-center text-red-500 mt-4">{error}</div>}
      {success && (
        <div className="text-center text-green-500 mt-4">
          Candidate added! Redirecting...
        </div>
      )}
    </form>
  );
};

export default AddCandidate;