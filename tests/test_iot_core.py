from __future__ import annotations

from datetime import datetime, timedelta, timezone

from libs.iot_core import (
    Store,
    append_edge_cache,
    list_edge_cache,
    measure_alert_latency_seconds,
    process_alert_events,
    process_telemetry,
    rewrite_edge_cache,
    sample_telemetry,
    update_shadow,
)


def test_abnormal_temperature_creates_alert(tmp_path):
    store = Store(tmp_path)
    telemetry = sample_telemetry(abnormal=True)

    result = process_telemetry(store, telemetry)
    alert_result = process_alert_events(store)

    assert result["accepted"] is True
    assert result["events"][0]["eventType"] == "HIGH_TEMPERATURE"
    assert alert_result["createdCount"] == 1
    assert measure_alert_latency_seconds(telemetry, alert_result["created"][0]) <= 5


def test_stale_shadow_update_is_rejected(tmp_path):
    store = Store(tmp_path)
    newer = sample_telemetry()
    older = sample_telemetry()
    newer["deviceId"] = "sensor-stale"
    older["deviceId"] = "sensor-stale"
    newer["timestamp"] = datetime.now(timezone.utc).isoformat()
    older["timestamp"] = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    newer["readings"]["temperature"] = 26
    older["readings"]["temperature"] = 19

    assert update_shadow(store, newer)["updated"] is True
    result = update_shadow(store, older)

    assert result["updated"] is False
    assert result["shadow"]["reported"]["temperature"] == 26


def test_edge_cache_replay_is_idempotent(tmp_path):
    store = Store(tmp_path)
    telemetry = sample_telemetry(abnormal=True)
    append_edge_cache(store, telemetry, reason="inventory unavailable")
    cached = list_edge_cache(store)

    first = process_telemetry(store, cached[0]["message"])
    second = process_telemetry(store, cached[0]["message"])
    rewrite_edge_cache(store, [])

    assert first["duplicate"] is False
    assert second["duplicate"] is True
    assert list_edge_cache(store) == []


def test_low_stock_creates_replenishment_event(tmp_path):
    store = Store(tmp_path)
    telemetry = sample_telemetry(low_stock=True)

    result = process_telemetry(store, telemetry)

    event_types = {event["eventType"] for event in result["events"]}
    assert "REPLENISHMENT_REQUIRED" in event_types
