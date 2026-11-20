#!/usr/bin/env python3
"""Labo : échantillons de voix Gemini (sur la musique flower à 1:20) + pack SFX Mixkit. Sortie : ./labo_out"""
import json, os, re, sys, time, base64, subprocess, urllib.request, urllib.error, html
OUT = "labo_out"; os.makedirs(OUT + "/voix", exist_ok=True); os.makedirs(OUT + "/sfx", exist_ok=True)
MUS = "atelier/music_pack/flower.mp3"
def get(u, t=60): return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=t).read()
# clé Gemini depuis le Drive « GTA VI »/00_ATELIER
def ls(fid):
    h = get(f"https://drive.google.com/embeddedfolderview?id={fid}").decode()
    for m in re.finditer(r'<a href="([^"]+)"[^>]*>.*?<div class="flip-entry-title">([^<]*)</div>', h, re.S):
        i = re.search(r'/(?:d|folders)/([A-Za-z0-9_-]{20,})', m.group(1))
        if i: yield ("dir" if "/folders/" in m.group(1) else "file"), i.group(1), html.unescape(m.group(2))
key = None
for t, i, n in ls("1n6nLkWVVGK8pHDaZd36WOTlNESQ_tU7A"):
    if t == "dir" and n == "00_ATELIER":
        for t2, i2, n2 in ls(i):
            if n2 == "gemini_key.txt":
                key = get(f"https://drive.usercontent.google.com/download?id={i2}&export=download&confirm=t").decode().strip()
TEXT = ("Dans GTA 6, il y a une technique toute simple pour te faire 20 000 dollars en une minute. "
        "Et franchement, presque personne ne la connaît. Abonne-toi pour rien rater de GTA 6. Allez, je te montre !")
STYLE = ("Lis ce texte EXACTEMENT mot pour mot, en français, comme un pote sympa et souriant qui te file un bon plan sur TikTok : "
         "ton chaleureux, détendu et enjoué, on entend le sourire, débit dynamique mais naturel, bien articulé. Texte : ")
VOIX = [("Achird", "amical"), ("Puck", "enjoue"), ("Laomedeia", "enjoue"), ("Sadachbia", "vif"), ("Zubenelgenubi", "decontracte"),
        ("Umbriel", "posé-cool"), ("Callirrhoe", "decontracte"), ("Sulafat", "chaleureux"), ("Aoede", "leger"), ("Zephyr", "lumineux"),
        ("Fenrir", "ACTUELLE")]
def tts(voice, out):
    body = {"contents": [{"parts": [{"text": STYLE + TEXT}]}], "generationConfig": {"responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for a in range(8):
        try: r = json.load(urllib.request.urlopen(req, timeout=180)); break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and a < 7: time.sleep(20 * (a + 1))
            else: raise
    p = r["candidates"][0]["content"]["parts"][0]["inlineData"]
    rate = int(p["mimeType"].split("rate=")[1].split(";")[0]) if "rate=" in p.get("mimeType", "") else 24000
    open(out + ".pcm", "wb").write(base64.b64decode(p["data"]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", out + ".pcm", out], check=True)
    os.remove(out + ".pcm")
if key and "--sfx-only" not in sys.argv:
    for k, (v, tag) in enumerate(VOIX, 1):
        w = f"/tmp/{v}.wav"
        try: tts(v, w)
        except Exception as e: print("ECHEC", v, e); continue
        # voix + musique flower à 80 s, volume comme en prod (0,12 sous la voix)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w, "-ss", "80", "-i", MUS, "-filter_complex",
                        "[0:a]aresample=48000,apad=pad_dur=1.5[v];[1:a]volume=0.12,aresample=48000[m];[v][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1[o]",
                        "-map", "[o]", "-b:a", "160k", f"{OUT}/voix/{k:02d}_{v}_{tag}.mp3"], check=True)
        print("ok", v); time.sleep(4)
else:
    print("pas de clé Gemini" if not key else "sfx seulement")
# pack SFX Mixkit (licence Mixkit : usage libre dans les vidéos, y compris réseaux sociaux)
CATS = ["money", "whoosh", "transition", "swoosh", "impact", "glitch", "camera", "notification", "pop", "cinematic", "game",
        "coins", "cash", "boom", "riser", "click", "magic", "bass", "slot-machine", "arcade", "hit", "swipe", "typing", "phone"]
idx = []
seen = set()
for c in CATS:
    try: h = get(f"https://mixkit.co/free-sound-effects/{c}/").decode("utf-8", "ignore")
    except Exception as e: print("cat", c, e); continue
    for m in re.finditer(r'data-audio-player-preview-url-value="([^"]+)"', h):
        pass
    ids = list(dict.fromkeys(re.findall(r'active_storage/sfx/(\d+)/\1-preview\.mp3', h)))
    titles = re.findall(r'<h2 class="item-grid-card__title">\s*([^<]+?)\s*</h2>', h)
    for j, i in enumerate(ids):
        if i in seen: continue
        seen.add(i)
        t = titles[j] if j < len(titles) else ""
        f = f"{OUT}/sfx/{c}__{i}__{re.sub(r'[^a-z0-9]+', '_', t.lower()).strip('_')[:40]}.mp3"
        try: open(f, "wb").write(get(f"https://assets.mixkit.co/active_storage/sfx/{i}/{i}-preview.mp3"))
        except Exception as e: print("dl", i, e); continue
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
        idx.append({"cat": c, "id": i, "title": t, "dur": d, "file": os.path.basename(f)})
json.dump(idx, open(f"{OUT}/sfx/index.json", "w"), ensure_ascii=False, indent=1)
print("sfx", len(idx))
