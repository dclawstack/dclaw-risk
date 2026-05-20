"use client";

import { useEffect, useState } from "react";
import { RefreshCw, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

type Signal = Awaited<ReturnType<typeof api.emerging.list>>["items"][number];

export default function EmergingPage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [feeds, setFeeds] = useState<string[]>([]);
  const [feed, setFeed] = useState("nvd-cve");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  async function refresh() {
    try {
      const data = await api.emerging.list();
      setSignals(data.items);
      setFeeds(data.feeds);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function pull() {
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const res = await api.emerging.refresh(feed, 10);
      setInfo(`Fetched ${res.fetched} signal(s) from ${res.feed}, ${res.new} new.`);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Emerging risk</h1>
          <p className="text-sm text-slate-600">
            Pull signals from external feeds. Default: NIST NVD CVE 2.0 (last 7
            days).
          </p>
        </div>
        <div className="flex items-end gap-2">
          <div>
            <label className="text-xs font-medium text-slate-600">Feed</label>
            <select
              value={feed}
              onChange={(e) => setFeed(e.target.value)}
              className="block w-40 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
            >
              {feeds.length === 0 ? (
                <option value="nvd-cve">nvd-cve</option>
              ) : (
                feeds.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))
              )}
            </select>
          </div>
          <Button onClick={pull} disabled={busy}>
            <RefreshCw className="w-4 h-4 mr-1" />
            {busy ? "Pulling…" : "Pull feed"}
          </Button>
        </div>
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

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {signals.length} signal{signals.length === 1 ? "" : "s"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {signals.length === 0 ? (
            <div className="text-sm text-slate-500">
              No signals yet — click Pull feed to fetch.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {signals.map((s) => (
                <div key={s.id} className="py-3 flex justify-between gap-3">
                  <div className="min-w-0">
                    <div className="font-medium truncate">
                      {s.title}{" "}
                      {s.url && (
                        <a
                          href={s.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-emerald-600 hover:text-emerald-700 inline-flex"
                          aria-label="External link"
                        >
                          <ExternalLink className="w-3.5 h-3.5 inline" />
                        </a>
                      )}
                    </div>
                    <div className="text-xs text-slate-500">
                      {s.source} ·{" "}
                      {new Date(s.detected_at).toLocaleString()}
                    </div>
                    {s.summary && (
                      <div className="text-xs text-slate-600 mt-1 line-clamp-2">
                        {s.summary}
                      </div>
                    )}
                  </div>
                  <Badge
                    className={
                      s.impact_score >= 5
                        ? "bg-red-500"
                        : s.impact_score >= 4
                        ? "bg-amber-500"
                        : "bg-emerald-500"
                    }
                  >
                    impact {s.impact_score}/5
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
