import argparse
import os

from textual_serve.server import Server


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Textual game in a browser")
    parser.add_argument("--port", type=int, default=int(os.getenv("SERVICE_PORT", "8000")))
    parser.add_argument("--host", default=os.getenv("SERVICE_HOST", "0.0.0.0"))
    args = parser.parse_args()
    Server("python main.py", host=args.host, port=args.port, title="Выйди из тюрьмы").serve()


if __name__ == "__main__":
    main()
