from google import genai
from google.genai import types
from llm import LLMProvider

from config import TOOL_SWITCH
from config import BLUE, RESET


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

        texts = []

        for part in model_turn.parts:
            if getattr(part, "text", None):
                text = part.text
                # print(f"{BLUE}---- text ----{RESET}")
                # print(text)
                texts.append(text)

        return "\n".join(texts).strip()

    def extract_function_calls(self, model_turn):
        """Extract the function_call part of a LLM (Actions)"""

        function_calls = []

        for part in model_turn.parts:

            if getattr(part, "function_call", None):
                function_call = part.function_call
                function_calls.append(function_call)

        return function_calls

    def react_call(self, conversation, max_steps):

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
