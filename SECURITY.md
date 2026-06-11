# Security policy

## Reporting a vulnerability

Email **xji1 [at] mail.yu.edu** with subject line `vibex-video-extractor security`. Include:

- The vulnerability description
- Reproduction steps (or the closest you can describe without weaponizing it)
- The Docker image tag / commit SHA / Python version where you found it
- Whether you've disclosed it elsewhere

I'll acknowledge within 72 hours and aim to patch within 7 days for high-severity issues.

## Threat model

This is a single-tenant Python sidecar designed to run in a private Railway / Render / Fly container, accessed only by a known vibex Vercel function via Bearer token. It is **not** designed for:

- Public-internet exposure without a token gate
- Multi-user or multi-tenant deployment
- Untrusted input that the operator hasn't vetted

What it does protect against:
- ✅ Bearer token comparison is constant-time (`secrets.compare_digest`) — no timing oracle
- ✅ URL validation via Pydantic `HttpUrl`
- ✅ Platform allowlist (only known Douyin / Xiaohongshu hosts accepted)
- ✅ Max filesize cap (`MAX_FILESIZE_MB`) to bound disk + memory use
- ✅ Per-request tmpdirs so concurrent calls don't cross-contaminate

What it does **not** protect against:
- ❌ A compromised Bearer token. Rotate it if you suspect leak.
- ❌ A malicious URL that triggers yt-dlp into spending CPU on a million-redirect chain (mitigation: container has a Railway-imposed CPU / memory limit; consider adding a request timeout)
- ❌ Side-channel attacks against the Bearer token via Railway's network logs

## Cookies handling

If you upload a `cookies.txt` to a Railway Volume, treat it as a secret:
- Never commit to git
- Never include in Docker image
- Rotate on schedule (~monthly when Douyin invalidates)
- Use a dedicated, low-value account, not your personal Douyin login

The cookie file is read at `COOKIES_FILE` path inside the container. We do not log, transmit, or persist cookies beyond yt-dlp's normal usage.

## Bearer token rotation

```bash
# 1. Generate new token
openssl rand -base64 32

# 2. Update Railway env var BEARER_TOKEN

# 3. Update vibex Vercel env var VIDEO_EXTRACTOR_TOKEN to match

# 4. Redeploy both (Railway auto-redeploys on env change; Vercel needs a new commit)
```

## Dependencies

`requirements.txt` pins exact versions. `dependabot` will surface CVEs in upstream. Apply patches in PRs labeled `security`.
