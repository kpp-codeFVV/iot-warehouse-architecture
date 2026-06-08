from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import Store, process_alert_events, read_jsonl


app = FastAPI(title="alert-service", version="0.1.0")
store = Store()


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "alert-service", "status": "ok"}


@app.post("/process-events")
def process_events() -> dict[str, Any]:
    return process_alert_events(store)


@app.get("/alerts")
def alerts() -> dict[str, Any]:
    rows = read_jsonl(store.alerts_path)
    return {"count": len(rows), "items": rows}

