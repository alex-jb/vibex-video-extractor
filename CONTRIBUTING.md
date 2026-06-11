# Contributing

Thanks for your interest. This is a small indie sidecar service — contributions welcome, kept lean.

## Quickstart

```bash
git clone https://github.com/alex-jb/vibex-video-extractor
cd vibex-video-extractor
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install ruff pytest
export BEARER_TOKEN=dev-token
python main.py
# → http://localhost:8000/healthz
```

## Before you open a PR

1. **Run ruff** — `ruff check main.py` should pass with 0 errors
2. **Build the Docker image** — `docker build -t vibex-video-extractor:dev .` should succeed
3. **Smoke test** — `curl http://localhost:8000/healthz` should return `{"ok": true}`
4. **Keep changes small and orthogonal** — single-purpose PRs land fast, sprawl PRs get bounced

## What we want

- **More platforms.** Bilibili, Weibo, and Kuaishou are all candidates. yt-dlp has Bilibili out of the box.
- **Xiaohongshu real extraction.** Vendor JoeanAmier/XHS-Downloader as a GPL-3.0 sibling subprocess. Issue #1 tracks this.
- **Cookies rotation helper.** When Douyin invalidates cookies, surface that signal (Telegram bot? Slack webhook? GitHub issue auto-file?) so the operator knows to re-export.
- **Sentry / Prometheus integration** for production monitoring.
- **R2 / S3 cache layer** for repeat-fetches of the same URL within 24h.

## What we don't want

- **Built-in user accounts / auth UI.** Sidecar is single-tenant by design. Bearer token gate is enough.
- **Multi-tenancy or per-user rate limiting.** That belongs in the vibex-side API.
- **Heavy dependencies (Playwright, headless Chrome).** Sidecar runs in a 256MB Railway box. If you need a real browser, run a separate service.
- **Anything that requires bulk-scraping Douyin/小红书 platforms.** That violates ToS at the volume that interests platform legal teams. Sidecar handles single user-triggered URLs only.

## Legal posture

This sidecar acts on individual user-triggered URLs. It does not crawl, batch-scrape, or cache videos beyond the immediate response. We do not warrant ToS compliance — Douyin user agreement section 8.2 explicitly prohibits automated access, and contributors assume the risk for their own deployments.

**Recommended use:** indie / research / personal-scale.
**Not recommended:** large-volume B2B SaaS over Chinese platforms.

## Code style

- Black is not required; ruff defaults are fine
- Type hints encouraged on public functions
- Keep `main.py` flat and readable — split into modules only when it exceeds ~500 lines
- Comments explain *why*, not *what*

## Reporting bugs

GitHub Issues. Include:
- yt-dlp version (`pip show yt-dlp | grep Version`)
- Docker / Python version
- The URL that failed (or a similar non-personal URL that reproduces)
- The full error response from `/extract`

## Reporting security issues

Don't open a public issue. See [SECURITY.md](SECURITY.md).
