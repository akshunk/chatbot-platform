import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .conversation import Conversation
from .message import Message


class ConversationHistory:
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.conversations_dir = self.data_dir / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)

    def _conv_path(self, conv_id: str) -> Path:
        return self.conversations_dir / f"{conv_id}.jsonl"

    def create_conversation(
        self,
        title: str = "New Conversation",
        model: str = "",
        provider: str = "",
        personality: str = "default",
    ) -> Conversation:
        conv = Conversation(
            title=title,
            model=model,
            provider=provider,
            personality=personality,
        )
        return conv

    def save_conversation(self, conv: Conversation):
        path = self.conversations_dir / f"{conv.id}.json"
        path.write_text(json.dumps(conv.to_dict(), indent=2))

    def load_conversation(self, conv_id: str) -> Optional[Conversation]:
        path = self.conversations_dir / f"{conv_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return Conversation(**data)

    def list_conversations(self) -> list[Conversation]:
        convs = []
        for path in sorted(self.conversations_dir.glob("*.json"), reverse=True):
            data = json.loads(path.read_text())
            convs.append(Conversation(**data))
        return convs

    def add_message(self, message: Message):
        path = self._conv_path(message.conversation_id)
        with open(path, "a") as f:
            f.write(json.dumps(message.to_dict()) + "\n")

    def get_messages(self, conv_id: str) -> list[Message]:
        path = self._conv_path(conv_id)
        if not path.exists():
            return []
        messages = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append(Message(**json.loads(line)))
        return messages

    def update_message_feedback(self, conv_id: str, msg_id: str, feedback: str):
        messages = self.get_messages(conv_id)
        path = self._conv_path(conv_id)
        with open(path, "w") as f:
            for msg in messages:
                if msg.id == msg_id:
                    msg.feedback = feedback
                f.write(json.dumps(msg.to_dict()) + "\n")

    def delete_conversation(self, conv_id: str):
        json_path = self.conversations_dir / f"{conv_id}.json"
        jsonl_path = self._conv_path(conv_id)
        if json_path.exists():
            json_path.unlink()
        if jsonl_path.exists():
            jsonl_path.unlink()
