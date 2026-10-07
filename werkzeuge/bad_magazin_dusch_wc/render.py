import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
GF = '/usr/share/fonts/truetype/google-fonts/'
LORA = GF + 'Lora-Variable.ttf'; LORAI = GF + 'Lora-Italic-Variable.ttf'
OD = '/usr/share/fonts/opentype/inter/'
BLK = OD + 'InterDisplay-Black.otf'; BLD = OD + 'InterDisplay-Bold.otf'; SEM = OD + 'Inter-SemiBold.otf'
DJ = '/usr/share/fonts/truetype/dejavu/'
_fc = {}
def F(p, s, wght=None):
    k = (p, int(s), wght)
    if k not in _fc:
        f = ImageFont.truetype(p, int(s))
        if wght:
            try: f.set_variation_by_axes([wght])
            except Exception: pass
        _fc[k] = f
    return _fc[k]
GREEN = (108, 208, 74); DGREEN = (40, 96, 38); WHITE = (255, 255, 255); INK = (22, 24, 24)
PAPER = (244, 241, 235); GOLD = (198, 164, 98)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eob(x):
    x = clamp(x); c1 = 1.7; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, a, d): return clamp((t - a) / d)
def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]
rng = np.random.default_rng(5)
GRAIN = [rng.normal(0, 3.5, (H, W, 1)).astype(np.float32) for _ in range(4)]

def cover(fn, w, h, zoom=1.12):
    im = Image.open(fn).convert('RGB'); s = max(w * zoom / im.width, h * zoom / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = (im.width - int(w * zoom)) // 2; y = (im.height - int(h * zoom)) // 2
    return im.crop((x, y, x + int(w * zoom), y + int(h * zoom)))
def kb(im, w, h, p, z0=1.0, z1=1.08, pan=(0, 0)):
    z = z0 + (z1 - z0) * p; cw = int(im.width / 1.12 / z); ch = int(im.height / 1.12 / z)
    cx = im.width / 2 + pan[0] * p * 30; cy = im.height / 2 + pan[1] * p * 30
    return im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)).resize((w, h), Image.BILINEAR)

def logo(img, x, y, sc, center=False, dark=False):
    d = ImageDraw.Draw(img)
    f1 = F(DJ + 'DejaVuSans-Bold.ttf', 120 * sc); f2 = F(DJ + 'DejaVuSansCondensed-Bold.ttf', 34 * sc)
    w1 = tw(d, 'Mair', f1); w2 = tw(d, 'GEBÄUDETECHNIK', f2) + int(36 * sc); ww = max(w1, w2)
    if center: x -= ww // 2
    d.text((x + (ww - w1) // 2, y), 'Mair', font=f1, fill=(120, 124, 127) if dark else (232, 234, 236))
    by = y + int(128 * sc)
    d.rounded_rectangle([x, by, x + ww, by + int(48 * sc)], radius=int(8 * sc), fill=GREEN)
    d.text((x + (ww - tw(d, 'GEBÄUDETECHNIK', f2)) // 2, by + int(4 * sc)), 'GEBÄUDETECHNIK', font=f2, fill=WHITE)

def render(frame, dur, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        im = frame(i / FPS); a = np.asarray(im).astype(np.float32) + GRAIN[i % 4]
        p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

# ======================= REEL A: Editorial "Bad aus einer Hand" =======================
B = 60 / 118.0; HB = 2 * B
A_SHOTS = [('bc4d0eb23', 'Lust auf eine', 'begehbare Dusche?'), ('be5a0ff98', 'Mosaik, Regendusche,', 'Thermostat.'),
           ('b8c3473ed', 'Wanne unter', 'der Dachschräge.'), ('b6a435537', 'Großformat', 'in Marmor-Optik.'),
           ('b9bb2d176', 'Doppelwaschtisch', 'mit Licht.'), ('bde6d651d_r', 'Walk-in-Dusche', 'mit Mosaik-Akzent.')]
A_T = [0, 3 * HB] + [3 * HB + i * HB for i in range(1, 6)]   # hook 3 half-bars, then 1 half-bar each
A_CARD = A_T[-1] + HB      # card 1: eigener Fliesenleger
A_END = A_CARD + 3 * HB    # end card
A_DUR = round(A_END + 3.6, 2)
A_IMG = {}
def a_img(k, w, h):
    if (k, w, h) not in A_IMG: A_IMG[(k, w, h)] = cover(k + '.jpg', w, h)
    return A_IMG[(k, w, h)]
FR = 54  # frame border

def a_frame(t):
    img = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(img)
    idx = max([i for i in range(len(A_T)) if t >= A_T[i]] or [0])
    if t < A_CARD:
        k, l1, l2 = A_SHOTS[min(idx, 5)]; t0 = A_T[min(idx, 5)]; dd = (A_T[idx + 1] if idx + 1 < len(A_T) else A_CARD) - t0
        ph = 1180; pw = W - 2 * FR
        im = kb(a_img(k, pw, ph), pw, ph, prog(t, t0, dd + 0.5), 1.0, 1.06, (1 if idx % 2 else -1, 0))
        # slide-in reveal from right
        rp = eo(prog(t, t0, 0.32)) if idx else 1
        x = FR + int((1 - rp) * 300)
        img.paste(im, (x, 330))
        if rp < 1:
            d.rectangle([W - int((1 - rp) * 300) - FR, 330, W, 330 + ph], fill=PAPER)
        # issue line top
        f = F(SEM, 30); d.text((FR, 240), 'MAIR · BAD & FLIESEN', font=f, fill=(120, 116, 108))
        s = f'{min(idx, 5) + 1:02d} / 06'; d.text((W - FR - tw(d, s, f), 240), s, font=f, fill=(120, 116, 108))
        # serif caption
        p1 = eo(prog(t, t0 + 0.08, 0.35)); p2 = eo(prog(t, t0 + 0.2, 0.35))
        big = 92 if idx == 0 else 70
        f1 = F(LORA, big, 600); f2 = F(LORAI, big, 600)
        y0 = 330 + ph + 50
        if p1 > 0: d.text((FR, y0 + int((1 - p1) * 40)), l1, font=f1, fill=INK)
        if p2 > 0:
            d.text((FR, y0 + int(big * 1.15) + int((1 - p2) * 40)), l2, font=f2, fill=DGREEN)
            uw = int(tw(d, l2, f2) * eo(prog(t, t0 + 0.35, 0.4)))
            d.rectangle([FR, y0 + int(big * 2.32), FR + uw, y0 + int(big * 2.32) + 8], fill=GREEN)
    elif t < A_END:
        lt = t - A_CARD
        img.paste(Image.new('RGB', (W, H), INK)); d = ImageDraw.Draw(img)
        # three small photos stacked as background strip
        for i, k in enumerate(['bf3dafa0e', 'b04ef2100', 'be8a74be4']):
            p = eo(prog(lt, 0.05 + i * 0.12, 0.4))
            if p <= 0: continue
            im = kb(a_img(k, 300, 420), 300, 420, 0.3)
            im = Image.fromarray((np.asarray(im) * 0.75).astype(np.uint8))
            img.paste(im, (FR + i * 330, 260 + int((1 - p) * 120)))
        lines = [('Wir fliesen', LORA, WHITE), ('und montieren.', LORA, WHITE), ('Mit eigenem', LORAI, GREEN), ('Fliesenleger.', LORAI, GREEN)]
        for i, (s, fp, c) in enumerate(lines):
            p = eo(prog(lt, 0.3 + i * 0.18, 0.35))
            if p > 0: d.text((FR, 780 + i * 128 + int((1 - p) * 40)), s, font=F(fp, 112, 700), fill=c)
        p = eo(prog(lt, 1.4, 0.35))
        if p > 0:
            f = F(SEM, 40); s = 'Kein Subunternehmer. Unser Team.'
            d.text((FR, 1330 + int((1 - p) * 20)), s, font=f, fill=(200, 200, 196))
    else:
        lt = t - A_END
        bg = kb(a_img('b6a435537', W, H), W, H, prog(t, A_END, 4), 1.0, 1.05)
        bg = bg.filter(ImageFilter.GaussianBlur(14)); bg = Image.fromarray((np.asarray(bg) * 0.35).astype(np.uint8))
        img.paste(bg); d = ImageDraw.Draw(img)
        p = eob(prog(lt, 0, 0.4))
        if p > 0:
            lay = Image.new('RGBA', (W, 400), (0, 0, 0, 0)); logo(lay, W // 2, 30, 1.0 * p + 1e-4, center=True); img.paste(lay, (0, 280), lay)
        for i, s in enumerate(['Bad + Sanitär', 'aus einer Hand.']):
            p = eo(prog(lt, 0.3 + i * 0.15, 0.35))
            if p > 0:
                f = F(LORA, 100, 700) if i == 0 else F(LORAI, 100, 700)
                d.text(((W - tw(d, s, f)) // 2, 720 + i * 120 + int((1 - p) * 30)), s, font=f, fill=WHITE if i == 0 else GREEN)
        items = ['Eigener Fliesenleger', 'Eigene Badausstellung in Aurachtal', 'Sanitär, Fliesen und Montage']
        for i, s in enumerate(items):
            p = eo(prog(lt, 0.9 + i * 0.18, 0.3))
            if p > 0:
                f = F(SEM, 42); y = 1010 + i * 72
                d.text((FR + 120 + int((1 - p) * 30), y), '✓  ' + s, font=f, fill=WHITE)
        p = eob(prog(lt, 1.6, 0.35))
        if p > 0:
            f = F(BLK, 62); s = 'Kommentiere BAD'; w = tw(d, s, f); x = (W - w) // 2; y = 1270
            d.rounded_rectangle([x - 34, y - 12, x + w + 34, y + 86], radius=48, fill=GREEN); d.text((x, y), s, font=f, fill=INK)
            f2 = F(BLD, 44); s2 = '09132 / 74 97 5-27'; d.text(((W - tw(d, s2, f2)) // 2, 1400), s2, font=f2, fill=WHITE)
    # cut flash
    for c in A_T[1:] + [A_CARD, A_END]:
        if 0 <= t - c < 0.1:
            a = np.asarray(img).astype(np.float32); img = Image.fromarray(np.clip(a + 255 * 0.3 * (1 - (t - c) / 0.1), 0, 255).astype(np.uint8))
    if t > A_DUR - 0.4:
        img = Image.blend(img, a_frame(0.0), (t - (A_DUR - 0.4)) / 0.4)
    return img

# ======================= REEL B: Dusch-WC (dark luxury) =======================
B_DUR = 13.0
FEAT = [('Warmwasser-Dusche', '5 Druckstufen'), ('Ladydusche', 'extra sanfter Strahl'), ('Warmluft-Föhn', 'Temperatur einstellbar'),
        ('Geruchsabsaugung', 'mit Keramikfilter'), ('Spülrandlos', 'leicht zu putzen')]
BWC = cover('b625344f4.jpg', W, H); BWC2 = cover('bf97d34de.jpg', W, H)
def b_frame(t):
    img = Image.new('RGB', (W, H), (12, 14, 14)); d = ImageDraw.Draw(img)
    if t < 3.2:
        im = kb(BWC2, W, H, prog(t, 0, 3.6), 1.12, 1.0)
        a = np.asarray(im).astype(np.float32); yy = np.linspace(0, 1, H)[:, None, None]
        a *= (0.55 + 0.25 * (1 - yy)); img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        for i, (s, fp, c) in enumerate([('Dein WC', LORA, WHITE), ('kann mehr.', LORAI, GREEN)]):
            p = eob(prog(t, 0.1 + i * 0.35, 0.35))
            if p > 0:
                f = F(fp, int(140 * (0.7 + 0.3 * p)), 700); w = tw(d, s, f)
                d.text(((W - w) // 2 + 4, 700 + i * 170 + 4), s, font=f, fill=(0, 0, 0)); d.text(((W - w) // 2, 700 + i * 170), s, font=f, fill=c)
        p = eo(prog(t, 1.3, 0.35))
        if p > 0:
            f = F(SEM, 46); s = 'Schon mal ein Dusch-WC probiert?'
            d.text(((W - tw(d, s, f)) // 2, 1080 + int((1 - p) * 30)), s, font=f, fill=WHITE)
    elif t < 9.8:
        lt = t - 3.2
        im = kb(BWC, W, H, prog(lt, 0, 7), 1.0, 1.1, (1, 1))
        im = im.filter(ImageFilter.GaussianBlur(3)); a = np.asarray(im).astype(np.float32) * 0.42
        img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
        f = F(LORA, 76, 700); s = 'Was ein Dusch-WC kann:'
        d.text((70, 300), s, font=f, fill=WHITE)
        f3 = F(SEM, 34); s3 = 'z. B. Geberit AquaClean Mera'
        d.text((72, 404), s3, font=f3, fill=GOLD)
        for i, (a1, a2) in enumerate(FEAT):
            p = eo(prog(lt, 0.4 + i * 0.95, 0.35))
            if p <= 0: continue
            y = 520 + i * 182; x = 70 + int((1 - p) * -500)
            d.rounded_rectangle([x, y, x + 940, y + 152], radius=22, fill=(250, 250, 248))
            d.ellipse([x + 30, y + 41, x + 100, y + 111], fill=GREEN); d.text((x + 48, y + 46), '✓', font=F(DJ + 'DejaVuSans-Bold.ttf', 50), fill=WHITE)
            d.text((x + 130, y + 22), a1, font=F(BLK, 56), fill=INK); d.text((x + 132, y + 92), a2, font=F(SEM, 34), fill=DGREEN)
    else:
        lt = t - 9.8
        bg = BWC.resize((W, H)).filter(ImageFilter.GaussianBlur(16)); img = Image.fromarray((np.asarray(bg) * 0.3).astype(np.uint8)); d = ImageDraw.Draw(img)
        p = eob(prog(lt, 0, 0.4))
        if p > 0:
            lay = Image.new('RGBA', (W, 400), (0, 0, 0, 0)); logo(lay, W // 2, 30, p + 1e-4, center=True); img.paste(lay, (0, 330), lay)
        for i, (s, fp, c) in enumerate([('Wir bauen es ein.', LORA, WHITE), ('Inklusive Fliesen.', LORAI, GREEN)]):
            p = eo(prog(lt, 0.3 + i * 0.2, 0.35))
            if p > 0:
                f = F(fp, 86, 700); d.text(((W - tw(d, s, f)) // 2, 760 + i * 110 + int((1 - p) * 30)), s, font=f, fill=c)
        p = eob(prog(lt, 1.0, 0.35))
        if p > 0:
            f = F(BLK, 62); s = 'Kommentiere WC'; w = tw(d, s, f); x = (W - w) // 2; y = 1060
            d.rounded_rectangle([x - 34, y - 12, x + w + 34, y + 86], radius=48, fill=GREEN); d.text((x, y), s, font=f, fill=INK)
            f2 = F(BLD, 42); s2 = 'Beratung in unserer Badausstellung'; d.text(((W - tw(d, s2, f2)) // 2, 1190), s2, font=f2, fill=WHITE)
            s3 = '09132 / 74 97 5-27'; d.text(((W - tw(d, s3, f2)) // 2, 1250), s3, font=f2, fill=WHITE)
    for c in (3.2, 9.8):
        if 0 <= t - c < 0.1:
            a = np.asarray(img).astype(np.float32); img = Image.fromarray(np.clip(a + 255 * 0.35 * (1 - (t - c) / 0.1), 0, 255).astype(np.uint8))
    if t > B_DUR - 0.4: img = Image.blend(img, b_frame(0.0), (t - (B_DUR - 0.4)) / 0.4)
    return img

if __name__ == '__main__':
    which = sys.argv[1]
    fr, dur = (a_frame, A_DUR) if which == 'A' else (b_frame, B_DUR)
    if sys.argv[2] == 'still':
        for s in sys.argv[3:]: fr(float(s)).save(f'{which}_{s}.jpg', quality=85)
    elif sys.argv[2] == 'info': print(dur, A_T, A_CARD, A_END)
    else: render(fr, dur, sys.argv[2])
