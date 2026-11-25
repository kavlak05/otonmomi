import json
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from config import SystemConfig
from logic import LogicReasoner
from memory import MemoryStore
from research import ResearchEngine
from social import SocialListener
from telemetry import TelemetryCollector


class AutonomousBrain:
    def __init__(self, config: SystemConfig, memory: MemoryStore) -> None:
        self.config = config
        self.memory = memory
        self.telemetry = TelemetryCollector()
        self.research = ResearchEngine(config.rss_feeds, timeout=config.request_timeout)
        self.social = SocialListener(config.social_topics)
        self.logic = LogicReasoner()
        self.cycle_count = 0

    def _call_llm_decision(self, context_summary: str) -> dict[str, Any] | None:
        if self.config.llm_provider != "openai" or not self.config.openai_api_key:
            return None

        payload = {
            "model": self.config.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Sen otonom bir karar motorusun. Yalnızca JSON döndür: "
                        '{"action": "...", "rationale": "...", "confidence": 0.0}'
                    ),
                },
                {"role": "user", "content": context_summary},
            ],
            "temperature": 0.2,
        }
        req = Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.openai_api_key}",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.config.request_timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return {
                "action": str(parsed.get("action", "consolidate_and_monitor")),
                "rationale": str(parsed.get("rationale", "LLM kararı alındı.")),
                "confidence": float(parsed.get("confidence", 0.75)),
            }
        except (URLError, TimeoutError, OSError, KeyError, ValueError, TypeError):
            return None

    def step(self) -> dict[str, Any]:
        self.cycle_count += 1

        tel = self.telemetry.collect()
        self.memory.add_observation("telemetry", tel)

        res = self.research.scan()
        self.memory.add_observation("research", res)

        soc = self.social.analyze_items(res.get("items", []))
        self.memory.add_observation("social", soc)

        hypotheses = self.logic.evaluate_hypotheses(tel, res, soc)
        for h in hypotheses:
            self.memory.record_hypothesis(h["claim"], h["status"], h["evidence_score"])

        top_titles = [i.get("title", "") for i in res.get("items", [])[:3] if i.get("title")]
        summary_text = " | ".join(top_titles) if top_titles else "Yeni başlık bulunamadı; kaynaklar izleniyor."
        self.memory.consolidate_topic(
            topic="global_ai_and_tech",
            summary=summary_text[:500],
            item_count=max(1, int(res.get("item_count", 0))),
        )

        llm_decision = self._call_llm_decision(
            f"Cycle={self.cycle_count}, Items={res.get('item_count', 0)}, Signal={soc.get('signal_strength', 0)}"
        )
        if llm_decision:
            action = llm_decision["action"]
            rationale = llm_decision["rationale"]
            confidence = max(0.0, min(1.0, llm_decision["confidence"]))
        elif res.get("item_count", 0) > 0:
            action = "consolidate_knowledge"
            rationale = f"{res['item_count']} araştırma kaydı işlendi ve sosyal sinyal={soc['signal_strength']}."
            confidence = 0.82
        else:
            action = "backoff_and_retry"
            rationale = "Aktif akış verisi sınırlı; bir sonraki döngüde yeniden taranacak."
            confidence = 0.65

        self.memory.add_decision(self.cycle_count, action, rationale, confidence)

        return {
            "cycle": self.cycle_count,
            "telemetry": tel,
            "research_items": res.get("item_count", 0),
            "social_signal": soc.get("signal_strength", 0.0),
            "action": action,
            "rationale": rationale,
            "confidence": confidence,
        }
