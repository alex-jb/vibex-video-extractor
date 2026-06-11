# vibex-video-extractor

> [English](README.md) | **中文**

**VibeXForge 的 Python sidecar — 粘一个抖音链接,返回原始 .mp4。**

跑在 [vibex](https://github.com/alex-jb/vibex) 的 `/api/video-decode` endpoint 后面。Vercel serverless 跑不了 yt-dlp,所以我们把它塞进 256MB 的 Railway 容器里,$5/月。

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/alex-jb/vibex-video-extractor)

---

## 干什么的

```
POST /extract                 Authorization: Bearer <token>
{ "url": "https://v.douyin.com/iJSxxxxxx/" }
                                      ↓
                                返回 mp4 二进制
```

从抖音拉底层 mp4。Vibex 网站拿到 mp4 之后,转给 Gemini 2.5 Flash 做 hook + 节奏 + CTA + 仿写脚本拆解。

## 覆盖范围 2026-06

| 平台 | 状态 | 底层 |
|---|---|---|
| 抖音 (Douyin) | ✅ 支持 | yt-dlp extractor — 依赖 cookie,大概每月坏一次 (a_bogus 签名轮换) |
| TikTok | ✅ 支持 | 同 yt-dlp extractor |
| 小红书 (Xiaohongshu) | ❌ Phase 2 | yt-dlp 没 extractor。计划:vendor [JoeanAmier/XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader) 逻辑,作为 GPL-3.0 独立子进程 |

## Railway 5 分钟部署

```bash
# 1. Fork / clone 这个 repo
git clone https://github.com/alex-jb/vibex-video-extractor
cd vibex-video-extractor

# 2. 生成共享密钥
openssl rand -base64 32
# → 把它粘到 Railway → Variables → BEARER_TOKEN

# 3. 上 https://railway.com/new → 选这个 repo → 点 Deploy
#    Railway 会自动读 Dockerfile + railway.json

# 4. 部署后,在 Railway 设环境变量:
#    BEARER_TOKEN=<第 2 步的密钥>
#    MAX_FILESIZE_MB=100   (默认;Railway 付费 plan 可以调大)

# 5. (抖音强烈推荐) 上传 cookies.txt
#    - 在登录的 Chrome 装 "Get cookies.txt LOCALLY" 扩展
#    - 把 douyin.com 的 cookies 导成 cookies.txt
#    - Railway → Volumes → 挂载到 /app/cookies.txt
#    - 设 COOKIES_FILE=/app/cookies.txt

# 6. 烟测
curl https://<你的应用>.up.railway.app/healthz
# {"ok": true, "version": "0.1.0", "cookies_configured": true}
```

然后在 [vibex](https://github.com/alex-jb/vibex) 的 `.env.local` 和 Vercel env 加:

```bash
VIDEO_EXTRACTOR_URL=https://<你的应用>.up.railway.app
VIDEO_EXTRACTOR_TOKEN=<同一个密钥>
```

## 本地开发

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

## Cookie 是真实的 ops 成本

抖音会检查登录指纹。没 cookie 你会一直看到 "fresh cookies needed" 错误。诚实的 workflow:

1. 用常规 Chrome profile 登一次 douyin.com
2. 装 [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/cclelndahbckbenkjhflpdbgdldlbecc) 扩展导出 cookies
3. 存成 `cookies.txt`,通过 Railway → Volumes 上传
4. 每月大概重导一次 (抖音 session 失效)

每月 10 分钟 ops。比 $99 RapidAPI 便宜。

## 法律姿态

这个 sidecar 处理的是用户单次主动触发的 URL。它**不爬虫**、**不批量抓取**、**不缓存视频**。这个姿态跟你在自己 laptop 上装 yt-dlp 一样。我们不保证 ToS 合规 — 抖音用户协议第 8.2 条明令禁止"自动化访问",你自己部署你自己承担。

**推荐用途:** indie / 研究 / 个人规模。**不推荐:** 大规模 B2B SaaS 对中国平台 (平台法务会注意到)。

## 为什么不用 Vercel?

- Vercel serverless 默认不带 Python runtime
- yt-dlp + ffmpeg 加起来 ~80MB → 超过 Vercel 50MB-zipped function 限制
- yt-dlp 需要可写的 `/tmp` + spawn 语义,serverless 适配不好

Railway / Render / Fly = $5/月,真正的 Docker,没限制。值得。

## 为什么不用 RapidAPI / TikAPI?

- $99/月起步
- 它们偶尔挂一周 — 你 0 控制
- 它们的 TOS 跟 yt-dlp 一样灰 — 你花钱替别人承担风险
- Solo indie scale 下,$5 Railway + 每月 10 分钟刷 cookie 是赢家

## Roadmap

- [x] 抖音 / TikTok (yt-dlp)
- [ ] 小红书 Phase 2 (vendor JoeanAmier/XHS-Downloader)
- [ ] Bilibili (yt-dlp 有 extractor)
- [ ] Cloudflare R2 缓存复用同 URL (~30% 成本下降)
- [ ] Prometheus `/metrics`
- [ ] 失败时 Telegram bot ping 提醒刷 cookie

## License

MIT。yt-dlp 是 The Unlicense (公有领域等价)。这是我们能找的最干净的商用栈。

## 相关

- [vibex](https://github.com/alex-jb/vibex) — 调用这个 sidecar 的 Next.js 应用
- [council-diff](https://github.com/alex-jb/council-diff) — 5 voice + Fable 5 Oracle 决策框架
- [solo-founder-os](https://github.com/alex-jb/solo-founder-os) — 11-agent 开源栈
