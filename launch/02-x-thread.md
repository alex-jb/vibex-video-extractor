# X thread — vibex-video-extractor

**Best post window:** weekdays 9-11am ET or 5-7pm ET
**Hashtags:** none (algorithm penalizes)

---

**1/**
Shipped a $5/mo Python sidecar that lets your Vercel function watch Douyin videos.

Vercel can't run yt-dlp. RapidAPI is $99/mo + unreliable. TikAPI is $99/mo + stable.

This sidecar: FastAPI + yt-dlp + Docker + Railway one-click. $5/mo flat.

🔗 github.com/alex-jb/vibex-video-extractor

**2/**
The use case:

I have a Next.js app on Vercel (vibexforge.com) that wants to analyze Chinese short-form video via Gemini 2.5 Flash. Gemini needs the mp4. Vercel can't run yt-dlp. Railway can.

Sidecar exposes one endpoint:

```
POST /extract  { url: "https://v.douyin.com/..." }
→ returns mp4 binary
```

**3/**
Bearer token auth + constant-time compare so it's not a public scraper.
Per-request tmpdirs so concurrent calls don't cross-contaminate.
GitHub Actions CI verifies the Docker image actually boots on every push.

200 lines of Python. Bilingual README (EN + 中文). MIT.

**4/**
Honest about coverage:

✅ Douyin / TikTok — works most weeks. Cookie-dependent. Breaks ~monthly on the a_bogus signature rotation, gets patched 1-3 weeks later in yt-dlp main.

❌ Xiaohongshu — yt-dlp has no extractor. Plan: vendor JoeanAmier/XHS-Downloader as a GPL-3.0 sibling subprocess. Phase 2.

**5/**
Cost math vs alternatives:

- TikAPI: $99/mo (stable)
- RapidAPI: $10-30/mo (breaks every few months)
- This sidecar: $5/mo Railway + 10 min/mo cookies re-export

For indie / personal scale, $5 + 10 min wins easily.

**6/**
Paired with vibexforge.com/tools/video-decode + a Claude Skill (vibex-video-decoder-skill) so users in claude.ai paste a Douyin URL and Claude returns the hook breakdown + 3 remix scripts.

Sidecar is the boring infra layer that makes the rest work.

**7/**
Legal posture (honest):

Acts on individual user-triggered URLs only, no bulk scraping, no caching beyond the immediate response. Same posture as your personal yt-dlp install. Douyin ToS section 8.2 forbids automated access — recommended for indie/research/personal, NOT B2B SaaS scale.

**8/**
Source: github.com/alex-jb/vibex-video-extractor

If you've been blocked by "Vercel can't run X" for any other Python-only OSS tool — this pattern (Railway sidecar + Bearer token + Docker) generalizes. Steal it.

Replies open. What would you point yt-dlp at if you had a one-click way to deploy it as a service?
