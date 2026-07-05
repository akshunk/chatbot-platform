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
  open,
  onClose,
}: {
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  open: boolean;
  onClose: () => void;
}) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    load();
  }, []);

  async function load() {
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
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`
          fixed md:relative z-50 h-full
          bg-[#141416] border-r border-[#2c2c30]
          transition-transform duration-300 ease-out
          ${open ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
          w-[280px] flex flex-col
        `}
      >
        <div className="p-3 border-b border-[#2c2c30]">
          <button
            onClick={() => { onNew(); onClose(); }}
            className="w-full flex items-center gap-2 px-4 py-2.5 bg-[#6c5ce7] hover:bg-[#5a4bd1] rounded-lg text-white font-medium text-sm transition-colors"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            New chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto scrollbar-thin p-2 space-y-0.5">
          {conversations.length === 0 && (
            <p className="text-[#636366] text-xs text-center py-8">
              No conversations yet
            </p>
          )}
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => { onSelect(conv.id); onClose(); }}
              className={`
                w-full text-left px-3 py-2.5 rounded-lg text-sm flex items-center gap-2.5 transition-colors group
                ${conv.id === activeId
                  ? "bg-[#2d2640] text-white"
                  : "text-[#aeaeb2] hover:bg-[#1c1c1f] hover:text-[#f5f5f7]"
                }
              `}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="shrink-0 opacity-50">
                <path d="M2 4.5A1.5 1.5 0 013.5 3h9A1.5 1.5 0 0114 4.5v7a1.5 1.5 0 01-1.5 1.5h-9A1.5 1.5 0 012 11.5v-7z" stroke="currentColor" strokeWidth="1.2"/>
                <path d="M2 6.5h12" stroke="currentColor" strokeWidth="1.2"/>
              </svg>
              <span className="truncate flex-1">{conv.title}</span>
              <button
                onClick={(e) => handleDelete(e, conv.id)}
                className="shrink-0 opacity-0 group-hover:opacity-100 text-[#636366] hover:text-[#ff4757] transition-all text-xs"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
                </svg>
              </button>
            </button>
          ))}
        </div>

        <div className="p-3 border-t border-[#2c2c30]">
          <div className="flex items-center gap-2.5 px-2">
            <div className="w-7 h-7 rounded-full bg-[#6c5ce7] flex items-center justify-center text-xs font-semibold">
              N
            </div>
            <span className="text-sm text-[#aeaeb2]">Nova</span>
          </div>
        </div>
      </aside>
    </>
  );
}
