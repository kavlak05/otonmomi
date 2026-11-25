import asyncio
import logging
from config import CONFIG
from websocket_server import AvatarServer
from stt_engine import SpeechToTextEngine
from reasoned_agent import ReasonedAgent
from tts_engine import TextToSpeechEngine

logging.basicConfig(level=logging.INFO)

class MetaHumanSystem:
    def __init__(self):
        self.config = CONFIG
        self.avatar_server = AvatarServer(self.config.host, self.config.ws_port)
        self.stt = SpeechToTextEngine(self.config.openai_api_key)
        self.agent = ReasonedAgent(self.config.openai_api_key, self.config.reasoning_model)
        self.tts = TextToSpeechEngine(self.config.openai_api_key, self.config.voice_model)

    async def process_interaction(self, simulated_audio_input: bytes):
        logging.info("Girdi işleniyor...")
        user_text = self.stt.transcribe(simulated_audio_input)
        logging.info(f"Anlaşılan metin: {user_text}")

        agent_decision = self.agent.generate_response(user_text)
        emotion = agent_decision.get("emotion", "neutral")
        reply_text = agent_decision.get("reply_text", "")
        logging.info(f"Karar: {agent_decision}")

        audio_b64, visemes = self.tts.synthesize(reply_text)
        await self.avatar_server.send_state(emotion, visemes, audio_b64)
        logging.info("Avatar durumu güncellendi.")

    async def main_loop(self):
        server = await self.avatar_server.start()
        logging.info("Sistem başlatıldı, Unreal Engine bağlantısı bekleniyor.")
        
        await asyncio.sleep(5)
        mock_audio = b"\x00\x01\x02\x03" 
        await self.process_interaction(mock_audio)
        
        await server.wait_closed()

if __name__ == "__main__":
    system = MetaHumanSystem()
    asyncio.run(system.main_loop())
