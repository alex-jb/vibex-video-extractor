# LinkedIn — vibex-video-extractor

**Best post window:** weekday 8-10am ET
**Audience:** technical hiring managers, fellow indie founders, infra engineers

---

Shipped a $5/mo Python sidecar that solves a specific gap: how do you run yt-dlp from a Vercel serverless function?

The honest answer: you don't. Vercel doesn't ship a Python runtime by default, yt-dlp's PyInstaller bundle is too big for the 50MB-zipped Functions limit, and the writable-/tmp + subprocess-spawn semantics map poorly to serverless.

What's worked for me: shove yt-dlp into a 256MB Railway container behind FastAPI, gate it with a Bearer token, expose one `/extract` endpoint, and call it from the Vercel function the same way you'd call any 3rd-party API.

Why I bothered building it:

I'm running vibexforge.com — a platform for Chinese indie AI makers — and I needed a way to let the app analyze Douyin / TikTok videos via Gemini 2.5 Flash. The third-party APIs were $99/mo (TikAPI) or $30/mo and unreliable (RapidAPI). Building the sidecar took an afternoon. $5/mo Railway is now my baseline cost.

What's in the box:

→ Python 3.12 + FastAPI + uvicorn
→ yt-dlp 2025.6.5 (The Unlicense — public-domain-equivalent)
→ Docker image with ffmpeg pre-installed
→ railway.json for one-click deploy
→ Bearer token auth + constant-time comparison
→ Per-request tmpdirs (concurrency-safe)
→ GitHub Actions CI: ruff + smoke tests + Docker build verify
→ Bilingual README (EN + 中文)
→ MIT license

Honest coverage:
✅ Douyin / TikTok — works most weeks, breaks ~monthly on a_bogus signature rotation
❌ Xiaohongshu — yt-dlp has no extractor. Vendor JoeanAmier/XHS-Downloader as GPL-3.0 sibling subprocess. Phase 2.

Why I'm sharing publicly:

If you've been blocked by "Vercel can't run X" for some Python-only OSS tool, this pattern (Railway sidecar + Bearer token + Docker + the matching Vercel client) generalizes to any such case. Steal it.

If you want a Chinese short-form video AI assistant, the full stack is also open:
- github.com/alex-jb/vibex-video-extractor (this — the sidecar)
- github.com/alex-jb/vibex (Next.js app + Gemini integration)
- github.com/alex-jb/vibex-video-decoder-skill (Claude Skill wrapper)

Calibration-honest by default. Built solo, shipped to production this week.
