#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人情报站 · RSS 抓取脚本 v1
- 拉取多个真实 RSS 源，去重、按时间排序，输出 data.json
- 依赖: pip install feedparser requests
- 用法: python3 fetcher.py   （生成同目录 data.json）
- 云端定时: 在 Vercel Cron / GitHub Actions / 腾讯云函数里每 30 分钟跑一次
"""
import json, hashlib, time, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser

try:
    import zoneinfo
    TZ = zoneinfo.ZoneInfo("Asia/Shanghai")
except Exception:
    TZ = timezone(timedelta(hours=8))

# ── 信息源配置：在此添加/删除你的订阅 ─────────────────────────
SOURCES = [
    # name, url, category(分类), weight(重要性 1-3)
    ("量子位",       "https://www.qbitai.com/feed",    "AI 动态", 3),
    ("Hacker News",  "https://hnrss.org/frontpage",    "科技社区", 2),
    ("36氪",         "https://36kr.com/feed",          "创投要闻", 2),
    ("Solidot",      "https://www.solidot.org/index.rss", "科技资讯", 2),
    ("阮一峰周刊",   "https://www.ruanyifeng.com/blog/atom.xml", "教程", 3),
]

MAX_PER_SOURCE = 15          # 每个源最多保留条数
MAX_AGE_HOURS  = 72          # 只保留 72 小时内的条目
OUT = Path(__file__).parent / "data.json"

# 即时推送关键词（命中则标记 urgent，云端版可据此触发推送）
URGENT_KEYWORDS = ["发布", "发布会", "开源", "融资", "发布", "launch", "release", "announce", "模型"]

def classify(title, summary):
    t = (title + " " + (summary or "")).lower()
    if any(k in t for k in ["教程", "tutorial", "guide", "how to", "入门", "实践"]):
        return "教程"
    if any(k in t for k in URGENT_KEYWORDS):
        return "发布/大事件"
    return "资讯"

def run():
    items, seen = [], set()
    now = time.time()
    for name, url, cat, weight in SOURCES:
        try:
            d = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0 IntelStation/1.0"})
            entries = d.entries or []
        except Exception as e:
            print(f"[WARN] {name} 拉取失败: {e}", file=sys.stderr)
            continue
        count = 0
        for e in entries:
            if count >= MAX_PER_SOURCE:
                break
            title = (e.get("title") or "").strip()
            link  = (e.get("link") or "").strip()
            if not title or not link:
                continue
            key = hashlib.md5((title.split(" ")[0] + link.split("?")[0]).encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            ts = 0
            if e.get("published_parsed"):
                ts = time.mktime(e.published_parsed)
            elif e.get("updated_parsed"):
                ts = time.mktime(e.updated_parsed)
            if ts and now - ts > MAX_AGE_HOURS * 3600:
                continue
            summary = ""
            raw = e.get("summary") or e.get("description") or ""
            # 粗略去 HTML 标签
            import re
            summary = re.sub(r"<[^>]+>", "", raw).strip()[:160]
            dt = datetime.fromtimestamp(ts, tz=TZ) if ts else datetime.now(tz=TZ)
            items.append({
                "id": key,
                "title": title,
                "summary": summary,
                "link": link,
                "source": name,
                "category": classify(title, summary),
                "topic": cat,
                "weight": weight,
                "urgent": any(k in title for k in URGENT_KEYWORDS),
                "fetched_at": dt.strftime("%m-%d %H:%M"),
                "ts": int(ts or now),
            })
            count += 1
        print(f"[OK] {name}: {count} 条")
    items.sort(key=lambda x: -x["ts"])
    OUT.write_text(json.dumps({
        "updated_at": datetime.now(tz=TZ).strftime("%Y-%m-%d %H:%M"),
        "total": len(items),
        "items": items[:120],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[DONE] 共 {len(items)} 条 → {OUT}")

if __name__ == "__main__":
    run()
