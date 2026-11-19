#!/usr/bin/env bash
# Reconstruit l'atelier vidéo GTA VI dans une session neuve.
# Usage : bash setup.sh <dossier>   (make_video.py et rush_index.json doivent déjà y être)
set -euo pipefail
D="${1:-$PWD}"; cd "$D"
mkdir -p rush rush_tv music fonts piper out scripts work
export SSL_CERT_FILE=~/.ccr/ca-bundle.crt REQUESTS_CA_BUNDLE=~/.ccr/ca-bundle.crt

pip install --break-system-packages -q faster-whisper piper-tts pillow 2>/dev/null || true

# Rushes : dossier Drive partagé par lien (RUSH GTA VI)
dl() { curl -sS -L -m 180 -o "$2" "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"; }
while IFS=$'\t' read -r id name; do [ -s "rush/$name" ] || dl "$id" "rush/$name" & done < rush_ids.tsv
wait

# Musique (thème GTA VI) : ID Drive dans music_id.txt
[ -s music/theme.mp3 ] || dl "$(cat music_id.txt)" music/theme.mp3
# vérifie que c'est bien un mp3 (sinon le fichier n'est pas partagé par lien)
file music/theme.mp3 | grep -qi -E "audio|MPEG" || { echo "MUSIQUE INACCESSIBLE : partager le mp3 par lien et mettre son ID dans music_id.txt"; rm -f music/theme.mp3; }

# Plans verticaux tirés du trailer de lancement vertical
python3 - <<'EOF'
import subprocess, os
cuts=[0]+[float(x) for x in "4.3 7.3 9.23333 11.5333 12.5 14.7 15.7667 17.2333 18.8 22.2 23.0333 24.4667 25.8667 27.4 28.4 29.8333 31.7333 32.8333 34.4667 36.3667 38.3 40.7 42.3667 43.6 45.5 46.9333 48.3333 49.3 51.6 52.4667 52.8667 54.4333 55.5 56.9667 58.3667 59.3 60.5 61.2333 62.2333 64.6333".split()]
i=0
for a,b in zip(cuts,cuts[1:]):
    d=b-a-0.1
    if d<0.6: continue
    n=f"TV_{i:02d}"; i+=1
    if n=="TV_31": continue          # écran noir
    out=f"rush_tv/{n}.mp4"
    if not os.path.exists(out):
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{a+0.05:.3f}","-i","rush/Launch Trailer.mp4","-t",f"{d:.3f}","-an","-c:v","libx264","-preset","veryfast","-crf","16",out],check=True)
EOF

# Polices
G=https://raw.githubusercontent.com
[ -s fonts/Montserrat-Black.ttf ] || curl -sSL -o fonts/Montserrat-Black.ttf $G/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Black.ttf
[ -s fonts/Montserrat-ExtraBoldItalic.ttf ] || curl -sSL -o fonts/Montserrat-ExtraBoldItalic.ttf $G/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-ExtraBoldItalic.ttf
# emojis (incrustations)
fc-list | grep -qi "Color Emoji" || curl -sSL -o fonts/NotoColorEmoji.ttf $G/googlefonts/noto-emoji/main/fonts/NotoColorEmoji.ttf
mkdir -p ~/.fonts && cp fonts/*.ttf ~/.fonts/ && fc-cache -f >/dev/null 2>&1 || true

# Effets sonores (synthétisés, libres de droits) : make_sfx.py
python3 make_sfx.py

# Détection des personnages (cadrage 9:16) : modèle YuNet + analyse des rushes pas encore indexés
pip install --break-system-packages -q opencv-python-headless numpy 2>/dev/null || true
mkdir -p models
[ -s models/yunet.onnx ] || curl -sSL -o models/yunet.onnx https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx
python3 -c "import json,sys; sys.exit(0 if all('focus_x' in c for c in json.load(open('rush_index.json'))) else 1)" || python3 analyze_rushes.py >/dev/null 2>&1

# Remotion (modèle vidéo) : remotion/src/{index.ts,Root.tsx,Video.tsx} doivent être présents
if [ -d remotion/src ] && [ ! -d remotion/node_modules ]; then
  (cd remotion && npm init -y >/dev/null && npm i --silent remotion@4 @remotion/cli@4 @remotion/renderer@4 @remotion/bundler@4 react@18 react-dom@18 typescript)
fi
mkdir -p logos

# Voix de secours (si Gemini indisponible)
H=https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/tom/medium
for f in fr_FR-tom-medium.onnx fr_FR-tom-medium.onnx.json; do [ -s piper/$f ] || curl -sSL -o piper/$f $H/$f; done
echo "Atelier prêt : $(ls rush | wc -l) rushes, $(ls rush_tv | wc -l) plans verticaux"
