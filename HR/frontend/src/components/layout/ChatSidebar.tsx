import React from 'react';
import { Plus, MessageSquare, MoreVertical, Pencil, Trash2, Check, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { motion, AnimatePresence } from 'framer-motion';

// ChatSidebar Component
const ChatSidebar: React.FC<{
  sessions: any[];
  activeSessionId: number | null;
  onSelect: (id: number) => void;
  onRename: (id: number, currentName: string) => void;
  onDelete: (id: number) => void;
  editingSessionId: number | null;
  editingSessionName: string;
  setEditingSessionName: (name: string) => void;
  onSaveRename: (id: number) => void;
  onCancelRename: () => void;
  menuOpenId: number | null;
  setMenuOpenId: (id: number | null) => void;
  onNewChat: () => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}> = ({
  sessions,
  activeSessionId,
  onSelect,
  onRename,
  onDelete,
  editingSessionId,
  editingSessionName,
  setEditingSessionName,
  onSaveRename,
  onCancelRename,
  menuOpenId,
  setMenuOpenId,
  onNewChat,
  collapsed,
  onToggleCollapse,
}) => (
  <TooltipProvider>
    <motion.div
      initial={{ x: -288 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 flex flex-col h-full ${collapsed ? 'w-16' : 'w-72'}`}
    >
      {/* Header */}
      <div className={`flex items-center justify-between ${collapsed ? 'px-3' : 'px-4'} py-4 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800`}>
        {!collapsed && (
          <h2 className="text-base font-semibold text-slate-900 dark:text-slate-100 tracking-normal">
            Conversations
          </h2>
        )}
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-700"
                onClick={onNewChat}
                aria-label="Start new chat"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            {collapsed && <TooltipContent side="right">New Chat</TooltipContent>}
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-700"
                onClick={onToggleCollapse}
                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              >
                {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">{collapsed ? 'Expand sidebar' : 'Collapse sidebar'}</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto">
        {sessions.length === 0 ? (
          <div className={`p-6 text-sm text-slate-500 dark:text-slate-400 text-center ${collapsed ? 'hidden' : ''}`}>
            No conversations yet
          </div>
        ) : (
          <div className="py-2">
            <AnimatePresence>
              {sessions.map((session) => (
                <motion.div
                  key={session.id}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.15 }}
                  className={`group flex items-center justify-between ${collapsed ? 'px-3 py-3 mx-2' : 'px-4 py-3 mx-2'} rounded-md cursor-pointer transition-colors duration-150 ${
                    activeSessionId === session.id
                      ? 'bg-slate-100 dark:bg-slate-800 border-l-2 border-blue-600'
                      : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
                  }`}
                  onClick={() => onSelect(session.id)}
                >
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex items-center flex-1 min-w-0 gap-3">
                        <MessageSquare className={`h-4 w-4 flex-shrink-0 ${activeSessionId === session.id ? 'text-blue-600' : 'text-slate-400 dark:text-slate-500'}`} />
                        {!collapsed && (
                          editingSessionId === session.id ? (
                            <div className="flex items-center gap-2 flex-1">
                              <input
                                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded px-2 py-1 text-sm text-slate-900 dark:text-slate-100 w-full focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                                value={editingSessionName}
                                onChange={(e) => setEditingSessionName(e.target.value)}
                                onClick={(e) => e.stopPropagation()}
                                autoFocus
                                placeholder="Conversation name"
                                aria-label="Edit conversation name"
                              />
                              <button
                                className="text-green-600 hover:text-green-700 dark:text-green-500 dark:hover:text-green-400 p-1"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onSaveRename(session.id);
                                }}
                                aria-label="Save name"
                              >
                                <Check className="h-4 w-4" />
                              </button>
                              <button
                                className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 p-1"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onCancelRename();
                                }}
                                aria-label="Cancel rename"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          ) : (
                            <div className="flex flex-col flex-1 min-w-0">
                              <span className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                                {session.session_name || 'New Conversation'}
                              </span>
                              <span className="truncate text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                {session.latest_message?.slice(0, 35) || 'No messages'}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </TooltipTrigger>
                    {collapsed && (
                      <TooltipContent side="right">
                        <div className="font-medium">{session.session_name || 'New Conversation'}</div>
                        <div className="text-xs text-slate-400 mt-1">{session.latest_message?.slice(0, 30) || 'No messages'}</div>
                      </TooltipContent>
                    )}
                  </Tooltip>
                  
                  {/* Menu - only visible on hover and when not collapsed */}
                  {!collapsed && (
                    <DropdownMenu open={menuOpenId === session.id} onOpenChange={(open) => setMenuOpenId(open ? session.id : null)}>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                          onClick={(e) => e.stopPropagation()}
                          aria-label="Conversation options"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-48 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700">
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onRename(session.id, session.session_name);
                            setMenuOpenId(null);
                          }}
                          className="cursor-pointer"
                        >
                          <Pencil className="h-4 w-4 mr-2" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onDelete(session.id);
                            setMenuOpenId(null);
                          }}
                          className="cursor-pointer text-red-600 dark:text-red-400 focus:text-red-700 dark:focus:text-red-300"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Footer with New Chat Button */}
      {!collapsed && (
        <div className="px-4 py-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
          <Button
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-md transition-colors duration-150"
            onClick={onNewChat}
            aria-label="Create new conversation"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </div>
      )}
    </motion.div>
  </TooltipProvider>
);

export default ChatSidebar;