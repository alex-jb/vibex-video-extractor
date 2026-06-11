# Reddit r/Python — vibex-video-extractor

**Subreddit:** r/Python · 1M+ members
**Best post window:** weekday 10am-1pm ET
**Flair:** Show and Tell

---

## Title

I built a 200-line FastAPI sidecar that lets Vercel functions call yt-dlp (the workaround pattern, not the destination)

## Body

Wanted to share a small pattern that's been useful for me.

**The problem:**

Vercel serverless functions can't run yt-dlp. The PyInstaller bundle is too big for the 50MB-zipped Functions limit. The writable-/tmp + subprocess-spawn semantics don't map well to serverless. Third-party scraping APIs are $99/mo (TikAPI) or $10-30/mo and break frequently (RapidAPI).

**The pattern:**

Shove yt-dlp into a 256MB Railway container behind FastAPI. Gate it with a Bearer token. Expose one `/extract` endpoint. Call it from the Vercel function the same way you'd call any 3rd-party API.

Total cost: $5/mo Railway + ~10 min/month to re-export cookies.txt when the platform invalidates the session.

```python
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
import yt_dlp
import os, secrets, tempfile

app = FastAPI()
BEARER_TOKEN = os.environ["BEARER_TOKEN"]

@app.post("/extract")
def extract(url: str, authorization: str = Header(...)):
    # Constant-time compare so we don't leak the token via timing
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "expected Bearer")
    if not secrets.compare_digest(parts[1], BEARER_TOKEN):
        raise HTTPException(401, "invalid")

    # Per-request tmpdir so concurrent calls don't cross-contaminate
    workdir = tempfile.mkdtemp(prefix="dl-")
    opts = {"outtmpl": f"{workdir}/%(id)s.%(ext)s", "quiet": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)
    # Find the produced mp4, return as FileResponse
    ...
```

The full sidecar (200 lines) is at github.com/alex-jb/vibex-video-extractor — MIT, Docker + Railway + GitHub Actions CI included.

**Why I'm sharing the pattern, not just the project:**

This pattern generalizes way past my Douyin use case. If you've been blocked by "Vercel/Cloudflare-Workers/Lambda can't run X" for any Python-only OSS tool, the same approach works:

- ffmpeg processing → ffmpeg-sidecar
- pandas-on-server → pandas-sidecar
- whisper transcription → whisper-sidecar
- spacy NER → spacy-sidecar

Just put the Python tool behind FastAPI, deploy to Railway/Render/Fly, and call it from your serverless function. The friction is much lower than people assume — you don't need Kubernetes, you don't need autoscaling for indie scale, you don't need anything fancy.

**Honest about coverage:**

- ✅ Douyin / TikTok works most weeks (yt-dlp's cat-and-mouse with the `a_bogus` signature breaks ~monthly, gets patched in 1-3 weeks)
- ❌ Xiaohongshu (yt-dlp has no extractor) — Phase 2 plan is vendoring JoeanAmier/XHS-Downloader as a GPL-3.0 sibling subprocess

**What I'd love feedback on:**

Anyone running a similar sidecar pattern in production? Specifically:
- How do you handle the 256MB Railway limit when adding more extractors?
- Have you found a clean Sentry / Prometheus integration that doesn't blow the memory budget?
- For cookies rotation, is anyone automating the re-export step or is everyone doing it manually?

Source: github.com/alex-jb/vibex-video-extractor
