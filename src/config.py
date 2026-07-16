from google.genai import types
import os
from dotenv import load_dotenv
from tools.weather import get_weather
from tools.current_time import get_current_time
from tools.read_skill import read_skill
from skills_loader import render_skills_catalog


load_dotenv()

SUNRAISE_VERSION = "v0.1.3"

LLM_MODEL_GEMINI = os.getenv("LLM_MODEL_GEMINI")
API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")

LLM_MODEL_OPENLLM = os.getenv("LLM_MODEL_OPENLLM")
API_KEY_OPENLLM = os.getenv("API_KEY_OPENLLM")
BASE_URL_OPENLLM = os.getenv("BASE_URL_OPENLLM")

LLM_MODEL_CLAUDE = os.getenv("LLM_MODEL_CLAUDE")
API_KEY_CLAUDE = os.getenv("API_KEY_CLAUDE")

LLM_MODEL_GPT = os.getenv("LLM_MODEL_GPT")
API_KEY_GPT = os.getenv("API_KEY_GPT")

LLM_MODEL_MISTRAL = os.getenv("LLM_MODEL_MISTRAL")
API_KEY_MISTRAL = os.getenv("API_KEY_MISTRAL")


TOOL_SWITCH = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "read_skill": read_skill,
}

BLUE = "\033[38;5;117m"
GREEN = "\033[38;5;46m"
YELLOW = "\033[38;5;220m"
RESET = "\033[0m"


def get_sunraise_version():
    return SUNRAISE_VERSION


# Config map with all provider configurations
def get_provider_config_map():

    PROVIDER_CONFIG_MAP = {
        "anthropic": {
            "name": "anthropic",
            "model": LLM_MODEL_CLAUDE,
            "api_key": API_KEY_CLAUDE,
            "temperature": 0,
        },
        "dummy": {
            "name": "dummy",
            "model": "dummy model",
            "api_key": "api",
            "temperature": 0,
        },
        "google": {
            "name": "google",
            "model": LLM_MODEL_GEMINI,
            "api_key": API_KEY_GEMINI,
            "temperature": 0,
        },
        "openllm": {
            "name": "openllm",
            "model": LLM_MODEL_OPENLLM,
            "base_url": BASE_URL_OPENLLM,
            "api_key": API_KEY_OPENLLM,
            "temperature": 0,
        },
        "mistral": {
            "name": "mistral",
            "model": LLM_MODEL_MISTRAL,
            "api_key": API_KEY_MISTRAL,
            "temperature": 0,
        },
        "openai": {
            "name": "openai",
            "model": LLM_MODEL_GPT,
            "api_key": API_KEY_GPT,
            "temperature": 0,
        },
    }
    return PROVIDER_CONFIG_MAP


# ---------------------------------------------------------------------------
# SYSTEM INSTRUCTIONS
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """
# System Instructions
You are a helpful assistant named Sunraise.
When weather is requested, you MUST use the get_weather tool.
When current time is requested, you MUST use get_current_time tool.
When a skill is requested, you MUST use read_skill tool.
""".strip()

REACT_SYSTEM_INSTRUCTION = """
# System Instructions
You are a helpful ReAct-style assistant named Sunraise.

Reason step by step. When you need external information, call a tool instead of
guessing. After you receive a tool result, decide whether you need another tool
call or whether you can give the final answer.

When weather is requested, you MUST use the get_weather tool.
When the current time is requested, you MUST use the get_current_time tool.
When a skill is requested, you MUST use read_skill tool.
""".strip()


def build_anthropic_system_prompt(system_instruction, skills):

    skills_catalog = render_skills_catalog(skills)

    system_prompt = system_instruction + "\n\n" + skills_catalog

    return system_prompt


def build_google_config(system_instruction, tools, skills):
    print("Using google default config.")
    if tools:
        tool_decl_list = []
        for tool in tools:
            if isinstance(tool, dict):
                tool_decl = types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"],
                )
                tool_decl_list.append(tool_decl)

            else:
                tool_decl = tool
                print(f"tool_decl:{tool_decl}")
                tool_decl_list.append(tool_decl)

        # LLM general config, system instruction + tools (optional)

        skills_catalog = render_skills_catalog(skills)

        system_instruction = system_instruction + "\n\n" + skills_catalog

        google_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[types.Tool(function_declarations=tool_decl_list)],
        )
    else:
        google_config = None

    return google_config


def build_google_react_config(system_instruction, tools, skills):
    print("Using google ReAct loop config.")
    if tools:
        tool_decl_list = []
        for tool in tools:
            if isinstance(tool, dict):
                tool_decl = types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"],
                )
                tool_decl_list.append(tool_decl)

            else:
                tool_decl = tool
                print(f"tool_decl:{tool_decl}")
                tool_decl_list.append(tool_decl)

        # LLM general config, system instruction + tools (optional)

        skills_catalog = render_skills_catalog(skills)
        system_instruction = system_instruction + "\n\n" + skills_catalog

        react_google_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[types.Tool(function_declarations=tool_decl_list)],
            temperature=0,
        )
    else:
        react_google_config = None

    return react_google_config


def build_openai_system_prompt(system_instruction, skills):

    skills_catalog = render_skills_catalog(skills)

    system_prompt = system_instruction + "\n\n" + skills_catalog

    return system_prompt


def build_openllm_system_prompt(system_instruction, skills):

    skills_catalog = render_skills_catalog(skills)

    system_instruction = system_instruction + "\n\n" + skills_catalog

    system_prompt = {"role": "developer", "content": system_instruction}

    return system_prompt


def build_mistral_system_prompt(system_instruction, skills):

    skills_catalog = render_skills_catalog(skills)

    system_instruction = system_instruction + "\n\n" + skills_catalog

    system_prompt = {"role": "system", "content": system_instruction}

    return system_prompt
