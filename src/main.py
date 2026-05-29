from agent import Agent
from user import User
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

LLM_MODEL_GEMINI = os.getenv("LLM_MODEL_GEMINI")
API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")
LLM_MODEL_CLAUDE = os.getenv("LLM_MODEL_CLAUDE")
API_KEY_CLAUDE = os.getenv("API_KEY_CLAUDE")
LLM_MODEL_GPT = os.getenv("LLM_MODEL_GPT")
API_KEY_GPT = os.getenv("API_KEY_GPT")


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Agent app")
    parser.add_argument(
        "--provider",
        type=str,
        help="provider name",
        choices=["dummy", "gemini", "claude", "gpt"],
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
        a = Agent("test_agent", LLM_MODEL_GEMINI, API_KEY_GEMINI, 0.5, "system")
    elif provider == "claude":
        a = Agent("test_agent", LLM_MODEL_CLAUDE, API_KEY_CLAUDE, 0.5, "system")
    elif provider == "gpt":
        a = Agent("test_agent", LLM_MODEL_GPT, API_KEY_GPT, 0.5, "system")
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
            if provider == "claude":
                agent_response = a.call_claude(user_prompt)
            if provider == "gpt":
                agent_response = a.call_gpt(user_prompt)
            elif provider == "dummy":
                agent_response = a.call_dummy(user_prompt)
            print(f"[agent]:{agent_response}")
