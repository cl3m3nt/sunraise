from abc import ABC, abstractmethod
import anthropic
from google import genai
from google.genai import types
from openai import OpenAI
from mistralai.client import Mistral

from tools.weather import get_weather
from tools.current_time import get_current_time

import json


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
    provider = "anthropic"

    def __init__(self, name, model, api_key, temperature, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.args = args

    def __call__(self, conversation):

        # defining tool from self.args
        tools = list(self.args)

        response = self.client.messages.create(
            model=self.model, max_tokens=1000, messages=conversation, tools=tools
        )

        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if tool_calls:
            prepared_input_with_tools = []
            prepared_input_with_tools.append(
                {"role": "assistant", "content": response.content}
            )

            tool_switch = {
                "get_weather": get_weather,
                "get_current_time": get_current_time,
            }

            tool_result = []
            for tool_call in tool_calls:
                print("TOOL CALL:", tool_call.name, tool_call.input)
                tool_function = tool_switch[tool_call.name]
                tool_function_args = tool_call.input
                result = tool_function(**tool_function_args)

                tool_result.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

            prepared_tool_result = {"role": "user", "content": tool_result}

            prepared_input_with_tools.append(prepared_tool_result)

            response_with_tool = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=conversation + prepared_input_with_tools,
                tools=tools,
            )
            return response_with_tool.content[0].text

        else:

            return response.content[0].text


class DummyProvider(LLMProvider):
    provider = "dummy"

    def __call__(self, message) -> str:
        response = f"You said: {message}"
        return response


class GoogleProvider(LLMProvider):
    provider = "google"

    def __init__(self, name, model, api_key, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = genai.Client(api_key=self.api_key)
        self.config = config
        self.args = args

    def __call__(self, message) -> str:

        # STEP 1: first call to LLM
        response = self.client.models.generate_content(
            model=self.model, contents=message, config=self.config
        )

        tool_calls = [
            part
            for part in response.candidates[0].content.parts
            if getattr(part, "function_call")
        ]

        if tool_calls:

            # STEP 2, 3, 4 are optional in case of tool call
            parts = response.candidates[0].content.parts

            tool_result = []

            for part in parts:

                # STEP 2: checking for tool call
                if getattr(part, "function_call", None):
                    tool_function_call = part.function_call

                    # STEP 3: execute tool
                    tool_switch = {
                        "get_weather": get_weather,
                        "get_current_time": get_current_time,
                    }
                    print(
                        "TOOL CALL:", tool_function_call.name, tool_function_call.args
                    )
                    tool_function = tool_switch[tool_function_call.name]
                    result = tool_function(**tool_function_call.args)

                tool_result.append(
                    types.Part.from_function_response(
                        name=tool_function_call.name,
                        response={"result": result},
                    )
                )

            # STEP 4: send back tool result to LLM for new response
            response_with_tool = self.client.models.generate_content(
                model=self.model,
                contents=[
                    *message,
                    response.candidates[0].content,
                    types.Content(role="user", parts=tool_result),
                ],
                config=self.config,
            )

            return response_with_tool.text

        else:
            # When no tool used
            return response.text


class OpenAIProvider(LLMProvider):
    provider = "openai"

    def __init__(self, name, model, api_key, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = OpenAI(api_key=self.api_key)
        self.config = config
        self.args = args

    def __call__(self, message) -> str:

        # defining tool from self.args
        tools = list(self.args)

        response = self.client.responses.create(
            model=self.model, input=message, tools=tools
        )

        tool_calls = [item for item in response.output if item.type == "function_call"]

        if tool_calls:
            input_with_tools = list(response.output)

            tool_switch = {
                "get_weather": get_weather,
                "get_current_time": get_current_time,
            }

            for tool_call in tool_calls:
                print("TOOL CALL:", tool_call.name, tool_call.arguments)
                tool_function = tool_switch[tool_call.name]
                tool_function_args = json.loads(tool_call.arguments)
                result = tool_function(**tool_function_args)

                tool_result = {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result),
                }

                input_with_tools.append(tool_result)

            # Checking current input: message history + input_with_tools
            # print(message+input_with_tools)

            response_with_tool = self.client.responses.create(
                model=self.model, input=message + input_with_tools, tools=tools
            )
            return response_with_tool.output_text

        else:
            return response.output_text


class MistralProvider(LLMProvider):
    provider = "mistral"

    def __init__(self, name, model, api_key, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = Mistral(api_key=self.api_key)
        self.config = config
        self.args = args

    def __call__(self, conversation) -> str:

        # defining tool from self.args
        tools = list(self.args)

        # STEP 1: first call to LLM
        response = self.client.chat.complete(
            model=self.model, messages=conversation, tools=tools, stream=False
        )

        message = response.choices[0].message

        # STEP 2, 3, 4 are optional in case of tool call
        if getattr(message, "tool_calls", None):
            tool_calls = [
                item
                for item in response.choices[0].message.tool_calls
                if item.type == "function"
            ]

            if tool_calls:
                # the assistant_tool_message is required in the conversation by Mistral API
                assistant_tool_message = {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in (
                            message.tool_calls
                        )  # iterating over tools here
                    ],
                }
                conversation.append(assistant_tool_message)

                tool_switch = {
                    "get_weather": get_weather,
                    "get_current_time": get_current_time,
                }

                for tool_call in tool_calls:

                    print(
                        "TOOL CALL:",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    tool_function = tool_switch[tool_call.function.name]
                    tool_func_args = json.loads(tool_call.function.arguments)

                    result = tool_function(**tool_func_args)

                    function_message = {
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id,
                    }
                    conversation.append(function_message)

                response_with_tool = self.client.chat.complete(
                    model=self.model, messages=conversation, tools=tools, stream=False
                )
                return response_with_tool.choices[0].message.content

        else:
            return response.choices[0].message.content
