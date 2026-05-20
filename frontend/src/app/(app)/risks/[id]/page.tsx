"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { api, type Assessment, type Control, type Risk } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LossExceedanceCurve } from "@/components/loss-exceedance-curve";

export default function RiskDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [risk, setRisk] = useState<Risk | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [controls, setControls] = useState<Control[]>([]);
  const [allControls, setAllControls] = useState<Control[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // qualitative form state
  const [qSev, setQSev] = useState(3);
  const [qProb, setQProb] = useState(3);

  // quantitative form state
  const [lossMin, setLossMin] = useState(10_000);
  const [lossMode, setLossMode] = useState(100_000);
  const [lossMax, setLossMax] = useState(1_000_000);
  const [freqMin, setFreqMin] = useState(0.05);
  const [freqMax, setFreqMax] = useState(0.5);
  const [iterations, setIterations] = useState(10_000);

  const [pickControl, setPickControl] = useState("");
  const [pickEff, setPickEff] = useState(3);

  async function refresh() {
    try {
      const [r, a, c, allC] = await Promise.all([
        api.risks.get(id),
        api.assessments.list(id),
        api.riskControls.list(id),
        api.controls.list(),
      ]);
      setRisk(r);
      setAssessments(a);
      setControls(c);
      setAllControls(allC.items);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    refresh();
  }, [id]);

  const quantitative = assessments.find((a) => a.kind === "quantitative");

  async function submitQualitative() {
    setBusy(true);
    setError(null);
    try {
      await api.assessments.qualitative(id, {
        severity: qSev,
        probability: qProb,
      });
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function submitQuantitative() {
    setBusy(true);
    setError(null);
    try {
      await api.assessments.quantitative(id, {
        loss_min: lossMin,
        loss_mode: lossMode,
        loss_max: lossMax,
        freq_min: freqMin,
        freq_max: freqMax,
        iterations,
      });
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function mapControl() {
    if (!pickControl) return;
    setBusy(true);
    setError(null);
    try {
      await api.riskControls.map(id, pickControl, pickEff);
      setPickControl("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function unmapControl(controlId: string) {
    setBusy(true);
    setError(null);
    try {
      await api.riskControls.unmap(id, controlId);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!risk) {
    return (
      <div className="max-w-5xl mx-auto">
        {error ? (
          <div className="text-red-600 text-sm">{error}</div>
        ) : (
          <div className="text-sm text-slate-500">Loading…</div>
        )}
      </div>
    );
  }

  const availableControls = allControls.filter(
    (c) => !controls.some((mc) => mc.id === c.id)
  );

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <Link
          href="/risks"
          className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
        >
          <ArrowLeft className="w-4 h-4" /> Risk register
        </Link>
      </div>

      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{risk.name}</h1>
          <div className="text-sm text-slate-500">
            {risk.category} · S{risk.severity} × P{risk.probability} = {risk.score}
          </div>
          {risk.description && (
            <p className="text-sm text-slate-700 mt-2">{risk.description}</p>
          )}
        </div>
        <Badge
          className={
            risk.score >= 16
              ? "bg-red-500"
              : risk.score >= 9
              ? "bg-amber-500"
              : "bg-emerald-500"
          }
        >
          {risk.status}
        </Badge>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Qualitative assessment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Severity (1-5)</label>
                <Input
                  type="number"
                  min={1}
                  max={5}
                  value={qSev}
                  onChange={(e) => setQSev(Number(e.target.value))}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-600">Probability (1-5)</label>
                <Input
                  type="number"
                  min={1}
                  max={5}
                  value={qProb}
                  onChange={(e) => setQProb(Number(e.target.value))}
                />
              </div>
            </div>
            <Button onClick={submitQualitative} disabled={busy}>
              Save qualitative
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Quantitative (FAIR Monte Carlo)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-3 gap-2">
              <NumField
                label="Loss min ($)"
                value={lossMin}
                onChange={setLossMin}
              />
              <NumField
                label="Loss mode ($)"
                value={lossMode}
                onChange={setLossMode}
              />
              <NumField
                label="Loss max ($)"
                value={lossMax}
                onChange={setLossMax}
              />
              <NumField
                label="Freq min /yr"
                value={freqMin}
                step={0.01}
                onChange={setFreqMin}
              />
              <NumField
                label="Freq max /yr"
                value={freqMax}
                step={0.01}
                onChange={setFreqMax}
              />
              <NumField
                label="Iterations"
                value={iterations}
                onChange={setIterations}
              />
            </div>
            <Button onClick={submitQuantitative} disabled={busy}>
              Run simulation
            </Button>
          </CardContent>
        </Card>
      </div>

      {quantitative && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Latest quantitative result
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-4 gap-3 text-sm">
              <Stat label="Mean" value={quantitative.loss_mean} />
              <Stat label="P10" value={quantitative.loss_p10} />
              <Stat label="P50" value={quantitative.loss_p50} />
              <Stat label="P90" value={quantitative.loss_p90} />
            </div>
            <LossExceedanceCurve points={quantitative.curve || []} />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Mitigating controls</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {controls.length === 0 ? (
            <div className="text-sm text-slate-500">No controls mapped.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {controls.map((c) => (
                <div
                  key={c.id}
                  className="flex items-center justify-between py-2"
                >
                  <div>
                    <div className="font-medium text-sm">{c.name}</div>
                    <div className="text-xs text-slate-500">
                      {c.control_type} · effectiveness {c.effectiveness}/5
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => unmapControl(c.id)}
                  >
                    Unmap
                  </Button>
                </div>
              ))}
            </div>
          )}
          <div className="border-t border-slate-200 pt-3 flex items-end gap-2">
            <div className="flex-1 space-y-1">
              <label className="text-xs font-medium text-slate-600">
                Map a control
              </label>
              <select
                value={pickControl}
                onChange={(e) => setPickControl(e.target.value)}
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
              >
                <option value="">Select a control…</option>
                {availableControls.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="w-32 space-y-1">
              <label className="text-xs font-medium text-slate-600">
                Effectiveness
              </label>
              <Input
                type="number"
                min={1}
                max={5}
                value={pickEff}
                onChange={(e) => setPickEff(Number(e.target.value))}
              />
            </div>
            <Button onClick={mapControl} disabled={!pickControl || busy}>
              Map
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value?: number | null }) {
  return (
    <div className="rounded-md bg-slate-50 p-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="font-semibold tabular-nums">
        {value == null ? "—" : `$${Math.round(value).toLocaleString()}`}
      </div>
    </div>
  );
}

function NumField({
  label,
  value,
  onChange,
  step,
}: {
  label: string;
  value: number;
  onChange: (n: number) => void;
  step?: number;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-slate-600">{label}</label>
      <Input
        type="number"
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}
