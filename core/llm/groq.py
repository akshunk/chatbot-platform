from .openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, config: dict):
        config.setdefault("base_url", "https://api.groq.com/openai/v1")
        super().__init__(config)
