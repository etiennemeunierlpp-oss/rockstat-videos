#!/usr/bin/env python3
"""Pipeline TikTok GTA VI : script JSON -> voix -> sous-titres mot à mot -> montage 9:16 -> MP4.

Usage :
  python3 make_video.py script.json out/video.mp4 [--engine gemini|piper] [--voice Puck]

Format du script (JSON) :
{
  "title_lines": ["8 CHOSES", "À SAVOIR", "AVANT JEUDI"],   # carton titre (1re ligne en rose)
  "sections": [
    {"id": "hook",     "text": "...", "clips": ["Jayson_2", "Lucia_1"]},
    {"id": "promesse", "text": "...", "clips": ["Vice City"], "title": true},
    {"id": "1",        "text": "...", "clips": ["..."]},          # id numérique => compteur n/N
    {"id": "outro",    "text": "...", "clips": ["..."]}
  ]
}
"""
import json, os, re, subprocess, sys, argparse, shutil, math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
RUSH = os.path.join(ROOT, "rush")
FONTS = os.path.join(ROOT, "fonts")
MUSIC = os.path.join(ROOT, "music", "theme.mp3")
MUSIC_START = 4.0          # la musique démarre à 4 s (demande d'Etienne)
MUSIC_VOL = 0.16
MIN_DURATION = 61.5        # > 1 min (programme de rémunération TikTok)
W, H, FPS = 1080, 1920, 30
PINK = (255, 79, 163)

os.environ.setdefault("SSL_CERT_FILE", os.path.expanduser("~/.ccr/ca-bundle.crt"))
os.environ.setdefault("REQUESTS_CA_BUNDLE", os.path.expanduser("~/.ccr/ca-bundle.crt"))


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode().strip())


# ---------------------------------------------------------------- voix
PRONONCIATION = [  # appliqué au texte lu par la voix uniquement (les sous-titres gardent l'original)
    (r"\bGTA 6\b", "GTA six"), (r"\bGTA 5\b", "GTA cinq"), (r"\bGTA VI\b", "GTA six"), (r"\bGTA V\b", "GTA cinq"),
    (r"\bPSN\b", "P.S.N."), (r"\bPS5\b", "PS cinq"), (r"\bLeonida\b", "Léonida"), (r"\bgigas\b", "gigas"),
    (r"\bDrops\b", "drops"), (r"\bGame Pass\b", "Game Pass"), (r"(\d+) H\b", r"\1 heures"),
]


def for_speech(text):
    for a, b in PRONONCIATION:
        text = re.sub(a, b, text)
    return text


def tts_gemini(text, out, voice):
    import base64, urllib.request
    key = open(os.path.join(ROOT, ".gemini_key")).read().strip()
    model = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
    style = ("Lis ce texte EXACTEMENT mot pour mot, sans rien ajouter, retirer ni reformuler, en français, d'une seule traite, "
             "comme un jeune créateur TikTok gaming qui raconte une info à son pote : énergique et naturel, débit rapide mais "
             "en articulant bien chaque mot, le MÊME ton du début à la fin, pas de pause entre les phrases. Texte : ")
    body = {"contents": [{"parts": [{"text": style + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    import time, urllib.error
    for attempt in range(8):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 7:
                wait = 15 * (attempt + 1)
                print(f"Gemini {e.code}, nouvel essai dans {wait}s"); time.sleep(wait)
            else:
                raise
    part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
    rate = 24000
    if "rate=" in part.get("mimeType", ""):
        rate = int(part["mimeType"].split("rate=")[1].split(";")[0])
    open(out + ".pcm", "wb").write(base64.b64decode(part["data"]))
    run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", out + ".pcm", out])
    os.remove(out + ".pcm")


def tts_piper(text, out, voice):
    model = os.path.join(ROOT, "piper", f"{voice}.onnx")
    subprocess.run([sys.executable, "-m", "piper", "-m", model, "--length-scale", "0.78", "-f", out],
                   input=text.encode(), check=True, capture_output=True)


def _norm(w):
    import unicodedata
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


_WHISPER = None


def _whisper():
    global _WHISPER
    if _WHISPER is None:
        from faster_whisper import WhisperModel
        _WHISPER = WhisperModel("small", device="cpu", compute_type="int8")
    return _WHISPER


def take_score(wav, text):
    """part des mots du script (hors nombres) retrouvés dans la transcription -> détecte les mots mal dits ou reformulés"""
    import numpy as np, difflib
    pcm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", wav, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"])
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    segs, _ = _whisper().transcribe(audio, language="fr", beam_size=5)
    heard = [_norm(w) for w in " ".join(sg.text for sg in segs).replace("'", " ").split()]
    ref = [_norm(w) for w in text.replace("'", " ").split()]
    ref = [w for w in ref if w and not w.isdigit() and w not in ("vi", "v")]
    heard = [w for w in heard if w and not w.isdigit() and w not in ("vi", "v")]
    sm = difflib.SequenceMatcher(None, ref, heard, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / max(len(ref), 1)


def make_voice(sections, work, engine, voice):
    """Voix en UNE seule prise (ton constant), puis découpage par alignement Whisper.
    Retourne (wav, [(start,end)] par section, mots [{w,start,sec}])."""
    full = " ".join(s["text"].strip() for s in sections)
    raw = os.path.join(work, "tts_full_raw.wav")
    if not os.path.exists(raw):
        best, best_score = None, -1
        for take in range(4):
            cand = os.path.join(work, f"tts_take{take}.wav")
            (tts_gemini if engine == "gemini" else tts_piper)(for_speech(full), cand, voice)
            score = take_score(cand, full)
            print(f"prise {take + 1} : fidélité {score:.0%}")
            if score > best_score:
                best, best_score = cand, score
            if score >= 0.985 or engine != "gemini":
                break
        shutil.copy(best, raw)
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse")
    if engine == "piper":
        af += ",atempo=1.08"
    af += ",loudnorm=I=-14:TP=-1.5:LRA=11"
    voice_wav = os.path.join(work, "voice.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "1", voice_wav])

    # alignement mot à mot
    import numpy as np, difflib
    model = _whisper()
    pcm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", voice_wav, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"])
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    segs, _ = model.transcribe(audio, language="fr", word_timestamps=True, beam_size=5)
    heard = []
    for sg in segs:
        for w in sg.words:
            t = w.word.strip()
            if heard and (t[:1] in "'’-" or heard[-1][0][-1:] in "'’"):  # l + 'as -> l'as
                heard[-1] = (heard[-1][0] + t, heard[-1][1], w.end)
            else:
                heard.append((t, w.start, w.end))
    script = []
    for s in sections:
        for w in s["text"].split():
            script.append({"w": w, "sec": s["id"]})
    A = [_norm(x["w"]) for x in script]
    B = [_norm(h[0]) for h in heard]
    times = [None] * len(script)
    matched = 0
    for blk in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = heard[blk.b + k][1]; matched += 1
    # interpolation des mots non retrouvés
    total = dur(voice_wav)
    known = [(i, t) for i, t in enumerate(times) if t is not None] or [(0, 0.0)]
    known = [(-1, 0.0)] + known + [(len(script), total)]
    for (i0, t0), (i1, t1) in zip(known, known[1:]):
        for i in range(i0 + 1, i1):
            times[i] = t0 + (t1 - t0) * (i - i0) / (i1 - i0)
    for i in range(1, len(times)):  # monotone
        times[i] = max(times[i], times[i - 1])
    for x, t in zip(script, times):
        x["start"] = t
    for i, x in enumerate(script):
        x["end"] = script[i + 1]["start"] if i + 1 < len(script) else total + 0.3
    bounds = []
    for s in sections:
        ws = [x for x in script if x["sec"] == s["id"]]
        bounds.append((ws[0]["start"], ws[-1]["end"]))
    bounds = [(float(a), float(bounds[i + 1][0]) if i + 1 < len(bounds) else float(total)) for i, (a, b) in enumerate(bounds)]
    bounds[0] = (0.0, bounds[0][1])
    for x in script:
        x["start"] = float(x["start"]); x["end"] = float(x["end"])
    print(f"alignement : {matched}/{len(script)} mots retrouvés")
    return voice_wav, bounds, script


# ---------------------------------------------------------------- sous-titres
def align_words(voice_wav, sections, bounds):
    """Timestamps mot à mot via faster-whisper, texte remplacé par celui du script (orthographe exacte)."""
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    words = []
    for s, (a, b) in zip(sections, bounds):
        # transcrit chaque section isolément -> alignement robuste
        seg_wav = voice_wav + f".{s['id']}.wav"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", voice_wav, seg_wav])
        import numpy as np
        pcm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", seg_wav, "-f", "s16le", "-ac", "1",
                                       "-ar", "16000", "-"])
        audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
        segs, _ = model.transcribe(audio, language="fr", word_timestamps=True, initial_prompt=s["text"],
                                   vad_filter=False, beam_size=5)
        heard = [(w.start + a, w.end + a) for sg in segs for w in sg.words]
        os.remove(seg_wav)
        script_words = s["text"].split()
        n, m = len(script_words), max(len(heard), 1)
        # projection proportionnelle des mots du script sur les timings entendus
        for i, w in enumerate(script_words):
            if heard:
                j = min(int(i * m / n), m - 1)
                st = heard[j][0]
            else:
                st = a + (b - a) * i / n
            words.append({"w": w, "start": st, "sec": s["id"]})
    # fin de chaque mot = début du suivant
    for i, w in enumerate(words):
        w["end"] = words[i + 1]["start"] if i + 1 < len(words) else bounds[-1][1] + 0.3
    return words


def group_words(words):
    """Paquets de 1-2 mots (style ADR), coupe sur la ponctuation et au-delà de 14 caractères."""
    # garde "GTA 6", "GTA 5" ensemble
    merged = []
    for w in words:
        if merged and merged[-1]["w"].upper() == "GTA" and re.match(r"^\d", w["w"]):
            merged[-1] = dict(merged[-1], w="GTA " + w["w"], end=w["end"])
        else:
            merged.append(w)
    words = merged
    groups, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        punct = re.search(r"[,.!?:;]$", w["w"])
        if len(cur) >= 2 or punct or len(txt) >= 11:
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    out = []
    for g in groups:
        text = " ".join(x["w"] for x in g)
        text = re.sub(r"[,.!?:;]+$", "", text).upper()
        out.append({"text": text, "start": g[0]["start"], "end": g[-1]["end"]})
    return out


def ass_time(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(groups, path, title=None):
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat ExtraBold,108,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,1,0,0,100,100,0,0,1,7,3,5,40,40,0,1
Style: Title,Montserrat Black,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,8,4,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for g in groups:
        if title and title["start"] - 0.01 <= g["start"] < title["end"]:
            continue  # pendant le carton titre, le titre remplace les sous-titres
        pop = r"{\pos(540,1190)\fscx75\fscy75\t(0,90,\fscx100\fscy100)}"
        txt = g["text"]
        txt = re.sub(r"(\d+)", r"{\\c&HA34FFF&}\1{\\c&HFFFFFF&}", txt)  # chiffres en rose
        lines.append(f"Dialogue: 1,{ass_time(g['start'])},{ass_time(g['end'])},Sub,,0,0,0,,{pop}{txt}")
    if title:
        y = 760
        for i, l in enumerate(title["lines"]):
            col = r"\c&HA34FFF&" if i == 0 else r"\c&HFFFFFF&"
            size = 170 if i == 0 else 120
            delay = i * 180
            eff = (rf"{{\pos(540,{y})\fs{size}{col}\alpha&HFF&\fscx60\fscy60"
                   rf"\t({delay},{delay + 160},\alpha&H00&\fscx100\fscy100)}}")
            lines.append(f"Dialogue: 2,{ass_time(title['start'])},{ass_time(title['end'])},Title,,0,0,0,,{eff}{l}")
            y += 175 if i == 0 else 140
    open(path, "w", encoding="utf-8").write(hdr + "\n".join(lines) + "\n")


# ---------------------------------------------------------------- compteur n/N
def make_badges(n_items, work):
    paths = []
    f_big = ImageFont.truetype(os.path.join(FONTS, "Montserrat-Black.ttf"), 64)
    f_small = ImageFont.truetype(os.path.join(FONTS, "Montserrat-Black.ttf"), 34)
    S = 220
    for k in range(1, n_items + 1):
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse((14, 14, S - 14, S - 14), fill=(15, 10, 30, 190))
        d.arc((14, 14, S - 14, S - 14), 0, 360, fill=(80, 200, 255, 120), width=8)
        d.arc((14, 14, S - 14, S - 14), -90, -90 + 360 * k / n_items, fill=PINK + (255,), width=12)
        num, tot = str(k), f"/{n_items}"
        wn = d.textlength(num, font=f_big); wt = d.textlength(tot, font=f_small)
        x = (S - wn - wt) / 2
        d.text((x, S / 2), num, font=f_big, fill=PINK + (255,), anchor="lm")
        d.text((x + wn + 2, S / 2 + 10), tot, font=f_small, fill=(255, 255, 255, 255), anchor="lm")
        p = os.path.join(work, f"badge_{k}.png"); im.save(p); paths.append(p)
    return paths


# ---------------------------------------------------------------- images
RUSH_DIRS = [os.path.join(ROOT, "rush_tv"), RUSH]   # plans verticaux natifs en priorité
EXCLUDE = {"launch trailer", "launch trailer_1"}


def all_clips():
    out = []
    for d in RUSH_DIRS:
        for f in sorted(os.listdir(d)):
            n = os.path.splitext(f)[0]
            gp = n.startswith("gp_")
            # GP_ONLY=1 (format gameplay, Etienne 23/11) : uniquement les plans gp_ ; sinon jamais de gp_ en bouche-trou
            if f.endswith(".mp4") and n.lower() not in EXCLUDE and (gp if os.environ.get("GP_ONLY") else not gp):
                out.append(n)
    return out


def find_clip(name):
    for d in RUSH_DIRS:
        for f in os.listdir(d):
            if os.path.splitext(f)[0].lower() == name.lower():
                return os.path.join(d, f)
    raise FileNotFoundError(name)


def build_visuals(sections, bounds, work, total):
    pieces, idx = [], 0
    used = set()
    idx_path = os.path.join(ROOT, "rush_index.json")
    dark = {c["name"] for c in json.load(open(idx_path)) if "sombre" in c["tags"]} if os.path.exists(idx_path) else set()
    pool = [c for c in all_clips() if c not in dark]
    for si, (s, (a, b)) in enumerate(zip(sections, bounds)):
        end = bounds[si + 1][0] if si + 1 < len(bounds) else total
        need, ci = end - a, 0
        clips = s["clips"]
        while need > 0.05:
            if ci < len(clips):
                name = clips[ci]
            else:  # plus de plans prévus : on pioche un plan pas encore utilisé
                spare = [c for c in pool if c not in used]
                name = spare[0] if spare else clips[ci % len(clips)]
            used.add(name)
            fit = name.endswith("|fit")      # plan affiché en entier sur fond flouté (logos, textes)
            base = name.split("|")[0]
            offset = float(base.split("@")[1]) if "@" in base else 0.0   # "Car_2@2.0" = entrer à 2 s
            src = find_clip(base.split("@")[0])
            cd = dur(src) - offset
            # un plan dure au plus 2,2 s pour garder un rythme TikTok
            take = min(cd - 0.05, 2.2, need) if need - min(cd, 2.2) > 0.4 else need
            take = max(min(take, need), 0.3)
            ss = offset  # si on réutilise un plan, on décale le point d'entrée
            out = os.path.join(work, f"v_{idx:03d}.mp4")
            vf = (f"scale=-2:{H}:flags=lanczos,crop={W}:{H},"
                  f"zoompan=z='min(1+0.0018*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
                  "eq=saturation=1.12:contrast=1.04,setsar=1")
            if fit:
                vf = (f"split[a][b];[a]scale=-2:{H},crop={W}:{H},boxblur=30:2,eq=brightness=-0.12[bg];"
                      f"[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={FPS}")
            if cd < take:  # plan trop court : on fige la dernière image
                vf = f"tpad=stop_mode=clone:stop_duration={take - cd + 0.1}," + vf
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-i", src, "-t", f"{take:.3f}", "-an",
                 "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                 "-pix_fmt", "yuv420p", out])
            pieces.append(out); idx += 1; need -= dur(out); ci += 1
    lst = os.path.join(work, "video_list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in pieces))
    v = os.path.join(work, "video.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", v])
    return v


# ---------------------------------------------------------------- rendu Remotion
REMOTION = os.path.join(ROOT, "remotion")


def plan_shots(sections, bounds, total):
    """Même logique de choix des plans que build_visuals, sans encoder : retourne la liste pour Remotion."""
    idx_path = os.path.join(ROOT, "rush_index.json")
    meta = {c["name"].lower(): c for c in json.load(open(idx_path))} if os.path.exists(idx_path) else {}
    bad = {n for n, c in meta.items() if {"sombre", "detail"} & set(c["tags"])}
    pool = [c for c in all_clips() if c.lower() not in bad]
    pool.sort(key=lambda n: -(meta.get(n.lower(), {}).get("coverage", 0)))  # plans avec personnages d'abord
    used, shots, t = set(), [], 0.0
    reserved = {c.split("|")[0].split("@")[0] for s in sections for c in s["clips"]}  # plans prévus ailleurs
    for si, (s, (a, b)) in enumerate(zip(sections, bounds)):
        end = bounds[si + 1][0] if si + 1 < len(bounds) else total
        need, ci, clips = end - a, 0, s["clips"]
        while need > 0.05:
            if ci < len(clips):
                name = clips[ci]
            else:
                spare = [c for c in pool if c not in used and c not in reserved]
                name = spare[0] if spare else clips[ci % len(clips)]
            used.add(name.split("|")[0].split("@")[0])
            fit = name.endswith("|fit")
            base = name.split("|")[0]
            m = meta.get(base.split("@")[0].lower(), {})
            # point d'entrée : celui du script, sinon le 1er instant où un personnage est visible
            offset = float(base.split("@")[1]) if "@" in base else float(m.get("start_ok", 0) or 0)
            src = find_clip(base.split("@")[0])
            if dur(src) - offset < 0.6:
                offset = 0.0
            cd = dur(src) - offset
            take = min(cd - 0.05, 2.2, need) if need - min(cd, 2.2) > 0.4 else need
            take = max(min(take, need, cd - 0.03), 0.3)
            rel = os.path.relpath(src, ROOT)
            # cadrage 9:16 centré sur les personnages (rushes 16:9)
            pos = 50.0
            if m.get("format") == "horizontal" and not fit:
                vis = (1080 / 1920) / (16 / 9)          # part visible de la largeur (~0,32)
                fx_ = float(m.get("focus_x", 0.5))
                if m.get("spread", 0) > 0.6 and m.get("coverage", 0) > 0.5:
                    fit = True                           # personnages trop écartés : plan entier sur fond flouté
                else:
                    pos = max(0.0, min(100.0, (fx_ - vis / 2) / (1 - vis) * 100))
            shots.append({"src": rel, "start": t, "dur": take, "startFrom": offset, "fit": fit, "pos": round(pos, 1),
                          "cut": "section" if ci == 0 else "hard"})
            t += take; need -= take; ci += 1
    return shots


TRANSITIONS = ["whip", "zoomblur", "glitch", "swipeup", "spin"]
FX_SFX = {"label": [("sfx/pop.wav", 0.5, 0)], "sticker": [("sfx/swish.wav", 0.3, -3), ("sfx/pop.wav", 0.55, 2)],
          "big": [("sfx/whoosh.wav", 0.35, -6), ("sfx/soft_boom.wav", 0.5, 0)],
          "counter": [("sfx/bloop.wav", 0.4, 0)], "clock": [("sfx/bloop.wav", 0.4, 0)],
          "bars": [("sfx/rise_blip.wav", 0.4, 4), ("sfx/rise_blip.wav", 0.4, 9)],
          "stars": [("sfx/sparkle.wav", 0.45, 0)], "source": [("sfx/pop.wav", 0.45, 0), ("sfx/ding.wav", 0.3, 4)],
          "alert": [("sfx/notif.wav", 0.55, 0)], "emoji": [("sfx/pop.wav", 0.5, 0), ("sfx/pop.wav", 0.5, 6)],
          "logo": [("sfx/soft_boom.wav", 0.45, 0)],
          "subscribe": [("sfx/pop.wav", 0.5, 0), ("sfx/tick.wav", 0.5, 18), ("sfx/ding.wav", 0.4, 20)], "image": [("sfx/card_in.wav", 0.5, 0)]}


def render_remotion(cfg, sections, bounds, groups, voice_wav, total, out, work, words=None):
    import shutil
    fps = FPS
    F = lambda x: int(round(x * fps))
    pub = os.path.join(REMOTION, "public")
    os.makedirs(pub, exist_ok=True)
    for d in ["rush", "rush_tv", "fonts", "music", "sfx", "logos", "gallery"]:
        link = os.path.join(pub, d)
        if os.path.isdir(os.path.join(ROOT, d)) and not os.path.exists(link):
            os.symlink(os.path.join(ROOT, d), link)
    vname = f"voice_{os.path.basename(work)}.wav"
    shutil.copy(voice_wav, os.path.join(pub, vname))
    shots = plan_shots(sections, bounds, total)
    S, sec_i = [], -1
    for s in shots:
        if s["cut"] == "section":
            sec_i += 1
        S.append({"src": s["src"], "from": F(s["start"]), "dur": max(F(s["start"] + s["dur"]) - F(s["start"]), 1),
                  "startFrom": F(s["startFrom"]), "fit": s["fit"], "cut": s["cut"], "pos": s.get("pos", 50),
                  "trans": ("zoomin" if sec_i == 0 else TRANSITIONS[sec_i % len(TRANSITIONS)]) if s["cut"] == "section" else None})
    S[-1]["dur"] = F(total) - S[-1]["from"]
    items = [(s, bd) for s, bd in zip(sections, bounds) if s["id"].isdigit()]
    I, cards = [], []
    for k, (s, (a, b)) in enumerate(items):
        I.append({"n": k + 1, "total": len(items), "start": F(a), "end": F(b)})
        if s.get("layout") == "card":
            cards.append({"start": F(a), "end": F(b), "header": s.get("header"), "n": k + 1, "total": len(items)})
    title = None
    for s, (a, b) in zip(sections, bounds):
        if s.get("title"):
            title = {"start": F(a), "end": F(b), "lines": cfg["title_lines"]}
    G = [{"text": g["text"], "start": F(g["start"]), "end": F(g["end"])} for g in groups
         if not (title and title["start"] - 1 <= F(g["start"]) < title["end"])]
    # incrustations : "word" (mot déclencheur) ou "at" (secondes depuis le début de la partie)
    FX = []
    for s, (a, b) in zip(sections, bounds):
        sw = [w for w in (words or []) if w["sec"] == s["id"]]
        for fx in s.get("fx", []):
            t = a + float(fx.get("at", 0.25))
            if fx.get("word") and sw:
                key = _norm(fx["word"])
                hit = next((w for w in sw if key and key in _norm(w["w"])), None)
                if hit:
                    t = hit["start"]
            d = float(fx.get("dur", 1.8))
            if t + d > b:                      # ne jamais déborder sur la partie suivante
                t = max(a, b - d)
                d = min(d, b - t)
            item = {k: v for k, v in fx.items() if k not in ("at", "word", "dur")}
            item.update({"start": F(t), "dur": max(F(min(d, total - t)), 6)})
            FX.append(item)
    sfx = [{"src": "sfx/intro_whoosh.wav", "frame": 0, "volume": 0.7}]       # ouverture : whoosh + zoom
    card_starts = {c["start"] for c in cards}
    for s in S[1:]:
        if s["cut"] == "section":
            if s["from"] in card_starts or any(abs(s["from"] - c) <= 2 for c in card_starts):
                sfx.append({"src": "sfx/card_in.wav", "frame": s["from"] - 6, "volume": 0.5})
            else:
                sfx.append({"src": "sfx/whoosh.wav", "frame": s["from"] - 8, "volume": 0.45})
        else:
            sfx.append({"src": "sfx/swish.wav", "frame": s["from"] - 3, "volume": 0.12})
    for it in I:
        if not any(c["start"] <= it["start"] < c["end"] for c in cards):
            sfx.append({"src": "sfx/bloop.wav", "frame": it["start"] + 3, "volume": 0.4})
    for x in FX:
        for src, vol, dl in FX_SFX.get(x["type"], []):
            sfx.append({"src": src, "frame": x["start"] + dl, "volume": vol})
        if x["type"] in ("counter", "clock"):
            for k in range(3, 24, 3):
                sfx.append({"src": "sfx/tick.wav", "frame": x["start"] + k, "volume": 0.22})
            sfx.append({"src": "sfx/ding.wav", "frame": x["start"] + 24, "volume": 0.3})
    if title:
        sfx.append({"src": "sfx/riser.wav", "frame": title["start"] - 30, "volume": 0.3})
        sfx.append({"src": "sfx/soft_boom.wav", "frame": title["start"], "volume": 0.55})
    props = {"fps": fps, "durationInFrames": F(total), "shots": S, "groups": G, "items": I, "sfx": sfx,
             "fx": FX, "cards": cards, "title": title, "voice": vname, "music": "music/theme.mp3",
             "musicStartFrom": F(MUSIC_START), "musicVolume": MUSIC_VOL, "duck": [[F(a), F(b)] for a, b in bounds],
             "logo": cfg.get("logo"), "handle": cfg.get("handle", "@rockstat433")}
    pp = os.path.join(work, "props.json")
    json.dump(props, open(pp, "w"), ensure_ascii=False)
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    cmd = ["npx", "remotion", "render", "src/index.ts", "GtaVideo", os.path.abspath(out), f"--props={pp}",
           "--concurrency=2", "--crf=20", "--log=error", "--offthreadvideo-cache-size-in-bytes=400000000"]
    if chrome:
        cmd.append(f"--browser-executable={chrome}")
    if os.environ.get("PROPS_ONLY"):
        print("props:", pp); return
    subprocess.run(cmd, cwd=REMOTION, check=True)


# ---------------------------------------------------------------- assemblage
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script"); ap.add_argument("out")
    ap.add_argument("--engine", default="gemini"); ap.add_argument("--voice", default="Puck")
    ap.add_argument("--renderer", default="remotion", choices=["remotion", "ffmpeg"])
    args = ap.parse_args()
    cfg = json.load(open(args.script))
    sections = cfg["sections"]
    work = os.path.join(ROOT, "work", os.path.splitext(os.path.basename(args.out))[0])
    os.makedirs(work, exist_ok=True)

    voice_wav, bounds, words = make_voice(sections, work, args.engine, args.voice)
    vdur = dur(voice_wav)
    total = max(vdur + 0.6, MIN_DURATION)
    print(f"voix {vdur:.1f}s -> vidéo {total:.1f}s")

    groups = group_words(words)
    title = None
    for s, (a, b) in zip(sections, bounds):
        if s.get("title"):
            title = {"start": a, "end": b + 0.06, "lines": cfg["title_lines"]}
    if args.renderer == "remotion":
        render_remotion(cfg, sections, bounds, groups, voice_wav, total, args.out, work, words)
        if not os.environ.get("PROPS_ONLY"):
            print("OK", args.out, f"{dur(args.out):.1f}s")
        return
    ass = os.path.join(work, "subs.ass")
    write_ass(groups, ass, title)

    items = [(s, bd) for s, bd in zip(sections, bounds) if s["id"].isdigit()]
    badges = make_badges(len(items), work)
    video = build_visuals(sections, bounds, work, total)

    # filtre : vidéo + compteur + sous-titres ; audio : voix + musique (à partir de 4 s) en ducking
    inputs = ["-i", video, "-i", voice_wav, "-ss", str(MUSIC_START), "-stream_loop", "-1", "-i", MUSIC]
    for p in badges:
        inputs += ["-i", p]
    fc, last = [], "[0:v]"
    for k, (s, (a, b)) in enumerate(items):
        nxt = items[k + 1][1][0] if k + 1 < len(items) else b + 0.06
        fc.append(f"[{3 + k}:v]format=rgba[b{k}]")
        fc.append(f"{last}[b{k}]overlay=x=(W-w)/2:y=110:enable='between(t,{a:.3f},{nxt:.3f})'[o{k}]")
        last = f"[o{k}]"
    fontsdir = FONTS.replace(":", r"\:")
    fc.append(f"{last}ass={ass}:fontsdir={fontsdir}[vout]")
    fc.append(f"[2:a]volume={MUSIC_VOL},afade=t=in:d=0.4,afade=t=out:st={total - 1.2:.2f}:d=1.2[mus]")
    fc.append("[1:a]apad,asplit=2[vo][sc]")
    fc.append("[mus][sc]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=250[duck]")
    fc.append("[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95[aout]")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", args.out])
    json.dump({"bounds": bounds, "groups": groups, "duration": total},
              open(os.path.join(work, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("OK", args.out, f"{dur(args.out):.1f}s")


if __name__ == "__main__":
    main()
