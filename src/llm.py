from abc import ABC, abstractmethod
import anthropic
from google import genai
from openai import OpenAI
from mistralai import Mistral


class LLMProvider(ABC):

    def __init__(self, name, model, api_key, temperature):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

    @abstractmethod
    def __call__(self, message):
        pass


class AnthropicProvider(LLMProvider):
    provider = "anthropic"  # class variable

    def __init__(self, name, model, api_key, temperature):
        super().__init__(name, model, api_key, temperature)
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def __call__(self, message):
        prepared_message = {"role": "user", "content": message}
        print
        response = self.client.messages.create(
            model=self.model, max_tokens=1000, messages=[prepared_message]
        )
        return response.content[0].text


class DummyProvider(LLMProvider):
    provider = "dummy"

    def __call__(self, message) -> str:
        response = f"You said: {message}"
        return response


class GoogleProvider(LLMProvider):
    provider = "google"

    def __init__(self, name, model, api_key, temperature):
        super().__init__(name, model, api_key, temperature)
        self.client = genai.Client(api_key=self.api_key)

    def __call__(self, message) -> str:
        response = self.client.models.generate_content(
            model=self.model, contents=message
        )
        return response.text


class OpenAIProvider(LLMProvider):
    provider = "openai"

    def __init__(self, name, model, api_key, temperature):
        super().__init__(name, model, api_key, temperature)
        self.client = OpenAI(api_key=self.api_key)

    def __call__(self, message) -> str:
        response = self.client.responses.create(model=self.model, input=message)
        return response.output_text


class MistralProvider(LLMProvider):
    provider = "mistral"

    def __init__(self, name, model, api_key, temperature):
        super().__init__(name, model, api_key, temperature)
        self.client = Mistral(api_key=self.api_key)

    def __call__(self, conversation) -> str:
        # prepared_message = {"role": "user", "content": message}
        print(conversation)
        response = self.client.chat.complete(
            model=self.model, messages=conversation, stream=False
        )
        return response.choices[0].message.content
