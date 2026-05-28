from google import genai


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
        print("calling LLM...")
        response = client.models.generate_content(model=self.model, contents=message)

        return response.text
