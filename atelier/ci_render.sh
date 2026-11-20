#!/usr/bin/env bash
# Rendu sur GitHub Actions : rend chaque fichier queue/*.json pas encore publié (branche v-<slug> absente).
# Fichier de file : {"slug":..., "thumb":["rush_v2/b_146.mp4",3,"LIGNE ROSE","LIGNE 2","LIGNE 3"], "cfg":{...script...}}
set -uo pipefail
REPO=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p ~/.ccr && cp /etc/ssl/certs/ca-certificates.crt ~/.ccr/ca-bundle.crt
sudo apt-get -qq update >/dev/null && sudo apt-get -qq install -y ffmpeg fonts-noto-color-emoji >/dev/null
# file d'attente : dépôt + dossier Drive « 07_FILE » (partagé par lien) déposé par la tâche programmée
mkdir -p /tmp/q && cp $REPO/queue/*.json /tmp/q/ 2>/dev/null || true
if [ -n "${DRIVE_QUEUE:-}" ]; then python3 - "$DRIVE_QUEUE" <<'PY'
import re,sys,urllib.request,html
h=urllib.request.urlopen(f"https://drive.google.com/embeddedfolderview?id={sys.argv[1]}",timeout=60).read().decode()
for m in re.finditer(r'<a href="([^"]+)"[^>]*>.*?<div class="flip-entry-title">([^<]*)</div>',h,re.S):
    i=re.search(r'/d/([A-Za-z0-9_-]{20,})',m.group(1)); n=html.unescape(m.group(2))
    if i and n.endswith(".json"):
        urllib.request.urlretrieve(f"https://drive.usercontent.google.com/download?id={i.group(1)}&export=download&confirm=t","/tmp/q/"+n)
PY
fi
todo=()
for f in /tmp/q/*.json; do [ -e "$f" ] || continue
  s=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['slug'])" "$f")
  git -C $REPO ls-remote --exit-code --heads origin "v-$s" >/dev/null 2>&1 || todo+=("$f")
done
[ ${#todo[@]} -eq 0 ] && { echo "rien à rendre"; exit 0; }
bash $REPO/atelier/bootstrap.sh > /tmp/boot.log 2>&1; tail -5 /tmp/boot.log
H=$(git -C $REPO config --get http.https://github.com/.extraheader || true)
[ -n "$H" ] && git -C ~/rv config http.https://github.com/.extraheader "$H"
cd ~/gta
for f in "${todo[@]}"; do
  read -r S T1 T2 T3 T4 T5 < <(python3 - "$f" <<'PY'
import json,sys
q=json.load(open(sys.argv[1])); json.dump(q["cfg"],open(f"scripts/{q['slug']}.json","w"),ensure_ascii=False)
print(q["slug"],*[str(x).replace(" "," ") for x in q["thumb"]])
PY
)
  u(){ echo "${1//$' '/ }"; }
  if ! bash -x video.sh "$S" "scripts/$S.json" "$(u "$T1")" "$(u "$T2")" "$(u "$T3")" "$(u "$T4")" "$(u "$T5")" > /tmp/$S.log 2>&1; then
    python3 tg.py send "❌ Rendu GitHub échoué : $S — $(tail -c 300 /tmp/$S.log)"
    (cd ~/rv && git checkout -q --orphan log-$S && git rm -rqf . 2>/dev/null; cp /tmp/$S.log /tmp/boot.log . 2>/dev/null; cp ~/gta/work/$S/*.log . 2>/dev/null; git add -A && git commit -qm "log $S" && git push -qf origin log-$S) || true
  fi
done
