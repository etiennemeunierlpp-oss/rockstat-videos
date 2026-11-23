#!/usr/bin/env python3
"""Format gameplay : découpe les plans d'un gameplay préparé (branche g-<id>) en plans verticaux ~/gta/rush_tv/<nom>.mp4.
Dans le fichier de file : "gameplay":{"src":"g-<id>","cuts":[["gp_map1",20.5,0],["gp_corps1",46,1,0.4],...]}
  cut = [nom (commence par gp_), début en s, sombre 0/1, (option) cadrage x 0-1 (0,5 = centre), (option) zoom 1-1,6] ; chaque plan dure 2,5 s.
Recadrage (Etienne 23/11, d'après le reel koumaoff) : source 16:9 recoupée (on retire 4 % en haut et 12 % en bas : sous-titres
incrustés du créateur source), bande verticale 1080x1600 au centre, fond = même image floutée (bandes de 160 px en haut/bas).
Avec zoom > 1 : la bande est prise plus serrée (gros plan sur le cadrage x)."""
import json, os, subprocess, sys, urllib.request
q = json.load(open(sys.argv[1])); g = q.get("gameplay") or q.get("cfg", {}).get("gameplay")   # tolère "gameplay" rangé dans cfg (bug 23/11)
if not g:
    if '"gp_' in json.dumps(q.get("cfg", {})): sys.exit("plans gp_ référencés mais aucun bloc \"gameplay\" (à mettre au niveau racine du fichier)")
    sys.exit(0)
R = os.path.expanduser("~/gta/rush_tv"); os.makedirs(R, exist_ok=True)
src = f"/tmp/{g['src']}.mp4"
if not os.path.exists(src):
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/etiennemeunierlpp-oss/rockstat-videos/{g['src']}/src.mp4", src)
for c in g["cuts"]:
    n, s, dark = c[0], float(c[1]), int(c[2]); x = float(c[3]) if len(c) > 3 else 0.5; z = max(1.0, min(1.6, float(c[4]) if len(c) > 4 else 1.0))
    assert n.startswith("gp_"), n
    eq = "eq=brightness=0.03:gamma=1.28:saturation=1.2:contrast=1.12" if dark else "eq=saturation=1.1:contrast=1.03"
    h = int(1600 * z)
    vf = (f"crop=iw:ih*0.84:0:ih*0.04,{eq},split[a][b];"
          f"[a]scale=-2:1920,crop=1080:1920:(iw-1080)*{x}:0,boxblur=28:2,eq=brightness=-0.15[bg];"
          f"[b]scale=-2:{h}:flags=lanczos,crop=1080:1600:(iw-1080)*{x}:(ih-1600)/2[fg];"
          f"[bg][fg]overlay=0:160,fps=30,setsar=1")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{s:.2f}", "-t", "2.5", "-i", src, "-an", "-filter_complex", vf,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", f"{R}/{n}.mp4"], check=True)
print(f"gameplay : {len(g['cuts'])} plans découpés depuis {g['src']}")
