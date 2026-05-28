class Agent:
    def __init__(self, name, model, api_key, temperature, role):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.role = role

    def __call__(self, message):

        response = f"You said: {message}"

        return response
