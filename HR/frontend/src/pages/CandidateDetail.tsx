import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  Calendar,
  Edit,
  Trash2,
  Download,
  FileText,
  User,
  Clock,
  MessageSquare,
  Image as ImageIcon,
  Sparkles,
  Star,
  TrendingUp,
  Building,
  GraduationCap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import api from '@/services/api';
import { DeleteConfirmationModal } from '@/components/DeleteConfirmationModal';

const CandidateDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [candidate, setCandidate] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showInterviewModal, setShowInterviewModal] = useState(false);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [showStageModal, setShowStageModal] = useState(false);
  const [interviewDate, setInterviewDate] = useState('');
  const [interviewTime, setInterviewTime] = useState('');
  const [note, setNote] = useState('');
  const [newStage, setNewStage] = useState(candidate?.candidate_stage || '');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [notes, setNotes] = useState<any[]>([]);
  const [notesLoading, setNotesLoading] = useState(false);

  // Fetch notes for candidate
  const fetchNotes = async () => {
    setNotesLoading(true);
    try {
      const res = await api.get(`/notes/?candidate=${id}`);
      // Accept both array and paginated response
      const notesArr = Array.isArray(res.data)
        ? res.data
        : Array.isArray(res.data.results)
          ? res.data.results
          : [];
      setNotes(notesArr);
    } catch (err) {
      setNotes([]);
    } finally {
      setNotesLoading(false);
    }
  };

  useEffect(() => {
    const fetchCandidate = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await api.get(`/candidates/${id}/`);
        setCandidate(res.data);
      } catch (err) {
        setError('Failed to load candidate data.');
      } finally {
        setLoading(false);
      }
    };
    fetchCandidate();
    fetchNotes();
  }, [id]);

  const getStageInfo = (stage: string) => {
    const stageMap = {
      'applied': { label: 'Applied', class: 'status-applied', progress: 16 },
      'screening': { label: 'Screening', class: 'status-screening', progress: 32 },
      'technical': { label: 'Technical', class: 'status-technical', progress: 48 },
      'interview': { label: 'Interview', class: 'status-interview', progress: 64 },
      'offer': { label: 'Offer', class: 'status-offer', progress: 80 },
      'hired': { label: 'Hired', class: 'status-hired', progress: 100 },
      'rejected': { label: 'Rejected', class: 'status-rejected', progress: 0 }
    };
    return stageMap[stage?.toLowerCase()] || { label: 'Unknown', class: 'status-applied', progress: 0 };
  };

  const handleDelete = async () => {
    setShowDeleteModal(false);
    if (!window.confirm('Are you sure you want to delete this candidate? This action cannot be undone.')) {
      return;
    }
    toast({
      title: 'Candidate Deleted',
      description: `${fullName} has been successfully removed.`,
    });
    navigate('/candidates');
  };

  const handleScheduleInterview = () => setShowInterviewModal(true);
  const saveInterview = () => {
    setShowInterviewModal(false);
    toast({ title: 'Not Implemented', description: 'Interview scheduling is not yet implemented in the backend.' });
    setInterviewDate('');
    setInterviewTime('');
  };

  const handleAddNote = () => setShowNoteModal(true);
  // Add note
  const saveNote = async () => {
    setLoading(true);
    try {
      await api.post('/notes/', { candidate: id, content: note });
      setNote('');
      setShowNoteModal(false);
      toast({ title: 'Note Added', description: 'Your note has been saved.' });
      fetchNotes();
    } catch (err) {
      toast({ title: 'Error', description: 'Failed to save note.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  // Delete note
  const deleteNote = async (noteId: number) => {
    setLoading(true);
    try {
      await api.delete(`/notes/${noteId}/`);
      toast({ title: 'Note Deleted', description: 'The note has been deleted.' });
      fetchNotes();
    } catch (err) {
      toast({ title: 'Error', description: 'Failed to delete note.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmail = () => {
    if (candidate?.email) {
      window.location.href = `mailto:${candidate.email}`;
    } else {
      toast({ title: 'No Email', description: 'No email address available for this candidate.' });
    }
  };

  const handleUpdateStage = () => setShowStageModal(true);
  const saveStage = async () => {
    if (!newStage) return;
    setLoading(true);
    try {
      await api.patch(`/candidates/${id}/`, { candidate_stage: newStage });
      toast({ title: 'Stage Updated', description: `Candidate stage updated to ${newStage}` });
      setShowStageModal(false);
      // Refresh candidate data
      const res = await api.get(`/candidates/${id}/`);
      setCandidate(res.data);
    } catch (err) {
      toast({ title: 'Error', description: 'Failed to update stage.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  if (loading || !candidate) {
    return <div className="flex items-center justify-center min-h-screen text-gray-500 dark:text-gray-400">Loading candidate...</div>;
  }
  
  if (error) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="text-destructive text-lg font-medium mb-2">Error</div>
        <div className="text-muted-foreground">{error}</div>
      </div>
    </div>
  );
  
  if (!candidate) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="text-muted-foreground text-lg">No candidate found</div>
      </div>
    </div>
  );

  const fullName = `${candidate.first_name || ''} ${candidate.last_name || ''}`.trim();
  const stageInfo = getStageInfo(candidate.candidate_stage);

  // Defensive fallback before rendering notes:
  const safeNotes = Array.isArray(notes) ? notes : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Professional Header */}
        <div className="flex items-center justify-between mb-8 animate-fade-in">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="h-12 w-12 rounded-full hover:bg-accent/10 transition-colors"
              onClick={() => navigate('/candidates')}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-4xl font-bold text-foreground tracking-tight">{fullName}</h1>
              <p className="text-xl text-muted-foreground mt-1">Candidate Profile</p>
            </div>
          </div>
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              onClick={() => navigate(`/candidates/${id}/edit`)}
              className="gap-2 hover:bg-accent/10 transition-colors"
            >
              <Edit className="h-4 w-4" />
              Edit Profile
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => setShowDeleteModal(true)}
              className="gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content - 3 columns */}
          <div className="lg:col-span-3 space-y-8">
            {/* Hero Profile Card */}
            <Card className="overflow-hidden border-0 shadow-[var(--shadow-medium)] animate-slide-up">
              <div className="bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5 p-8">
                <div className="flex items-start gap-6">
                  <div className="relative">
                    <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-primary-foreground text-2xl font-bold shadow-lg">
                      {fullName.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full bg-success flex items-center justify-center">
                      <div className="h-3 w-3 rounded-full bg-success-foreground"></div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-3xl font-bold text-foreground">{fullName}</h2>
                      <Badge className={`px-3 py-1 rounded-full ${stageInfo.class} font-medium`}>
                        {stageInfo.label}
                      </Badge>
                    </div>
                    <p className="text-xl text-accent font-medium mb-4">{candidate.job_title_detail?.name}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Briefcase className="h-4 w-4 text-accent" />
                        <span>{candidate.years_of_experience} years experience</span>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <MapPin className="h-4 w-4 text-accent" />
                        <span>{candidate.city_detail?.name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Calendar className="h-4 w-4 text-accent" />
                        <span>Applied {candidate.created_at}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="px-8 py-4 bg-gradient-to-r from-muted/30 to-muted/10">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-foreground">Application Progress</span>
                  <span className="text-sm text-muted-foreground">{stageInfo.progress}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-accent to-primary h-2 rounded-full transition-all duration-500"
                    style={{ width: `${stageInfo.progress}%` }}
                  ></div>
                </div>
              </div>
            </Card>

            {/* Contact & Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in" style={{ animationDelay: '200ms' }}>
              <Card className="border-0 shadow-[var(--shadow-soft)] card-hover">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Mail className="h-5 w-5 text-accent" />
                    Contact Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Email</div>
                      <div className="text-sm text-muted-foreground">{candidate.email}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Phone</div>
                      <div className="text-sm text-muted-foreground">{candidate.phone_number}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
                    <Building className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-sm font-medium">Current Company</div>
                      <div className="text-sm text-muted-foreground">{candidate.company}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-[var(--shadow-soft)] card-hover">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <TrendingUp className="h-5 w-5 text-accent" />
                    Compensation
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
                    <div className="text-sm font-medium mb-1">Expected Salary</div>
                    <div className="text-lg font-semibold text-success">{candidate.expected_salary}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
                    <div className="text-sm font-medium mb-1">Current Salary</div>
                    <div className="text-lg font-semibold text-foreground">{candidate.current_salary}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
                    <div className="text-sm font-medium mb-1">Source</div>
                    <div className="text-sm text-muted-foreground">{candidate.source_detail?.name}</div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Tabs */}
            <Card className="border-0 shadow-[var(--shadow-soft)] animate-fade-in" style={{ animationDelay: '300ms' }}>
              <Tabs defaultValue="overview" className="w-full">
                <CardHeader className="pb-4">
                  <TabsList className="grid w-full grid-cols-4 bg-muted/30">
                    <TabsTrigger value="overview" className="data-[state=active]:bg-background">Overview</TabsTrigger>
                    <TabsTrigger value="skills" className="data-[state=active]:bg-background">Skills</TabsTrigger>
                    <TabsTrigger value="documents" className="data-[state=active]:bg-background">Documents</TabsTrigger>
                    <TabsTrigger value="notes" className="data-[state=active]:bg-background">Notes</TabsTrigger>
                  </TabsList>
                </CardHeader>
                
                <CardContent>
                  <TabsContent value="overview" className="space-y-6 mt-0">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                            <GraduationCap className="h-4 w-4 text-accent" />
                            Education
                          </h4>
                          <p className="text-muted-foreground">{candidate.education}</p>
                        </div>
                        <div>
                          <h4 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                            <MessageSquare className="h-4 w-4 text-accent" />
                            Communication Skills
                          </h4>
                          <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                            {candidate.communication_skills_detail?.name}
                          </Badge>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                            <Clock className="h-4 w-4 text-accent" />
                            Experience Level
                          </h4>
                          <div className="flex items-center gap-2">
                            <div className="flex">
                              {[...Array(5)].map((_, i) => (
                                <Star 
                                  key={i} 
                                  className={`h-4 w-4 ${i < 4 ? 'text-warning fill-warning' : 'text-muted-foreground'}`} 
                                />
                              ))}
                            </div>
                            <span className="text-muted-foreground text-sm">Senior Level</span>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-semibold text-foreground mb-3">Application Stage</h4>
                          <Badge className={`${stageInfo.class} px-3 py-1`}>
                            {stageInfo.label}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="skills" className="mt-0">
                    <div>
                      <h4 className="font-semibold text-foreground mb-4">Technical Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {(candidate?.skills || []).map((skill: string, index: number) => (
                          <Badge 
                            key={index} 
                            variant="outline" 
                            className="bg-accent/10 text-accent border-accent/20 hover:bg-accent/20 transition-colors px-3 py-1"
                          >
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="documents" className="mt-0">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 border border-border rounded-xl bg-muted/20 hover:bg-muted/30 transition-colors">
                        <div className="flex items-center gap-4">
                          <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                            <FileText className="h-6 w-6 text-accent" />
                          </div>
                          <div>
                            <div className="font-medium text-foreground">Resume</div>
                            <div className="text-sm text-muted-foreground">PDF • 2.4 MB</div>
                          </div>
                        </div>
                        <Button size="sm" variant="outline" className="gap-2">
                          <Download className="h-4 w-4" />
                          Download
                        </Button>
                      </div>
                      
                      <div className="flex items-center justify-between p-4 border border-border rounded-xl bg-muted/20 hover:bg-muted/30 transition-colors">
                        <div className="flex items-center gap-4">
                          <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                            <ImageIcon className="h-6 w-6 text-accent" />
                          </div>
                          <div>
                            <div className="font-medium text-foreground">Profile Photo</div>
                            <div className="text-sm text-muted-foreground">JPG • 1.1 MB</div>
                          </div>
                        </div>
                        <Button size="sm" variant="outline" className="gap-2">
                          <Download className="h-4 w-4" />
                          Download
                        </Button>
                      </div>
                    </div>
                  </TabsContent>

                  {/* Notes Section */}
                  <TabsContent value="notes" className="mt-0">
                    <Card className="shadow-lg border-0 bg-white dark:bg-gray-800">
                      <CardHeader className="border-b bg-gray-50 dark:bg-gray-700">
                        <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100 flex items-center justify-between">
                          Notes
                          <Button size="sm" onClick={handleAddNote}>
                            Add Note
                          </Button>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-6 space-y-4">
                        {notesLoading ? (
                          <div className="text-gray-500 dark:text-gray-400">Loading notes...</div>
                        ) : safeNotes.length === 0 ? (
                          <div className="text-gray-500 dark:text-gray-400">No notes yet.</div>
                        ) : (
                          <ul className="space-y-3">
                            {safeNotes.map((n: any) => (
                              <li key={n.id} className="flex items-start justify-between bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
                                <div>
                                  <div className="text-sm text-gray-900 dark:text-gray-100 whitespace-pre-line">{n.content}</div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</div>
                                </div>
                                <Button variant="ghost" size="icon" onClick={() => deleteNote(n.id)} aria-label="Delete note">
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                                </Button>
                              </li>
                            ))}
                          </ul>
                        )}
                      </CardContent>
                    </Card>
                  </TabsContent>
                </CardContent>
              </Tabs>
            </Card>
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="border-0 shadow-[var(--shadow-medium)] card-hover animate-scale-in bg-gradient-to-br from-background to-muted/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-accent/20 to-primary/20">
                    <Sparkles className="h-5 w-5 text-accent" />
                  </div>
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full justify-start gap-3 h-12 bg-gradient-to-r from-accent to-accent/80 hover:from-accent/90 hover:to-accent/70 text-accent-foreground shadow-lg" 
                  onClick={handleScheduleInterview}
                >
                  <Calendar className="h-4 w-4" />
                  Schedule Interview
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start gap-3 h-12 hover:bg-accent/5 hover:border-accent/30 transition-all" 
                  onClick={handleAddNote}
                >
                  <MessageSquare className="h-4 w-4" />
                  Add Note
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start gap-3 h-12 hover:bg-accent/5 hover:border-accent/30 transition-all" 
                  onClick={handleSendEmail}
                >
                  <Mail className="h-4 w-4" />
                  Send Email
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start gap-3 h-12 hover:bg-accent/5 hover:border-accent/30 transition-all" 
                  onClick={handleUpdateStage}
                >
                  <Edit className="h-4 w-4" />
                  Update Stage
                </Button>
              </CardContent>
            </Card>

            {/* Application Timeline */}
            <Card className="border-0 shadow-[var(--shadow-soft)] animate-fade-in" style={{ animationDelay: '400ms' }}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-accent" />
                  Application Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { stage: 'Applied', date: 'Mar 15', active: true, completed: true },
                    { stage: 'Screening', date: 'Mar 18', active: true, completed: true },
                    { stage: 'Technical', date: 'Mar 22', active: true, completed: true },
                    { stage: 'Interview', date: 'Mar 25', active: true, completed: false },
                    { stage: 'Offer', date: 'Pending', active: false, completed: false },
                    { stage: 'Hired', date: 'Pending', active: false, completed: false }
                  ].map((item, index) => (
                    <div key={item.stage} className="flex items-center gap-3">
                      <div className={`h-3 w-3 rounded-full transition-all ${
                        item.completed ? 'bg-success' : 
                        item.active ? 'bg-accent animate-pulse' : 'bg-muted'
                      }`} />
                      <div className="flex-1">
                        <div className={`text-sm font-medium ${
                          item.active ? 'text-foreground' : 'text-muted-foreground'
                        }`}>
                          {item.stage}
                        </div>
                        <div className="text-xs text-muted-foreground">{item.date}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Modals */}
      <Dialog open={showInterviewModal} onOpenChange={setShowInterviewModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Schedule Interview</DialogTitle>
            <DialogDescription>
              Select the date and time for the interview with {fullName}.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Date</label>
              <input 
                type="date" 
                value={interviewDate} 
                onChange={e => setInterviewDate(e.target.value)} 
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:ring-2 focus:ring-accent focus:border-transparent transition-all"
                title="Interview Date"
                placeholder="Select date"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Time</label>
              <input 
                type="time" 
                value={interviewTime} 
                onChange={e => setInterviewTime(e.target.value)} 
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:ring-2 focus:ring-accent focus:border-transparent transition-all"
                title="Interview Time"
                placeholder="Select time"
              />
            </div>
            <div className="flex gap-3 pt-4">
              <Button onClick={saveInterview} disabled={!interviewDate || !interviewTime} className="flex-1">
                Schedule Interview
              </Button>
              <Button variant="outline" onClick={() => setShowInterviewModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showNoteModal} onOpenChange={setShowNoteModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add Note</DialogTitle>
            <DialogDescription>
              Add a note about {fullName} for future reference.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Note</label>
              <textarea 
                value={note} 
                onChange={e => setNote(e.target.value)} 
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:ring-2 focus:ring-accent focus:border-transparent transition-all min-h-[100px] resize-none"
                placeholder="Enter your note here..."
              />
            </div>
            <div className="flex gap-3 pt-4">
              <Button onClick={saveNote} disabled={!note.trim()} className="flex-1">
                Save Note
              </Button>
              <Button variant="outline" onClick={() => setShowNoteModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showStageModal} onOpenChange={setShowStageModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Update Stage</DialogTitle>
            <DialogDescription>
              Update the application stage for {fullName}.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Stage</label>
              <select 
                value={newStage} 
                onChange={e => setNewStage(e.target.value)} 
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground focus:ring-2 focus:ring-accent focus:border-transparent transition-all"
                title="Application Stage"
              >
                <option value="applied">Applied</option>
                <option value="screening">Screening</option>
                <option value="technical">Technical Interview</option>
                <option value="interview">Final Interview</option>
                <option value="offer">Offer Extended</option>
                <option value="hired">Hired</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div className="flex gap-3 pt-4">
              <Button onClick={saveStage} disabled={!newStage} className="flex-1">
                Update Stage
              </Button>
              <Button variant="outline" onClick={() => setShowStageModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <DeleteConfirmationModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
        onConfirm={handleDelete}
        jobTitle={fullName}
        isDeleting={false}
      />
    </div>
  );
};

export default CandidateDetail;