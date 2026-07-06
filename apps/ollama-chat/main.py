#!/usr/bin/env python3
import gradio as gr
import httpx
import json

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "llama3.2:3b"


def to_str(v):
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return to_str(v.get("text", v.get("content", "")))
    if isinstance(v, (list, tuple)):
        return " ".join(to_str(x) for x in v)
    return str(v or "")


def build_messages(message, history):
    msgs = []
    for h in history:
        if isinstance(h, dict):
            msgs.append({"role": h.get("role", "user"), "content": to_str(h.get("content", ""))})
        elif isinstance(h, (list, tuple)) and len(h) >= 2:
            msgs.append({"role": "user", "content": to_str(h[0])})
            msgs.append({"role": "assistant", "content": to_str(h[1])})
    msgs.append({"role": "user", "content": to_str(message)})
    return msgs


async def chat(message, history):
    messages = build_messages(message, history)

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
            if resp.status_code != 200:
                error_body = await resp.aread()
                yield f"Error {resp.status_code}: {error_body.decode()[:200]}"
                return
            full = ""
            async for line in resp.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if data.get("done"):
                    break
                if "message" in data and "content" in data["message"]:
                    full += data["message"]["content"]
                    yield full


demo = gr.ChatInterface(
    chat,
    title="Nova",
    description="Uncensored conversational AI",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
