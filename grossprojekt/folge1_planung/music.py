import numpy as np, wave
SR = 48000; BPM = 120; B = 60 / BPM; DUR = 34.0; DROP = 26.0
N = int(SR * DUR); t = np.arange(N) / SR
out = np.zeros(N)

def env(n, a=0.005, r=0.2):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / (r * SR)); return e

def add(sig, start, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i < N: out[i:j] += sig[: j - i] * gain

def kick():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    f = 50 + 110 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)

def noise_hit(d, hp, r):
    n = int(d * SR); x = np.random.randn(n)
    x = np.diff(np.concatenate([[0], x])) if hp else x
    return x * env(n, 0.001, r)

def saw(f, n):
    tt = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * tt) / k for k in range(1, 9))

def lowpass(x, a):
    from scipy.signal import lfilter
    return lfilter([a], [1, -(1 - a)], x)
def _lp_old(x, a):
    y = np.zeros_like(x); s = 0.0
    for i in range(0, len(x)):
        s += a * (x[i] - s); y[i] = s
    return y

# Am F C G, one bar (2 s) each
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]
roots = [45, 41, 48, 43]
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
bar = 4 * B
pad = np.zeros(N)
for b in range(int(DUR / bar) + 1):
    c = chords[b % 4]; n = int(bar * SR); s = int(b * bar * SR)
    if s >= N: break
    seg = sum(saw(mtof(m), n) for m in c) / 3
    e = np.minimum(1, np.minimum(np.arange(n) / (0.3 * SR), (n - np.arange(n)) / (0.2 * SR)))
    pad[s:s + n] += (seg * e)[: N - s]
# pre-drop: dark filtered pad, post-drop: brighter (approximate with two filters, crossfade)
dark = lowpass(pad, 0.02); bright = lowpass(pad, 0.12)
x = np.clip((t - DROP + 0.1) / 0.2, 0, 1)
padmix = dark * (1 - x) * 0.22 + bright * x * 0.16

# sidechain pump after drop
pump = np.ones(N)
for k in np.arange(DROP, DUR, B):
    i = int(k * SR); n = int(0.35 * SR); j = min(N, i + n)
    pump[i:j] = np.minimum(pump[i:j], 0.35 + 0.65 * (np.arange(j - i) / n) ** 0.6)
out += padmix * pump

K = kick()
for k in np.arange(0, DROP - 2, bar):
    add(K, k, 0.55)                                   # kick on the 1 in intro
for k in np.arange(DROP, DUR - 0.01, B):
    add(K, k, 0.9)                                    # four on the floor
for k in np.arange(DROP + B, DUR, 2 * B):
    add(noise_hit(0.22, False, 0.06) * 0.9 + lowpass(noise_hit(0.22, False, 0.08), 0.3), k, 0.32)  # clap
for k in np.arange(10, DUR, B / 2):
    off = (round((k - 10) / (B / 2)) % 2) == 1
    g = 0.05 if k < DROP else 0.09
    add(noise_hit(0.05, True, 0.012), k, g * (1.3 if off else 0.7))
# rolling bass after drop (8ths, off-beat accent)
for i, k in enumerate(np.arange(DROP, DUR - 0.01, B / 2)):
    r = roots[int((k) / bar) % 4]; n = int(0.22 * SR)
    sig = np.sin(2 * np.pi * mtof(r - 12) * np.arange(n) / SR) + 0.3 * np.sign(np.sin(2 * np.pi * mtof(r - 12) * np.arange(n) / SR))
    add(sig * env(n, 0.003, 0.12), k, 0.20 if i % 2 else 0.12)
# pluck hook after drop
hook = [76, 72, 69, 72, 74, 72, 69, 67]
for i, k in enumerate(np.arange(DROP, DUR - 0.5, B)):
    m = hook[i % 8]; n = int(0.3 * SR); tt = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * mtof(m) * tt) + 0.4 * np.sin(4 * np.pi * mtof(m) * tt)) * env(n, 0.002, 0.09)
    add(sig, k + (B / 2 if i % 4 == 3 else 0), 0.07)
# riser + snare roll before drop
n = int(2.0 * SR); tt = np.arange(n) / SR
rz = np.random.randn(n) * (tt / 2.0) ** 2
add(lowpass(rz, 0.05) * 3 + np.diff(np.concatenate([[0], rz])) * 0.3, DROP - 2.0, 0.25)
k = DROP - 2.0; step = B / 2
while k < DROP - 0.01:
    add(noise_hit(0.08, False, 0.03), k, 0.08 + 0.2 * (k - (DROP - 2)) / 2)
    step = B / 2 if k < DROP - 1 else B / 4
    k += step
# gentle fade end
fade = np.clip((DUR - t) / 0.4, 0, 1); out *= fade
out /= np.max(np.abs(out)) + 1e-9; out *= 0.85
w = wave.open('music.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
print('music ok')
