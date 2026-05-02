import { api } from './api';

// Types for the OS v2 API
export interface MissionLaunchRequest {
  mission_type: 'scout' | 'ammo_generation' | 'bounty_match';
  payload: any;
  agent_preference?: string;
}

export interface MissionLaunchResponse {
  trace_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  predicted_win_probability?: number;
  predicted_cost?: number;
  estimated_rank_change?: number;
}

export interface AgentInfo {
  name: string;
  success_rate: number;
  speed: number;
  stake: number;
  score: number;
}

export interface CostSummary {
  total_spent: number;
  budget_remaining: number;
  daily_limit: number;
  per_mission_type: {
    scout: number;
    ammo_generation: number;
    bounty_match: number;
  };
}

export interface ActiveMission {
  trace_id: string;
  mission_type: string;
  status: 'running' | 'paused' | 'completed' | 'failed';
  started_at: string;
  progress_percent: number;
}

export interface ReplayData {
  trace_id: string;
  mission_type: string;
  steps: ReplayStep[];
  total_cost: number;
  final_rank_change: number;
  created_at: string;
}

export interface ReplayStep {
  node_id: string;
  node_type: string;
  timestamp: string;
  result: any;
  cost: number;
  rank_impact: number;
}

export interface MissionEvent {
  type: 'node_start' | 'node_complete' | 'cost_update' | 'rank_update' | 'mission_complete';
  data: any;
  timestamp: string;
}

// New interfaces for OS v2.5 wireframe
export interface Offer {
  id: string;
  location: string;
  reward: number;
  distance: number; // in km
  expiry: string; // ISO timestamp
  highDemand: boolean;
  claimCount: number;
  lat: number;
  lon: number;
  address?: string;
  description?: string;
}

export interface MissionHistory {
  id: string;
  location: string;
  reward: number;
  completed_at: string;
  status: 'completed' | 'failed' | 'pending';
  trace_id?: string;
}

export interface Earnings {
  total: number;
  pending: number;
  today: number;
  week: number;
}

export interface UserProfile {
  rank: string;
  streak: number;
  total_earned: number;
  city_percentile: number;
  tier: string;
}

/**
 * Launch a new mission
 */
export async function launchMission(
  type: MissionLaunchRequest['mission_type'],
  payload: any,
  agentName?: string
): Promise<MissionLaunchResponse> {
  const response = await api.post('/mission/v2', {
    mission_type: type,
    payload,
    agent_preference: agentName,
  });
  return response.data;
}

/**
 * Get mission status
 */
export async function getMissionStatus(trace_id: string): Promise<MissionLaunchResponse> {
  const response = await api.get(`/mission/${trace_id}`);
  return response.data;
}

/**
 * Pause a running mission
 */
export async function pauseMission(trace_id: string): Promise<{ status: string }> {
  const response = await api.post(`/mission/${trace_id}/pause`);
  return response.data;
}

/**
 * Resume a paused mission
 */
export async function resumeMission(trace_id: string): Promise<{ status: string }> {
  const response = await api.post(`/mission/${trace_id}/resume`);
  return response.data;
}

/**
 * Get agent market information
 */
export async function getAgentMarket(): Promise<AgentInfo[]> {
  const response = await api.get('/market/agents');
  return response.data;
}

/**
 * Stake on an agent
 */
export async function stakeAgent(agentName: string, amount: number): Promise<{ status: string }> {
  const response = await api.post('/market/stake', {
    agent_name: agentName,
    amount,
  });
  return response.data;
}

/**
 * Get cost summary for current user
 */
export async function getCostSummary(): Promise<CostSummary> {
  const response = await api.get('/cost/summary');
  return response.data;
}

/**
 * Get active missions for current user
 */
export async function getActiveMissions(): Promise<ActiveMission[]> {
  const response = await api.get('/missions/active');
  return response.data;
}

/**
 * Get replay data for a mission
 */
export async function getReplay(trace_id: string): Promise<ReplayData> {
  const response = await api.get(`/replay/${trace_id}`);
  return response.data;
}

/**
 * Connect to mission WebSocket stream
 */
export function connectMissionStream(trace_id: string, onMessage: (event: MissionEvent) => void): WebSocket {
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/stream/${trace_id}`;
  const ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data as MissionEvent);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };

  return ws;
}

/**
 * Connect to telemetry WebSocket (global system events)
 */
export function connectTelemetry(onMessage: (event: any) => void): WebSocket {
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/telemetry`;
  const ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Failed to parse telemetry message:', error);
    }
  };

  return ws;
}

/**
 * Get mission types available
 */
export async function getMissionTypes(): Promise<Array<{ id: string; name: string; description: string }>> {
  // This endpoint might not exist yet, return mock data
  return [
    { id: 'scout', name: 'Scout', description: 'Explore and gather intelligence' },
    { id: 'ammo_generation', name: 'Ammo Generation', description: 'Generate content assets' },
    { id: 'bounty_match', name: 'Bounty Match', description: 'Match with high-value targets' },
  ];
}

/**
 * Get predicted outcome for a mission
 */
export async function getPredictedOutcome(
  missionType: string,
  agentName?: string
): Promise<{
  win_probability: number;
  expected_cost: number;
  estimated_rank_change: number;
}> {
  // Mock prediction - in real app, call a prediction endpoint
  return {
    win_probability: 0.75,
    expected_cost: 0.42,
    estimated_rank_change: 2,
  };
}

// New functions for OS v2.5 wireframe

/**
 * Get nearby offers based on user location
 */
export async function getNearbyOffers(lat: number, lon: number): Promise<Offer[]> {
  // Mock data - in real app, call /offers/nearby?lat=...&lon=...
  return [
    {
      id: 'offer1',
      location: 'Café Central',
      reward: 15,
      distance: 0.8,
      expiry: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours
      highDemand: true,
      claimCount: 3,
      lat: 36.8065,
      lon: 10.1815,
      address: '123 Main Street, Tunis',
      description: 'Create a short video showcasing the café atmosphere'
    },
    {
      id: 'offer2',
      location: 'Tech Hub Coworking',
      reward: 25,
      distance: 1.2,
      expiry: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), // 3 hours
      highDemand: false,
      claimCount: 0,
      lat: 36.7989,
      lon: 10.1765,
      address: '456 Innovation Ave, Tunis',
      description: 'Capture the workspace environment'
    },
    {
      id: 'offer3',
      location: 'Urban Park',
      reward: 18,
      distance: 2.5,
      expiry: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(), // 5 hours
      highDemand: true,
      claimCount: 5,
      lat: 36.8123,
      lon: 10.1654,
      address: '789 Green Blvd, Tunis',
      description: 'Showcase weekend activities'
    }
  ];
}

/**
 * Claim an offer to start a mission
 */
export async function claimOffer(offerId: string): Promise<{ trace_id: string; status: string }> {
  const response = await api.post(`/offers/${offerId}/claim`);
  return response.data;
}

/**
 * Get offer details
 */
export async function getOfferDetails(offerId: string): Promise<Offer> {
  const response = await api.get(`/offers/${offerId}`);
  return response.data;
}

/**
 * Upload video for a mission
 */
export async function uploadVideo(traceId: string, videoFile: File): Promise<{ status: string }> {
  const formData = new FormData();
  formData.append('video', videoFile);

  const response = await api.post(`/mission/${traceId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

/**
 * Fetch mission history
 */
export async function fetchMissionHistory(): Promise<MissionHistory[]> {
  const response = await api.get('/missions/history');
  return response.data;
}

/**
 * Fetch earnings summary
 */
export async function fetchEarnings(): Promise<Earnings> {
  const response = await api.get('/earnings');
  return response.data;
}

/**
 * Get user profile
 */
export async function getUserProfile(): Promise<UserProfile> {
  const response = await api.get('/users/me/profile');
  return response.data;
}