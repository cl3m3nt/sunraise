# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project overview

**sunraise** is a Python CLI that runs an interactive terminal chat between a `User` and an `Agent`. The agent can use several LLM providers (`gemini`, `claude`, `gpt`, `mistral`) or a local **`dummy`** provider that echoes input (no API keys required).

Entry point: `src/main.py`. Core logic: `src/agent.py`, `src/user.py`.

## Cursor Cloud specific instructions

### Services

| Service | Required | Notes |
|---------|----------|--------|
| sunraise CLI | Yes | Only runnable application |
| LLM vendor APIs | No | Only when testing `--provider` other than `dummy` |

There is no web server, database, or Docker Compose stack.

### One-time VM prerequisites

If `python3 -m venv .venv` fails with `ensurepip is not available`, install the venv package once:

```bash
sudo apt-get update && sudo apt-get install -y python3.12-venv
```

### Python environment

Use the project virtualenv at `/workspace/.venv`:

```bash
source /workspace/.venv/bin/activate
cd /workspace/src
python3 main.py --provider dummy
```

The VM **update script** refreshes `.venv` on each Cloud Agent session (see SetupVmEnvironment). Activate the venv before running the app or pre-commit.

### Dependency gap

`requirements.txt` lists only `google-genai` and `python-dotenv`, but `src/agent.py` imports `anthropic`, `openai`, and `mistralai` at module load time. The update script installs those SDKs plus `pre-commit`.

**mistralai:** Use `mistralai==1.5.0`. Newer 2.x releases moved `Mistral` off the top-level package (`from mistralai import Mistral` fails); the app imports it that way.

### Lint / CI checks

No unit test suite in the repo. CI runs pre-commit only (`.github/workflows/pre-commit.yml`):

```bash
source /workspace/.venv/bin/activate
cd /workspace
pre-commit run --all-files
```

Hooks: gitleaks, detect-private-key, check-added-large-files, Black, Ruff.

### Running the app (dummy provider)

Offline smoke test (no `.env` or API keys):

```bash
source /workspace/.venv/bin/activate
cd /workspace/src
printf 'your message\nexit\n' | python3 main.py --provider dummy
```

Exit the REPL with `exit`, `quit`, or `/q`.

### Live LLM providers

Create `/workspace/.env` (gitignored) with keys and models, for example:

- `API_KEY_GEMINI`, `LLM_MODEL_GEMINI`
- `API_KEY_CLAUDE`, `LLM_MODEL_CLAUDE`
- `API_KEY_GPT`, `LLM_MODEL_GPT`
- `API_KEY_MISTRAL`, `LLM_MODEL_MISTRAL`

Then run `python3 main.py --provider <name>` from `src/`.
