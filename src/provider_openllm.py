from openai import OpenAI
import json
from llm import LLMProvider
from tools.weather import get_weather
from tools.current_time import get_current_time
from tools.read_skill import read_skill

from config import TOOL_SWITCH
from config import BLUE, RESET


class OpenLLMProvider(LLMProvider):
    provider = "openLLM"

    def __init__(self, name, model, api_key, base_url, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.base_url = base_url  # extra base_url attribute for open llm local model
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.config = config
        self.args = args

    def __call__(self, conversation) -> str:
        # defining tool from self.args
        tools = list(self.args)

        # initial response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=conversation,
            temperature=self.temperature,
            tools=tools,
        )

        message = response.choices[0].message

        # tool_calls built from item - similar to MistralAI api definition
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
                    "read_skill": read_skill,
                }

                # the assistant_tool_message is required in the conversation by Mistral API
                assistant_tool_message = {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",  # expected by openai chatCompletion endpoint, different from Mistral
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

                # final response
                response_with_tool = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation + tool_results,
                    temperature=self.temperature,
                    tools=tools,
                    stream=False,
                )

                return response_with_tool.choices[0].message.content

        else:
            return response.choices[0].message.content

    def extract_text(self, model_turn) -> str:
        """Extract text content from an openai compatible message."""
        return model_turn.choices[0].message.content or ""

    def extract_function_calls(self, model_turn):
        """Extract the function_call part of a LLM (Actions)"""
        function_calls = None
        if model_turn.choices[0].message.tool_calls:
            for tool_call in model_turn.choices[0].message.tool_calls:
                assistant_tool_message = {
                    "role": "assistant",
                    "content": model_turn.choices[0].message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",  # expected by openai chatCompletion endpoint, different from Mistral
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in (
                            model_turn.choices[0].message.tool_calls
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=conversation,
                temperature=self.temperature,
                tools=tools,
            )

            model_turn = response.choices[0].message
            # The text part from model
            thought = self.extract_text(response)

            # Multiple or parallel function calls
            function_calls = self.extract_function_calls(response)

            if thought:
                print(f"    [thought {step}]: {thought}")

            # Exiting ReAct loop
            if not function_calls:
                return thought

            # Appending function calls to conversation
            if function_calls is not None:
                conversation.append(function_calls)

            # Actions
            tool_results = []
            # Appending tool results to conversation

            for tc in model_turn.tool_calls:

                print(
                    f"    [action {step}]: {tc.function.name}({tc.function.arguments})"
                )
                tool_function = TOOL_SWITCH.get(tc.function.name)
                tool_function_args = json.loads(tc.function.arguments)

                if tool_function is None:
                    result = f"Error: unknown tool '{tc.function.name}'"

                else:
                    try:
                        result = tool_function(**tool_function_args)
                    except Exception as exc:
                        result = f"Error in ReAct loop while running {tc.function.name}: {exc}"
                print(f"    [observation {step}]: {result}")

                tool_result = {
                    "role": "tool",
                    "name": tc.function.name,
                    "content": json.dumps(result),
                    "tool_call_id": tc.id,
                }

                tool_results.append(tool_result)

            conversation.extend(tool_results)

        budget_content = "Reached the maximum number of reasoning steps without a final answer. Ask to finalize."
        budget_message = {"role": "assistant", "content": budget_content}
        conversation.append(budget_message)
        return budget_content
