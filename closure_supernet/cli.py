from __future__ import annotations

import argparse
import asyncio
import json
import signal
from pathlib import Path

import uvicorn

from .backup import create_backup, list_backups, prune_backups
from .config import RuntimeConfig
from .integration_models import IntegrationCreate, IntegrationKind
from .models import OccurrenceCreate
from .runtime import ClosureSupernetRuntime


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="closure-supernet", description="Closure Supernet autonomous runtime"
    )
    parser.add_argument("--db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Run API, public network and autonomous loop")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--no-autonomy", action="store_true")

    sub.add_parser("worker", help="Run only the autonomous reintegration loop")

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

    backup = sub.add_parser("backup", help="Create a consistent SQLite snapshot")
    backup.add_argument("--label", default="cli")
    sub.add_parser("backup-list", help="List available production snapshots")

    bootstrap = sub.add_parser("bootstrap", help="Ingest markdown files from a source tree")
    bootstrap.add_argument("root", nargs="?", default=".")

    integration_add = sub.add_parser("integration-add", help="Register a digital integration")
    integration_add.add_argument("--name", required=True)
    integration_add.add_argument(
        "--kind", required=True, choices=[kind.value for kind in IntegrationKind]
    )
    integration_add.add_argument(
        "--config", default="{}", help="Connector configuration as a JSON object"
    )
    integration_add.add_argument(
        "--secret-env",
        help="Environment-variable name holding the connector secret; the secret is not stored",
    )
    integration_add.add_argument("--disabled", action="store_true")

    sub.add_parser("integration-list", help="List registered integrations")
    integration_poll = sub.add_parser(
        "integration-poll", help="Poll one pull integration or all enabled pull integrations"
    )
    integration_poll.add_argument("integration_id", nargs="?")
    integration_enable = sub.add_parser("integration-enable", help="Enable an integration")
    integration_enable.add_argument("integration_id")
    integration_disable = sub.add_parser("integration-disable", help="Disable an integration")
    integration_disable.add_argument("integration_id")
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
        if args.command == "worker":
            stop = asyncio.Event()
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    loop.add_signal_handler(sig, stop.set)
                except (NotImplementedError, RuntimeError):
                    pass
            await runtime.start()
            await stop.wait()
            await runtime.stop()
        elif args.command == "ingest":
            if args.text:
                text = args.source
                location = None
            else:
                path = Path(args.source)
                text = path.read_text(encoding="utf-8")
                location = str(path.resolve())
            occurrence = await runtime.ingest(
                OccurrenceCreate(
                    exact_text=text,
                    source_id=args.source_id,
                    source_location=location,
                )
            )
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
        elif args.command == "backup":
            manifest = create_backup(config.database_path, config.backup_dir, label=args.label)
            manifest["pruned"] = prune_backups(config.backup_dir, keep=config.backup_keep)
            print(json.dumps(manifest, indent=2))
        elif args.command == "backup-list":
            print(json.dumps(list_backups(config.backup_dir, limit=config.backup_keep), indent=2))
        elif args.command == "bootstrap":
            print(
                json.dumps(
                    {"ingested": await runtime.bootstrap_markdown(Path(args.root))},
                    indent=2,
                )
            )
        elif args.command == "integration-add":
            raw_config = json.loads(args.config)
            if not isinstance(raw_config, dict):
                raise ValueError("--config must decode to a JSON object")
            record = runtime.integrations.create(
                IntegrationCreate(
                    name=args.name,
                    kind=IntegrationKind(args.kind),
                    config=raw_config,
                    secret_env=args.secret_env,
                    enabled=not args.disabled,
                )
            )
            print(record.model_dump_json(indent=2))
        elif args.command == "integration-list":
            print(
                json.dumps(
                    runtime.integration_store.list_integrations(),
                    indent=2,
                    ensure_ascii=False,
                )
            )
        elif args.command == "integration-poll":
            results = await runtime.integrations.poll_enabled(args.integration_id)
            print(
                json.dumps(
                    [result.model_dump(mode="json") for result in results],
                    indent=2,
                    ensure_ascii=False,
                )
            )
        elif args.command == "integration-enable":
            print(
                json.dumps(
                    runtime.integration_store.set_enabled(args.integration_id, True),
                    indent=2,
                    ensure_ascii=False,
                )
            )
        elif args.command == "integration-disable":
            print(
                json.dumps(
                    runtime.integration_store.set_enabled(args.integration_id, False),
                    indent=2,
                    ensure_ascii=False,
                )
            )
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
        uvicorn.run(
            "closure_supernet.api:app",
            host=args.host,
            port=args.port,
            reload=False,
        )
        return
    raise SystemExit(asyncio.run(_async_main(args)))
