"""Kling 4.0 through the Raywake API: text to video, multi-shot and image to video.

Every command only prices the request unless you add --generate.

    export RAYWAKE_API_KEY=...
    python kling4.py text                     # one continuous shot
    python kling4.py shots                    # three shots in one video
    python kling4.py image --image-url URL    # animate a start frame
    python kling4.py shots --generate         # actually run it
"""
import argparse
import os
import sys
import time
import uuid

import requests

BASE = os.environ.get("RAYWAKE_API_BASE", "https://api.raywake.com")
TERMINAL = {"succeeded", "failed", "needs_review", "submission_unknown", "needs_reconciliation"}
SAMPLE_IMAGE = "https://raywake.si/previews/catalog/kling-v4-text-to-video.jpg"


def text_request(args):
    # One prompt (up to 26,000 characters) for one continuous shot of 3–30 seconds.
    return "kling/v4/text-to-video", {
        "prompt": "A detective in a black trench coat stands on a rooftop in the rain, looking through a "
                  "telescope at the street below. Neon reflections ripple across the wet concrete as the "
                  "camera slowly circles behind him.",
        "duration": args.duration,
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio,
    }


def shots_request(args):
    # Each shot: a prompt of up to 512 characters and 1–30 seconds. The video lasts the sum (3–30 s).
    # Send multi_prompt or prompt, never both. This is the burger clip shown on raywake.si.
    return "kling/v4/text-to-video", {
        "multi_prompt": [
            {"prompt": "Unbranded burger ingredients burst apart in mid-air against a pure black background: "
                       "a sesame seed bun, a flame-grilled beef patty, melting cheddar, crisp lettuce and a "
                       "tomato slice fly toward the camera in slow motion. Hard studio rim light.", "duration": 2},
            {"prompt": "The ingredients snap down onto each other and stack into a tall burger in one fast "
                       "motion. The camera rushes upward from a low angle, cheddar drips, sesame seeds bounce.",
             "duration": 2},
            {"prompt": "The finished burger lands on a dark wooden board, steam rising. The camera eases into "
                       "a slow orbit and settles on a hero shot. No text, no logos.", "duration": 1},
        ],
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio,
    }


def image_request(args):
    # The video takes its framing from the start image, so there is no aspect_ratio here.
    # Images: JPEG, PNG or WebP, at least 300 px, aspect ratio 0.4–2.5, at a public https URL.
    body = {
        "start_image_url": args.image_url,
        "prompt": "The camera slowly pushes in while steam rises from the burger and warm light moves across it.",
        "duration": args.duration,
        "resolution": args.resolution,
    }
    if args.end_image_url:
        body["end_image_url"] = args.end_image_url
    return "kling/v4/image-to-video", body


def call(method, path, **kwargs):
    headers = {"Authorization": f"Bearer {os.environ['RAYWAKE_API_KEY']}", **kwargs.pop("headers", {})}
    response = requests.request(method, f"{BASE}{path}", headers=headers, timeout=60, **kwargs)
    if not response.ok:
        sys.exit(f"{method} {path} failed with {response.status_code}: {response.text}")
    return response.json()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["text", "shots", "image"])
    parser.add_argument("--duration", type=int, default=5, help="3–30 seconds (ignored for shots)")
    parser.add_argument("--resolution", choices=["720p", "1080p"], default="720p")
    parser.add_argument("--aspect-ratio", choices=["16:9", "9:16", "1:1", "21:9"], default="16:9")
    parser.add_argument("--image-url", default=SAMPLE_IMAGE, help="start frame for image mode")
    parser.add_argument("--end-image-url", help="optional last frame for image mode")
    parser.add_argument("--generate", action="store_true", help="start the paid generation after quoting")
    args = parser.parse_args()

    model, payload = {"text": text_request, "shots": shots_request, "image": image_request}[args.mode](args)

    quote = call("POST", "/v1/quotes", json={"model": model, "input": payload})
    print(f"{model}: ${quote['price_usd']} (quote {quote['quote_id']}, expires {quote['expires_at']})")
    if not args.generate:
        print("Add --generate to start this generation.")
        return

    job = call("POST", "/v1/generate", json={"model": model, "input": payload, "quote_id": quote["quote_id"]},
               headers={"Idempotency-Key": str(uuid.uuid4())})
    while job["status"] not in TERMINAL:
        time.sleep(5)
        job = call("GET", f"/v1/jobs/{job['job_id']}")
        print("status:", job["status"])
    for output in job.get("outputs", []):
        print(output["type"], output["url"])


if __name__ == "__main__":
    main()
