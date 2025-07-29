import React, { useEffect, useState, useRef } from 'react';
import {
  Send, Bot, User, Settings, Eraser, Copy, MoreVertical, MessageSquare, RefreshCw,
  Volume2, VolumeX, Download, Building2, Shield, TrendingUp, Users, Pencil, Plus, Check, X, Trash2, ChevronLeft, ChevronRight, Paperclip, AppWindow, Megaphone, Brush, Globe, PenTool, Mic, ArrowUp,
  FileText, List, Briefcase, Search
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator, DropdownMenuSub, DropdownMenuSubTrigger, DropdownMenuSubContent } from '@/components/ui/dropdown-menu';
import { Switch } from '@/components/ui/switch';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Card, CardContent } from '@/components/ui/card';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { sendMessage, fetchModels, getChatSessions, createChatSession, deleteChatSession, getChatMessages, createChatMessage, updateChatSession } from '@/services/chatService';
import { format } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import ChatSidebar from '@/components/layout/ChatSidebar';

// Interfaces
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

const SIDEBAR_COLLAPSED_KEY = 'chatSidebarCollapsed';

// ErrorBoundary Component
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean; error: any }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950 p-4">
          <div className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">System Error</div>
          <div className="text-red-500 dark:text-red-300 text-sm max-w-xl text-center">{String(this.state.error)}</div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Professional Header Component
const ChatHeader: React.FC<{
  selectedModel: string;
  models: any[];
  chatStats: ChatStats;
  onOpenConfig: () => void;
  onExportChat: () => void;
  onClearChat: () => void;
  sessionModel: string;
  onModelChange: (modelId: string) => void;
  availableModels: any[];
}> = ({ selectedModel, models, chatStats, onOpenConfig, onExportChat, onClearChat, sessionModel, onModelChange, availableModels }) => {
  const modelData = models.find(m => m.id === selectedModel) || { label: 'Loading...', badge: '' };
  
  return (
    <div className="sticky top-0 z-20 bg-white/95 dark:bg-slate-950/95 backdrop-blur-sm border-b border-slate-200/60 dark:border-slate-800/60 shadow-sm">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Brand Section */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <Avatar className="h-10 w-10 ring-2 ring-slate-200 dark:ring-slate-700">
                <AvatarFallback className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white font-semibold">
                  <Building2 className="h-5 w-5" />
                </AvatarFallback>
              </Avatar>
              <div className="absolute -bottom-1 -right-1 h-4 w-4 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-950"></div>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                {/* Status row removed */}
              </div>
            </div>
          </div>

          {/* Stats & Actions */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
              <div className="flex items-center gap-1">
                <MessageSquare className="h-4 w-4" />
                <span className="font-medium">{chatStats.totalMessages}</span>
              </div>
              <div className="flex items-center gap-1">
                <TrendingUp className="h-4 w-4" />
                <span className="font-medium">{chatStats.averageResponseTime}s</span>
              </div>
            </div>
            
            <Separator orientation="vertical" className="h-6 hidden md:block" />
            
            <div className="flex items-center gap-1">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-9 w-9" onClick={onClearChat}>
                      <Eraser className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Clear conversation</TooltipContent>
                </Tooltip>
              </TooltipProvider>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-9 w-9">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-52">
                  <DropdownMenuItem onClick={onOpenConfig} className="cursor-pointer">
                    <Settings className="h-4 w-4 mr-3" />
                    Settings & Configuration
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={onExportChat} className="cursor-pointer">
                    <Download className="h-4 w-4 mr-3" />
                    Export Conversation
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced Message Component
const ChatMessage = React.forwardRef<HTMLDivElement, { message: Message; onCopy: (content: string) => void }>(
  ({ message, onCopy }, ref) => {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';
  const isError = message.type === 'error';
  
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`flex gap-4 group px-6 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[75%]`}>
        <Card className={`group-hover:shadow-md transition-all duration-200 border-0 ${
          isUser 
            ? 'bg-[#6B7280] text-white shadow-lg' 
            : isError
              ? 'bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300'
              : isSystem
                ? 'bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20 border border-emerald-200 dark:border-emerald-800'
                : 'bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800'
        }`}>
          <CardContent className="p-4 relative">
            <div className={`prose prose-sm max-w-none ${
              isUser ? 'prose-invert' : 
              isSystem ? 'prose-emerald dark:prose-invert' :
              'dark:prose-invert'
            }`}>
              <ReactMarkdown
                rehypePlugins={[rehypeRaw]}
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  ul: ({ children }) => <ul className="mb-2 last:mb-0">{children}</ul>,
                  ol: ({ children }) => <ol className="mb-2 last:mb-0">{children}</ol>,
                }}
              >
                {typeof message.content === 'string' ? message.content : JSON.stringify(message.content)}
              </ReactMarkdown>
            </div>
            
            {/* Copy Button */}
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className={`h-7 w-7 p-0 ${isUser ? 'hover:bg-white/20' : 'hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                      onClick={() => onCopy(message.content)}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Copy message</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </CardContent>
        </Card>
        
      </div>
      
    </motion.div>
  );
});

// Professional Input Bar
const InputBar = ({ 
  value, 
  onChange, 
  onSend, 
  isLoading, 
  disabled, 
  onNewChat,
  selectedModel,
  availableModels,
  onModelChange,
}) => (
  <div className="flex flex-col gap-2 w-full px-4 pb-4">
    <div className="relative w-full">
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Ask anything"
        className="w-full rounded-full bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white px-6 py-4 pr-14 border-0 shadow-none focus:ring-2 focus:ring-blue-500 focus:outline-none text-lg placeholder:text-slate-400 min-h-[56px] max-h-[120px] resize-none"
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey && !isLoading && !disabled) {
            e.preventDefault();
            onSend();
          }
        }}
        disabled={disabled}
        aria-label="Enter your query"
        style={{ fontWeight: 500 }}
      />
      <Button
        variant="ghost"
        size="icon"
        className={`absolute right-2 top-1/2 -translate-y-1/2 h-12 w-12 rounded-full flex items-center justify-center border-0 shadow-none transition
    ${value.trim() ? 'bg-zinc-800 hover:bg-zinc-700' : 'bg-white hover:bg-gray-200'}`}
  onClick={onSend}
  disabled={isLoading || disabled || !value.trim()}
  aria-label="Send message"
>
  <ArrowUp className={`h-6 w-6 ${value.trim() ? 'text-white' : 'text-zinc-900'}`} />
</Button>
      <Button
        variant="ghost"
        size="icon"
        className="absolute right-14 top-1/2 -translate-y-1/2 h-10 w-10 text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
        aria-label="Voice input"
        type="button"
        disabled
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
      </Button>
    </div>
    <div className="flex items-center gap-2 mt-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full h-10 w-10 flex items-center justify-center bg-slate-700/80 hover:bg-slate-600/80 text-white"
            aria-label="Add"
            type="button"
          >
            <Plus className="h-5 w-5" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-60 rounded-xl shadow-lg border border-slate-700 mt-2 bg-slate-800 text-white">
          <DropdownMenuItem className="flex items-center cursor-pointer rounded-lg px-3 py-2 hover:bg-slate-700">
            <Paperclip className="h-4 w-4 mr-2" />
            <span>Add photos & files</span>
          </DropdownMenuItem>
          <DropdownMenuSub>
            <DropdownMenuSubTrigger className="flex items-center cursor-pointer rounded-lg px-3 py-2 hover:bg-slate-700">
              <AppWindow className="h-4 w-4 mr-2" />
              <span>Add from apps</span>
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent className="w-56 rounded-xl shadow-lg border border-slate-700 mt-2 bg-slate-800">
              <DropdownMenuItem disabled className="text-slate-400">Coming soon…</DropdownMenuItem>
            </DropdownMenuSubContent>
          </DropdownMenuSub>
        </DropdownMenuContent>
      </DropdownMenu>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="rounded-full flex items-center gap-2 h-10 px-4 font-medium text-sm bg-slate-700/80 hover:bg-slate-600/80 text-white shadow-none border-none"
            aria-label="Tools"
            type="button"
          >
            <Settings className="h-5 w-5" />
            <span className="hidden md:inline">Tools</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-72 rounded-xl shadow-lg border border-slate-700 mt-2 bg-slate-800 text-white max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800 p-2">
          {[
            { name: 'Get Candidate', desc: 'get_candidate <candidate_id>', icon: <User className="h-5 w-5 mr-2" /> },
            { name: 'Delete Candidate', desc: 'delete_candidate <candidate_id>', icon: <Trash2 className="h-5 w-5 mr-2" /> },
            { name: 'Update Candidate', desc: 'update_candidate <candidate_id> <field> <value>', icon: <Pencil className="h-5 w-5 mr-2" /> },
            { name: 'Candidate Metrics', desc: 'get_candidate_metrics', icon: <TrendingUp className="h-5 w-5 mr-2" /> },
            { name: 'List Candidates', desc: 'list_candidates', icon: <Users className="h-5 w-5 mr-2" /> },
            { name: 'Add Candidate', desc: 'add_candidate', icon: <User className="h-5 w-5 mr-2" /> },
            { name: 'Add Note', desc: 'add_note <candidate_id> <content>', icon: <FileText className="h-5 w-5 mr-2" /> },
            { name: 'List Notes', desc: 'list_notes <candidate_id>', icon: <List className="h-5 w-5 mr-2" /> },
            { name: 'Delete Note', desc: 'delete_note <note_id>', icon: <Trash2 className="h-5 w-5 mr-2" /> },
            { name: 'List Job Titles', desc: 'list_job_titles', icon: <Briefcase className="h-5 w-5 mr-2" /> },
            { name: 'Export Candidates', desc: 'export_candidates_csv', icon: <Download className="h-5 w-5 mr-2" /> },
            { name: 'Recent Activities', desc: 'get_recent_activities', icon: <TrendingUp className="h-5 w-5 mr-2" /> },
            { name: 'Overall Metrics', desc: 'get_overall_metrics', icon: <TrendingUp className="h-5 w-5 mr-2" /> },
            { name: 'List Job Posts', desc: 'list_job_posts', icon: <FileText className="h-5 w-5 mr-2" /> },
            { name: 'Add Job Post', desc: 'add_job_post', icon: <Plus className="h-5 w-5 mr-2" /> },
            { name: 'Update Job Post', desc: 'update_job_post <job_post_id>', icon: <Pencil className="h-5 w-5 mr-2" /> },
            { name: 'Delete Job Post', desc: 'delete_job_post <job_post_id>', icon: <Trash2 className="h-5 w-5 mr-2" /> },
            { name: 'Job Post Choices', desc: 'get_job_post_title_choices', icon: <List className="h-5 w-5 mr-2" /> },
            { name: 'Search Candidates', desc: 'search_candidates <filters>', icon: <Search className="h-5 w-5 mr-2" /> },
            { name: 'Bulk Update', desc: 'bulk_update_candidates <ids> <field> <value>', icon: <Users className="h-5 w-5 mr-2" /> },
            { name: 'Bulk Delete', desc: 'bulk_delete_candidates <ids>', icon: <Trash2 className="h-5 w-5 mr-2" /> },
            { name: 'Get Job Post', desc: 'get_job_post <job_post_id>', icon: <FileText className="h-5 w-5 mr-2" /> },
          ].map(tool => (
            <DropdownMenuItem
              key={tool.name}
              onClick={() => onChange(tool.desc)}
              className="flex items-center cursor-pointer rounded-lg px-3 py-2 hover:bg-slate-700 text-sm"
            >
              {tool.icon}
              <span>{tool.name}</span>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
      <Select
        value={selectedModel}
        onValueChange={onModelChange}
        disabled={disabled}
      >
        <SelectTrigger className="w-[180px] text-sm bg-slate-700/80 hover:bg-slate-600/80 text-white rounded-full h-10 px-4">
          <SelectValue placeholder="Select Model" />
        </SelectTrigger>
        <SelectContent style={{ maxHeight: 240, overflowY: 'auto' }}>
          {availableModels.map((model) => (
            <SelectItem key={model.id} value={model.id}>
              {model.label || model.id}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  </div>
);

// Typing Indicator
const TypingIndicator = React.forwardRef<HTMLDivElement>((props, ref) => (
  <motion.div
    ref={ref}
    initial={{ opacity: 0, y: 15 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -15 }}
    transition={{ duration: 0.3 }}
    className="flex gap-4 px-6"
  >
    <Avatar className="h-8 w-8 mt-1 ring-2 ring-blue-200 dark:ring-blue-800">
      <AvatarFallback className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
        <Bot className="h-4 w-4" />
      </AvatarFallback>
    </Avatar>
    <Card className="bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800">
      <CardContent className="p-4 flex items-center gap-3">
        <span className="text-sm text-slate-600 dark:text-slate-400 font-medium">Analyzing your request</span>
        <div className="flex gap-1">
          <div className="h-2 w-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
          <div className="h-2 w-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          <div className="h-2 w-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
        </div>
      </CardContent>
    </Card>
  </motion.div>
));

// Main Component
const HRAssistantPro: React.FC = () => {
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: `👋 Welcome to HR Assistant Pro! How can I help you with HR today?`,
      timestamp: new Date(),
      confidence: 100,
      model: 'System',
    },
  ]);

  // Auth integration for logout/destruct
  const { user, isAuthenticated } = useAuth();
  useEffect(() => {
    if (!user || !isAuthenticated) {
      setMessages([
        {
          id: '1',
          type: 'system',
          content: `👋 Welcome to HR Assistant Pro! How can I help you with HR today?`,
          timestamp: new Date(),
          confidence: 100,
          model: 'System',
        },
      ]);
      localStorage.removeItem('hrAiModel');
    }
  }, [user, isAuthenticated]);

  // Load messages from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('chatMessages');
    if (saved) {
      setMessages(JSON.parse(saved));
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);

  const [inputValue, setInputValue] = useState('');
  
  const DEFAULT_PROMPT = `You are HR Assistant Pro, a friendly and highly capable AI HR assistant. Greet users warmly, answer their HR-related questions conversationally, and use your available tools to help with candidate management, analytics, and HR operations whenever appropriate. If a user asks for candidate details, analytics, or CRUD actions, proactively use your tools to fetch or update data. If the user asks a general HR question, answer conversationally and helpfully. Always be clear, concise, and supportive. If you need more information, politely ask clarifying questions. If a tool fails, explain the issue and suggest next steps. Your goal is to make HR easy, efficient, and approachable for everyone.`;
  
  const QUICK_PROMPTS = [
    {
      title: 'Interview Framework',
      prompt: 'Design a comprehensive interview framework for evaluating senior software engineers, including technical and behavioral assessment criteria.',
      icon: <Users className="h-3 w-3" />
    },
    {
      title: 'Job Description',
      prompt: 'Create a detailed job description for a Product Manager role, including requirements, responsibilities, and success metrics.',
      icon: <Building2 className="h-3 w-3" />
    },
    {
      title: 'Performance Review',
      prompt: 'Develop a 360-degree performance review framework with clear KPIs and evaluation criteria for mid-level managers.',
      icon: <TrendingUp className="h-3 w-3" />
    },
    {
      title: 'Onboarding Program',
      prompt: 'Design a comprehensive 90-day onboarding program for remote employees, including milestones and check-in processes.',
      icon: <Shield className="h-3 w-3" />
    },
  ];

  const [models, setModels] = useState<any[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState('');
  const [selectedModel, setSelectedModel] = useState(() => localStorage.getItem('hrAiModel') || '');
  const [isLoading, setIsLoading] = useState(false);
  const [customPrompt, setCustomPrompt] = useState(DEFAULT_PROMPT);
  const [showConfig, setShowConfig] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [chatStats, setChatStats] = useState<ChatStats>({
    totalMessages: 0,
    totalTokens: 0,
    averageResponseTime: 1.2,
    sessionsToday: 1,
  });

  // Add state for model search
  const [modelSearch, setModelSearch] = useState('');
  const [showClearModal, setShowClearModal] = useState(false);
  const [cancelRequested, setCancelRequested] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Add pendingMessages state:
  const [pendingMessages, setPendingMessages] = useState<Message[]>([]);

  // Persist selected model to localStorage
  useEffect(() => {
    if (selectedModel) {
      localStorage.setItem('hrAiModel', selectedModel);
    }
  }, [selectedModel]);

  // Fetch models
  useEffect(() => {
    const loadModels = async () => {
      setModelsLoading(true);
      setModelsError('');
      try {
        const data = await fetchModels();
        setModels(Array.isArray(data) ? data : []);
      } catch (err) {
        setModelsError('Failed to load AI models.');
        toast({ 
          title: 'System Error', 
          description: 'Unable to connect to AI services.', 
          variant: 'destructive' 
        });
      } finally {
        setModelsLoading(false);
      }
    };
    loadModels();
  }, []);

  // Restore selected model from localStorage or default to first model after models are loaded
  useEffect(() => {
    if (models.length > 0) {
      const saved = localStorage.getItem('hrAiModel');
      const found = models.find(m => m.id === saved);
      if (found) {
        setSelectedModel(found.id);
      } else {
        setSelectedModel(models[0].id);
        localStorage.setItem('hrAiModel', models[0].id);
      }
    }
  }, [models]);

  // Update stats
  useEffect(() => {
    setChatStats((prev) => ({
      ...prev,
      totalMessages: messages.filter((m) => m.type !== 'system').length,
    }));
  }, [messages]);

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Add a ref to track if the user is near the bottom
  const isUserAtBottomRef = useRef(true);

  // Attach a scroll event to the chat container to update isUserAtBottomRef
  // (Assume chat container has ref chatContainerRef)
  const chatContainerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const handleScroll = () => {
      const el = chatContainerRef.current;
      if (!el) return;
      // 40px threshold
      isUserAtBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
    };
    const el = chatContainerRef.current;
    if (el) el.addEventListener('scroll', handleScroll);
    return () => {
      if (el) el.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Only scroll to bottom if user is at bottom or a new user message is sent
  const prevMessagesLength = useRef(messages.length);
  useEffect(() => {
    const newMessageAdded = messages.length > prevMessagesLength.current;
    prevMessagesLength.current = messages.length;
    if (newMessageAdded && isUserAtBottomRef.current) {
      scrollToBottom();
    }
  }, [messages]);

  // Notification sound
  const playNotificationSound = () => {
    if (soundEnabled) {
      const audio = new Audio('/notification.mp3');
      audio.play().catch(() => {});
    }
  };

  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [sessionsError, setSessionsError] = useState('');
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [editingSessionId, setEditingSessionId] = useState<number | null>(null);
  const [editingSessionName, setEditingSessionName] = useState('');
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [newChatName, setNewChatName] = useState('');
  const [newChatRole, setNewChatRole] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<number | null>(null);
  const [menuOpenId, setMenuOpenId] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const stored = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
    return stored === 'true';
  });

  useEffect(() => {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, sidebarCollapsed ? 'true' : 'false');
  }, [sidebarCollapsed]);

  // Fetch sessions on mount
  useEffect(() => {
    setSessionsLoading(true);
    setSessionsError('');
    getChatSessions()
      .then(data => setSessions(Array.isArray(data) ? data : data.results || []))
      .catch(() => setSessionsError('Failed to load chat sessions.'))
      .finally(() => setSessionsLoading(false));
  }, []);

  // When a session is selected, load its messages
  useEffect(() => {
    if (activeSessionId) {
      getChatMessages(activeSessionId).then(data => {
        const msgs = data.results || data;
        setMessages(msgs.map((m: any) => ({
          id: m.id,
          type: m.role === 'user' ? 'user' : m.role === 'assistant' ? 'bot' : 'system',
          content: m.content,
          timestamp: new Date(m.timestamp),
          model: m.role === 'assistant' ? 'AI' : undefined,
        })));
      });
    }
    // eslint-disable-next-line
  }, [activeSessionId]);

  // Merge in pendingMessages after messages are fetched
  useEffect(() => {
    if (!activeSessionId) return;
    setMessages(prevMessages => {
      const backendContents = new Set(prevMessages.map((m: any) => (typeof m.content === 'string' ? m.content.trim() : '')));
      const filteredPending = pendingMessages.filter(m => !backendContents.has((typeof m.content === 'string' ? m.content.trim() : '')));
      return [...prevMessages, ...filteredPending];
    });
    // Clean up pendingMessages that are now in the backend
    setPendingMessages(prev => {
      const backendContents = new Set(messages.map((m: any) => (typeof m.content === 'string' ? m.content.trim() : '')));
      return prev.filter(m => !backendContents.has((typeof m.content === 'string' ? m.content.trim() : '')));
    });
    // eslint-disable-next-line
  }, [pendingMessages, activeSessionId]);

  const handleSelectSession = (id: number) => {
    setActiveSessionId(id);
  };

  const handleNewChat = async () => {
    const session = await createChatSession({});
    setSessions(prev => [session, ...prev.filter(s => s.id !== session.id)]); // Move new chat to top
    setActiveSessionId(session.id);
    setMessages([]);
  };

  const handleRenameSession = (id: number, currentName: string) => {
    setEditingSessionId(id);
    setEditingSessionName(currentName || '');
  };

  const handleSaveRename = async (id: number) => {
    // PATCH the session name
    await updateChatSession(id, { session_name: editingSessionName });
    setSessions(prev => prev.map(s => s.id === id ? { ...s, session_name: editingSessionName } : s));
    setEditingSessionId(null);
    setEditingSessionName('');
  };

  const handleCancelRename = () => {
    setEditingSessionId(null);
    setEditingSessionName('');
  };

  const handleCreateChat = async () => {
    if (!newChatName.trim()) {
      toast({ title: 'Please enter a chat name.' });
      return;
    }
    const session = await createChatSession({ session_name: newChatName, role: newChatRole });
    setSessions(prev => [session, ...prev]);
    setActiveSessionId(session.id);
    setShowNewChatModal(false);
  };

  const handleDeleteSession = (id: number) => {
    setSessionToDelete(id);
    setShowDeleteModal(true);
  };

  const confirmDeleteSession = async () => {
    if (sessionToDelete) {
      await deleteChatSession(sessionToDelete);
      setSessions(prev => prev.filter(s => s.id !== sessionToDelete));
      if (activeSessionId === sessionToDelete) {
        setActiveSessionId(null);
        setMessages([]);
      }
      setShowDeleteModal(false);
      setSessionToDelete(null);
    }
  };

  const [sessionModel, setSessionModel] = useState(selectedModel);

  // When a chat is selected, set sessionModel to its model
  useEffect(() => {
    const session = sessions.find(s => s.id === activeSessionId);
    if (session && session.model) {
      setSessionModel(session.model);
    }
  }, [activeSessionId, sessions]);

  // When the model is changed in the dropdown
  const handleModelChange = async (modelId: string) => {
    setSessionModel(modelId);
    if (activeSessionId) {
      await updateChatSession(activeSessionId, { model: modelId });
      setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, model: modelId } : s));
    }
  };

  const handleSendMessage = async (messageText?: string) => {
    let sessionId = activeSessionId;
    let isNewSession = false;
    if (!sessionId) {
      const session = await createChatSession({});
      setSessions(prev => [session, ...prev.filter(s => s.id !== session.id)]);
      setActiveSessionId(session.id);
      sessionId = session.id;
      isNewSession = true;
    }
    const tempId = 'pending-' + Date.now();
    const userMessage: Message = {
      id: tempId,
      type: 'user',
      content: messageText || inputValue,
      timestamp: new Date(),
      tokens: Math.ceil((messageText || inputValue).length / 4),
    };
    // Save user message to backend
    await createChatMessage({ session: sessionId, role: 'user', content: userMessage.content });
    
    // If this is a new session, refresh the session list to get the auto-generated name
    if (isNewSession) {
      try {
        const updatedSessions = await getChatSessions();
        setSessions(Array.isArray(updatedSessions) ? updatedSessions : updatedSessions.results || []);
      } catch (error) {
        console.error('Failed to refresh sessions:', error);
      }
    }
    
    setPendingMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setIsTyping(true);
    setCancelRequested(false);

    try {
      abortControllerRef.current = new AbortController();
      // Use both confirmed and pending messages for context
      const fullHistory = [
        ...messages,
        ...pendingMessages,
        userMessage
      ].filter(m => m.type === 'user' || m.type === 'bot');
      const history = fullHistory.map((m) => ({
        role: m.type === 'user' ? 'user' : 'assistant',
        content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content),
      }));
      const mcpMessages = [
        { role: 'system', content: customPrompt },
        ...history,
      ];
      const modelToUse = sessionModel || selectedModel;
      const response = await sendMessage({
        model: modelToUse,
        messages: mcpMessages,
        prompt: customPrompt,
      }, undefined, undefined, { signal: abortControllerRef.current.signal });
      setIsTyping(false);

      const botResponse: Message = {
        id: `${Date.now()}_bot`,
        type: 'bot',
        content: response.response || 'I apologize, but I was unable to generate a response. Please try rephrasing your question.',
        timestamp: new Date(),
        model: selectedModel,
        confidence: Math.round(85 + Math.random() * 15),
        tokens: Math.ceil((response.response || '').length / 4),
      };
      setMessages((prev) => [...prev, botResponse]);
      setIsLoading(false);
      playNotificationSound();
      setChatStats((prev) => ({
        ...prev,
        totalTokens: prev.totalTokens + (userMessage.tokens || 0) + (botResponse.tokens || 0),
        averageResponseTime: 1.2 + Math.random() * 0.8,
      }));
      await createChatMessage({ session: sessionId, role: 'assistant', content: response.response || 'I apologize, but I was unable to generate a response. Please try rephrasing your question.' });
      setPendingMessages(prev => prev.filter(m => m.id !== tempId));
    } catch (error: any) {
      setIsTyping(false);
      setIsLoading(false);
      setPendingMessages(prev => prev.filter(m => m.id !== tempId));
      let errorMsg = 'I encountered an error while processing your request. Please try again or contact support if the issue persists.';
      let toastMsg = 'Failed to get a response from the AI service.';
      const errStr = (error?.message || error?.toString() || '').toLowerCase();
      if (errStr.includes('limit') || errStr.includes('quota') || errStr.includes('rate')) {
        errorMsg = '⚠️ Sorry, our AI service is temporarily unavailable due to usage limits or quota. Please try again later or contact support if this issue persists.';
        toastMsg = 'Rate limit or quota exceeded. Please try again later.';
      } else if (errStr.includes('network')) {
        errorMsg = '⚠️ Network error: Unable to reach the AI service. Please check your connection and try again.';
        toastMsg = 'Network error: Unable to reach the AI service.';
      } else if (errStr.includes('timeout')) {
        errorMsg = '⚠️ The request to the AI service timed out. Please try again.';
        toastMsg = 'AI service timeout. Please try again.';
      }
      setMessages((prev) => [
        ...prev,
        {
          id: `${Date.now()}_error`,
          type: 'error',
          content: errorMsg,
          timestamp: new Date(),
        },
      ]);
      toast({ 
        title: 'Service Error', 
        description: toastMsg, 
        variant: 'destructive' 
      });
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    setCancelRequested(true);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsTyping(false);
    setIsLoading(false);
  };

  const handleClearChat = () => {
    setShowClearModal(true);
  };

  const confirmClearChat = () => {
    setMessages([]);
    localStorage.removeItem('chatMessages');
    setShowClearModal(false);
      toast({ 
        title: 'Conversation Cleared', 
        description: 'Started a new consultation session.' 
      });
  };

  const cancelClearChat = () => {
    setShowClearModal(false);
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast({ 
      title: 'Copied to Clipboard', 
      description: 'Message content has been copied successfully.' 
    });
  };

  const handleExportChat = () => {
    const chatExport = messages
      .map((msg) => `[${format(msg.timestamp, 'MMM d, HH:mm')}] ${msg.type.toUpperCase()}: ${msg.content}`)
      .join('\n\n');
    const blob = new Blob([chatExport], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `HR_Consultation_${format(new Date(), 'yyyy-MM-dd_HH-mm')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast({ 
      title: 'Export Complete', 
      description: 'Conversation history has been downloaded.' 
    });
  };

  // Fix: ensure model dropdown below input updates both selectedModel and sessionModel
  const handleInputBarModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    setSessionModel(modelId);
    if (activeSessionId) {
      updateChatSession(activeSessionId, { model: modelId });
      setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, model: modelId } : s));
    }
  };

  return (
    <ErrorBoundary>
      <TooltipProvider>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-blue-950/10 flex flex-col">
          {/* Status Banner */}
          {(modelsLoading || modelsError || models.length === 0) && (
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20 text-amber-800 dark:text-amber-200 p-4 text-sm border-b border-amber-200 dark:border-amber-800">
              <div className="max-w-4xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-amber-500 rounded-full animate-pulse"></div>
                  {modelsLoading ? 'Initializing AI systems...' : modelsError || 'System configuration required'}
                </div>
                {modelsError && (
                  <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
                    Retry Connection
                  </Button>
                )}
              </div>
            </div>
          )}

          <ChatHeader
            selectedModel={selectedModel}
            models={models}
            chatStats={chatStats}
            onOpenConfig={() => setShowConfig(true)}
            onExportChat={handleExportChat}
            onClearChat={handleClearChat}
            sessionModel={sessionModel}
            onModelChange={handleModelChange}
            availableModels={models}
          />

          <div className="flex h-screen">
            <ChatSidebar
              sessions={sessions} // sessions already sorted with newest on top
              activeSessionId={activeSessionId}
              onSelect={handleSelectSession}
              onRename={handleRenameSession}
              onDelete={handleDeleteSession}
              editingSessionId={editingSessionId}
              editingSessionName={editingSessionName}
              setEditingSessionName={setEditingSessionName}
              onSaveRename={handleSaveRename}
              onCancelRename={handleCancelRename}
              menuOpenId={menuOpenId}
              setMenuOpenId={setMenuOpenId}
              onNewChat={handleNewChat}
              collapsed={sidebarCollapsed}
              onToggleCollapse={() => setSidebarCollapsed(prev => !prev)}
            />
            {!sidebarOpen && (
              <button
                className="fixed top-4 left-2 z-50 bg-slate-900 text-white rounded-full p-2 shadow hover:bg-slate-800 transition"
                onClick={() => setSidebarOpen(true)}
                title="Show sidebar"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            )}
          <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
            <div ref={chatContainerRef} className="flex-1 overflow-y-auto py-6 space-y-6">
              <AnimatePresence mode="popLayout">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} onCopy={handleCopyMessage} />
                ))}
                {isTyping && <TypingIndicator />}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            <InputBar
              value={inputValue}
              onChange={setInputValue}
              onSend={() => handleSendMessage()}
              isLoading={isLoading}
              disabled={isTyping}
              onNewChat={handleCreateChat}
              selectedModel={sessionModel}
              availableModels={models}
              onModelChange={handleInputBarModelChange}
            />
            </div>
          </div>

          {/* Configuration Dialog */}
          <Dialog open={showConfig} onOpenChange={setShowConfig}>
            <DialogContent className="sm:max-w-[650px]">
              <DialogHeader>
                <DialogTitle>HR Assistant Configuration</DialogTitle>
                <DialogDescription>
                  Customize your AI assistant's behavior and preferences.
                </DialogDescription>
              </DialogHeader>
              
              <div className="grid gap-6 py-4">
                <div className="space-y-2">
                  <Label htmlFor="model-select">AI Model Selection</Label>
                  <input
                    type="text"
                    placeholder="Search models..."
                    className="w-full px-3 py-2 mb-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={modelSearch}
                    onChange={e => setModelSearch(e.target.value)}
                    disabled={modelsLoading}
                  />
                  <Select
                    value={selectedModel}
                    onValueChange={setSelectedModel}
                    disabled={modelsLoading}
                  >
                    <SelectTrigger id="model-select" tabIndex={0} aria-label="AI Model Selection">
                      <SelectValue placeholder={models.find(m => m.id === selectedModel)?.label || 'Select AI model'} />
                    </SelectTrigger>
                    <SelectContent style={{ maxHeight: 240, overflowY: 'auto' }}>
                      {models
                        .filter(model =>
                          (model.label || model.id)
                            .toLowerCase()
                            .includes(modelSearch.toLowerCase())
                        )
                        .map((model) => (
                          <SelectItem key={model.id} value={model.id}>
                            {model.label || model.id} {model.badge ? `(${model.badge})` : ''}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                  <div className="text-xs text-muted-foreground mt-1">Use ↑ ↓ to scroll, type to search, Enter to select, Esc to close.</div>
                </div>

                <div className="space-y-2">
                  <Label>System Prompt</Label>
                  <Textarea
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    className="min-h-[120px]"
                    placeholder="Enter custom instructions for the AI..."
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div className="flex items-center gap-3">
                    <Switch 
                      id="sound-toggle" 
                      checked={soundEnabled} 
                      onCheckedChange={setSoundEnabled} 
                    />
                    <Label htmlFor="sound-toggle">Notification Sounds</Label>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={() => setCustomPrompt(DEFAULT_PROMPT)}
                  >
                    Reset Defaults
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          {/* Clear Chat Confirmation Modal */}
          <Dialog open={showClearModal} onOpenChange={setShowClearModal}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Clear Conversation</DialogTitle>
                <DialogDescription>
                  Are you sure you want to clear the entire conversation history? This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <div>Are you sure you want to clear the entire conversation history? This action cannot be undone.</div>
              <DialogFooter>
                <Button variant="outline" onClick={cancelClearChat}>Cancel</Button>
                <Button variant="destructive" onClick={confirmClearChat}>Clear Chat</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Dialog open={showNewChatModal} onOpenChange={setShowNewChatModal}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>New Chat</DialogTitle>
                <DialogDescription>
                  Create a new chat session with a name and role.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <Label>Chat Name</Label>
                <Textarea value={newChatName} onChange={e => setNewChatName(e.target.value)} placeholder="e.g. HR Policy Discussion" />
                <Label>Role (optional)</Label>
                <Textarea value={newChatRole} onChange={e => setNewChatRole(e.target.value)} placeholder="e.g. HR, Admin, Manager" />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNewChatModal(false)}>Cancel</Button>
                <Button onClick={handleCreateChat} disabled={!newChatName.trim()}>Create</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete Chat</DialogTitle>
                <DialogDescription>
                  Are you sure you want to delete this chat session? This cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <div>Are you sure you want to delete this chat session? This cannot be undone.</div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowDeleteModal(false)}>Cancel</Button>
                <Button variant="destructive" onClick={confirmDeleteSession}>Delete</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </TooltipProvider>
    </ErrorBoundary>
  );
};

export default HRAssistantPro;