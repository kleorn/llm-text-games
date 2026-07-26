# Prison Escape MVP Design

## Purpose

Build the first playable LLM text game, **"Выйди из тюрьмы"**. A player talks to a prison guard and wins only when the guard calls the `release` tool. The implementation must make adding further games straightforward.

## Scope

The MVP is a terminal application launched with `uv run python main.py`. It provides a numbered difficulty selection, a turn-based chat, Rich-based coloured Markdown output, and a victory screen with ASCII art.

The MVP does not include a full-screen, keyboard-driven TUI or REST endpoints. A richer Rich TUI and an HTTP interface can be added later without changing the game or LLM layers.

## Configuration

Settings load from a `.env` file and environment variables using Pydantic settings. Environment variables are:

- `OPENAI_API_KEY` — required API key.
- `OPENAI_BASE_URL` — required base URL for an OpenAI-compatible API.
- `OPENAI_MODEL` — required chat model name.
- `SERVICE_PORT` — optional port value, default `8000`; retained for Docker and a future HTTP layer, and not used by the console MVP.

The project targets Python 3.12.8 and uses uv for dependency management.

## Architecture

`main.py` is a small entry point that runs the CLI. Modules have one responsibility:

- `app/config.py`: Pydantic settings and configuration errors.
- `app/constants.py`: environment-variable names, player-facing text, tool name, game metadata, and victory ASCII art.
- `app/llm.py`: OpenAI-compatible client adapter that submits chat history and the `release` tool definition, returning a normalised assistant result.
- `app/games/base.py`: game protocol and result types.
- `app/games/prison_escape.py`: difficulty-dependent guard prompt, conversation state, and release-tool win handling.
- `app/games/registry.py`: registered games. The CLI bypasses the selector when only one game is registered; it shows a numbered game list automatically when a second game is added.
- `app/cli.py`: input prompts, Rich rendering, and the main chat loop. It contains no prompt or LLM-specific decision logic.

## Game flow

1. Load configuration. If a required setting is absent, print a concise instruction and exit with a non-zero status.
2. Resolve the game from the registry. With the initial single game, select it directly; with multiple games, ask for a numbered selection until valid input is received or stdin ends.
3. Ask for difficulty from 1 to 10 until valid input is received or stdin ends.
4. Create the prison-escape game. Its system prompt tells the model it is the lone night guard, free to converse, and that it may release the player only by calling `release` with no arguments.
5. Read player messages in a loop, append each to history, and call the LLM adapter with the current history and tool definition.
6. Render a non-empty guard message as Rich Markdown. If the adapter reports a `release` tool call, show the coloured win message and ASCII art, then finish successfully.
7. On EOF, finish cleanly. On an API, timeout, or malformed-response error, print a concise retry-or-exit message and exit non-zero without exposing a traceback by default.

## Difficulty semantics

Difficulty changes only the guard's system-prompt instructions. Level 1 makes the guard receptive to ordinary, harmless persuasion. Level 10 makes the guard exceptionally rule-bound and difficult to persuade. Intermediate levels use the level as an explicit resistance scale. The guard must never claim the player is free unless it calls `release`.

## LLM contract

The LLM adapter uses the official OpenAI Python client configured with `api_key` and `base_url`, so it supports OpenAI and compatible endpoints. Every turn sends the accumulated messages and exactly one function tool:

```json
{
  "type": "function",
  "function": {
    "name": "release",
    "description": "Release the player from the prison cell.",
    "parameters": {"type": "object", "properties": {}, "additionalProperties": false}
  }
}
```

The adapter turns the provider-specific response into an assistant text value plus a Boolean `released`. Any tool call named `release` sets `released` to true; all other tool calls are treated as a malformed response.

## Packaging and operations

`pyproject.toml` declares production dependencies: `openai`, `pydantic-settings`, and `rich`, with pytest as a development dependency. The lockfile is generated and used by uv.

The Dockerfile installs dependencies through uv and starts the console application. The Makefile supplies `docker-build`, `docker-run`, `docker-restart`, `docker-stop`, `docker-rm`, and `docker-update`; `docker-run` passes `SERVICE_PORT` through to the container. README documents installation, environment settings, startup, Docker commands, the console interaction, and the intentional absence of endpoints in the MVP.

## Verification

Automated tests must not call an external API. They cover settings validation, game-registry selection behaviour, guard prompt differences at low and high difficulties, message-history updates, release recognition, malformed tool-call handling, and CLI rendering/termination using a fake LLM adapter. A separate manual smoke test runs the console application against a configured compatible endpoint.
