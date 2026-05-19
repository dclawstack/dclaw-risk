"use client";

import { useEffect, useState } from "react";
import { Upload } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

type View = Awaited<ReturnType<typeof api.compliance.unifiedView>>;

export default function CompliancePage() {
  const [view, setView] = useState<View | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      setView(await api.compliance.unifiedView());
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function sync() {
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const r = await api.compliance.sync();
      setInfo(
        r.mock
          ? "Mock-mode sync acknowledged — wire COMPLIANCE_BASE_URL for live."
          : `Synced to ${r.source}.`
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  const grouped: Record<string, View["rows"]> = {};
  view?.rows.forEach((r) => {
    grouped[r.framework] ||= [];
    grouped[r.framework].push(r);
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Compliance</h1>
          <p className="text-sm text-slate-600">
            Joined view of framework requirements and our local controls.
            {view?.mock && (
              <span className="ml-2 inline-block">
                <Badge className="bg-amber-500">mock</Badge> — wire{" "}
                <code>COMPLIANCE_BASE_URL</code> to a live DClaw Compliance app.
              </span>
            )}
          </p>
        </div>
        <Button onClick={sync} disabled={busy}>
          <Upload className="w-4 h-4 mr-1" />
          Push controls
        </Button>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}
      {info && (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 text-emerald-700 px-3 py-2 text-sm">
          {info}
        </div>
      )}

      {view && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Stat label="Requirements" value={view.totals.requirements} />
          <Stat label="Covered" value={view.totals.covered} />
          <Stat label="Uncovered" value={view.totals.uncovered} />
          <Stat label="Coverage" value={`${view.totals.coverage_pct}%`} />
        </div>
      )}

      {Object.entries(grouped).map(([fw, rows]) => (
        <Card key={fw}>
          <CardHeader>
            <CardTitle className="text-base">{fw}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="divide-y divide-slate-100">
              {rows.map((r) => (
                <div
                  key={r.requirement_id}
                  className="py-3 flex justify-between gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium text-sm">
                      {r.requirement_id} — {r.requirement}
                    </div>
                    <div className="text-xs text-slate-500">
                      expects: {r.expects.join(", ") || "—"}
                    </div>
                    {r.matching_controls.length > 0 && (
                      <div className="text-xs text-slate-600 mt-1">
                        {r.matching_controls.map((c) => c.name).join(" · ")}
                      </div>
                    )}
                  </div>
                  <Badge
                    className={r.covered ? "bg-emerald-500" : "bg-red-500"}
                  >
                    {r.covered ? "covered" : "gap"}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
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
