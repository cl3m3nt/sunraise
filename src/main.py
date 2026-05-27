from agent import Agent
from user import User

if __name__ == "__main__":

    print("Getting started...")

    u = User("test_user","user")
    print(u.__dict__)

    a = Agent("test_agent","model","api_key",0.5,"system")
    print(a.__dict__)