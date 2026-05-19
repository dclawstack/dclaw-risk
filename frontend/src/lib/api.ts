const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  body: string;
  constructor(message: string, status: number, body: string) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(`API ${response.status} ${path}`, response.status, body);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

// --- Types ---

export type RiskStatus =
  | "identified"
  | "assessed"
  | "treated"
  | "monitored"
  | "closed"
  | "accepted";

export interface Risk {
  id: string;
  name: string;
  description?: string | null;
  category: string;
  status: RiskStatus;
  owner?: string | null;
  severity: number;
  probability: number;
  velocity: number;
  score: number;
  ai_classification?: string | null;
  ai_rationale?: string | null;
  created_at: string;
  updated_at: string;
}

export interface RiskList {
  items: Risk[];
  total: number;
}

export interface RiskCreate {
  name: string;
  description?: string;
  category: string;
  status?: RiskStatus;
  owner?: string;
  severity?: number;
  probability?: number;
  velocity?: number;
}

export type ControlType =
  | "preventive"
  | "detective"
  | "corrective"
  | "compensating";

export interface Control {
  id: string;
  name: string;
  description?: string | null;
  framework?: string | null;
  control_type: ControlType;
  effectiveness: number;
  owner?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ControlList {
  items: Control[];
  total: number;
}

export interface CurvePoint {
  loss: number;
  exceedance_probability: number;
}

export interface Assessment {
  id: string;
  risk_id: string;
  kind: "qualitative" | "quantitative";
  assessor?: string | null;
  severity?: number | null;
  probability?: number | null;
  loss_min?: number | null;
  loss_mode?: number | null;
  loss_max?: number | null;
  freq_min?: number | null;
  freq_max?: number | null;
  iterations?: number | null;
  loss_p10?: number | null;
  loss_p50?: number | null;
  loss_p90?: number | null;
  loss_mean?: number | null;
  curve?: CurvePoint[] | null;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface SuggestedAction {
  title: string;
  detail?: string | null;
}

export interface ChatResponse {
  reply: string;
  suggested_actions: SuggestedAction[];
  provider: string;
}

// --- API surface ---

export const api = {
  health: () => fetchJson<{ status: string }>("/health/"),

  risks: {
    list: (params?: { category?: string; status?: string }) => {
      const q = new URLSearchParams();
      if (params?.category) q.set("category", params.category);
      if (params?.status) q.set("status", params.status);
      const qs = q.toString();
      return fetchJson<RiskList>(`/api/v1/risks${qs ? `?${qs}` : ""}`);
    },
    create: (payload: RiskCreate) =>
      fetchJson<Risk>("/api/v1/risks", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    get: (id: string) => fetchJson<Risk>(`/api/v1/risks/${id}`),
    update: (id: string, payload: Partial<RiskCreate>) =>
      fetchJson<Risk>(`/api/v1/risks/${id}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
    delete: (id: string) =>
      fetchJson<void>(`/api/v1/risks/${id}`, { method: "DELETE" }),
  },

  controls: {
    list: () => fetchJson<ControlList>("/api/v1/controls"),
    create: (payload: {
      name: string;
      description?: string;
      framework?: string;
      control_type?: ControlType;
      effectiveness?: number;
      owner?: string;
    }) =>
      fetchJson<Control>("/api/v1/controls", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    delete: (id: string) =>
      fetchJson<void>(`/api/v1/controls/${id}`, { method: "DELETE" }),
  },

  riskControls: {
    list: (riskId: string) =>
      fetchJson<Control[]>(`/api/v1/risks/${riskId}/controls`),
    map: (riskId: string, controlId: string, effectiveness: number) =>
      fetchJson<Control[]>(`/api/v1/risks/${riskId}/controls`, {
        method: "POST",
        body: JSON.stringify({
          control_id: controlId,
          effectiveness,
        }),
      }),
    unmap: (riskId: string, controlId: string) =>
      fetchJson<void>(`/api/v1/risks/${riskId}/controls/${controlId}`, {
        method: "DELETE",
      }),
  },

  assessments: {
    list: (riskId: string) =>
      fetchJson<Assessment[]>(`/api/v1/risks/${riskId}/assessments`),
    qualitative: (
      riskId: string,
      payload: { severity: number; probability: number; assessor?: string }
    ) =>
      fetchJson<Assessment>(
        `/api/v1/risks/${riskId}/assessments/qualitative`,
        {
          method: "POST",
          body: JSON.stringify({ kind: "qualitative", ...payload }),
        }
      ),
    quantitative: (
      riskId: string,
      payload: {
        loss_min: number;
        loss_mode: number;
        loss_max: number;
        freq_min: number;
        freq_max: number;
        iterations?: number;
        assessor?: string;
      }
    ) =>
      fetchJson<Assessment>(
        `/api/v1/risks/${riskId}/assessments/quantitative`,
        {
          method: "POST",
          body: JSON.stringify({ kind: "quantitative", ...payload }),
        }
      ),
  },

  ai: {
    chat: (messages: ChatMessage[]) =>
      fetchJson<ChatResponse>("/api/v1/ai/risk-chat", {
        method: "POST",
        body: JSON.stringify({ messages }),
      }),
    identify: (context: string, count = 5) =>
      fetchJson<{
        risks: Array<{
          name: string;
          category: string;
          severity: number;
          probability: number;
          rationale?: string;
        }>;
        provider: string;
      }>("/api/v1/ai/identify-risks", {
        method: "POST",
        body: JSON.stringify({ context, count }),
      }),
    classify: (name: string, description?: string) =>
      fetchJson<{
        category: string;
        severity: number;
        probability: number;
        rationale: string;
        provider: string;
      }>("/api/v1/ai/classify-risk", {
        method: "POST",
        body: JSON.stringify({ name, description }),
      }),
  },
};
