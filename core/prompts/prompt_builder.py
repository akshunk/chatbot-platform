from pathlib import Path
from string import Template

from core.personality import PersonalityBuilder


class PromptBuilder:
    def __init__(self, prompts_dir: str | Path, personality_dir: str | Path):
        self.prompts_dir = Path(prompts_dir)
        self.personality = PersonalityBuilder(personality_dir)

    def _read_template(self, name: str) -> str:
        path = self.prompts_dir / name
        if path.exists():
            return path.read_text().strip()
        return ""

    def _render(self, template_name: str, variables: dict | None = None) -> str:
        template_str = self._read_template(template_name)
        if not variables:
            return template_str
        return Template(template_str).safe_substitute(**variables)

    def build_system_prompt(self) -> str:
        system_base = self._render("system.md")
        personality = self.personality.build_system_prompt()
        if system_base and personality:
            return f"{system_base}\n\n{personality}"
        return system_base or personality

    def build_conversation_block(self, history: list[dict]) -> str:
        if not history:
            return ""
        rendered = self._render("conversation.md", {"conversation_history": ""})
        lines = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            label = "User" if role == "user" else "Assistant"
            lines.append(f"{label}: {content}")
        block = "\n\n".join(lines)
        return rendered.replace("{{conversation_history}}", block)

    def build_rag_block(self, rag_context: str | None) -> str:
        if not rag_context:
            return ""
        return self._render("rag.md", {"rag_context": rag_context})

    def build_search_block(self, search_context: str | None) -> str:
        if not search_context:
            return ""
        return self._render("search.md", {"search_context": search_context})

    def build_memory_block(self, memory_context: str | None) -> str:
        if not memory_context:
            return ""
        return self._render("memory.md", {"memory_context": memory_context})

    def build_messages(
        self,
        user_message: str,
        history: list[dict] | None = None,
        rag_context: str | None = None,
        search_context: str | None = None,
        memory_context: str | None = None,
    ) -> list[dict]:
        system = self.build_system_prompt()
        messages = [{"role": "system", "content": system}]

        if history:
            conv_block = self.build_conversation_block(history)
            messages.append({"role": "system", "content": conv_block})

        if rag_context:
            messages.append({"role": "system", "content": self.build_rag_block(rag_context)})

        if search_context:
            messages.append({"role": "system", "content": self.build_search_block(search_context)})

        if memory_context:
            messages.append({"role": "system", "content": self.build_memory_block(memory_context)})

        messages.append({"role": "user", "content": user_message})
        return messages
