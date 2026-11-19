#!/usr/bin/env python3
"""Repère les personnages dans chaque rush (visages + silhouettes) pour cadrer le 9:16 sur eux.
Ajoute à rush_index.json : focus_x (0-1, centre du recadrage), subject (bool), start_ok (s), spread (largeur occupée)."""
import cv2, json, os, subprocess, numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
FACE = os.path.join(ROOT, "models/yunet.onnx")
hog = cv2.HOGDescriptor(); hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


def frames(path, step=0.2):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    k = max(int(fps * step), 1)
    for i in range(0, n, k):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if ok:
            yield i / fps, fr


def detect(fr):
    h, w = fr.shape[:2]
    boxes = []
    sw = 640; sh = int(sw * h / w)
    small = cv2.resize(fr, (sw, sh))
    fd = cv2.FaceDetectorYN.create(FACE, "", (sw, sh), 0.6, 0.3, 50)
    _, faces = fd.detect(small)
    if faces is not None:
        for f in faces:
            x, y, fw, fh, c = f[0], f[1], f[2], f[3], f[-1]
            if fw > sw * 0.025:
                boxes.append(("face", (x + fw / 2) / sw, fw / sw, float(c)))
    rects, weights = hog.detectMultiScale(small, winStride=(8, 8), padding=(8, 8), scale=1.05)
    for (x, y, rw, rh), wt in zip(rects, np.ravel(weights) if len(rects) else []):
        if wt > 0.6 and rh > small.shape[0] * 0.3:
            boxes.append(("body", (x + rw / 2) / small.shape[1], rw / small.shape[1], float(wt)))
    return boxes


def main():
    idx_path = os.path.join(ROOT, "rush_index.json")
    idx = json.load(open(idx_path))
    for c in idx:
        d = "rush_tv" if c["name"].startswith("TV_") else "rush"
        path = next((os.path.join(ROOT, d, f) for f in os.listdir(os.path.join(ROOT, d))
                     if os.path.splitext(f)[0].lower() == c["name"].lower()), None)
        if not path:
            continue
        hits, first = [], None
        for ts, fr in frames(path):
            b = detect(fr)
            if b:
                if first is None:
                    first = ts
                faces = [x for x in b if x[0] == "face"] or b
                hits.append((ts, faces))
        if hits:
            xs = [x[1] for _, bs in hits for x in bs]
            ws = [x[2] for _, bs in hits for x in bs]
            c["subject"] = True
            c["focus_x"] = round(float(np.median(xs)), 3)
            c["spread"] = round(float(max(xs) - min(xs) + np.median(ws)), 3)
            c["start_ok"] = round(max(first - 0.05, 0), 2)
            c["coverage"] = round(len(hits) / max(1, sum(1 for _ in frames(path))), 2)
        else:
            c["subject"] = False; c["focus_x"] = 0.5; c["spread"] = 0; c["start_ok"] = 0; c["coverage"] = 0
        print(f'{c["name"]:14s} {c["format"]:10s} subj={c["subject"]!s:5s} x={c["focus_x"]:.2f} start={c["start_ok"]:.2f} cov={c["coverage"]:.2f} spread={c["spread"]:.2f}')
    json.dump(idx, open(idx_path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
