"use client";

import { useState } from "react";
import { Bot, Send, X } from "lucide-react";
import { api, type ChatMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function RiskCopilot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi — I'm the DClaw Risk Copilot. Ask me to identify risks, suggest mitigations, or explain a score.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState<string | null>(null);

  async function send() {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    const next: ChatMessage[] = [...messages, { role: "user", content: trimmed }];
    setMessages(next);
    setInput("");
    setLoading(true);
    try {
      const res = await api.ai.chat(
        next.filter((m) => m.role !== "assistant" || messages.indexOf(m) > 0)
      );
      setMessages([...next, { role: "assistant", content: res.reply }]);
      setProvider(res.provider);
    } catch (e) {
      setMessages([
        ...next,
        {
          role: "assistant",
          content: `Copilot is unavailable: ${String(e)}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-6 right-6 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg w-14 h-14 flex items-center justify-center z-40"
        aria-label="Toggle Risk Copilot"
      >
        {open ? <X className="w-6 h-6" /> : <Bot className="w-6 h-6" />}
      </button>
      <div
        className={cn(
          "fixed bottom-24 right-6 w-96 max-w-[calc(100vw-2rem)] bg-white rounded-xl shadow-2xl border border-slate-200 z-40 flex flex-col transition-all",
          open ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"
        )}
        style={{ height: "min(560px, 70vh)" }}
      >
        <header className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-emerald-600" />
            <div className="font-semibold text-sm">Risk Copilot</div>
          </div>
          {provider && (
            <div className="text-xs text-slate-400">{provider}</div>
          )}
        </header>
        <div className="flex-1 overflow-y-auto p-3 space-y-3 text-sm">
          {messages.map((m, i) => (
            <div
              key={i}
              className={cn(
                "rounded-lg px-3 py-2 max-w-[85%] whitespace-pre-wrap",
                m.role === "user"
                  ? "bg-emerald-600 text-white ml-auto"
                  : "bg-slate-100 text-slate-800"
              )}
            >
              {m.content}
            </div>
          ))}
          {loading && (
            <div className="bg-slate-100 text-slate-500 italic rounded-lg px-3 py-2 max-w-[85%]">
              Thinking…
            </div>
          )}
        </div>
        <form
          className="border-t border-slate-200 p-2 flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
        >
          <input
            className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500"
            placeholder="Ask about risks, controls, or mitigations…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <Button type="submit" disabled={loading || !input.trim()} size="sm">
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </>
  );
}
