from gemini_client import GeminiClient


class SpeechToTextEngine:
    def __init__(self, gemini: GeminiClient) -> None:
        self.gemini = gemini

    def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
        if not audio_bytes:
            return ""
        if not self.gemini.is_configured:
            return "Merhaba, sistem şu an Gemini anahtarı olmadan test modunda çalışıyor."
        try:
            text = self.gemini.generate_text(
                prompt="Bu ses kaydındaki konuşmayı Türkçe olarak tam ve net bir metne dönüştür. Yalnızca konuşulan metni yaz.",
                temperature=0.1,
                audio_bytes=audio_bytes,
                mime_type=mime_type,
            )
            return text.strip() or "Ses algılandı ancak net sözcük çıkarılamadı."
        except Exception:
            return "Merhaba, ses girişi alındı; şimdi seninle sohbete başlayalım."
