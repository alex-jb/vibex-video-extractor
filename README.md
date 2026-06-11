# vibex-video-extractor

> **English** | [中文](README.zh-CN.md)

**Python sidecar for VibeXForge — paste a Douyin (抖音) URL, get the raw .mp4 back.**

Lives behind the `/api/video-decode` endpoint in [vibex](https://github.com/alex-jb/vibex). Vercel serverless can't run yt-dlp, so we shoved it into a 256MB Railway container and paid $5/mo for sanity.

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/alex-jb/vibex-video-extractor)

---

## What it does

```
POST /extract                 Authorization: Bearer <token>
{ "url": "https://v.douyin.com/iJSxxxxxx/" }
                                      ↓
                                returns mp4 bytes
```

Streams the underlying mp4 from Douyin. The vibex web app then forwards the bytes to Gemini 2.5 Flash for hook + rhythm + CTA + remix-script analysis.

## Coverage 2026-06

| Platform | Status | Underlying |
|---|---|---|
| Douyin (抖音) | ✅ supported | `yt-dlp` extractor — cookie-dependent, breaks ~once a month on `a_bogus` signature rotation |
| TikTok | ✅ supported | same yt-dlp extractor |
| Xiaohongshu (小红书) | ❌ Phase 2 | yt-dlp has no extractor. Plan: vendor [JoeanAmier/XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader) logic under GPL-3.0 sibling process |

## Deploy on Railway in 5 minutes

```bash
# 1. Fork / clone this repo
git clone https://github.com/alex-jb/vibex-video-extractor
cd vibex-video-extractor

# 2. Generate a shared secret
openssl rand -base64 32
# → paste that into Railway → Variables → BEARER_TOKEN

# 3. Hit "Deploy" on https://railway.com/new — pick this repo
#    Railway reads Dockerfile + railway.json automatically.

# 4. After deploy, set Railway env vars:
#    BEARER_TOKEN=<the secret from step 2>
#    MAX_FILESIZE_MB=100   (default; bigger Railway plans can raise)

# 5. (Recommended for Douyin) Upload cookies.txt
#    - Use a logged-in Chrome with the "Get cookies.txt LOCALLY" extension
#    - Save the douyin.com cookies as cookies.txt
#    - Railway → Volumes → mount as /app/cookies.txt
#    - Set COOKIES_FILE=/app/cookies.txt

# 6. Smoke-test
curl https://<your-app>.up.railway.app/healthz
# {"ok": true, "version": "0.1.0", "cookies_configured": true}
```

Then in [vibex](https://github.com/alex-jb/vibex) `.env.local` and Vercel env:

```bash
VIDEO_EXTRACTOR_URL=https://<your-app>.up.railway.app
VIDEO_EXTRACTOR_TOKEN=<the same secret>
```

## Local dev

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export BEARER_TOKEN=dev-token
python main.py
# → http://localhost:8000

curl -X POST http://localhost:8000/extract \
  -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://v.douyin.com/iJSxxxxxx/"}' \
  --output out.mp4
```

## API

### `GET /healthz`

```json
{ "ok": true, "version": "0.1.0", "cookies_configured": true }
```

### `POST /extract`

Headers:
- `Authorization: Bearer <BEARER_TOKEN>`
- `Content-Type: application/json`

Body:
```json
{ "url": "https://v.douyin.com/..." }
```

Success: `200`, `Content-Type: video/mp4`, mp4 binary stream.
Failure:
- `400` unsupported URL host
- `401` missing / invalid bearer
- `403` cookies expired or required
- `413` exceeds `MAX_FILESIZE_MB`
- `501` Xiaohongshu (Phase 2)
- `502` upstream extractor failure (signature rotation, network)

Response headers on success:
- `X-Video-Platform: douyin`
- `X-Video-Duration: 47`
- `X-Video-Title: <utf-8 title>`
- `X-Extractor-Version: 0.1.0`

## Cookies — the actual ops cost

Douyin checks for a logged-in fingerprint. Without cookies you'll see "fresh cookies needed" failures. The honest workflow:

1. Use a regular Chrome profile to log in to douyin.com once
2. Export cookies with [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/cclelndahbckbenkjhflpdbgdldlbecc)
3. Save the file as `cookies.txt`, upload via Railway → Volumes
4. Re-export ~monthly when Douyin invalidates the session

About 10 minutes of ops per month. Cheaper than $99 RapidAPI.

## Legal posture

This sidecar acts on individual user-triggered URLs. It does not crawl, batch-scrape, or cache videos beyond the immediate response. That posture is the same as a personal `yt-dlp` install on your laptop. We do not warrant ToS compliance — Douyin's user agreement section 8.2 explicitly prohibits automated access, and you assume the risk for your own deployment.

**Recommended use:** indie / research / personal-scale. **Not recommended for:** large-volume B2B SaaS over Chinese platforms (the platform legal teams notice).

## Why not Vercel?

- Vercel serverless functions don't ship Python runtime by default
- yt-dlp + ffmpeg add ~80MB → too tight under Vercel's 50MB-zipped Function limit
- yt-dlp needs writable `/tmp` + spawn semantics that map poorly to serverless

Railway / Render / Fly = $5/mo, real Docker, no limits. Worth it.

## Why not RapidAPI / TikAPI?

- $99/mo flat minimum
- They go down for a week sometimes — you have zero control
- Their TOS is just as gray as yt-dlp; you pay for someone else's risk
- For solo indie scale, $5 Railway + 10 min/month cookies refresh wins

## Roadmap

- [x] Douyin / TikTok (yt-dlp)
- [ ] Xiaohongshu Phase 2 (vendor JoeanAmier/XHS-Downloader)
- [ ] Bilibili (yt-dlp has an extractor)
- [ ] Optional Cloudflare R2 cache for repeat-fetch of same URL (~30% cost cut)
- [ ] Prometheus `/metrics` endpoint
- [ ] Cookies rotation via Telegram bot ping (when extraction starts failing)

## License

MIT. yt-dlp is The Unlicense (public-domain equivalent). This is the cleanest commercial-friendly stack we could find.

## Related

- [vibex](https://github.com/alex-jb/vibex) — the Next.js app that calls this sidecar
- [council-diff](https://github.com/alex-jb/council-diff) — 5-voice + Fable 5 Oracle decision framework
- [solo-founder-os](https://github.com/alex-jb/solo-founder-os) — 11-agent open-source stack
