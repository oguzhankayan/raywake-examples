# Raywake API examples

Runnable examples for the [Raywake](https://raywake.si) API: one API key and one prepaid USD balance for hundreds
of image, video and audio models, including Kling 4.0, FLUX 3 Max, Nano Banana and Seedance. Every request is
priced first with a free quote, and a generation can never cost more than the quote you approve.

These examples call the public HTTPS API only. Every script requests a free quote by default and starts a paid
generation only when you pass `--generate`.

## Quickstart

```bash
export RAYWAKE_API_KEY=...   # create a key at https://raywake.si/api-keys

python quickstart/python/quickstart.py            # pip install -r requirements.txt
node quickstart/javascript/quickstart.mjs         # Node.js 18+
bash quickstart/curl/quickstart.sh                # needs jq
```

Each one runs the same three steps: `POST /v1/quotes` prices the input, `POST /v1/generate` spends that quote with
an `Idempotency-Key`, and `GET /v1/jobs/{job_id}` is polled until the job is terminal.

## Examples

| Folder | What it shows |
| --- | --- |
| [models/kling-4-0](models/kling-4-0) | Kling 4.0 text to video, 30-second multi-shot video and image to video with an end frame |
| [recipes/product-ad-video](recipes/product-ad-video) | Turn a CSV of product photos into short ad clips, with the total price before anything runs |

## Documentation

- [Quickstart](https://raywake.si/docs/quickstart) and [authentication](https://raywake.si/docs/authentication)
- [Quotes and funds](https://raywake.si/docs/credits), [generations and job statuses](https://raywake.si/docs/generations)
- [Inputs and files](https://raywake.si/docs/inputs), [errors and limits](https://raywake.si/docs/errors)
- [All models](https://raywake.si/explore) · [Blog](https://raywake.si/blog)

Keep API keys on your server. They spend your balance; never ship them in browser or mobile code.

## License

MIT
