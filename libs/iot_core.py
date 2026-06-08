from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TEMP_THRESHOLD = float(os.getenv("TEMP_THRESHOLD", "38.0"))
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: str) -> float:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).timestamp()


def data_dir() -> Path:
    path = Path(os.getenv("IOT_DATA_DIR", "runtime"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class Store:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or data_dir()
        self.root.mkdir(parents=True, exist_ok=True)
        self.shadows_path = self.root / "device_shadows.json"
        self.inventory_path = self.root / "inventory.json"
        self.events_path = self.root / "events.jsonl"
        self.alerts_path = self.root / "alerts.jsonl"
        self.processed_path = self.root / "processed_messages.json"
        self.processed_events_path = self.root / "processed_events.json"
        self.edge_cache_path = self.root / "edge_cache.jsonl"

    def shadows(self) -> dict[str, Any]:
        return read_json(self.shadows_path, {})

    def save_shadows(self, value: dict[str, Any]) -> None:
        write_json(self.shadows_path, value)

    def inventory(self) -> dict[str, Any]:
        return read_json(self.inventory_path, {})

    def save_inventory(self, value: dict[str, Any]) -> None:
        write_json(self.inventory_path, value)

    def processed_messages(self) -> set[str]:
        return set(read_json(self.processed_path, []))

    def save_processed_messages(self, value: set[str]) -> None:
        write_json(self.processed_path, sorted(value))

    def processed_events(self) -> set[str]:
        return set(read_json(self.processed_events_path, []))

    def save_processed_events(self, value: set[str]) -> None:
        write_json(self.processed_events_path, sorted(value))


def validate_telemetry(payload: dict[str, Any]) -> dict[str, Any]:
    required = ["messageId", "deviceId", "warehouseId", "deviceType", "timestamp", "readings"]
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if not isinstance(payload["readings"], dict):
        raise ValueError("readings must be an object")
    parse_time(str(payload["timestamp"]))
    return payload


def update_shadow(store: Store, telemetry: dict[str, Any]) -> dict[str, Any]:
    shadows = store.shadows()
    device_id = telemetry["deviceId"]
    existing = shadows.get(device_id)
    incoming_ts = parse_time(telemetry["timestamp"])
    if existing and parse_time(existing["lastSeenAt"]) > incoming_ts:
        return {"updated": False, "reason": "stale_message", "shadow": existing}

    shadow = {
        "deviceId": device_id,
        "warehouseId": telemetry["warehouseId"],
        "deviceType": telemetry["deviceType"],
        "connectionStatus": "online",
        "lastSeenAt": telemetry["timestamp"],
        "reported": telemetry["readings"],
        "desired": existing.get("desired", {}) if existing else {},
    }
    shadows[device_id] = shadow
    store.save_shadows(shadows)
    return {"updated": True, "shadow": shadow}


def update_inventory(store: Store, telemetry: dict[str, Any]) -> dict[str, Any] | None:
    readings = telemetry["readings"]
    shelf_id = readings.get("shelfId")
    sku_id = readings.get("skuId")
    quantity = readings.get("quantity")
    if shelf_id is None or sku_id is None or quantity is None:
        return None

    inventory = store.inventory()
    key = f"{telemetry['warehouseId']}:{shelf_id}:{sku_id}"
    item = {
        "warehouseId": telemetry["warehouseId"],
        "shelfId": shelf_id,
        "skuId": sku_id,
        "currentQuantity": int(quantity),
        "updatedAt": telemetry["timestamp"],
    }
    inventory[key] = item
    store.save_inventory(inventory)
    return item


def build_events(telemetry: dict[str, Any], inventory_item: dict[str, Any] | None) -> list[dict[str, Any]]:
    readings = telemetry["readings"]
    events: list[dict[str, Any]] = []
    temperature = readings.get("temperature")
    if temperature is not None and float(temperature) >= TEMP_THRESHOLD:
        events.append(
            {
                "eventId": f"evt-{telemetry['messageId']}-temp",
                "eventType": "HIGH_TEMPERATURE",
                "messageId": telemetry["messageId"],
                "deviceId": telemetry["deviceId"],
                "warehouseId": telemetry["warehouseId"],
                "occurredAt": telemetry["timestamp"],
                "detectedAt": utc_now(),
                "value": float(temperature),
                "threshold": TEMP_THRESHOLD,
            }
        )
    if inventory_item and inventory_item["currentQuantity"] <= LOW_STOCK_THRESHOLD:
        events.append(
            {
                "eventId": f"evt-{telemetry['messageId']}-stock",
                "eventType": "REPLENISHMENT_REQUIRED",
                "messageId": telemetry["messageId"],
                "warehouseId": telemetry["warehouseId"],
                "shelfId": inventory_item["shelfId"],
                "skuId": inventory_item["skuId"],
                "currentQuantity": inventory_item["currentQuantity"],
                "threshold": LOW_STOCK_THRESHOLD,
                "occurredAt": telemetry["timestamp"],
                "detectedAt": utc_now(),
            }
        )
    return events


def process_telemetry(store: Store, payload: dict[str, Any]) -> dict[str, Any]:
    telemetry = validate_telemetry(payload)
    processed = store.processed_messages()
    if telemetry["messageId"] in processed:
        return {"accepted": True, "duplicate": True, "events": []}

    shadow_result = update_shadow(store, telemetry)
    inventory_item = update_inventory(store, telemetry)
    events = build_events(telemetry, inventory_item)
    for event in events:
        append_jsonl(store.events_path, event)
    processed.add(telemetry["messageId"])
    store.save_processed_messages(processed)
    return {
        "accepted": True,
        "duplicate": False,
        "shadowUpdated": shadow_result["updated"],
        "events": events,
    }


def process_alert_events(store: Store) -> dict[str, Any]:
    processed = store.processed_events()
    created: list[dict[str, Any]] = []
    for event in read_jsonl(store.events_path):
        event_id = event["eventId"]
        if event_id in processed or event["eventType"] == "REPLENISHMENT_REQUIRED":
            continue
        alert = {
            "alertId": f"alert-{event_id}",
            "eventId": event_id,
            "alertType": event["eventType"],
            "deviceId": event.get("deviceId"),
            "warehouseId": event["warehouseId"],
            "value": event.get("value"),
            "threshold": event.get("threshold"),
            "status": "OPEN",
            "createdAt": utc_now(),
        }
        append_jsonl(store.alerts_path, alert)
        processed.add(event_id)
        created.append(alert)
    store.save_processed_events(processed)
    return {"created": created, "createdCount": len(created)}


def append_edge_cache(store: Store, telemetry: dict[str, Any], reason: str) -> dict[str, Any]:
    validate_telemetry(telemetry)
    row = {
        "cacheId": str(uuid.uuid4()),
        "reason": reason,
        "cachedAt": utc_now(),
        "message": telemetry,
    }
    append_jsonl(store.edge_cache_path, row)
    return row


def list_edge_cache(store: Store) -> list[dict[str, Any]]:
    return read_jsonl(store.edge_cache_path)


def rewrite_edge_cache(store: Store, rows: list[dict[str, Any]]) -> None:
    if not rows:
        store.edge_cache_path.write_text("", encoding="utf-8")
        return
    store.edge_cache_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def sample_telemetry(abnormal: bool = False, low_stock: bool = False) -> dict[str, Any]:
    now = utc_now()
    return {
        "messageId": f"msg-{uuid.uuid4()}",
        "deviceId": "sensor-001",
        "warehouseId": "wh-01",
        "deviceType": "temperature-weight-sensor",
        "timestamp": now,
        "readings": {
            "temperature": 39.8 if abnormal else 25.1,
            "humidity": 60.0,
            "shelfId": "shelf-A1",
            "skuId": "SKU-001",
            "quantity": 5 if low_stock else 42,
        },
    }


def measure_alert_latency_seconds(telemetry: dict[str, Any], alert: dict[str, Any]) -> float:
    return round(parse_time(alert["createdAt"]) - parse_time(telemetry["timestamp"]), 3)


def sleep_ms(milliseconds: int) -> None:
    time.sleep(milliseconds / 1000)

