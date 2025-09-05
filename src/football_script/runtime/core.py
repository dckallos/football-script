from __future__ import annotations
import asyncio
from typing import Any, get_origin, get_args

# Public runtime surface
def print(*args, **kwargs):
    __builtins__["print"](*args, **kwargs)

async def sleep_ms(ms: int):
    await asyncio.sleep(ms / 1000.0)

async def gather_all(*aws):
    """Await all coroutines, raising ExceptionGroup if any failed; otherwise return ordered results."""
    results = await asyncio.gather(*aws, return_exceptions=True)
    errors = [e for e in results if isinstance(e, BaseException)]
    if errors:
        raise ExceptionGroup("parallel errors", errors)
    return results

# Gradual typing helpers (Phase 2 will use)
def runtime_cast(value: Any, annotation: Any) -> Any:
    # minimal, permissive v1
    origin = get_origin(annotation)
    if origin is None:
        return value  # v1: no-op; Phase 2 replaces with real checks
    return value
