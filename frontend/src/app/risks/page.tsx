"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Sparkles, Trash2 } from "lucide-react";
import { api, type Risk } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { HeatMap } from "@/components/heat-map";

const CATEGORIES = [
  "Operational",
  "Financial",
  "Legal",
  "Reputational",
  "Cybersecurity",
  "Strategic",
  "Compliance",
  "Third-Party",
];

export default function RisksPage() {
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [category, setCategory] = useState("Operational");
  const [description, setDescription] = useState("");
  const [aiBusy, setAiBusy] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const data = await api.risks.list();
      setRisks(data.items);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function aiClassify() {
    if (!name) return;
    setAiBusy(true);
    try {
      const res = await api.ai.classify(name, description);
      setCategory(res.category);
    } catch (e) {
      setError(String(e));
    } finally {
      setAiBusy(false);
    }
  }

  async function createRisk() {
    if (!name) return;
    setCreating(true);
    setError(null);
    try {
      await api.risks.create({
        name,
        category,
        description: description || undefined,
      });
      setName("");
      setDescription("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setCreating(false);
    }
  }

  async function remove(id: string) {
    try {
      await api.risks.delete(id);
      setRisks((rs) => rs.filter((r) => r.id !== id));
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Risk Register</h1>
          <p className="text-slate-600 text-sm">
            {risks.length} risk{risks.length === 1 ? "" : "s"} tracked
          </p>
        </div>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add a new risk</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Name</label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Cloud provider outage"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Category</label>
              <div className="flex gap-2">
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="flex-1 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={aiClassify}
                  disabled={!name || aiBusy}
                >
                  <Sparkles className="w-4 h-4 mr-1" />
                  {aiBusy ? "…" : "AI"}
                </Button>
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-600">Description (optional)</label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Briefly describe the risk"
            />
          </div>
          <Button onClick={createRisk} disabled={creating || !name}>
            <Plus className="w-4 h-4 mr-1" />
            {creating ? "Adding…" : "Add risk"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Heat map</CardTitle>
        </CardHeader>
        <CardContent>
          <HeatMap risks={risks} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Risks</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-sm text-slate-500">Loading…</div>
          ) : risks.length === 0 ? (
            <div className="text-sm text-slate-500">
              No risks yet — add one above to get started.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {risks.map((r) => (
                <div
                  key={r.id}
                  className="flex items-center justify-between py-3 gap-3"
                >
                  <div className="min-w-0">
                    <Link
                      href={`/risks/${r.id}`}
                      className="font-medium text-slate-900 hover:text-emerald-700 truncate block"
                    >
                      {r.name}
                    </Link>
                    <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                      <span>{r.category}</span>
                      <span>·</span>
                      <span>S{r.severity} × P{r.probability} = {r.score}</span>
                      <span>·</span>
                      <span>{r.owner || "Unassigned"}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        r.score >= 16
                          ? "bg-red-500"
                          : r.score >= 9
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }
                    >
                      {r.status}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => remove(r.id)}
                      aria-label="Delete risk"
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
