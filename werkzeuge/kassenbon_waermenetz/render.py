import sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 42.0
FD = '/usr/share/fonts/truetype/'
HB = FD + 'dejavu/DejaVuSansCondensed-Bold.ttf'
HR = FD + 'dejavu/DejaVuSansCondensed.ttf'
MB = FD + 'dejavu/DejaVuSansMono-Bold.ttf'
MR = FD + 'dejavu/DejaVuSansMono.ttf'
SI = FD + 'crosextra/Caladea-Italic.ttf'
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]

# palette: cool paper, ink, Mair green, heat red, oil brown
PAPER = (236, 239, 235); INK = (21, 25, 28); GREY = (110, 117, 120); LGREY = (190, 196, 196)
GREEN = (93, 179, 58); DGREEN = (52, 128, 33); RED = (210, 65, 47); OIL = (74, 58, 46)
WHITE = (255, 255, 255); MARK = (255, 226, 92)

SC = [0, 5, 10, 15, 21, 28, 32, 38, 42]
DROP = 28.0

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eob(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, a, d): return clamp((t - a) / d)

# ---------- static background ----------
rng = np.random.default_rng(3)
base = np.zeros((H, W, 3), np.float32) + np.array(PAPER, np.float32)
yy, xx = np.mgrid[0:H, 0:W]
vig = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
base *= (1 - 0.10 * vig)[..., None]
GRAIN = [rng.normal(0, 4.0, (H, W, 1)).astype(np.float32) for _ in range(4)]
BG = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]
def ctext(d, y, s, f, fill, cx=W // 2):
    d.text((cx - tw(d, s, f) // 2, y), s, font=f, fill=fill)

def logo(img, x, y, sc, center=False):
    d = ImageDraw.Draw(img)
    f1 = F(FD + 'dejavu/DejaVuSans-Bold.ttf', 120 * sc); f2 = F(HB, 34 * sc)
    w1 = tw(d, 'Mair', f1); w2 = tw(d, 'GEBÄUDETECHNIK', f2) + int(36 * sc)
    ww = max(w1, w2)
    if center: x = x - ww // 2
    d.text((x + (ww - w1) // 2, y), 'Mair', font=f1, fill=(132, 136, 139))
    by = y + int(128 * sc)
    d.rounded_rectangle([x, by, x + ww, by + int(48 * sc)], radius=int(8 * sc), fill=GREEN)
    d.text((x + (ww - tw(d, 'GEBÄUDETECHNIK', f2)) // 2, by + int(4 * sc)), 'GEBÄUDETECHNIK', font=f2, fill=WHITE)
    return ww

def header(img, d, t):
    logo(img, 60, 262, 0.42)
    f = F(MB, 24); s = 'KOSTENCHECK · 10/2026'
    d.text((930 - tw(d, s, f), 290), s, font=f, fill=GREY)
    d.line([(60, 352), (930, 352)], fill=LGREY, width=2)

FINE = ['Beispiel, brutto: 17.000 kWh/Jahr, 10 kW · Heizöl 1,64 €/l (Bayern,',
        '05.10.2026) · Wärmenetz Paket S, Preisblatt 2026 · WP-Strom 25 ct,',
        'JAZ 3,5 · Förderung 46 % (KfW 458) · Richtwerte, keine Gewähr']
def fineprint(d):
    f = F(MR, 22)
    for i, s in enumerate(FINE): d.text((60, 1418 + i * 30), s, font=f, fill=GREY)

def padlock(d, cx, cy, s, col, open_=0.0, width=14):
    bw, bh = 150 * s, 120 * s
    d.rounded_rectangle([cx - bw / 2, cy, cx + bw / 2, cy + bh], radius=18 * s, fill=col)
    lift = 45 * s * open_
    r = 48 * s
    box = [cx - r, cy - r - 30 * s - lift, cx + r, cy + r - 30 * s - lift]
    d.arc(box, 180, 360, fill=col, width=int(width * s))
    d.line([(cx - r + 7 * s, cy - 30 * s - lift), (cx - r + 7 * s, cy + 6 * s)], fill=col, width=int(width * s))
    if open_ < 0.5:
        d.line([(cx + r - 7 * s, cy - 30 * s - lift), (cx + r - 7 * s, cy + 6 * s)], fill=col, width=int(width * s))
    d.ellipse([cx - 14 * s, cy + 40 * s, cx + 14 * s, cy + 68 * s], fill=PAPER)
    d.rectangle([cx - 5 * s, cy + 60 * s, cx + 5 * s, cy + 92 * s], fill=PAPER)

_stc = {}
def stamp(img, cx, cy, text, col, p, ang=-12):
    if p <= 0: return
    key = (text, col)
    if key not in _stc:
        f = F(HB, 74); tmp = ImageDraw.Draw(img)
        w = tw(tmp, text, f) + 70; h = 120
        s = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
        sd.rounded_rectangle([5, 5, w - 5, h - 5], radius=14, outline=col + (235,), width=9)
        sd.text((35, 14), text, font=f, fill=col + (235,))
        a = np.array(s); m = rng.random(a.shape[:2]) < 0.12; a[m, 3] = (a[m, 3] * 0.35).astype(np.uint8)
        _stc[key] = Image.fromarray(a).rotate(ang, expand=True, resample=Image.BICUBIC)
    s = _stc[key]; sc = 1 + 1.2 * (1 - eo(p * 1.0))
    if sc != 1: s = s.resize((int(s.width * sc), int(s.height * sc)), Image.BICUBIC)
    a = clamp(p * 3)
    if a < 1:
        s = s.copy(); al = np.array(s.split()[3], np.float32) * a; s.putalpha(Image.fromarray(al.astype(np.uint8)))
    img.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)

# ---------- receipt ----------
_shadow = {}
def receipt(img, t, t0, title, col, items, total, total_s, line_dt=0.42, stamp_t=None, stamp_txt='', stamp_col=RED, h=900, st_y=600):
    x0, w = 150, 780
    p_in = eo(prog(t, t0, 0.45))
    y0 = int(-h + (h + 400) * p_in)
    if (w, h) not in _shadow:
        sh = Image.new('L', (w + 80, h + 80), 0); ImageDraw.Draw(sh).rectangle([40, 50, w + 40, h + 40], fill=90)
        _shadow[(w, h)] = sh.filter(ImageFilter.GaussianBlur(18))
    img.paste((40, 44, 46), (x0 - 40, y0 - 40), _shadow[(w, h)])
    d = ImageDraw.Draw(img)
    zz = [(x0, y0), (x0 + w, y0)]
    n = 26
    for i in range(n + 1):
        zz.append((x0 + w - i * w / n, y0 + h + (0 if i % 2 else 14)))
    d.polygon(zz, fill=WHITE)
    # printer slot
    d.rectangle([110, 372, 970, 400], fill=INK)
    d.rectangle([130, 396, 950, 404], fill=(60, 64, 66))
    x = x0 + 44; y = y0 + 40
    d.rectangle([x, y + 10, x + 30, y + 40], fill=col)
    d.text((x + 46, y - 4), title, font=F(HB, 58), fill=INK)
    y += 78
    d.text((x, y), 'KOSTEN PRO JAHR · BEISPIELHAUS', font=F(MR, 22), fill=GREY)
    y += 44
    for xx_ in range(x, x0 + w - 44, 18): d.line([(xx_, y), (xx_ + 9, y)], fill=LGREY, width=2)
    y += 26
    tl = t0 + 0.55
    for i, (lab, sub, val) in enumerate(items):
        pi = prog(t, tl + i * line_dt, line_dt * 0.8)
        if pi <= 0: break
        s = lab[: max(1, int(len(lab) * min(1, pi * 1.6)))]
        d.text((x, y), s, font=F(MR, 31), fill=INK)
        if pi > 0.45:
            vf = F(MB, 33); d.text((x0 + w - 44 - tw(d, val, vf), y - 1), val, font=vf, fill=INK)
        if sub and pi > 0.3:
            d.text((x, y + 40), sub, font=F(MR, 22), fill=GREY)
        y += 86 if sub else 58
    tt = tl + len(items) * line_dt
    y = max(y, y0 + h - 210)
    if t >= tt:
        d.line([(x, y), (x0 + w - 44, y)], fill=INK, width=3); d.line([(x, y + 8), (x0 + w - 44, y + 8)], fill=INK, width=3)
        d.text((x, y + 40), 'GESAMT', font=F(MB, 30), fill=GREY)
        d.text((x, y + 76), 'pro Jahr', font=F(MR, 24), fill=GREY)
        v = int(total * eo(prog(t, tt, 0.6)))
        s = f'{v:,}'.replace(',', '.') + ' €'
        vf = F(HB, 104); d.text((x0 + w - 44 - tw(d, s, vf), y + 26), s, font=vf, fill=col)
    if stamp_t is not None:
        stamp(img, 600, y0 + st_y, stamp_txt, stamp_col, prog(t, stamp_t, 0.22))
    return tt

# ---------- scenes ----------
def s1(img, d, t):
    lines = [(0.05, 'WÄRMENETZ.', INK, 140, 470), (1.15, '10 JAHRE', RED, 150, 700), (1.5, 'VERTRAG.', RED, 150, 860)]
    for a, s, c, sz, y in lines:
        p = prog(t, a, 0.28)
        if p <= 0: continue
        sc = 1 + 0.5 * (1 - eo(p)); f = F(HB, sz * sc)
        ww = tw(d, s, f); d.text((80 + (1 - sc) * 0 , y - (sc - 1) * sz * 0.5), s, font=f, fill=c)
    p = prog(t, 1.15, 0.35)
    if p > 0: padlock(d, 878, 745, 0.95 * eob(p), RED)
    p = prog(t, 2.45, 0.25)
    if p > 0:
        f = F(HB, 92); d.text((80, 1090), 'UND TROTZDEM', font=f, fill=INK)
    p = prog(t, 2.95, 0.25)
    if p > 0:
        f = F(HB, 92); s = 'TEURER'; ww = tw(d, s, f)
        d.rectangle([70, 1205, 70 + (ww + 30) * eo(p), 1320], fill=RED)
        if p > 0.4: d.text((85, 1206), s, font=f, fill=WHITE)
        d.text((110 + ww, 1206), '?', font=f, fill=RED)
    p = prog(t, 3.3, 0.3)
    if p > 0:
        f = F(HB, 62); d.text((80, 1345), 'ALS EINE WÄRMEPUMPE', font=f, fill=DGREEN)

def house(d, cx, cy, s, col, w=12):
    pts = [(cx - 190 * s, cy), (cx, cy - 170 * s), (cx + 190 * s, cy)]
    d.line(pts, fill=col, width=int(w * s), joint='curve')
    d.rectangle([cx - 150 * s, cy, cx + 150 * s, cy + 210 * s], outline=col, width=int(w * s))
    d.rectangle([cx - 40 * s, cy + 90 * s, cx + 40 * s, cy + 210 * s], outline=col, width=int(w * s))

def s2(img, d, t):
    lt = t - 5
    p = prog(lt, 0.0, 0.3)
    f = F(HB, 96); ctext(d, 420, 'WIR RECHNEN', f, INK); ctext(d, 520, 'NACH.', f, INK)
    house(d, 540, 860, 1.0 * eob(prog(lt, 0.3, 0.4)), INK)
    for i in range(3):
        pw = prog(lt, 0.9 + i * 0.15, 0.4)
        if pw > 0:
            x = 470 + i * 70; yb = 760
            pts = [(x + 12 * math.sin((yy_ / 18) + lt * 6), yb - yy_) for yy_ in range(0, int(120 * pw), 6)]
            if len(pts) > 1: d.line(pts, fill=RED, width=8)
    v = int(17000 * eo(prog(lt, 1.6, 1.6)))
    s = f'{v:,}'.replace(',', '.') + ' kWh'
    ctext(d, 1130, s, F(HB, 150), DGREEN if v == 17000 else INK)
    ctext(d, 1300, 'Wärme pro Jahr · Einfamilienhaus', F(MR, 34), GREY)

OEL = [('Heizöl', '2.000 l × 1,64 €', '3.280 €'), ('Kaminkehrer', '', '70 €'), ('Wartung Kessel', '', '250 €'),
       ('Rücklage neuer Kessel', '18.000 € auf 20 Jahre', '900 €'), ('Sonstiges', '', '100 €')]
NW = [('Arbeitspreis', '17.000 kWh × 12,25 ct', '2.083 €'), ('Grundpreis Paket S', 'Leistungs- und Messpreis', '531 €'),
      ('Hausanschluss + Station', '8.000 €, 46 % gefördert, 20 J.', '216 €'), ('Kaminkehrer, Wartung', '', '0 €')]
WP = [('Strom (WP-Tarif)', '4.857 kWh × 25 ct', '1.214 €'), ('Zähler-Grundpreis', '', '120 €'), ('Wartung', '', '180 €'),
      ('Rücklage Anlage', '30.000 € − 46 % Förderung, 20 J.', '856 €'), ('Sonstiges', '', '50 €')]
T_OEL, T_NW, T_WP = 4600, 2830, 2420

def s3(img, d, t):
    receipt(img, t, 10.0, 'ÖLHEIZUNG', OIL, OEL, T_OEL, 0, line_dt=0.45, stamp_t=13.9, stamp_txt='TEUERSTE', stamp_col=RED, h=930, st_y=630)

def s4(img, d, t):
    receipt(img, t, 15.0, 'WÄRMENETZ', RED, NW, T_NW, 0, line_dt=0.55, h=820)
    for i, s in enumerate(['✓ kein Kessel', '✓ kein Kaminkehrer']):
        p = prog(t, 18.0 + i * 0.4, 0.25)
        if p > 0:
            f = F(MB, 34); ww = tw(d, s, f) + 44; x = 150 + i * 390; y = 1245 + 20 * (1 - eob(p))
            d.rounded_rectangle([x, y, x + ww, y + 64], radius=32, fill=GREEN)
            d.text((x + 22, y + 11), s, font=f, fill=WHITE)
    p = prog(t, 19.7, 0.4)
    if p > 0:
        f = F(SI, 54); s = 'Klingt gut …'
        d.text((930 - tw(d, s, f), 1330 + 10 * (1 - eo(p))), s, font=f, fill=GREY)

CLAUSES = [(21.85, 'Anbieter', 'nur einer, kein Wechsel'), (23.45, 'Preis', 'jährlich nach Index'),
           (25.25, 'Grundpreis', '531 €/Jahr, immer'), (26.4, 'Laufzeit', 'bis zu 10 Jahre')]
def s5(img, d, t):
    lt = t - 21
    x0, y0, w, h = 120, 420, 840, 930
    y0 += int(60 * (1 - eo(prog(lt, 0, 0.35))))
    d.rectangle([x0 + 14, y0 + 16, x0 + w + 14, y0 + h + 16], fill=(205, 209, 205))
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=WHITE)
    d.text((x0 + 50, y0 + 40), 'Wärmeliefervertrag', font=F(SI, 66), fill=INK)
    d.text((x0 + 52, y0 + 128), 'WÄRMENETZ · TYPISCHE KLAUSELN, JE NACH VERTRAG', font=F(MR, 22), fill=GREY)
    for i in range(3):
        d.rectangle([x0 + 50, y0 + 186 + i * 22, x0 + w - 60 - (i * 90) % 200, y0 + 196 + i * 22], fill=(226, 229, 226))
    y = y0 + 280
    for a, k, v in CLAUSES:
        p = prog(t, a, 0.35)
        d.rectangle([x0 + 110, y + 70, x0 + w - 80, y + 78], fill=(226, 229, 226))
        if p > 0:
            ww = (w - 160) * eo(p)
            d.rectangle([x0 + 100, y - 6, x0 + 100 + ww, y + 56], fill=MARK)
            d.text((x0 + 112, y), k + ':', font=F(MB, 34), fill=INK)
            d.text((x0 + 112 + tw(d, k + ': ', F(MB, 34)), y + 2), v, font=F(MR, 32), fill=INK)
            q = prog(t, a + 0.1, 0.2)
            if q > 0:
                c = 70; cx = x0 + 58; cy = y + 25; r = 22 * eob(q)
                d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=RED, width=9); d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED, width=9)
        else:
            d.rectangle([x0 + 110, y + 10, x0 + w - 120, y + 34], fill=(226, 229, 226))
        y += 140
    stamp(img, 640, y0 + h - 95, 'GEBUNDEN', RED, prog(t, 27.15, 0.22), ang=-9)

def s6(img, d, t):
    receipt(img, t, 28.0, 'WÄRMEPUMPE', GREEN, WP, T_WP, 0, stamp_t=31.2, stamp_txt='GÜNSTIGSTE', stamp_col=DGREEN, h=930, st_y=640, line_dt=0.34)

def s7(img, d, t):
    lt = t - 32
    ctext(d, 400, 'KOSTEN PRO JAHR', F(HB, 74), INK)
    rows = [('Ölheizung', T_OEL, OIL), ('Wärmenetz', T_NW, RED), ('Wärmepumpe', T_WP, GREEN)]
    for i, (n, v, c) in enumerate(rows):
        p = eo(prog(lt, 0.15 + i * 0.25, 0.7)); y = 520 + i * 140
        d.text((80, y), n, font=F(MB, 32), fill=INK)
        bw = int(640 * v / T_OEL * p)
        d.rectangle([80, y + 46, 80 + bw, y + 110], fill=c)
        s = f'{int(v * p):,}'.replace(',', '.') + ' €'
        d.text((80 + bw + 16, y + 56), s, font=F(MB, 38), fill=c if c != GREEN else DGREEN)
    p = prog(lt, 1.7, 0.3)
    if p > 0:
        y = 950 + int(40 * (1 - eo(p)))
        d.rounded_rectangle([80, y, 1000 - 70, y + 290], radius=28, fill=INK)
        v = int(4100 * eo(prog(lt, 1.8, 1.4))); s = f'{v:,}'.replace(',', '.') + ' €'
        ctext(d, y + 20, s, F(HB, 165), GREEN, cx=505)
        ctext(d, y + 200, 'weniger als Wärmenetz · in 10 Jahren', F(MR, 30), (220, 225, 222), cx=505)
        if lt > 2.9: ctext(d, y + 242, 'gegenüber Öl: 21.800 €', F(MB, 30), GREEN, cx=505)
    p = prog(lt, 3.6, 0.3)
    if p > 0:
        f = F(HB, 70); ctext(d, 1370 - 0, '', f, INK)
        padlock(d, 150, 1305, 0.42, DGREEN, open_=eo(prog(lt, 3.8, 0.4)))
        d.text((225, 1292), 'UND DU BLEIBST FREI.', font=F(HB, 64), fill=DGREEN)

def s8(img, d, t):
    lt = t - 38
    p = eob(prog(lt, 0.0, 0.5))
    logo(img, 540, 470 + int(40 * (1 - p)), 1.25, center=True)
    ctext(d, 820, 'Lass dein Haus', F(HB, 84), INK)
    ctext(d, 915, 'durchrechnen.', F(HB, 84), INK)
    ctext(d, 1035, 'Beratung vom Meisterbetrieb aus Aurachtal', F(MR, 30), GREY)
    q = prog(lt, 0.6, 0.3)
    if q > 0:
        y = 1130 + int(30 * (1 - eo(q)))
        d.rounded_rectangle([150, y, 930, y + 120], radius=60, fill=GREEN)
        ctext(d, y + 26, '09132 / 74 97 5-27', F(HB, 66), WHITE)
        ctext(d, y + 160, 'mair-gebäudetechnik.de', F(MB, 38), INK)

SCENES = [s1, s2, s3, s4, s5, s6, s7, s8]
KICKS = [DROP + i * 0.5 for i in range(int((DUR - DROP) / 0.5))]
SLAMS = [0.05, 1.15, 2.95, 13.9, 27.15, 31.2]

def frame(t):
    img = BG.copy(); d = ImageDraw.Draw(img)
    si = max(i for i in range(8) if SC[i] <= t)
    if si < 7: header(img, d, t)
    SCENES[si](img, d, t)
    if 2 <= si <= 6: fineprint(d)
    # camera
    z = 1.0 + 0.025 * (t - SC[si]) / (SC[si + 1] - SC[si])
    z += 0.05 * math.exp(-(t - SC[si]) / 0.09)
    for k in KICKS:
        if 0 <= t - k < 0.3: z += 0.028 * math.exp(-(t - k) / 0.08)
    if 0 <= t - DROP < 0.5: z += 0.10 * math.exp(-(t - DROP) / 0.15)
    sx = sy = 0.0
    for s in SLAMS + [DROP]:
        dt = t - s
        if 0 <= dt < 0.35:
            a = 16 * math.exp(-dt / 0.09); sx += a * math.sin(dt * 90); sy += a * math.cos(dt * 70)
    cw, ch = W / z, H / z
    x0 = (W - cw) / 2 + sx; y0 = (H - ch) / 2 + sy
    img = img.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    a = np.asarray(img, np.float32) + GRAIN[int(t * FPS) % 4]
    if 0 <= t - DROP < 0.25: a = a + (255 - a) * (1 - (t - DROP) / 0.25)
    return np.clip(a, 0, 255).astype(np.uint8)

def render(a, b, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    total = int(DUR * FPS); loop_n = int(0.4 * FPS)
    first = frame(0.35).astype(np.float32)
    for i in range(a, b):
        t = i / FPS; f = frame(t)
        if i >= total - loop_n:
            k = (i - (total - loop_n) + 1) / loop_n
            f = (f.astype(np.float32) * (1 - k) + first * k).astype(np.uint8)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for ts in sys.argv[2:]:
            Image.fromarray(frame(float(ts))).save(f'still_{ts}.jpg', quality=88)
    else:
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        render(a, b, out)
