"use client";

import { useState, FormEvent, useRef, useEffect } from "react";

export default function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (message: string) => void;
  disabled: boolean;
}) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-[#333] p-4 bg-[#1a1a1a]">
      <div className="max-w-4xl mx-auto flex gap-3">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          rows={1}
          disabled={disabled}
          className="flex-1 bg-[#0f0f0f] text-[#e8e8e8] border border-[#333] rounded-xl px-4 py-3 resize-none focus:outline-none focus:border-[#7c3aed] transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="bg-[#7c3aed] hover:bg-[#6d28d9] disabled:bg-[#333] disabled:text-[#666] text-white rounded-xl px-6 py-3 font-medium transition-colors"
        >
          {disabled ? "..." : "Send"}
        </button>
      </div>
    </form>
  );
}
