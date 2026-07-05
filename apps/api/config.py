from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Chatbot Platform API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    data_dir: str = str(Path(__file__).parent.parent.parent / "data")
    config_dir: str = str(Path(__file__).parent.parent.parent / "config")
    core_dir: str = str(Path(__file__).parent.parent.parent / "core")
    default_provider: str = "ollama"
    default_model: str = "llama3.2:3b"
    default_personality: str = "default"
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_prefix": "CHATBOT_", "extra": "ignore"}


settings = Settings()


def load_yaml_config(filename: str) -> dict:
    path = Path(settings.config_dir) / filename
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}
