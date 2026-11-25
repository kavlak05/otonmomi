import asyncio
import logging
from config import CONFIG
from gemini_client import GeminiClient
from memory import MemoryStore
from brain import AutonomousBrain
from reasoned_agent import ReasonedAgent
from stt_engine import SpeechToTextEngine
from tts_engine import TextToSpeechEngine
from web_avatar_server import WebAvatarServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class MetaHumanSystem:
    def __init__(self) -> None:
        self.config = CONFIG
        self.memory = MemoryStore(self.config.db_path)
        self.gemini = GeminiClient(
            api_key=self.config.gemini_api_key,
            model=self.config.gemini_model,
            timeout=self.config.request_timeout,
        )
        self.brain = AutonomousBrain(self.config, self.memory, gemini=self.gemini)
        self.stt = SpeechToTextEngine(self.gemini)
        self.agent = ReasonedAgent(self.gemini, self.memory, model_name=self.config.gemini_model)
        self.tts = TextToSpeechEngine()
        self.web_server = WebAvatarServer(
            host=self.config.host,
            http_port=self.config.http_port,
            ws_port=self.config.ws_port,
            on_chat=self.handle_text_chat,
            on_cycle=self.run_autonomy_step,
            get_state=self.get_system_state,
        )

    async def run_autonomy_step(self) -> dict:
        state = await asyncio.to_thread(self.brain.step)
        logging.info(
            "Otonom döngü #%s tamamlandı -> aksiyon=%s, güven=%.2f",
            state.get("cycle"),
            state.get("action"),
            state.get("confidence", 0.0),
        )
        return state

    async def handle_text_chat(self, user_text: str) -> dict:
        decision = await asyncio.to_thread(
            self.agent.generate_response,
            user_text,
            self.brain.last_state,
        )
        reply_text = decision.get("reply_text", "")
        emotion = decision.get("emotion", "happy")
        audio_b64, visemes = self.tts.synthesize(reply_text)
        return {
            "action": decision.get("action", "chat_and_evolve"),
            "emotion": emotion,
            "reply_text": reply_text,
            "self_improvement": decision.get("self_improvement", ""),
            "audio_b64": audio_b64,
            "visemes": visemes,
        }

    async def process_audio_interaction(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> dict:
        user_text = await asyncio.to_thread(self.stt.transcribe, audio_bytes, mime_type)
        return await self.handle_text_chat(user_text)

    def get_system_state(self) -> dict:
        return {
            "gemini_configured": self.gemini.is_configured,
            "model": self.config.gemini_model,
            "brain_state": self.brain.last_state,
            "decisions": self.memory.recent_decisions(limit=8),
            "improvements": self.memory.recent_improvements(limit=8),
            "knowledge": self.memory.get_knowledge()[:6],
            "chat": self.memory.recent_chat(limit=12),
        }

    async def _autonomy_loop(self) -> None:
        while True:
            try:
                await self.run_autonomy_step()
            except Exception as exc:
                logging.exception("Otonom döngü hatası: %s", exc)
            await asyncio.sleep(max(10, self.config.autonomy_interval_sec))

    async def main_loop(self) -> None:
        if not self.gemini.is_configured:
            logging.warning(
                "GEMINI_API_KEY ortam değişkeni boş! Çalıştırmadan önce GEMINI_API_KEY tanımlayın."
            )
        await self.web_server.start()
        logging.info(
            "Web İnsansı Avatar arayüzü aktif: http://localhost:%s",
            self.config.http_port,
        )
        bg_task = asyncio.create_task(self._autonomy_loop())
        try:
            await asyncio.Event().wait()
        finally:
            bg_task.cancel()
            await self.web_server.stop()


if __name__ == "__main__":
    system = MetaHumanSystem()
    asyncio.run(system.main_loop())
