from agent import Agent
from user import User
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Agent app")
    parser.add_argument(
        "--provider",
        type=str,
        help="provider name",
        choices=["dummy", "gemini"],
        default="dummy",
    )
    args = parser.parse_args()
    provider = args.provider

    # Getting started
    print("Building user and agent...")

    # creating user
    u = User("test_user", "user")

    # creating agent
    if provider == "gemini":
        a = Agent("test_agent", LLM_MODEL, LLM_API_KEY, 0.5, "system")
    elif provider == "dummy":
        a = Agent("test_agent", "llm_model", "api_key", 0.5, "system")

    print("Conversation...")
    active_conversation = True

    while active_conversation:
        user_prompt = input("[user]:")

        if user_prompt == "exit" or user_prompt == "quit":
            active_conversation = False
            print("Bye!")
        else:
            if provider == "gemini":
                agent_response = a.call_gemini(user_prompt)
            elif provider == "dummy":
                agent_response = a.call_dummy(user_prompt)
            print(f"[agent]:{agent_response}")
