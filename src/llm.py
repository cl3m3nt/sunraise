from abc import ABC, abstractmethod
import anthropic
from google import genai
from google.genai import types
from openai import OpenAI
from mistralai.client import Mistral

from tools.weather import get_weather
from tools.current_time import get_current_time


class LLMProvider(ABC):

    def __init__(self, name, model, api_key, temperature):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

    @abstractmethod
    def __call__(self, message, *args):
        pass


class AnthropicProvider(LLMProvider):
    provider = "anthropic"  # class variable

    def __init__(self, name, model, api_key, temperature):
        super().__init__(name, model, api_key, temperature)
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def __call__(self, conversation, *args):
        print
        response = self.client.messages.create(
            model=self.model, max_tokens=1000, messages=conversation
        )
        return response.content[0].text


class DummyProvider(LLMProvider):
    provider = "dummy"

    def __call__(self, message, *args) -> str:
        response = f"You said: {message}"
        return response


class GoogleProvider(LLMProvider):
    provider = "google"

    def __init__(self, name, model, api_key, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = genai.Client(api_key=self.api_key)
        self.config = config
        self.args = args

    def __call__(self, message, *args) -> str:

        # STEP 1: first call to LLM
        response = self.client.models.generate_content(
            model=self.model, contents=message, config=self.config
        )

        # STEP 2, 3, 4 are optional in case of tool call
        parts = response.candidates[0].content.parts

        for part in parts:

            # STEP 2: checking for tool call
            if getattr(part, "function_call", None):
                tool_function_call = part.function_call

                # STEP 3: execute tool
                tool_switch = {
                    "get_weather": get_weather,
                    "get_current_time": get_current_time,
                }
                print("TOOL CALL:", tool_function_call.name, tool_function_call.args)
                tool_function = tool_switch[tool_function_call.name]
                result = tool_function(**tool_function_call.args)

                # STEP 4: send back tool result to LLM for new response
                response_with_tool = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        *message,
                        response.candidates[0].content,
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_function_response(
                                    name=tool_function_call.name,
                                    response={"result": result},
                                )
                            ],
                        ),
                    ],
                    config=self.config,
                )

                return response_with_tool.text

        # When no tool used
        return response.text


class OpenAIProvider(LLMProvider):
    provider = "openai"

    def __init__(self, name, model, api_key, temperature):
        super().__init__(name, model, api_key, temperature)
        self.client = OpenAI(api_key=self.api_key)

    def __call__(self, message, *args) -> str:
        response = self.client.responses.create(model=self.model, input=message)
        return response.output_text


class MistralProvider(LLMProvider):
    provider = "mistral"

    def __init__(self, name, model, api_key, temperature):
        super().__init__(name, model, api_key, temperature)
        self.client = Mistral(api_key=self.api_key)

    def __call__(self, conversation, *args) -> str:
        # prepared_message = {"role": "user", "content": message}
        # print(conversation)
        response = self.client.chat.complete(
            model=self.model, messages=conversation, stream=False
        )
        return response.choices[0].message.content
