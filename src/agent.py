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
