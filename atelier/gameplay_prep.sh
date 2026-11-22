#!/usr/bin/env bash
# Prépare un gameplay YouTube pour le format « gameplay » : gameplay_req/<id>.json = {"id":"<id>","url":"https://www.youtube.com/watch?v=…"}
# -> branche g-<id> : src.mp4 (H.264 ≤1080p, sans son), transcript.txt (timecodes), sheet_*.jpg (1 image / 2 s, timecodes), info.txt
set -uo pipefail
REPO=$(cd "$(dirname "$0")/.." && pwd)
sudo apt-get -qq update >/dev/null && sudo apt-get -qq install -y ffmpeg fonts-dejavu-core >/dev/null
pip install -q -U yt-dlp >/dev/null 2>&1
mkdir -p ~/gta && curl -sSL -o ~/gta/.tg_token "https://drive.usercontent.google.com/download?id=10dqt-uGTmtvOztO4KxMxFmrBWeAlUjOb&export=download&confirm=t" && tr -d '\n\r ' < ~/gta/.tg_token > ~/gta/.t && mv ~/gta/.t ~/gta/.tg_token
for f in $REPO/gameplay_req/*.json; do [ -e "$f" ] || continue
  read -r ID URL < <(python3 -c "import json,sys;q=json.load(open(sys.argv[1]));print(q['id'],q['url'])" "$f")
  git -C $REPO ls-remote --exit-code --heads origin "g-$ID" >/dev/null 2>&1 && continue
  W=/tmp/g_$ID; rm -rf $W; mkdir -p $W; cd $W
  if echo "$URL" | grep -qE "youtube\.com|youtu\.be"; then   # YouTube bloque GitHub -> téléchargement via Apify (epctex, 0,00075 $/s en 1080p)
    VID=$(python3 -c "import re,sys;print(re.search(r'(?:v=|youtu\.be/|shorts/)([\w-]{11})',sys.argv[1]).group(1))" "$URL")
    AT=$(curl -sSL "https://drive.usercontent.google.com/download?id=1hyGTkqB1Zcjjnq2n-fJ1IeLA_e_vS1k6&export=download&confirm=t" | tr -d '\n\r ')
    curl -s -m 600 -X POST -H "Authorization: Bearer $AT" -H "Content-Type: application/json" \
      "https://api.apify.com/v2/acts/epctex~youtube-video-downloader/run-sync-get-dataset-items?timeout=580" \
      -d "{\"videoIds\":[\"$VID\"],\"quality\":\"1080\",\"storageType\":\"apify\",\"apifyAutoDelete\":true}" > apify.json
    U=$(python3 -c "import json;d=json.load(open('apify.json'));print(d[0]['output']['url'] if d and d[0].get('status')=='succeeded' else '')" 2>>yt.log)
    [ -n "$U" ] && curl -sSL -o dl.mp4 "$U" || cat apify.json >> yt.log
    yt-dlp -q --skip-download --write-info-json -o "dl.%(ext)s" "$URL" >> yt.log 2>&1 || echo "{\"title\":\"$VID\",\"webpage_url\":\"$URL\"}" > dl.info.json
  fi
  [ -s dl.mp4 ] || yt-dlp -q --no-warnings -f "bv*[vcodec^=avc1][height<=1080]/bv*[height<=1080]" --write-auto-subs --sub-langs "en.*,fr.*" --sub-format vtt \
         --write-info-json -o "dl.%(ext)s" "$URL" > yt.log 2>&1 || true
  for pc in tv mweb web_safari android_vr; do [ -n "$(ls dl.mp4 dl.webm dl.mkv 2>/dev/null)" ] && break   # YouTube bloque souvent les serveurs GitHub
    yt-dlp -q --no-warnings --extractor-args "youtube:player_client=$pc" -f "bv*[vcodec^=avc1][height<=1080]/bv*[height<=1080]/b" --write-auto-subs --sub-langs "en.*,fr.*" --sub-format vtt \
           --write-info-json -o "dl.%(ext)s" "$URL" >> yt.log 2>&1 || true; done
  V=$(ls dl.mp4 dl.webm dl.mkv 2>/dev/null | head -1)
  if [ -z "$V" ]; then
    (cd $REPO/atelier && python3 tg.py send "❌ Gameplay $ID : téléchargement YouTube refusé — $(tail -c 250 $W/yt.log)" 2>/dev/null) || true
    cd $REPO; git checkout -q --orphan "log-g-$ID"; git rm -rqf . 2>/dev/null; cp $W/yt.log .; git add yt.log; git commit -qm "log g-$ID"; git push -qf origin "log-g-$ID"; git checkout -q main; continue
  fi
  ffmpeg -nostdin -v error -y -i "$V" -an -vf "scale=-2:1080,fps=30" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -movflags +faststart src.mp4
  python3 - <<'PY'
import json,re,glob
d=json.load(open(glob.glob("dl.info.json")[0]))
open("info.txt","w").write(f"{d.get('title')}\n{d.get('channel')} ({d.get('uploader_id')})\n{d.get('webpage_url')}\n{d.get('duration')} s, {d.get('view_count')} vues, {d.get('upload_date')}\n")
out=[];last=""
for v in glob.glob("dl.*.vtt")[:1]:
    for b in open(v).read().split("\n\n"):
        m=re.search(r"(\d\d:\d\d:\d\d)\.\d+ -->",b)
        if not m: continue
        L=[re.sub(r"<[^>]+>","",l).strip() for l in b.split("\n")[1:] if l.strip() and "-->" not in l]
        t=L[-1] if L else ""
        if t and t!=last: out.append(m.group(1)[3:]+" "+t); last=t
open("transcript.txt","w").write("\n".join(out) or "(pas de sous-titres)")
PY
  if grep -q "pas de sous-titres" transcript.txt; then   # TikTok : pas de sous-titres -> Whisper
    pip install -q faster-whisper >/dev/null 2>&1
    ffmpeg -nostdin -v error -y -i "$V" -vn -ac 1 -ar 16000 a.wav && python3 - <<'PY'
import wave,numpy as np
from faster_whisper import WhisperModel
w=wave.open("a.wav"); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
m=WhisperModel("small",device="cpu",compute_type="int8")
seg,_=m.transcribe(a,vad_filter=True)
open("transcript.txt","w").write("\n".join(f"{int(x.start)//60:02d}:{int(x.start)%60:02d} {x.text.strip()}" for x in seg))
PY
  fi
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 src.mp4 | cut -d. -f1)
  i=0; for ((ss=0; ss<D; ss+=60)); do
    ffmpeg -nostdin -v error -y -ss $ss -t 60 -i src.mp4 -vf "fps=1/2,scale=320:-1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='%{eif\:t+$ss\:d}s':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black,tile=6x5" -frames:v 1 -q:v 5 sheet_$(printf %02d $i).jpg; i=$((i+1)); done
  cd $REPO; git checkout -q --orphan "g-$ID"; git rm -rqf . 2>/dev/null
  cp $W/src.mp4 $W/transcript.txt $W/info.txt $W/sheet_*.jpg .
  git add src.mp4 transcript.txt info.txt sheet_*.jpg && git commit -qm "gameplay $ID" && git push -qf origin "g-$ID"
  git checkout -q main
  (cd $REPO/atelier && python3 tg.py send "🎮 Gameplay $ID prêt ($(head -1 $W/info.txt))" 2>/dev/null) || true
done
