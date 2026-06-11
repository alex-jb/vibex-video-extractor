# HN Show launch — vibex-video-extractor

**When to post:** Tue/Wed/Thu 8-10am ET. Avoid Mondays + Fridays.
**Title:** Show HN: $5/mo Python sidecar that lets your Vercel function watch Douyin videos

---

## Post body

Vercel serverless can't run yt-dlp. Third-party scraping APIs are $99/mo. I needed a way to let my Vercel-hosted Next.js app (vibexforge.com) analyze Douyin / TikTok videos via Gemini 2.5 Flash, so I shoved yt-dlp into a 256MB Railway container and paid $5/mo for sanity.

This repo is that container. Paste a Douyin URL, get the raw mp4 back. Python + FastAPI + yt-dlp + Docker + Railway one-click deploy.

**What's interesting (maybe):**

- yt-dlp gets ~$0.00 of attention even though it's the most-active video extractor in OSS. Wraping it in a 200-line FastAPI service unlocks it for the entire Vercel/Cloudflare-Workers/Lambda ecosystem that can't run Python natively.
- Bearer token + constant-time compare so it's not a public scraper. Per-request tmpdirs so concurrent calls don't cross-contaminate. Smoke test in CI verifies the Docker image actually boots.
- Honest about coverage: Douyin / TikTok works most of the time (cookie-dependent, breaks ~monthly on a_bogus signature rotation). Xiaohongshu doesn't — yt-dlp has no XHS extractor and the path forward is vendoring JoeanAmier/XHS-Downloader under a GPL-3.0 sibling subprocess. Phase 2.
- Bilingual README (EN + 中文) because Chinese short-form is where the audience is.

**Cost math vs alternatives:**

- TikAPI: $99/mo. Stable. We didn't pick it.
- RapidAPI TikTok scrapers: $10-30/mo. Break every few months.
- This sidecar: $5/mo Railway + ~10 min/month to re-export cookies.txt when Douyin invalidates the session.

**What the sidecar is paired with:**

- vibex-video-decoder-skill (Claude Skill): users in claude.ai paste a Douyin URL → Claude calls vibex API → sidecar pulls mp4 → Gemini 2.5 Flash watches → returns hook breakdown + 3 remix scripts. Single thread, no tab switching.
- vibexforge.com/tools/video-decode: web UI same idea, $5 for 100 decodes.

**Legal posture (honest):** acts on individual user-triggered URLs only, no bulk scraping, no caching beyond the immediate response. Same posture as your personal yt-dlp install. Douyin ToS section 8.2 forbids automated access, so this is for indie / research / personal use, NOT B2B SaaS scale.

MIT license, source: github.com/alex-jb/vibex-video-extractor

What problems would you point yt-dlp at if you had a one-click way to deploy it as a service?
