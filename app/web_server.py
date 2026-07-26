import argparse
import os
from collections.abc import Mapping
from typing import Any

import aiohttp_jinja2
from aiohttp import web
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Textual game in a browser")
    parser.add_argument("--port", type=int, default=int(os.getenv("SERVICE_PORT", "8000")))
    parser.add_argument("--host", default=os.getenv("SERVICE_HOST", "0.0.0.0"))
    args = parser.parse_args()
    SameOriginServer("python main.py", host=args.host, port=args.port, title="Выйди из тюрьмы").serve()


if __name__ == "__main__":
    main()
