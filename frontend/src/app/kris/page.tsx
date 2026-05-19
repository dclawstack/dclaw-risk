"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type KRI = Awaited<ReturnType<typeof api.kris.list>>["items"][number];

export default function KRIsPage() {
  const [kris, setKris] = useState<KRI[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [name, setName] = useState("");
  const [unit, setUnit] = useState("count");
  const [warn, setWarn] = useState(5);
  const [crit, setCrit] = useState(10);
  const [direction, setDirection] = useState<"above" | "below">("above");
  const [value, setValue] = useState(0);

  async function refresh() {
    try {
      const data = await api.kris.list();
      setKris(data.items);
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
    setError(null);
    try {
      await api.kris.create({
        name,
        unit,
        current_value: value,
        threshold_warn: warn,
        threshold_critical: crit,
        direction,
      });
      setName("");
      setValue(0);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await api.kris.delete(id);
      setKris((ks) => ks.filter((k) => k.id !== id));
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Key Risk Indicators</h1>
        <p className="text-sm text-slate-600">
          Track metrics that signal risk crossing tolerance thresholds.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add a KRI</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <Field label="Name">
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </Field>
            <Field label="Unit">
              <Input value={unit} onChange={(e) => setUnit(e.target.value)} />
            </Field>
            <Field label="Current value">
              <Input
                type="number"
                value={value}
                onChange={(e) => setValue(Number(e.target.value))}
              />
            </Field>
            <Field label="Warn threshold">
              <Input
                type="number"
                value={warn}
                onChange={(e) => setWarn(Number(e.target.value))}
              />
            </Field>
            <Field label="Critical threshold">
              <Input
                type="number"
                value={crit}
                onChange={(e) => setCrit(Number(e.target.value))}
              />
            </Field>
            <Field label="Bad if">
              <select
                value={direction}
                onChange={(e) =>
                  setDirection(e.target.value as "above" | "below")
                }
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
              >
                <option value="above">value ≥ threshold</option>
                <option value="below">value ≤ threshold</option>
              </select>
            </Field>
          </div>
          <Button onClick={add} disabled={!name || busy}>
            <Plus className="w-4 h-4 mr-1" /> Add KRI
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          {kris.length === 0 ? (
            <div className="text-sm text-slate-500">
              No KRIs yet — add one above.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {kris.map((k) => (
                <div
                  key={k.id}
                  className="flex items-center justify-between py-3 gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium truncate">{k.name}</div>
                    <div className="text-xs text-slate-500">
                      current {k.current_value} {k.unit} ·{" "}
                      {k.direction === "above" ? "≥" : "≤"} warn {k.threshold_warn}{" "}
                      / crit {k.threshold_critical}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        k.status === "critical"
                          ? "bg-red-500"
                          : k.status === "warn"
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }
                    >
                      {k.status}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => remove(k.id)}
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
