"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Summary = Awaited<ReturnType<typeof api.reports.summary>>;
type Exposure = Awaited<ReturnType<typeof api.reports.exposure>>;

export default function ReportsPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [exposure, setExposure] = useState<Exposure | null>(null);
  const [narrative, setNarrative] = useState<string | null>(null);
  const [provider, setProvider] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [s, e] = await Promise.all([
          api.reports.summary(),
          api.reports.exposure(),
        ]);
        setSummary(s);
        setExposure(e);
      } catch (err) {
        setError(String(err));
      }
    })();
  }, []);

  async function gen() {
    setGenerating(true);
    setError(null);
    try {
      const res = await api.reports.narrative();
      setNarrative(res.narrative);
      setProvider(res.provider);
    } catch (err) {
      setError(String(err));
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Risk Reporting</h1>
        <p className="text-sm text-slate-600">
          Aggregate posture, exposure, and an AI-written executive briefing.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="Risks" value={summary?.total_risks ?? "—"} />
        <Stat label="Mean score" value={summary?.mean_score ?? "—"} />
        <Stat
          label="Control coverage"
          value={
            summary ? `${summary.control_coverage_pct}%` : "—"
          }
        />
        <Stat label="Controls" value={summary?.total_controls ?? "—"} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">By category</CardTitle>
          </CardHeader>
          <CardContent>
            {summary ? (
              <Distribution data={summary.by_category} />
            ) : (
              <div className="text-sm text-slate-500">Loading…</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">By status</CardTitle>
          </CardHeader>
          <CardContent>
            {summary ? (
              <Distribution data={summary.by_status} />
            ) : (
              <div className="text-sm text-slate-500">Loading…</div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Top risks</CardTitle>
        </CardHeader>
        <CardContent>
          {summary && summary.top_risks.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {summary.top_risks.map((r) => (
                <div key={r.id} className="flex justify-between py-2 text-sm">
                  <div>
                    <div className="font-medium">{r.name}</div>
                    <div className="text-xs text-slate-500">
                      {r.category} · {r.status}
                    </div>
                  </div>
                  <div className="font-semibold tabular-nums">{r.score}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-slate-500">No risks yet.</div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Annualised loss exposure</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          {exposure && exposure.risks_with_quantitative > 0 ? (
            <>
              <div className="grid grid-cols-3 gap-3">
                <Stat
                  label="Total mean"
                  value={`$${Math.round(exposure.total_mean).toLocaleString()}`}
                />
                <Stat
                  label="Total P50"
                  value={`$${Math.round(exposure.total_p50).toLocaleString()}`}
                />
                <Stat
                  label="Total P90"
                  value={`$${Math.round(exposure.total_p90).toLocaleString()}`}
                />
              </div>
              <div className="divide-y divide-slate-100 mt-2">
                {exposure.per_risk.map((r) => (
                  <div key={r.risk_id} className="flex justify-between py-2">
                    <div className="truncate pr-2">
                      <div className="font-medium">{r.name}</div>
                      <div className="text-xs text-slate-500">{r.category}</div>
                    </div>
                    <div className="text-right tabular-nums">
                      <div>${Math.round(r.loss_mean ?? 0).toLocaleString()}</div>
                      <div className="text-xs text-slate-500">
                        P90 ${Math.round(r.loss_p90 ?? 0).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-sm text-slate-500">
              No quantitative assessments yet. Run a Monte Carlo simulation on a
              risk to see exposure here.
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Executive briefing</CardTitle>
          <Button onClick={gen} disabled={generating} size="sm">
            <Sparkles className="w-4 h-4 mr-1" />
            {generating ? "Writing…" : "Generate"}
          </Button>
        </CardHeader>
        <CardContent>
          {narrative ? (
            <>
              <div className="whitespace-pre-wrap text-sm text-slate-800">
                {narrative}
              </div>
              {provider && (
                <div className="text-xs text-slate-400 mt-2">
                  via {provider}
                </div>
              )}
            </>
          ) : (
            <div className="text-sm text-slate-500">
              Click Generate to produce an AI-written board summary grounded in
              the numbers above.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="font-semibold text-lg tabular-nums">{value}</div>
    </div>
  );
}

function Distribution({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map((e) => e[1]));
  return (
    <div className="space-y-1.5 text-sm">
      {entries.length === 0 ? (
        <div className="text-slate-500">No data.</div>
      ) : (
        entries.map(([k, v]) => (
          <div key={k} className="flex items-center gap-2">
            <div className="w-32 truncate text-slate-700">{k}</div>
            <div className="flex-1 bg-slate-100 rounded-sm h-3 overflow-hidden">
              <div
                className="bg-emerald-500 h-3"
                style={{ width: `${(v / max) * 100}%` }}
              />
            </div>
            <div className="w-8 text-right tabular-nums text-slate-600">{v}</div>
          </div>
        ))
      )}
    </div>
  );
}
