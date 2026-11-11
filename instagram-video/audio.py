"""Synthesizes an original music bed + sound effects for the reel (no copyrighted audio)."""
import sys
import wave
import numpy as np

SR = 44100
DUR = 15.0
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(7)


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - max(pan, 0))
    R[i:i + len(sig)] += sig * (1 + min(pan, 0))


def tt(d):
    return np.arange(int(d * SR)) / SR


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pluck(m, d=0.45):
    t = tt(d)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return s * np.exp(-t * 7) * np.minimum(1, t * 400)


def pad(ms, d):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(2 * np.pi * hz(m) * 1.003 * t) for m in ms)
    env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    return s * env / len(ms)


def kick():
    t = tt(0.35)
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat():
    t = tt(0.06)
    n = rng.standard_normal(len(t))
    return np.diff(n, prepend=0) * np.exp(-t * 70)


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode='same')


def whoosh(d=0.35):
    t = tt(d)
    n = lowpass(rng.standard_normal(len(t)), 6)
    return n * np.sin(np.pi * t / d) ** 2


def pop():
    t = tt(0.08)
    f = 500 + 900 * t / 0.08
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)


def beep():
    t = tt(0.09)
    s = np.sign(np.sin(2 * np.pi * 1760 * t)) * 0.5 + np.sin(2 * np.pi * 1760 * t)
    return s * np.minimum(1, (0.09 - t) * 200)


def chaching():
    t = tt(0.9)
    s = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(2093, 1), (2637, .8), (3136, .6), (4186, .4)])
    clack = lowpass(rng.standard_normal(len(t)), 3) * np.exp(-t * 60)
    return s * np.exp(-t * 5) * 0.4 + clack * 0.8


def sigh():
    t = tt(0.9)
    n = lowpass(rng.standard_normal(len(t)), 30)
    return n * np.sin(np.pi * t / 0.9) ** 1.5 * np.exp(-t * 1.2)


def chime():
    out = np.zeros(int(1.2 * SR))
    for k, m in enumerate([84, 88, 91, 96]):
        s = pluck(m, 0.8)
        i = int(k * 0.07 * SR)
        out[i:i + len(s)] += s
    return out


def click():
    t = tt(0.025)
    return rng.standard_normal(len(t)) * np.exp(-t * 300)


# ---- music: F - G - Em - Am, 120 bpm ----
chords = [[53, 57, 60, 64], [55, 59, 62, 67], [52, 55, 59, 62], [57, 60, 64, 67]]
beat = 0.5
for bar in range(8):
    t0 = bar * 2.0
    ch = chords[bar % 4]
    night = 10.8 <= t0 + 1 < 13.2
    if night:
        add(pad([m + 12 for m in ch], 2.0), t0, 0.22)
    else:
        add(pad([m + 12 for m in ch], 2.0), t0, 0.07)
    add(pluck(ch[0] - 12, 1.2), t0, 0.35)
    for e in range(8):
        tn = t0 + e * 0.25
        if tn >= DUR:
            break
        in_night = 10.8 <= tn < 13.2
        note = ch[[0, 2, 1, 3, 2, 1, 3, 2][e]] + 12
        add(pluck(note), tn, 0.10 if in_night else 0.16, pan=(-.3 if e % 2 else .3))
        if not in_night:
            if e % 2 == 0:
                add(kick(), tn, 0.5)
            else:
                add(hat(), tn, 0.06)

# ---- SFX ----
for t in [3.0, 4.3, 6.0, 7.3, 8.6, 10.8, 13.2]:
    add(whoosh(), t - 0.18, 0.18)
for t in [0.1, 1.4, 3.1, 4.35, 6.05, 7.35, 8.7, 9.7, 10.9, 12.25, 13.25, 13.4]:
    add(pop(), t, 0.25)
add(sigh(), 3.45, 0.35)
for t in [5.0, 6.75, 8.05]:
    add(beep(), t, 0.12)
    add(beep(), t + 0.12, 0.12)
    add(chaching(), t + 0.2, 0.35)
add(chime(), 12.2, 0.4)
for k in range(4):
    add(click(), 13.2 + 0.8 + k * 0.12, 0.25)

mix = np.stack([L, R], axis=1)
fade = np.ones(N)
fade[-int(0.4 * SR):] = np.linspace(1, 0, int(0.4 * SR))
mix *= fade[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.4) * 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('audio ok')
