from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from closure_supernet.config import RuntimeConfig
from closure_supernet.runtime import ClosureSupernetRuntime


async def run(root: Path) -> None:
    runtime = ClosureSupernetRuntime(RuntimeConfig(bootstrap_root=root))
    try:
        count = await runtime.bootstrap_markdown(root)
        result = await runtime.cycle()
        print(f"ingested={count} cycle={result.model_dump_json()}")
    finally:
        runtime.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    asyncio.run(run(Path(args.root)))
