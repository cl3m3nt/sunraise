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
LLM_MODEL_MISTRAL = os.getenv("LLM_MODEL_MISTRAL")
API_KEY_MISTRAL = os.getenv("API_KEY_MISTRAL")


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Agent app")
    parser.add_argument(
        "--provider",
        type=str,
        help="provider name",
        choices=["dummy", "gemini", "claude", "gpt", "mistral"],
        default="dummy",
    )
    args = parser.parse_args()
    provider = args.provider

    # creating user
    u = User("test_user", "user")

    # creating agent
    if provider == "gemini":
        a = Agent("gemini", LLM_MODEL_GEMINI, API_KEY_GEMINI, 0.5, "system")
    elif provider == "claude":
        a = Agent("claude", LLM_MODEL_CLAUDE, API_KEY_CLAUDE, 0.5, "system")
    elif provider == "gpt":
        a = Agent("gpt", LLM_MODEL_GPT, API_KEY_GPT, 0.5, "system")
    elif provider == "mistral":
        a = Agent("mistral", LLM_MODEL_MISTRAL, API_KEY_MISTRAL, 0.5, "system")
    elif provider == "dummy":
        a = Agent("dummy", "llm_model", "api_key", 0.5, "system")

    # Getting started
    print(f"Built user and {a.name} agent...Starting conversation")

    active_conversation = True

    while active_conversation:
        user_prompt = input("[user]:")

        if user_prompt == "exit" or user_prompt == "quit" or user_prompt == "/q":
            active_conversation = False
            print("Bye!")
        else:
            if provider == "gemini":
                agent_response = a.call_gemini(user_prompt)
            elif provider == "claude":
                agent_response = a.call_claude(user_prompt)
            elif provider == "gpt":
                agent_response = a.call_gpt(user_prompt)
            elif provider == "mistral":
                agent_response = a.call_mistral(user_prompt)
            elif provider == "dummy":
                agent_response = a.call_dummy(user_prompt)
            print(f"[agent]:{agent_response}")
