"use client";

import { useEffect, useState } from "react";
import { Plus, Search, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Doc = Awaited<ReturnType<typeof api.documents.list>>["items"][number];
type Hit = Awaited<ReturnType<typeof api.documents.search>>["hits"][number];

export default function KnowledgePage() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [title, setTitle] = useState("");
  const [source, setSource] = useState("");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[] | null>(null);

  async function refresh() {
    try {
      const data = await api.documents.list();
      setDocs(data.items);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function add() {
    if (!title || !content) return;
    setBusy(true);
    try {
      await api.documents.create({
        title,
        content,
        source: source || undefined,
      });
      setTitle("");
      setSource("");
      setContent("");
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await api.documents.delete(id);
      setDocs((d) => d.filter((x) => x.id !== id));
    } catch (e) {
      setError(String(e));
    }
  }

  async function search() {
    if (!q) return;
    try {
      const res = await api.documents.search(q);
      setHits(res.hits);
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Knowledge base</h1>
        <p className="text-sm text-slate-600">
          Documents the Copilot retrieves from (TF-IDF). New documents become
          available to the chat immediately.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add document</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Title</label>
              <Input value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-600">Source (optional)</label>
              <Input value={source} onChange={(e) => setSource(e.target.value)} />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-600">Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm font-mono"
              rows={6}
            />
          </div>
          <Button onClick={add} disabled={!title || !content || busy}>
            <Plus className="w-4 h-4 mr-1" /> Add
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Test retrieval</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex gap-2">
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Type a Copilot question to preview the retrieved passages"
            />
            <Button onClick={search} disabled={!q}>
              <Search className="w-4 h-4 mr-1" /> Search
            </Button>
          </div>
          {hits && (
            <div className="text-sm space-y-1">
              {hits.length === 0 ? (
                <div className="text-slate-500">No matches.</div>
              ) : (
                hits.map((h) => (
                  <div key={h.document_id} className="border-l-2 border-emerald-400 pl-2">
                    <div className="font-medium">
                      {h.title}{" "}
                      <span className="text-xs text-slate-400">score {h.score}</span>
                    </div>
                    <div className="text-xs text-slate-600">{h.snippet}</div>
                  </div>
                ))
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {docs.length === 0 ? (
            <div className="text-sm text-slate-500">No documents yet.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {docs.map((d) => (
                <div
                  key={d.id}
                  className="flex items-center justify-between py-3 gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium truncate">{d.title}</div>
                    <div className="text-xs text-slate-500">
                      {d.source ? `${d.source} · ` : ""}
                      {d.excerpt.slice(0, 120)}…
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => remove(d.id)}>
                    <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-600" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
