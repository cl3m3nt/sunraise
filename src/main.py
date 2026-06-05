import argparse
import os
import json
from datetime import datetime


from agent import Agent
from llm import (
    AnthropicProvider,
    DummyProvider,
    GoogleProvider,
    OpenAIProvider,
    MistralProvider,
)
from user import User

from dotenv import load_dotenv

# saving load_dotenv() as boolean for downstream check
isdotenv = load_dotenv()

LLM_MODEL_GEMINI = os.getenv("LLM_MODEL_GEMINI")
API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")
LLM_MODEL_CLAUDE = os.getenv("LLM_MODEL_CLAUDE")
API_KEY_CLAUDE = os.getenv("API_KEY_CLAUDE")
LLM_MODEL_GPT = os.getenv("LLM_MODEL_GPT")
API_KEY_GPT = os.getenv("API_KEY_GPT")
LLM_MODEL_MISTRAL = os.getenv("LLM_MODEL_MISTRAL")
API_KEY_MISTRAL = os.getenv("API_KEY_MISTRAL")

# Config map with all provider configurations
PROVIDER_CONFIG_MAP = {
    "anthropic": {
        "name": "anthropic",
        "model": LLM_MODEL_CLAUDE,
        "api_key": API_KEY_CLAUDE,
        "temperature": 0.5,
    },
    "dummy": {
        "name": "dummy",
        "model": "dummy model",
        "api_key": "api",
        "temperature": 0.5,
    },
    "google": {
        "name": "google",
        "model": LLM_MODEL_GEMINI,
        "api_key": API_KEY_GEMINI,
        "temperature": 0.5,
    },
    "mistral": {
        "name": "mistral",
        "model": LLM_MODEL_MISTRAL,
        "api_key": API_KEY_MISTRAL,
        "temperature": 0.5,
    },
    "openai": {
        "name": "openai",
        "model": LLM_MODEL_GPT,
        "api_key": API_KEY_GPT,
        "temperature": 0.5,
    },
}


# helper to debug conversation
def debug_conversation(current_messages, conversation):
    print("\n")
    print("Debug:")
    print("[current messages]:")
    print(current_messages)
    print("[conversation]:")
    print(conversation)
    print("\n")


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Agent app")
    parser.add_argument(
        "--provider",
        type=str,
        help="provider name",
        choices=["anthropic", "dummy", "google", "mistral", "openai"],
        default="dummy",
    )
    args = parser.parse_args()
    provider = args.provider

    # creating user
    u = User("test_user", "user")

    # load config from map
    provider_cfg = PROVIDER_CONFIG_MAP[provider]

    if isdotenv:

        # creating agent
        if provider == "anthropic":

            anthropic_llm = AnthropicProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
            )
            a = Agent("anthropicAgent", anthropic_llm, "system")

        elif provider == "dummy":

            dummy_llm = DummyProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
            )
            a = Agent("dummyAgent", dummy_llm, "system")

        elif provider == "google":

            google_llm = GoogleProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
            )
            a = Agent("googleAgent", google_llm, "system")

        elif provider == "mistral":

            mistral_llm = MistralProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
            )
            a = Agent("mistralAgent", mistral_llm, "system")

        elif provider == "openai":

            openai_llm = OpenAIProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
            )

            a = Agent("openaiAgent", openai_llm, "system")

        print(f"Created {a.LLMProvider.provider} agent with {a.LLMProvider.model} LLM")

        active_conversation = True

        conversation = []

        while active_conversation:
            current_messages = []
            user_prompt = input("[user]:")
            if provider == "google":
                user_message = {"role": "user", "parts": [{"text": user_prompt}]}
            elif provider == "mistral":
                user_message = {"role": "user", "content": user_prompt}
            elif provider == "openai":
                user_message = {"role": "user", "content": user_prompt}
            elif provider == "anthropic":
                user_message = {"role": "user", "content": user_prompt}
            # print(user_message)
            elif provider == "dummy":
                user_message = user_prompt

            # for all provider
            current_messages.append(user_message)
            conversation.append(user_message)

            if user_prompt == "exit" or user_prompt == "quit" or user_prompt == "/q":
                active_conversation = False
                # saving conversation locally
                print("Saving conversation")
                with open(
                    f"conversation/conversation_{a.LLMProvider.name}_{datetime.now()}.json",
                    "w",
                ) as f:
                    json.dump(conversation, f)

                print("Bye!")
            else:
                try:

                    agent_response = a(conversation)

                    if provider == "google":
                        agent_message = {
                            "role": "model",
                            "parts": [{"text": agent_response}],
                        }
                    elif provider == "mistral":
                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }
                    elif provider == "openai":
                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }
                    elif provider == "anthropic":
                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }
                    elif provider == "dummy":
                        agent_message = a(user_prompt)
                        agent_response = a(user_prompt)

                    print(f"[agent]:{agent_response}")
                    # print(agent_message)
                    current_messages.append(agent_message)
                    conversation.append(agent_message)

                except Exception as e:
                    print(
                        "There was an error while calling LLM API. Safe exit. More info:"
                    )
                    print(e)
                    active_conversation = False

                # debug_conversation(
                # current_messages=current_messages, conversation=conversation
                # )
    else:
        if provider == "dummy":

            dummy_llm = DummyProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
            )
            a = Agent("dummyAgent", dummy_llm, "system")

            active_conversation = True

            while active_conversation:
                user_prompt = input("[user]:")

                if (
                    user_prompt == "exit"
                    or user_prompt == "quit"
                    or user_prompt == "/q"
                ):
                    active_conversation = False
                    print("Bye!")
                else:
                    agent_response = a(user_prompt)
                    print(f"[agent]:{agent_response}")

        else:
            print("There is no .env file and provider is not dummy model. Safe exit.")
