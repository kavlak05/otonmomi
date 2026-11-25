from openai import OpenAI
import json

class ReasonedAgent:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_response(self, user_input: str) -> dict:
        prompt = (
            "Sen gelişmiş bir insansı yapay zeka asistanısın. Kullanıcıyla sohbet et, "
            "verilen komutları analiz et ve şu formatta JSON çıktısı ver: "
            '{"action": "exec_code_or_reasoning", "emotion": "happy/sad/neutral/surprised", "reply_text": "Cümle"}'
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
