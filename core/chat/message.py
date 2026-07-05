from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{datetime.now(timezone.utc).timestamp()}")
    conversation_id: str
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sources: Optional[list[dict]] = None
    feedback: Optional[str] = None

    model_config = {"extra": "allow"}

    def to_dict(self) -> dict:
        return self.model_dump(exclude={"timestamp"}) | {
            "timestamp": self.timestamp.isoformat()
        }
