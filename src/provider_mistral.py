from mistralai.client import Mistral
from llm import LLMProvider
import json
from config import TOOL_SWITCH
from config import BLUE, RESET


class MistralProvider(LLMProvider):
    provider = "mistral"

    def __init__(self, name, model, api_key, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = Mistral(api_key=self.api_key)
        self.config = config
        self.args = args

    def __call__(self, conversation, mcp_managers: dict) -> str:

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

                    if tool_call.function.name in TOOL_SWITCH:
                        tool_function = TOOL_SWITCH[tool_call.function.name]
                        tool_func_args = json.loads(tool_call.function.arguments)

                        result = tool_function(**tool_func_args)

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for GREETINGS server
                    # ------------------------------------

                    elif (
                        tool_call.function.name == "greetings"
                        or tool_call.function.name == "farewell"
                    ) and mcp_managers is not None:

                        tool_function = mcp_managers["greetings"].execute_tool

                        if tool_call.function.name == "greetings":
                            result = tool_function(
                                "greetings", json.loads(tool_call.function.arguments)
                            )
                        elif tool_call.function.name == "farewell":
                            result = tool_function(
                                "farewell", json.loads(tool_call.function.arguments)
                            )

                        print(f"{BLUE} greeting/farewell result:{result}{RESET}")

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for ARITHM server
                    # ------------------------------------

                    elif (
                        tool_call.function.name == "add"
                        or tool_call.function.name == "multiply"
                    ) and mcp_managers is not None:

                        tool_function = mcp_managers["arithm"].execute_tool

                        if tool_call.function.name == "add":
                            result = tool_function(
                                "add", json.loads(tool_call.function.arguments)
                            )
                        elif tool_call.function.name == "multiply":
                            result = tool_function(
                                "multiply", json.loads(tool_call.function.arguments)
                            )

                        print(f"{BLUE} add/multiply result:{result}{RESET}")

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for CALENDAR server
                    # ------------------------------------
                    elif (
                        tool_call.function.name == "get_calendar_events"
                    ) and mcp_managers is not None:

                        tool_function = mcp_managers["calendar"].execute_tool

                        if tool_call.function.name == "get_calendar_events":
                            result = tool_function(
                                "get_calendar_events",
                                json.loads(tool_call.function.arguments),
                            )

                        print(f"{BLUE} get calendar events result:{result}{RESET}")

                    else:
                        result = f"Error: unknown tool '{tool_call.function.name}'"

                    function_message = {
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id,
                    }

                    # adding function message to tool_results
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

    def react_call(self, conversation, mcp_managers, max_steps):

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
                conversation.append(function_calls)

            if thought:
                print(f"    [thought {step}]: {thought}")

            # Case where there is no tool_call - Exiting ReAct loop
            if not model_turn.tool_calls:
                return model_turn.content

            if function_calls["tool_calls"] is not None:
                tool_calls = function_calls["tool_calls"]

                for tc in tool_calls:
                    args = json.loads(tc["function"]["arguments"])
                    print(f"    [action {step}]: {tc["function"]["name"]}({args})")
                    tool_function = TOOL_SWITCH.get(tc["function"]["name"])

                    if tc["function"]["name"] in TOOL_SWITCH:
                        try:
                            result = tool_function(**args)
                        except Exception as exc:
                            result = f"Error in ReAct loop while running {tc["function"]["name"]}: {exc}"

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for GREETINGS server
                    # ------------------------------------

                    elif (
                        tc["function"]["name"] == "greetings"
                        or tc["function"]["name"] == "farewell"
                    ) and mcp_managers is not None:

                        tool_function = mcp_managers["greetings"].execute_tool

                        if tc["function"]["name"] == "greetings":
                            result = tool_function("greetings", args)
                        elif tc["function"]["name"] == "farewell":
                            result = tool_function("farewell", args)

                        print(f"{BLUE} greeting/farewell result:{result}{RESET}")

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for ARITHM server
                    # ------------------------------------

                    elif (
                        tc["function"]["name"] == "add"
                        or tc["function"]["name"] == "multiply"
                    ) and mcp_managers is not None:

                        tool_function = mcp_managers["arithm"].execute_tool

                        if tc["function"]["name"] == "add":
                            result = tool_function("add", args)
                        elif tc["function"]["name"] == "multiply":
                            result = tool_function("multiply", args)

                        print(f"{BLUE} add/multiply result:{result}{RESET}")

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for CALENDAR server
                    # ------------------------------------

                    elif (
                        tc["function"]["name"] == "get_calendar_events"
                    ) and mcp_managers is not None:

                        tool_function = mcp_managers["calendar"].execute_tool

                        if tc["function"]["name"] == "get_calendar_events":
                            result = tool_function("get_calendar_events", args)

                        print(f"{BLUE} get calendar events result:{result}{RESET}")

                    else:
                        result = f"Error: unknown tool '{tc["function"]["name"]}'"

                    print(f"    [observation {step}]: {result}")

                    prepared_observation = {
                        "role": "tool",
                        "name": tc["function"]["name"],
                        "content": json.dumps(result),
                        "tool_call_id": tc["id"],
                    }

                    conversation.append(prepared_observation)
        budget_content = "Reached the maximum number of reasoning steps without a final answer. Ask to finalize."
        budget_message = {"role": "assistant", "content": budget_content}
        conversation.append(budget_message)
        return budget_content
