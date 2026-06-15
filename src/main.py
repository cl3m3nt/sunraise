import argparse
import json
from datetime import datetime
from pathlib import Path

from agent import Agent
from llm import (
    AnthropicProvider,
    DummyProvider,
    GoogleProvider,
    OpenAIProvider,
    MistralProvider,
)

from tools.weather import weather_tool
from tools.weather import mistral_weather_tool
from tools.weather import openai_weather_tool
from tools.current_time import current_time_tool
from tools.current_time import mistral_current_time_tool
from tools.current_time import openai_current_time_tool
from config import get_provider_config_map, get_google_config

from user import User

from dotenv import load_dotenv

# saving load_dotenv() as boolean for downstream check
isdotenv = load_dotenv()

# Config map with all provider configurations
PROVIDER_CONFIG_MAP = get_provider_config_map()


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

            # system instruction + tool config passed during LLM creation
            tools = [weather_tool, current_time_tool]
            google_config = get_google_config(tools)

            google_llm = GoogleProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
                google_config,
            )
            a = Agent("googleAgent", google_llm, "system")

        elif provider == "mistral":

            tools = [mistral_weather_tool, mistral_current_time_tool]
            mistral_config = None

            mistral_llm = MistralProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
                mistral_config,
                *tools,
            )
            a = Agent("mistralAgent", mistral_llm, "system")

        elif provider == "openai":

            tools = [openai_weather_tool, openai_current_time_tool]
            openai_config = None

            openai_llm = OpenAIProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
                openai_config,
                *tools,
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

            # For all provider
            # store current user - agent messages
            current_messages.append(user_message)
            # store all user - agent messages into full conversation
            conversation.append(user_message)

            # conversation exit condition
            if user_prompt == "exit" or user_prompt == "quit" or user_prompt == "/q":
                active_conversation = False

                # saving conversation locally
                print("Saving conversation")
                Path("conversation").mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")  # [:-3]
                with open(
                    f"conversation/conversation_{a.LLMProvider.name}_{timestamp}.json",
                    "w",
                ) as f:
                    json.dump(conversation, f)

                print("Bye!")

            # conversation loop
            else:
                try:

                    # agent_response = a(conversation)

                    if provider == "google":
                        agent_response = a(conversation)
                        agent_message = {
                            "role": "model",
                            "parts": [{"text": agent_response}],
                        }
                    elif provider == "mistral":
                        agent_response = a(conversation)

                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }
                    elif provider == "openai":
                        agent_response = a(conversation)

                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }
                    elif provider == "anthropic":
                        agent_response = a(conversation)

                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }
                    elif provider == "dummy":
                        agent_message = a(user_prompt)
                        agent_response = a(user_prompt)

                    print(f"[agent]:{agent_response}")

                    # appending agent_message to user-agent one turn messages
                    current_messages.append(agent_message)

                    # appending agent_message to full conversation
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
