#!/usr/bin/env python3
import sys

sys.path.insert(0, "/workspace/chatbot-platform")

import gradio as gr
import httpx
import json

from core.personality import PersonalityBuilder, get_personality_dir, list_personalities

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


def build_chat_messages(message, history):
    msgs = []
    for h in history:
        if isinstance(h, dict):
            msgs.append({"role": h.get("role", "user"), "content": to_str(h.get("content", ""))})
        elif isinstance(h, (list, tuple)) and len(h) >= 2:
            msgs.append({"role": "user", "content": to_str(h[0])})
            msgs.append({"role": "assistant", "content": to_str(h[1])})
    msgs.append({"role": "user", "content": to_str(message)})
    return msgs


def build_messages(message, history, personality_name: str):
    msgs = []
    personality_dir = get_personality_dir(personality_name)
    builder = PersonalityBuilder(personality_dir)
    system_prompt = builder.build_system_prompt()
    if system_prompt:
        msgs.append({"role": "system", "content": system_prompt})
    return msgs + build_chat_messages(message, history)


async def chat(message, history, personality_name):
    messages = build_messages(message, history, personality_name)

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


personalities_list = list_personalities()
personality_choices = [(f"{p['label']} ({p['name']}) — {p['description']}", p["name"]) for p in personalities_list]

demo = gr.ChatInterface(
    chat,
    additional_inputs=[
        gr.Dropdown(
            choices=personality_choices,
            value=personality_choices[0][1],
            label="Personality",
            interactive=True,
            allow_custom_value=False,
        ),
    ],
    additional_inputs_accordion=gr.Accordion(label="Personality", open=True),
    title="Nova",
    description="Conversational AI with selectable personality",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
