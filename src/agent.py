from google import genai
import anthropic


class Agent:
    def __init__(self, name, model, api_key, temperature, role):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.role = role

    def call_dummy(self, message):

        response = f"You said: {message}"

        return response

    def call_gemini(self, message):
        client = genai.Client(api_key=self.api_key)
        print("calling gemini...")
        response = client.models.generate_content(model=self.model, contents=message)

        return response.text

    def call_claude(self, message):
        client = anthropic.Anthropic(api_key=self.api_key)
        print("calling claude")
        prepared_message = {"role": "user", "content": message}
        response = client.messages.create(
            model=self.model, max_tokens=1000, messages=[prepared_message]
        )
        return response.content[0].text
