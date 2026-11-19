#!/usr/bin/env python3
"""Synthèse des effets sonores (doux, "TikTok friendly", libres de droits) -> sfx/*.wav"""
import numpy as np, os, wave, sys

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, a, d, curve=4.0):
    """attaque linéaire a (s), décroissance exponentielle sur le reste"""
    x = np.ones(n)
    na = max(int(a * SR), 1)
    x[:na] = np.linspace(0, 1, na)
    rest = n - na
    if rest > 0:
        x[na:] = np.exp(-curve * np.linspace(0, 1, rest) * (d if d else 1))
    return x


def glide(f0, f1, d, shape=1.0):
    tt = t(d)
    f = f0 + (f1 - f0) * (tt / d) ** shape
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def bandpass_sweep(x, f0, f1):
    """filtre passe-bande glissant simple (biquad mis à jour par blocs)"""
    y = np.zeros_like(x)
    n, blk = len(x), 256
    z1 = z2 = 0.0
    for i in range(0, n, blk):
        fc = f0 + (f1 - f0) * (i / n)
        q = 1.2
        w0 = 2 * np.pi * fc / SR
        al = np.sin(w0) / (2 * q)
        b0, b1, b2 = al, 0, -al
        a0, a1, a2 = 1 + al, -2 * np.cos(w0), 1 - al
        b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
        for j in range(i, min(i + blk, n)):
            xn = x[j]
            yn = b0 * xn + z1
            z1 = b1 * xn - a1 * yn + z2
            z2 = b2 * xn - a2 * yn
            y[j] = yn
    return y


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x); p = 0.0
    for i, v in enumerate(x):
        p = (1 - a) * v + a * p; y[i] = p
    return y


def reverb(x, mix=0.18, decay=0.35):
    out = np.copy(x)
    for dly, g in [(0.023, 0.5), (0.037, 0.4), (0.051, 0.32), (0.071, 0.25), (0.097, 0.18)]:
        k = int(dly * SR)
        tail = np.concatenate([np.zeros(k), x[:-k] if k < len(x) else np.zeros(0)])[:len(x)]
        out += mix * g * tail
    pad = np.zeros(int(decay * SR))
    return np.concatenate([out, pad])


def bell(f, d, partials=((1, 1), (2.0, 0.35), (3.01, 0.18), (4.2, 0.08)), decay=6):
    tt = t(d); y = np.zeros_like(tt)
    for k, a in partials:
        y += a * np.sin(2 * np.pi * f * k * tt) * np.exp(-decay * k ** 0.6 * tt / d * 3)
    return y * env(len(tt), 0.003, 1, 0.2)


def save(name, x, gain=0.8):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    fade = int(0.01 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)
    pcm = (x * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def noise(d):
    w = rng.standard_normal(int(SR * d))
    return lowpass(w, 6000)  # bruit un peu adouci


# whoosh doux (changement de partie)
d = 0.55; n = noise(d)
w = bandpass_sweep(n, 300, 2600) * np.sin(np.pi * np.linspace(0, 1, len(n))) ** 1.6
save("whoosh.wav", reverb(w, 0.2), 0.7)

# swish court (coupe simple)
d = 0.22; n = noise(d)
w = bandpass_sweep(n, 1200, 4500) * np.sin(np.pi * np.linspace(0, 1, len(n))) ** 2
save("swish.wav", w, 0.45)

# whoosh + zoom d'ouverture (montée + petit boom doux)
d = 0.75; n = noise(d)
w = bandpass_sweep(n, 200, 3800) * np.linspace(0, 1, len(n)) ** 2.2
boom = glide(90, 45, 0.45) * env(int(0.45 * SR), 0.005, 1, 5)
x = np.concatenate([w, np.zeros(int(0.45 * SR))])
x[int(0.7 * SR):int(0.7 * SR) + len(boom)] += 0.9 * boom
save("intro_whoosh.wav", reverb(x, 0.25), 0.85)

# pop bulle (labels, stickers, emojis)
d = 0.12
p = glide(1100, 380, d, 0.5) * env(int(d * SR), 0.002, 1, 6)
save("pop.wav", reverb(p, 0.15, 0.15), 0.75)

# bloop grave (cartes, compteur n/N)
d = 0.16
p = glide(520, 180, d, 0.6) * env(int(d * SR), 0.003, 1, 5) + 0.25 * glide(1040, 360, d, 0.6) * env(int(d * SR), 0.003, 1, 7)
save("bloop.wav", reverb(p, 0.18, 0.2), 0.8)

# bloop montant (barres qui poussent)
d = 0.4
p = glide(260, 880, d, 1.4) * env(int(d * SR), 0.02, 1, 2.5)
save("rise_blip.wav", reverb(p, 0.2, 0.2), 0.6)

# tick bois doux (compteurs)
d = 0.05
p = np.sin(2 * np.pi * 1650 * t(d)) * env(int(d * SR), 0.001, 1, 9)
save("tick.wav", p, 0.4)

# ding / chime (source, fin de compteur)
save("ding.wav", reverb(bell(1318.5, 0.9), 0.22, 0.4), 0.55)

# notification 2 notes montantes (alerte, à la place de la sirène)
a = bell(880, 0.25, decay=5); b = bell(1318.5, 0.6, decay=5)
x = np.concatenate([a[: int(0.13 * SR)], b])
save("notif.wav", reverb(x, 0.22, 0.35), 0.6)

# sparkle (étoiles) : arpège rapide
notes = [1046.5, 1318.5, 1568, 2093]
x = np.zeros(int(0.9 * SR))
for i, f in enumerate(notes):
    s = bell(f, 0.5, decay=7) * 0.8
    k = int(i * 0.07 * SR); x[k:k + len(s)] += s[: len(x) - k]
save("sparkle.wav", reverb(x, 0.25, 0.4), 0.5)

# boom doux (titre, mot géant)
d = 0.6
x = glide(85, 42, d, 0.7) * env(int(d * SR), 0.004, 1, 4) + 0.3 * lowpass(rng.standard_normal(int(d * SR)), 300) * env(int(d * SR), 0.002, 1, 8)
save("soft_boom.wav", reverb(x, 0.2, 0.3), 0.85)

# montée douce avant le titre
d = 1.0; n = noise(d)
x = bandpass_sweep(n, 300, 5000) * np.linspace(0, 1, len(n)) ** 2.5 * 0.7 + 0.15 * glide(200, 800, d, 1.5) * np.linspace(0, 1, int(d * SR)) ** 2
save("riser.wav", x, 0.5)

# whoosh + pop pour l'arrivée d'une carte
d = 0.3; n = noise(d)
w = bandpass_sweep(n, 800, 3500) * np.sin(np.pi * np.linspace(0, 1, len(n))) ** 2
p = glide(700, 260, 0.12, 0.5) * env(int(0.12 * SR), 0.002, 1, 6)
x = np.concatenate([w, np.zeros(int(0.12 * SR))]); x[int(0.24 * SR):int(0.24 * SR) + len(p)] += 0.9 * p
save("card_in.wav", reverb(x, 0.18, 0.2), 0.7)
print("sfx ok :", sorted(os.listdir(OUT)))
