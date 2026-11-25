from openai import OpenAI
import base64

class TextToSpeechEngine:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def synthesize(self, text: str) -> tuple[str, str]:
        response = self.client.audio.speech.create(
            model=self.model,
            voice="alloy",
            input=text
        )
        audio_stream = response.content
        audio_base64 = base64.b64encode(audio_stream).decode('utf-8')
        
        mock_visemes = "A,O,E,I,U,B,F,M"
        return audio_base64, mock_visemes
