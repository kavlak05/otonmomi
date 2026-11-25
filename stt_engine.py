import io
from openai import OpenAI

class SpeechToTextEngine:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_bytes: bytes) -> str:
        buffer = io.BytesIO(audio_bytes)
        buffer.name = "audio.wav"
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer
        )
        return transcript.text
