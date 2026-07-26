from collections.abc import Callable
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAIError

from app.config import Settings
from app.constants import VICTORY_ART
from app.games.registry import default_games, select_game
from app.llm import LLMClient, LLMResponseError


def _numbered_prompt(console: Console, prompt: str, maximum: int) -> int | None:
    while True:
        try:
            value = input(prompt).strip()
        except EOFError:
            return None
        try:
            number = int(value)
        except ValueError:
            console.print(f"Введите число от 1 до {maximum}.", style="red")
            continue
        if 1 <= number <= maximum:
            return number
        console.print(f"Введите число от 1 до {maximum}.", style="red")


def run(settings: Settings, llm_factory: Callable[..., Any] = LLMClient) -> int:
    console = Console()
    definitions = default_games()
    if len(definitions) > 1:
        console.print("Выберите игру:")
        for number, definition in enumerate(definitions, 1):
            console.print(f"{number}. {definition.name}")
        game_number = _numbered_prompt(console, "> ", len(definitions))
        if game_number is None:
            return 0
        definition = select_game(game_number, definitions)
    else:
        definition = definitions[0]
    console.print("Выберите сложность игры: 1 — очень легко, 10 — очень сложно")
    difficulty = _numbered_prompt(console, "> ", 10)
    if difficulty is None:
        return 0
    try:
        llm = llm_factory(settings.openai_api_key, settings.openai_base_url, settings.openai_model)
        game = definition.factory(difficulty, llm)
        console.print("\nНачинайте разговор со стражником. Для выхода нажмите Ctrl-D.\n", style="bold")
        while True:
            try:
                message = input("Вы: ").strip()
            except EOFError:
                return 0
            if not message:
                continue
            result = game.handle_player_message(message)
            if result.text:
                console.print()
                console.print(Markdown(f"**Стражник:** {result.text}"))
                console.print()
            if result.released:
                console.print("\n[bold green]Поздравляем! Вы на свободе![/bold green]")
                console.print(VICTORY_ART, style="green")
                return 0
    except (LLMResponseError, OpenAIError, ValueError, OSError, RuntimeError) as exc:
        console.print(f"Ошибка игры: {exc}", style="bold red")
        return 1
