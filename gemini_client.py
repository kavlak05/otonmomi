import base64
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", timeout: int = 25) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @staticmethod
    def _extract_json_object(raw_text: str) -> dict[str, Any]:
        cleaned = raw_text.strip()
        fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
        if fenced:
            cleaned = fenced.group(1).strip()
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
        return {}

    def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.4,
        json_mode: bool = False,
        audio_bytes: bytes | None = None,
        mime_type: str = "audio/wav",
    ) -> str:
        if not self.is_configured:
            raise RuntimeError("GEMINI_API_KEY tanımlı değil.")

        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"
        parts: list[dict[str, Any]] = []
        if audio_bytes:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(audio_bytes).decode("ascii"),
                }
            })
        parts.append({"text": prompt})

        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": temperature,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        req = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Gemini HTTP {exc.code}: {detail[:300]}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Gemini ağ hatası: {exc}") from exc

        candidates = body.get("candidates") or []
        if not candidates:
            return ""
        content = candidates[0].get("content") or {}
        out_parts = content.get("parts") or []
        texts = [str(p.get("text", "")) for p in out_parts if isinstance(p, dict) and p.get("text")]
        return "\n".join(texts).strip()

    def generate_json(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.25,
    ) -> dict[str, Any]:
        raw = self.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            json_mode=True,
        )
        return self._extract_json_object(raw)
