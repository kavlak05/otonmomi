from typing import Any
from config import SystemConfig
from gemini_client import GeminiClient
from logic import LogicReasoner
from memory import MemoryStore
from research import ResearchEngine
from social import SocialListener
from telemetry import TelemetryCollector


class AutonomousBrain:
    def __init__(self, config: SystemConfig, memory: MemoryStore, gemini: GeminiClient | None = None) -> None:
        self.config = config
        self.memory = memory
        self.gemini = gemini or GeminiClient(
            api_key=config.gemini_api_key,
            model=config.gemini_model,
            timeout=config.request_timeout,
        )
        self.telemetry = TelemetryCollector()
        self.research = ResearchEngine(config.rss_feeds, timeout=config.request_timeout)
        self.social = SocialListener(config.social_topics)
        self.logic = LogicReasoner()
        self.cycle_count = 0
        self.last_state: dict[str, Any] = {}

    def _call_llm_decision(self, context_summary: str) -> dict[str, Any] | None:
        if not self.gemini.is_configured:
            return None

        system_instruction = (
            "Sen otonom bir yapay zeka karar ve öz-gelişim motorusun. "
            "YALNIZCA geçerli JSON döndür: "
            '{"action": "...", "rationale": "...", "confidence": 0.85, "self_improvement": "..."}'
        )
        try:
            parsed = self.gemini.generate_json(
                prompt=context_summary,
                system_instruction=system_instruction,
                temperature=0.25,
            )
            if not parsed:
                return None
            conf = float(parsed.get("confidence", 0.78))
            return {
                "action": str(parsed.get("action", "consolidate_and_evolve")),
                "rationale": str(parsed.get("rationale", "Gemini otonom kararı üretildi.")),
                "confidence": max(0.0, min(1.0, conf)),
                "self_improvement": str(parsed.get("self_improvement", "")).strip(),
            }
        except Exception:
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

        top_titles = [
            i.get("title", "") for i in res.get("items", [])[:3] if i.get("title")
        ]
        summary_text = (
            " | ".join(top_titles)
            if top_titles
            else "Yeni başlık bulunamadı; dış kaynaklar ve avatar sohbet hafızası izleniyor."
        )
        self.memory.consolidate_topic(
            topic="global_ai_and_autonomy",
            summary=summary_text[:500],
            item_count=max(1, int(res.get("item_count", 0))),
        )

        context_summary = (
            f"Cycle={self.cycle_count}, Items={res.get('item_count', 0)}, "
            f"Signal={soc.get('signal_strength', 0.0)}, TopTerms={soc.get('top_terms', [])}, "
            f"Summary={summary_text[:280]}"
        )
        llm_decision = self._call_llm_decision(context_summary)

        if llm_decision:
            action = llm_decision["action"]
            rationale = llm_decision["rationale"]
            confidence = llm_decision["confidence"]
            if llm_decision.get("self_improvement"):
                self.memory.add_improvement(
                    area="autonomous_cycle",
                    proposal=llm_decision["self_improvement"][:400],
                    priority="high",
                )
        elif res.get("item_count", 0) > 0:
            action = "consolidate_knowledge"
            rationale = (
                f"{res['item_count']} araştırma kaydı işlendi; sosyal sinyal={soc['signal_strength']}."
            )
            confidence = 0.82
        else:
            action = "observe_and_adapt"
            rationale = "Aktif akış verisi sınırlı; hafıza pekiştiriliyor ve bir sonraki döngü hazırlanıyor."
            confidence = 0.68

        self.memory.add_decision(self.cycle_count, action, rationale, confidence)

        state = {
            "cycle": self.cycle_count,
            "telemetry": tel,
            "research_items": res.get("item_count", 0),
            "social_signal": soc.get("signal_strength", 0.0),
            "top_terms": soc.get("top_terms", []),
            "hypotheses": hypotheses,
            "action": action,
            "rationale": rationale,
            "confidence": confidence,
        }
        self.last_state = state
        return state
