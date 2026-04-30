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

export default api;
