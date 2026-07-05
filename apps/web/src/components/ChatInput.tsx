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

  function adjustHeight() {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  }

  function handleSubmit(e?: FormEvent) {
    if (e) e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="border-t border-[#2c2c30] bg-[#141416]">
      <div className="max-w-4xl mx-auto p-4">
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-end gap-2 bg-[#0a0a0b] border border-[#2c2c30] rounded-xl px-3 py-2 focus-within:border-[#6c5ce7] transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => { setInput(e.target.value); adjustHeight(); }}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              rows={1}
              disabled={disabled}
              className="flex-1 bg-transparent text-[#f5f5f7] placeholder-[#636366] resize-none outline-none text-sm py-1.5 max-h-[200px] disabled:opacity-40"
            />
            <button
              type="submit"
              disabled={disabled || !input.trim()}
              className="shrink-0 w-9 h-9 flex items-center justify-center rounded-lg bg-[#6c5ce7] hover:bg-[#5a4bd1] disabled:bg-[#2c2c30] disabled:text-[#636366] text-white transition-colors"
            >
              {disabled ? (
                <svg className="animate-spin" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" opacity="0.3"/>
                  <path d="M14 8A6 6 0 002 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 8l12-6-6 12-2-4-4-2z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round"/>
                </svg>
              )}
            </button>
          </div>
          <p className="text-[10px] text-[#636366] text-center mt-2">
            Nova may produce inaccurate information. Verify important facts.
          </p>
        </form>
      </div>
    </div>
  );
}
