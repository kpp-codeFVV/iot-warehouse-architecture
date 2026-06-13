from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import Store, process_alert_events


app = FastAPI(title="alert-service", version="0.1.0")
store = Store()
_processor_task: asyncio.Task | None = None


async def event_processor_loop() -> None:
    while True:
        process_alert_events(store)
        await asyncio.sleep(0.5)


@app.on_event("startup")
async def start_event_processor() -> None:
    global _processor_task
    _processor_task = asyncio.create_task(event_processor_loop())


@app.on_event("shutdown")
async def stop_event_processor() -> None:
    if _processor_task:
        _processor_task.cancel()


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "alert-service", "status": "ok"}


@app.post("/process-events")
def process_events() -> dict[str, Any]:
    return process_alert_events(store)


@app.get("/alerts")
def alerts() -> dict[str, Any]:
    rows = store.alerts()
    return {"count": len(rows), "items": rows}
