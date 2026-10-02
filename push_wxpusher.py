#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WxPusher 微信推送（支持多人）
- 读取 data.json，把最新情报推送到你的微信（以及朋友）
- 前置步骤：
  1. https://wxpusher.zjiecode.com/ 注册 → 创建应用 → 拿 APP_TOKEN
  2. 微信扫码关注你的应用 → 在「用户管理」复制 UID（可多个，朋友扫码关注后也会出现）
  3. GitHub 仓库 Settings → Secrets and variables → Actions：
       WXPUSHER_TOKEN = APP_TOKEN
       WXPUSHER_UIDS  = UID1,UID2,UID3   ← 多个用英文逗号分隔（多人推送）
"""
import json, os, sys
from pathlib import Path
import requests

TOKEN = os.environ.get("WXPUSHER_TOKEN", "")
UIDS_RAW = os.environ.get("WXPUSHER_UIDS") or os.environ.get("WXPUSHER_UID", "")

def run():
    uids = [u.strip() for u in UIDS_RAW.split(",") if u.strip()]
    if not TOKEN or not uids:
        print("[SKIP] 缺少 WXPUSHER_TOKEN 或 WXPUSHER_UIDS")
        return
    base = Path(__file__).parent
    data = json.loads((base / "data.json").read_text(encoding="utf-8"))
    items = data["items"][:10]
    if not items:
        print("[SKIP] 无数据")
        return
    lines = [f"<b>📰 个人情报站 · {data['updated_at']} 更新</b>", ""]
    for i, it in enumerate(items, 1):
        tag = "🔴" if it.get("urgent") else "▫️"
        lines.append(f"{tag} {i}. <a href=\"{it['link']}\">{it['title']}</a>")
        ch = it.get("channel") or it.get("topic") or ""
        lines.append(f"  <small>{it['source']} · {ch} · {it['category']} · {it['fetched_at']}</small>")
        lines.append("")
    body = {
        "appToken": TOKEN,
        "content": "<br>".join(lines),
        "summary": f"情报站更新：{len(items)} 条新情报",
        "contentType": 3,
        "uids": uids,
    }
    r = requests.post("https://wxpusher.zjiecode.com/api/send/message", json=body, timeout=15)
    ok = r.json().get("code") == 1000
    print(f"[PUSH {'OK' if ok else 'FAIL'}] 发送给 {len(uids)} 人" + ("" if ok else f" {r.text[:200]}"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    run()
