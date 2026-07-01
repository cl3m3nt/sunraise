from abc import ABC, abstractmethod
import anthropic
from google import genai
from google.genai import types
from openai import OpenAI
from mistralai.client import Mistral

from tools.weather import get_weather
from tools.current_time import get_current_time

import json

TOOL_SWITCH = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
}

BLUE = "\033[38;5;117m"
GREEN = "\033[38;5;46m"  # bright green   # sky blue
YELLOW = "\033[38;5;220m"
RESET = "\033[0m"


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

            # tool_result definition
            tool_results = []

            for tool_call in tool_calls:

                if getattr(tool_call, "function_call", None):
                    tool_call_function = tool_call.function_call

                    print(
                        "TOOL CALL:", tool_call_function.name, tool_call_function.args
                    )
                    tool_function = TOOL_SWITCH[tool_call_function.name]
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

    def extract_text(self, model_turn) -> str:
        """Extract Text from LLM response"""

        # BLUE = "\033[38;5;117m"
        # GREEN = "\033[38;5;46m"  # bright green   # sky blue
        # RESET = "\033[0m"

        texts = []

        for part in model_turn.parts:
            if getattr(part, "text", None):
                text = part.text
                # print(f"{BLUE}---- text ----{RESET}")
                # print(text)
                texts.append(text)

            # else:
            # print(f"{BLUE}---- text ----{RESET}")
            #   print("No Text part")

        return "\n".join(texts).strip()

    def extract_function_calls(self, model_turn):
        """Extract the function_call part of a LLM (Actions)"""

        # BLUE = "\033[38;5;117m"
        # GREEN = "\033[38;5;46m"  # bright green   # sky blue
        # RESET = "\033[0m"

        # print("----- from extract function call -----")
        function_calls = []

        # print(response)
        # print("parts")
        for part in model_turn.parts:
            # print("------part------")
            # print(part)

            if getattr(part, "function_call", None):
                function_call = part.function_call
                # print(f"{GREEN}---- function_call ----{RESET}")
                # print(function_call)
                function_calls.append(function_call)
            # else:
            # In case there is a no tool call
            # print(f"{GREEN}---- function_call ----{RESET}")
            #   print("No Function call part")

        return function_calls

    def react_call(self, conversation, max_steps):

        # init react_conversation from User/Agent conversation
        # react_conversation = list(conversation)

        for step in range(1, max_steps + 1):

            # Initial response from model
            response = self.client.models.generate_content(
                model=self.model, contents=conversation, config=self.config
            )

            # Defining model turn
            model_turn = response.candidates[0].content
            print(f"{BLUE}--- model turn {step} ---{RESET}")

            # Record the model's turn
            conversation.append(model_turn)

            # The text part from model
            thought = self.extract_text(model_turn)

            # Multiple or parallel function calls
            function_calls = self.extract_function_calls(model_turn)

            if thought:
                print(f"  [thought {step}]: {thought}")

            # No tool calls -> the model is done reasoning, this is the answer.
            if not function_calls:
                return thought or response.text

            # Otherwise execute each requested tool and feed observations back.
            # This section is subject to non-deterministic behavior
            # All tools can be call executed in 1 ReAct turn if // tool call
            # Or tools can be executed sequentially in multiple turns
            # Temperature and prompt influence this process
            observation_parts = []
            for fc in function_calls:
                print(f"  [action {step}]: {fc.name}({dict(fc.args)})")
                tool_function = TOOL_SWITCH.get(fc.name)

                if tool_function is None:
                    result = f"Error: unknown tool '{fc.name}'"
                else:
                    try:
                        result = tool_function(**fc.args)
                    except Exception as exc:  # surface tool errors back to the model
                        result = f"Error in ReAct loop while running {fc.name}: {exc}"

                print(f"  [observation {step}]: {result}")
                observation_parts.append(
                    types.Part.from_function_response(
                        name=fc.name, response={"result": result}
                    )
                )

            # Observations are sent back as a user turn for the next iteration.
            conversation.append(types.Content(role="user", parts=observation_parts))

        budget_message = "Reached the maximum number of reasoning steps without a final answer. Ask to finalize"
        conversation.append(
            types.Content(role="model", parts=[types.Part(text=budget_message)])
        )
        return budget_message


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
                # adding assistant_tool_message to tool_results
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

                    # adding function message to tool_results
                    tool_results.append(function_message)

                # print(tool_results)

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

    def extract_text(self, model_turn) -> str:
        """Extract text content from a Mistral message."""
        return model_turn.content or ""

    def extract_function_calls(self, model_turn):
        """Extract the function_call part of a LLM (Actions)"""
        function_calls = None
        if model_turn.tool_calls is not None:
            for tool_call in model_turn.tool_calls:
                assistant_tool_message = {
                    "role": "assistant",
                    "content": model_turn.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in (
                            model_turn.tool_calls
                        )  # iterating over tools here
                    ],
                }
            function_calls = assistant_tool_message
            return function_calls

    def react_call(self, conversation, max_steps):

        # defining tool from self.args
        tools = list(self.args)

        for step in range(1, max_steps + 1):
            print(f"{BLUE}--- model turn {step} ---{RESET}")

            # Initial response from model
            response = self.client.chat.complete(
                model=self.model, messages=conversation, tools=tools, stream=False
            )

            # Defining model turn
            model_turn = response.choices[0].message

            # The text part from model
            thought = self.extract_text(model_turn)

            # Multiple or parallel function calls
            function_calls = self.extract_function_calls(model_turn)
            if function_calls is not None:
                # print(f"{GREEN}--- REASON ---{RESET}")
                # print(function_calls)
                conversation.append(function_calls)

            if thought:
                print(f"    [thought {step}]: {thought}")

            # Case where there is no tool_call - Exiting ReAct loop
            if not model_turn.tool_calls:
                return model_turn.content
                # then exit the ReAct loop

            # print(f"{GREEN}--- ACTION ---{RESET}")
            # print(function_calls["tool_calls"])

            if function_calls["tool_calls"] is not None:
                tool_calls = function_calls["tool_calls"]

                for tc in tool_calls:
                    # print("--------- loop hello ----------")
                    args = json.loads(tc["function"]["arguments"])
                    print(f"    [action {step}]: {tc["function"]["name"]}({args})")
                    tool_function = TOOL_SWITCH.get(tc["function"]["name"])

                    if tool_function is None:
                        result = f"Error: unknown tool '{tc["function"]["name"]}'"
                    else:
                        try:
                            result = tool_function(**args)
                        except Exception as exc:
                            result = f"Error in ReAct loop while running {tc["function"]["name"]}: {exc}"
                    # print(f"{GREEN}--- OBSERVATION ---{RESET}")
                    print(f"    [observation {step}]: {result}")

                    prepared_observation = {
                        "role": "tool",
                        "name": tc["function"]["name"],
                        "content": json.dumps(result),
                        "tool_call_id": tc["id"],
                    }

                    conversation.append(prepared_observation)
                # print(conversation)
        budget_content = "Reached the maximum number of reasoning steps without a final answer. Ask to finalize."
        budget_message = {"role": "assistant", "content": budget_content}
        conversation.append(budget_message)
        return budget_content
