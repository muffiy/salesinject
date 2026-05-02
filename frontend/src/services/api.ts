import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authenticateWithTelegram = async (initData: string) => {
  const response = await api.post('/auth/telegram', { initData });
  return response.data;
};

export const getPaperclips = async (itemType?: string) => {
  const url = itemType ? `/scout/paperclips?item_type=${itemType}` : '/scout/paperclips';
  const response = await api.get(url);
  return response.data;
};

export const getLatestScoutReport = async () => {
  const response = await api.get('/scout/latest');
  return response.data;
};

export const getOffers = async () => {
  const response = await api.get('/offers/');
  return response.data;
};

export const runScoutMission = async (niche: string, location: string) => {
  const response = await api.post('/scout/mission', { niche, location });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

export const getAgents = async () => {
  const response = await api.get('/agents/');
  return response.data;
};

export const createAgent = async (data: { name: string; niche: string; agent_type?: string }) => {
  const response = await api.post('/agents/', data);
  return response.data;
};

export const deleteAgent = async (agentId: string) => {
  const response = await api.delete(`/agents/${agentId}`);
  return response.data;
};

export const runAgentTask = async (data: any) => {
  const response = await api.post('/agent/task', data);
  return response.data;
};

export const pollUntilDone = async (taskId: string, intervalMs = 2000): Promise<any> => {
  return new Promise((resolve, reject) => {
    const timer = setInterval(async () => {
      try {
        const response = await api.get(`/agent/task/${taskId}/status`);
        if (response.data.state === 'SUCCESS') {
          clearInterval(timer);
          resolve(response.data);
        } else if (response.data.state === 'FAILURE') {
          clearInterval(timer);
          reject(new Error(response.data.error || 'Task failed'));
        }
      } catch (err) {
        clearInterval(timer);
        reject(err);
      }
    }, intervalMs);
  });
};

export const getPayments = async () => {
  const response = await api.get('/users/me/payments');
  return response.data;
};

export const getTasks = async () => {
  const response = await api.get('/tasks/');
  return response.data;
};

export const claimTask = async (taskId: string) => {
  const response = await api.post(`/tasks/${taskId}/claim`);
  return response.data;
};

export const getMySubmissions = async () => {
  const response = await api.get('/tasks/me/submissions');
  return response.data;
};

export default api;
