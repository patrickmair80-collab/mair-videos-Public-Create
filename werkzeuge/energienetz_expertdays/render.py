import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BPM = 125.0; B = 60 / BPM; BAR = 4 * B; HB = 2 * B
# scene starts (half-bar grid)
T = [0, 3 * HB, 5 * HB, 7 * HB, 9 * HB, 11 * HB, 13 * HB, 19 * HB, 23 * HB]
DROP = T[6]
DUR = round(23 * HB + 4.0, 2)
OD = '/usr/share/fonts/opentype/inter/'
BLK = OD + 'InterDisplay-Black.otf'; BLD = OD + 'InterDisplay-Bold.otf'; SEM = OD + 'Inter-SemiBold.otf'
DJ = '/usr/share/fonts/truetype/dejavu/'
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]

GREEN = (108, 208, 74); DGREEN = (46, 107, 42); WHITE = (255, 255, 255); INK = (12, 18, 16)
VOLT = (255, 214, 64); NIGHT = (8, 14, 22)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eob(x):
    x = clamp(x); c1 = 1.7; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, a, d): return clamp((t - a) / d)
def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def load(fn, zoom=1.14):
    im = Image.open(fn).convert('RGB')
    w, h = im.size; tw_ = int(W * zoom); th = int(H * zoom)
    s = max(tw_ / w, th / h); im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    x = (im.width - tw_) // 2; y = (im.height - th) // 2
    return im.crop((x, y, x + tw_, y + th))
P = {k: load(k + '.jpg') for k in ['hall', 'wall', 'wp', 'e3dc', 'pv', 'klima', 'agenda', 'badge']}
def dark(im, f=0.45, blur=0):
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im).astype(np.float32) * f
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
AG_BG = dark(P['agenda'].resize((W, H)), 0.32, 18)
BADGE_BG = dark(P['badge'].resize((W, H)), 0.30, 22)

yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.55 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2, 0, 1))[..., None].astype(np.float32)
GRAD = np.clip((yy - H * 0.55) / (H * 0.45), 0, 1)[..., None].astype(np.float32)
rng = np.random.default_rng(3)
GRAIN = [rng.normal(0, 4, (H, W, 1)).astype(np.float32) for _ in range(4)]

def kb(name, t, t0, d, z0=1.0, z1=1.08, pan=(0, 0)):
    im = P[name]; p = clamp((t - t0) / d)
    z = z0 + (z1 - z0) * p
    if t >= DROP:  # beat punch
        ph = ((t - DROP) % B) / B; z *= 1 + 0.028 * math.exp(-ph * 7)
    cw = int(im.width / z / 1.14 * 1.0); ch = int(im.height / z / 1.14)
    cx = im.width / 2 + pan[0] * p * 40; cy = im.height / 2 + pan[1] * p * 40
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)
    return im.crop(box).resize((W, H), Image.BILINEAR)

def logo(img, x, y, sc, center=False):
    d = ImageDraw.Draw(img)
    f1 = F(DJ + 'DejaVuSans-Bold.ttf', 120 * sc); f2 = F(DJ + 'DejaVuSansCondensed-Bold.ttf', 34 * sc)
    w1 = tw(d, 'Mair', f1); w2 = tw(d, 'GEBÄUDETECHNIK', f2) + int(36 * sc); ww = max(w1, w2)
    if center: x -= ww // 2
    d.text((x + (ww - w1) // 2, y), 'Mair', font=f1, fill=(230, 233, 235))
    by = y + int(128 * sc)
    d.rounded_rectangle([x, by, x + ww, by + int(48 * sc)], radius=int(8 * sc), fill=GREEN)
    d.text((x + (ww - tw(d, 'GEBÄUDETECHNIK', f2)) // 2, by + int(4 * sc)), 'GEBÄUDETECHNIK', font=f2, fill=WHITE)

def slam(img, lines, t, t0, y, size=118, hl=None):
    """lines appear one by one with scale-pop; hl = index of line on green box"""
    d = ImageDraw.Draw(img)
    for i, s in enumerate(lines):
        a = t0 + i * 0.22; p = prog(t, a, 0.28)
        if p <= 0: continue
        sc = 0.6 + 0.4 * eob(p)
        f = F(BLK, size * sc); w = tw(d, s, f)
        yy_ = y + i * int(size * 1.08) + int((1 - sc) * size * 0.5)
        x = (W - w) // 2
        if hl == i:
            pad = 22; d.rounded_rectangle([x - pad, yy_ - 4, x + w + pad, yy_ + int(size * sc * 1.05)], radius=14, fill=GREEN)
            d.text((x, yy_ - int(size * sc * 0.12)), s, font=f, fill=INK)
        else:
            d.text((x + 5, yy_ - int(size * sc * 0.12) + 6), s, font=f, fill=(0, 0, 0))
            d.text((x, yy_ - int(size * sc * 0.12)), s, font=f, fill=WHITE)

def chip(img, label, sub, t, t0):
    d = ImageDraw.Draw(img); p = eo(prog(t, t0 + 0.15, 0.35))
    if p <= 0: return
    f1 = F(BLK, 74); f2 = F(SEM, 40)
    x0 = int(-700 + p * 770); y0 = 1250
    w = max(tw(d, label, f1), tw(d, sub, f2)) + 80
    d.rounded_rectangle([x0, y0, x0 + w, y0 + 200], radius=26, fill=(10, 16, 14, 255))
    d.rectangle([x0, y0 + 20, x0 + 12, y0 + 180], fill=GREEN)
    d.text((x0 + 44, y0 + 22), label, font=f1, fill=WHITE)
    d.text((x0 + 46, y0 + 122), sub, font=f2, fill=GREEN)

def bolt(d, cx, cy, s, col):
    pts = [(0, -1), (-0.45, 0.1), (-0.05, 0.1), (-0.25, 1), (0.45, -0.15), (0.05, -0.15), (0.25, -1)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=col)

def energy_bar(img, t):
    """progress line with lightning that runs through the whole reel"""
    d = ImageDraw.Draw(img); p = clamp(t / (DUR - 0.4))
    y = 1490
    d.rounded_rectangle([60, y, W - 60, y + 10], radius=5, fill=(255, 255, 255, 60) if False else (60, 70, 70))
    x = 60 + int((W - 120) * p)
    d.rounded_rectangle([60, y, x, y + 10], radius=5, fill=GREEN)
    bolt(d, x, y + 5, 26, VOLT)

def tag(img, t):
    d = ImageDraw.Draw(img); f = F(BLD, 30)
    s = 'MEMODO EXPERT DAYS 2026'
    d.rounded_rectangle([60, 250, 60 + tw(d, s, f) + 44, 304], radius=27, fill=(10, 16, 14))
    d.ellipse([80, 268, 98, 286], fill=(235, 60, 50) if int(t * 2) % 2 == 0 else (120, 30, 25))
    d.text((112, 258), s, font=f, fill=WHITE)

# ---------- network scene ----------
NODES = [('PV-ANLAGE', (540, 560), 'sun'), ('SPEICHER', (230, 900), 'bat'), ('WÄRMEPUMPE', (850, 900), 'wp'),
         ('KLIMA', (230, 1260), 'ac'), ('E-AUTO', (850, 1260), 'car')]
HOUSE = (540, 1080)
def icon(d, kind, cx, cy, s, col):
    if kind == 'sun':
        d.ellipse([cx - s * .45, cy - s * .45, cx + s * .45, cy + s * .45], fill=VOLT)
        for k in range(8):
            a = k * math.pi / 4; d.line([(cx + math.cos(a) * s * .6, cy + math.sin(a) * s * .6), (cx + math.cos(a) * s * .85, cy + math.sin(a) * s * .85)], fill=VOLT, width=int(s * .1))
    elif kind == 'bat':
        d.rounded_rectangle([cx - s * .35, cy - s * .55, cx + s * .35, cy + s * .55], radius=int(s * .08), outline=col, width=int(s * .08))
        d.rectangle([cx - s * .12, cy - s * .68, cx + s * .12, cy - s * .55], fill=col)
        bolt(d, cx, cy, s * .32, VOLT)
    elif kind == 'wp':
        d.rounded_rectangle([cx - s * .6, cy - s * .45, cx + s * .6, cy + s * .45], radius=int(s * .1), outline=col, width=int(s * .08))
        d.ellipse([cx - s * .45, cy - s * .32, cx + s * .19, cy + s * .32], outline=col, width=int(s * .07))
    elif kind == 'ac':
        d.rounded_rectangle([cx - s * .65, cy - s * .3, cx + s * .65, cy + s * .2], radius=int(s * .1), outline=col, width=int(s * .08))
        for k in range(3): d.line([(cx - s * .4 + k * s * .4, cy + s * .35), (cx - s * .5 + k * s * .4, cy + s * .6)], fill=col, width=int(s * .07))
    elif kind == 'car':
        d.rounded_rectangle([cx - s * .65, cy - s * .1, cx + s * .65, cy + s * .35], radius=int(s * .12), outline=col, width=int(s * .08))
        d.polygon([(cx - s * .4, cy - s * .1), (cx - s * .2, cy - s * .4), (cx + s * .25, cy - s * .4), (cx + s * .45, cy - s * .1)], outline=col)
        d.line([(cx - s * .4, cy - s * .1), (cx - s * .2, cy - s * .4), (cx + s * .25, cy - s * .4), (cx + s * .45, cy - s * .1)], fill=col, width=int(s * .08))
        for ox in (-.38, .38): d.ellipse([cx + s * ox - s * .14, cy + s * .25, cx + s * ox + s * .14, cy + s * .53], fill=col)

def house(d, cx, cy, s, col, glow):
    if glow > 0:
        r = s * (1.0 + 0.3 * glow)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(int(108 * glow * .25), int(208 * glow * .25), int(74 * glow * .25)))
    d.polygon([(cx - s * .7, cy - s * .05), (cx, cy - s * .7), (cx + s * .7, cy - s * .05)], fill=col)
    d.rectangle([cx - s * .52, cy - s * .08, cx + s * .52, cy + s * .62], fill=col)
    d.rectangle([cx - s * .14, cy + s * .2, cx + s * .14, cy + s * .62], fill=NIGHT)

def s_net(img, t):
    t0 = DROP; lt = t - t0
    a = np.zeros((H, W, 3), np.float32) + np.array(NIGHT, np.float32)
    g = np.exp(-(((xx - 540) / 600.0) ** 2 + ((yy - 1000) / 700.0) ** 2))[..., None]
    a += g * np.array([10, 40, 30], np.float32)
    img.paste(Image.fromarray(a.astype(np.uint8)))
    d = ImageDraw.Draw(img)
    # grid dots
    for gy in range(420, 1500, 60):
        for gx in range(60, 1040, 60): d.point((gx, gy), fill=(30, 52, 44))
    # lines
    for i, (lab, (nx, ny), k) in enumerate(NODES):
        a0 = 0.35 + i * 0.32; p = eo(prog(lt, a0, 0.45))
        if p <= 0: continue
        ex = nx + (HOUSE[0] - nx) * p; ey = ny + (HOUSE[1] - ny) * p
        d.line([(nx, ny), (ex, ey)], fill=(50, 110, 60), width=10)
        if p >= 1:
            bidir = k in ('car', 'bat')
            for j in range(3):
                q = ((lt * 0.9 + j / 3.0) % 1.0)
                if k == 'sun' or (bidir and j % 2 == 0) or k in ('bat',) and False:
                    fx, fy = nx + (HOUSE[0] - nx) * q, ny + (HOUSE[1] - ny) * q
                elif bidir:
                    fx, fy = HOUSE[0] + (nx - HOUSE[0]) * q, HOUSE[1] + (ny - HOUSE[1]) * q
                else:
                    fx, fy = HOUSE[0] + (nx - HOUSE[0]) * q, HOUSE[1] + (ny - HOUSE[1]) * q
                d.ellipse([fx - 11, fy - 11, fx + 11, fy + 11], fill=VOLT if k == 'sun' else GREEN)
    # house
    hp = eob(prog(lt, 0.0, 0.4))
    if hp > 0:
        glow = 0.5 + 0.5 * math.sin(lt * 6) if lt > 2.0 else 0
        house(d, HOUSE[0], HOUSE[1], 130 * hp, WHITE, glow)
    # nodes
    for i, (lab, (nx, ny), k) in enumerate(NODES):
        p = eob(prog(lt, 0.2 + i * 0.32, 0.35))
        if p <= 0: continue
        r = 92 * p
        d.ellipse([nx - r, ny - r, nx + r, ny + r], fill=(14, 26, 22), outline=GREEN, width=6)
        icon(d, k, nx, ny, 100 * p, WHITE)
        f = F(BLD, 34); w = tw(d, lab, f)
        if p > 0.9: d.text((nx - w // 2, ny + 104), lab, font=f, fill=WHITE)
        if k in ('car', 'bat') and p > 0.9 and lt > 2.2:
            f2 = F(SEM, 26); s2 = 'bidirektional' if k == 'car' else 'speichert & gibt ab'
            d.text((nx - tw(d, s2, f2) // 2, ny + 146), s2, font=f2, fill=VOLT)
    # titles
    slam(img, ['Sonnenstrom zuerst', 'in DEIN Haus.'], t, t0 + 0.1, 300, 92, hl=1)
    p2 = prog(lt, 3.0, 0.35)
    if p2 > 0:
        f = F(BLK, 64); s = 'Automatisch gesteuert.'
        dd = ImageDraw.Draw(img); w = tw(dd, s, f); y = 1560 + int((1 - eo(p2)) * 60)
        dd.text(((W - w) // 2, y), s, font=f, fill=WHITE)
        f3 = F(SEM, 38); s3 = 'Smart-Home-Energiemanagement'
        dd.text(((W - tw(dd, s3, f3)) // 2, y + 84), s3, font=f3, fill=GREEN)

# ---------- speakers ----------
SPK = [('Prof. Timo Leukefeld', '„Intelligent verschwenden“'), ('Hans-Josef Fell', '„Das EEG und die Energie der Zukunft“'), ('Max Glas', '„KI im Handwerk: Hype oder Gamechanger?“')]
def s_spk(img, t):
    t0 = T[7]; lt = t - t0
    z = 1 + 0.03 * prog(t, t0, 4)
    bg = AG_BG.resize((int(W * z), int(H * z))); ox = (bg.width - W) // 2; img.paste(bg.crop((ox, ox, ox + W, ox + H)))
    slam(img, ['Das hat uns', 'heute begleitet:'], t, t0 + 0.05, 330, 90, hl=None)
    d = ImageDraw.Draw(img)
    for i, (n, topic) in enumerate(SPK):
        p = eo(prog(lt, 0.5 + i * 0.45, 0.4))
        if p <= 0: continue
        y = 620 + i * 250; x = int(W + 40 - p * (W - 60 + 40))
        d.rounded_rectangle([x, y, x + W - 120, y + 210], radius=24, fill=(250, 252, 250))
        d.rectangle([x, y + 24, x + 14, y + 186], fill=GREEN)
        d.text((x + 48, y + 34), n, font=F(BLK, 56), fill=INK)
        d.text((x + 50, y + 118), topic, font=F(SEM, 36), fill=DGREEN)
    p = eo(prog(lt, 2.1, 0.4))
    if p > 0:
        f = F(BLD, 44); s = '+ 38 Hersteller an einem Ort'
        d.text(((W - tw(d, s, f)) // 2, 1400 + int((1 - p) * 40)), s, font=f, fill=VOLT)

# ---------- end ----------
def s_end(img, t):
    t0 = T[8]; lt = t - t0
    img.paste(BADGE_BG)
    d = ImageDraw.Draw(img)
    p = eob(prog(lt, 0.0, 0.4))
    if p > 0:
        im2 = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); logo(im2, W // 2, 40, 1.05 * p + 0.0001, center=True)
        img.paste(im2, (0, 300), im2)
    slam(img, ['Wir verknüpfen', 'das bei dir.'], t, t0 + 0.35, 700, 96, hl=1)
    p = eo(prog(lt, 1.0, 0.4))
    if p > 0:
        f = F(SEM, 40); s = 'PV · Speicher · Wärmepumpe · Klima'
        d.text(((W - tw(d, s, f)) // 2, 960 + int((1 - p) * 30)), s, font=f, fill=WHITE)
    p = eob(prog(lt, 1.5, 0.35))
    if p > 0:
        f = F(BLK, 64); s = 'Kommentiere SMART'
        w = tw(d, s, f); x = (W - w) // 2; y = 1110
        d.rounded_rectangle([x - 30, y - 10, x + w + 30, y + 90], radius=45, fill=VOLT)
        d.text((x, y), s, font=f, fill=INK)
        f2 = F(BLD, 46); s2 = '09132 / 74 97 5-27'
        d.text(((W - tw(d, s2, f2)) // 2, 1250), s2, font=f2, fill=WHITE)

# ---------- photo scenes ----------
SC = [('hall', None), ('wall', ('EXPERT DAYS', '38 Hersteller · 1 Thema')), ('wp', ('WÄRMEPUMPE', 'heizt mit Sonnenstrom')),
      ('e3dc', ('SPEICHER + WALLBOX', 'Hauskraftwerk fürs Haus')), ('pv', ('PV-ANLAGE', 'sogar in Terrakotta-Rot')), ('klima', ('KLIMA', 'kühlt & heizt mit PV'))]
PANS = [(0, -1), (1, 0), (-1, 0), (0, 1), (1, 1), (-1, 0)]

def frame(t):
    img = Image.new('RGB', (W, H), NIGHT)
    idx = max(i for i in range(len(T)) if t >= T[i] - 1e-9)
    if idx <= 5:
        name, ch = SC[idx]; t0 = T[idx]; d_ = T[idx + 1] - t0
        img.paste(kb(name, t, t0, d_, 1.0, 1.07 if idx else 1.12, PANS[idx]))
        a = np.asarray(img).astype(np.float32)
        a = a * VIG * (1 - 0.55 * GRAD)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        if idx == 0:
            slam(img, ['Energie', 'verschwenden?'], t, 0.05, 620, 104)
            if t > 1.35:
                slam(img, ['Ja. Aber', 'intelligent.'], t, 1.35, 900, 112, hl=1)
        else:
            chip(img, ch[0], ch[1], t, t0)
        tag(img, t)
    elif idx == 6: s_net(img, t)
    elif idx == 7: s_spk(img, t)
    else: s_end(img, t)
    energy_bar(img, t)
    # cut flash
    for c in T[1:]:
        dt = t - c
        if 0 <= dt < 0.12:
            a = np.asarray(img).astype(np.float32); k = (1 - dt / 0.12) * (0.85 if c == DROP else 0.35)
            img = Image.fromarray(np.clip(a + 255 * k, 0, 255).astype(np.uint8))
    # drop shake
    if 0 <= t - DROP < 0.35:
        s = int(16 * (1 - (t - DROP) / 0.35)); img = img.transform((W, H), Image.AFFINE, (1, 0, s * math.sin(t * 90), 0, 1, s * math.cos(t * 77)))
    # loop: last 0.4s blend to first frame
    if t > DUR - 0.4:
        k = (t - (DUR - 0.4)) / 0.4
        img = Image.blend(img, frame0(), k)
    a = np.asarray(img).astype(np.float32) + GRAIN[int(t * FPS) % 4]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

_f0 = []
def frame0():
    if not _f0:
        im = Image.new('RGB', (W, H)); im.paste(kb('hall', 0, 0, 1, 1.0, 1.12, PANS[0]))
        a = np.asarray(im).astype(np.float32) * VIG * (1 - 0.55 * GRAD); _f0.append(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    return _f0[0]

def render(a, b, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(int(round(a * FPS)), int(round(b * FPS))):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for s in sys.argv[2:]: frame(float(s)).save(f'still_{s}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(T, DROP, DUR)
    else: render(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3])
