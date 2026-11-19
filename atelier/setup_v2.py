#!/usr/bin/env python3
"""Style v2 (validé par Etienne le 18/11) : prépare les assets du Drive partagé « 0AKiz2I5IeDsqUk9PVA ».

Avant : télécharger avec le connecteur Drive (download_file_content) dans ~/gta/raw/ en gardant le NOM EXACT du fichier Drive :
  - RUSH VIDEO/*.mp4            (dossier 1qI08JqYIOIF_nLjlxDRUCB1Opm4EsipN)
  - sound-Design/*              (dossier 1A8U6O4Jo_TjDo4i2RCUg-Q74RP_IFAbp)
  - light leak transitions/*.mp4 sauf « Riser Light leak V4.mov » (trop lourd) (dossier 1H_WoWXXuD4gvuZ39DVDKGxg36htarCbQ)
  - Musique/reelsvideo.io_1794679757715.mp3 (dossier 1ChZqIm2EXCNsWZR3IVNwC49ozKmopjPZ)
  - sons en plus (IDs Drive) : Hit.mp3 1ThKqRlqIghIhdVvFMhzjBbeNUqDSM1WQ, SFX- Ui10.mp3 1MMYx_NbFLSo7MUTkWls6TD-th-i_uI-s,
    SFX- Ui07.mp3 1yhr4Jeqfkwtt36o37OwA1LoFcjb6ZgaP, SFX- Ui06.mp3 1xeLKfwgOExjYItOX1mAPOzms44kRll5H, Keyboard.mp3 1zV1zO7lh4J_onetRWsJG35nqMwUecahp,
    Marker.mp3 1I2GjzlXAwomF7TecySbx3hZFi0LiPL9f, The Big One - short.wav 1FIXSc3oUKS06ZNgO92mgPhFBLVS-6z6n, Taiko - short.wav 19Ud2OdcfczyfMFeHeW9fo_OQ-kZN8M56
  - ASSETS/Logo GTA VI.webp, ASSETS/Map GTA 6.png (dossier 1Qzrg6x2Hujk8XlDntTMV7COtrwFxfgeu)
Puis : python3 setup_v2.py   (après setup.sh ; applique aussi v2.patch à make_video.py et Video.tsx)
"""
import os, re, subprocess, shutil, unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "raw")
DARK = {"love", "love3", "jayson"}            # plans trop sombres (jayson.mp4 = gros plan noir)


def slug(n):
    n = unicodedata.normalize("NFD", n.lower())
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", n).strip("_")


def run(c):
    subprocess.run(c, check=True)


# 1) passer make_video.py et Video.tsx en v2 (patch v2.patch, idempotent)
if "def v2_design" not in open(os.path.join(ROOT, "make_video.py")).read():
    vt = os.path.join(ROOT, "remotion", "src", "Video.tsx")
    shutil.copy(vt, os.path.join(ROOT, "remotion_Video.tsx"))
    run(["patch", "-p1", "-d", ROOT, "-i", os.path.join(ROOT, "v2.patch")])
    shutil.copy(os.path.join(ROOT, "remotion_Video.tsx"), vt)
    print("atelier passé en v2")

# 2) assets du Drive partagé
for d in ["rush_v2", "sfx", "leaks", "music_pack", "assets", "raw"]:
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)

for f in sorted(os.listdir(RAW)):
    p = os.path.join(RAW, f); base, ext = os.path.splitext(f); ext = ext.lower(); s = slug(base)
    if ext == ".mp4" and ("leak" in s or "scratch" in s):
        shutil.copy(p, os.path.join(ROOT, "leaks", {"light_leak_v1": "leak1", "light_leak_v2": "leak2", "light_scratch_v3": "scratch3"}.get(s, s) + ".mp4"))
    elif ext == ".mp4":
        if s in DARK:
            continue
        shutil.copy(p, os.path.join(ROOT, "rush_v2", "v_" + s + ".mp4"))
    elif ext in (".wav", ".mp3") and s.startswith("reelsvideo"):
        shutil.copy(p, os.path.join(ROOT, "music_pack", "m1_1114.mp3" if "1794679757715" in s else s + ".mp3"))
    elif ext in (".wav", ".mp3"):
        name = {"swoosh_quick_1": "swoosh_quick", "deep_woosh": "deep_woosh", "text_appear_sound_effect": "text_pop",
                "cam_shutter": "cam_shutter", "mixkit_cinematic_laser_swoosh_1467": "laser_swoosh", "riser": "riser",
                "cha_ching_sound_effect": "cha_ching", "censor_beep_sound_effect": "censor_beep", "sfx_ui10": "ui10", "sfx_ui07": "ui07",
                "sfx_ui06": "ui06", "the_big_one_short": "big_one", "taiko_short": "taiko"}.get(s, s)
        src = p
        if name == "text_pop":   # le fichier fait 29 s : on garde le 1er son
            src = os.path.join(RAW, "_text_pop.wav")
            run(["ffmpeg", "-v", "error", "-y", "-i", p, "-t", "0.7", "-af", "afade=t=out:st=0.5:d=0.2", src])
        pk = subprocess.run(["ffmpeg", "-i", src, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        m = re.search(r"max_volume: (-?[\d.]+) dB", pk); g = -1.0 - float(m.group(1)) if m else 0
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"volume={g:.2f}dB", "-ar", "48000", "-ac", "2",
             os.path.join(ROOT, "sfx", f"v2_{name}.wav")])
    elif ext in (".webp", ".png", ".jpg"):
        shutil.copy(p, os.path.join(ROOT, "assets", {"logo_gta_vi": "logo_gta6", "map_gta_6": "map_gta6"}.get(s, s) + ext))

# sons utilisés par le style v2 et absents des téléchargements : remplacés par les sons synthétisés de make_sfx.py
for need, fallback in [("swoosh_low", "swish"), ("ui10", "pop"), ("ui07", "bloop"), ("ui06", "sparkle"), ("hit", "soft_boom"),
                       ("big_one", "soft_boom"), ("taiko", "soft_boom"), ("keyboard", "tick"), ("marker", "ding"),
                       ("deep_woosh", "whoosh"), ("riser", "riser"), ("text_pop", "pop"), ("cam_shutter", "pop")]:
    dst = os.path.join(ROOT, "sfx", f"v2_{need}.wav")
    if not os.path.exists(dst):
        shutil.copy(os.path.join(ROOT, "sfx", f"{fallback}.wav"), dst)
print("v2 prêt :", len(os.listdir(os.path.join(ROOT, "rush_v2"))), "rushes v2,",
      len([x for x in os.listdir(os.path.join(ROOT, "sfx")) if x.startswith("v2_")]), "sons v2,",
      os.listdir(os.path.join(ROOT, "leaks")), os.listdir(os.path.join(ROOT, "music_pack")))
