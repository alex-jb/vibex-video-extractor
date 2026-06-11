# Changelog

All notable changes to vibex-video-extractor.

## [Unreleased]

### Planned
- Phase 2: Xiaohongshu real extraction via vendored JoeanAmier/XHS-Downloader (GPL-3.0 sibling subprocess)
- Bilibili extractor (yt-dlp has it, just need to wire)
- Optional Cloudflare R2 cache for repeat-fetch of same URL (~30% cost cut)
- Prometheus `/metrics` endpoint
- Cookies rotation Telegram bot ping when extraction starts failing

## [0.1.1] — 2026-06-11

### Added
- **Xiaohongshu best-effort path**: `_extract_xiaohongshu` now tries yt-dlp's generic extractor (`force_generic_extractor=True`) before raising 501. Most XHS URLs still fail (yt-dlp has no XHS extractor by design), but the occasional direct-mp4 link or non-DRMd older note surprise-wins without engineering.
- **Actionable 501 error message** for XHS naming 3 specific workarounds:
  - xhs-downloader Python lib
  - browser DevTools Network tab on `xiaohongshu.com/explore/<id>`
  - switch to `/tools/video-decode` upload mode in vibex
- **GitHub Actions CI** (`.github/workflows/test.yml`): ruff lint + smoke test on Python 3.11/3.12 + Docker build verify on every push and PR.
- **OSS hygiene** files: CONTRIBUTING.md, SECURITY.md, CHANGELOG.md.
- **Launch kit** in `launch/`: HN Show + X thread + LinkedIn drafts.

### Companion change
The vibex `/tools/video-decode` UI now detects 501 / 'xiaohongshu' in the error response and auto-switches the mode toggle from URL → upload, guiding the user to the workaround path in one click instead of two.

## [0.1.0] — 2026-06-10

### Initial release
- Python 3.12 + FastAPI + uvicorn
- yt-dlp 2025.6.5 (The Unlicense, public-domain equiv)
- Docker image with ffmpeg
- railway.json one-click deploy
- Bearer-token auth + constant-time comparison
- Coverage:
  - Douyin / TikTok: ✅ supported (cookie-dependent, breaks ~monthly on a_bogus signature rotation)
  - Xiaohongshu: ❌ Phase 2 stub
- Bilingual README (EN + 中文)
- MIT license
