from collections.abc import Callable
from typing import Any

from rich.markdown import Markdown
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, RichLog, Select, Static

from app.config import Settings, load_settings
from app.constants import GAME_NAME, INTRODUCTION, VICTORY_ART
from app.games.prison_escape import PrisonEscapeGame
from app.llm import LLMClient, LLMResponseError, ToolResult
from app.logging_config import configure_logging


class PrisonEscapeApp(App[None]):
    TITLE = GAME_NAME
    CSS = """
    Screen { align: center middle; }
    #shell { width: 90%; height: 90%; }
    #intro { padding: 1 2; border: round $accent; margin-bottom: 1; }
    #setup { height: auto; }
    #difficulty { width: 30; }
    #start { margin-left: 1; }
    #chat { height: 1fr; border: round $accent; padding: 1; }
    #input-row { height: auto; margin-top: 1; }
    #message { width: 1fr; }
    .hidden { display: none; }
    """

    def __init__(self, settings: Settings | None = None, llm_factory: Callable[..., Any] = LLMClient):
        super().__init__()
        self.settings = settings
        self.llm_factory = llm_factory
        self.game: PrisonEscapeGame | None = None
        self.logger = configure_logging()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="shell"):
            yield Static(INTRODUCTION, id="intro")
            with Horizontal(id="setup"):
                yield Select([(str(level), level) for level in range(1, 11)], prompt="Сложность 1–10", id="difficulty")
                yield Button("Начать игру", id="start", variant="primary")
            yield RichLog(id="chat", markup=False)
            with Horizontal(id="input-row", classes="hidden"):
                yield Input(placeholder="Сообщение стражнику…", id="message")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#chat", RichLog).write("Выберите сложность и нажмите «Начать игру».")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "start":
            return
        difficulty = self.query_one("#difficulty", Select).value
        if difficulty is Select.BLANK or not isinstance(difficulty, int):
            self.notify("Выберите сложность от 1 до 10", severity="warning")
            return
        try:
            settings = self.settings or load_settings()
            llm = self.llm_factory(settings.openai_api_key, settings.openai_base_url, settings.openai_model)
            self.game = PrisonEscapeGame(difficulty, llm)
        except Exception as exc:
            self.logger.exception("Failed to start game")
            self.notify(f"Ошибка запуска: {exc}", severity="error")
            return
        self.query_one("#setup").add_class("hidden")
        self.query_one("#input-row").remove_class("hidden")
        self.query_one("#message", Input).focus()
        self.query_one("#chat", RichLog).write("Игра началась. Поговорите со стражником.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "message" or not event.value.strip() or self.game is None:
            return
        message = event.value.strip()
        event.input.value = ""
        self.query_one("#chat", RichLog).write(Markdown(f"**Вы:** {message}"))
        self.respond_to_player(message)

    @work(thread=True, exclusive=True)
    def respond_to_player(self, message: str) -> None:
        if self.game is None:
            return
        try:
            result = self.game.handle_player_message(message)
            self.call_from_thread(self._show_result, result)
        except (LLMResponseError, RuntimeError, OSError) as exc:
            self.logger.exception("Textual game turn failed")
            self.call_from_thread(self.notify, f"Ошибка игры: {exc}", severity="error")

    def _show_result(self, result: ToolResult) -> None:
        chat = self.query_one("#chat", RichLog)
        if result.text:
            chat.write(Markdown(f"**Стражник:** {result.text}"))
        if result.released:
            chat.write(Markdown("**Поздравляем! Вы на свободе!**"))
            chat.write(VICTORY_ART)
            self.query_one("#message", Input).disabled = True
