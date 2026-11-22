#!/usr/bin/env bash
# Atelier GTA VI v3 depuis le dépôt GitHub (le CODE vient du dépôt, seules les DONNÉES viennent du Drive).
# Usage : bash /home/claude/rockstat-videos/atelier/bootstrap.sh
set -uo pipefail
REPO=$(cd "$(dirname "$0")/.." && pwd); A=$REPO/atelier
G=~/gta; mkdir -p $G/tools $G/raw $G/bank $G/remotion/src $G/scripts $G/assets $G/out $G/rush_tv; cd $G
export SSL_CERT_FILE=~/.ccr/ca-bundle.crt REQUESTS_CA_BUNDLE=~/.ccr/ca-bundle.crt
dl(){ curl -sS -L -m 300 -o "$2" "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"; }
# 0) code depuis le dépôt (jamais depuis le Drive)
cp -r $A/. $G/ && rm -f $G/bootstrap.sh
cp remotion_Video.tsx remotion/src/Video.tsx; cp remotion_Root.tsx remotion/src/Root.tsx; cp remotion_index.ts remotion/src/index.ts
cp logo_rs.png assets/
# 1) inventaire du Drive « GTA VI » (données uniquement)
python3 -I - <<'PY'
import re,urllib.request,html
def ls(fid):
    h=urllib.request.urlopen(f"https://drive.google.com/embeddedfolderview?id={fid}",timeout=60).read().decode()
    for m in re.finditer(r'<a href="([^"]+)"[^>]*>.*?<div class="flip-entry-title">([^<]*)</div>',h,re.S):
        i=re.search(r'/(?:d|folders)/([A-Za-z0-9_-]{20,})',m.group(1))
        if i: yield ("dir" if "/folders/" in m.group(1) else "file"),i.group(1),html.unescape(m.group(2))
def walk(fid,p=""):
    for t,i,n in ls(fid):
        if t=="dir": yield from walk(i,p+n+"/")
        else: yield i,p+n
with open("all_ids.tsv","w") as f:
    for i,n in walk("1n6nLkWVVGK8pHDaZd36WOTlNESQ_tU7A"): f.write(f"{i}\t{n}\n")
PY
# 2) clés (jamais dans le dépôt), fiche, index, assets, banque
declare -A KEY=([gemini_key.txt]=.gemini_key [telegram_token.txt]=.tg_token [apify_token.txt]=.apify_token [telegram_radar_token.txt]=.tg_radar_token)
while IFS=$'\t' read -r id path; do
  case "$path" in
    00_ATELIER/gemini_key.txt|00_ATELIER/telegram_token.txt|00_ATELIER/apify_token.txt|00_ATELIER/telegram_radar_token.txt) dl "$id" "${KEY[${path#00_ATELIER/}]}" & ;;
    00_ATELIER/LISEZMOI_FICHE_V3.md) dl "$id" LISEZMOI_FICHE_V3.md & ;;
    INDEX_PLANS.csv) dl "$id" INDEX_PLANS.csv & ;;
    00_ATELIER/ASSETS_V2/*) dl "$id" "raw/${path##*/}" & ;;
    0[1-6]_*/*.mp4|99_HABILLAGE/*.mp4) [ -s "bank/${path##*/}" ] || dl "$id" "bank/${path##*/}" & ;;
  esac
done < all_ids.tsv; wait
for k in .gemini_key .tg_token .apify_token .tg_radar_token; do [ -f $k ] && tr -d '\n\r ' < $k > $k.t && mv $k.t $k && chmod 600 $k; done
# 3) installation
bash setup.sh $G >/tmp/setup.log 2>&1; tail -1 /tmp/setup.log
python3 setup_v2.py | tail -2
grep -q "v3" remotion/src/Video.tsx && grep -q 'subscribe' remotion/src/Video.tsx || { cp remotion/src/Video.tsx remotion_Video.tsx && patch -p1 -i v3.patch && cp remotion_Video.tsx remotion/src/Video.tsx; }
python3 fix_sans_numeros.py
# plans gameplay gp_* : jamais pris en bouche-trou dans les autres vidéos
sed -i 's/if f.endswith(".mp4") and n.lower() not in EXCLUDE:/if f.endswith(".mp4") and n.lower() not in EXCLUDE and not n.startswith("gp_"):/' make_video.py; grep -c 'startswith("gp_")' make_video.py
# copie AVANT sfx v5 = rendu de la vidéo Randy du 21/11 (voix Fenrir énergique, SFX v4) -> preset "v4"
cp make_video.py make_video_v4.py
python3 sfx_v5.py
# 4) index de la banque disponible
python3 - <<'PY'
import csv,os
rows=list(csv.reader(open("INDEX_PLANS.csv",encoding="utf-8-sig"),delimiter=";"))
ok=[rows[0]]+[r for r in rows[1:] if len(r)>2 and os.path.exists("bank/"+r[2])]
csv.writer(open("BANQUE.csv","w"),delimiter=";").writerows(ok); print(f"banque : {len(ok)-1} plans")
PY
# 5) clone de travail pour video.sh (branches v-<slug>)
[ -d ~/rv/.git ] || git clone -q "$REPO" ~/rv && git -C ~/rv remote set-url origin "$(git -C $REPO remote get-url origin)"
echo "ATELIER PRÊT"
mkdir -p rush_v2; for f in bank/*.mp4; do n=$(basename "$f" .mp4); n=${n##*_}; [ -e rush_v2/b_$n.mp4 ] || cp "$f" rush_v2/b_$n.mp4; done
python3 bank_focus.py >/dev/null 2>&1; echo "cadrage OK"
