from pathlib import Path


class PersonalityBuilder:
    def __init__(self, personality_dir: str | Path):
        self.dir = Path(personality_dir)

    def _read_md(self, filename: str) -> str:
        path = self.dir / filename
        if path.exists():
            return path.read_text().strip()
        return ""

    def identity(self) -> str:
        return self._read_md("identity.md")

    def tone(self) -> str:
        return self._read_md("tone.md")

    def boundaries(self) -> str:
        return self._read_md("boundaries.md")

    def examples(self) -> str:
        return self._read_md("examples.md")

    def build_system_prompt(self) -> str:
        parts = [self.identity(), self.tone(), self.boundaries()]
        examples = self.examples()
        if examples:
            parts.append(f"Here are examples of your conversation style:\n\n{examples}")
        return "\n\n---\n\n".join(p for p in parts if p)
