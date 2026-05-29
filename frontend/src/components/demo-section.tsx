"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Database, Sparkles, Trash2, ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

type Counts = Awaited<ReturnType<typeof api.demo.status>>["counts"];

const COUNT_LABELS: Array<{ key: keyof Counts; label: string }> = [
  { key: "risks", label: "Risks" },
  { key: "controls", label: "Controls" },
  { key: "risk_controls", label: "Mappings" },
  { key: "assessments", label: "Assessments" },
  { key: "incidents", label: "Incidents" },
  { key: "kris", label: "KRIs" },
  { key: "scenarios", label: "Scenarios" },
  { key: "vendors", label: "Vendors" },
  { key: "emerging", label: "Emerging" },
  { key: "culture", label: "Culture" },
  { key: "surveys", label: "Surveys" },
  { key: "documents", label: "Docs" },
];

export function DemoSection() {
  const [counts, setCounts] = useState<Counts | null>(null);
  const [isEmpty, setIsEmpty] = useState<boolean | null>(null);
  const [busy, setBusy] = useState<"seed" | "clear" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reachable, setReachable] = useState<boolean | null>(null);

  async function refresh() {
    try {
      const s = await api.demo.status();
      setCounts(s.counts);
      setIsEmpty(s.is_empty);
      setReachable(true);
      setError(null);
    } catch (e) {
      setReachable(false);
      setError(String(e));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function seed() {
    setBusy("seed");
    setError(null);
    try {
      const r = await api.demo.seed();
      setCounts(r.counts as Counts);
      setIsEmpty(false);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(null);
    }
  }

  async function clear() {
    setBusy("clear");
    setError(null);
    try {
      const r = await api.demo.clear();
      setCounts(r.removed as Counts);
      // After clear, refresh to get the empty counts
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(null);
    }
  }

  const total =
    counts == null
      ? 0
      : Object.values(counts).reduce((s, v) => s + Number(v || 0), 0);

  return (
    <section
      id="demo"
      className="mx-auto max-w-6xl px-6 py-24"
    >
      <div className="text-center max-w-2xl mx-auto">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 text-emerald-700 px-3 py-1 text-xs font-medium">
          <Database className="w-3.5 h-3.5" />
          Try it live
        </span>
        <h2 className="mt-5 text-3xl md:text-4xl font-bold tracking-tight">
          Seed the demo, click around, wipe it clean.
        </h2>
        <p className="mt-4 text-slate-600">
          One click populates every page — risks, controls, a quantitative
          assessment, KRIs, incidents, a scenario, vendors, an emerging-risk
          signal, a survey, and two indexed documents for the Copilot.
        </p>
      </div>

      <div className="mt-12 rounded-xl border border-slate-200 bg-white p-6 md:p-8 shadow-sm">
        {reachable === false ? (
          <div className="flex items-start gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
            <div>
              <div className="font-medium">Backend not reachable.</div>
              <div className="mt-1 text-amber-800">
                The demo widget calls the FastAPI backend at{" "}
                <code className="rounded bg-amber-100 px-1.5 py-0.5">
                  NEXT_PUBLIC_API_URL
                </code>
                . Run{" "}
                <code className="rounded bg-amber-100 px-1.5 py-0.5">
                  docker compose up
                </code>{" "}
                or start the backend with{" "}
                <code className="rounded bg-amber-100 px-1.5 py-0.5">
                  uvicorn app.api.main:app --port 8155
                </code>
                .
              </div>
              {error && (
                <div className="mt-1 text-xs text-amber-700/80">{error}</div>
              )}
            </div>
          </div>
        ) : (
          <>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <div className="text-sm text-slate-500">Current dataset</div>
                <div className="text-2xl font-semibold tabular-nums">
                  {counts === null ? (
                    <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
                  ) : total === 0 ? (
                    "Empty"
                  ) : (
                    `${total} record${total === 1 ? "" : "s"}`
                  )}
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={seed}
                  disabled={busy !== null}
                  className="inline-flex items-center gap-2 rounded-md bg-emerald-600 px-4 py-2 text-white font-medium hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {busy === "seed" ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  {busy === "seed" ? "Seeding…" : "Seed demo data"}
                </button>
                <Link
                  href="/dashboard"
                  className={
                    "inline-flex items-center gap-2 rounded-md px-4 py-2 font-medium " +
                    (isEmpty === false
                      ? "border border-emerald-600 text-emerald-700 hover:bg-emerald-50"
                      : "border border-slate-300 text-slate-600 hover:bg-slate-50")
                  }
                >
                  View it
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <button
                  onClick={clear}
                  disabled={busy !== null || isEmpty === true}
                  className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-4 py-2 font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Wipes all domain tables"
                >
                  {busy === "clear" ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                  {busy === "clear" ? "Clearing…" : "Clear data"}
                </button>
              </div>
            </div>

            {counts && (
              <div className="mt-6 grid grid-cols-3 md:grid-cols-6 gap-2">
                {COUNT_LABELS.map(({ key, label }) => {
                  const v = counts[key] ?? 0;
                  return (
                    <div
                      key={key}
                      className={
                        "rounded-md border p-2 text-center transition-colors " +
                        (v > 0
                          ? "border-emerald-200 bg-emerald-50"
                          : "border-slate-200 bg-slate-50")
                      }
                    >
                      <div className="text-xs text-slate-500">{label}</div>
                      <div
                        className={
                          "text-lg font-semibold tabular-nums " +
                          (v > 0 ? "text-emerald-700" : "text-slate-400")
                        }
                      >
                        {v}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {error && (
              <div className="mt-4 text-sm text-red-600">{error}</div>
            )}

            <p className="mt-6 text-xs text-slate-500">
              <strong>Heads up:</strong>{" "}
              <span className="text-slate-500">
                Clear deletes <em>everything</em> in the domain tables — not
                just the seeded rows. Use it on a demo database only.
              </span>
            </p>
          </>
        )}
      </div>
    </section>
  );
}
