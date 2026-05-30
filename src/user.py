import uuid


class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.identity = self.get_identity()

    def get_identity(self):
        identity = uuid.uuid4()
        return identity
