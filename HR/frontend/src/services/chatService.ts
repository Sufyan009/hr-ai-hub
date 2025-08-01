import axios from 'axios';
import api from './api';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export const fetchModels = async () => {
  const response = await axios.get('http://127.0.0.1:8001/models');
  return response.data.models || response.data;
};

// Accepts either (message, model, prompt) or ({ model, messages, prompt, extra_headers, extra_body })
export const sendMessage = async (
  messageOrPayload: string | {
    model: string,
    messages: any[],
    prompt?: string,
    session_id?: string,
    extra_headers?: any,
    extra_body?: any
  },
  model?: string,
  prompt?: string,
  axiosConfig?: any
) => {
  let payload;
  if (typeof messageOrPayload === 'string') {
    // Backward compatible: (message, model, prompt)
    payload = {
      message: messageOrPayload,
      model,
      prompt,
    };
  } else {
    // Advanced: full payload
    payload = { ...messageOrPayload };
  }
  // Always include authToken from localStorage if present
  const token = localStorage.getItem('authToken');
  if (token) {
    payload.authToken = token;
  }
  // Debug: Log the payload being sent
  console.log('[DEBUG] Frontend sending payload:', payload);
  const response = await axios.post('http://127.0.0.1:8001/chat', payload, axiosConfig);
  return response.data;
};

export const getChatSessions = async () => {
  const response = await api.get('/chatsessions/');
  return response.data;
};

export const createChatSession = async (data: { session_name?: string; role?: string }) => {
  const response = await api.post('/chatsessions/', data);
  return response.data;
};

export const deleteChatSession = async (id: number) => {
  const response = await api.delete(`/chatsessions/${id}/`);
  return response.data;
};

export const updateChatSession = async (id: number, data: { session_name?: string; role?: string; model?: string }) => {
  const response = await api.patch(`/chatsessions/${id}/`, data);
  return response.data;
};

export const getChatMessages = async (sessionId: number) => {
  const response = await api.get(`/chatmessages/?session=${sessionId}`);
  return response.data;
};

export const createChatMessage = async (data: { session: number; role: string; content: string }) => {
  const response = await api.post('/chatmessages/', data);
  return response.data;
};

export const deleteChatMessage = async (id: number) => {
  const response = await api.delete(`/chatmessages/${id}/`);
  return response.data;
};

export async function uploadCandidatesFile(file: File, sessionId: string, authToken?: string, duplicateMode: string = 'skip', columnMapping?: Record<string, string>) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);
  formData.append('duplicate_mode', duplicateMode);
  if (columnMapping) {
    formData.append('column_mapping', JSON.stringify(columnMapping));
  }
  const headers: Record<string, string> = {};
  if (authToken) headers['Authorization'] = `Token ${authToken}`;
  const response = await axios.post(`${API_URL}/chat/upload`, formData, { headers });
  return response.data;
}

export async function uploadSingleFile(file: File, sessionId: string, authToken?: string) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);
  if (authToken) {
    formData.append('auth_token', authToken);
  }
  
  const headers: Record<string, string> = {};
  if (authToken) headers['Authorization'] = `Token ${authToken}`;
  
  const response = await axios.post(`${API_URL}/chat/upload/file`, formData, { headers });
  return response.data;
}

export async function processUploadedFile(sessionId: string, fileName: string, authToken?: string) {
  const headers: Record<string, string> = {};
  if (authToken) headers['Authorization'] = `Token ${authToken}`;
  
  const response = await axios.post(`${API_URL}/chat/process/file`, {
    session_id: sessionId,
    file_name: fileName,
    auth_token: authToken
  }, { headers });
  return response.data;
}

export async function downloadCandidateTemplate() {
  const response = await axios.get(`${API_URL}/chat/template/candidates`, {
    responseType: 'blob'
  });
  
  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'candidates_template.csv');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
  
  return { success: true, message: 'Template downloaded successfully' };
} 