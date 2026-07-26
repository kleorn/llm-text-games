from dataclasses import dataclass
from typing import Callable

from app.constants import GAME_NAME


@dataclass(frozen=True)
class GameDefinition:
    name: str
    factory: Callable


def select_game(index: int, definitions: tuple[GameDefinition, ...]) -> GameDefinition:
    if index < 1 or index > len(definitions):
        raise ValueError("game index out of range")
    return definitions[index - 1]


def default_games() -> tuple[GameDefinition, ...]:
    return (GameDefinition(GAME_NAME, __import__("app.games.prison_escape", fromlist=["PrisonEscapeGame"]).PrisonEscapeGame),)
