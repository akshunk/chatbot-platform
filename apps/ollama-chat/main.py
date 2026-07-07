#!/usr/bin/env python3
import sys

sys.path.insert(0, "/workspace/chatbot-platform")

import gradio as gr
import httpx
import json
import re

from core.personality import PersonalityBuilder, get_personality_dir, get_personality_model, list_personalities
from core.imagegen.client import generate_image, enhance_prompt
from core.imagegen.workflow import DEFAULT_NEGATIVE

OLLAMA_URL = "http://127.0.0.1:11434"
GEN_TAG = re.compile(r'<gen>(.+?)</gen>', re.DOTALL)
GEN_INTENT = re.compile(r'(?:generate|create|make|draw|render|produce)\s+(?:(?:a|an|the)\s+)?(?:image|photo|picture|render|drawing|art)', re.IGNORECASE)

ANIMAL_KEYWORDS = {
    "deer", "dog", "cat", "horse", "bird", "rabbit", "wolf", "bunny", "puppy", "kitten",
    "animal", "animals", "lion", "tiger", "bear", "fox", "elephant", "monkey", "ape",
    "gorilla", "zebra", "giraffe", "panda", "koala", "kangaroo", "owl", "eagle", "hawk",
    "fish", "shark", "whale", "dolphin", "seal", "pig", "cow", "sheep", "goat", "duck",
    "chicken", "frog", "snake", "lizard", "turtle", "mouse", "rat", "hamster", "parrot",
    "swan", "goose", "butterfly", "bat", "squirrel", "beaver", "otter", "moose", "elk",
    "bison", "rhino", "hippo", "gator", "crocodile", "alligator", "cheetah", "leopard",
    "panther", "jaguar", "cougar", "puma", "lynx", "bobcat", "hyena", "coyote", "dingo",
    "ferret", "meerkat", "warthog", "boar", "hog", "sloth", "tapir", "capybara", "marmot",
    "hedgehog", "platypus", "wombat", "possum", "penguin", "seagull", "crow", "raven",
    "sparrow", "robin", "pigeon", "dove", "falcon", "hawk", "buzzard", "vulture", "stork",
    "heron", "crane", "pelican", "flamingo", "parrot", "macaw", "cockatoo", "finch",
    "canary", "budgie", "parakeet", "lovebird", "hummingbird", "woodpecker", "kingfisher",
    "kookaburra", "rooster", "hen", "turkey", "peacock", "pheasant", "quail", "emu",
    "ostrich", "kiwi", "puffin", "albatross", "gull", "tern", "swallow", "swift",
    "goldfish", "koi", "betta", "guppy", "molly", "tetra", "cichlid", "angelfish",
    "clownfish", "tang", "damsel", "wrasse", "bass", "trout", "salmon", "tuna", "cod",
    "halibut", "flounder", "catfish", "eel", "stingray", "manta ray", "jellyfish",
    "octopus", "squid", "cuttlefish", "starfish", "sea horse", "sea urchin", "coral",
    "anemone", "lobster", "crab", "shrimp", "prawn", "crayfish", "mussel", "clam",
    "oyster", "scallop", "snail", "slug", "worm", "leech", "centipede", "millipede",
    "spider", "scorpion", "tick", "mite", "ant", "bee", "wasp", "hornet", "termite",
    "cockroach", "beetle", "ladybug", "firefly", "dragonfly", "damselfly", "grasshopper",
    "cricket", "locust", "cicada", "aphid", "mantis", "mosquito", "fly", "moth",
    "caterpillar", "butterfly", "larva", "pupa", "chrysalis",
}

HARMFUL_KEYWORDS = {
    "child", "minor", "underage", "kid", "baby", "infant", "toddler", "teen", "teenager",
    "girl", "boy", "young", "childhood",
}

VIOLENT_KEYWORDS = {
    "gore", "blood", "bloody", "violence", "violent", "torture", "murder", "kill",
    "killing", "death", "dead body", "corpse", "dismember", "mutilate", "mutilation",
    "execution", "beheading", "decapitation", "crucifixion", "burning alive",
    "suffocation", "strangulation", "stab", "stabbing", "shoot", "shooting",
    "gunshot", "wound", "injury", "injured", "surgery", "operation", "medical procedure",
    "autopsy", "dissection", "open wound", "flesh wound", "exposed muscle",
    "skeleton", "skull", "bones", "broken bone", "fracture",
}

EXPLICIT_KEYWORDS = {
    "naked", "nude", "explicit", "erotic", "nsfw", "sex", "sexual", "penis", "vagina",
    "breasts", "nipples", "genitals", "pussy", "dick", "cock", "cum", "semen",
    "ejaculate", "orgasm", "climax", "fuck", "suck", "blowjob", "handjob",
    "fingering", "penetration", "intercourse", "foreplay", "masturbate",
    "masturbation", "striptease", "lingerie", "thong", "g-string", "dildo",
    "vibrator", "anal", "oral", "vaginal", "bondage", "bdsm", "domination",
    "submission", "fetish", "kink", "hardcore", "porn", "pornographic", "lewd",
    "seductive", "provocative", "sultry", "sensual", "intimate", "caress",
    "fondle", "lick", "moan", "thrust", "horny", "aroused", "lust", "lustful",
    "passion", "passionate", "nakedness", "nudity", "bare", "exposed",
    "revealing", "scantily", "topless", "bottomless", "undress", "undressed",
    "stripped", "stripping",
}


def is_safe_prompt(prompt: str) -> tuple[bool, str | None]:
    lower = prompt.lower()
    words = set(lower.replace(",", "").replace(".", "").split())

    # Block: child/minor + explicit or violent
    if words & HARMFUL_KEYWORDS:
        if words & EXPLICIT_KEYWORDS or words & VIOLENT_KEYWORDS:
            return False, "Cannot generate images involving minors in explicit or violent contexts."

    # Block: animal + explicit
    if words & ANIMAL_KEYWORDS and words & EXPLICIT_KEYWORDS:
        return False, "Cannot generate explicit images of animals."

    # Block: any occurrence of harmful child keywords
    child_explicit = {"child", "minor", "underage", "kid", "baby", "infant", "toddler"}
    if lower.startswith("photograph of a ") or lower.startswith("photo of a "):
        first_word = lower.split()[-1] if len(lower.split()) <= 5 else ""
        if words & child_explicit and (words & EXPLICIT_KEYWORDS or words & VIOLENT_KEYWORDS):
            return False, "Cannot generate images involving minors in explicit or violent contexts."

    return True, None


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
    if has_image_intent(message):
        msgs.append({
            "role": "system",
            "content": "The user wants to generate an image. Output a short comma-separated prompt in <gen> tags. Start with 'photograph of' or 'photo of'. Use keywords, not prose. Under 30 words. Example: <gen>photograph of a woman, soft window lighting, detailed skin, shallow depth of field, candid expression, 8k</gen>"
        })
    return msgs + build_chat_messages(message, history)


def chat(message, history, personality_name):
    messages = build_messages(message, history, personality_name)
    model = get_personality_model(personality_name)

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
        # Strip common role prefixes the LLM sometimes outputs
        clean_text = re.sub(r'^(assistant|nova|ai)\s*[:\-]?\s*', '', clean_text, flags=re.IGNORECASE).strip()
        if not clean_text:
            clean_text = "Here is your generated image."

        # Safety filter
        safe, reason = is_safe_prompt(prompt)
        if not safe:
            yield f"{reason}"
            return

        enhanced = enhance_prompt(prompt)
        try:
            image_path = generate_image(enhanced, negative_prompt=DEFAULT_NEGATIVE)
            yield f"{clean_text}\n\n<img src=\"/gradio_api/file={image_path}\" style=\"max-width: 100%; border-radius: 8px;\">"
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
    import threading
    threading.Thread(target=_warm_models, daemon=True).start()
    demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=["/workspace/ComfyUI/output"])
