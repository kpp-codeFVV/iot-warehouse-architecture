from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import Store, process_telemetry


app = FastAPI(title="inventory-service", version="0.1.0")
store = Store()


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "inventory-service", "status": "ok"}


@app.post("/telemetry")
def telemetry(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return process_telemetry(store, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/shadows")
def shadows() -> dict[str, Any]:
    return store.shadows()


@app.get("/inventory")
def inventory() -> dict[str, Any]:
    return store.inventory()


@app.get("/events")
def events() -> dict[str, Any]:
    rows = store.events()
    return {"count": len(rows), "items": rows}
