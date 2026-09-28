#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WxPusher 微信推送脚本
- 读取 data.json，把最新情报汇总推送到你的微信
- 前置步骤：
  1. 打开 https://wxpusher.zjiecode.com/ → 注册 → 创建「应用」拿到 APP_TOKEN
  2. 用你的微信扫码关注该应用，得到你的 UID（在「用户管理」里看）
  3. 在 GitHub 仓库 Settings → Secrets and variables → Actions 新建两个 Secret:
       WXPUSHER_TOKEN = 你的 APP_TOKEN
       WXPUSHER_UID   = 你的 UID
"""
import json, os, sys
from pathlib import Path
import requests

TOKEN = os.environ.get("WXPUSHER_TOKEN", "")
UID   = os.environ.get("WXPUSHER_UID", "")

def run():
    if not TOKEN or not UID:
        print("[SKIP] 缺少 WXPUSHER_TOKEN / WXPUSHER_UID")
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
        lines.append(f"　　<small>{it['source']} · {it['category']} · {it['fetched_at']}</small>")
        lines.append("")
    body = {
        "appToken": TOKEN,
        "content": "<br>".join(lines),
        "summary": f"情报站更新：{len(items)} 条新情报",
        "contentType": 3,   # 3 = HTML
        "uids": [UID],
    }
    r = requests.post("https://wxpusher.zjiecode.com/api/send/message", json=body, timeout=15)
    ok = r.json().get("code") == 1000
    print("[PUSH OK]" if ok else f"[PUSH FAIL] {r.text[:200]}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    run()
