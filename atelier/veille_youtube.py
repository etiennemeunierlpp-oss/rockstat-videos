#!/usr/bin/env python3
"""Veille gameplay : vidéos YouTube « argent GTA 6 » de la semaine, < 3 min, triées par vues (Apify streamers/youtube-scraper, 0,004 $/vidéo).
Usage : python3 atelier/veille_youtube.py   (depuis la racine du dépôt)
- Une seule recherche Apify par jour : le résultat est gardé dans veille/youtube_<AAAA-MM-JJ>.json (la tâche de 18 h réutilise celui de 10 h).
- Écarte les vidéos déjà utilisées (veille/gameplay_utilises.txt : une ligne « <videoId> <date> <slug> »).
Affiche : vues | durée | date | id | titre | url"""
import datetime, json, os, re, sys, urllib.request
os.makedirs("veille", exist_ok=True)
day = datetime.date.today().isoformat(); cache = f"veille/youtube_{day}.json"
if os.path.exists(cache):
    items = json.load(open(cache))
else:
    tok = urllib.request.urlopen("https://drive.usercontent.google.com/download?id=1hyGTkqB1Zcjjnq2n-fJ1IeLA_e_vS1k6&export=download&confirm=t").read().decode().strip()
    body = json.dumps({"searchQueries": ["GTA 6 money", "GTA 6 money glitch"], "maxResults": 12, "maxResultsShorts": 0, "maxResultStreams": 0,
                       "dateFilter": "week", "lengthFilter": "under4", "sortingOrder": "relevance"}).encode()
    req = urllib.request.Request("https://api.apify.com/v2/acts/streamers~youtube-scraper/run-sync-get-dataset-items?timeout=280", body,
                                 {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    items = json.load(urllib.request.urlopen(req, timeout=300))
    json.dump(items, open(cache, "w"), ensure_ascii=False)
used = set(l.split()[0] for l in open("veille/gameplay_utilises.txt")) if os.path.exists("veille/gameplay_utilises.txt") else set()
def sec(d):
    p = [int(x) for x in re.findall(r"\d+", d or "0")]; s = 0
    for x in p: s = s * 60 + x
    return s
seen, rows = set(), []
for v in items:
    vid = v.get("id") or (v.get("url") or "").split("v=")[-1]
    if not vid or vid in seen or vid in used: continue
    seen.add(vid); d = sec(v.get("duration"))
    if not 30 <= d <= 180: continue
    rows.append((v.get("viewCount") or 0, d, (v.get("date") or "")[:10], vid, v.get("title"), v.get("url")))
for r in sorted(rows, reverse=True): print(f"{r[0]:>8} | {r[1]:>3}s | {r[2]} | {r[3]} | {r[4]} | {r[5]}")
