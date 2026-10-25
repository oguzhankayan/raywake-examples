# Kling 4.0 API example

Kling 4.0 generates 3–30 second videos at 720p or 1080p from a prompt, from per-shot prompts or from a start
image with an optional end frame. Clips come back with generated sound. On Raywake it is billed per second of
output with no subscription: **$0.2737/s at 720p and $0.4097/s at 1080p** (25 October 2026).

```bash
pip install -r ../../requirements.txt
export RAYWAKE_API_KEY=...            # create one at https://raywake.si/api-keys

python kling4.py text                 # free quote for one continuous shot
python kling4.py shots                # free quote for the three-shot burger clip
python kling4.py image --image-url https://example.com/product.jpg
python kling4.py shots --generate     # start the paid run and wait for the video
```

| Mode | Model ID | Key inputs |
| --- | --- | --- |
| `text` | `kling/v4/text-to-video` | `prompt` (≤26,000 chars), `duration` 3–30, `resolution`, `aspect_ratio` 16:9 · 9:16 · 1:1 · 21:9 |
| `shots` | `kling/v4/text-to-video` | `multi_prompt`: shots of ≤512 chars and 1–30 s each, 3–30 s in total |
| `image` | `kling/v4/image-to-video` | `start_image_url` (required), optional `end_image_url`, `prompt`, `duration`, `resolution` |

`prompt` and `multi_prompt` are alternatives: send one of them. The 512-character limit applies to each shot's
prompt, and both limits come from the Kling 4.0 API itself.

| Length | 720p | 1080p |
| --- | ---: | ---: |
| 5 s | $1.37 | $2.05 |
| 10 s | $2.74 | $4.10 |
| 30 s | $8.21 | $12.29 |

Quotes are the price you approve; the run is never charged more.

More: [Kling 4.0 guide](https://raywake.si/blog/kling-4-0) · [model page](https://raywake.si/explore/kling/v4/text-to-video) ·
[quotes reference](https://raywake.si/docs/reference/quotes) · [generations](https://raywake.si/docs/generations)
