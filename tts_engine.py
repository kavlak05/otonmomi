import base64
import json
import re
from typing import Any


class TextToSpeechEngine:
    VISEME_MAP = {
        "a": "AA",
        "e": "E",
        "ı": "IH",
        "i": "IH",
        "o": "O",
        "ö": "O",
        "u": "U",
        "ü": "U",
        "b": "MBP",
        "m": "MBP",
        "p": "MBP",
        "f": "FV",
        "v": "FV",
        "l": "L",
        "r": "R",
        "s": "SH",
        "ş": "SH",
        "z": "S",
        "c": "CH",
        "ç": "CH",
    }

    def synthesize(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        clean = re.sub(r"\s+", " ", (text or "")).strip()
        if not clean:
            clean = "Seni dinliyorum."

        visemes: list[dict[str, Any]] = []
        t = 0.0
        for ch in clean.lower()[:180]:
            viseme = self.VISEME_MAP.get(ch, "sil" if ch == " " else "neutral")
            duration = 0.06 if ch == " " else 0.085
            visemes.append({
                "viseme": viseme,
                "start": round(t, 3),
                "duration": duration,
            })
            t += duration

        payload = json.dumps({"text": clean, "visemes": visemes}, ensure_ascii=False).encode("utf-8")
        audio_b64 = base64.b64encode(payload).decode("ascii")
        return audio_b64, visemes
