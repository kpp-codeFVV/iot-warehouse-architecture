from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import Store, append_edge_cache, list_edge_cache, rewrite_edge_cache, validate_telemetry


app = FastAPI(title="device-gateway", version="0.1.0")
store = Store()
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://localhost:8002")


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


@app.get("/health")
def health() -> dict[str, Any]:
    return {"service": "device-gateway", "status": "ok", "cachedMessages": len(list_edge_cache(store))}


@app.post("/ingest")
def ingest(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        telemetry = validate_telemetry(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        result = post_json(f"{INVENTORY_URL}/telemetry", telemetry)
        return {"accepted": True, "forwarded": True, "inventory": result}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        cached = append_edge_cache(store, telemetry, reason=str(exc))
        return {"accepted": True, "forwarded": False, "cached": cached}


@app.get("/cache")
def cache() -> dict[str, Any]:
    rows = list_edge_cache(store)
    return {"count": len(rows), "items": rows}


@app.post("/replay")
def replay() -> dict[str, Any]:
    rows = list_edge_cache(store)
    remaining: list[dict[str, Any]] = []
    replayed = 0
    for row in rows:
        try:
            post_json(f"{INVENTORY_URL}/telemetry", row["message"])
            replayed += 1
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            remaining.append(row)
    rewrite_edge_cache(store, remaining)
    return {"replayed": replayed, "remaining": len(remaining)}

