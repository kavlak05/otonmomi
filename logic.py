from typing import Any


class LogicReasoner:
    def evaluate_hypotheses(
        self,
        telemetry: dict[str, Any],
        research: dict[str, Any],
        social: dict[str, Any],
    ) -> list[dict[str, Any]]:
        hypotheses: list[dict[str, Any]] = []

        load_1m = telemetry.get("load_1m")
        if load_1m is not None and load_1m > 4.0:
            hypotheses.append({
                "claim": "Sistem yükü yükseliyor; tarama sıklığı dengelenmeli.",
                "status": "supported",
                "evidence_score": 0.85,
            })
        else:
            hypotheses.append({
                "claim": "Sistem kaynakları otonom araştırma döngüsü için yeterli.",
                "status": "supported",
                "evidence_score": 0.90,
            })

        signal = float(social.get("signal_strength", 0.0))
        if research.get("item_count", 0) > 0 and signal >= 0.2:
            hypotheses.append({
                "claim": "Takip edilen teknoloji/yapay zeka konularında aktif sinyal mevcut.",
                "status": "verified",
                "evidence_score": round(min(1.0, 0.5 + signal), 2),
            })
        else:
            hypotheses.append({
                "claim": "Mevcut kaynaklarda yeni konu sinyali düşük; ek kaynak taraması gerekli.",
                "status": "tentative",
                "evidence_score": 0.45,
            })

        return hypotheses
