import React, { useEffect, useState, useRef } from 'react';
import { Send, Bot, User, Sparkles, MessageCircle, Loader2, Copy, Settings, Eraser } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';
import { Textarea } from '@/components/ui/textarea';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';

interface Message {
  id: string;
  type: 'user' | 'bot' | 'error';
  content: string;
  timestamp: Date;
}

const OPENROUTER_MODELS = [
  { label: 'GPT-3.5 Turbo', value: 'openai/gpt-3.5-turbo' },
  { label: 'GPT-4 Turbo', value: 'openai/gpt-4-turbo' },
  { label: 'Mixtral 8x7B', value: 'mistralai/mixtral-8x7b' },
];

const DEFAULT_PROMPT = `
You are a helpful HR assistant. Always answer in clear, well-structured markdown.
- Use **bold** for key points.
- Use numbered or bulleted lists for steps or options.
- Use headings (##) for sections.
- Keep answers concise, actionable, and visually organized.
- If the user asks for examples, provide them in markdown code blocks or lists.
- Never include raw HTML, only markdown.
`;

const ChatPage: React.FC = () => {
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = localStorage.getItem('chatMessages');
    return saved ? JSON.parse(saved) : [
      {
        id: '1',
        type: 'bot',
        content: "Hello! I'm your AI recruitment assistant. I can help you analyze candidates, suggest interview questions, and provide insights about your hiring process. What would you like to know?",
        timestamp: new Date()
      }
    ];
  });
  const [inputValue, setInputValue] = useState('');
  const [selectedModel, setSelectedModel] = useState(() => localStorage.getItem('aiModel') || OPENROUTER_MODELS[0].value);
  const [models, setModels] = useState<{ label: string, value: string }[]>(OPENROUTER_MODELS);
  const [isLoading, setIsLoading] = useState(false);
  const [customPrompt, setCustomPrompt] = useState(() => localStorage.getItem('aiPrompt') || DEFAULT_PROMPT);
  const [showConfig, setShowConfig] = useState(false);

  // Persist model and prompt
  useEffect(() => {
    localStorage.setItem('aiModel', selectedModel);
  }, [selectedModel]);
  useEffect(() => {
    localStorage.setItem('aiPrompt', customPrompt);
  }, [customPrompt]);

  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/openrouter-models/');
        if (res.data && Array.isArray(res.data.data)) {
          setModels(res.data.data.map((m: any) => ({
            label: m.id,
            value: m.id
          })));
        }
      } catch (error) {
        toast({
          title: 'Error fetching models',
          description: 'Could not load available models. Using default options.',
          variant: 'destructive',
        });
      }
    };
    fetchModels();
  }, [toast]);

  const quickActions = [
    "Analyze candidate skills for React Developer position",
    "Suggest interview questions for Product Manager role",
    "Compare candidates for UX Designer position",
    "Help me draft a job description",
    "What are the trending skills in tech?"
  ];

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('authToken');
      console.log('Sending token:', token); // Debug: log token
      if (!token) {
        throw new Error('No auth token found, please log in again.');
      }
      
      const res = await axios.post(
        'http://localhost:8000/api/chat/',
        {
          message: inputValue,
          model: selectedModel,
          prompt: customPrompt
        },
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString() + Math.random().toString(36).substring(2, 8),
          type: 'bot',
          content: res.data.response,
          timestamp: new Date()
        }
      ]);
    } catch (error: any) {
      let errorMsg = 'I encountered an error. Please try again.';
      if (error?.response?.status === 401) {
        errorMsg = 'Your session has expired. Please log in again.';
      } else if (error?.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (error?.message) {
        errorMsg = error.message;
      }
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString() + Math.random().toString(36).substring(2, 8),
          type: 'error',
          content: errorMsg,
          timestamp: new Date()
        }
      ]);
      if (error?.response?.status === 401) {
        setTimeout(() => window.location.href = '/login', 2000);
      }
    } finally {
      setIsLoading(false);
    }
};

  const handleQuickAction = (action: string) => {
    setInputValue(action);
    setTimeout(() => handleSendMessage(), 0);
  };

  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied to clipboard!',
      description: 'The message has been copied.',
    });
  };

  const promptSuggestions = [
    "Summarize the top 3 qualities of a great team leader.",
    "List 5 best practices for remote onboarding.",
    "What are the key steps in a structured interview process?",
    "How can we improve diversity in hiring?",
    "Give an example of a strong job description for a Data Scientist."
  ];

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history? This cannot be undone.')) {
      localStorage.removeItem('chatMessages');
      setMessages([
        {
          id: '1',
          type: 'bot',
          content: "Hello! I'm your AI recruitment assistant. I can help you analyze candidates, suggest interview questions, and provide insights about your hiring process. What would you like to know?",
          timestamp: new Date()
        }
      ]);
      toast({ title: 'Chat history cleared!' });
    }
  };

  return (
    <div className="flex flex-col h-[100dvh] min-h-0 w-full max-w-4xl mx-auto bg-background dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b bg-white/80 backdrop-blur sticky top-0 z-10">
        <div className="h-10 w-10 rounded-full bg-gradient-primary flex items-center justify-center shadow">
          <Bot className="h-5 w-5 text-primary-foreground" />
        </div>
        <div className="flex-1">
          <h1 className="text-lg sm:text-xl font-bold text-foreground tracking-tight">AI HR Assistant</h1>
          <p className="text-xs text-muted-foreground">Smart, structured answers for all your HR needs</p>
        </div>
        <Button variant="ghost" size="icon" className="ml-auto" onClick={handleClearChat} title="Clear chat history">
          <Eraser className="h-5 w-5 text-muted-foreground" />
        </Button>
        <Dialog open={showConfig} onOpenChange={setShowConfig}>
          <DialogTrigger asChild>
            <Button variant="ghost" size="icon" className="ml-auto">
              <Settings className="h-5 w-5 text-muted-foreground" />
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg w-full">
            <DialogHeader>
              <DialogTitle>AI Configuration</DialogTitle>
              <DialogDescription>
                Change the AI model and system prompt for your chat experience.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 mt-2">
              <div>
                <label className="text-sm font-medium">AI Model</label>
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select AI model" />
                  </SelectTrigger>
                  <SelectContent>
                    {models.map((model) => (
                      <SelectItem key={model.value} value={model.value}>
                        {model.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">System Prompt</label>
                <Textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Set the AI's personality and instructions..."
                  className="min-h-[100px]"
                />
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Chat Area */}
      <div className="flex-1 min-h-0 overflow-y-auto px-2 sm:px-4 py-4 sm:py-6 space-y-4 bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-900 dark:text-gray-100">
        {messages.map((message, idx) => (
          <div
            key={message.id}
            className={`flex items-end gap-2 animate-fade-in-up ${message.type === 'user' ? 'flex-row-reverse' : ''}`}
            style={{ animationDelay: `${idx * 60}ms` }}
          >
            {/* Avatar */}
            <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${message.type === 'user' ? 'bg-blue-400 dark:bg-primary/80' : 'bg-gradient-primary'}`}>
              {message.type === 'user' ? (
                <User className="h-4 w-4 text-white" />
              ) : (
                <Bot className="h-4 w-4 text-primary-foreground" />
              )}
            </div>
            {/* Bubble */}
            <div className={`relative px-4 py-3 rounded-2xl shadow-md max-w-[85%] w-fit ${
              message.type === 'user'
                ? 'bg-blue-500 text-white dark:bg-primary/80 dark:text-white'
                : message.type === 'error'
                ? 'bg-destructive/10 text-destructive border border-destructive/20'
                : 'bg-white text-foreground dark:bg-gray-800 dark:text-gray-100 rounded-bl-md'
            }`}>
              <div className="prose prose-sm dark:prose-invert">
                <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                  {message.content}
                </ReactMarkdown>
              </div>
              {message.type === 'bot' && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-1 right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => handleCopyToClipboard(message.content)}
                >
                  <Copy className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-end gap-2 animate-pulse">
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-primary flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="px-4 py-3 rounded-2xl bg-white text-muted-foreground dark:bg-gray-800 dark:text-gray-100 shadow-md max-w-[85%] w-fit">
              Typing...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Sticky Input Bar */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur px-2 sm:px-4 py-2 sm:py-3 border-t border-gray-200 dark:border-gray-800 sticky bottom-0 z-10">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 min-w-0"
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
            disabled={isLoading}
          />
          <Button 
            onClick={handleSendMessage}
            className="bg-gradient-primary hover:shadow-glow transition-all duration-300"
            disabled={!inputValue.trim() || isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        {/* Removed prompt suggestion buttons */}
      </div>
    </div>
  );
};

export default ChatPage;