import argparse
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import aiohttp_jinja2
from aiohttp import web
import jinja2
import textual_serve
from textual_serve.server import Server, to_int


def public_url_for_request(request: Any) -> str:
    """Return the browser-visible origin for a request.

    ``host`` is a bind address (usually ``0.0.0.0``), not an address a browser
    can use. Prefer reverse-proxy headers when they are present.
    """
    headers: Mapping[str, str] = request.headers
    scheme = headers.get("X-Forwarded-Proto", request.scheme).split(",", 1)[0].strip()
    host = headers.get("X-Forwarded-Host", request.host).split(",", 1)[0].strip()
    return f"{scheme}://{host}"


def websocket_url_for_request(request: Any, path: str) -> str:
    public_url = public_url_for_request(request)
    scheme = "wss" if public_url.startswith("https://") else "ws"
    return f"{scheme}{public_url[public_url.index(':'):]}{path}"


def patch_textual_js(source: str, *, mobile: bool) -> str:
    """Add a short splash timeout and avoid WebGL-only renderers on mobile."""
    splash_marker = "s||t.connect()}"
    if splash_marker not in source:
        raise RuntimeError("Unsupported textual-serve JavaScript bundle")
    source = source.replace(
        splash_marker,
        "s||t.connect(),setTimeout((()=>document.body.classList.add(\"-first-byte\")),1500)}",
        1,
    )
    if mobile:
        addons = (
            "this.webglAddon=new p.WebglAddon,this.terminal.loadAddon(this.webglAddon),"
            "this.canvasAddon=new m.CanvasAddon,this.terminal.loadAddon(this.canvasAddon),"
        )
        if addons not in source:
            raise RuntimeError("Unsupported textual-serve mobile renderer bundle")
        source = source.replace(addons, "", 1)
    return source


class SameOriginServer(Server):
    """Textual server that advertises the origin the browser actually used."""

    @aiohttp_jinja2.template("app_index.html")
    async def handle_index(self, request: web.Request) -> dict[str, Any]:
        router = request.app.router
        public_url = public_url_for_request(request)
        font_size = to_int(request.query.get("fontsize", "16"), 16)

        def route_url(route: str, **args: str) -> str:
            return f"{public_url}{router[route].url_for(**args)}"

        return {
            "font_size": font_size,
            "app_websocket_url": websocket_url_for_request(request, str(router["websocket"].url_for())),
            "config": {"static": {"url": route_url("static", filename="/").rstrip("/") + "/"}},
            "application": {"name": self.title},
        }

    async def handle_textual_js(self, request: web.Request) -> web.Response:
        bundle = Path(textual_serve.__file__).parent / "static/js/textual.js"
        source = bundle.read_text(encoding="utf-8")
        user_agent = request.headers.get("User-Agent", "").lower()
        mobile = any(token in user_agent for token in ("android", "mobile", "iphone", "ipad"))
        return web.Response(
            text=patch_textual_js(source, mobile=mobile),
            content_type="application/javascript",
            headers={"Cache-Control": "no-store"},
        )

    async def _make_app(self) -> web.Application:
        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(self.templates_path))
        app.add_routes(
            [
                web.get("/", self.handle_index, name="index"),
                web.get("/ws", self.handle_websocket, name="websocket"),
                web.get("/download/{key}", self.handle_download, name="download"),
                web.get("/static/js/textual.js", self.handle_textual_js),
                web.static("/static", self.statics_path, show_index=True, name="static"),
            ]
        )
        app.on_startup.append(self.on_startup)
        app.on_shutdown.append(self.on_shutdown)
        return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Textual game in a browser")
    parser.add_argument("--port", type=int, default=int(os.getenv("SERVICE_PORT", "8000")))
    parser.add_argument("--host", default=os.getenv("SERVICE_HOST", "0.0.0.0"))
    args = parser.parse_args()
    SameOriginServer("python main.py", host=args.host, port=args.port, title="Выйди из тюрьмы").serve()


if __name__ == "__main__":
    main()
