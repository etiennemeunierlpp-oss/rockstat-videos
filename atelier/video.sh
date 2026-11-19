#!/usr/bin/env bash
# Vidéo complète en une commande : bash video.sh <slug> <script.json> <clip_miniature.mp4> <t> "<ligne rose>" "<ligne 2>" "<ligne 3>"
# Prérequis : bootstrap.sh fait ; dépôt rockstat-videos cloné dans ~/rv (add_repo push).
set -euo pipefail; cd ~/gta
S=$1; J=$2; O=out/$S.mp4
PROPS_ONLY=1 python3 make_video.py $J $O --engine gemini --voice Fenrir 2>&1 | grep -v WARN | tail -3
python3 make_video.py $J $O --engine gemini --voice Fenrir 2>&1 | grep -v WARN | tail -3
python3 thumb.py "$3" "$4" "$5" "$6" "$7" out/${S}_thumb.jpg
python3 add_cover.py $O out/${S}_thumb.jpg
ffmpeg -y -v error -i $O -c:v libx264 -b:v 4500k -maxrate 5000k -bufsize 9000k -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart out/${S}_web.mp4
cd ~/rv && git checkout -q --orphan v-$S && git rm -rqf . 2>/dev/null || true
cp ~/gta/out/${S}_web.mp4 $S.mp4 && cp ~/gta/out/${S}_thumb.jpg ${S}_thumb.jpg
git add $S.mp4 ${S}_thumb.jpg && git commit -qm "$S" && git -c push.negotiate=true push -q origin v-$S
URL="https://raw.githubusercontent.com/etiennemeunierlpp-oss/rockstat-videos/v-$S/$S.mp4"
echo "LIEN $URL"; cd ~/gta
python3 tg.py video out/${S}_web.mp4 "🎬 $S — réponds « go » + créneau (ou « go maintenant ») pour publier sur les 4 réseaux."
