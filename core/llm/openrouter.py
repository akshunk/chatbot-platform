from .openai_compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    def __init__(self, config: dict):
        config.setdefault("base_url", "https://openrouter.ai/api/v1")
        super().__init__(config)
        self.client.headers["HTTP-Referer"] = config.get(
            "site_url", "http://localhost:3000"
        )
        self.client.headers["X-Title"] = config.get("site_name", "Chatbot Platform")
