"use client";

import { useEffect, useState } from "react";
import { Plus, Send, CheckCircle2, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type Survey = Awaited<ReturnType<typeof api.culture.listSurveys>>["items"][number];
type Score = Awaited<ReturnType<typeof api.culture.listScores>>["items"][number];

const PRESET_QS = [
  { dimension: "Speak-up", prompt: "I feel safe raising risk concerns." },
  { dimension: "Tone-at-top", prompt: "Leadership models risk-aware behaviour." },
  { dimension: "Accountability", prompt: "We follow through on identified risks." },
];

export default function CulturePage() {
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [scores, setScores] = useState<Score[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [name, setName] = useState("");
  const [period, setPeriod] = useState("2026-Q2");
  const [questions, setQuestions] =
    useState<typeof PRESET_QS>(PRESET_QS);

  const [activeSurvey, setActiveSurvey] = useState<Survey | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});

  async function refresh() {
    try {
      const [s, sc] = await Promise.all([
        api.culture.listSurveys(),
        api.culture.listScores(),
      ]);
      setSurveys(s.items);
      setScores(sc.items);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function createSurvey() {
    if (!name) return;
    setBusy(true);
    try {
      await api.culture.createSurvey({
        name,
        period,
        questions: questions.map((q, i) => ({ ...q, order_index: i })),
      });
      setName("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function openSurvey(id: string) {
    setBusy(true);
    try {
      await api.culture.openSurvey(id);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function closeSurvey(id: string) {
    setBusy(true);
    try {
      const res = await api.culture.closeSurvey(id);
      setError(null);
      await refresh();
      alert(
        `Closed. ${res.responses_total} response(s) → ${res.dimensions_scored} dimension score(s).`
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function submitResponse() {
    if (!activeSurvey) return;
    setBusy(true);
    try {
      const payload = {
        respondent_hash: Math.random().toString(36).slice(2, 14),
        answers: activeSurvey.questions.map((q) => ({
          question_id: q.id,
          score: answers[q.id] ?? 50,
        })),
      };
      await api.culture.submitSurvey(activeSurvey.id, payload);
      setActiveSurvey(null);
      setAnswers({});
      alert("Response submitted.");
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    setBusy(true);
    try {
      await api.culture.deleteSurvey(id);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Risk culture</h1>
        <p className="text-sm text-slate-600">
          Publish surveys, collect responses, and let the platform aggregate
          dimensional culture scores automatically.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">New survey</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Name</label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Period</label>
              <Input value={period} onChange={(e) => setPeriod(e.target.value)} />
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-xs font-medium text-slate-600">Questions</div>
            {questions.map((q, i) => (
              <div key={i} className="grid grid-cols-3 gap-2">
                <Input
                  value={q.dimension}
                  onChange={(e) => {
                    const next = [...questions];
                    next[i] = { ...q, dimension: e.target.value };
                    setQuestions(next);
                  }}
                />
                <Input
                  className="col-span-2"
                  value={q.prompt}
                  onChange={(e) => {
                    const next = [...questions];
                    next[i] = { ...q, prompt: e.target.value };
                    setQuestions(next);
                  }}
                />
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setQuestions((qs) => [
                  ...qs,
                  { dimension: "", prompt: "" },
                ])
              }
            >
              Add question
            </Button>
          </div>
          <Button onClick={createSurvey} disabled={!name || busy}>
            <Plus className="w-4 h-4 mr-1" /> Create
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Surveys</CardTitle>
        </CardHeader>
        <CardContent>
          {surveys.length === 0 ? (
            <div className="text-sm text-slate-500">No surveys yet.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {surveys.map((s) => (
                <div key={s.id} className="py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="font-medium">{s.name}</div>
                    <div className="text-xs text-slate-500">
                      {s.period} · {s.questions.length} question(s) ·{" "}
                      <Badge variant="secondary">{s.status}</Badge>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {s.status === "draft" && (
                      <Button size="sm" onClick={() => openSurvey(s.id)} disabled={busy}>
                        Open
                      </Button>
                    )}
                    {s.status === "open" && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setActiveSurvey(s);
                            setAnswers(
                              Object.fromEntries(s.questions.map((q) => [q.id, 50]))
                            );
                          }}
                        >
                          Take
                        </Button>
                        <Button size="sm" onClick={() => closeSurvey(s.id)} disabled={busy}>
                          <CheckCircle2 className="w-4 h-4 mr-1" /> Close
                        </Button>
                      </>
                    )}
                    <Button variant="ghost" size="sm" onClick={() => remove(s.id)}>
                      <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {activeSurvey && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Take: {activeSurvey.name}</CardTitle>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setActiveSurvey(null)}
            >
              Cancel
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {activeSurvey.questions.map((q) => (
              <div key={q.id} className="space-y-1">
                <div className="text-sm">
                  <span className="text-xs text-emerald-700 mr-2">
                    {q.dimension}
                  </span>
                  {q.prompt}
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={answers[q.id] ?? 50}
                    onChange={(e) =>
                      setAnswers((a) => ({ ...a, [q.id]: Number(e.target.value) }))
                    }
                    className="flex-1"
                  />
                  <span className="text-xs tabular-nums w-10 text-right">
                    {answers[q.id] ?? 50}
                  </span>
                </div>
              </div>
            ))}
            <Button onClick={submitResponse} disabled={busy}>
              <Send className="w-4 h-4 mr-1" /> Submit
            </Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Aggregated dimension scores</CardTitle>
        </CardHeader>
        <CardContent>
          {scores.length === 0 ? (
            <div className="text-sm text-slate-500">
              No scores yet — close a survey to aggregate responses.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {scores.map((s) => (
                <div key={s.id} className="py-2 flex justify-between text-sm">
                  <div>
                    <span className="text-xs text-slate-500 mr-2">{s.period}</span>
                    {s.dimension}
                  </div>
                  <div className="font-semibold tabular-nums">{s.score}</div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
