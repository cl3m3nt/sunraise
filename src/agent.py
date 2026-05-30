import anthropic
import uuid
from google import genai
from openai import OpenAI


class Agent:
    def __init__(self, name, model, api_key, temperature, role):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.role = role
        self.identity = self.get_identity()

    def get_identity(self):
        identity = uuid.uuid4()
        return identity

    def call_dummy(self, message):

        response = f"You said: {message}"

        return response

    def call_gemini(self, message):
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(model=self.model, contents=message)

        return response.text

    def call_claude(self, message):
        client = anthropic.Anthropic(api_key=self.api_key)
        prepared_message = {"role": "user", "content": message}
        response = client.messages.create(
            model=self.model, max_tokens=1000, messages=[prepared_message]
        )
        return response.content[0].text

    def call_gpt(self, message):
        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(model=self.model, input=message)
        return response.output_text
