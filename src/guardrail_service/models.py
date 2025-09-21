from typing import Optional
from pydantic import BaseModel


class GuardOutput(BaseModel):
    allowed: bool
    reason: Optional[str] = None


class LLMResponse(BaseModel):
    # Keep it simple. Add fields (citations, metadata, etc.) as your app grows.
    answer: str