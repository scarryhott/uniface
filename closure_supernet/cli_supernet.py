from __future__ import annotations

import asyncio
import os

import uvicorn

from .cli import _async_main, _parser


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.command == "serve":
        if args.no_autonomy:
            os.environ["CLOSURE_AUTONOMY_ENABLED"] = "false"
        if args.db:
            os.environ["CLOSURE_DB_PATH"] = args.db
        port = int(os.getenv("PORT", str(args.port)))
        uvicorn.run(
            "closure_supernet.api_selection:app",
            host=args.host,
            port=port,
            reload=False,
            proxy_headers=True,
            forwarded_allow_ips="*",
        )
        return
    raise SystemExit(asyncio.run(_async_main(args)))
