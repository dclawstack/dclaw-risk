"use client";

import { useEffect, useState } from "react";
import { Plus, Sparkles, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type Incident = Awaited<ReturnType<typeof api.incidents.list>>["items"][number];

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [title, setTitle] = useState("");
  const [severity, setSeverity] = useState(3);
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [patterns, setPatterns] = useState<string[] | null>(null);
  const [provider, setProvider] = useState<string | null>(null);

  async function refresh() {
    try {
      const data = await api.incidents.list();
      setIncidents(data.items);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function add() {
    if (!title) return;
    setBusy(true);
    try {
      await api.incidents.create({ title, severity, description });
      setTitle("");
      setDescription("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await api.incidents.delete(id);
      setIncidents((xs) => xs.filter((x) => x.id !== id));
    } catch (e) {
      setError(String(e));
    }
  }

  async function detectPatterns() {
    setBusy(true);
    try {
      const res = await api.incidents.patterns();
      setPatterns(res.patterns);
      setProvider(res.provider);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Incidents</h1>
        <p className="text-sm text-slate-600">
          Log realised events. Link them to a risk to keep your register
          calibrated.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Log an incident</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="md:col-span-2 space-y-1">
              <label className="text-xs font-medium text-slate-600">Title</label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. CDN outage 17 May"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">
                Severity 1-5
              </label>
              <Input
                type="number"
                min={1}
                max={5}
                value={severity}
                onChange={(e) => setSeverity(Number(e.target.value))}
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-600">
              Description (optional)
            </label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <Button onClick={add} disabled={!title || busy}>
            <Plus className="w-4 h-4 mr-1" />
            {busy ? "…" : "Log incident"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">AI pattern detection</CardTitle>
          <Button
            size="sm"
            variant="outline"
            onClick={detectPatterns}
            disabled={busy || incidents.length === 0}
          >
            <Sparkles className="w-4 h-4 mr-1" /> Analyse
          </Button>
        </CardHeader>
        <CardContent>
          {patterns ? (
            <ul className="text-sm space-y-1 list-disc pl-5">
              {patterns.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
              {provider && (
                <div className="text-xs text-slate-400 mt-2">via {provider}</div>
              )}
            </ul>
          ) : (
            <div className="text-sm text-slate-500">
              Click Analyse to find recurring themes across your incident log.
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Log</CardTitle>
        </CardHeader>
        <CardContent>
          {incidents.length === 0 ? (
            <div className="text-sm text-slate-500">
              No incidents logged yet.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {incidents.map((i) => (
                <div
                  key={i.id}
                  className="flex items-center justify-between py-3 gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium truncate">{i.title}</div>
                    <div className="text-xs text-slate-500">
                      {new Date(i.occurred_at).toLocaleDateString()} ·{" "}
                      severity {i.severity}/5 · {i.status}
                      {i.description ? ` — ${i.description}` : ""}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{i.status}</Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => remove(i.id)}
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
    </div>
  );
}
