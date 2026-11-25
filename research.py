from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


class ResearchEngine:
    def __init__(self, feeds: list[str], timeout: int = 10) -> None:
        self.feeds = feeds
        self.timeout = timeout

    def fetch_feed(self, url: str) -> list[dict[str, str]]:
        req = Request(url, headers={"User-Agent": "AutonomyResearchBot/1.0"})
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw_xml = resp.read()
        except (URLError, TimeoutError, OSError) as exc:
            return [{"title": f"Akış erişim uyarısı: {url}", "summary": str(exc), "link": url}]

        try:
            root = ET.fromstring(raw_xml)
        except ET.ParseError as exc:
            return [{"title": f"XML ayrıştırma uyarısı: {url}", "summary": str(exc), "link": url}]

        items: list[dict[str, str]] = []
        for item in root.findall(".//item")[:5]:
            title = (item.findtext("title") or "").strip()
            summary = (item.findtext("description") or "").strip()
            link = (item.findtext("link") or url).strip()
            if title or summary:
                items.append({
                    "title": title[:200],
                    "summary": summary[:400],
                    "link": link,
                })
        return items

    def scan(self) -> dict[str, Any]:
        collected: list[dict[str, str]] = []
        for feed in self.feeds:
            collected.extend(self.fetch_feed(feed))
        return {
            "feed_count": len(self.feeds),
            "item_count": len(collected),
            "items": collected[:10],
        }
