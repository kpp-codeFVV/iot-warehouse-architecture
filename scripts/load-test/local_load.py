from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import sample_telemetry


def post_json(url: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:
        response.read()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small local telemetry load test.")
    parser.add_argument("--url", default="http://localhost:8001/ingest")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--abnormal-every", type=int, default=10)
    args = parser.parse_args()

    started = time.perf_counter()
    errors = 0
    for index in range(args.count):
        payload = sample_telemetry(abnormal=(index % args.abnormal_every == 0), low_stock=(index % 15 == 0))
        try:
            post_json(args.url, payload)
        except Exception:
            errors += 1
    elapsed = time.perf_counter() - started
    result = {
        "count": args.count,
        "errors": errors,
        "elapsedSeconds": round(elapsed, 3),
        "messagesPerSecond": round(args.count / elapsed, 2) if elapsed else args.count,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

