import re
import sys
sys.path.insert(0, "/workspace/chatbot-platform")

from core.imagegen.workflow import create_txt2img_workflow, MODEL_NAME, DEFAULT_NEGATIVE
from core.imagegen.client import enhance_prompt, IMG_PATTERN


def test_workflow_structure():
    wf = create_txt2img_workflow(prompt="test")
    assert "3" in wf
    assert "4" in wf
    assert "5" in wf
    assert "6" in wf
    assert "7" in wf
    assert "8" in wf
    assert "9" in wf


def test_workflow_model_name():
    wf = create_txt2img_workflow(prompt="test")
    assert wf["4"]["inputs"]["ckpt_name"] == MODEL_NAME


def test_workflow_positive_prompt():
    wf = create_txt2img_workflow(prompt="a cat")
    assert wf["6"]["inputs"]["text"] == "a cat"


def test_workflow_negative_prompt_default():
    wf = create_txt2img_workflow(prompt="test")
    assert wf["7"]["inputs"]["text"] == DEFAULT_NEGATIVE


def test_workflow_custom_negative():
    wf = create_txt2img_workflow(prompt="test", negative_prompt="custom negative")
    assert wf["7"]["inputs"]["text"] == "custom negative"


def test_workflow_image_size():
    wf = create_txt2img_workflow(prompt="test", width=896, height=1152)
    assert wf["5"]["inputs"]["width"] == 896
    assert wf["5"]["inputs"]["height"] == 1152


def test_workflow_seed_deterministic():
    wf1 = create_txt2img_workflow(prompt="test", seed=42)
    wf2 = create_txt2img_workflow(prompt="test", seed=42)
    assert wf1["3"]["inputs"]["seed"] == 42
    assert wf1["3"]["inputs"]["seed"] == wf2["3"]["inputs"]["seed"]


def test_workflow_sampler_params():
    wf = create_txt2img_workflow(prompt="test", steps=30, cfg=10.0, sampler_name="dpmpp_2m", scheduler="karras")
    assert wf["3"]["inputs"]["steps"] == 30
    assert wf["3"]["inputs"]["cfg"] == 10.0
    assert wf["3"]["inputs"]["sampler_name"] == "dpmpp_2m"
    assert wf["3"]["inputs"]["scheduler"] == "karras"


def test_workflow_filename_prefix():
    wf = create_txt2img_workflow(prompt="test", filename_prefix="custom_")
    assert wf["9"]["inputs"]["filename_prefix"] == "custom_"


def test_workflow_node_connections():
    wf = create_txt2img_workflow(prompt="test")
    assert wf["3"]["inputs"]["model"] == ["4", 0]
    assert wf["3"]["inputs"]["positive"] == ["6", 0]
    assert wf["3"]["inputs"]["negative"] == ["7", 0]
    assert wf["3"]["inputs"]["latent_image"] == ["5", 0]
    assert wf["6"]["inputs"]["clip"] == ["4", 1]
    assert wf["7"]["inputs"]["clip"] == ["4", 1]
    assert wf["8"]["inputs"]["samples"] == ["3", 0]
    assert wf["8"]["inputs"]["vae"] == ["4", 2]
    assert wf["9"]["inputs"]["images"] == ["8", 0]


def test_img_pattern_matches_simple():
    text = "Here is <gen>a cat</gen> for you"
    match = IMG_PATTERN.search(text)
    assert match is not None
    assert match.group(1).strip() == "a cat"


def test_img_pattern_matches_complex():
    text = '<gen>a hyper-realistic woman with long dark hair, red dress, studio lighting</gen>'
    match = IMG_PATTERN.search(text)
    assert match is not None
    assert "hyper-realistic" in match.group(1)


def test_img_pattern_no_match():
    text = "Here is a cat for you"
    assert IMG_PATTERN.search(text) is None


def test_img_pattern_multiline():
    text = "The scene:\n<gen>\na woman in red\n</gen>\nis stunning"
    match = IMG_PATTERN.search(text)
    assert match is not None
    assert "woman in red" in match.group(1)


def test_img_pattern_substitution():
    text = "Here is <gen>a cat</gen> for you"
    clean = IMG_PATTERN.sub("", text).strip()
    assert clean == "Here is  for you"


def test_enhance_prompt():
    result = enhance_prompt("a cat")
    assert result.startswith("score_9, score_8_up")
    assert "a cat" in result


def test_enhance_prompt_empty():
    result = enhance_prompt("")
    assert "rating_explicit" in result
