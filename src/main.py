import argparse
from agent import Agent
from banner import get_banner
from llm import (
    AnthropicProvider,
    DummyProvider,
    GoogleProvider,
    OpenAIProvider,
    MistralProvider,
)

from tools.weather import google_weather_tool
from tools.weather import mistral_weather_tool
from tools.weather import openai_weather_tool
from tools.weather import anthropic_weather_tool
from tools.current_time import google_current_time_tool
from tools.current_time import mistral_current_time_tool
from tools.current_time import openai_current_time_tool
from tools.current_time import anthropic_current_time_tool
from config import get_sunraise_version, get_provider_config_map
from config import build_google_config, build_google_react_config

from conversation import save_conversation, serialize_conversation

from user import User

from dotenv import load_dotenv

# saving load_dotenv() as boolean for downstream check
isdotenv = load_dotenv()

# Config map with all provider configurations
PROVIDER_CONFIG_MAP = get_provider_config_map()


# ---------------------------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # sunrAIse banner
    sunraise_version = get_sunraise_version()
    get_banner(sunraise_version)

    # parsing arguments
    parser = argparse.ArgumentParser(description="Agent app")
    parser.add_argument(
        "--provider",
        type=str,
        help="provider name",
        choices=["anthropic", "dummy", "google", "mistral", "openai"],
        default="dummy",
    )
    parser.add_argument(
        "--react",
        type=int,
        help="react iteration steps",
        choices=[3, 5, 7, 9],
        default=None,
    )
    args = parser.parse_args()
    provider = args.provider
    react = args.react

    # creating user
    u = User("test_user", "user")

    # load config from map
    provider_cfg = PROVIDER_CONFIG_MAP[provider]

    if isdotenv:

        # ---------------------------------------------------------------------------
        # ANTHROPIC PROVIDER
        # ---------------------------------------------------------------------------
        if provider == "anthropic":

            tools = [anthropic_weather_tool, anthropic_current_time_tool]

            anthropic_llm = AnthropicProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
                *tools,
            )
            a = Agent("anthropicAgent", anthropic_llm, "system")

        # ---------------------------------------------------------------------------
        # DUMMY PROVIDER
        # ---------------------------------------------------------------------------
        elif provider == "dummy":

            dummy_llm = DummyProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
            )
            a = Agent("dummyAgent", dummy_llm, "system")

        # ---------------------------------------------------------------------------
        # GOOGLE PROVIDER
        # ---------------------------------------------------------------------------
        elif provider == "google":

            # system instruction + tool config passed during LLM creation
            tools = [google_weather_tool, google_current_time_tool]

            if react is not None:
                google_config = build_google_react_config(tools)
            else:
                google_config = build_google_config(tools)

            google_llm = GoogleProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
                google_config,
            )
            a = Agent("googleAgent", google_llm, "system")

        # ---------------------------------------------------------------------------
        # MISTRAL PROVIDER
        # ---------------------------------------------------------------------------
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

        # ---------------------------------------------------------------------------
        # OPENAI PROVIDER
        # ---------------------------------------------------------------------------
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

        print(f"Created {a.LLMProvider.provider} agent with {a.LLMProvider.model} LLM.")

        # ---------------------------------------------------------------------------
        # MAIN CONVERSATION LOOP
        # ---------------------------------------------------------------------------

        active_conversation = True

        conversation = []

        conversation_index = 0

        while active_conversation:
            current_messages = []

            # ---------------------------------------------------------------------------
            # USER PROMPT MANAGEMENT
            # ---------------------------------------------------------------------------

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
                if provider != "google" or react is None:
                    save_conversation(a, conversation)
                else:
                    serialized_conversation = serialize_conversation(conversation)
                    conversation_path = save_conversation(a, serialized_conversation)

                print("Bye!")

            # conversation loop
            else:
                try:

                    YELLOW = "\033[38;5;220m"  # yellow
                    RESET = "\033[0m"

                    # ---------------------------------------------------------------------------
                    # GOOGLE AGENT PROCESSING - DEFAULT AND REACT
                    # ---------------------------------------------------------------------------

                    if provider == "google":

                        print(
                            f"{YELLOW}---- conversation step {conversation_index} ---{RESET}"
                        )
                        if not react:
                            agent_response = a(conversation)

                        elif react:
                            agent_response = a.react_call(conversation, react)

                        agent_message = {
                            "role": "model",
                            "parts": [{"text": agent_response}],
                        }

                    # ---------------------------------------------------------------------------
                    # MISTRAL AGENT PROCESSING - DEFAULT AND REACT
                    # ---------------------------------------------------------------------------

                    elif provider == "mistral":

                        print(
                            f"{YELLOW}---- conversation step {conversation_index} ---{RESET}"
                        )

                        if not react:
                            agent_response = a(conversation)

                            agent_message = {
                                "role": "assistant",
                                "content": agent_response,
                            }

                        elif react:
                            agent_response = a.react_call(conversation, react)
                            agent_message = {
                                "role": "assistant",
                                "content": agent_response,
                            }

                    # ---------------------------------------------------------------------------
                    # OTHER PROVIDER PROCESSING - DEFAULT
                    # ---------------------------------------------------------------------------

                    elif provider == "openai":
                        agent_response = a(conversation)

                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }

                    # ---------------------------------------------------------------------------
                    # ANTHROPIC AGENT PROCESSING - DEFAULT AND REACT
                    # ---------------------------------------------------------------------------
                    elif provider == "anthropic":
                        print(
                            f"{YELLOW}---- conversation step {conversation_index} ---{RESET}"
                        )
                        if not react:
                            agent_response = a(conversation)

                        elif react:
                            agent_response = a.react_call(conversation, react)

                        agent_message = {
                            "role": "assistant",
                            "content": agent_response,
                        }

                    # ---------------------------------------------------------------------------
                    # DUMMY AGENT PROCESSING - DEFAULT
                    # ---------------------------------------------------------------------------

                    elif provider == "dummy":
                        agent_message = a(user_prompt)
                        agent_response = a(user_prompt)

                    # ---------------------------------------------------------------------------
                    # AGENT RESPONSE PRINT
                    # ---------------------------------------------------------------------------

                    print(f"[agent]:{agent_response}")

                    # appending agent_message to user-agent one turn messages
                    current_messages.append(agent_message)

                    # ---------------------------------------------------------------------------
                    # CONVERSATION AND GLOBAL TURN MANAGEMENT
                    # ---------------------------------------------------------------------------

                    # appending agent_message to full conversation
                    if provider != "google" or react is None:
                        conversation.append(agent_message)

                    # print("---- current conversation ----")
                    # print(conversation)
                    conversation_index = conversation_index + 1

                # ---------------------------------------------------------------------------
                # CONVERSATION AND GLOBAL TURN MANAGEMENT
                # ---------------------------------------------------------------------------

                except Exception as e:
                    print(
                        "There was an error while calling LLM API. Safe exit. More info:"
                    )
                    print(e)
                    active_conversation = False

    # ---------------------------------------------------------------------------
    # CONVERSATION FOR DUMMY
    # ---------------------------------------------------------------------------

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
