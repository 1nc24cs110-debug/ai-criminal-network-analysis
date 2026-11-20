import {
  User, Case, Entity, Relationship, EvidenceDocument, EvidenceReference,
  EntityMatchSuggestion, NetworkPatternAlert, AuditLog, GraphData,
  CentralityAnalytics
} from './types';

const API_BASE = '/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('intel_auth_token');
}

export function setAuthToken(token: string): void {
  localStorage.setItem('intel_auth_token', token);
}

export function clearAuthToken(): void {
  localStorage.removeItem('intel_auth_token');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearAuthToken();
    // Only redirect if not already on login
    if (!window.location.pathname.includes('login')) {
      window.dispatchEvent(new CustomEvent('auth-expired'));
    }
    throw new Error('Session expired or unauthorized');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: async (username: string, password: string) => {
    const data = await request<{ access_token: string; token_type: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    setAuthToken(data.access_token);
    return data;
  },
  getMe: () => request<User>('/auth/me'),
  listUsers: () => request<User[]>('/auth/users'),

  // Dashboard
  getDashboardStats: () => request<any>('/dashboard/stats'),
  getDashboardCharts: () => request<any>('/dashboard/charts'),
  getRecentActivity: () => request<any>('/dashboard/recent-activity'),

  // Cases
  listCases: () => request<Case[]>('/cases'),
  getCase: (id: number) => request<Case>(`/cases/${id}`),
  createCase: (data: Partial<Case>) => request<Case>('/cases', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  updateCase: (id: number, data: Partial<Case>) => request<Case>(`/cases/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  // Entities
  listEntities: (params: { case_id?: number; entity_type?: string; risk_level?: string; verification_status?: string; search?: string } = {}) => {
    const searchParams = new URLSearchParams();
    if (params.case_id) searchParams.set('case_id', String(params.case_id));
    if (params.entity_type) searchParams.set('entity_type', params.entity_type);
    if (params.risk_level) searchParams.set('risk_level', params.risk_level);
    if (params.verification_status) searchParams.set('verification_status', params.verification_status);
    if (params.search) searchParams.set('search', params.search);
    return request<Entity[]>(`/entities?${searchParams.toString()}`);
  },
  getEntity: (id: number) => request<Entity>(`/entities/${id}`),
  createEntity: (data: Partial<Entity>) => request<Entity>('/entities', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  updateEntity: (id: number, data: Partial<Entity>) => request<Entity>(`/entities/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  // Relationships
  listRelationships: (params: { case_id?: number; verification_status?: string } = {}) => {
    const searchParams = new URLSearchParams();
    if (params.case_id) searchParams.set('case_id', String(params.case_id));
    if (params.verification_status) searchParams.set('verification_status', params.verification_status);
    return request<Relationship[]>(`/relationships?${searchParams.toString()}`);
  },
  createRelationship: (data: any) => request<Relationship>('/relationships', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  verifyRelationship: (id: number, verification_status: string, notes?: string) => request<Relationship>(`/relationships/${id}/verify`, {
    method: 'PUT',
    body: JSON.stringify({ verification_status, notes }),
  }),

  // Evidence Center
  listEvidenceDocuments: (case_id?: number) => {
    const q = case_id ? `?case_id=${case_id}` : '';
    return request<EvidenceDocument[]>(`/evidence/documents${q}`);
  },
  getEvidenceDocument: (id: number) => request<EvidenceDocument>(`/evidence/documents/${id}`),
  uploadEvidenceDocument: (formData: FormData) => request<any>('/evidence/upload', {
    method: 'POST',
    body: formData,
  }),
  extractFromText: (text: string, document_id?: number) => request<any>('/evidence/extract', {
    method: 'POST',
    body: JSON.stringify({ text, document_id }),
  }),
  commitExtraction: (payload: any) => request<any>('/evidence/commit-extraction', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // Entity Matching
  listMatchSuggestions: () => request<EntityMatchSuggestion[]>('/matching/suggestions'),
  runEntityMatching: () => request<any>('/matching/run', { method: 'POST' }),
  reviewMatchSuggestion: (id: number, status: string, review_notes?: string) => request<any>(`/matching/review/${id}`, {
    method: 'POST',
    body: JSON.stringify({ status, review_notes }),
  }),

  // Graph & Analytics
  getGraphData: (params: { case_id?: number; include_unverified?: boolean; min_confidence?: number; entity_types?: string } = {}) => {
    const searchParams = new URLSearchParams();
    if (params.case_id) searchParams.set('case_id', String(params.case_id));
    if (params.include_unverified !== undefined) searchParams.set('include_unverified', String(params.include_unverified));
    if (params.min_confidence !== undefined) searchParams.set('min_confidence', String(params.min_confidence));
    if (params.entity_types) searchParams.set('entity_types', params.entity_types);
    return request<GraphData>(`/graph/data?${searchParams.toString()}`);
  },
  getGraphAnalytics: (case_id?: number) => {
    const q = case_id ? `?case_id=${case_id}` : '';
    return request<CentralityAnalytics>(`/graph/analytics${q}`);
  },
  findShortestPath: (source_entity_id: number, target_entity_id: number) => request<any>('/graph/shortest-path', {
    method: 'POST',
    body: JSON.stringify({ source_entity_id, target_entity_id }),
  }),

  // AI Assistant
  askAssistant: (query: string, case_id?: number, focus_entity_id?: number) => request<{
    query: string;
    answer: string;
    evidence_citations: Array<{ document_title: string; excerpt: string; page: number; confidence: number }>;
    suggested_followups: string[];
    has_unverified_mentions: boolean;
  }>('/assistant/chat', {
    method: 'POST',
    body: JSON.stringify({ query, case_id, focus_entity_id }),
  }),

  // Alerts
  listAlerts: (case_id?: number, status?: string) => {
    const searchParams = new URLSearchParams();
    if (case_id) searchParams.set('case_id', String(case_id));
    if (status) searchParams.set('status', status);
    return request<NetworkPatternAlert[]>(`/alerts?${searchParams.toString()}`);
  },
  resolveAlert: (id: number, status: string, resolution_notes?: string) => request<NetworkPatternAlert>(`/alerts/${id}/resolve`, {
    method: 'PUT',
    body: JSON.stringify({ status, resolution_notes }),
  }),

  // Audit Logs
  listAuditLogs: (action?: string, case_id?: number) => {
    const searchParams = new URLSearchParams();
    if (action) searchParams.set('action', action);
    if (case_id) searchParams.set('case_id', String(case_id));
    return request<AuditLog[]>(`/audit/logs?${searchParams.toString()}`);
  },

  // Health
  getSystemHealth: () => request<any>('/system/health'),

  // Synthetic Data Engine & Scenarios
  listSyntheticScenarios: () => request<Array<{ id: string; title: string; description: string; cases_count: number; entities_count: number; relationships_count: number; focus: string }>>('/synthetic/scenarios'),
  listSyntheticSamples: () => request<Array<{ id: string; title: string; category: string; jurisdiction: string; text: string }>>('/synthetic/samples'),
  loadSyntheticScenario: (scenario_id: string) => request<any>(`/synthetic/load-scenario/${scenario_id}`, { method: 'POST' }),
  resetSyntheticDataset: () => request<any>('/synthetic/reset', { method: 'POST' }),
  exportSyntheticDataset: () => request<any>('/synthetic/export'),

  // Report URL
  getReportUrl: (case_id?: number) => {
    return case_id ? `/api/reports/html?case_id=${case_id}` : `/api/reports/html`;
  }
};
