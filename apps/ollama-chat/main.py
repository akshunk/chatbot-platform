#!/usr/bin/env python3
import sys

sys.path.insert(0, "/workspace/chatbot-platform")

import gradio as gr
import httpx
import json
import re

from core.personality import PersonalityBuilder, get_personality_dir, get_personality_model, list_personalities
from core.imagegen.client import generate_image, enhance_prompt

OLLAMA_URL = "http://127.0.0.1:11434"
GEN_TAG = re.compile(r'<gen>(.+?)</gen>', re.DOTALL)
GEN_INTENT = re.compile(r'(?:generate|create|make|draw|render|produce)\s+(?:(?:a|an|the)\s+)?(?:image|photo|picture|render|drawing|art)', re.IGNORECASE)


def has_image_intent(message: str) -> bool:
    return bool(GEN_INTENT.search(message))


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

    if has_image_intent(message):
        messages.append({
            "role": "system",
            "content": "The user wants to generate an image. Provide a detailed visual description in <gen> tags like this: <gen>detailed scene description with pose, lighting, colors, and mood</gen>"
        })

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    # Yield immediately to establish the websocket connection
    yield ""
    # Collect the full LLM response before deciding how to render it
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
    except Exception as e:
        yield f"Error: {e}"
        return

    # Check if image generation is needed
    img_match = GEN_TAG.search(full)
    if img_match:
        prompt = img_match.group(1).strip()
        clean_text = re.sub(r'\s+', ' ', GEN_TAG.sub("", full)).strip()
        if not clean_text:
            clean_text = "Here is your generated image."
        enhanced = enhance_prompt(prompt)
        try:
            image_path = generate_image(enhanced)
            yield f"{clean_text}\n\n<img src=\"/file={image_path}\" style=\"max-width: 100%; border-radius: 8px;\">"
        except Exception as e:
            yield f"{clean_text}\n\n[Image generation failed: {e}]"
    else:
        yield full


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
                print(f"  Warming model: {model}...")
                client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": model, "prompt": "", "stream": False, "keep_alive": "5m"},
                    timeout=120,
                )
                print(f"  {model} ready")
            except Exception as e:
                print(f"  {model} warmup skipped ({e})")


if __name__ == "__main__":
    _warm_models()
    demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=["/workspace/ComfyUI/output"])
