from core.llm.base import LLMMessage
from core.prompts import PromptBuilder


class ContextBuilder:
    def __init__(self, prompt_builder: PromptBuilder):
        self.prompt_builder = prompt_builder

    def build(
        self,
        user_message: str,
        history: list[dict] | None = None,
        rag_context: str | None = None,
        search_context: str | None = None,
        memory_context: str | None = None,
    ) -> list[LLMMessage]:
        raw_messages = self.prompt_builder.build_messages(
            user_message=user_message,
            history=history,
            rag_context=rag_context,
            search_context=search_context,
            memory_context=memory_context,
        )
        return [
            LLMMessage(role=m["role"], content=m["content"]) for m in raw_messages
        ]
