"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";

interface Message {
  id: string;
  role: string;
  content: string;
  feedback?: string | null;
}

export default function Home() {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  async function loadConversation(id: string) {
    setActiveId(id);
    try {
      const res = await fetch(`/api/conversations/${id}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      }
    } catch {}
  }

  async function handleNew() {
    try {
      const res = await fetch("/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (res.ok) {
        const data = await res.json();
        setActiveId(data.id);
        setMessages([]);
      }
    } catch {}
  }

  const handleSend = useCallback(
    async (content: string) => {
      if (!activeId) return;

      const userMsg: Message = {
        id: `temp-${Date.now()}`,
        role: "user",
        content,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsStreaming(true);
      setStreamingContent("");

      try {
        const res = await fetch(
          `/api/conversations/${activeId}/messages`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content }),
          }
        );

        if (!res.ok) throw new Error("Failed to send");

        const reader = res.body?.getReader();
        if (!reader) return;

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.done) {
                  setIsStreaming(false);
                  loadConversation(activeId);
                } else {
                  setStreamingContent((prev) => prev + (data.content || ""));
                }
              } catch {}
            }
          }
        }
      } catch (err) {
        console.error("Stream error:", err);
        setIsStreaming(false);
      }
    },
    [activeId]
  );

  async function handleFeedback(
    msgId: string,
    feedback: "thumbs_up" | "thumbs_down"
  ) {
    if (!activeId) return;
    try {
      await fetch(
        `/api/conversations/${activeId}/messages/${msgId}/feedback`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ feedback }),
        }
      );
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, feedback } : m))
      );
    } catch {}
  }

  async function handleRegenerate() {
    if (!activeId) return;
    setIsStreaming(true);
    setStreamingContent("");
    try {
      const res = await fetch(
        `/api/conversations/${activeId}/regenerate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        }
      );

      if (!res.ok) throw new Error("Failed to regenerate");

      const reader = res.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.done) {
                setIsStreaming(false);
                loadConversation(activeId);
              } else {
                setStreamingContent((prev) => prev + (data.content || ""));
              }
            } catch {}
          }
        }
      }
    } catch (err) {
      console.error("Regenerate error:", err);
      setIsStreaming(false);
    }
  }

  return (
    <div className="flex h-screen">
      <ChatSidebar
        activeId={activeId}
        onSelect={loadConversation}
        onNew={handleNew}
      />
      <div className="flex-1 flex flex-col">
        {activeId ? (
          <>
            <div className="flex-1 overflow-y-auto p-4">
              <div className="max-w-4xl mx-auto">
                {messages.length === 0 && !isStreaming && (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <h1 className="text-3xl font-bold text-[#e8e8e8] mb-2">
                        Nova
                      </h1>
                      <p className="text-[#666]">
                        Unfiltered. Direct. Intelligent.
                      </p>
                    </div>
                  </div>
                )}
                {messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    message={msg}
                    onFeedback={handleFeedback}
                    onRegenerate={
                      msg.role === "assistant" && !isStreaming
                        ? handleRegenerate
                        : undefined
                    }
                  />
                ))}
                {isStreaming && streamingContent && (
                  <ChatMessage
                    message={{
                      id: "streaming",
                      role: "assistant",
                      content: streamingContent,
                    }}
                    onFeedback={() => {}}
                  />
                )}
                {isStreaming && !streamingContent && (
                  <div className="flex justify-start mb-4">
                    <div className="bg-[#1e1e1e] border border-[#333] rounded-2xl rounded-bl-md px-4 py-3">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-[#7c3aed] rounded-full animate-bounce" />
                        <span className="w-2 h-2 bg-[#7c3aed] rounded-full animate-bounce [animation-delay:0.1s]" />
                        <span className="w-2 h-2 bg-[#7c3aed] rounded-full animate-bounce [animation-delay:0.2s]" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
            <ChatInput onSend={handleSend} disabled={isStreaming} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-[#e8e8e8] mb-3">Nova</h1>
              <p className="text-[#666] mb-6">
                Unfiltered. Direct. Intelligent.
              </p>
              <button
                onClick={handleNew}
                className="bg-[#7c3aed] hover:bg-[#6d28d9] text-white rounded-xl px-6 py-3 font-medium transition-colors"
              >
                Start a conversation
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
