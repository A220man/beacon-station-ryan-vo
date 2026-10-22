import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  Plan,
  PlanCreate,
  PlanUpdate,
  PlanListResponse,
  Task,
  TaskCreate,
  TaskUpdate,
  LedgerEntry,
  LedgerEntryCreate,
  HealthResponse,
  AuthTestResponse,
  TokenEstimateResponse,
} from '../types';

const API_BASE = (import.meta as { env?: Record<string, string> }).env?.VITE_API_BASE || '/api/v1';

class ApiClient {
  client: AxiosInstance;
  private accessToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // For OIDC cookie-based auth
    });

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.accessToken && config.headers) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.clearToken();
          // Don't redirect here - let the auth context handle it
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string | null) {
    this.accessToken = token;
  }

  clearToken() {
    this.accessToken = null;
  }

  getToken(): string | null {
    return this.accessToken;
  }

  // Health
  async health(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  async authTest(): Promise<AuthTestResponse> {
    const response = await this.client.get<AuthTestResponse>('/auth/test');
    return response.data;
  }

  // Plans
  async listPlans(limit = 50, offset = 0, status?: string): Promise<PlanListResponse> {
    const params = new URLSearchParams();
    params.append('limit', String(limit));
    params.append('offset', String(offset));
    if (status) params.append('status', status);
    const response = await this.client.get<PlanListResponse>(`/plans?${params.toString()}`);
    return response.data;
  }

  async createPlan(data: PlanCreate): Promise<Plan> {
    const response = await this.client.post<Plan>('/plans', data);
    return response.data;
  }

  async getPlan(id: string): Promise<Plan> {
    const response = await this.client.get<Plan>(`/plans/${id}`);
    return response.data;
  }

  async updatePlan(id: string, data: PlanUpdate): Promise<Plan> {
    const response = await this.client.patch<Plan>(`/plans/${id}`, data);
    return response.data;
  }

  async deletePlan(id: string): Promise<void> {
    await this.client.delete(`/plans/${id}`);
  }

  // Tasks
  async listTasks(planId: string): Promise<Task[]> {
    const response = await this.client.get<Task[]>(`/plans/${planId}/tasks`);
    return response.data;
  }

  async createTask(planId: string, data: TaskCreate): Promise<Task> {
    const response = await this.client.post<Task>(`/plans/${planId}/tasks`, data);
    return response.data;
  }

  async getTask(planId: string, taskId: string): Promise<Task> {
    const response = await this.client.get<Task>(`/plans/${planId}/tasks/${taskId}`);
    return response.data;
  }

  async updateTask(planId: string, taskId: string, data: TaskUpdate): Promise<Task> {
    const response = await this.client.patch<Task>(`/plans/${planId}/tasks/${taskId}`, data);
    return response.data;
  }

  // Ledger
  async getLedger(planId: string, limit = 100, offset = 0): Promise<LedgerEntry[]> {
    const response = await this.client.get<LedgerEntry[]>(`/plans/${planId}/ledger?limit=${limit}&offset=${offset}`);
    return response.data;
  }

  async addLedgerEntry(planId: string, data: LedgerEntryCreate): Promise<LedgerEntry> {
    const response = await this.client.post<LedgerEntry>(`/plans/${planId}/ledger`, data);
    return response.data;
  }

  // Token estimation
  async estimateTokens(planId: string): Promise<TokenEstimateResponse> {
    const response = await this.client.get<TokenEstimateResponse>(`/plans/${planId}/tokens`);
    return response.data;
  }
}

export const api = new ApiClient();