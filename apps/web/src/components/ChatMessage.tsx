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

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-[#2e1065] text-white rounded-br-md"
            : "bg-[#1e1e1e] text-[#e8e8e8] rounded-bl-md border border-[#333]"
        }`}
      >
        <div className="text-xs font-medium mb-1 opacity-60">
          {isUser ? "You" : "Nova"}
        </div>
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        {!isUser && (
          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-[#333]">
            <button
              onClick={handleCopy}
              className="text-xs text-[#666] hover:text-white transition-colors"
              title="Copy"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
            <button
              onClick={() => onFeedback(message.id, "thumbs_up")}
              className={`text-xs transition-colors ${
                message.feedback === "thumbs_up"
                  ? "text-green-400"
                  : "text-[#666] hover:text-white"
              }`}
              title="Good response"
            >
              👍
            </button>
            <button
              onClick={() => onFeedback(message.id, "thumbs_down")}
              className={`text-xs transition-colors ${
                message.feedback === "thumbs_down"
                  ? "text-red-400"
                  : "text-[#666] hover:text-white"
              }`}
              title="Bad response"
            >
              👎
            </button>
            {onRegenerate && (
              <button
                onClick={onRegenerate}
                className="text-xs text-[#666] hover:text-white transition-colors ml-auto"
                title="Regenerate"
              >
                🔄 Regenerate
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
