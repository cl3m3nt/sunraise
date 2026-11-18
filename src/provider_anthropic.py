import anthropic
from llm import LLMProvider
import json
from config import TOOL_SWITCH
from config import BLUE, RESET


class AnthropicProvider(LLMProvider):
    provider = "anthropic"

    def __init__(self, name, model, api_key, temperature, config, *args):
        super().__init__(name, model, api_key, temperature)
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.config = config
        self.args = args

    def __call__(self, conversation, mcp_managers: dict):

        # defining tool from self.args
        tools = list(self.args)

        # initial response
        response = self.client.messages.create(
            model=self.model,
            system=self.config,
            max_token=1000,
            # max_tokens=16000, # enough for thinking + response
            # output_config={"effort": "low"}, # low effort thinking
            # cache_control={"type": "ephemeral"}, # cache system + tool + history
            messages=conversation,
            tools=tools,
        )

        # tool_calls built from block
        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if tool_calls:
            prepared_input_with_tools = []
            prepared_input_with_tools.append(
                {"role": "assistant", "content": response.content}
            )

            # tool_result definition
            tool_results = []

            for tool_call in tool_calls:
                print("TOOL CALL:", tool_call.name, tool_call.input)

                if tool_call.name in TOOL_SWITCH:
                    tool_function = TOOL_SWITCH[tool_call.name]
                    print(f"{BLUE}tool_function:{tool_function}{RESET}")
                    tool_function_args = tool_call.input
                    result = tool_function(**tool_function_args)

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for GREETINGS server
                    # ------------------------------------

                elif (
                    tool_call.name == "greetings" or tool_call.name == "farewell"
                ) and mcp_managers is not None:

                    tool_function = mcp_managers["greetings"].execute_tool
                    tool_function_args = tool_call.input

                    if tool_call.name == "greetings":
                        result = tool_function("greetings", tool_function_args)
                    elif tool_call.name == "farewell":
                        result = tool_function("farewell", tool_function_args)

                    print(f"{BLUE} greeting/farewell result:{result}{RESET}")

                # ------------------------------------
                # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for ARITHM server
                # ------------------------------------

                elif (
                    tool_call.name == "add" or tool_call.name == "multiply"
                ) and mcp_managers is not None:

                    tool_function = mcp_managers["arithm"].execute_tool
                    tool_function_args = tool_call.input

                    if tool_call.name == "add":
                        result = tool_function("add", tool_function_args)
                    elif tool_call.name == "multiply":
                        result = tool_function("multiply", tool_function_args)

                    print(f"{BLUE} add/multiply result:{result}{RESET}")

                # ------------------------------------
                # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for CALENDAR server
                # ------------------------------------
                elif (
                    tool_call.name == "get_calendar_events"
                ) and mcp_managers is not None:

                    tool_function = mcp_managers["calendar"].execute_tool
                    tool_function_args = tool_call.input

                    if tool_call.name == "get_calendar_events":
                        result = tool_function(
                            "get_calendar_events", tool_function_args
                        )

                    print(f"{BLUE} get calendar events result:{result}{RESET}")

                else:
                    result = f"Error: unknown tool '{tool_call.name}'"

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
                system=self.config,
                max_tokens=1000,
                messages=conversation + prepared_input_with_tools,
                tools=tools,
            )
            return response_with_tool.content[0].text

        else:

            return response.content[0].text

    def extract_text(self, model_turn) -> str:
        """Extract text content from an Anthropic message."""
        texts = [
            block.text for block in model_turn.content if getattr(block, "text", None)
        ]
        return "\n".join(texts).strip()

    def extract_function_calls(self, model_turn):
        """Extract the tool_call of the LLM (Actions)"""
        tool_calls = [block for block in model_turn.content if block.type == "tool_use"]
        return tool_calls

    def react_call(self, conversation, mcp_managers, max_steps):

        # defining tool from self.args
        tools = list(self.args)

        for step in range(1, max_steps + 1):

            # Initial response from model
            response = self.client.messages.create(
                model=self.model,
                system=self.config,
                max_token=1000,
                # max_tokens=16000, # enough for thinking + response
                # output_config={"effort": "low"}, # low effort thinking
                # cache_control={"type": "ephemeral"}, # cache system + tool + history
                messages=conversation,
                tools=tools,
            )

            # Defining model turn
            model_turn = response
            print(f"{BLUE}--- model turn {step} ---{RESET}")
            # print(model_turn)

            # Extract Text
            thought = self.extract_text(model_turn)

            # Extract Tool calls
            tool_calls = self.extract_function_calls(model_turn)

            if thought:
                print(f"    [thought {step}]: {thought}")

            # Exiting ReAct loop
            if not tool_calls:
                return thought

            # Preparing input with tool calls
            if tool_calls:
                conversation.append({"role": "assistant", "content": response.content})

            # Actions
            tool_results = []
            for tc in tool_calls:
                tool_function_args = tc.input

                if tc.name in TOOL_SWITCH:
                    print(f"    [action {step}]: {tc.name}({tc.input})")
                    tool_function = TOOL_SWITCH.get(tc.name)
                    try:
                        result = tool_function(**tool_function_args)
                    except Exception as exc:
                        result = f"Error in ReAct loop while running {tc.name}: {exc}"

                    # ------------------------------------
                    # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for GREETINGS server
                    # ------------------------------------

                elif (
                    tc.name == "greetings" or tc.name == "farewell"
                ) and mcp_managers is not None:

                    tool_function = mcp_managers["greetings"].execute_tool

                    if tc.name == "greetings":
                        result = tool_function("greetings", tool_function_args)
                    elif tc.name == "farewell":
                        result = tool_function("farewell", tool_function_args)

                    print(f"{BLUE} greeting/farewell result:{result}{RESET}")

                # ------------------------------------
                # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for ARITHM server
                # ------------------------------------

                elif (
                    tc.name == "add" or tc.name == "multiply"
                ) and mcp_managers is not None:

                    tool_function = mcp_managers["arithm"].execute_tool

                    if tc.name == "add":
                        result = tool_function("add", tool_function_args)
                    elif tc.name == "multiply":
                        result = tool_function("multiply", tool_function_args)

                    print(f"{BLUE} add/multiply result:{result}{RESET}")

                # ------------------------------------
                # INSTANTIATING TOOL_FUNCTION FROM MCP_MANAGER for CALENDAR server
                # ------------------------------------

                elif (tc.name == "get_calendar_events") and mcp_managers is not None:

                    tool_function = mcp_managers["calendar"].execute_tool

                    if tc.name == "get_calendar_events":
                        result = tool_function(
                            "get_calendar_events", tool_function_args
                        )

                    print(f"{BLUE} get calendar events result:{result}{RESET}")

                else:
                    result = f"Error: unknown tool '{tc.name}'"

                print(f"    [observation {step}]: {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tc.id,
                        "content": json.dumps(result),
                    }
                )

            # all tool_result concatenated as prepared_tool_result
            if tool_results:
                prepared_tool_result = {"role": "user", "content": tool_results}

                conversation.append(prepared_tool_result)

        budget_content = "Reached the maximum number of reasoning steps without a final answer. Ask to finalize."
        budget_message = {"role": "user", "content": budget_content}
        conversation.append(budget_message)
        return budget_content
