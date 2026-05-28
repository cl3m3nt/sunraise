from agent import Agent
from user import User
import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

if __name__ == "__main__":

    print("Building user and agent...")

    u = User("test_user", "user")

    a = Agent("test_agent", LLM_MODEL, LLM_API_KEY, 0.5, "system")

    print("Conversation...")
    active_conversation = True

    while active_conversation:
        user_prompt = input("[user]:")

        if user_prompt == "exit" or user_prompt == "quit":
            active_conversation = False
            print("Bye!")
        else:
            agent_response = a.call_gemini(user_prompt)
            print(f"[agent]:{agent_response}")
