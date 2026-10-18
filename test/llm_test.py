import sys
from pathlib import Path

# Add the project root to sys.path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.llmprovider import AnthropicProvider,DummyProvider,GoogleProvider,OpenAIProvider,MistralProvider


if __name__ == "__main__":

    anthropic_cfg = {
        "name":"anthropic",
        "model":"claude",
        "api_key":"api_key",
        "temperature":0.5
    }

    dummy_cfg = {
        "name":"dummyLLM",
        "model":"dummyModel",
        "api_key":"api_key",
        "temperature":0.5
    }

    google_cfg = {
        "name":"google",
        "model":"gemini",
        "api_key":"api_key",
        "temperature":0.5
    }

    openai_cfg = {
        "name":"openai",
        "model":"gpt",
        "api_key":"api_key",
        "temperature":0.5
    }


    mistral_cfg = {
        "name":"mistral",
        "model":"mistral-mini",
        "api_key":"api_key",
        "temperature":0.5
    }

    a = AnthropicProvider(anthropic_cfg["name"],anthropic_cfg["model"],anthropic_cfg["api_key"],anthropic_cfg["temperature"])
    print(a.__dict__)
    print(a.provider)
    print(a.model)

    d = DummyProvider(dummy_cfg["name"],dummy_cfg["model"],dummy_cfg["api_key"],dummy_cfg["temperature"])
    print(d.__dict__)
    print(d.provider)
    print(d.model)

    g = GoogleProvider(google_cfg["name"],google_cfg["model"],google_cfg["api_key"],google_cfg["temperature"])
    print(g.__dict__)
    print(g.provider)
    print(g.model)

    o = OpenAIProvider(openai_cfg["name"],openai_cfg["model"],openai_cfg["api_key"],openai_cfg["temperature"])
    print(o.__dict__)
    print(o.provider)
    print(o.model)

    m = MistralProvider(mistral_cfg["name"],mistral_cfg["model"],mistral_cfg["api_key"],mistral_cfg["temperature"])
    print(m.__dict__)
    print(m.provider)
    print(m.model)