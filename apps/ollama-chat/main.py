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


async def stream_chat(message, history, personality_name):
    messages = build_messages(message, history, personality_name)
    model = get_personality_model(personality_name)

    payload = {
        "model": model,
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
personality_choices = [(f"{p['label']} ({p['name']}) — {p['description']} [{p['model']}]", p["name"]) for p in personalities_list]

CSS = """
html, body, .gradio-container { height: 100vh; margin: 0; padding: 0; overflow: hidden; }
.gradio-container { display: flex; flex-direction: column; }
"""

with gr.Blocks(title="Nova", fill_height=True) as demo:
    gr.Markdown("## Nova")

    personality = gr.Dropdown(
        choices=personality_choices,
        value=personality_choices[0][1],
        label="Personality",
        interactive=True,
        allow_custom_value=False,
    )

    chatbot = gr.Chatbot(
        label="Chat",
        render_markdown=True,
        autoscroll=False,
        height=None,
    )

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Type a message...",
            show_label=False,
            container=False,
            scale=9,
        )
        send = gr.Button("Send", variant="primary", scale=1)

    async def respond(user_msg, chat_history, personality_name):
        if chat_history is None:
            chat_history = []
        if not user_msg:
            yield "", chat_history
            return
        chat_history.append([user_msg, None])
        yield "", chat_history
        full = ""
        async for chunk in stream_chat(user_msg, chat_history[:-1], personality_name):
            full = chunk
            chat_history[-1] = [user_msg, full]
            yield "", chat_history

    send.click(respond, [msg, chatbot, personality], [msg, chatbot])
    msg.submit(respond, [msg, chatbot, personality], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, css=CSS)
