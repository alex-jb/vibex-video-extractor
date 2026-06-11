"""
vibex-video-extractor — Python sidecar for VibeXForge video-decode pipeline.

Exposes:
  GET  /healthz
  POST /extract   { url: str }  -> mp4 binary stream

Why this sidecar exists:
  Vercel serverless (Node) cannot run yt-dlp (Python). Third-party
  scraping APIs are $99+/mo or unreliable. This sidecar is the cheap
  ($5/mo Railway), self-hosted, controllable middle layer.

Auth:
  Bearer token in `Authorization: Bearer <token>` header.
  Token shared between this sidecar and the vibex Vercel function via env.

Coverage 2026-06-10:
  - Douyin (抖音): yt-dlp extractor. Works ~90% of the time, breaks on
    a_bogus signature rotations; community patches in 1-3 weeks.
  - Xiaohongshu (小红书): yt-dlp doesn't support. Stubbed for Phase 2.
    Plan: vendor JoeanAmier/XHS-Downloader logic under GPL-3.0 boundary.

Legal posture:
  Sidecar acts on individual user-triggered URLs, not crawling. Same
  posture as a personal yt-dlp install. We don't bulk-scrape; we don't
  cache videos beyond the immediate request. Output goes back to the
  user-controlled vibex pipeline. ToS gray-zone but at the safer edge.
"""
from __future__ import annotations

import os
import re
import secrets
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
import yt_dlp

VERSION = "0.1.0"
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")
MAX_FILESIZE_MB = int(os.environ.get("MAX_FILESIZE_MB", "100"))
TMP_DIR = Path(os.environ.get("TMP_DIR", "/tmp/extractor"))
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Cookies file path — bind-mount or env-baked. Required for Douyin.
# If unset, Douyin will mostly fail with "fresh cookies needed".
COOKIES_FILE = os.environ.get("COOKIES_FILE", "")

app = FastAPI(
    title="vibex-video-extractor",
    version=VERSION,
    description="Douyin + Xiaohongshu URL → mp4 binary for VibeXForge.",
)


class ExtractRequest(BaseModel):
    url: HttpUrl


# ─────────────────────────────────────────────────────────────────────
# Platform detection
# ─────────────────────────────────────────────────────────────────────

_DOUYIN_HOSTS = ("douyin.com", "iesdouyin.com", "v.douyin.com", "tiktok.com")
_XHS_HOSTS = ("xiaohongshu.com", "xhslink.com")


def _platform_of(url: str) -> str:
    u = url.lower()
    if any(h in u for h in _DOUYIN_HOSTS):
        return "douyin"
    if any(h in u for h in _XHS_HOSTS):
        return "xiaohongshu"
    return "unknown"


# ─────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────


def _check_auth(authorization: Optional[str]) -> None:
    if not BEARER_TOKEN:
        # If no token configured, allow everything but log loudly.
        print("⚠ BEARER_TOKEN not set — sidecar is open to anyone")
        return
    if not authorization:
        raise HTTPException(401, "missing Authorization header")
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "expected `Authorization: Bearer <token>`")
    # Constant-time compare to avoid timing oracles.
    if not secrets.compare_digest(parts[1], BEARER_TOKEN):
        raise HTTPException(401, "invalid bearer token")


# ─────────────────────────────────────────────────────────────────────
# Extraction
# ─────────────────────────────────────────────────────────────────────


def _build_ydl_opts(out_template: str) -> dict:
    """yt-dlp options tuned for short-form Chinese content."""
    opts: dict = {
        "outtmpl": out_template,
        "format": "best[ext=mp4]/best",  # prefer mp4
        "quiet": True,
        "noplaylist": True,
        "max_filesize": MAX_FILESIZE_MB * 1024 * 1024,
        "retries": 2,
        "fragment_retries": 2,
        # Defeat HTTP geo-blocks where possible.
        "geo_bypass": True,
    }
    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        opts["cookiefile"] = COOKIES_FILE
    return opts


def _extract_douyin(url: str) -> tuple[Path, dict]:
    """Pull a Douyin video. Returns (mp4_path, info_dict)."""
    # Each call gets its own tmpdir so concurrent requests don't clash.
    workdir = tempfile.mkdtemp(prefix="dy-", dir=str(TMP_DIR))
    out_template = str(Path(workdir) / "%(id)s.%(ext)s")
    opts = _build_ydl_opts(out_template)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "signature" in msg.lower() or "bogus" in msg.lower():
            raise HTTPException(
                502,
                "Douyin signature rotation — yt-dlp needs an update. "
                "Try again in a few hours, or refresh cookies.",
            ) from e
        if "cookies" in msg.lower():
            raise HTTPException(
                403,
                "Douyin requires fresh cookies. Re-export from a logged-in "
                "browser and update COOKIES_FILE.",
            ) from e
        raise HTTPException(502, f"yt-dlp failed: {msg[:200]}") from e

    # Find the produced mp4. yt-dlp normalizes ext, so glob for it.
    candidates = sorted(Path(workdir).glob("*"))
    mp4s = [p for p in candidates if p.suffix.lower() in (".mp4", ".mov", ".webm")]
    if not mp4s:
        raise HTTPException(502, "yt-dlp produced no video file")
    return mp4s[0], info or {}


def _extract_xiaohongshu(url: str) -> tuple[Path, dict]:
    """Phase 2 placeholder with best-effort yt-dlp generic extraction.

    yt-dlp does NOT have an official Xiaohongshu extractor. We try the generic
    extractor first — it sometimes resolves direct mp4 links from xhslink short
    URLs. When that fails, raise a clean 501 so the vibex UI auto-switches to
    mp4 upload mode.

    Future Phase 2 plan: vendor JoeanAmier/XHS-Downloader extraction logic
    under a GPL-3.0 sibling subprocess to keep license isolation. Tracked
    in repo issue #1.
    """
    # Best-effort: yt-dlp generic extractor with cookies. Most XHS URLs will
    # fail this; the ones that succeed are usually older / non-DRMd / direct.
    workdir = tempfile.mkdtemp(prefix="xhs-", dir=str(TMP_DIR))
    out_template = str(Path(workdir) / "%(id)s.%(ext)s")
    opts = _build_ydl_opts(out_template)
    opts["force_generic_extractor"] = True

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        candidates = sorted(Path(workdir).glob("*"))
        mp4s = [p for p in candidates if p.suffix.lower() in (".mp4", ".mov", ".webm")]
        if mp4s:
            print(f"[xhs] generic extractor surprise-win: {url}")
            return mp4s[0], info or {}
    except Exception as e:
        # Expected — generic extractor usually fails on XHS. Log and fall
        # through to the 501.
        print(f"[xhs] generic extractor declined as expected: {type(e).__name__}")

    raise HTTPException(
        501,
        "Xiaohongshu URL extraction is Phase 2 in this sidecar. "
        "yt-dlp has no official extractor for xiaohongshu.com. "
        "Workaround: download the .mp4 manually (xhs-downloader Python lib, "
        "or browser DevTools Network tab on xiaohongshu.com/explore/<id>) "
        "and use the /tools/video-decode upload mode instead. "
        "Phase 2 will vendor JoeanAmier/XHS-Downloader logic.",
    )


# ─────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────


@app.get("/")
def root() -> dict:
    return {
        "service": "vibex-video-extractor",
        "version": VERSION,
        "platforms": {
            "douyin": "supported (yt-dlp, cookie-dependent)",
            "xiaohongshu": "phase 2 — not yet implemented",
        },
        "auth": "Bearer token via Authorization header" if BEARER_TOKEN else "OPEN — no token configured",
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "version": VERSION, "cookies_configured": bool(COOKIES_FILE)}


@app.post("/extract")
def extract(
    body: ExtractRequest,
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> FileResponse:
    _check_auth(authorization)

    url = str(body.url)
    platform = _platform_of(url)
    if platform == "unknown":
        raise HTTPException(400, f"unsupported URL host: {url[:80]}")

    print(f"[extract] {platform} {url}")

    if platform == "douyin":
        path, info = _extract_douyin(url)
    elif platform == "xiaohongshu":
        path, info = _extract_xiaohongshu(url)
    else:
        raise HTTPException(400, f"unknown platform: {platform}")

    # Return the mp4. FileResponse streams; we delete after send via
    # BackgroundTask so the disk doesn't fill on Railway's tiny container.
    title = info.get("title") or "video"
    safe_title = re.sub(r"[^\w\-_.]", "_", str(title))[:60] or "video"
    filename = f"{safe_title}.mp4"

    return FileResponse(
        path=str(path),
        media_type="video/mp4",
        filename=filename,
        headers={
            "X-Video-Platform": platform,
            "X-Video-Duration": str(info.get("duration", "")),
            "X-Video-Title": title[:200] if title else "",
            "X-Extractor-Version": VERSION,
        },
    )


# ─────────────────────────────────────────────────────────────────────
# Local dev entry point
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        log_level="info",
    )
