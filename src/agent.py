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

    def __call__(self, message):
        return self.LLMProvider(message)

    def extract_text(self, model_turn):
        return self.LLMProvider.extract_text(model_turn)

    def extract_function_call(self, model_turn):
        return self.LLMProvider.extract_function_call(model_turn)

    def react_call(self, message, max_step):
        return self.LLMProvider.react_call(message, max_step)
