import uuid
from llm import LLMProvider


class Agent:
    def __init__(self, name: str, LLMProvider: LLMProvider, role: str):
        self.name = name
        self.LLMProvider = LLMProvider
        self.role = role
        self.identity = self.get_identity()

    def get_identity(self):
        identity = uuid.uuid4()
        return identity

    def __call__(self, message, mcp_managers: dict = None):
        if mcp_managers is None:
            return self.LLMProvider(message)
        return self.LLMProvider(message, mcp_managers)

    def extract_text(self, model_turn):
        return self.LLMProvider.extract_text(model_turn)

    def extract_function_calls(self, model_turn):
        return self.LLMProvider.extract_function_calls(model_turn)

    def react_call(self, message, mcp_managers, max_step):
        if mcp_managers is None:
            return self.LLMProvider(message)
        return self.LLMProvider.react_call(message, mcp_managers, max_step)
