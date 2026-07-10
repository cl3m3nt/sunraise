from abc import ABC, abstractmethod


class LLMProvider(ABC):

    def __init__(self, name, model, api_key, temperature):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

    @abstractmethod
    def __call__(self, message):
        pass

    @abstractmethod
    def extract_text(self, conversation, test):
        pass

    @abstractmethod
    def extract_function_calls(self, conversation):
        pass

    @abstractmethod
    def react_call(self, conversation, max_steps):
        pass
