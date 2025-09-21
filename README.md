# Guardrail Service

Guardrail Service is a LangGraph-based pipeline that screens user prompts with simple business rules before handing them to a larger language model. It ships with a CLI for quick experiments and a LangGraph graph definition that can be deployed with the LangGraph API or CLI.

## Features
- Two-stage flow: a lightweight guard model classifies prompts before the assistant model runs
- Configurable policy (character limits and banned terms) through `Settings` and environment variables
- Structured outputs from both guard and assistant nodes via Pydantic models
- Ready-to-run CLI entry point and LangGraph configuration for local or hosted execution
- Test suite that exercises the guardrail branch logic

## Requirements
- Python 3.11 or 3.12
- An OpenAI API key with access to the configured models (`gpt-4o-mini` and `gpt-4o` by default)
- (Optional) LangSmith API key if you plan to trace runs with LangGraph tooling

## Installation
Using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Environment variables
Create a `.env` file (or export variables another way) with at least:

```bash
OPENAI_API_KEY="sk-your-openai-key"
LANGSMITH_API_KEY="lsv2-your-langsmith-key"  # optional
```

The project loads `.env` automatically via `python-dotenv` in `config.py`.

## Usage
### CLI
Run the guardrail once for a prompt:

```bash
uv run guardrail --prompt "Summarize protocol ABC for cardiology."
```

You can also invoke the module directly:

```bash
uv run python -m guardrail_service.cli --prompt "tell me a joke"
```

### LangGraph runtime
`langgraph.json` exposes the compiled graph as `guardrail_agent`. With the LangGraph CLI installed:

```bash
uv run langgraph dev guardrail_agent
```

This will start an interactive session where you can send prompts and inspect runs.

## How it works
- `guard_node` renders `prompts.GUARD_PROMPT_TEMPLATE` and classifies the latest user message with a small model via `GuardOutput`.
- `route_after_guard` chooses between `reminder_node` (sends a kind rejection) and `llm_node`.
- `llm_node` calls the main assistant model and returns a structured `LLMResponse`, ensuring JSON-only replies.

Business rules such as maximum prompt length and banned terms live in `config.Settings`. Adjust them there or extend the model to pull from your own policy source.

## Tests
Run the fast guardrail tests with:

```bash
uv run pytest
```

The tests assert that blocked prompts trigger the reminder branch and that allowed prompts reach the assistant node.

## Project structure
```
guardrail_service/
|-- src/guardrail_service/
|   |-- config.py          # Environment-backed settings and policy defaults
|   |-- models.py          # Pydantic models for guard + assistant outputs
|   |-- prompts.py         # Business-rule prompt template for the guard node
|   |-- graph.py           # LangGraph workflow definition
|   `-- cli.py             # Command-line entry point
|-- tests/test_guard.py    # Branch-behavior regression tests
|-- langgraph.json         # LangGraph CLI/API configuration
`-- README.md
```

## Next steps
- Swap in your own guard policies or additional checks (PII detection, rate limits, etc.)
- Add retrieval, tools, or memory to `llm_node` to grow the assistant capability
- Configure LangSmith or LangGraph Cloud to monitor production traffic
