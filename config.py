from dataclasses import dataclass, field
import os

@dataclass
class SystemConfig:
    host: str = "127.0.0.1"
    ws_port: int = 8765
    http_port: int = 8080
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    voice_model: str = "tts-1"
    reasoning_model: str = "gpt-4o"
    avatar_assets_path: str = "./meta_human_assets"

CONFIG = SystemConfig()
