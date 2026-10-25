"""Turn a CSV of product photos into short Kling 4.0 ad clips.

products.csv needs the columns name, image_url and (optionally) motion. The script quotes
every row and prints the total before anything runs; add --generate to start the clips.

    export RAYWAKE_API_KEY=...
    python product_ads.py products.csv
    python product_ads.py products.csv --generate --resolution 1080p
"""
import argparse
import csv
import os
import sys
import time
import uuid
from decimal import Decimal

import requests

BASE = os.environ.get("RAYWAKE_API_BASE", "https://api.raywake.com")
MODEL = "kling/v4/image-to-video"
TERMINAL = {"succeeded", "failed", "needs_review", "submission_unknown", "needs_reconciliation"}
DEFAULT_MOTION = "The camera slowly pushes in and orbits slightly while soft studio light sweeps across the product."


def call(method, path, **kwargs):
    headers = {"Authorization": f"Bearer {os.environ['RAYWAKE_API_KEY']}", **kwargs.pop("headers", {})}
    response = requests.request(method, f"{BASE}{path}", headers=headers, timeout=60, **kwargs)
    if not response.ok:
        sys.exit(f"{method} {path} failed with {response.status_code}: {response.text}")
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--duration", type=int, default=5, help="3–30 seconds per clip")
    parser.add_argument("--resolution", choices=["720p", "1080p"], default="720p")
    parser.add_argument("--generate", action="store_true", help="start the paid clips after quoting")
    args = parser.parse_args()

    with open(args.csv_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    planned, total = [], Decimal("0")
    for row in rows:
        payload = {
            "start_image_url": row["image_url"],
            "prompt": f"{row['name']} on a clean studio set. {row.get('motion') or DEFAULT_MOTION} No text, no logos.",
            "duration": args.duration,
            "resolution": args.resolution,
        }
        quote = call("POST", "/v1/quotes", json={"model": MODEL, "input": payload})
        total += Decimal(quote["price_usd"])
        planned.append((row["name"], payload, quote))
        print(f"{row['name']}: ${quote['price_usd']}")
    print(f"Total for {len(planned)} clips: ${total}")

    if not args.generate:
        print("Add --generate to start these clips. Quotes expire after about 10 minutes.")
        return

    for name, payload, quote in planned:
        job = call("POST", "/v1/generate", json={"model": MODEL, "input": payload, "quote_id": quote["quote_id"]},
                   headers={"Idempotency-Key": str(uuid.uuid4())})
        while job["status"] not in TERMINAL:
            time.sleep(5)
            job = call("GET", f"/v1/jobs/{job['job_id']}")
        urls = [output["url"] for output in job.get("outputs", [])]
        print(f"{name}: {job['status']} {' '.join(urls)}")


if __name__ == "__main__":
    main()
