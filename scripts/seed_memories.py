"""
Legacy AI Platform -- Memory Seeder

Loads all memories from backend/data/sample_memories.json into the running API
via POST /api/v1/memories.

Usage:
    python scripts/seed_memories.py [--url http://localhost:8001]

The server must be running before you execute this script.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

DEFAULT_BASE_URL = "http://localhost:8001"
MEMORIES_ENDPOINT = "/api/v1/memories"
SAMPLE_FILE = "backend/data/sample_memories.json"


def _post_memory(base_url: str, payload: dict) -> tuple[int, dict]:
    url = base_url.rstrip("/") + MEMORIES_ENDPOINT
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            body = {"detail": str(exc)}
        return exc.code, body
    except urllib.error.URLError as exc:
        return 0, {"error": str(exc.reason)}


def seed(base_url: str) -> None:
    with open(SAMPLE_FILE, encoding="utf-8") as f:
        memories = json.load(f)

    print(f"Seeding {len(memories)} memories into {base_url} ...")
    ok = 0
    errors = 0
    for m in memories:
        status, body = _post_memory(base_url, m)
        if status == 200:
            ok += 1
            print(f"  [OK] {m.get('title', '?')} -> {body.get('memory_id', '?')}")
        else:
            errors += 1
            print(f"  [ERR {status}] {m.get('title', '?')} : {body}")

    print(f"\nDone: {ok} loaded, {errors} errors.")
    if errors:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed sample memories into the Legacy AI API.")
    parser.add_argument("--url", default=DEFAULT_BASE_URL,
                        help=f"Base URL of the running API (default: {DEFAULT_BASE_URL})")
    args = parser.parse_args()
    seed(base_url=args.url)


if __name__ == "__main__":
    main()
