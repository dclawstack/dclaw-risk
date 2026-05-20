"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { api, type Control, type ControlType } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

const TYPES: ControlType[] = [
  "preventive",
  "detective",
  "corrective",
  "compensating",
];

export default function ControlsPage() {
  const [controls, setControls] = useState<Control[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [framework, setFramework] = useState("");
  const [type, setType] = useState<ControlType>("preventive");
  const [effectiveness, setEffectiveness] = useState(3);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const data = await api.controls.list();
      setControls(data.items);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function addControl() {
    if (!name) return;
    setBusy(true);
    setError(null);
    try {
      await api.controls.create({
        name,
        framework: framework || undefined,
        control_type: type,
        effectiveness,
      });
      setName("");
      setFramework("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await api.controls.delete(id);
      setControls((cs) => cs.filter((c) => c.id !== id));
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Controls</h1>
        <p className="text-slate-600 text-sm">
          {controls.length} control{controls.length === 1 ? "" : "s"} in the
          catalogue
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add a control</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Name</label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. MFA on all admin accounts"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">
                Framework (optional)
              </label>
              <Input
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                placeholder="e.g. NIST 800-53"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as ControlType)}
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
              >
                {TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">
                Effectiveness (1-5)
              </label>
              <Input
                type="number"
                min={1}
                max={5}
                value={effectiveness}
                onChange={(e) => setEffectiveness(Number(e.target.value))}
              />
            </div>
          </div>
          <Button onClick={addControl} disabled={!name || busy}>
            <Plus className="w-4 h-4 mr-1" />
            {busy ? "Adding…" : "Add control"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Catalogue</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-sm text-slate-500">Loading…</div>
          ) : controls.length === 0 ? (
            <div className="text-sm text-slate-500">
              No controls yet — add one above.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {controls.map((c) => (
                <div
                  key={c.id}
                  className="flex items-center justify-between py-3 gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium truncate">{c.name}</div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {c.framework || "no framework"} · {c.control_type} ·
                      effectiveness {c.effectiveness}/5
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{c.control_type}</Badge>
                    <Button variant="ghost" size="sm" onClick={() => remove(c.id)}>
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
