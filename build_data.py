#!/usr/bin/env python3
"""GitHub Actions용 — data.json 생성. 3단계 신뢰도 시스템."""
import json, datetime, urllib.request, urllib.error
from pathlib import Path

CONFIG = Path(__file__).parent / "ai_price_watcher_config.json"
OUT = Path(__file__).parent / "docs" / "data.json"

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode("utf-8", errors="ignore")[:50000]
    except:
        return None

def check_free(html, words):
    h = html.lower()
    return any(w.lower() in h for w in words)

tools = json.loads(CONFIG.read_text(encoding="utf-8"))["tools"]
prev = json.loads(OUT.read_text()) if OUT.exists() else {}

result = {"updated": datetime.datetime.now().isoformat(), "tools": []}

for t in tools:
    html = fetch(t["url"])
    has_free_cfg = t.get("free_tier", False)
    note = t.get("note", "")

    if html is None:
        free_now = "unknown"
    elif check_free(html, t["check_text"]):
        free_now = "free"
    elif has_free_cfg:
        free_now = "likely_free"
    else:
        free_now = "paid"

    old = prev.get(t["name"], {}).get("free")
    changed = old and old != free_now

    result["tools"].append({
        "name": t["name"],
        "category": t["category"],
        "free": free_now,
        "changed": changed,
        "prev_free": old,
        "url": t["url"],
        "alternatives": t.get("alternatives", []),
        "note": note,
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"✅ {len(result['tools'])}개 생성 완료")
