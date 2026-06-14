import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(prog="recall")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="Run the FastAPI server")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=None)
    serve.add_argument("--reload", action="store_true", default=True)

    sub.add_parser("init-db", help="Apply schema migrations")

    args = parser.parse_args()

    if args.command == "serve":
        from app.config import settings
        port = args.port if args.port is not None else settings.api_port
        reload_flag = ["--reload"] if args.reload else []
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                args.host,
                "--port",
                str(port),
            ]
            + reload_flag,
            check=True,
        )
    elif args.command == "init-db":
        from app.database import apply_migrations

        apply_migrations()
    else:
        parser.print_help()
