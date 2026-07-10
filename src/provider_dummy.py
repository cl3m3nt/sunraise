from llm import LLMProvider


class DummyProvider(LLMProvider):
    provider = "dummy"

    def __call__(self, message) -> str:
        response = f"You said: {message}"
        return response

    def extract_text(self, conversation, test):
        pass

    def extract_function_calls(self, conversation):
        pass

    def react_call(self, conversation, max_steps):
        pass
