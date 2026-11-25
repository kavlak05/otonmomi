from dataclasses import dataclass, field
import os


@dataclass
class SystemConfig:
    host: str = "0.0.0.0"
    http_port: int = int(os.getenv("HTTP_PORT", "8080"))
    ws_port: int = int(os.getenv("WS_PORT", "8765"))
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip()
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    )
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "25"))
    autonomy_interval_sec: int = int(os.getenv("AUTONOMY_INTERVAL_SEC", "45"))
    db_path: str = field(
        default_factory=lambda: os.getenv("DB_PATH", "./data/autonomous_avatar.db").strip()
    )
    avatar_assets_path: str = field(
        default_factory=lambda: os.getenv("AVATAR_ASSETS_PATH", "./meta_human_assets").strip()
    )
    rss_feeds: list[str] = field(
        default_factory=lambda: [
            "https://hnrss.org/frontpage",
            "https://export.arxiv.org/rss/cs.AI",
        ]
    )
    social_topics: list[str] = field(
        default_factory=lambda: [
            "ai",
            "agent",
            "autonomous",
            "llm",
            "robotics",
            "avatar",
        ]
    )


CONFIG = SystemConfig()
