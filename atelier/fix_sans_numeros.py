#!/usr/bin/env python3
"""Supprime la numérotation des parties (badge « 2/5 », pastille numérotée devant l'en-tête des cartes, points 1-2-3-4-5).
Demande d'Etienne du 18/11. À lancer après setup_v2.py (et v3.patch) : cd ~/gta && python3 fix_sans_numeros.py
Idempotent. Pour réactiver ponctuellement : "numbering": true dans le script JSON.
"""
import os

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_video.py")
s = open(p).read()
old = '''        I.append({"n": k + 1, "total": len(items), "start": F(a), "end": F(b)})
        if s.get("layout") == "card":
            cards.append({"start": F(a), "end": F(b), "header": s.get("header"), "n": k + 1, "total": len(items)})'''
new = '''        num = bool(cfg.get("numbering", False))  # numérotation des parties désactivée depuis le 18/11 (demande d'Etienne)
        if num:
            I.append({"n": k + 1, "total": len(items), "start": F(a), "end": F(b)})
        if s.get("layout") == "card":
            cards.append({"start": F(a), "end": F(b), "header": s.get("header"), "n": (k + 1) if num else None, "total": len(items) if num else None})'''
if new in s:
    print("numérotation déjà désactivée")
elif old in s:
    open(p, "w").write(s.replace(old, new))
    print("numérotation désactivée")
else:
    raise SystemExit("ERREUR : bloc de numérotation introuvable dans make_video.py")
