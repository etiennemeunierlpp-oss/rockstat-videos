#!/usr/bin/env python3
"""Sound design v5 (Etienne 20/11) : 20 SFX Mixkit (sfx/mk_*.mp3) sur chaque animation. À lancer après setup_v2.py / v3.patch / fix_sans_numeros.py."""
import os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_video.py")
s = open(p).read()
if "SFX_V5" in s:
    raise SystemExit("sfx v5 déjà en place")
NEW = '''def v2_design(S, I, cards, FX, title, bounds, sections, F, total):
    # SFX_V5 : un son par animation (pack Mixkit validé par Etienne le 20/11)
    M = lambda n: "sfx/" + n + ".mp3"
    MK = {"label": [("mk_02_swoosh_express", 0.35, -4)], "sticker": [("mk_04_zoom_impact", 0.45, -3)],
          "big": [("mk_03_swipe_zoom", 0.3, -8), ("mk_05_bass_hit", 0.6, 0)], "clock": [("mk_17_ui_click", 0.45, 0)],
          "bars": [("mk_14_bonus", 0.4, 4)], "stars": [("mk_12_coin_game", 0.45, 0)], "source": [("mk_17_ui_click", 0.5, 0)],
          "alert": [("mk_16_message", 0.55, 0)], "emoji": [("mk_15_bubble_pop", 0.5, 0), ("mk_15_bubble_pop", 0.4, 6)],
          "image": [("mk_03_swipe_zoom", 0.35, -6), ("mk_18_camera", 0.5, 0)], "logo": [("mk_07_glitch_trailer", 0.5, -2), ("mk_05_bass_hit", 0.5, 0)],
          "subscribe": [("mk_02_swoosh_express", 0.3, -4), ("mk_15_bubble_pop", 0.45, 1), ("mk_17_ui_click", 0.5, 26), ("mk_20_unlock", 0.45, 30)]}
    sfx = [{"src": M("mk_07_glitch_trailer"), "frame": 0, "volume": 0.5}]
    leaks, shakes, flashes = [], [], []
    drop = F(bounds[1][0]) if len(bounds) > 1 else None
    last_sec = F(bounds[-1][0]) if len(bounds) > 2 else None
    k = 0; nc = 0
    for s in S[1:]:
        if s["cut"] == "section":
            if s["from"] == drop:
                continue
            if s["from"] == last_sec:
                sfx.append({"src": M("mk_19_scratch"), "frame": s["from"] - 4, "volume": 0.4})
            else:
                sfx.append({"src": M("mk_01_transition"), "frame": s["from"] - 8, "volume": 0.4})
            src, d = LEAKS[k % len(LEAKS)]; k += 1
            leaks.append({"src": src, "frame": s["from"] - 3, "dur": d})
        else:
            nc += 1
            if nc % 3 == 0:   # coupes rapides : un swipe léger une coupe sur trois
                sfx.append({"src": M("mk_03_swipe_zoom"), "frame": s["from"] - 4, "volume": 0.12})
    if drop:
        sfx.append({"src": M("mk_09_riser"), "frame": drop - 70, "volume": 0.35})
        sfx.append({"src": M("mk_06_bass_futur"), "frame": drop, "volume": 0.55})
        sfx.append({"src": M("mk_08_glitch_break"), "frame": drop - 2, "volume": 0.3})
        flashes.append(drop); shakes.append(drop)
        leaks.append({"src": "leaks/leak2.mp4", "frame": drop - 2, "dur": 18})
    for it in I:
        sfx.append({"src": M("mk_05_bass_hit"), "frame": it["start"] - 2, "volume": 0.4})
        shakes.append(it["start"])
    for x in FX:
        if x["type"] == "counter":
            # argent : plus de sons (Etienne 21/11) — pièces au départ, cliquetis pendant le défilement, sac + pièce magique à l'arrivée
            sfx.append({"src": M("mk_10_coins"), "frame": x["start"], "volume": 0.55})
            for k in range(4, 24, 5):
                sfx.append({"src": M("mk_12_coin_game"), "frame": x["start"] + k, "volume": 0.22})
            sfx.append({"src": M("mk_13_money_bag"), "frame": x["start"] + 24, "volume": 0.6})
            sfx.append({"src": M("mk_11_coin_magic"), "frame": x["start"] + 26, "volume": 0.35})
        if x["type"] == "big" and "$" in str(x.get("text", "")):
            sfx.append({"src": M("mk_10_coins"), "frame": x["start"], "volume": 0.5})
            sfx.append({"src": M("mk_13_money_bag"), "frame": x["start"] + 8, "volume": 0.5})
        for src, vol, dl in MK.get(x["type"], []):
            sfx.append({"src": M(src), "frame": x["start"] + dl, "volume": vol})
        if x["type"] in ("big", "alert"):
            shakes.append(x["start"])
    if title:
        sfx.append({"src": M("mk_06_bass_futur"), "frame": title["start"] - 2, "volume": 0.5})
        shakes.append(title["start"])
    sfx = [x for x in sfx if 0 <= x["frame"] < F(total) - 3]
    return sfx, leaks, sorted(set(shakes)), flashes


'''
s2, n = re.subn(r"def v2_design\(.*?\n(?=def render_remotion)", lambda m: NEW, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("ERREUR : v2_design introuvable dans make_video.py")
old_style = ("Parle comme un jeune créateur TikTok gaming qui raconte une info à son pote : énergique et naturel, débit rapide mais ")
new_style = ("Parle comme un pote sympa et souriant qui te file un bon plan sur TikTok : ton chaleureux, détendu et enjoué, on entend le sourire, "
             "débit dynamique mais ")
if old_style in s2:   # voix Achird « amical » (Etienne 20/11)
    s2 = s2.replace(old_style, new_style)
else:
    print("ATTENTION : style de voix non trouvé, inchangé")
open(p, "w").write(s2)
print("sfx v5 en place")
