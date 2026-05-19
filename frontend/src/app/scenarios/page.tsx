"use client";

import { useEffect, useState } from "react";
import { Plus, Sparkles, Play, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type Scenario = Awaited<ReturnType<typeof api.scenarios.list>>["items"][number];
type Result = Awaited<ReturnType<typeof api.scenarios.stressTest>>;

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [multJson, setMultJson] = useState(
    '{"Financial":{"severity":1.5,"probability":1.3}}'
  );
  const [aiContext, setAiContext] = useState("Severe global recession");

  const [result, setResult] = useState<Result | null>(null);

  async function refresh() {
    try {
      const data = await api.scenarios.list();
      setScenarios(data.items);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function create() {
    setBusy(true);
    setError(null);
    try {
      const multipliers = JSON.parse(multJson);
      await api.scenarios.create({
        name,
        description: description || undefined,
        multipliers,
      });
      setName("");
      setDescription("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function generate() {
    setBusy(true);
    setError(null);
    try {
      const res = await api.scenarios.generate(aiContext);
      setName(res.name);
      setDescription(res.description);
      setMultJson(JSON.stringify(res.multipliers, null, 2));
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function run(id: string) {
    setBusy(true);
    setError(null);
    try {
      const res = await api.scenarios.stressTest(id);
      setResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await api.scenarios.delete(id);
      setScenarios((s) => s.filter((x) => x.id !== id));
      if (result?.scenario_id === id) setResult(null);
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Scenarios</h1>
        <p className="text-sm text-slate-600">
          Define what-if multipliers per category, then stress-test the register.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">New scenario</CardTitle>
          <div className="flex items-center gap-2">
            <Input
              value={aiContext}
              onChange={(e) => setAiContext(e.target.value)}
              className="w-64"
              placeholder="AI context (e.g. cyber pandemic)"
            />
            <Button variant="outline" size="sm" onClick={generate} disabled={busy}>
              <Sparkles className="w-4 h-4 mr-1" />
              Generate
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-600">Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Severe recession"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-600">
              Description
            </label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-600">
              Multipliers JSON ({"{category: {severity, probability}}"})
            </label>
            <textarea
              value={multJson}
              onChange={(e) => setMultJson(e.target.value)}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-xs font-mono"
              rows={6}
            />
          </div>
          <Button onClick={create} disabled={!name || busy}>
            <Plus className="w-4 h-4 mr-1" /> Add scenario
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Scenarios</CardTitle>
        </CardHeader>
        <CardContent>
          {scenarios.length === 0 ? (
            <div className="text-sm text-slate-500">No scenarios yet.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {scenarios.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between py-3 gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium truncate">{s.name}</div>
                    <div className="text-xs text-slate-500">
                      {Object.keys(s.multipliers).length} category multiplier(s)
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" onClick={() => run(s.id)} disabled={busy}>
                      <Play className="w-4 h-4 mr-1" /> Run
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => remove(s.id)}
                    >
                      <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Stress test result</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex gap-6">
              <div>
                <div className="text-xs text-slate-500">Baseline total</div>
                <div className="font-semibold tabular-nums">
                  {result.baseline_total}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Projected total</div>
                <div className="font-semibold tabular-nums">
                  {result.projected_total}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Delta</div>
                <Badge
                  className={
                    result.delta_pct >= 25
                      ? "bg-red-500"
                      : result.delta_pct >= 10
                      ? "bg-amber-500"
                      : "bg-emerald-500"
                  }
                >
                  {result.delta_pct > 0 ? "+" : ""}
                  {result.delta_pct}%
                </Badge>
              </div>
            </div>
            <div className="divide-y divide-slate-100">
              {result.rows.map((r) => (
                <div
                  key={r.risk_id}
                  className="flex justify-between py-2"
                >
                  <div className="min-w-0">
                    <div className="font-medium truncate">{r.name}</div>
                    <div className="text-xs text-slate-500">{r.category}</div>
                  </div>
                  <div className="text-right tabular-nums">
                    <div>
                      {r.baseline_score} → {r.projected_score}
                    </div>
                    <div className="text-xs text-slate-500">
                      S{r.projected_severity} × P{r.projected_probability}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
