import api from './api';

export const fetchModels = async () => {
  const response = await api.get('/openrouter-models/');
  // OpenRouter returns { data: [...] }, so return .data if present
  return response.data?.data || response.data;
};

// Accepts either (message, model, prompt) or ({ model, messages, prompt, extra_headers, extra_body })
export const sendMessage = async (
  messageOrPayload: string | {
    model: string,
    messages: any[],
    prompt?: string,
    extra_headers?: any,
    extra_body?: any
  },
  model?: string,
  prompt?: string
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
  const response = await api.post('/chat/', payload);
  return response.data;
}; 