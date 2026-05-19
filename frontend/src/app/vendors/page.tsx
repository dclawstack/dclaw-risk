"use client";

import { useEffect, useState } from "react";
import { Plus, Sparkles, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type Vendor = Awaited<ReturnType<typeof api.vendors.list>>["items"][number];

export default function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [category, setCategory] = useState("SaaS");
  const [criticality, setCriticality] = useState(3);
  const [notes, setNotes] = useState("");

  async function refresh() {
    try {
      const data = await api.vendors.list();
      setVendors(data.items);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function add() {
    if (!name) return;
    setBusy(true);
    try {
      await api.vendors.create({ name, category, criticality, notes });
      setName("");
      setNotes("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function score(id: string) {
    setBusy(true);
    try {
      await api.vendors.aiScore(id);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await api.vendors.delete(id);
      setVendors((vs) => vs.filter((v) => v.id !== id));
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Third-party vendors</h1>
        <p className="text-sm text-slate-600">
          Score and monitor critical dependencies.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add a vendor</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Field label="Name">
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </Field>
            <Field label="Category">
              <Input
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </Field>
            <Field label="Criticality 1-5">
              <Input
                type="number"
                min={1}
                max={5}
                value={criticality}
                onChange={(e) => setCriticality(Number(e.target.value))}
              />
            </Field>
          </div>
          <Field label="Notes (optional)">
            <Input value={notes} onChange={(e) => setNotes(e.target.value)} />
          </Field>
          <Button onClick={add} disabled={!name || busy}>
            <Plus className="w-4 h-4 mr-1" /> Add vendor
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Vendors</CardTitle>
        </CardHeader>
        <CardContent>
          {vendors.length === 0 ? (
            <div className="text-sm text-slate-500">No vendors yet.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {vendors.map((v) => (
                <div
                  key={v.id}
                  className="flex items-center justify-between py-3 gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium truncate">{v.name}</div>
                    <div className="text-xs text-slate-500">
                      {v.category || "uncategorised"} · criticality{" "}
                      {v.criticality}/5
                      {v.last_assessed_at
                        ? ` · last scored ${new Date(
                            v.last_assessed_at
                          ).toLocaleDateString()}`
                        : ""}
                    </div>
                    {v.ai_rationale && (
                      <div className="text-xs text-slate-400 mt-1 italic">
                        {v.ai_rationale}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        v.score >= 70
                          ? "bg-red-500"
                          : v.score >= 40
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }
                    >
                      {v.score}/100
                    </Badge>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => score(v.id)}
                      disabled={busy}
                    >
                      <Sparkles className="w-4 h-4 mr-1" />
                      AI score
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => remove(v.id)}
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

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-slate-600">{label}</label>
      {children}
    </div>
  );
}
