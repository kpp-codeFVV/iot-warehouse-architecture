from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import sample_telemetry


def post_json(url: str, payload: dict) -> float:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=10) as response:
        response.read()
    return time.perf_counter() - started


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((percent / 100) * (len(ordered) - 1))))
    return round(ordered[index] * 1000, 2)


def send_one(url: str, index: int, abnormal_every: int, unique_devices: bool) -> tuple[bool, float | None]:
    payload = sample_telemetry(abnormal=(index % abnormal_every == 0), low_stock=(index % 15 == 0))
    if unique_devices:
        payload["deviceId"] = f"sensor-{index + 1:05d}"
        payload["readings"]["shelfId"] = f"shelf-{(index % 100) + 1:03d}"
    try:
        latency = post_json(url, payload)
        return True, latency
    except Exception:
        return False, None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small local telemetry load test.")
    parser.add_argument("--url", default="http://localhost:8001/ingest")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--abnormal-every", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--unique-devices", action="store_true")
    args = parser.parse_args()

    started = time.perf_counter()
    latencies: list[float] = []
    errors = 0
    if args.concurrency <= 1:
        for index in range(args.count):
            ok, latency = send_one(args.url, index, args.abnormal_every, args.unique_devices)
            if ok and latency is not None:
                latencies.append(latency)
            else:
                errors += 1
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = [
                executor.submit(send_one, args.url, index, args.abnormal_every, args.unique_devices)
                for index in range(args.count)
            ]
            for future in concurrent.futures.as_completed(futures):
                ok, latency = future.result()
                if ok and latency is not None:
                    latencies.append(latency)
                else:
                    errors += 1
    elapsed = time.perf_counter() - started
    result = {
        "count": args.count,
        "concurrency": args.concurrency,
        "uniqueDevices": args.unique_devices,
        "errors": errors,
        "elapsedSeconds": round(elapsed, 3),
        "messagesPerSecond": round(args.count / elapsed, 2) if elapsed else args.count,
        "p50Ms": percentile(latencies, 50),
        "p95Ms": percentile(latencies, 95),
        "p99Ms": percentile(latencies, 99),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
