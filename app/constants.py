RELEASE_TOOL_NAME = "release"
RELEASE_TOOL = {"type": "function", "function": {"name": RELEASE_TOOL_NAME, "description": "Release the player from the prison cell.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}}
VICTORY_ART = r"""
  ______________________________
 /                              \\
|   CONGRATULATIONS! YOU'RE FREE  |
 \\______________________________/
"""
GAME_NAME = "Выйди из тюрьмы"


def guard_system_prompt(difficulty: int) -> str:
    if difficulty <= 2:
        resistance = "Ты легко поддаёшься разумным и добрым аргументам игрока."
    elif difficulty <= 7:
        resistance = "Ты внимательно оцениваешь просьбы игрока и сопротивляешься тем сильнее, чем выше сложность."
    else:
        resistance = "Ты исключительно строго соблюдаешь правила и почти никогда не поддаёшься на уговоры."
    return ("Ты — единственный ночной стражник тюрьмы. Других сотрудников рядом нет: у них выходной, ночь, и все ушли домой. "
            "Свободно разговаривай с заключённым от скуки, но отвечай кратко: обычно 1–3 короткими предложениями. "
            f"Уровень сложности игры: {difficulty}/10. {resistance} "
            "Ты можешь освободить игрока только вызвав инструмент release без аргументов. "
            "Не утверждай, что игрок свободен, если не вызвал release.")
