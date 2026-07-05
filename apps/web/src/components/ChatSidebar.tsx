"use client";

import { useEffect, useState } from "react";

interface Conversation {
  id: string;
  title: string;
  updated_at: string;
}

export default function ChatSidebar({
  activeId,
  onSelect,
  onNew,
}: {
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
}) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    fetchConversations();
  }, []);

  async function fetchConversations() {
    try {
      const res = await fetch("/api/conversations");
      if (res.ok) setConversations(await res.json());
    } catch {}
  }

  async function handleDelete(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    await fetch(`/api/conversations/${id}`, { method: "DELETE" });
    setConversations((prev) => prev.filter((c) => c.id !== id));
  }

  return (
    <div className="w-64 bg-[#1a1a1a] border-r border-[#333] flex flex-col h-screen">
      <button
        onClick={onNew}
        className="m-3 p-2.5 bg-[#7c3aed] hover:bg-[#6d28d9] rounded-lg text-white font-medium transition-colors"
      >
        + New Chat
      </button>
      <div className="flex-1 overflow-y-auto px-2 space-y-1">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`p-2.5 rounded-lg cursor-pointer text-sm transition-colors flex justify-between items-center ${
              conv.id === activeId
                ? "bg-[#2e1065] text-white"
                : "text-[#a0a0a0] hover:bg-[#252525] hover:text-white"
            }`}
          >
            <span className="truncate flex-1">{conv.title}</span>
            <button
              onClick={(e) => handleDelete(e, conv.id)}
              className="text-[#666] hover:text-red-400 ml-2 text-xs"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
