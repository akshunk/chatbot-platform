"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

interface Message {
  id: string;
  role: string;
  content: string;
  feedback?: string | null;
}

export default function ChatMessage({
  message,
  onFeedback,
  onRegenerate,
}: {
  message: Message;
  onFeedback: (id: string, feedback: "thumbs_up" | "thumbs_down") => void;
  onRegenerate?: () => void;
}) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  function handleCopy() {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function formatTime() {
    const ts = (message as any).timestamp;
    if (!ts) return "";
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  }

  return (
    <div className={`flex items-start gap-3 mb-5 animate-fade-in ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${
          isUser
            ? "bg-[#2d2640] text-[#aeaeb2] border border-[#3d3560]"
            : "bg-[#6c5ce7] text-white"
        }`}
      >
        {isUser ? "U" : "N"}
      </div>

      <div className={`flex flex-col max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`
            rounded-2xl px-4 py-3 text-sm leading-relaxed
            ${isUser
              ? "bg-[#2d2640] border border-[#3d3560] text-[#f5f5f7] rounded-tr-md"
              : "bg-[#1c1c1f] border border-[#2c2c30] text-[#f5f5f7] rounded-tl-md"
            }
          `}
        >
          <div className="prose prose-invert">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        <div className={`flex items-center gap-1.5 mt-1.5 ${isUser ? "flex-row-reverse" : ""}`}>
          <span className="text-[10px] text-[#636366]">{formatTime()}</span>

          {!isUser && (
            <>
              <button
                onClick={handleCopy}
                className="text-[#636366] hover:text-[#aeaeb2] transition-colors p-0.5"
                title="Copy"
              >
                {copied ? (
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M11.667 3.5L5.25 9.917 2.333 7" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : (
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <rect x="4" y="4" width="9" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.2"/>
                    <path d="M10 4V2.5A1.5 1.5 0 008.5 1h-6A1.5 1.5 0 001 2.5v6A1.5 1.5 0 002.5 10H4" stroke="currentColor" strokeWidth="1.2"/>
                  </svg>
                )}
              </button>

              <button
                onClick={() => onFeedback(message.id, "thumbs_up")}
                className={`p-0.5 transition-colors ${
                  message.feedback === "thumbs_up" ? "text-[#2ed573]" : "text-[#636366] hover:text-[#aeaeb2]"
                }`}
                title="Good response"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M4 8.5V4m0 4.5l-2.5-1A1 1 0 011 10.5V11a2 2 0 002 2h5.25a2 2 0 001.8-1.1l1.35-2.7a2 2 0 00.1-.7V7a1.5 1.5 0 00-1.5-1.5H8.5M4 8.5V4m0 0V2a1 1 0 011-1h1.5a1 1 0 011 1v2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>

              <button
                onClick={() => onFeedback(message.id, "thumbs_down")}
                className={`p-0.5 transition-colors ${
                  message.feedback === "thumbs_down" ? "text-[#ff4757]" : "text-[#636366] hover:text-[#aeaeb2]"
                }`}
                title="Bad response"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M10 5.5V10m0-4.5l2.5-1A1 1 0 0113 3.5V3a2 2 0 00-2-2H5.75a2 2 0 00-1.8 1.1L2.6 4.8a2 2 0 00-.1.7V7A1.5 1.5 0 004 8.5H5.5M10 5.5V10m0 0v2a1 1 0 01-1 1H7.5a1 1 0 01-1-1v-2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>

              {onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="p-0.5 text-[#636366] hover:text-[#aeaeb2] transition-colors"
                  title="Regenerate"
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M12 7A5 5 0 113.4 3.4M12 2v3.5H8.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
