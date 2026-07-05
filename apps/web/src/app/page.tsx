"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import ReactMarkdown from "react-markdown";

interface Msg {
  id: string;
  role: string;
  content: string;
  feedback?: string | null;
  timestamp?: string;
}

export default function Home() {
  const [convId, setConvId] = useState<string | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const convIdRef = useRef<string | null>(null);

  useEffect(() => { convIdRef.current = convId; }, [convId]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, streaming]);

  async function ensureConv(): Promise<string> {
    if (convIdRef.current) return convIdRef.current;
    const res = await fetch("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    const data = await res.json();
    setConvId(data.id);
    return data.id;
  }

  async function send(msg: string) {
    const id = await ensureConv();
    setMsgs((p) => [...p, { id: `u-${Date.now()}`, role: "user", content: msg }]);
    setBusy(true);
    setStreaming("");

    try {
      const res = await fetch(`/api/conversations/${id}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: msg }),
      });
      if (!res.ok) throw new Error("send failed");

      const reader = res.body?.getReader();
      if (!reader) return;
      const dec = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const d = JSON.parse(line.slice(6));
            if (d.done) {
              setBusy(false);
              const r = await fetch(`/api/conversations/${id}`);
              if (r.ok) { const x = await r.json(); setMsgs(x.messages || []); }
            } else {
              setStreaming((p) => p + (d.content || ""));
            }
          } catch {}
        }
      }
    } catch { setBusy(false); }
  }

  async function redo() {
    if (!convIdRef.current || busy) return;
    setBusy(true);
    setStreaming("");

    try {
      const res = await fetch(`/api/conversations/${convIdRef.current}/regenerate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      if (!res.ok) throw new Error("redo failed");

      const reader = res.body?.getReader();
      if (!reader) return;
      const dec = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const d = JSON.parse(line.slice(6));
            if (d.done) {
              setBusy(false);
              const r = await fetch(`/api/conversations/${convIdRef.current}`);
              if (r.ok) { const x = await r.json(); setMsgs(x.messages || []); }
            } else {
              setStreaming((p) => p + (d.content || ""));
            }
          } catch {}
        }
      }
    } catch { setBusy(false); }
  }

  async function feedback(mid: string, fb: "thumbs_up" | "thumbs_down") {
    if (!convIdRef.current) return;
    await fetch(`/api/conversations/${convIdRef.current}/messages/${mid}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback: fb }),
    });
    setMsgs((p) => p.map((m) => (m.id === mid ? { ...m, feedback: fb } : m)));
  }

  function handleSubmit(e?: FormEvent) {
    if (e) e.preventDefault();
    const t = input.trim();
    if (!t || busy) return;
    setInput("");
    send(t);
    if (inputRef.current) inputRef.current.style.height = "auto";
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  }

  function adjust() {
    const el = inputRef.current;
    if (el) { el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 150) + "px"; }
  }

  async function newChat() {
    setConvId(null);
    convIdRef.current = null;
    setMsgs([]);
    setStreaming("");
    setBusy(false);
  }

  return (
    <div className="h-dvh flex flex-col bg-[#0a0a0b]">
      {/* header */}
      <div className="flex items-center justify-between px-4 h-12 border-b border-[#2c2c30] bg-[#141416] shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-[#6c5ce7] flex items-center justify-center text-[10px] font-bold">N</div>
          <span className="text-sm font-medium">Nova</span>
        </div>
        <button onClick={newChat} className="text-xs text-[#636366] hover:text-white px-2 py-1 rounded hover:bg-[#1c1c1f] transition-colors">+ New</button>
      </div>

      {/* messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {msgs.length === 0 && !busy && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="w-14 h-14 rounded-2xl bg-[#6c5ce7]/10 flex items-center justify-center mb-4">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <circle cx="14" cy="14" r="10" stroke="#6c5ce7" strokeWidth="1.5"/>
                <path d="M10 13l4 4 4-4" stroke="#6c5ce7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h1 className="text-xl font-semibold mb-1">Nova</h1>
            <p className="text-sm text-[#636366] mb-6">Unfiltered. Direct. Intelligent.</p>
            <div className="grid grid-cols-1 gap-2 w-full max-w-sm">
              {[
                "Explain quantum computing simply",
                "How to negotiate a higher salary?",
                "Tell me something mind-blowing",
                "Best way to learn a language",
              ].map((ex, i) => (
                <button key={i} onClick={() => { setInput(ex); setTimeout(() => inputRef.current?.focus(), 50); }}
                  className="text-left px-4 py-3 rounded-xl bg-[#1c1c1f] border border-[#2c2c30] text-sm text-[#aeaeb2] hover:border-[#6c5ce7] transition-colors"
                >{ex}</button>
              ))}
            </div>
          </div>
        )}

        {msgs.map((m) => (
          <div key={m.id} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-semibold ${
              m.role === "user" ? "bg-[#2d2640] border border-[#3d3560] text-[#aeaeb2]" : "bg-[#6c5ce7] text-white"
            }`}>
              {m.role === "user" ? "U" : "N"}
            </div>
            <div className={`flex flex-col max-w-[85%] sm:max-w-[75%] ${m.role === "user" ? "items-end" : "items-start"}`}>
              <div className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-[#2d2640] border border-[#3d3560] rounded-tr-md"
                  : "bg-[#1c1c1f] border border-[#2c2c30] rounded-tl-md"
              }`}>
                <div className="prose prose-invert"><ReactMarkdown>{m.content}</ReactMarkdown></div>
              </div>
              {m.role === "assistant" && !busy && (
                <div className="flex items-center gap-2 mt-1.5">
                  <button onClick={() => feedback(m.id, "thumbs_up")}
                    className={`text-xs ${m.feedback === "thumbs_up" ? "text-green-400" : "text-[#636366]"} hover:text-white transition-colors`}>👍</button>
                  <button onClick={() => feedback(m.id, "thumbs_down")}
                    className={`text-xs ${m.feedback === "thumbs_down" ? "text-red-400" : "text-[#636366]"} hover:text-white transition-colors`}>👎</button>
                  <button onClick={redo} className="text-xs text-[#636366] hover:text-white transition-colors">↻</button>
                </div>
              )}
            </div>
          </div>
        ))}

        {busy && (
          <div className="flex gap-3">
            <div className="shrink-0 w-7 h-7 rounded-full bg-[#6c5ce7] flex items-center justify-center text-[10px] font-bold">N</div>
            <div className="bg-[#1c1c1f] border border-[#2c2c30] rounded-2xl rounded-tl-md px-4 py-2.5 max-w-[85%] sm:max-w-[75%]">
              {streaming ? (
                <div className="prose prose-invert text-sm">{streaming}<span className="inline-block w-[3px] h-4 bg-[#6c5ce7] ml-0.5 animate-blink" /></div>
              ) : (
                <div className="flex gap-1 py-1">
                  <span className="w-1.5 h-1.5 bg-[#6c5ce7] rounded-full" style={{ animation: "pulse 1.4s infinite ease-in-out" }} />
                  <span className="w-1.5 h-1.5 bg-[#6c5ce7] rounded-full" style={{ animation: "pulse 1.4s infinite ease-in-out 0.2s" }} />
                  <span className="w-1.5 h-1.5 bg-[#6c5ce7] rounded-full" style={{ animation: "pulse 1.4s infinite ease-in-out 0.4s" }} />
                </div>
              )}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* input */}
      <div className="border-t border-[#2c2c30] bg-[#141416] pb-safe">
        <div className="max-w-2xl mx-auto p-3">
          <form onSubmit={handleSubmit} className="flex items-end gap-2 bg-[#0a0a0b] border border-[#2c2c30] rounded-xl px-3 py-2 focus-within:border-[#6c5ce7] transition-colors">
            <textarea ref={inputRef} value={input} onChange={e => { setInput(e.target.value); adjust(); }}
              onKeyDown={handleKey} placeholder="Message Nova..." rows={1}
              disabled={busy}
              className="flex-1 bg-transparent text-white placeholder-[#636366] outline-none resize-none text-sm py-1 max-h-[150px] disabled:opacity-40"
            />
            <button type="submit" disabled={busy || !input.trim()}
              className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-[#6c5ce7] hover:bg-[#5a4bd1] disabled:bg-[#2c2c30] disabled:text-[#636366] text-white transition-colors text-sm"
            >{busy ? "·" : "→"}</button>
          </form>
        </div>
      </div>
    </div>
  );
}
