from llm import LLMProvider


class DummyProvider(LLMProvider):
    provider = "dummy"

    def __call__(self, message) -> str:
        response = f"You said: {message}"
        return response

    def extract_text(self, model_turn) -> str:
        return str(model_turn)

    def extract_function_calls(self, model_turn):
        return []

    def react_call(self, conversation, max_steps):
        return self(conversation)
