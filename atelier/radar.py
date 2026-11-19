#!/usr/bin/env python3
"""Radar GTA VI : scan TikTok (Apify), classement vues/heure < 12 h, envoi Telegram.

Usage :
  python3 radar.py scan  [--results 10]   -> scan Apify, écrit scan.json + top.txt
  python3 radar.py rank  scan.json        -> classe un scan existant (sans coût)
  python3 radar.py send  message.txt      -> envoie un message Telegram (HTML)
  python3 radar.py chatid                 -> récupère l'identifiant de discussion Telegram

Clés lues dans .apify, .tg et .chat (même dossier que ce script).
"""
import json, os, sys, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
QUERIES = ["gta 6", "gta vi", "gta 6 news"]
MAX_AGE_H = 12


def key(name):
    with open(os.path.join(HERE, name)) as f:
        return f.read().strip()


def http(url, data=None, headers=None, timeout=300):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def scan(results_per_query=10):
    body = {
        "searchQueries": QUERIES, "searchSection": "/video",
        "videoSearchDateFilter": "PAST_24_HOURS", "resultsPerPage": results_per_query,
        "shouldDownloadVideos": False, "shouldDownloadCovers": False,
        "shouldDownloadAvatars": False, "shouldDownloadMusicCovers": False,
        "shouldDownloadSlideshowImages": False,
    }
    url = ("https://api.apify.com/v2/acts/clockworks~tiktok-scraper/"
           "run-sync-get-dataset-items?timeout=280")
    items = http(url, json.dumps(body).encode(), {
        "Authorization": "Bearer " + key(".apify"), "Content-Type": "application/json"})
    path = os.path.join(HERE, "scan.json")
    json.dump(items, open(path, "w"))
    return path


def rank(path):
    now = time.time()
    seen = {}
    for v in json.load(open(path)):
        try:
            age = (now - int(v["createTime"])) / 3600
        except (KeyError, ValueError, TypeError):
            continue
        if age > MAX_AGE_H:
            continue
        plays = v.get("playCount") or 0
        seen[v["id"]] = {
            "vph": round(plays / max(age, 0.5)), "plays": plays, "age_h": round(age, 1),
            "author": v.get("authorMeta", {}).get("name"), "lang": v.get("textLanguage"),
            "text": (v.get("text") or "")[:140].replace("\n", " "),
            "url": v.get("webVideoUrl"),
        }
    top = sorted(seen.values(), key=lambda x: -x["vph"])
    json.dump(top, open(os.path.join(HERE, "top.json"), "w"), ensure_ascii=False, indent=1)
    for x in top[:20]:
        print(f"{x['vph']:>8}/h {x['plays']:>8} {x['age_h']:>4}h {x['lang']} @{x['author']}: {x['text'][:90]}")
    return top


def send(text_path):
    text = open(text_path).read()
    data = urllib.parse.urlencode({
        "chat_id": key(".chat"), "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": "true"}).encode()
    r = http(f"https://api.telegram.org/bot{key('.tg')}/sendMessage", data)
    print("ok" if r.get("ok") else r)


def chatid():
    r = http(f"https://api.telegram.org/bot{key('.tg')}/getUpdates")
    ids = {u["message"]["chat"]["id"] for u in r.get("result", []) if "message" in u}
    if ids:
        open(os.path.join(HERE, ".chat"), "w").write(str(sorted(ids)[0]))
    print(ids or "aucun message reçu par le bot")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        n = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--results" else 10
        rank(scan(n))
    elif cmd == "rank":
        rank(sys.argv[2])
    elif cmd == "send":
        send(sys.argv[2])
    elif cmd == "chatid":
        chatid()
