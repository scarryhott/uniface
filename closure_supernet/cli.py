from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import uvicorn

from .config import RuntimeConfig
from .models import OccurrenceCreate
from .runtime import ClosureSupernetRuntime


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="closure-supernet", description="Closure Supernet autonomous runtime")
    parser.add_argument("--db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Run API, dashboard and autonomous loop")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--no-autonomy", action="store_true")

    ingest = sub.add_parser("ingest", help="Ingest an exact source file or literal text")
    ingest.add_argument("source")
    ingest.add_argument("--text", action="store_true", help="Treat source argument as literal text")
    ingest.add_argument("--source-id", default="cli")

    sub.add_parser("cycle", help="Run one autonomous cycle")
    run = sub.add_parser("run", help="Run a fixed number of cycles")
    run.add_argument("--cycles", type=int, default=10)
    run.add_argument("--interval", type=float, default=1.0)
    sub.add_parser("status", help="Print runtime status")
    sub.add_parser("projection", help="Print current Black Mirror projection")
    bootstrap = sub.add_parser("bootstrap", help="Ingest markdown files from a source tree")
    bootstrap.add_argument("root", nargs="?", default=".")
    return parser


def _config(args: argparse.Namespace) -> RuntimeConfig:
    config = RuntimeConfig()
    if args.db:
        config.database_path = Path(args.db)
    return config


async def _async_main(args: argparse.Namespace) -> int:
    config = _config(args)
    runtime = ClosureSupernetRuntime(config)
    try:
        if args.command == "ingest":
            if args.text:
                text = args.source
                location = None
            else:
                path = Path(args.source)
                text = path.read_text(encoding="utf-8")
                location = str(path.resolve())
            occurrence = await runtime.ingest(OccurrenceCreate(exact_text=text, source_id=args.source_id, source_location=location))
            print(json.dumps(occurrence, indent=2, ensure_ascii=False))
        elif args.command == "cycle":
            print((await runtime.cycle()).model_dump_json(indent=2))
        elif args.command == "run":
            for _ in range(args.cycles):
                result = await runtime.cycle()
                print(result.model_dump_json())
                await asyncio.sleep(args.interval)
        elif args.command == "status":
            print(runtime.status().model_dump_json(indent=2))
        elif args.command == "projection":
            print(json.dumps(runtime.black_mirror(), indent=2, ensure_ascii=False))
        elif args.command == "bootstrap":
            print(json.dumps({"ingested": await runtime.bootstrap_markdown(Path(args.root))}, indent=2))
        return 0
    finally:
        runtime.close()


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.command == "serve":
        if args.no_autonomy:
            import os
            os.environ["CLOSURE_AUTONOMY_ENABLED"] = "false"
        if args.db:
            import os
            os.environ["CLOSURE_DB_PATH"] = args.db
        uvicorn.run("closure_supernet.api:app", host=args.host, port=args.port, reload=False)
        return
    raise SystemExit(asyncio.run(_async_main(args)))
