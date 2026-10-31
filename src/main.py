import argparse
import logging
from agent import Agent
from banner import get_banner

from provider_anthropic import AnthropicProvider
from provider_dummy import DummyProvider
from provider_google import GoogleProvider
from provider_openai import OpenAIProvider
from provider_openllm import OpenLLMProvider
from provider_mistral import MistralProvider

from tools.weather import google_weather_tool
from tools.weather import openllm_weather_tool
from tools.weather import mistral_weather_tool
from tools.weather import openai_weather_tool
from tools.weather import anthropic_weather_tool
from tools.current_time import google_current_time_tool
from tools.current_time import openllm_current_time_tool
from tools.current_time import mistral_current_time_tool
from tools.current_time import openai_current_time_tool
from tools.current_time import anthropic_current_time_tool
from tools.read_skill import anthropic_read_skill_tool
from tools.read_skill import google_read_skill_tool
from tools.read_skill import openai_read_skill_tool
from tools.read_skill import openllm_read_skill_tool
from tools.read_skill import mistral_read_skill_tool


from config import SYSTEM_INSTRUCTION, REACT_SYSTEM_INSTRUCTION
from config import get_sunraise_version, get_provider_config_map
from config import build_anthropic_system_prompt
from config import build_google_config, build_google_react_config
from config import build_openai_system_prompt
from config import build_openllm_system_prompt
from config import build_mistral_system_prompt

from skills_loader import get_skills
from skills_loader import SKILLS_DIR

from mcp_client import MCPClient
from mcp_manager import MCPManager
from prepare_mcp_tools import prepare_mcp_google


from conversation import (
    save_conversation,
    serialize_google_conversation,
    serialize_openai_conversation,
    serialize_anthropic_conversation,
)

from user import User

from dotenv import load_dotenv

from config import YELLOW, RESET


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# logging.disable(logging.CRITICAL)

logger = logging.getLogger(__name__)

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
        choices=["anthropic", "dummy", "google", "openllm", "mistral", "openai"],
        default="dummy",
    )
    parser.add_argument(
        "--react",
        type=int,
        help="react iteration steps",
        choices=[3, 5, 7, 9, 100],
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

            tools = [
                anthropic_weather_tool,
                anthropic_current_time_tool,
                anthropic_read_skill_tool,
            ]

            skills = get_skills(SKILLS_DIR)

            if react is not None:
                anthropic_config = build_anthropic_system_prompt(
                    REACT_SYSTEM_INSTRUCTION, skills
                )
            else:
                anthropic_config = build_anthropic_system_prompt(
                    SYSTEM_INSTRUCTION, skills
                )

            anthropic_llm = AnthropicProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
                anthropic_config,
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

            # ------------------------------------
            # TOOLS SUBSECTION
            # ------------------------------------

            print("--------------- GETTING Tool(s)  ---------------")
            tools = [
                google_weather_tool,
                google_current_time_tool,
                google_read_skill_tool,
            ]
            tools_name = []
            for t in tools:
                tools_name.append(t["name"])
            logger.info(tools_name)

            # ------------------------------------
            # SKILLS SUBSECTION
            # ------------------------------------
            skills = get_skills(SKILLS_DIR)

            # ------------------------------------
            # MCP SUBSECTION
            # ------------------------------------
            # creating mcp client
            mcp_client_greetings = MCPClient()
            # creating mcp manager that takes clients input
            mcp_manager_greetings = MCPManager("greetings", mcp_client_greetings)
            # defining the mcp server module path
            mcp_server_path_greetings = "./mcp_servers/greetings/server.py"

            # creating mcp client
            mcp_client_arithm = MCPClient()
            # creating mcp manager that takes clients input
            mcp_manager_arithm = MCPManager("arithm", mcp_client_arithm)
            # defining the mcp server module path
            mcp_server_path_arithm = "./mcp_servers/arithm/server.py"

            # creating mcp client
            mcp_client_calendar = MCPClient()
            # creating mcp manager that takes clients input
            mcp_manager_calendar = MCPManager("calendar", mcp_client_calendar)
            # defining the mcp server module path
            mcp_server_path_calendar = "./mcp_servers/calendar/server.py"

            print("\n" + "--------------- STARTING MCP Manager(s) ---------------")
            # starting the MCP servers
            result_greetings = mcp_manager_greetings.start(mcp_server_path_greetings)
            result_arithm = mcp_manager_arithm.start(mcp_server_path_arithm)
            result_calendar = mcp_manager_calendar.start(mcp_server_path_calendar)

            mcp_managers = {
                mcp_manager_greetings.name: mcp_manager_greetings,
                mcp_manager_arithm.name: mcp_manager_arithm,
                mcp_manager_calendar.name: mcp_manager_calendar,
            }

            # Executing get_tools fom MCPManager
            tool_result_greetings = mcp_manager_greetings.get_tools()
            for t in tool_result_greetings:
                # print(t["description"])
                mcp_tool = prepare_mcp_google(t)
                tools.append(mcp_tool)

            # Executing get_tools fom MCPManager
            tool_result_arithm = mcp_manager_arithm.get_tools()
            print(tool_result_arithm)
            for t in tool_result_arithm:
                # print(t["description"])
                mcp_tool = prepare_mcp_google(t)
                tools.append(mcp_tool)

            # Executing get_tools fom MCPManager
            tool_result_calendar = mcp_manager_calendar.get_tools()
            print(tool_result_calendar)
            for t in tool_result_calendar:
                print(t["description"])
                mcp_tool = prepare_mcp_google(t)
                tools.append(mcp_tool)

            print("\n" + "--------------- LISTING local + mcp Tools ---------------")
            tools_name = []
            for t in tools:
                tools_name.append(t["name"])
            logger.info(tools_name)

            # ------------------------------------
            # GOOGLE SYSTEM INSTRUCTION
            # ------------------------------------

            if react is not None:
                google_config = build_google_react_config(
                    REACT_SYSTEM_INSTRUCTION, tools, skills
                )
            else:
                SYSTEM_INSTRUCTION_WITH_MCP = SYSTEM_INSTRUCTION

                for t in tool_result_greetings:
                    SYSTEM_INSTRUCTION_WITH_MCP = (
                        SYSTEM_INSTRUCTION_WITH_MCP
                        + "\n"
                        + "You can "
                        + t["description"]
                        + " "
                        + "with "
                        + t["name"]
                        + " tool."
                    )
                for t in tool_result_arithm:
                    SYSTEM_INSTRUCTION_WITH_MCP = (
                        SYSTEM_INSTRUCTION_WITH_MCP
                        + "\n"
                        + "You can "
                        + t["description"]
                        + " "
                        + "with "
                        + t["name"]
                        + " tool."
                    )

                for t in tool_result_calendar:
                    SYSTEM_INSTRUCTION_WITH_MCP = (
                        SYSTEM_INSTRUCTION_WITH_MCP
                        + "\n"
                        + "You can "
                        + t["description"]
                        + " "
                        + "with "
                        + t["name"]
                        + " tool."
                    )

                print(
                    "\n"
                    + "---------------BUILDING System instruction with MCP ----------------"
                )
                logger.info("\n" + SYSTEM_INSTRUCTION_WITH_MCP)
                google_config = build_google_config(
                    SYSTEM_INSTRUCTION_WITH_MCP, tools, skills
                )

            google_llm = GoogleProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["temperature"],
                google_config,
            )
            a = Agent("googleAgent", google_llm, "system")

        # ---------------------------------------------------------------------------
        # OPENLLM PROVIDER
        # ---------------------------------------------------------------------------
        elif provider == "openllm":

            # system instruction + tool config passed during LLM creation
            tools = [
                openllm_weather_tool,
                openllm_current_time_tool,
                openllm_read_skill_tool,
            ]

            if react is not None:
                openllm_config = REACT_SYSTEM_INSTRUCTION
            else:
                openllm_config = SYSTEM_INSTRUCTION

            openllm_llm = OpenLLMProvider(
                provider_cfg["name"],
                provider_cfg["model"],
                provider_cfg["api_key"],
                provider_cfg["base_url"],
                provider_cfg["temperature"],
                openllm_config,
                *tools,
            )
            a = Agent("openllmAgent", openllm_llm, "system")

        # ---------------------------------------------------------------------------
        # MISTRAL PROVIDER
        # ---------------------------------------------------------------------------
        elif provider == "mistral":

            tools = [
                mistral_weather_tool,
                mistral_current_time_tool,
                mistral_read_skill_tool,
            ]

            if react is not None:
                mistral_config = REACT_SYSTEM_INSTRUCTION
            else:
                mistral_config = SYSTEM_INSTRUCTION

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

            tools = [
                openai_weather_tool,
                openai_current_time_tool,
                openai_read_skill_tool,
            ]

            skills = get_skills(SKILLS_DIR)

            if react is not None:
                openai_config = build_openai_system_prompt(
                    REACT_SYSTEM_INSTRUCTION, skills
                )
            else:
                openai_config = build_openai_system_prompt(SYSTEM_INSTRUCTION, skills)

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

        # System Instruction initial configuration for Mistral and OpenLLM
        if provider == "mistral":

            skills = get_skills(SKILLS_DIR)
            system_prompt = build_mistral_system_prompt(a.LLMProvider.config, skills)
            conversation.append(system_prompt)

        elif provider == "openllm":
            skills = get_skills(SKILLS_DIR)
            system_prompt = build_openllm_system_prompt(a.LLMProvider.config, skills)
            conversation.append(system_prompt)

        while active_conversation:
            current_messages = []

            # ---------------------------------------------------------------------------
            # USER PROMPT MANAGEMENT
            # ---------------------------------------------------------------------------

            user_prompt = input("[user]:").strip()
            if user_prompt == "":
                continue

            if provider == "anthropic":
                user_message = {"role": "user", "content": user_prompt}
            elif provider == "dummy":
                user_message = user_prompt
            elif provider == "google":
                user_message = {"role": "user", "parts": [{"text": user_prompt}]}
            elif provider == "openllm":
                user_message = {"role": "user", "content": user_prompt}
            elif provider == "mistral":
                user_message = {"role": "user", "content": user_prompt}
            elif provider == "openai":
                user_message = {"role": "user", "content": user_prompt}

            # For all provider
            # store current user - agent messages
            current_messages.append(user_message)
            # store all user - agent messages into full conversation
            conversation.append(user_message)

            # conversation exit condition
            if user_prompt == "exit" or user_prompt == "quit" or user_prompt == "/q":
                active_conversation = False

                # saving conversation locally
                if react is None or (
                    provider != "google"
                    and provider != "openai"
                    and provider != "anthropic"
                ):
                    save_conversation(a, conversation)
                elif provider == "anthropic":
                    serialized_conversation = serialize_anthropic_conversation(
                        conversation
                    )
                    conversation_path = save_conversation(a, serialized_conversation)
                elif provider == "google":
                    serialized_conversation = serialize_google_conversation(
                        conversation
                    )
                    conversation_path = save_conversation(a, serialized_conversation)
                elif provider == "openllm":
                    serialized_conversation = serialize_google_conversation(
                        conversation
                    )
                    conversation_path = save_conversation(a, serialized_conversation)
                elif provider == "openai":
                    serialized_conversation = serialize_openai_conversation(
                        conversation
                    )
                    conversation_path = save_conversation(a, serialized_conversation)

                print("Bye!")

            # MCP server information
            elif user_prompt == "/mcp":
                if provider == "google":
                    print(f"MCP servers: {', '.join(mcp_managers)}")
                    for mcp_manager in mcp_managers.values():
                        print(
                            f"MCP server: {mcp_manager.name}, "
                            f"status: {mcp_manager.mcp_client.server_status}"
                        )
                        for t in mcp_manager.mcp_client.tools:
                            print(f"tool:{t["name"]}, {t["description"]}")
                else:
                    print("No MCP server available")

            # conversation loop
            else:

                try:

                    # ---------------------------------------------------------------------------
                    # GOOGLE AGENT PROCESSING - DEFAULT AND REACT
                    # ---------------------------------------------------------------------------

                    if provider == "google":

                        print(
                            f"{YELLOW}---- conversation step {conversation_index} ---{RESET}"
                        )
                        if not react:
                            # OPTION 1: ADDING MCP MANAGER here as an agent call ARG
                            agent_response = a(conversation, mcp_managers)

                        elif react:
                            agent_response = a.react_call(conversation, react)

                        agent_message = {
                            "role": "model",
                            "parts": [{"text": agent_response}],
                        }

                    # ---------------------------------------------------------------------------
                    # OPENLLM AGENT PROCESSING - DEFAULT AND REACT
                    # ---------------------------------------------------------------------------

                    if provider == "openllm":

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
                    # OPENAI AGENT PROCESSING - DEFAULT AND REACT
                    # ---------------------------------------------------------------------------

                    elif provider == "openai":
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
