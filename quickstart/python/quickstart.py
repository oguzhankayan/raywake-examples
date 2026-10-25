"""Quote, generate and poll one Raywake generation.

By default this only requests a free quote. Add --generate to start the paid run.

    export RAYWAKE_API_KEY=...
    python quickstart.py                 # price only
    python quickstart.py --generate      # spend the quote and wait for the result
"""
import argparse
import os
import sys
import time
import uuid

import requests

BASE = os.environ.get("RAYWAKE_API_BASE", "https://api.raywake.com")
TERMINAL = {"succeeded", "failed", "needs_review", "submission_unknown", "needs_reconciliation"}

MODEL = "kling/v4/text-to-video"
INPUT = {
    "prompt": "A perfume bottle on a stone table. Slow camera push in, soft window light, one continuous shot.",
    "duration": 5,
    "resolution": "720p",
    "aspect_ratio": "16:9",
}


def call(method, path, **kwargs):
    headers = {"Authorization": f"Bearer {os.environ['RAYWAKE_API_KEY']}", **kwargs.pop("headers", {})}
    response = requests.request(method, f"{BASE}{path}", headers=headers, timeout=60, **kwargs)
    if not response.ok:
        sys.exit(f"{method} {path} failed with {response.status_code}: {response.text}")
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="start the paid generation after quoting")
    args = parser.parse_args()

    # 1. Price the exact input. Quotes are free and valid for up to 10 minutes.
    quote = call("POST", "/v1/quotes", json={"model": MODEL, "input": INPUT})
    print(f"Quote {quote['quote_id']}: ${quote['price_usd']} (expires {quote['expires_at']})")
    if not args.generate:
        print("Run again with --generate to start this generation.")
        return

    # 2. Start the generation with the same model and input. Keep the key if you retry this request.
    job = call("POST", "/v1/generate", json={"model": MODEL, "input": INPUT, "quote_id": quote["quote_id"]},
               headers={"Idempotency-Key": str(uuid.uuid4())})

    # 3. Poll until the job reaches a terminal status.
    while job["status"] not in TERMINAL:
        time.sleep(3)
        job = call("GET", f"/v1/jobs/{job['job_id']}")
        print("status:", job["status"])

    for output in job.get("outputs", []):
        print(output["type"], output["url"])


if __name__ == "__main__":
    main()
