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
        self.database_url = os.getenv("DATABASE_URL") if root is None else None
        self._pool: Any | None = None
        self.shadows_path = self.root / "device_shadows.json"
        self.inventory_path = self.root / "inventory.json"
        self.events_path = self.root / "events.jsonl"
        self.alerts_path = self.root / "alerts.jsonl"
        self.processed_path = self.root / "processed_messages.json"
        self.processed_events_path = self.root / "processed_events.json"
        self.edge_cache_path = self.root / "edge_cache.jsonl"
        if self.database_url:
            self._open_pool()
            self._ensure_schema()

    def _open_pool(self) -> None:
        from psycopg_pool import ConnectionPool

        max_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self._pool = ConnectionPool(self.database_url, min_size=1, max_size=max_size, open=False)
        self._pool.open(wait=True)

    def _jsonb(self, value: Any) -> Any:
        from psycopg.types.json import Jsonb

        return Jsonb(value)

    def _connection(self) -> Any:
        if self._pool is None:
            raise RuntimeError("database pool is not initialized")
        return self._pool.connection()

    def _ensure_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS iot_messages (
            message_id TEXT PRIMARY KEY,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE IF NOT EXISTS device_shadows (
            device_id TEXT PRIMARY KEY,
            warehouse_id TEXT NOT NULL,
            device_type TEXT NOT NULL,
            connection_status TEXT NOT NULL,
            last_seen_at TIMESTAMPTZ NOT NULL,
            reported JSONB NOT NULL,
            desired JSONB NOT NULL DEFAULT '{}'::jsonb
        );
        CREATE TABLE IF NOT EXISTS inventory_items (
            item_key TEXT PRIMARY KEY,
            warehouse_id TEXT NOT NULL,
            shelf_id TEXT NOT NULL,
            sku_id TEXT NOT NULL,
            current_quantity INTEGER NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL
        );
        CREATE TABLE IF NOT EXISTS iot_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            message_id TEXT NOT NULL,
            warehouse_id TEXT NOT NULL,
            occurred_at TIMESTAMPTZ NOT NULL,
            detected_at TIMESTAMPTZ NOT NULL,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS idx_iot_events_created_at ON iot_events (created_at);
        CREATE INDEX IF NOT EXISTS idx_iot_events_type_created_at ON iot_events (event_type, created_at);
        CREATE TABLE IF NOT EXISTS iot_alerts (
            alert_id TEXT PRIMARY KEY,
            event_id TEXT UNIQUE NOT NULL,
            alert_type TEXT NOT NULL,
            device_id TEXT,
            warehouse_id TEXT NOT NULL,
            status TEXT NOT NULL,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS idx_iot_alerts_created_at ON iot_alerts (created_at);
        """
        last_error: Exception | None = None
        for _ in range(30):
            try:
                with self._connection() as conn:
                    conn.execute(schema)
                return
            except Exception as exc:  # pragma: no cover - exercised by Docker startup timing
                last_error = exc
                time.sleep(1)
        raise RuntimeError(f"database schema initialization failed: {last_error}") from last_error

    def shadows(self) -> dict[str, Any]:
        if self.database_url:
            with self._connection() as conn:
                rows = conn.execute(
                    """
                    SELECT device_id, warehouse_id, device_type, connection_status,
                           last_seen_at, reported, desired
                    FROM device_shadows
                    """
                ).fetchall()
            return {
                row[0]: {
                    "deviceId": row[0],
                    "warehouseId": row[1],
                    "deviceType": row[2],
                    "connectionStatus": row[3],
                    "lastSeenAt": row[4].isoformat(),
                    "reported": row[5],
                    "desired": row[6],
                }
                for row in rows
            }
        return read_json(self.shadows_path, {})

    def save_shadows(self, value: dict[str, Any]) -> None:
        write_json(self.shadows_path, value)

    def inventory(self) -> dict[str, Any]:
        if self.database_url:
            with self._connection() as conn:
                rows = conn.execute(
                    """
                    SELECT item_key, warehouse_id, shelf_id, sku_id, current_quantity, updated_at
                    FROM inventory_items
                    """
                ).fetchall()
            return {
                row[0]: {
                    "warehouseId": row[1],
                    "shelfId": row[2],
                    "skuId": row[3],
                    "currentQuantity": row[4],
                    "updatedAt": row[5].isoformat(),
                }
                for row in rows
            }
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

    def record_message_once(self, telemetry: dict[str, Any]) -> bool:
        if self.database_url:
            with self._connection() as conn:
                row = conn.execute(
                    """
                    INSERT INTO iot_messages (message_id, payload)
                    VALUES (%s, %s)
                    ON CONFLICT (message_id) DO NOTHING
                    RETURNING message_id
                    """,
                    (telemetry["messageId"], self._jsonb(telemetry)),
                ).fetchone()
            return row is not None

        processed = self.processed_messages()
        if telemetry["messageId"] in processed:
            return False
        processed.add(telemetry["messageId"])
        self.save_processed_messages(processed)
        return True

    def upsert_shadow(self, telemetry: dict[str, Any]) -> dict[str, Any]:
        if self.database_url:
            shadow = {
                "deviceId": telemetry["deviceId"],
                "warehouseId": telemetry["warehouseId"],
                "deviceType": telemetry["deviceType"],
                "connectionStatus": "online",
                "lastSeenAt": telemetry["timestamp"],
                "reported": telemetry["readings"],
                "desired": {},
            }
            with self._connection() as conn:
                row = conn.execute(
                    """
                    INSERT INTO device_shadows (
                        device_id, warehouse_id, device_type, connection_status,
                        last_seen_at, reported, desired
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, '{}'::jsonb)
                    ON CONFLICT (device_id) DO UPDATE SET
                        warehouse_id = EXCLUDED.warehouse_id,
                        device_type = EXCLUDED.device_type,
                        connection_status = EXCLUDED.connection_status,
                        last_seen_at = EXCLUDED.last_seen_at,
                        reported = EXCLUDED.reported
                    WHERE device_shadows.last_seen_at <= EXCLUDED.last_seen_at
                    RETURNING desired
                    """,
                    (
                        telemetry["deviceId"],
                        telemetry["warehouseId"],
                        telemetry["deviceType"],
                        "online",
                        telemetry["timestamp"],
                        self._jsonb(telemetry["readings"]),
                    ),
                ).fetchone()
                if row is not None:
                    shadow["desired"] = row[0]
                    return {"updated": True, "shadow": shadow}
            existing = self.shadows()[telemetry["deviceId"]]
            return {"updated": False, "reason": "stale_message", "shadow": existing}

        shadows = self.shadows()
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
        self.save_shadows(shadows)
        return {"updated": True, "shadow": shadow}

    def upsert_inventory(self, telemetry: dict[str, Any]) -> dict[str, Any] | None:
        item = self._inventory_item_from_telemetry(telemetry)
        if item is None:
            return None
        if self.database_url:
            with self._connection() as conn:
                conn.execute(
                    """
                    INSERT INTO inventory_items (
                        item_key, warehouse_id, shelf_id, sku_id, current_quantity, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (item_key) DO UPDATE SET
                        warehouse_id = EXCLUDED.warehouse_id,
                        shelf_id = EXCLUDED.shelf_id,
                        sku_id = EXCLUDED.sku_id,
                        current_quantity = EXCLUDED.current_quantity,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        item["itemKey"],
                        item["warehouseId"],
                        item["shelfId"],
                        item["skuId"],
                        item["currentQuantity"],
                        item["updatedAt"],
                    ),
                )
            return {key: value for key, value in item.items() if key != "itemKey"}

        inventory = self.inventory()
        inventory[item["itemKey"]] = {key: value for key, value in item.items() if key != "itemKey"}
        self.save_inventory(inventory)
        return inventory[item["itemKey"]]

    def append_events(self, events: list[dict[str, Any]]) -> None:
        if not events:
            return
        if self.database_url:
            with self._connection() as conn:
                for event in events:
                    conn.execute(
                        """
                        INSERT INTO iot_events (
                            event_id, event_type, message_id, warehouse_id,
                            occurred_at, detected_at, payload
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (event_id) DO NOTHING
                        """,
                        (
                            event["eventId"],
                            event["eventType"],
                            event["messageId"],
                            event["warehouseId"],
                            event["occurredAt"],
                            event["detectedAt"],
                            self._jsonb(event),
                        ),
                    )
            return
        for event in events:
            append_jsonl(self.events_path, event)

    def events(self) -> list[dict[str, Any]]:
        if self.database_url:
            with self._connection() as conn:
                rows = conn.execute("SELECT payload FROM iot_events ORDER BY created_at, event_id").fetchall()
            return [row[0] for row in rows]
        return read_jsonl(self.events_path)

    def record_alert_once(self, alert: dict[str, Any]) -> bool:
        if self.database_url:
            with self._connection() as conn:
                row = conn.execute(
                    """
                    INSERT INTO iot_alerts (
                        alert_id, event_id, alert_type, device_id, warehouse_id, status, payload
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO NOTHING
                    RETURNING alert_id
                    """,
                    (
                        alert["alertId"],
                        alert["eventId"],
                        alert["alertType"],
                        alert.get("deviceId"),
                        alert["warehouseId"],
                        alert["status"],
                        self._jsonb(alert),
                    ),
                ).fetchone()
            return row is not None

        processed = self.processed_events()
        if alert["eventId"] in processed:
            return False
        append_jsonl(self.alerts_path, alert)
        processed.add(alert["eventId"])
        self.save_processed_events(processed)
        return True

    def alerts(self) -> list[dict[str, Any]]:
        if self.database_url:
            with self._connection() as conn:
                rows = conn.execute("SELECT payload FROM iot_alerts ORDER BY created_at, alert_id").fetchall()
            return [row[0] for row in rows]
        return read_jsonl(self.alerts_path)

    def process_telemetry_in_database(self, telemetry: dict[str, Any]) -> dict[str, Any]:
        if not self.database_url:
            raise RuntimeError("database mode is not enabled")

        shadow = {
            "deviceId": telemetry["deviceId"],
            "warehouseId": telemetry["warehouseId"],
            "deviceType": telemetry["deviceType"],
            "connectionStatus": "online",
            "lastSeenAt": telemetry["timestamp"],
            "reported": telemetry["readings"],
            "desired": {},
        }
        inventory_item = self._inventory_item_from_telemetry(telemetry)

        with self._connection() as conn:
            message_row = conn.execute(
                """
                INSERT INTO iot_messages (message_id, payload)
                VALUES (%s, %s)
                ON CONFLICT (message_id) DO NOTHING
                RETURNING message_id
                """,
                (telemetry["messageId"], self._jsonb(telemetry)),
            ).fetchone()
            if message_row is None:
                return {"accepted": True, "duplicate": True, "events": []}

            shadow_row = conn.execute(
                """
                INSERT INTO device_shadows (
                    device_id, warehouse_id, device_type, connection_status,
                    last_seen_at, reported, desired
                )
                VALUES (%s, %s, %s, %s, %s, %s, '{}'::jsonb)
                ON CONFLICT (device_id) DO UPDATE SET
                    warehouse_id = EXCLUDED.warehouse_id,
                    device_type = EXCLUDED.device_type,
                    connection_status = EXCLUDED.connection_status,
                    last_seen_at = EXCLUDED.last_seen_at,
                    reported = EXCLUDED.reported
                WHERE device_shadows.last_seen_at <= EXCLUDED.last_seen_at
                RETURNING desired
                """,
                (
                    telemetry["deviceId"],
                    telemetry["warehouseId"],
                    telemetry["deviceType"],
                    "online",
                    telemetry["timestamp"],
                    self._jsonb(telemetry["readings"]),
                ),
            ).fetchone()
            shadow_updated = shadow_row is not None
            if shadow_row is not None:
                shadow["desired"] = shadow_row[0]

            if inventory_item is not None:
                conn.execute(
                    """
                    INSERT INTO inventory_items (
                        item_key, warehouse_id, shelf_id, sku_id, current_quantity, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (item_key) DO UPDATE SET
                        warehouse_id = EXCLUDED.warehouse_id,
                        shelf_id = EXCLUDED.shelf_id,
                        sku_id = EXCLUDED.sku_id,
                        current_quantity = EXCLUDED.current_quantity,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        inventory_item["itemKey"],
                        inventory_item["warehouseId"],
                        inventory_item["shelfId"],
                        inventory_item["skuId"],
                        inventory_item["currentQuantity"],
                        inventory_item["updatedAt"],
                    ),
                )

            events = build_events(telemetry, inventory_item)
            for event in events:
                conn.execute(
                    """
                    INSERT INTO iot_events (
                        event_id, event_type, message_id, warehouse_id,
                        occurred_at, detected_at, payload
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO NOTHING
                    """,
                    (
                        event["eventId"],
                        event["eventType"],
                        event["messageId"],
                        event["warehouseId"],
                        event["occurredAt"],
                        event["detectedAt"],
                        self._jsonb(event),
                    ),
                )

        return {
            "accepted": True,
            "duplicate": False,
            "shadowUpdated": shadow_updated,
            "events": events,
        }

    def _inventory_item_from_telemetry(self, telemetry: dict[str, Any]) -> dict[str, Any] | None:
        readings = telemetry["readings"]
        shelf_id = readings.get("shelfId")
        sku_id = readings.get("skuId")
        quantity = readings.get("quantity")
        if shelf_id is None or sku_id is None or quantity is None:
            return None
        key = f"{telemetry['warehouseId']}:{shelf_id}:{sku_id}"
        return {
            "itemKey": key,
            "warehouseId": telemetry["warehouseId"],
            "shelfId": shelf_id,
            "skuId": sku_id,
            "currentQuantity": int(quantity),
            "updatedAt": telemetry["timestamp"],
        }


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
    return store.upsert_shadow(telemetry)


def update_inventory(store: Store, telemetry: dict[str, Any]) -> dict[str, Any] | None:
    return store.upsert_inventory(telemetry)


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
    if store.database_url:
        return store.process_telemetry_in_database(telemetry)
    if not store.record_message_once(telemetry):
        return {"accepted": True, "duplicate": True, "events": []}

    shadow_result = update_shadow(store, telemetry)
    inventory_item = update_inventory(store, telemetry)
    events = build_events(telemetry, inventory_item)
    store.append_events(events)
    return {
        "accepted": True,
        "duplicate": False,
        "shadowUpdated": shadow_result["updated"],
        "events": events,
    }


def process_alert_events(store: Store) -> dict[str, Any]:
    created: list[dict[str, Any]] = []
    for event in store.events():
        event_id = event["eventId"]
        if event["eventType"] == "REPLENISHMENT_REQUIRED":
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
        if store.record_alert_once(alert):
            created.append(alert)
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
