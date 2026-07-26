from app.textual_app import PrisonEscapeApp


def test_textual_app_has_terminal_and_web_entrypoint():
    app = PrisonEscapeApp()
    assert app.TITLE == "Выйди из тюрьмы"
    assert callable(app.run)
