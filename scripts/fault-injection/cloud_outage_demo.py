from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import Store, append_edge_cache, list_edge_cache, process_telemetry, rewrite_edge_cache, sample_telemetry


def main() -> None:
    store = Store()
    payloads = [sample_telemetry(abnormal=True), sample_telemetry(low_stock=True)]
    cached = [append_edge_cache(store, payload, reason="simulated cloud outage") for payload in payloads]
    replay_results = [process_telemetry(store, row["message"]) for row in cached]
    rewrite_edge_cache(store, [])
    result = {
        "cachedBeforeReplay": len(cached),
        "cacheRowsVisible": len(list_edge_cache(store)),
        "replayAccepted": sum(1 for item in replay_results if item["accepted"]),
        "eventsCreated": sum(len(item["events"]) for item in replay_results),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
