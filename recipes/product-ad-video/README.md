# Product photos to ad clips

Animate a list of product photos with Kling 4.0 image to video. Each row becomes one clip that starts on your
photo. The script prices every clip first and prints the total; nothing runs until you add `--generate`.

```bash
pip install -r ../../requirements.txt
export RAYWAKE_API_KEY=...

python product_ads.py products.csv                          # free quotes and the total
python product_ads.py products.csv --generate               # 5 s clips at 720p
python product_ads.py products.csv --generate --duration 10 --resolution 1080p
```

`products.csv` columns: `name`, `image_url` (a public https JPEG, PNG or WebP, at least 300 px, aspect ratio
0.4–2.5) and an optional `motion` sentence. The clip keeps the photo's framing, so a vertical photo gives a vertical
clip. A 5-second 720p clip costs $1.37 on Raywake.

Use photos you have the rights to. See the [Kling 4.0 guide](https://raywake.si/blog/kling-4-0) for prompting tips.
