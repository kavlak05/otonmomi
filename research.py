from typing import Any
import html
import re
from urllib.error import URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


class ResearchEngine:
    def __init__(self, feeds: list[str], timeout: int = 15) -> None:
        self.feeds = feeds
        self.timeout = timeout

    @staticmethod
    def _clean_html(text: str) -> str:
        no_tags = re.sub(r"<[^>]+>", " ", text)
        unescaped = html.unescape(no_tags)
        return re.sub(r"\s+", " ", unescaped).strip()

    def fetch_feed(self, url: str) -> list[dict[str, str]]:
        req = Request(url, headers={"User-Agent": "AetherAvatarAutonomy/2.0"})
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw_xml = resp.read()
        except (URLError, TimeoutError, OSError) as exc:
            return [{
                "title": f"Akış erişim uyarısı: {url}",
                "summary": str(exc),
                "link": url,
            }]

        try:
            root = ET.fromstring(raw_xml)
        except ET.ParseError as exc:
            return [{
                "title": f"XML ayrıştırma uyarısı: {url}",
                "summary": str(exc),
                "link": url,
            }]

        items: list[dict[str, str]] = []
        entries = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for item in entries[:5]:
            title = self._clean_html(
                item.findtext("title")
                or item.findtext("{http://www.w3.org/2005/Atom}title")
                or ""
            )
            summary = self._clean_html(
                item.findtext("description")
                or item.findtext("summary")
                or item.findtext("{http://www.w3.org/2005/Atom}summary")
                or ""
            )
            link = (
                item.findtext("link")
                or item.findtext("{http://www.w3.org/2005/Atom}link")
                or url
            ).strip()
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
