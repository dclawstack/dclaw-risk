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

  reports: {
    summary: () =>
      fetchJson<{
        total_risks: number;
        by_category: Record<string, number>;
        by_status: Record<string, number>;
        top_risks: Array<{
          id: string;
          name: string;
          category: string;
          score: number;
          status: string;
        }>;
        mean_score: number;
        control_coverage_pct: number;
        total_controls: number;
      }>("/api/v1/reports/summary"),
    exposure: () =>
      fetchJson<{
        risks_with_quantitative: number;
        total_p50: number;
        total_p90: number;
        total_mean: number;
        per_risk: Array<{
          risk_id: string;
          name: string;
          category: string;
          loss_p10: number | null;
          loss_p50: number | null;
          loss_p90: number | null;
          loss_mean: number | null;
        }>;
      }>("/api/v1/reports/exposure"),
    narrative: () =>
      fetchJson<{ narrative: string; provider: string; facts: string }>(
        "/api/v1/reports/narrative",
        { method: "POST" }
      ),
  },

  kris: {
    list: () =>
      fetchJson<{
        items: Array<{
          id: string;
          name: string;
          description?: string | null;
          unit: string;
          current_value: number;
          threshold_warn: number;
          threshold_critical: number;
          direction: "above" | "below";
          status: "ok" | "warn" | "critical";
          risk_id?: string | null;
          owner?: string | null;
          created_at: string;
          updated_at: string;
        }>;
        total: number;
      }>("/api/v1/kris"),
    create: (payload: {
      name: string;
      unit?: string;
      current_value: number;
      threshold_warn: number;
      threshold_critical: number;
      direction?: "above" | "below";
      description?: string;
      risk_id?: string;
      owner?: string;
    }) =>
      fetchJson("/api/v1/kris", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    update: (id: string, payload: Record<string, unknown>) =>
      fetchJson(`/api/v1/kris/${id}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
    delete: (id: string) =>
      fetchJson<void>(`/api/v1/kris/${id}`, { method: "DELETE" }),
  },

  incidents: {
    list: () =>
      fetchJson<{
        items: Array<{
          id: string;
          title: string;
          description?: string | null;
          severity: number;
          occurred_at: string;
          risk_id?: string | null;
          status: string;
        }>;
        total: number;
      }>("/api/v1/incidents"),
    create: (payload: {
      title: string;
      description?: string;
      severity?: number;
      occurred_at?: string;
      risk_id?: string;
      status?: string;
    }) =>
      fetchJson("/api/v1/incidents", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    delete: (id: string) =>
      fetchJson<void>(`/api/v1/incidents/${id}`, { method: "DELETE" }),
    patterns: () =>
      fetchJson<{
        patterns: string[];
        raw?: string;
        provider: string;
        count_analysed: number;
      }>("/api/v1/incidents/patterns"),
  },

  scenarios: {
    list: () =>
      fetchJson<{
        items: Array<{
          id: string;
          name: string;
          description?: string | null;
          multipliers: Record<string, { severity: number; probability: number }>;
          created_at: string;
        }>;
        total: number;
      }>("/api/v1/scenarios"),
    create: (payload: {
      name: string;
      description?: string;
      multipliers: Record<string, { severity: number; probability: number }>;
    }) =>
      fetchJson("/api/v1/scenarios", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    delete: (id: string) =>
      fetchJson<void>(`/api/v1/scenarios/${id}`, { method: "DELETE" }),
    stressTest: (id: string) =>
      fetchJson<{
        scenario_id: string;
        baseline_total: number;
        projected_total: number;
        delta_pct: number;
        rows: Array<{
          risk_id: string;
          name: string;
          category: string;
          baseline_score: number;
          projected_severity: number;
          projected_probability: number;
          projected_score: number;
        }>;
      }>(`/api/v1/scenarios/${id}/stress-test`, { method: "POST" }),
    generate: (context: string) =>
      fetchJson<{
        name: string;
        description: string;
        multipliers: Record<string, { severity: number; probability: number }>;
        provider: string;
      }>("/api/v1/scenarios/generate", {
        method: "POST",
        body: JSON.stringify({ context }),
      }),
  },

  vendors: {
    list: () =>
      fetchJson<{
        items: Array<{
          id: string;
          name: string;
          category?: string | null;
          criticality: number;
          score: number;
          notes?: string | null;
          last_assessed_at?: string | null;
          ai_rationale?: string | null;
        }>;
        total: number;
      }>("/api/v1/vendors"),
    create: (payload: {
      name: string;
      category?: string;
      criticality?: number;
      score?: number;
      notes?: string;
    }) =>
      fetchJson("/api/v1/vendors", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    delete: (id: string) =>
      fetchJson<void>(`/api/v1/vendors/${id}`, { method: "DELETE" }),
    aiScore: (id: string) =>
      fetchJson(`/api/v1/vendors/${id}/ai-score`, { method: "POST" }),
  },

  emerging: {
    list: () =>
      fetchJson<{
        items: Array<{
          id: string;
          title: string;
          source: string;
          url: string | null;
          summary: string | null;
          detected_at: string;
          impact_score: number;
          status: string;
        }>;
        total: number;
        feeds: string[];
      }>("/api/v1/emerging"),
    refresh: (feed = "nvd-cve", limit = 10) =>
      fetchJson<{ feed: string; fetched: number; new: number }>(
        `/api/v1/emerging/refresh?feed=${feed}&limit=${limit}`,
        { method: "POST" }
      ),
  },

  culture: {
    listScores: () =>
      fetchJson<{
        items: Array<{
          id: string;
          period: string;
          dimension: string;
          score: number;
          benchmark: number | null;
          notes: string | null;
        }>;
      }>("/api/v1/culture"),
    listSurveys: () =>
      fetchJson<{
        items: Array<{
          id: string;
          name: string;
          period: string;
          status: string;
          questions: Array<{
            id: string;
            dimension: string;
            prompt: string;
            order_index: number;
          }>;
        }>;
      }>("/api/v1/culture/surveys"),
    createSurvey: (payload: {
      name: string;
      period: string;
      description?: string;
      questions: Array<{
        dimension: string;
        prompt: string;
        order_index?: number;
      }>;
    }) =>
      fetchJson("/api/v1/culture/surveys", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    openSurvey: (id: string) =>
      fetchJson(`/api/v1/culture/surveys/${id}/open`, { method: "POST" }),
    submitSurvey: (
      id: string,
      payload: {
        respondent_hash?: string;
        answers: Array<{ question_id: string; score: number }>;
      }
    ) =>
      fetchJson(`/api/v1/culture/surveys/${id}/responses`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    closeSurvey: (id: string) =>
      fetchJson<{
        id: string;
        status: string;
        dimensions_scored: number;
        responses_total: number;
      }>(`/api/v1/culture/surveys/${id}/close`, { method: "POST" }),
    deleteSurvey: (id: string) =>
      fetchJson<void>(`/api/v1/culture/surveys/${id}`, { method: "DELETE" }),
  },

  documents: {
    list: () =>
      fetchJson<{
        items: Array<{
          id: string;
          title: string;
          source: string | null;
          excerpt: string;
          created_at: string;
        }>;
        total: number;
      }>("/api/v1/documents"),
    create: (payload: { title: string; content: string; source?: string }) =>
      fetchJson("/api/v1/documents", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    delete: (id: string) =>
      fetchJson<void>(`/api/v1/documents/${id}`, { method: "DELETE" }),
    search: (q: string, k = 5) =>
      fetchJson<{
        query: string;
        hits: Array<{
          document_id: string;
          title: string;
          score: number;
          snippet: string;
        }>;
      }>(`/api/v1/documents/search?q=${encodeURIComponent(q)}&k=${k}`),
  },

  compliance: {
    library: () =>
      fetchJson<{
        mock: boolean;
        source: string;
        frameworks: Array<{
          id: string;
          name: string;
          category: string;
          requirements: Array<{
            id: string;
            title: string;
            expects_control_types: string[];
          }>;
        }>;
      }>("/api/v1/compliance/library"),
    unifiedView: () =>
      fetchJson<{
        mock: boolean;
        source: string;
        totals: {
          requirements: number;
          covered: number;
          uncovered: number;
          coverage_pct: number;
        };
        rows: Array<{
          framework_id: string;
          framework: string;
          requirement_id: string;
          requirement: string;
          expects: string[];
          matching_controls: Array<{
            id: string;
            name: string;
            type: string;
            effectiveness: number;
          }>;
          covered: boolean;
        }>;
      }>("/api/v1/compliance/unified-view"),
    sync: () =>
      fetchJson<{ mock: boolean; source: string; received?: number }>(
        "/api/v1/compliance/sync",
        { method: "POST" }
      ),
  },
};
