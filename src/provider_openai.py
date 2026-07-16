from openai import OpenAI
import json
from llm import LLMProvider
from config import TOOL_SWITCH
from config import BLUE, RESET


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
            model=self.model, instructions=self.config, input=conversation, tools=tools
        )

        # tool_calls built from item
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if tool_calls:
            input_with_tools = list(response.output)

            # tool_result definition
            tool_results = []

            for tool_call in tool_calls:
                print("TOOL CALL:", tool_call.name, tool_call.arguments)
                tool_function = TOOL_SWITCH[tool_call.name]
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
                model=self.model,
                instructions=self.config,
                input=conversation + input_with_tools,
                tools=tools,
            )

            return response_with_tool.output_text

        else:
            return response.output_text

    def extract_text(self, model_turn):
        """Extract text content from an OpenAI message."""
        return model_turn.output_text

    def extract_function_calls(self, model_turn):
        # tool_calls built from item
        tool_calls = [
            item for item in model_turn.output if item.type == "function_call"
        ]
        return tool_calls

    def react_call(self, conversation, max_steps):
        """Extract the function_call part of a LLM (Actions)"""
        # defining tool from self.args
        tools = list(self.args)

        for step in range(1, max_steps + 1):

            # Initial response
            response = self.client.responses.create(
                model=self.model,
                instructions=self.config,
                input=conversation,
                tools=tools,
            )

            # Defining model turn
            model_turn = response
            print(f"{BLUE}--- model turn {step} ---{RESET}")

            # Extract Text
            thought = self.extract_text(model_turn)

            # Extract Tool calls
            tool_calls = self.extract_function_calls(model_turn)

            if thought:
                print(f"    [thought {step}]: {thought}")

            # Exiting ReAct loop
            if not tool_calls:
                return thought

            if tool_calls:
                input_with_tools = list(response.output)
                conversation.extend(input_with_tools)

            # Actions
            tool_results = []
            for tc in tool_calls:
                print(f"    [action {step}]: {tc.name}({tc.arguments})")
                tool_function = TOOL_SWITCH.get(tc.name)
                tool_function_args = json.loads(tc.arguments)

                if tool_function is None:
                    result = f"Error: unknown tool '{tc.name}'"
                else:
                    try:
                        result = tool_function(**tool_function_args)
                    except Exception as exc:
                        result = f"Error in ReAct loop while running {tc.name}: {exc}"
                print(f"    [observation {step}]: {result}")

                tool_result = {
                    "type": "function_call_output",
                    "call_id": tc.call_id,
                    "output": json.dumps(result),
                }

                tool_results.append(tool_result)

            conversation.extend(tool_results)

        budget_content = "Reached the maximum number of reasoning steps without a final answer. Ask to finalize."
        budget_message = {"role": "assistant", "content": budget_content}
        conversation.append(budget_message)

        return budget_content
