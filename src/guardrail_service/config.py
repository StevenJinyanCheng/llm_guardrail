from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env if present


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    guard_model: str = "gpt-4o-mini"  # small/cheap classifier
    main_model: str = "gpt-4o"        # larger model for final response
    temperature: float = 0.0

    # Business rules
    max_length: int = 500
    banned_words: List[str] = field(
        default_factory=lambda: "weather, joke, horoscope".split(", ")
    )  # example: only allow healthcare/investigation prompts, etc.


def get_settings() -> Settings:
    return Settings(openai_api_key=os.environ.get("OPENAI_API_KEY", ""))
