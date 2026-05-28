from agent import Agent
from user import User

if __name__ == "__main__":

    print("Building user and agent...")

    u = User("test_user", "user")

    a = Agent("test_agent", "model", "api_key", 0.5, "system")

    print("Conversation...")
    active_conversation = True

    while active_conversation:
        user_prompt = input("[user]:")

        if user_prompt == "exit" or user_prompt == "quit":
            active_conversation = False
            print("Bye!")
        else:
            agent_response = a(user_prompt)
            print(f"[agent]:{agent_response}")
