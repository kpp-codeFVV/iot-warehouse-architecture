from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from libs.iot_core import sample_telemetry


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Send sample telemetry to device-gateway.")
    parser.add_argument("--url", default="http://localhost:8001/ingest")
    parser.add_argument("--abnormal", action="store_true")
    parser.add_argument("--low-stock", action="store_true")
    args = parser.parse_args()

    payload = sample_telemetry(abnormal=args.abnormal, low_stock=args.low_stock)
    result = post_json(args.url, payload)
    print(json.dumps({"payload": payload, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

