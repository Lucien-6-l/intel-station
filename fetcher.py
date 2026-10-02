#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人情报站 · 多频道 RSS 抓取 v2
- 内置多分类信息源库（已实测可用），按频道归类
- 去重、按时间排序，输出 data.json（含 channel 字段）
- 用法: pip install feedparser; python3 fetcher.py
- 云端定时: GitHub Actions / cron-job.org 触发
"""
import json, hashlib, re, time, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import feedparser

try:
    import zoneinfo
    TZ = zoneinfo.ZoneInfo("Asia/Shanghai")
except Exception:
    TZ = timezone(timedelta(hours=8))

# ── 多频道信息源库（channel, name, url, weight）────────────────
SOURCE_LIBRARY = [
    # AI / 科技
    ("AI·科技", "量子位",       "https://www.qbitai.com/feed",            3),
    ("AI·科技", "IT之家",       "https://www.ithome.com/rss/",            2),
    ("AI·科技", "少数派",       "https://sspai.com/feed",                 2),
    ("AI·科技", "爱范儿",       "https://www.ifanr.com/feed",             2),
    ("AI·科技", "Solidot",      "https://www.solidot.org/index.rss",      2),
    ("AI·科技", "Hacker News",  "https://hnrss.org/frontpage",            2),
    ("AI·科技", "TechCrunch",   "https://techcrunch.com/feed/",           2),
    ("AI·科技", "The Verge",    "https://www.theverge.com/rss/index.xml", 2),
    # 教程
    ("教程",    "阮一峰周刊",   "https://www.ruanyifeng.com/blog/atom.xml", 3),
    # 游戏
    ("游戏",    "机核网",       "https://www.gcores.com/rss",             3),
    ("游戏",    "IGN",          "https://feeds.ign.com/ign/all",          2),
    # 科学
    ("科学",    "Nature",       "https://www.nature.com/nature.rss",      3),
    # 财经
    ("财经",    "雪球",         "https://xueqiu.com/hots/topic/rss",      2),
]

MAX_PER_SOURCE = 12
MAX_AGE_HOURS  = 96
OUT = Path(__file__).parent / "data.json"
URGENT_KEYWORDS = ["发布", "发布会", "开源", "融资", "launch", "release",
                   "announce", "模型", "突破", "收购", "上市"]

def classify(title, summary):
    t = (title + " " + (summary or "")).lower()
    if any(k in t for k in ["教程", "tutorial", "guide", "how to", "入门", "实践", "周刊"]):
        return "教程"
    if any(k in t for k in URGENT_KEYWORDS):
        return "发布/大事件"
    return "资讯"

def run():
    items, seen, ch_count = [], set(), {}
    now = time.time()
    for channel, name, url, weight in SOURCE_LIBRARY:
        try:
            d = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0 IntelStation/2.0"})
            entries = d.entries or []
        except Exception as e:
            print(f"[WARN] {name} 拉取失败: {e}", file=sys.stderr)
            continue
        c = 0
        for e in entries:
            if c >= MAX_PER_SOURCE:
                break
            title = (e.get("title") or "").strip()
            link = (e.get("link") or "").strip()
            if not title or not link:
                continue
            key = hashlib.md5((title.split(" ")[0] + link.split("?")[0]).encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            ts = 0
            for f in ("published_parsed", "updated_parsed"):
                if e.get(f):
                    ts = time.mktime(e[f]); break
            if ts and now - ts > MAX_AGE_HOURS * 3600:
                continue
            raw = e.get("summary") or e.get("description") or ""
            summary = re.sub(r"<[^>]+>", "", raw).strip()[:160]
            dt = datetime.fromtimestamp(ts, tz=TZ) if ts else datetime.now(tz=TZ)
            items.append({
                "id": key, "title": title, "summary": summary, "link": link,
                "source": name, "channel": channel,
                "category": classify(title, summary),
                "weight": weight,
                "urgent": any(k in title for k in URGENT_KEYWORDS),
                "fetched_at": dt.strftime("%m-%d %H:%M"),
                "ts": int(ts or now),
            })
            c += 1
        ch_count[channel] = ch_count.get(channel, 0) + c
        print(f"[OK] [{channel}] {name}: {c} 条")

    items.sort(key=lambda x: -x["ts"])
    channels = sorted({i["channel"] for i in items})
    OUT.write_text(json.dumps({
        "updated_at": datetime.now(tz=TZ).strftime("%Y-%m-%d %H:%M"),
        "total": len(items),
        "channels": channels,
        "items": items[:200],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[DONE] 共 {len(items)} 条 → {OUT}")
    print(f"[CHANNELS] {ch_count}")

if __name__ == "__main__":
    run()
