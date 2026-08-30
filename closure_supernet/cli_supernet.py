from __future__ import annotations

"""Minimal published CLI; it imports no historical semantic runtime."""

import argparse
import os

import uvicorn


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="closure-supernet")
    parser.add_argument("--db", default=None)
    commands = parser.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--no-autonomy", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.db:
        os.environ["CLOSURE_DB_PATH"] = args.db
    os.environ["CLOSURE_AUTONOMY_ENABLED"] = "false"
    port = int(os.getenv("PORT", str(args.port)))
    uvicorn.run(
        "closure_supernet.api_agent:app",
        host=args.host,
        port=port,
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


__all__ = ["main"]
