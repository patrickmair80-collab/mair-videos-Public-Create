import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 50.0
FD = '/usr/share/fonts/truetype/'
SER = FD + 'google-fonts/Lora-Variable.ttf'
SB = FD + 'crosextra/Carlito-Bold.ttf'
SR_ = FD + 'crosextra/Carlito-Regular.ttf'
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc:
        f = ImageFont.truetype(p, int(s))
        if p == SER:
            try: f.set_variation_by_axes([600])
            except Exception: pass
        _fc[k] = f
    return _fc[k]

# palette: slate desk, white pages, Mair green, amber gas, oil brown
DESK = (28, 37, 41); PAGE = (255, 255, 255); INK = (24, 30, 33); GREY = (112, 120, 124); LINE = (226, 230, 230)
GREEN = (93, 179, 58); DGREEN = (46, 107, 42); AMBER = (224, 160, 48); OIL = (78, 61, 48); RED = (200, 62, 46); WHITE = (255, 255, 255)
CREAMTXT = (232, 238, 234)

S_INTRO, S_A, S_B, S_C, S_END = 0, 3, 18, 31, 46
DROP = 18.0

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eob(x):
    x = clamp(x); c1 = 1.7; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, a, d): return clamp((t - a) / d)
def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]
def ctext(d, y, s, f, fill, cx=W // 2): d.text((cx - tw(d, s, f) // 2, y), s, font=f, fill=fill)
def eur(v): return f'{int(round(v)):,}'.replace(',', '.') + ' €'

# background: desk with spotlight + grain
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W]
spot = np.exp(-(((xx - W * 0.5) / (W * 0.8)) ** 2 + ((yy - H * 0.42) / (H * 0.55)) ** 2))
base = np.array(DESK, np.float32)[None, None, :] * (0.65 + 0.55 * spot[..., None])
BG = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
GRAIN = [rng.normal(0, 3.5, (H, W, 1)).astype(np.float32) for _ in range(4)]

def logo(img, x, y, sc, center=False, light=False):
    d = ImageDraw.Draw(img)
    f1 = F(FD + 'dejavu/DejaVuSans-Bold.ttf', 120 * sc); f2 = F(FD + 'dejavu/DejaVuSansCondensed-Bold.ttf', 34 * sc)
    w1 = tw(d, 'Mair', f1); w2 = tw(d, 'GEBÄUDETECHNIK', f2) + int(36 * sc); ww = max(w1, w2)
    if center: x -= ww // 2
    d.text((x + (ww - w1) // 2, y), 'Mair', font=f1, fill=(225, 228, 230) if light else (132, 136, 139))
    by = y + int(128 * sc)
    d.rounded_rectangle([x, by, x + ww, by + int(48 * sc)], radius=int(8 * sc), fill=GREEN)
    d.text((x + (ww - tw(d, 'GEBÄUDETECHNIK', f2)) // 2, by + int(4 * sc)), 'GEBÄUDETECHNIK', font=f2, fill=WHITE)

def header(img, d):
    logo(img, 60, 250, 0.40, light=True)
    f = F(SB, 26); s = 'PROJEKTMAPPE · BEISPIEL'
    d.text((960 - tw(d, s, f), 282), s, font=f, fill=(170, 182, 186))

_sh = {}
def page(img, t, t0, chap, label, x0=90, y0=420, w=900, h=1060, slide=True):
    p = eo(prog(t, t0, 0.45)) if slide else 1
    dx = int((1 - p) * 1000)
    key = (w, h)
    if key not in _sh:
        m = Image.new('L', (w + 120, h + 120), 0); ImageDraw.Draw(m).rectangle([60, 70, w + 60, h + 60], fill=150)
        _sh[key] = m.filter(ImageFilter.GaussianBlur(26))
    X = x0 + dx
    img.paste((0, 0, 0), (X - 60, y0 - 60), _sh[key])
    d = ImageDraw.Draw(img)
    d.rectangle([X, y0, X + w, y0 + h], fill=PAGE)
    d.rectangle([X, y0, X + 16, y0 + h], fill=GREEN)
    d.text((X + 56, y0 + 34), chap, font=F(SB, 30), fill=GREEN)
    d.text((X + 56 + tw(d, chap + '  ', F(SB, 30)), y0 + 34), label.upper(), font=F(SB, 26), fill=GREY)
    logo(img, X + w - 190, y0 + 28, 0.32)
    d.line([(X + 56, y0 + 100), (X + w - 50, y0 + 100)], fill=LINE, width=2)
    return X, y0, d

def wrap(d, s, f, maxw):
    out, cur = [], ''
    for wd in s.split():
        t2 = (cur + ' ' + wd).strip()
        if tw(d, t2, f) <= maxw: cur = t2
        else: out.append(cur); cur = wd
    out.append(cur); return out

def redact(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=(120, 150, 118))

# ---------------- INTRO / END: the folder cover ----------------
def cover(img, d, t, t0, end=False):
    lt = t - t0
    rise = eob(prog(lt, 0.0, 0.55))
    w, h = 800, 1000
    x0 = (W - w) // 2; y0 = 470 + int(260 * (1 - rise))
    openp = 0 if end else eo(prog(lt, 2.35, 0.55))
    cw = int(w * (1 - openp))
    if cw < 8: return
    c = Image.new('RGB', (w, h), (38, 92, 40)); cd = ImageDraw.Draw(c)
    for i in range(0, h, 4): cd.line([(0, i), (w, i)], fill=(40 + (i % 8 == 0) * 2, 95, 42))
    cd.rectangle([0, 0, 22, h], fill=(30, 74, 32))
    logo(c, 70, 70, 0.6, light=True)
    cd.text((70, 330), 'Ihr Zuhause.', font=F(SER, 70), fill=WHITE)
    cd.text((70, 415), 'Ihre Energie.', font=F(SER, 70), fill=WHITE)
    cd.text((70, 520), 'Ihr persönlicher Zukunftsplan', font=F(SB, 40), fill=(200, 230, 190))
    cd.text((70, 700), 'KUNDE', font=F(SB, 24), fill=(170, 205, 165)); redact(cd, 70, 734, 380, 34)
    cd.text((70, 800), 'OBJEKT', font=F(SB, 24), fill=(170, 205, 165)); redact(cd, 70, 834, 300, 34)
    cd.text((70, 900), 'Wärmepumpe · Heizungstausch', font=F(SB, 30), fill=WHITE)
    if end:
        cd.rectangle([0, 600, w, h], fill=(38, 92, 40))
        q = prog(lt, 0.5, 0.35)
        if q > 0:
            cd.text((70, 610), 'Deine eigene', font=F(SER, 64), fill=WHITE)
            cd.text((70, 690), 'Projektmappe?', font=F(SER, 64), fill=WHITE)
        q = prog(lt, 0.9, 0.3)
        if q > 0:
            cd.rounded_rectangle([70, 800, 730, 900], radius=50, fill=GREEN)
            s = '09132 / 74 97 5-27'; f = F(SB, 58); cd.text((400 - tw(cd, s, f) // 2, 814), s, font=f, fill=WHITE)
            cd.text((70, 925), 'oder kommentiere MAPPE', font=F(SB, 34), fill=(200, 230, 190))
    if cw < w: c = c.resize((cw, h), Image.BICUBIC)
    m = Image.new('L', (w + 120, h + 120), 0); ImageDraw.Draw(m).rectangle([60, 70, cw + 60, h + 60], fill=170)
    img.paste((0, 0, 0), (x0 - 60, y0 - 60), m.filter(ImageFilter.GaussianBlur(26)))
    img.paste(c, (x0, y0))

def s_intro(img, d, t):
    # page underneath already visible when cover opens
    if t > 2.3: s_a(img, d, max(t, 3.0) if t >= 3 else 3.0, static=True)
    cover(img, d, t, 0.0)
    p = prog(t, 0.15, 0.35)
    fade = 1 - prog(t, 2.2, 0.3)
    if p > 0 and fade > 0:
        lay = Image.new('RGBA', (W, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        f = F(SB, 66); y = 10 + int(20 * (1 - eo(p)))
        ctext(ld, y, 'So plant ein Meisterbetrieb', f, WHITE + (int(255 * fade),))
        ctext(ld, y + 70, 'deine Wärmepumpe.', f, GREEN + (int(255 * fade),))
        img.paste(lay, (0, 320), lay)

# ---------------- A: comparison ----------------
ROWS = [('Öl', 3700, OIL), ('Gas', 2410, AMBER), ('Wärmepumpe', 1564, GREEN)]
def calc_line(d, x, y, txt, p, f, col):
    if p <= 0: return
    n = max(1, int(len(txt) * min(1, p * 1.4)))
    d.text((x + int(24 * (1 - eo(p))), y), txt[:n], font=f, fill=col)

def s_a(img, d, t, static=False):
    X, Y, d = page(img, t, 3.0, '04', 'Ihre Vorteile', slide=not static and t < 3.6)
    fT = F(SER, 54)
    for i, ln in enumerate(['Was kostet dich deine', 'Heizung wirklich?']):
        d.text((X + 56, Y + 130 + i * 66), ln, font=fT, fill=INK)
    xL = X + 60; fM = F(SB, 44); fS = F(SR_, 30)
    if t < 13.6:
        d.text((xL, Y + 300), 'AUSGANGSLAGE', font=F(SB, 28), fill=GREY)
        calc_line(d, xL, Y + 350, '2.000 Liter Heizöl im Jahr', prog(t, 3.6, 0.6), F(SB, 56), OIL)
        calc_line(d, xL, Y + 450, '× 10 kWh pro Liter', prog(t, 5.6, 0.5), fM, GREY)
        calc_line(d, xL, Y + 520, '= 20.000 kWh im Öl', prog(t, 6.8, 0.5), fM, INK)
        calc_line(d, xL, Y + 610, '× 85 % Kesselwirkungsgrad', prog(t, 8.8, 0.5), fM, GREY)
        q = prog(t, 11.0, 0.4)
        if q > 0:
            y = Y + 720 + int(20 * (1 - eob(q)))
            d.rounded_rectangle([xL - 10, y, xL + 760, y + 110], radius=20, fill=GREEN)
            d.text((xL + 20, y + 22), '= 17.000 kWh Wärme im Haus', font=F(SB, 54), fill=WHITE)
    elif t < 22.1:
        d.rounded_rectangle([xL - 10, Y + 290, xL + 560, Y + 360], radius=16, fill=GREEN)
        d.text((xL + 14, Y + 300), '17.000 kWh Wärme gebraucht', font=F(SB, 40), fill=WHITE)
        d.text((xL, Y + 400), 'GLEICHE WÄRME MIT …', font=F(SB, 28), fill=GREY)
        p = prog(t, 13.9, 0.5)
        if p > 0:
            d.text((xL, Y + 450), 'Gas', font=F(SB, 50), fill=(170, 115, 20))
            calc_line(d, xL, Y + 515, '17.000 kWh ÷ 90 % Kessel', p, fS, GREY)
            calc_line(d, xL, Y + 560, '= 18.900 kWh Gas', prog(t, 14.8, 0.5), fM, INK)
        p = prog(t, 17.4, 0.5)
        if p > 0:
            d.text((xL, Y + 660), 'Wärmepumpe', font=F(SB, 50), fill=DGREEN)
            calc_line(d, xL, Y + 725, '17.000 kWh ÷ Jahresarbeitszahl 3,0', p, fS, GREY)
            calc_line(d, xL, Y + 770, '= 5.667 kWh Strom', prog(t, 18.4, 0.5), fM, INK)
            q = prog(t, 19.8, 0.4)
            if q > 0:
                d.text((xL, Y + 850), '+ 11.333 kWh gratis aus der Außenluft', font=F(SB, 36), fill=DGREEN)
    elif t < 29.4:
        d.text((xL, Y + 300), 'Laufende Kosten pro Jahr', font=F(SB, 36), fill=INK)
        rows = [('Öl', 3600, OIL, 23.6, '2.000 l × 1,64 €'), ('Gas', 2358, AMBER, 25.5, '18.900 kWh × 11,1 ct'), ('Wärmepumpe', 1773, GREEN, 27.2, '5.667 kWh × 26 ct')]
        base_y = Y + 880; cx0 = X + 110; bw = 200; gap = 60; maxh = 380
        for i, (n, val, c, a, sub) in enumerate(rows):
            p = eo(prog(t, a, 0.7))
            if p <= 0: continue
            hh = int(maxh * val / 3600 * p); x = cx0 + i * (bw + gap)
            d.rectangle([x, base_y - hh, x + bw, base_y], fill=c)
            s = eur(val * p); f = F(SB, 46); d.text((x + bw // 2 - tw(d, s, f) // 2, base_y - hh - 58), s, font=f, fill=INK)
            f2 = F(SB, 32); d.text((x + bw // 2 - tw(d, n, f2) // 2, base_y + 14), n, font=f2, fill=INK)
            f3 = F(SR_, 22); d.text((x + bw // 2 - tw(d, sub, f3) // 2, base_y + 54), sub, font=f3, fill=GREY)
    elif t < 33.0:
        d.text((xL, Y + 300), 'Laufende Kosten pro Jahr', font=F(SB, 36), fill=INK)
        rows = [('Öl', 3600, OIL, '3.280 € Öl · 250 € Wartung · 70 € Kaminkehrer'),
                ('Gas', 2358, (170, 115, 20), '2.098 € Gas · 200 € Wartung · 60 € Kaminkehrer'),
                ('Wärmepumpe', 1773, DGREEN, '1.473 € Strom · 180 € Wartung · 120 € Zähler')]
        for i, (n, val, c, sub) in enumerate(rows):
            y = Y + 360 + i * 98
            d.text((xL, y), n, font=F(SB, 42), fill=c)
            s = eur(val); f = F(SB, 42); d.text((X + 840 - tw(d, s, f), y), s, font=f, fill=c)
            d.text((xL, y + 50), sub, font=F(SR_, 24), fill=GREY)
        for i, (lab, v, a) in enumerate([('gegenüber Öl', 1827, 29.9), ('gegenüber Gas', 585, 31.1)]):
            q = prog(t, a, 0.35)
            if q <= 0: continue
            by = Y + 720 + i * 115 + int(20 * (1 - eob(q)))
            s = '−' + eur(v * eo(prog(t, a, 0.9))) + ' / Jahr'; f = F(SB, 52); ww = tw(d, s, f) + 60
            d.rounded_rectangle([X + 56, by, X + 56 + ww, by + 82], radius=41, fill=GREEN)
            d.text((X + 86, by + 8), s, font=f, fill=WHITE)
            d.text((X + 76 + ww, by + 24), lab, font=F(SB, 34), fill=INK)
    else:
        p = prog(t, 33.1, 0.3)
        if p > 0:
            d.text((xL, Y + 300), 'Und das ist noch', font=F(SB, 44), fill=GREY)
            sc = 1 + 0.4 * (1 - eo(p)); f = F(SB, 78 * sc)
            d.text((xL, Y + 360), 'OHNE PV-Anlage.', font=f, fill=RED)
        p = prog(t, 34.9, 0.4)
        if p > 0:
            calc_line(d, xL, Y + 480, 'Gerechnet mit 26 ct Netzstrom.', p, F(SB, 42), INK)
        p = prog(t, 37.0, 0.4)
        if p > 0:
            cx, cy, r = X + 140, Y + 660, 46 * eob(p)
            for k in range(12):
                ang = k * math.pi / 6 + t * 0.6
                d.line([(cx + math.cos(ang) * r * 1.3, cy + math.sin(ang) * r * 1.3), (cx + math.cos(ang) * r * 1.75, cy + math.sin(ang) * r * 1.75)], fill=AMBER, width=8)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)
            d.text((X + 250, Y + 610), 'Mit eigenem Sonnenstrom', font=F(SB, 42), fill=INK)
            d.text((X + 250, Y + 662), 'noch günstiger.', font=F(SB, 42), fill=INK)
        p = prog(t, 39.2, 0.35)
        if p > 0:
            y = Y + 800 + int(24 * (1 - eob(p)))
            d.rounded_rectangle([xL - 10, y, xL + 790, y + 170], radius=24, fill=GREEN)
            d.text((xL + 24, y + 20), 'Die Sonne schickt dir', font=F(SER, 58), fill=WHITE)
            d.text((xL + 24, y + 90), 'keine Rechnung.', font=F(SER, 58), fill=WHITE)
    d.text((X + 56, Y + 1030), 'Heizöl 1,64 €/l (05.10.26) · Gas 11,1 ct/kWh (BDEW) · WP-Strom 26 ct, JAZ 3,0 · ohne Anschaffung', font=F(SR_, 19), fill=GREY)

# ---------------- B: process ----------------
STEPS = [(18.9, 'Vor-Ort-Termin', 'Haus, Heizkörper, Aufstellort'), (22.3, 'Heizlast berechnen', 'Raum für Raum statt Pi mal Daumen'),
         (24.4, 'Projektmappe + Angebot', 'individuell auf dich zugeschnitten'), (27.4, 'Förderantrag', 'gemeinsam, vor dem Start'),
         (28.5, 'Einbau', 'eigenes Team, Altanlage raus'), (29.7, 'Einweisung + App', 'Service vom Meisterbetrieb')]
def s_b(img, d, t):
    X, Y, d = page(img, t, 18.0, '→', 'So läuft es ab')
    d.text((X + 56, Y + 130), 'Vom Anruf zur', font=F(SER, 54), fill=INK)
    d.text((X + 56, Y + 196), 'Wärmepumpe', font=F(SER, 54), fill=DGREEN)
    lx = X + 100; y0 = Y + 330; step = 122
    last = max([i for i, s in enumerate(STEPS) if t >= s[0]] or [-1])
    d.line([(lx, y0), (lx, y0 + step * 5)], fill=LINE, width=6)
    if last >= 0:
        fill_to = y0 + step * (last + eo(prog(t, STEPS[last][0], 0.4)) - 1) if last > 0 else y0
        fill_to = max(y0, y0 + step * last * 1.0) if t > STEPS[last][0] + 0.4 else fill_to
        d.line([(lx, y0), (lx, min(fill_to, y0 + step * 5))], fill=GREEN, width=6)
    for i, (a, k, v) in enumerate(STEPS):
        y = y0 + i * step; p = prog(t, a, 0.3)
        r = 30
        if p > 0:
            rr = r * eob(p); d.ellipse([lx - rr, y - rr, lx + rr, y + rr], fill=GREEN)
            s = str(i + 1); f = F(SB, 34); d.text((lx - tw(d, s, f) // 2, y - 21), s, font=f, fill=WHITE)
            off = int(30 * (1 - eo(p)))
            d.text((lx + 60 + off, y - 34), k, font=F(SB, 44), fill=INK)
            d.text((lx + 60 + off, y + 14), v, font=F(SR_, 30), fill=GREY)
        else:
            d.ellipse([lx - 14, y - 14, lx + 14, y + 14], fill=LINE)

# ---------------- C: funding ----------------
FUND = [(33.7, 'Vertrag mit Förderklausel', ''), (35.0, 'Bestätigung zum Antrag', 'erstellen wir'),
        (36.4, 'Antrag bei der KfW', 'VOR dem Start!'), (38.0, 'Zusage abwarten', ''),
        (39.6, 'Einbau', ''), (40.4, 'Nachweise einreichen', 'Geld kommt aufs Konto')]
def s_c(img, d, t):
    X, Y, d = page(img, t, 31.0, '05', 'Förderung')
    d.text((X + 56, Y + 130), 'Förderantrag?', font=F(SER, 54), fill=INK)
    d.text((X + 56, Y + 196), 'Machen wir zusammen.', font=F(SER, 54), fill=DGREEN)
    y = Y + 320
    for a, k, v in FUND:
        p = prog(t, a, 0.3)
        bx = X + 60
        d.rounded_rectangle([bx, y, bx + 46, y + 46], radius=8, outline=GREEN if p > 0 else LINE, width=4)
        if p > 0:
            q = eo(p)
            pts = [(bx + 10, y + 24), (bx + 20, y + 35), (bx + 38, y + 12)]
            if q < 0.5: d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * q * 2, pts[0][1] + (pts[1][1] - pts[0][1]) * q * 2)], fill=GREEN, width=7)
            else: d.line([pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * (q - .5) * 2, pts[1][1] + (pts[2][1] - pts[1][1]) * (q - .5) * 2)], fill=GREEN, width=7)
            d.text((bx + 70, y), k, font=F(SB, 40), fill=INK)
            if v:
                f = F(SB, 30); vx = bx + 70 + tw(d, k + '  ', F(SB, 40))
                if 'VOR' in v:
                    d.rounded_rectangle([vx - 10, y + 2, vx + tw(d, v, f) + 14, y + 46], radius=10, fill=RED); d.text((vx + 2, y + 7), v, font=f, fill=WHITE)
                else: d.text((vx, y + 7), v, font=f, fill=GREY)
        else:
            d.text((bx + 70, y), k, font=F(SB, 40), fill=LINE)
        y += 74
    q = prog(t, 41.9, 0.3)
    if q > 0:
        yb = Y + 790
        d.line([(X + 56, yb - 20), (X + 850, yb - 20)], fill=LINE, width=2)
        rows = [('Anlage, Beispiel', 30000, INK, 41.9), ('Zuschuss KfW', -12880, DGREEN, 42.6), ('Du zahlst', 17120, INK, 43.5)]
        for i, (k, v, c, a) in enumerate(rows):
            p = prog(t, a, 0.5)
            if p <= 0: continue
            yy_ = yb + i * 66
            if i == 2: d.line([(X + 500, yy_ - 6), (X + 850, yy_ - 6)], fill=INK, width=3)
            d.text((X + 60, yy_), k, font=F(SB, 40 if i < 2 else 46), fill=c)
            s = ('− ' if v < 0 else '') + eur(abs(v) * eo(p)); f = F(SB, 46 if i < 2 else 56)
            d.text((X + 850 - tw(d, s, f), yy_ - (6 if i == 2 else 0)), s, font=f, fill=c if i < 2 else DGREEN)
    d.text((X + 56, Y + 1020), 'KfW 458: 30 % + 16 % Bonus, max. 28.000 € förderfähig · Stand 10/2026 · ohne Gewähr', font=F(SR_, 19), fill=GREY)

def s_end(img, d, t):
    cover(img, d, t, 46.0, end=True)

KICKS = [DROP + i * 0.5 for i in range(int((DUR - DROP) / 0.5))]
SLAMS = [3.0, 18.0, 31.0, 46.0]

SHIFT = 24.0
A_END = 42.0
DUR = 74.0
def frame(t):
    img = BG.copy(); d = ImageDraw.Draw(img)
    header(img, d)
    tm = t - SHIFT if t >= A_END else t
    if t < 3: s_intro(img, d, t)
    elif t < A_END: s_a(img, d, t)
    elif tm < S_C: s_b(img, d, tm)
    elif tm < S_END: s_c(img, d, tm)
    else: s_end(img, d, tm)
    bounds = [0, 3, A_END, S_C + SHIFT, S_END + SHIFT]
    st = max(b for b in bounds if b <= t)
    z = 1.0 + 0.02 * min(1, (t - st) / 13) + 0.04 * math.exp(-(t - st) / 0.1)
    if A_END <= t < S_END + SHIFT:
        for k in KICKS:
            if 0 <= tm - k < 0.3: z += 0.018 * math.exp(-(tm - k) / 0.08)
    sx = sy = 0.0
    for s_ in bounds[1:]:
        dt = t - s_
        if 0 <= dt < 0.3:
            a = 10 * math.exp(-dt / 0.08); sx += a * math.sin(dt * 90); sy += a * math.cos(dt * 70)
    cw, ch = W / z, H / z; x0 = (W - cw) / 2 + sx; y0 = (H - ch) / 2 + sy
    img = img.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    a = np.asarray(img, np.float32) + GRAIN[int(t * FPS) % 4]
    if 0 <= t - A_END < 0.22: a = a + (255 - a) * (1 - (t - A_END) / 0.22)
    return np.clip(a, 0, 255).astype(np.uint8)

def render(a, b, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for ts in sys.argv[2:]: Image.fromarray(frame(float(ts))).save(f'still_{ts}.jpg', quality=88)
    else:
        render(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
