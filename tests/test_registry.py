import pytest

from app.games.registry import GameDefinition, select_game


def test_select_game_by_one_based_index():
    definitions = (GameDefinition("one", object), GameDefinition("two", object))
    assert select_game(2, definitions).name == "two"


def test_select_game_rejects_invalid_index():
    with pytest.raises(ValueError):
        select_game(0, (GameDefinition("one", object),))
