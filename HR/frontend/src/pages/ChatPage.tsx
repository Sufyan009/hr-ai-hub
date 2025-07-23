import React, { useEffect, useState, useRef } from 'react';
import { 
  Send, Bot, User, Settings, Eraser, Copy, MoreVertical, Sparkles, Shield, 
  Clock, Check, ChevronDown, Zap, Brain, Award, MessageSquare, RefreshCw,
  Volume2, VolumeX, Download, Star, TrendingUp
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { sendMessage as sendChatMessage, fetchModels } from '@/services/chatService';

interface Message {
  id: string;
  type: 'user' | 'bot' | 'error' | 'system';
  content: string;
  timestamp: Date;
  tokens?: number;
  model?: string;
  confidence?: number;
}

interface ChatStats {
  totalMessages: number;
  totalTokens: number;
  averageResponseTime: number;
  sessionsToday: number;
}

// ErrorBoundary component
class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: any}> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }
  componentDidCatch(error: any, errorInfo: any) {
    // You can log errorInfo here if needed
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-red-50 dark:bg-red-900/10">
          <div className="text-2xl font-bold text-red-700 dark:text-red-300 mb-4">Something went wrong</div>
          <div className="text-red-600 dark:text-red-200 text-sm max-w-xl break-all">{String(this.state.error)}</div>
        </div>
      );
    }
    return this.props.children;
  }
}

const HRAssistantPro: React.FC = () => {
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = localStorage.getItem('hrAssistantMessages');
    return saved ? JSON.parse(saved) : [
      {
        id: '1',
        type: 'system',
        // Only show a short greeting, not the full prompt
        content: `👋 Welcome! How can I help you with HR today?`,
        timestamp: new Date(),
        confidence: 100,
        model: 'System'
      }
    ];
  });
  
  const [inputValue, setInputValue] = useState('');
  // Add fallback for DEFAULT_PROMPT and QUICK_PROMPTS
  const DEFAULT_PROMPT = `You are an elite HR Assistant Pro specializing in strategic human resources management. You provide expert guidance on:

**CORE COMPETENCIES:**
• Talent Acquisition & Recruitment Strategy
• Performance Management & Development
• Compliance & Legal HR Frameworks
• Organizational Development & Culture
• Employee Relations & Engagement
• Compensation & Benefits Analysis

**RESPONSE STANDARDS:**
• Provide actionable, data-driven recommendations
• Include relevant legal considerations and compliance notes
• Use structured formatting with clear headings and bullet points
• Offer multiple approaches when applicable
• Include industry best practices and benchmarks
• Maintain professional, authoritative tone

**OUTPUT FORMAT:**
• Executive summary for complex topics
• Step-by-step implementation guides
• Template suggestions with customization options
• Risk assessments and mitigation strategies
• ROI considerations where applicable

Ensure all advice aligns with current employment law and industry standards.`;

  const QUICK_PROMPTS = [
    {
      title: "Candidate Interview Questions",
      prompt: "Generate a comprehensive set of behavioral and technical interview questions for a Senior Software Engineer position, including evaluation criteria."
    },
    {
      title: "Job Description Template",
      prompt: "Create a professional job description template for a Product Manager role, including responsibilities, requirements, and company culture elements."
    },
    {
      title: "Performance Review Framework",
      prompt: "Design a 360-degree performance review framework with specific metrics, competency areas, and development planning components."
    },
    {
      title: "Onboarding Checklist",
      prompt: "Develop a comprehensive 90-day onboarding checklist for new remote employees, including milestones and integration activities."
    }
  ];
  // Declare models state first
  const [models, setModels] = useState<any[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState('');
  // For selectedModel, use the first model from models as default if available
  const [selectedModel, setSelectedModel] = useState('');
  useEffect(() => {
    if (!selectedModel && models.length > 0) {
      setSelectedModel(models[0].value || models[0].id || '');
    }
  }, [models, selectedModel]);
  const [isLoading, setIsLoading] = useState(false);
  const [customPrompt, setCustomPrompt] = useState(() => 
    localStorage.getItem('hrAiPrompt') || DEFAULT_PROMPT
  );
  const [showConfig, setShowConfig] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(() => 
    localStorage.getItem('soundEnabled') !== 'false'
  );
  const [chatStats, setChatStats] = useState<ChatStats>({
    totalMessages: 0,
    totalTokens: 0,
    averageResponseTime: 1.2,
    sessionsToday: 1
  });
  const [responseProgress, setResponseProgress] = useState(0);
  const [showModelError, setShowModelError] = useState(false);

  // Fetch models from backend on mount
  useEffect(() => {
    const loadModels = async () => {
      setModelsLoading(true);
      setModelsError('');
      try {
        const data = await fetchModels();
        // Defensive: ensure models is always an array
        setModels(Array.isArray(data) ? data : (Array.isArray(data?.data) ? data.data : []));
      } catch (err) {
        setModelsError('Failed to load models from OpenRouter.');
      } finally {
        setModelsLoading(false);
      }
    };
    loadModels();
  }, []);

  // Persist settings and stats
  useEffect(() => {
    localStorage.setItem('hrAiModel', selectedModel);
    localStorage.setItem('hrAiPrompt', customPrompt);
    localStorage.setItem('hrAssistantMessages', JSON.stringify(messages));
    localStorage.setItem('soundEnabled', soundEnabled.toString());
    
    setChatStats(prev => ({
      ...prev,
      totalMessages: messages.filter(m => m.type !== 'system').length
    }));
  }, [selectedModel, customPrompt, messages, soundEnabled]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const playNotificationSound = () => {
    if (soundEnabled) {
      // Create a subtle notification sound
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
      oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
      
      gainNode.gain.setValueAtTime(0, audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.2);
    }
  };

  const handleSendMessage = async (messageText?: string, imageUrl?: string) => {
    if (modelsLoading || !models.length || !selectedModel) {
      setShowModelError(true);
      return;
    }
    setShowModelError(false);

    const content = messageText || inputValue;
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
      tokens: Math.ceil(content.length / 4)
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setIsTyping(true);
    setResponseProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setResponseProgress(prev => Math.min(prev + Math.random() * 15, 90));
    }, 200);

    try {
      // Build messages array for OpenAI/ChatML format
      const messagesArr = [
        { role: 'system', content: customPrompt },
        {
          role: 'user',
          content: imageUrl
            ? [
                { type: 'text', text: content },
                { type: 'image_url', image_url: { url: imageUrl } }
              ]
            : content
        }
      ];
      // Call backend API with full payload
      const response = await sendChatMessage({
        model: selectedModel,
        messages: messagesArr,
        prompt: customPrompt
      });
      clearInterval(progressInterval);
      setResponseProgress(100);
      setIsTyping(false);

      const modelData = getModelData(selectedModel);
      const color = modelData.color || 'gray';
      const badge = modelData.badge || '';
      const icon = modelData.icon || null;
      const label = modelData.label || '';
      const description = modelData.description || '';
      const confidence = 85 + Math.random() * 15;

      const botResponse: Message = {
        id: `${Date.now()}_bot`,
        type: 'bot',
        content: response.response || 'No response from AI.',
        timestamp: new Date(),
        model: label,
        confidence: Math.round(confidence),
        tokens: Math.ceil((response.response || '').length / 4)
      };

      setMessages(prev => [...prev, botResponse]);
      setIsLoading(false);
      setResponseProgress(0);
      playNotificationSound();
      setChatStats(prev => ({
        ...prev,
        totalTokens: prev.totalTokens + (userMessage.tokens || 0) + (botResponse.tokens || 0),
        averageResponseTime: 1.2 + Math.random() * 0.8
      }));
    } catch (error: any) {
      clearInterval(progressInterval);
      setIsTyping(false);
      setIsLoading(false);
      setResponseProgress(0);
      setMessages(prev => [
        ...prev,
        {
          id: `${Date.now()}_error`,
          type: 'error',
          content: 'Failed to get a response from the AI assistant. Please try again.',
          timestamp: new Date()
        }
      ]);
      toast({ title: 'Chat Error', description: 'Failed to get a response from the AI assistant.', variant: 'destructive' });
    }
  };

  const generateEnhancedResponse = (query: string): string => {
    return `## Strategic Analysis: ${query.slice(0, 50)}...

Thank you for your strategic HR inquiry. Based on current industry best practices and regulatory frameworks, here's my comprehensive analysis:

### 🎯 **Executive Summary**
This request aligns with modern HR excellence standards and requires a multi-faceted approach combining compliance, operational efficiency, and employee experience optimization.

### 📋 **Recommended Action Plan**

**Phase 1: Assessment & Planning**
- Conduct stakeholder analysis and requirements gathering
- Review current policies against regulatory compliance standards
- Establish baseline metrics and success criteria

**Phase 2: Implementation Strategy**
- Develop templated frameworks with customization options
- Create communication plan for organizational change management
- Implement monitoring and feedback collection systems

**Phase 3: Optimization & Scaling**
- Analyze performance data and ROI metrics
- Refine processes based on feedback and outcomes
- Scale successful initiatives across organization

### ⚖️ **Compliance Considerations**
• Ensure alignment with current employment law requirements
• Document all processes for audit trail compliance
• Regular review cycles for regulatory updates

### 📊 **Expected Outcomes**
- **Efficiency Gain**: 25-40% improvement in process speed
- **Risk Reduction**: 60% decrease in compliance issues
- **Employee Satisfaction**: 15-20% increase in engagement scores

### 🔄 **Next Steps**
1. Schedule stakeholder alignment meeting
2. Begin pilot program with selected department
3. Establish measurement framework and reporting cadence

*This is a demonstration response. In production, this would connect to your configured AI service to provide real-time, contextual HR guidance.*`;
  };

  const handleClearChat = () => {
    if (window.confirm('Clear all conversation history? This will start a fresh consultation session.')) {
      const initialMessage: Message = {
        id: '1',
        type: 'system',
        // Only show a short greeting, not the full prompt
        content: `👋 Welcome! How can I help you with HR today?`,
        timestamp: new Date(),
        confidence: 100,
        model: 'System'
      };
      setMessages([initialMessage]);
      localStorage.removeItem('hrAssistantMessages');
      toast({ 
        title: 'New Consultation Session', 
        description: 'Ready for fresh strategic HR guidance' 
      });
    }
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast({
      title: 'Content Copied',
      description: 'Professional HR guidance copied to clipboard',
    });
  };

  const handleExportChat = () => {
    const chatExport = messages.map(msg => 
      `[${msg.timestamp.toLocaleString()}] ${msg.type.toUpperCase()}: ${msg.content}`
    ).join('\n\n');
    
    const blob = new Blob([chatExport], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `HR_Consultation_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Chat Exported',
      description: 'Consultation history downloaded successfully'
    });
  };

  const formatTimestamp = (date: Date | string) => {
    const timestamp = typeof date === 'string' ? new Date(date) : date;
    if (timestamp instanceof Date && !isNaN(timestamp.getTime())) {
      return timestamp.toLocaleString([], { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
    return '';
  };

  const getModelData = (modelValue: string) => {
    return models.find(m => m.value === modelValue) || { color: 'gray', badge: '', icon: null, label: '', description: '' };
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'slate';
    if (confidence >= 90) return 'emerald';
    if (confidence >= 75) return 'blue';
    if (confidence >= 60) return 'amber';
    return 'red';
  };

  // Top-level loading and error check
  // Remove top-level early returns for models loading/error
  // Instead, add a warning banner and disable input/send if models are not loaded or selected
  // Show a warning banner if models are not loaded or selected
  if (modelsLoading || !models.length || !selectedModel) {
  return (
      <TooltipProvider>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30 dark:from-slate-900 dark:via-slate-800 dark:to-blue-900/10">
          <div className="container mx-auto px-4 py-6 max-w-7xl">
            <div className="professional-card h-[calc(100vh-3rem)] flex flex-col overflow-hidden animate-fade-in">
              
              {/* Premium Header */}
              <CardHeader className="border-b gradient-bg p-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5" />
                <div className="relative z-10 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="relative">
                      <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-blue-600 via-blue-500 to-indigo-600 flex items-center justify-center shadow-xl shadow-blue-500/25">
                        <Bot className="h-7 w-7 text-white" />
                      </div>
                      <div className="status-online absolute -bottom-1 -right-1" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-display bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                        HR Assistant Pro
                      </h1>
                      <div className="flex items-center space-x-3 mt-2">
                        <Badge variant="secondary" className="text-xs font-medium">
                          <Sparkles className="h-3 w-3 mr-1" />
                          AI-Powered Enterprise
                        </Badge>
                        <Badge variant="outline" className={`text-xs font-medium border-${getModelData(selectedModel).color}-200 text-${getModelData(selectedModel).color}-700`}>
                          {typeof getModelData(selectedModel).icon === 'function' ? React.createElement(getModelData(selectedModel).icon, { className: "h-3 w-3 mr-1" }) : null}
                          {getModelData(selectedModel).badge}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          {chatStats.totalMessages} queries
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="hidden md:flex items-center space-x-4 text-sm text-muted-foreground">
                      <div className="flex items-center space-x-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>{chatStats.totalMessages}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{chatStats.averageResponseTime}s avg</span>
                      </div>
                    </div>
                    
                    <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                      <AvatarImage src="/api/placeholder/40/40" />
                      <AvatarFallback className="text-sm font-semibold bg-gradient-to-br from-slate-100 to-slate-200">HR</AvatarFallback>
                    </Avatar>
                    
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-10 w-10 professional-button">
                          <MoreVertical className="h-5 w-5" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-56">
                        <DropdownMenuItem onClick={() => setShowConfig(true)}>
                          <Settings className="h-4 w-4 mr-2" />
                          Configuration
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={handleExportChat}>
                          <Download className="h-4 w-4 mr-2" />
                          Export Consultation
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={handleClearChat}>
                          <Eraser className="h-4 w-4 mr-2" />
                          New Session
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
                
                {/* Progress Bar for Loading */}
                {isLoading && (
                  <div className="absolute bottom-0 left-0 right-0">
                    <Progress value={responseProgress} className="h-1" />
                  </div>
                )}
              </CardHeader>

              {/* Enhanced Messages Area */}
              <CardContent className="flex-1 overflow-y-auto p-0 scroll-professional">
                <div className="p-6 space-y-8">
                  {messages.map((message, index) => (
                    <div
                      key={message.id}
                      className={`flex gap-4 group chat-message animate-fade-in ${
                        message.type === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      {message.type !== 'user' && (
                        <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                          <div className="h-full w-full bg-[#16B97F] flex items-center justify-center">
                            <Bot className="h-5 w-5 text-white" />
                          </div>
                        </Avatar>
                      )}
                      
                      <div className={`max-w-[85%] relative ${
                        message.type === 'user'
                          ? 'message-user bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-md hover:shadow-lg transition-shadow duration-200'
                          : 'message-bot bg-white dark:bg-slate-900 border-l-4 border-[#16B97F] border border-[#16B97F] shadow-md hover:shadow-lg transition-shadow duration-200'
                      } p-6 group-hover:shadow-lg transition-all duration-300`}>
                        
                        <div className={`prose prose-sm max-w-none ${message.type === 'user' ? 'text-slate-800 dark:text-slate-100' : 'text-blue-900 dark:text-blue-100'}`}>
                          <ReactMarkdown rehypePlugins={[rehypeRaw]} remarkPlugins={[remarkGfm]}>
                            {message.content}
                          </ReactMarkdown>
                        </div>
                        
                      </div>
                      
                      {message.type === 'user' && (
                        <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                          <div className="h-full w-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                            <User className="h-5 w-5 text-slate-600 dark:text-slate-200" />
                          </div>
                        </Avatar>
                      )}
                    </div>
                  ))}
                  
                  {/* Enhanced Typing Indicator */}
                  {isTyping && (
                    <div className="flex gap-4 animate-fade-in">
                      <div className="flex-shrink-0 mt-1">
                        <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                          <div className="h-full w-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                            <Bot className="h-5 w-5 text-white" />
                          </div>
                        </Avatar>
                      </div>
                      <div className="message-bot p-6 max-w-[85%] shimmer-effect">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-muted-foreground">Analyzing your request</span>
                          <div className="typing-indicator">
                            <div className="typing-dot" />
                            <div className="typing-dot" />
                            <div className="typing-dot" />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
              </CardContent>

              {/* Enhanced Input Area */}
              <div className="border-t gradient-bg p-6">
                {/* Quick Actions */}
                <div className="mb-4">
                  <div className="flex flex-wrap gap-2">
                    {QUICK_PROMPTS.map((prompt, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="text-xs professional-button"
                        onClick={() => handleSendMessage(prompt.prompt)}
                        disabled={isLoading}
                      >
                        {prompt.title}
                      </Button>
                    ))}
                  </div>
        </div>
                
                <div className="flex items-end space-x-3">
                  <div className="flex-1 relative">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="Ask about strategic HR initiatives, compliance frameworks, or talent optimization..."
                      className="min-h-[52px] pr-12 rounded-2xl input-professional text-professional resize-none border-border/50 focus:border-primary/50 shadow-sm"
                      onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && !isLoading && handleSendMessage()}
                      disabled={isLoading || modelsLoading || !models.length || !selectedModel}
                    />
        </div>
                  <Button
                    onClick={() => handleSendMessage()}
                    disabled={!inputValue.trim() || isLoading || modelsLoading || !models.length || !selectedModel}
                    className="h-[52px] w-[52px] rounded-2xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 professional-button shadow-lg"
                  >
                    {isLoading ? (
                      <RefreshCw className="h-5 w-5 animate-spin" />
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
        </Button>
                </div>
                
                <div className="flex items-center justify-between mt-4 text-xs text-muted-foreground">
                  <div className="flex items-center space-x-4">
                    <span>Press Enter to send • Shift+Enter for new line</span>
                    <div className="flex items-center space-x-2">
                      <span>Sound:</span>
                      <Switch
                        checked={soundEnabled}
                        onCheckedChange={setSoundEnabled}
                        className="scale-75"
                      />
                      {soundEnabled ? <Volume2 className="h-3 w-3" /> : <VolumeX className="h-3 w-3" />}
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Shield className="h-3 w-3" />
                    <span>Enterprise-grade security & compliance</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Enhanced Settings Dialog */}
        <Dialog open={showConfig} onOpenChange={setShowConfig}>
              <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
            <DialogHeader>
                  <DialogTitle className="flex items-center space-x-2 text-xl">
                    <Settings className="h-6 w-6" />
                    <span>Professional Configuration</span>
                  </DialogTitle>
              <DialogDescription>
                    Configure your AI assistant for optimal HR consultation performance and compliance.
              </DialogDescription>
            </DialogHeader>
                
                <div className="space-y-8 py-6">
                  <div className="space-y-4">
                    <Label className="text-base font-semibold">AI Model Selection</Label>
                    <Select
                      value={selectedModel}
                      onValueChange={setSelectedModel}
                    >
                      <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select AI model" />
                  </SelectTrigger>
                      <SelectContent style={{ maxHeight: '300px', overflowY: 'auto' }}>
                        {modelsLoading ? (
                          <div className="p-4 text-center text-muted-foreground">Loading models...</div>
                        ) : modelsError ? (
                          <div className="p-4 text-center text-red-500">{modelsError}</div>
                        ) : (
                          models.map((model) => (
                            <SelectItem key={model.value || model.id || model.name} value={model.value || model.id || model.name}>
                              <div className="flex items-center justify-between w-full">
                                <div className="flex items-center space-x-2">
                                  {/* Optionally use an icon if available */}
                                  <span>{model.label || model.id || model.name}</span>
                                </div>
                                {model.badge && <Badge variant="outline" className="ml-2 text-xs">{model.badge}</Badge>}
                              </div>
                      </SelectItem>
                          ))
                        )}
                  </SelectContent>
                </Select>
                    <p className="text-sm text-muted-foreground">
                      {getModelData(selectedModel).description}
                    </p>
              </div>
                  
                  <Separator />
                  
                  <div className="space-y-4">
                    <Label className="text-base font-semibold">Professional Instructions</Label>
                <Textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                      className="min-h-[250px] text-sm font-mono"
                      placeholder="Define your AI assistant's expertise and behavior patterns..."
                    />
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Comprehensive instructions ensure optimal professional guidance.</span>
                      <span>{customPrompt.length} characters</span>
                    </div>
                  </div>
                  
                  <Separator />
                  
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Session Statistics</Label>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Total Messages:</span>
                          <span className="font-mono">{chatStats.totalMessages}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Tokens:</span>
                          <span className="font-mono">{chatStats.totalTokens.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg Response Time:</span>
                          <span className="font-mono">{chatStats.averageResponseTime}s</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Preferences</Label>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Sound Notifications</span>
                          <Switch
                            checked={soundEnabled}
                            onCheckedChange={setSoundEnabled}
                          />
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Auto-scroll Messages</span>
                          <Switch checked={true} disabled />
                        </div>
                      </div>
                    </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
          </div>
        </div>
      </TooltipProvider>
    );
  }

  // Use safe modelData everywhere in JSX
  const modelData = getModelData(selectedModel);
  const color = modelData.color || 'gray';
  const badge = modelData.badge || '';
  const icon = modelData.icon || null;
  const label = modelData.label || '';
  const description = modelData.description || '';

  // Restore the three-dot (More/Settings) menu in the chat header
  return (
    <TooltipProvider>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30 dark:from-slate-900 dark:via-slate-800 dark:to-blue-900/10 flex flex-col items-stretch">
        <div className="w-full flex flex-col flex-1">
          {/* Feature-rich Header with More/Settings menu */}
          <div className="flex items-center justify-between py-4 px-4 bg-white dark:bg-slate-900 shadow-md border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="h-10 flex items-center justify-center px-4 text-lg font-semibold border-blue-400 text-blue-700 bg-blue-50 dark:bg-blue-900 dark:text-blue-200 shadow-md">
                {label || 'Model'}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <MessageSquare className="h-4 w-4" />
                <span>{chatStats.totalMessages}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{chatStats.averageResponseTime}s avg</span>
              </div>
              <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                <AvatarImage src="/api/placeholder/40/40" />
                <AvatarFallback className="text-sm font-semibold bg-gradient-to-br from-slate-100 to-slate-200">HR</AvatarFallback>
              </Avatar>
              {/* Three-dot More/Settings menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-10 w-10">
                    <MoreVertical className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem onClick={() => setShowConfig(true)}>
                    <Settings className="h-4 w-4 mr-2" />
                    Configuration
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleExportChat}>
                    <Download className="h-4 w-4 mr-2" />
                    Export Consultation
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleClearChat}>
                    <Eraser className="h-4 w-4 mr-2" />
                    New Session
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          {/* Chat Area with Input Inside */}
          <div className="flex-1 flex flex-col bg-white dark:bg-slate-900 shadow-md overflow-hidden">
            <div className="flex-1 overflow-y-auto px-2 sm:px-6 py-6 space-y-6" style={{scrollBehavior: 'smooth'}}>
              {messages.map((message, index) => (
                <div
                  key={message.id}
                  className={`flex gap-4 group chat-message animate-fade-in ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {message.type !== 'user' && (
                    <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                      <div className={`h-full w-full ${message.type === 'system' ? 'bg-gradient-to-br from-emerald-500 to-emerald-600' : 'bg-gradient-to-br from-blue-500 to-blue-600'} flex items-center justify-center`}>
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                    </Avatar>
                  )}
                  <div className={`max-w-[85%] relative ${message.type === 'user' ? 'message-user' : message.type === 'error' ? 'message-error' : message.type === 'system' ? 'message-bot border-emerald-200 dark:border-emerald-800' : 'message-bot'} p-6 group-hover:shadow-lg transition-all duration-300`}>
                    <div className={`prose prose-sm max-w-none text-professional ${message.type === 'user' ? 'prose-invert' : 'dark:prose-invert'}`}>
                      <ReactMarkdown rehypePlugins={[rehypeRaw]} remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                    </div>
                  </div>
                  {message.type === 'user' && (
                    <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                      <div className="h-full w-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center">
                        <User className="h-5 w-5 text-white" />
                      </div>
                    </Avatar>
                  )}
                </div>
              ))}
              {isTyping && (
                <div className="flex gap-4 animate-fade-in">
                  <div className="flex-shrink-0 mt-1">
                    <Avatar className="h-10 w-10 border-2 border-white shadow-lg">
                      <div className="h-full w-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                    </Avatar>
                  </div>
                  <div className="message-bot p-6 max-w-[85%] shimmer-effect">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-muted-foreground">Analyzing your request</span>
                      <div className="typing-indicator">
                        <div className="typing-dot" />
                        <div className="typing-dot" />
                        <div className="typing-dot" />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            {/* Quick Prompts as Chips */}
            <div className="flex flex-wrap gap-2 px-4 pb-2">
              {QUICK_PROMPTS.map((prompt, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="rounded-full px-4 py-1 text-xs border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-700"
                  onClick={() => handleSendMessage(prompt.prompt)}
                  disabled={isLoading}
                >
                  {prompt.title}
                </Button>
              ))}
            </div>
            {/* Input Bar inside chat container */}
            <div className="w-full px-2 py-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-end gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about strategic HR initiatives, compliance frameworks, or talent optimization..."
                className="flex-1 min-h-[44px] rounded-2xl border border-blue-200 focus:border-blue-500 shadow-sm text-base"
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && !isLoading && handleSendMessage()}
                disabled={isLoading || modelsLoading || !models.length || !selectedModel}
              />
              <Button
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isLoading || modelsLoading || !models.length || !selectedModel}
                className="h-11 w-11 rounded-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg flex items-center justify-center"
              >
                {isLoading ? (
                  <RefreshCw className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
      {/* Configuration Dialog */}
      <Dialog open={showConfig} onOpenChange={setShowConfig}>
        <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2 text-xl">
              <Settings className="h-6 w-6" />
              <span>Professional Configuration</span>
            </DialogTitle>
            <DialogDescription>
              Configure your AI assistant for optimal HR consultation performance and compliance.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-8 py-6">
            <div className="space-y-4">
              <Label className="text-base font-semibold">AI Model Selection</Label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select AI model" />
                </SelectTrigger>
                <SelectContent style={{ maxHeight: '300px', overflowY: 'auto' }}>
                  {modelsLoading ? (
                    <div className="p-4 text-center text-muted-foreground">Loading models...</div>
                  ) : modelsError ? (
                    <div className="p-4 text-center text-red-500">{modelsError}</div>
                  ) : (
                    models.map((model) => (
                      <SelectItem key={model.value || model.id || model.name} value={model.value || model.id || model.name}>
                        <div className="flex items-center justify-between w-full">
                          <div className="flex items-center space-x-2">
                            <span>{model.label || model.id || model.name}</span>
                          </div>
                          {model.badge && <Badge variant="outline" className="ml-2 text-xs">{model.badge}</Badge>}
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">{getModelData(selectedModel).description}</p>
            </div>
            <Separator />
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-sm font-medium">Session Statistics</Label>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Total Messages:</span>
                    <span className="font-mono">{chatStats.totalMessages}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Tokens:</span>
                    <span className="font-mono">{chatStats.totalTokens.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg Response Time:</span>
                    <span className="font-mono">{chatStats.averageResponseTime}s</span>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Preferences</Label>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Sound Notifications</span>
                    <Switch checked={soundEnabled} onCheckedChange={setSoundEnabled} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Auto-scroll Messages</span>
                    <Switch checked={true} disabled />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </TooltipProvider>
  );
};

export default HRAssistantPro;