from __future__ import annotations

import asyncio

import uvicorn

from .cli import _async_main, _parser


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
            "closure_supernet.api_resource:app",
            host=args.host,
            port=args.port,
            reload=False,
        )
        return
    raise SystemExit(asyncio.run(_async_main(args)))
