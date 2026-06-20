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

        # initial response
        response = self.client.messages.create(
            model=self.model, max_tokens=1000, messages=conversation, tools=tools
        )

        # tool_calls built from block
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

            # tool_result definition
            tool_results = []

            for tool_call in tool_calls:
                print("TOOL CALL:", tool_call.name, tool_call.input)
                tool_function = tool_switch[tool_call.name]
                tool_function_args = tool_call.input
                result = tool_function(**tool_function_args)

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

            # all tool_result concatenated as prepared_tool_result
            prepared_tool_result = {"role": "user", "content": tool_results}

            # initial response + prepared_tool_result
            prepared_input_with_tools.append(prepared_tool_result)

            # final response
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

    def __call__(self, conversation) -> str:

        # self.args unused as tools are defined by config

        # initial response
        response = self.client.models.generate_content(
            model=self.model, contents=conversation, config=self.config
        )

        # tool_calls built from part
        tool_calls = [
            part
            for part in response.candidates[0].content.parts
            if getattr(part, "function_call")
        ]

        if tool_calls:

            tool_switch = {
                "get_weather": get_weather,
                "get_current_time": get_current_time,
            }

            # tool_result definition
            tool_results = []

            for tool_call in tool_calls:

                if getattr(tool_call, "function_call", None):
                    tool_call_function = tool_call.function_call

                    print(
                        "TOOL CALL:", tool_call_function.name, tool_call_function.args
                    )
                    tool_function = tool_switch[tool_call_function.name]
                    result = tool_function(**tool_call_function.args)

                # all tool_result concatenated as prepared_tool_result
                tool_results.append(
                    types.Part.from_function_response(
                        name=tool_call_function.name,
                        response={"result": result},
                    )
                )

            # final response
            response_with_tool = self.client.models.generate_content(
                model=self.model,
                contents=[
                    *conversation,
                    response.candidates[0].content,
                    types.Content(role="user", parts=tool_results),
                ],
                config=self.config,
            )

            return response_with_tool.text

        else:

            return response.text


class OpenAIProvider(LLMProvider):
    provider = "openai"

    def __init__(self, name, model, api_key, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = OpenAI(api_key=self.api_key)
        self.config = config
        self.args = args

    def __call__(self, conversation) -> str:

        # defining tool from self.args
        tools = list(self.args)

        # initial response
        response = self.client.responses.create(
            model=self.model, input=conversation, tools=tools
        )

        # tool_calls built from item
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if tool_calls:
            input_with_tools = list(response.output)

            # tool_result definition
            tool_results = []

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

                tool_results.append(tool_result)

            # first response + tool_result concatenated
            input_with_tools = input_with_tools + tool_results

            # final response
            response_with_tool = self.client.responses.create(
                model=self.model, input=conversation + input_with_tools, tools=tools
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

        # initial response
        response = self.client.chat.complete(
            model=self.model, messages=conversation, tools=tools, stream=False
        )

        message = response.choices[0].message

        if getattr(message, "tool_calls", None):
            tool_calls = [
                item
                for item in response.choices[0].message.tool_calls
                if item.type == "function"
            ]

            if tool_calls:

                # tool_result definition
                tool_results = []

                tool_switch = {
                    "get_weather": get_weather,
                    "get_current_time": get_current_time,
                }

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
                tool_results.append(assistant_tool_message)

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

                    # tool_result concatenated
                    tool_results.append(function_message)

                # final response
                response_with_tool = self.client.chat.complete(
                    model=self.model,
                    messages=conversation + tool_results,
                    tools=tools,
                    stream=False,
                )
                return response_with_tool.choices[0].message.content

        else:
            return response.choices[0].message.content
