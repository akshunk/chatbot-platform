import re
import time
from pathlib import Path

import httpx

from .workflow import MODEL_NAME, create_txt2img_workflow

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = Path("/workspace/ComfyUI/output")
POLL_INTERVAL = 1.0
TIMEOUT = 120

PONY_PREFIX = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, rating_explicit, "
IMG_PATTERN = re.compile(r'<gen>(.+?)</gen>', re.DOTALL)


def enhance_prompt(user_prompt: str) -> str:
    return PONY_PREFIX + user_prompt


def generate_image(prompt: str, negative_prompt: str | None = None) -> str:
    workflow = create_txt2img_workflow(prompt=prompt, negative_prompt=negative_prompt)

    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow})
        resp.raise_for_status()
        result = resp.json()
        prompt_id = result["prompt_id"]

        for _ in range(int(TIMEOUT / POLL_INTERVAL)):
            time.sleep(POLL_INTERVAL)
            hist_resp = client.get(f"{COMFYUI_URL}/history/{prompt_id}")
            if hist_resp.status_code != 200:
                continue
            data = hist_resp.json()
            if isinstance(data, dict) and prompt_id in data:
                outputs = data[prompt_id].get("outputs", {})
                for node_id in outputs:
                    for key in outputs[node_id]:
                        items = outputs[node_id][key]
                        if not isinstance(items, list):
                            continue
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            if item.get("type") != "output":
                                continue
                            subfolder = item.get("subfolder", "")
                            filename = item.get("filename")
                            if not filename:
                                continue
                            return str(OUTPUT_DIR / subfolder / filename)

    raise TimeoutError("Image generation did not complete within 120 seconds")
