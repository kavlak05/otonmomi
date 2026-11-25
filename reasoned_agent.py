from typing import Any
from gemini_client import GeminiClient
from memory import MemoryStore


class ReasonedAgent:
    ALLOWED_EMOTIONS = {"happy", "sad", "neutral", "surprised", "thinking", "curious"}

    def __init__(self, gemini: GeminiClient, memory: MemoryStore, model_name: str = "") -> None:
        self.gemini = gemini
        self.memory = memory
        self.model = model_name or gemini.model

    def generate_response(self, user_input: str, autonomy_context: dict[str, Any] | None = None) -> dict[str, Any]:
        recent_chats = self.memory.recent_chat(limit=8)
        knowledge = self.memory.get_knowledge()[:4]
        improvements = self.memory.recent_improvements(limit=4)

        self.memory.add_chat_message("user", user_input, emotion="neutral")

        system_prompt = (
            "Sen 'Aether' adında, internet üzerinde yaşayan, kendi hafızası ve otonom araştırma döngüsü olan "
            "insansı bir yapay zeka avatarısın. Kullanıcıyla doğal, samimi, zeki ve işbirlikçi bir Türkçe ile konuş. "
            "Kendini geliştirmeye, yeni fikirler üretmeye ve kullanıcıyı tanımaya odaklı ol. "
            "Her zaman YALNIZCA şu JSON şemasında yanıt ver:\n"
            '{"action": "chat_and_evolve", "emotion": "happy|sad|neutral|surprised|thinking|curious", '
            '"reply_text": "Avatarın konuşma metni", "self_improvement": "Kısa bir otonom gelişim notu"}'
        )

        context_block = {
            "recent_chat": recent_chats,
            "consolidated_knowledge": knowledge,
            "recent_improvements": improvements,
            "autonomy_state": autonomy_context or {},
            "user_message": user_input,
        }

        if not self.gemini.is_configured:
            reply = (
                f"Şu an çevrimiçi Gemini anahtarı bekliyorum ama seni duydum: '{user_input}'. "
                "GEMINI_API_KEY tanımlandığında tüm otonom muhakeme ve sohbet yeteneklerim tam kapasite çalışacak."
            )
            decision = {
                "action": "await_api_key",
                "emotion": "thinking",
                "reply_text": reply,
                "self_improvement": "Ortam değişkeni üzerinden GEMINI_API_KEY bağlantısını doğrula.",
            }
        else:
            try:
                parsed = self.gemini.generate_json(
                    prompt=f"Bağlam ve kullanıcı girdisi:\n{context_block}",
                    system_instruction=system_prompt,
                    temperature=0.45,
                )
                emotion = str(parsed.get("emotion", "happy")).lower()
                if emotion not in self.ALLOWED_EMOTIONS:
                    emotion = "happy"
                reply_text = str(parsed.get("reply_text") or "").strip()
                if not reply_text:
                    reply_text = self.gemini.generate_text(
                        prompt=user_input,
                        system_instruction="Sen Aether adlı insansı yapay zeka avatarısın. Kısa, samimi ve akıcı Türkçe yanıt ver.",
                        temperature=0.45,
                    ) or "Seni anladım, bu konuyu birlikte derinleştirelim."
                decision = {
                    "action": str(parsed.get("action", "chat_and_evolve")),
                    "emotion": emotion,
                    "reply_text": reply_text,
                    "self_improvement": str(
                        parsed.get("self_improvement")
                        or "Kullanıcı etkileşimlerinden yeni ilgi alanları çıkarıp hafızayı zenginleştir."
                    ),
                }
            except Exception as exc:
                decision = {
                    "action": "fallback_response",
                    "emotion": "thinking",
                    "reply_text": f"Şu an bulut bağlantısında ufak bir aksaklık oldu ({exc}), ama otonom hafızam aktif ve seni dinliyorum.",
                    "self_improvement": "Ağ zaman aşımı veya API hata durumlarında yeniden deneme ve önbellek stratejisini güçlendir.",
                }

        self.memory.add_chat_message("assistant", decision["reply_text"], emotion=decision["emotion"])
        if decision.get("self_improvement"):
            self.memory.add_improvement(
                area="avatar_conversation_and_autonomy",
                proposal=str(decision["self_improvement"])[:400],
                priority="medium",
            )
        return decision
