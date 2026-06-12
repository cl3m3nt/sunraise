from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL_GEMINI = os.getenv("LLM_MODEL_GEMINI")
API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")
LLM_MODEL_CLAUDE = os.getenv("LLM_MODEL_CLAUDE")
API_KEY_CLAUDE = os.getenv("API_KEY_CLAUDE")
LLM_MODEL_GPT = os.getenv("LLM_MODEL_GPT")
API_KEY_GPT = os.getenv("API_KEY_GPT")
LLM_MODEL_MISTRAL = os.getenv("LLM_MODEL_MISTRAL")
API_KEY_MISTRAL = os.getenv("API_KEY_MISTRAL")


# Config map with all provider configurations
def get_provider_config_map():

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
    return PROVIDER_CONFIG_MAP


def get_google_config(tools):
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

        google_config = types.GenerateContentConfig(
            system_instruction="""
            You are a helpful assistant.

            When weather is requested, you MUST use the get_weather tool.
            When current time is requested, you MUST use get_current_time tool.
            """,
            tools=[types.Tool(function_declarations=tool_decl_list)],
        )
    else:
        google_config = None

    return google_config
