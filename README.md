# Sunraise

A modular Python CLI for multi-turn conversations with LLM agents. Sunraise wraps several providers behind a shared `Agent` / `LLMProvider` interface.

## What it does

- Runs an interactive chat loop from the terminal
- Supports **Anthropic**, **Google**, **OpenAI**, **Mistral**, and a **dummy** provider for local testing without API keys

## Project structure

```
sunraise/
├── src/
│   ├── main.py              # CLI entry point (multi-turn chat)
│   ├── agent.py             # Agent wrapper around an LLM provider
│   ├── llm.py               # Provider implementations (Anthropic, Google, OpenAI, Mistral, Dummy)
│   ├── user.py              # User identity model
└── requirements.txt
```

## Prerequisites

- Python 3.10+
- API keys for the providers you plan to use (not required for `--provider dummy`)

## Setup

1. Clone the repository and enter the project directory:

```bash
cd /sunraise
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
pip install anthropic openai mistralai requests
```

4. IMPORTANT: Create a `.env` file in `src/` with your API keys and model names (see table below).
API keys are free for Google Gemini and Mistral AI:
https://aistudio.google.com/api-keys
https://admin.mistral.ai/organization/api-keys

### Environment variables

Add these to `src/.env` (only the variables for your chosen provider are required):

| Variable | Description |
|---|---|
| `API_KEY_GEMINI` | Google Gemini API key |
| `LLM_MODEL_GEMINI` | Gemini model name (e.g. `gemini-flash-latest`) |
| `API_KEY_CLAUDE` | Anthropic API key |
| `LLM_MODEL_CLAUDE` | Claude model name (e.g. `claude-opus-4-8`) |
| `API_KEY_GPT` | OpenAI API key |
| `LLM_MODEL_GPT` | OpenAI model name (e.g `gpt-5.5`) |
| `API_KEY_MISTRAL` | Mistral API key |
| `LLM_MODEL_MISTRAL` | Mistral model name (e.g. `mistral-small-latest`) |

Without a `.env` file, only the **dummy** provider works.

## Usage

Run the chat CLI from the `src/` directory:

```bash
cd src
python main.py --provider dummy
```

### Provider options

| Flag | Provider |
|---|---|
| `--provider dummy` | Echoes your input (no API key needed) |
| `--provider anthropic` | Claude via Anthropic SDK |
| `--provider google` | Gemini via Google GenAI SDK |
| `--provider openai` | GPT via OpenAI SDK |
| `--provider mistral` | Mistral via Mistral SDK |

Example with a live provider:

```bash
python main.py --provider google
```

During the session:

- Type your message at the `[user]:` prompt
- Read the agent reply at `[agent]:`
- End the session with `exit`, `quit`, or `/q` — the conversation is saved under `src/conversation/`


## Architecture

```mermaid
flowchart LR
    User["User (CLI)"] --> Main["main.py"]
    Main --> Agent["Agent"]
    Agent --> LLM["LLMProvider"]
    LLM --> Anthropic
    LLM --> Google
    LLM --> OpenAI
    LLM --> Mistral
    LLM --> Dummy
```

- **`LLMProvider`** — abstract base class; each provider implements `__call__` with provider-specific message formatting
- **`Agent`** — holds a provider instance and delegates inference
- **`User`** — lightweight identity model (UUID per session)
- **`main.py`** — builds the conversation history, formats messages per provider, and persists on exit

## Development
- Pre-commit hooks are configured via `.pre-commit-config.yaml`

## License

See [LICENSE](LICENSE).
