from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class SystemConfig:
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    data_dir: Path = field(init=False)
    db_path: Path = field(init=False)
    loop_interval_seconds: int = 30
    max_history_items: int = 500
    request_timeout: int = 10
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    rss_feeds: list[str] = field(default_factory=lambda: [
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://hnrss.org/frontpage",
    ])
    social_topics: list[str] = field(default_factory=lambda: [
        "yapay zeka",
        "otonom sistemler",
        "açık kaynak modeller",
    ])
    web_host: str = "127.0.0.1"
    web_port: int = 8080

    def __post_init__(self) -> None:
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "memory.sqlite3"


CONFIG = SystemConfig()
