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
                "claim": "Sistem yükü yükseliyor; otonom tarama aralığı esnetilmeli.",
                "status": "supported",
                "evidence_score": 0.85,
            })
        else:
            hypotheses.append({
                "claim": "Sistem kaynakları sürekli otonom araştırma ve avatar sohbeti için uygun.",
                "status": "supported",
                "evidence_score": 0.92,
            })

        signal = float(social.get("signal_strength", 0.0))
        if research.get("item_count", 0) > 0 and signal >= 0.2:
            hypotheses.append({
                "claim": "Takip edilen yapay zeka ve otonomi konularında aktif bilgi akışı var.",
                "status": "verified",
                "evidence_score": round(min(1.0, 0.55 + signal), 2),
            })
        else:
            hypotheses.append({
                "claim": "Mevcut kaynaklarda sinyal düşük; ek besleme veya yeni sorgu stratejisi gerekli.",
                "status": "tentative",
                "evidence_score": 0.50,
            })

        return hypotheses
