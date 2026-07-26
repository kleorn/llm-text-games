# Prison Escape MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a tested, Docker-runnable console game in which a player persuades an LLM-controlled guard to call the `release` tool.

**Architecture:** Keep `main.py` as a thin entry point. Put configuration, LLM adaptation, game state, registry, and Rich CLI in focused `app/` modules with dependency injection so tests use fakes. The first registry has one game but supports numbered selection when expanded.

**Tech Stack:** Python 3.12.8, uv, OpenAI Python client, Pydantic Settings, Rich, pytest, Docker.

## Global Constraints

- Use Python 3.12.8 and uv.
- Support an OpenAI-compatible API via `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
- Load settings from `.env` and environment variables with Pydantic Settings.
- Console MVP must provide coloured output and Markdown rendering; full-screen TUI is out of scope.
- Keep constants in `app/constants.py` and make minimal, maintainable changes.
- Include Dockerfile, required Makefile commands, `.env.example`, and README.

### Task 1: Project packaging and configuration

**Files:** Create `pyproject.toml`, `uv.lock` (via uv), `.env.example`, `app/__init__.py`, `app/config.py`, `tests/test_config.py`.

**Interfaces:** `Settings` exposes `openai_api_key`, `openai_base_url`, `openai_model`, and `service_port`; `load_settings()` returns `Settings`.

- [ ] Write tests for valid environment loading, `.env` compatibility, and missing required values.
- [ ] Run `uv run pytest tests/test_config.py -q` and confirm the new tests fail before implementation.
- [ ] Implement Pydantic settings with required API values and `service_port: int = 8000`; make validation errors concise at the CLI boundary.
- [ ] Add runtime dependencies `openai`, `pydantic-settings`, `rich` and dev dependency `pytest` for Python 3.12.
- [ ] Run the focused tests and `uv lock`; expect all focused tests to pass.

### Task 2: Constants, LLM adapter, and game contracts

**Files:** Create `app/constants.py`, `app/llm.py`, `app/games/__init__.py`, `app/games/base.py`, `tests/test_llm.py`.

**Interfaces:** `ToolResult(text: str, released: bool)`; `LLMClient.respond(messages: list[dict[str, str]], tools: list[dict]) -> ToolResult`; `RELEASE_TOOL` is the exact no-argument tool schema.

- [ ] Write fake-client tests for normal text, `release`, and an unknown tool call.
- [ ] Run `uv run pytest tests/test_llm.py -q` and confirm failure.
- [ ] Implement the OpenAI adapter using `OpenAI(api_key=..., base_url=...)`, extracting the first choice message, text, and tool calls; reject malformed/unknown tool calls with a domain error.
- [ ] Add user-facing strings, difficulty labels, system-prompt fragments, and victory ASCII art to constants.
- [ ] Run focused tests and confirm pass without network access.

### Task 3: Prison Escape game and registry

**Files:** Create `app/games/prison_escape.py`, `app/games/registry.py`, `tests/test_prison_escape.py`, `tests/test_registry.py`.

**Interfaces:** `PrisonEscapeGame(difficulty: int, llm: LLMClient)`; `handle_player_message(text: str) -> ToolResult`; `games: tuple[GameDefinition, ...]`; `select_game(index: int) -> GameDefinition`.

- [ ] Write tests that difficulty 1 and 10 produce distinct prompts, history appends in order, release ends the game, and invalid difficulty/index values raise `ValueError`.
- [ ] Run focused tests and confirm failure.
- [ ] Implement the guard system prompt, history initialised with the system message, difficulty validation 1–10, and one `release` tool per request.
- [ ] Implement a registry with the initial game and deterministic index selection.
- [ ] Run focused tests and confirm pass.

### Task 4: Rich CLI and entry point

**Files:** Create `app/cli.py`, modify `main.py`, `tests/test_cli.py`.

**Interfaces:** `run(settings: Settings, llm_factory: Callable) -> int`; CLI returns `0` on victory/EOF and `1` on configuration/API errors.

- [ ] Write tests with monkeypatched input and a fake LLM for difficulty validation, Markdown rendering invocation, victory output, and clean EOF.
- [ ] Run focused tests and confirm failure.
- [ ] Implement Rich `Console` output, numbered game selection when registry size > 1, difficulty prompts, chat loop, and concise error handling without default tracebacks.
- [ ] Make `main.py` load settings, invoke `run`, and exit with its return code.
- [ ] Run `uv run pytest tests/test_cli.py -q` and then the full suite.

### Task 5: Container, Makefile, and documentation

**Files:** Create `Dockerfile`, `Makefile`, `README.md`; modify `.env.example` if needed.

- [ ] Add a Dockerfile based on Python 3.12 that installs with uv and starts `python main.py`.
- [ ] Add `docker-build`, `docker-run`, `docker-restart`, `docker-stop`, `docker-rm`, and `docker-update`; pass `SERVICE_PORT` through Docker commands.
- [ ] Document product purpose, environment parameters, local/Docker startup, console flow, OpenAI-compatible API expectations, and that MVP has no REST endpoints.
- [ ] Run `uv run pytest -q`, `docker build`, and a non-interactive `python main.py` configuration-error smoke test.

### Task 6: Final verification

- [ ] Run formatting/lint checks available in the project and the complete test suite.
- [ ] Inspect `git diff --check` and `git status` for accidental files.
- [ ] Perform a manual smoke test against a configured compatible endpoint if credentials are available; otherwise record that only offline tests were run.
