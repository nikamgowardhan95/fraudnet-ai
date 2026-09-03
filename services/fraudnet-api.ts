const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) } })
  if (!response.ok) throw new Error(`FraudNet API error (${response.status})`)
  return response.json() as Promise<T>
}

export type DashboardSummary = { total_transactions: number; fraud_detected: number; high_risk_transactions: number; fraud_rings: number; suspicious_amount: number; metrics: Record<string, unknown> }
export const fraudnetApi = {
  health: () => request<{ status: string }>('/health'),
  summary: () => request<DashboardSummary>('/api/dashboard/summary'),
  transactions: (query = '') => request<{ items: unknown[]; total: number }>(`/api/transactions${query ? `?q=${encodeURIComponent(query)}` : ''}`),
  rings: () => request<{ items: unknown[]; total: number }>('/api/fraud-rings'),
  ring: (id: string) => request<unknown>(`/api/fraud-rings/${encodeURIComponent(id)}`),
  graph: (id: string) => request<unknown>(`/api/fraud-rings/${encodeURIComponent(id)}/graph`),
  timeline: (id: string) => request<unknown>(`/api/fraud-rings/${encodeURIComponent(id)}/timeline`),
  investigation: (id: string) => request<unknown>(`/api/investigations/${encodeURIComponent(id)}`),
  metrics: () => request<Record<string, unknown>>('/api/model/metrics'),
  simulateDevice: (deviceId: string) => request<unknown>(`/api/simulation/block-device?device_id=${encodeURIComponent(deviceId)}`, { method: 'POST' }),
}
