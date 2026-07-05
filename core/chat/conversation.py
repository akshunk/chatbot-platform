from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: f"conv_{datetime.now(timezone.utc).timestamp()}")
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model: str = ""
    provider: str = ""
    system_prompt: Optional[str] = None
    personality: str = "default"
    metadata: dict = Field(default_factory=dict)

    def touch(self):
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return self.model_dump(exclude={"created_at", "updated_at"}) | {
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
