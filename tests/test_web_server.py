from types import SimpleNamespace

from app.web_server import (
    patch_textual_js,
    public_url_for_request,
    websocket_url_for_request,
)


def test_public_url_uses_the_request_host_instead_of_the_bind_address():
    request = SimpleNamespace(scheme="http", host="games.example:8001", headers={})

    assert public_url_for_request(request) == "http://games.example:8001"


def test_public_url_respects_forwarded_https_scheme():
    request = SimpleNamespace(
        scheme="http",
        host="llm-text-games:8001",
        headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "games.example"},
    )

    assert public_url_for_request(request) == "https://games.example"


def test_websocket_url_uses_secure_websocket_for_forwarded_https():
    request = SimpleNamespace(
        scheme="http",
        host="llm-text-games:8001",
        headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "games.example"},
    )

    assert websocket_url_for_request(request, "/ws") == "wss://games.example/ws"


def test_textual_script_auto_hides_splash_after_short_delay():
    source = "s||t.connect()}"

    patched = patch_textual_js(source, mobile=False)

    assert "setTimeout" in patched
    assert "1500" in patched


def test_textual_script_disables_webgl_addons_on_mobile():
    source = (
        "this.webglAddon=new p.WebglAddon,this.terminal.loadAddon(this.webglAddon),"
        "this.canvasAddon=new m.CanvasAddon,this.terminal.loadAddon(this.canvasAddon),"
        "s||t.connect()}"
    )

    patched = patch_textual_js(source, mobile=True)

    assert "WebglAddon" not in patched
    assert "CanvasAddon" not in patched
