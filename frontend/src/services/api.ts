import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
});

// Token is now managed by AuthContext (in-memory ref).
// AuthContext sets api.defaults.headers.common['Authorization'] directly.
// No localStorage — token is gone on page reload, triggering re-auth.

/** Called on first load / after token expires. Returns the raw access_token. */
export async function authenticate(initData: string): Promise<string> {
  const response = await api.post('/auth/telegram', { init_data: initData });
  return response.data.access_token;
}

/** Silently renew the JWT before it expires (call every ~28 min). */
export async function refreshToken(): Promise<string> {
  const response = await api.post('/auth/refresh');
  return response.data.access_token;
}


export async function getAgents() {
  const response = await api.get('/agents');
  return response.data;
}

export async function createAgent(name: string, niche: string) {
  const response = await api.post('/agents', { name, niche });
  return response.data;
}

export async function deleteAgent(agentId: string) {
  await api.delete(`/agents/${agentId}`);
}

export async function runAgentTask(agentId: string, niche: string, productName: string, actionType: string = "ad_gen") {
  const response = await api.post('/agent/task', {
    agent_id: agentId || null,
    niche,
    product_name: productName,
    action_type: actionType,
  });
  // Returns { status: 'accepted', task_id: '...' }
  return response.data;
}

export async function getLatestScout() {
  const response = await api.get('/scout/latest');
  return response.data;
}

export async function getTaskStatus(taskId: string): Promise<{
  task_id: string;
  state: 'PENDING' | 'STARTED' | 'RETRY' | 'FAILURE' | 'SUCCESS';
  result?: { ad_idea: Record<string, string> };
  error?: string;
}> {
  const response = await api.get(`/agent/task/${taskId}/status`);
  return response.data;
}

/**
 * Poll until the Celery task reaches a terminal state.
 * Resolves with the result or rejects with the error message.
 */
export async function pollUntilDone(
  taskId: string,
  intervalMs = 2000,
  timeoutMs = 120_000,
): Promise<{ ad_idea: Record<string, string> }> {
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolve, reject) => {
    const tick = async () => {
      if (Date.now() > deadline) { reject(new Error('Task timed out')); return; }
      try {
        const status = await getTaskStatus(taskId);
        if (status.state === 'SUCCESS') { resolve(status.result!); return; }
        if (status.state === 'FAILURE') { reject(new Error(status.error || 'Task failed')); return; }
        setTimeout(tick, intervalMs);
      } catch (e) { reject(e); }
    };
    setTimeout(tick, intervalMs);
  });
}

export async function getTasks() {
  const response = await api.get('/tasks');
  return response.data;
}

export async function claimTask(taskId: string) {
  const response = await api.post(`/tasks/${taskId}/claim`);
  return response.data;
}

export async function getMySubmissions() {
  const response = await api.get('/tasks/me/submissions');
  return response.data;
}

export async function getMe() {
  const response = await api.get('/users/me');
  return response.data;
}

export async function getPayments() {
  const response = await api.get('/users/me/payments');
  return response.data;
}

export async function getPaperclips() {
  const response = await api.get('/scout/paperclips');
  return response.data;
}
