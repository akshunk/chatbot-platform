#!/usr/bin/env python3
import sys

sys.path.insert(0, "/workspace/chatbot-platform")

import gradio as gr
import httpx
import json

from core.personality import PersonalityBuilder, get_personality_dir, get_personality_model, list_personalities

OLLAMA_URL = "http://127.0.0.1:11434"


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


def chat(message, history, personality_name):
    messages = build_messages(message, history, personality_name)
    model = get_personality_model(personality_name)

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    full = ""
    try:
        with httpx.Client(timeout=120) as client:
            with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
                if resp.status_code != 200:
                    yield f"Error {resp.status_code}: {resp.read()[:200]}"
                    return
                for line in resp.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    if data.get("done"):
                        break
                    if "message" in data and "content" in data["message"]:
                        full += data["message"]["content"]
                        yield full
    except Exception as e:
        yield f"Error: {e}"


personalities_list = list_personalities()
personality_choices = [(f"{p['label']} ({p['name']}) — {p['description']} [{p['model']}]", p["name"]) for p in personalities_list]

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
    additional_inputs_accordion=gr.Accordion(label="Personality", open=False),
    title="Nova",
    description="Conversational AI with selectable personality",
)

def _warm_models():
    """Pre-warm all personality models so first chat request doesn't stall on cold load."""
    models = set()
    for p in personalities_list:
        models.add(p["model"])
    with httpx.Client(timeout=120) as client:
        for model in sorted(models):
            try:
                client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": model, "prompt": "", "stream": False, "keep_alive": "5m"},
                    timeout=30,
                )
            except Exception:
                pass  # non-critical; will load on demand


if __name__ == "__main__":
    _warm_models()
    demo.launch(server_name="0.0.0.0", server_port=7860)
