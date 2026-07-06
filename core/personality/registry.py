from pathlib import Path
from typing import Optional

import yaml


_default_config_path = Path(__file__).parent.parent.parent / "config" / "personality.yaml"
_cached: Optional[dict] = None


def _load_config(config_path: Optional[Path] = None) -> dict:
    global _cached
    if _cached is not None:
        return _cached
    path = config_path or _default_config_path
    if not path.exists():
        _cached = {}
        return _cached
    with open(path) as f:
        _cached = yaml.safe_load(f) or {}
    return _cached


def list_personalities() -> list[dict]:
    """Return a list of {name, label, description, model} for UI dropdowns."""
    config = _load_config()
    result = []
    for name, entry in config.items():
        result.append({
            "name": name,
            "label": entry.get("name", name),
            "description": entry.get("description", ""),
            "model": entry.get("model", "llama3.2:3b"),
        })
    return result


def get_personality_model(name: str, config_path: Optional[Path] = None) -> str:
    """Get the model name for a personality."""
    config = _load_config(config_path)
    entry = config.get(name)
    if entry is None:
        raise KeyError(f"Unknown personality: {name!r}")
    return entry.get("model", "llama3.2:3b")


def get_personality_dir(name: str, config_path: Optional[Path] = None) -> Path:
    """Resolve a personality name to its directory path.

    Raises KeyError if the name is unknown.
    """
    config = _load_config(config_path)
    entry = config.get(name)
    if entry is None:
        raise KeyError(f"Unknown personality: {name!r}. Available: {list(config)}")
    raw = entry["directory"]
    path = Path(raw)
    if not path.is_absolute():
        path = _default_config_path.parent.parent / path
    return path.resolve()


def clear_cache():
    """Clear the cached config (useful in tests)."""
    global _cached
    _cached = None
