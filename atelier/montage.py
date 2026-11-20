"""Choix des plans v4 : jamais deux fois le même plan dans une vidéo.

Usage dans un gen_script :
    from montage import Picker
    P = Picker(seed="slug")                       # même slug = même montage
    "clips": P.take(["argent", "braquage"], n=14)  # mots-clés (tags INDEX_PLANS), nb de plans

Règles :
- chaque rush long est découpé en fenêtres de 3,5 s ; une fenêtre ne sert qu'UNE fois ;
- un rush ne revient jamais dans la même partie, et au plus 2 fois dans toute la vidéo
  (3 fois pour les longues séquences de gameplay > 20 s), toujours à un autre moment ;
- jamais deux plans du même rush à la suite ;
- les plans utilisés dans les 6 dernières vidéos sont pénalisés (historique_plans.json).
"""
import csv, json, os, random, subprocess

ROOT = os.path.expanduser("~/gta")
HIST = os.path.join(ROOT, "historique_plans.json")
WIN = 3.5


def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True).stdout.strip()
    return float(r or 0)


class Picker:
    def __init__(self, seed=None, avoid_recent=6):
        self.rng = random.Random(seed)
        meta = {}
        idx = os.path.join(ROOT, "rush_index.json")
        if os.path.exists(idx):
            meta = {c["name"].lower(): c for c in json.load(open(idx))}
        self.rush = {}
        for r in csv.reader(open(os.path.join(ROOT, "BANQUE.csv"), encoding="utf-8-sig"), delimiter=";"):
            if not r or not r[0].isdigit():
                continue
            n = f"{int(r[0]):03d}"
            p = os.path.join(ROOT, "rush_v2", f"b_{n}.mp4")
            if not os.path.exists(p):
                continue
            d = _dur(p)
            m = meta.get(f"b_{n}", {})
            start = float(m.get("start_ok", 0.3) or 0.3)
            if d - start < 1.0:
                start = 0.2
            wins = [round(start + k * WIN, 2) for k in range(max(1, int((d - start - 0.8) // WIN) + 1))]
            words = (r[3] + " " + r[4] + " " + r[2]).lower().replace(",", " ").replace("_", " ").replace("-", " ")
            self.rush[n] = {"wins": wins, "words": set(words.split()), "dur": d,
                            "max": 3 if d > 20 else 2, "used": 0}
        self.used_wins = set()
        self.last = None
        self.picked = []
        recent = []
        if os.path.exists(HIST):
            for v in json.load(open(HIST))[-avoid_recent:]:
                recent += v["plans"]
        self.recent = {}
        for n in recent:
            self.recent[n] = self.recent.get(n, 0) + 1

    def _score(self, n, kws):
        r = self.rush[n]
        s = sum(3 for k in kws if any(k in w for w in r["words"]))
        s -= 2.5 * r["used"] + 1.5 * self.recent.get(n, 0)
        return s + self.rng.random() * 2.0

    def take(self, kws, n=12):
        kws = [k.lower() for k in kws]
        section, out = set(), []
        for _ in range(n):
            cands = [x for x, r in self.rush.items()
                     if x not in section and x != self.last and r["used"] < r["max"]
                     and any((x, w) not in self.used_wins for w in r["wins"])]
            if not cands:
                break
            best = max(cands, key=lambda x: self._score(x, kws))
            r = self.rush[best]
            free = [w for w in r["wins"] if (best, w) not in self.used_wins]
            w = self.rng.choice(free)
            self.used_wins.add((best, w)); r["used"] += 1
            section.add(best); self.last = best
            out.append(f"b_{best}@{w:.2f}")
            self.picked.append(best)
        return out

    def save(self, slug):
        h = json.load(open(HIST)) if os.path.exists(HIST) else []
        h = [v for v in h if v["slug"] != slug] + [{"slug": slug, "plans": sorted(set(self.picked))}]
        json.dump(h[-30:], open(HIST, "w"), indent=0)


def check(cfg):
    """Contrôle : aucun (rush, moment) en double, aucun rush deux fois dans une partie."""
    seen, errs = set(), []
    for s in cfg["sections"]:
        rs = [c.split("@")[0] for c in s["clips"]]
        if len(rs) != len(set(rs)):
            errs.append(f"rush répété dans la partie {s['id']}")
        for c in s["clips"]:
            if c in seen:
                errs.append(f"plan en double : {c}")
            seen.add(c)
    return errs
