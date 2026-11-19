#!/usr/bin/env python3
"""Pose la miniature sur les premières images de la vidéo (durée inchangée, son intact).
Usage : python3 add_cover.py out/X.mp4 out/X_thumb.jpg [--dur 0.2]
La vidéo est remplacée sur place. Couverture TikTok : videoCoverMilliseconds = 100."""
import argparse, os, subprocess, json, shutil
p = argparse.ArgumentParser()
p.add_argument("video"); p.add_argument("thumb")
p.add_argument("--dur", type=float, default=0.2)
a = p.parse_args()
info = json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0",
    "-show_entries","stream=width,height","-of","json",a.video]))["streams"][0]
w, h = info["width"], info["height"]
tmp = a.video + ".cover.mp4"
vf = (f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1[c];"
      f"[0:v][c]overlay=0:0:enable='lt(t,{a.dur})'[v]")
subprocess.check_call(["ffmpeg","-y","-v","error","-i",a.video,"-loop","1","-t",str(a.dur+0.1),"-i",a.thumb,
    "-filter_complex",vf,"-map","[v]","-map","0:a?","-c:v","libx264","-preset","veryfast","-crf","18",
    "-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",tmp])
shutil.move(tmp, a.video)
print(f"OK : miniature sur 0-{int(a.dur*1000)} ms -> {a.video} (videoCoverMilliseconds=100)")
