from collections import Counter
from typing import Any


class SocialListener:
    def __init__(self, topics: list[str]) -> None:
        self.topics = topics

    def analyze_items(self, research_items: list[dict[str, str]]) -> dict[str, Any]:
        word_counts: Counter[str] = Counter()
        topic_hits: dict[str, int] = {t: 0 for t in self.topics}

        for item in research_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            for topic in self.topics:
                if topic.lower() in text:
                    topic_hits[topic] += 1
            for token in text.split():
                cleaned = token.strip(".,!?:;\"'()[]")
                if len(cleaned) >= 4 and not cleaned.startswith("http"):
                    word_counts[cleaned] += 1

        signal = min(
            1.0,
            round(sum(topic_hits.values()) / max(1, len(research_items)), 2),
        )
        return {
            "tracked_topics": self.topics,
            "topic_hits": topic_hits,
            "top_terms": word_counts.most_common(8),
            "signal_strength": signal,
        }
