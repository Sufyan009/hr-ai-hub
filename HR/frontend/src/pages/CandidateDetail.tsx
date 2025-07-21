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
  Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

const CandidateDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [candidate, setCandidate] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCandidate = async () => {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/api/candidates/${id}/`);
        if (!res.ok) throw new Error('Failed to fetch candidate');
        const data = await res.json();
        setCandidate(data);
      } catch (err) {
        setError('Failed to load candidate data.');
      } finally {
        setLoading(false);
      }
    };
    fetchCandidate();
  }, [id]);

  const getStageColor = (stage: string) => {
    switch ((stage || '').toLowerCase()) {
      case 'applied': return 'bg-muted text-muted-foreground';
      case 'screening': return 'bg-blue-100 text-blue-800';
      case 'technical': return 'bg-purple-100 text-purple-800';
      case 'interview': return 'bg-orange-100 text-orange-800';
      case 'offer': return 'bg-green-100 text-green-800';
      case 'hired': return 'bg-success text-success-foreground';
      case 'rejected': return 'bg-destructive text-destructive-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this candidate? This action cannot be undone.')) {
      return;
    }
    try {
      await axios.delete(`http://localhost:8000/api/candidates/${id}/`);
      toast({
        title: 'Candidate Deleted',
        description: `${fullName} has been successfully removed.`,
      });
      navigate('/candidates');
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to delete the candidate. Please try again.',
        variant: 'destructive',
      });
      setError('Failed to delete the candidate.');
    }
  };

  if (loading) return <div className="text-center py-10">Loading...</div>;
  if (error || !candidate) return <div className="text-center text-red-500 py-10">{error || 'Candidate not found.'}</div>;

  const fullName = `${candidate.first_name || ''} ${candidate.last_name || ''}`.trim();

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10"
          onClick={() => navigate('/candidates')}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-foreground">{fullName}</h1>
          <p className="text-muted-foreground">Candidate Profile & Details</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(`/candidates/${id}/edit`)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Profile Summary */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5 text-primary" />
                  Profile Summary
                </CardTitle>
                <Badge className={getStageColor(candidate.candidate_stage)}>
                  {candidate.candidate_stage || 'N/A'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground text-xl font-semibold">
                  {fullName.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-foreground">{fullName}</h3>
                  <p className="text-lg text-muted-foreground">{candidate.job_title?.name}</p>
                  <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                    {candidate.years_of_experience !== undefined && (
                      <span className="flex items-center gap-1">
                        <Briefcase className="h-4 w-4" />
                        {candidate.years_of_experience} yrs
                      </span>
                    )}
                    {candidate.city && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        {candidate.city?.name}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <Separator />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{candidate.email}</span>
                  </div>
                  {candidate.phone_number && (
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{candidate.phone_number}</span>
                    </div>
                  )}
                  {candidate.created_at && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Applied: {candidate.created_at}</span>
                    </div>
                  )}
                </div>
                <div className="space-y-3">
                  {candidate.expected_salary !== undefined && (
                    <div>
                      <span className="text-sm font-medium text-foreground">Expected Salary:</span>
                      <p className="text-sm text-muted-foreground">{candidate.expected_salary}</p>
                    </div>
                  )}
                  {candidate.current_salary !== undefined && (
                    <div>
                      <span className="text-sm font-medium text-foreground">Current Salary:</span>
                      <p className="text-sm text-muted-foreground">{candidate.current_salary}</p>
                    </div>
                  )}
                  {candidate.source && (
                    <div>
                      <span className="text-sm font-medium text-foreground">Source:</span>
                      <p className="text-sm text-muted-foreground">{candidate.source?.name}</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
          {/* Detailed Information Tabs */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '100ms' }}>
            <CardContent className="p-0">
              <Tabs defaultValue="details" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="details">Details</TabsTrigger>
                  <TabsTrigger value="documents">Documents</TabsTrigger>
                  <TabsTrigger value="notes">Notes</TabsTrigger>
                </TabsList>
                <TabsContent value="details" className="p-6 space-y-4">
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Key Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {candidate.communication_skills?.name ? (
                        <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
                          {candidate.communication_skills.name}
                        </Badge>
                      ) : <span className="text-muted-foreground">No skills listed.</span>}
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Stage</h4>
                    <p className="text-sm text-muted-foreground">{candidate.candidate_stage || 'N/A'}</p>
                  </div>
                  <Separator />
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Experience</h4>
                    <p className="text-sm text-muted-foreground">{candidate.years_of_experience !== undefined ? `${candidate.years_of_experience} years` : 'N/A'}</p>
                  </div>
                </TabsContent>
                <TabsContent value="documents" className="p-6 space-y-4">
                  <div className="space-y-3">
                    {candidate.resume ? (
                      <div className="flex items-center justify-between p-3 border border-border rounded-lg">
                        <div className="flex items-center gap-3">
                          <FileText className="h-8 w-8 text-primary" />
                          <div>
                            <a href={candidate.resume} target="_blank" rel="noopener noreferrer" className="font-medium text-foreground underline">View Resume</a>
                          </div>
                        </div>
                        <Button size="sm" variant="outline" asChild>
                          <a href={candidate.resume} download>
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </a>
                        </Button>
                      </div>
                    ) : (
                      <div className="p-3 border border-border rounded-lg bg-background/50 text-xs text-muted-foreground">No resume uploaded.</div>
                    )}
                    {candidate.avatar && (
                      <div className="flex items-center justify-between p-3 border border-border rounded-lg">
                        <div className="flex items-center gap-3">
                          <ImageIcon className="h-8 w-8 text-secondary" />
                          <div>
                            <a href={candidate.avatar} target="_blank" rel="noopener noreferrer" className="font-medium text-foreground underline">View Avatar</a>
                          </div>
                        </div>
                        <Button size="sm" variant="outline" asChild>
                          <a href={candidate.avatar} download>
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </a>
                        </Button>
                      </div>
                    )}
                  </div>
                </TabsContent>
                <TabsContent value="notes" className="p-6">
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Notes</h4>
                    <p className="text-sm text-muted-foreground">{candidate.notes || 'No notes.'}</p>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="shadow-medium border-0 bg-gradient-glass card-hover animate-fade-in backdrop-blur-sm" style={{ animationDelay: '200ms' }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="p-1.5 rounded-full bg-primary/10">
                  <Sparkles className="h-5 w-5 text-primary" />
                </div>
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start gap-3 bg-gradient-primary btn-glow shadow-soft">
                <Calendar className="h-4 w-4" />
                Schedule Interview
              </Button>
              <Button variant="outline" className="w-full justify-start gap-3 hover:bg-secondary/10 hover:text-secondary transition-colors">
                <MessageSquare className="h-4 w-4" />
                Add Note
              </Button>
              <Button variant="outline" className="w-full justify-start gap-3 hover:bg-secondary/10 hover:text-secondary transition-colors">
                <Mail className="h-4 w-4" />
                Send Email
              </Button>
              <Button variant="outline" className="w-full justify-start gap-3 hover:bg-secondary/10 hover:text-secondary transition-colors">
                <Edit className="h-4 w-4" />
                Update Stage
              </Button>
            </CardContent>
          </Card>
          {/* Stage Progression */}
          <Card className="shadow-soft border-0 bg-gradient-card animate-fade-in" style={{ animationDelay: '300ms' }}>
            <CardHeader>
              <CardTitle>Stage Progression</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {['Applied', 'Screening', 'Technical', 'Interview', 'Offer', 'Hired'].map((stage, index) => (
                  <div key={stage} className="flex items-center gap-3">
                    <div className={`h-4 w-4 rounded-full ${
                      (candidate.candidate_stage || '').toLowerCase() === stage.toLowerCase() ? 'bg-success' : 'bg-muted'
                    }`} />
                    <span className={`text-sm ${
                      (candidate.candidate_stage || '').toLowerCase() === stage.toLowerCase() ? 'text-foreground font-medium' : 'text-muted-foreground'
                    }`}>
                      {stage}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CandidateDetail;