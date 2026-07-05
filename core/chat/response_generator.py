from typing import AsyncGenerator, Optional

from core.llm.base import BaseLLMProvider, LLMConfig
from core.llm.router import LLMRouter
from .context_builder import ContextBuilder


class ResponseGenerator:
    def __init__(
        self,
        llm_router: LLMRouter,
        context_builder: ContextBuilder,
        provider_name: Optional[str] = None,
    ):
        self.llm_router = llm_router
        self.context_builder = context_builder
        self.provider_name = provider_name

    def _get_provider(self) -> BaseLLMProvider:
        return self.llm_router.get_provider(self.provider_name)

    async def generate(
        self,
        user_message: str,
        model: str = "default",
        temperature: float = 0.7,
        history: list[dict] | None = None,
        rag_context: str | None = None,
        search_context: str | None = None,
        memory_context: str | None = None,
    ) -> str:
        provider = self._get_provider()
        messages = self.context_builder.build(
            user_message=user_message,
            history=history,
            rag_context=rag_context,
            search_context=search_context,
            memory_context=memory_context,
        )
        config = LLMConfig(model=model, temperature=temperature)
        response = await provider.generate(messages, config)
        return response.content

    async def generate_stream(
        self,
        user_message: str,
        model: str = "default",
        temperature: float = 0.7,
        history: list[dict] | None = None,
        rag_context: str | None = None,
        search_context: str | None = None,
        memory_context: str | None = None,
    ) -> AsyncGenerator[str, None]:
        provider = self._get_provider()
        messages = self.context_builder.build(
            user_message=user_message,
            history=history,
            rag_context=rag_context,
            search_context=search_context,
            memory_context=memory_context,
        )
        config = LLMConfig(model=model, temperature=temperature)
        async for chunk in provider.generate_stream(messages, config):
            yield chunk
