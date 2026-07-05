from typing import Optional

from .base import BaseLLMProvider
from .ollama import OllamaProvider
from .groq import GroqProvider
from .openrouter import OpenRouterProvider
from .openai_compatible import OpenAICompatibleProvider


class LLMRouter:
    def __init__(self, providers_config: dict):
        self.providers_config = providers_config
        self._providers: dict[str, BaseLLMProvider] = {}

    def _build_provider(self, name: str, config: dict) -> BaseLLMProvider:
        provider_type = config.get("type", "").lower()
        if provider_type == "ollama":
            return OllamaProvider(config)
        elif provider_type == "groq":
            return GroqProvider(config)
        elif provider_type == "openrouter":
            return OpenRouterProvider(config)
        elif provider_type == "openai_compatible":
            return OpenAICompatibleProvider(config)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        if name is None:
            name = self.providers_config.get("default", list(self.providers_config.keys())[0])
        if name not in self._providers:
            config = self.providers_config.get(name)
            if config is None:
                raise ValueError(f"Provider '{name}' not found in config")
            self._providers[name] = self._build_provider(name, config)
        return self._providers[name]
