import random

MODEL_NAME = "Juggernaut-XL-v9.safetensors"
DEFAULT_NEGATIVE = "(cartoon:1.4), (anime:1.4), (illustration:1.3), (painting:1.3), (drawing:1.3), (digital art:1.3), (3d render:1.3), (cgi:1.3), worst quality, low quality, distorted, blurry, bad anatomy, watermark, text, signature, extra limbs, fused limbs, bad hands, bad feet, ugly, lowres"


def create_txt2img_workflow(
    prompt: str,
    negative_prompt: str | None = None,
    width: int = 1024,
    height: int = 1024,
    seed: int | None = None,
    steps: int = 30,
    cfg: float = 4.5,
    sampler_name: str = "dpmpp_2m",
    scheduler: str = "karras",
    filename_prefix: str = "nova_",
) -> dict:
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    neg = negative_prompt if negative_prompt else DEFAULT_NEGATIVE

    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": MODEL_NAME},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            },
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["4", 1],
            },
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": neg,
                "clip": ["4", 1],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2],
            },
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": filename_prefix,
                "images": ["8", 0],
            },
        },
    }
