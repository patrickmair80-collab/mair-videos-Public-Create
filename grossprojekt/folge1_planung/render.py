import math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = '/tmp/claude-0/reel/'
W, H, FPS, DUR = 1080, 1920, 30, 34.0
FI = '/usr/share/fonts/opentype/inter/'
def F(n, s): return ImageFont.truetype(FI + n + '.otf', s)
CREAM = (246, 241, 230); INK = (28, 33, 30); G = (47, 125, 58); DG = (29, 79, 37); LG = (108, 208, 74); OR = (185, 119, 46); GR = (110, 116, 112)

def cl(x, a=0., b=1.): return max(a, min(b, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eob(x):
    x = cl(x); c1 = 1.7; c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------- assets ----------
logo = Image.open('/root/mairvid/werkzeuge/marke/mair_logo_aus_anzeige.png').convert('RGBA')
def glow(im, r=10):
    a = im.split()[3].filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(r))
    g = Image.new('RGBA', im.size, (255, 255, 255, 0)); g.putalpha(a.point(lambda v: min(255, v * 2)))
    out = Image.new('RGBA', im.size); out.alpha_composite(g); out.alpha_composite(im); return out
def pad(im, p): o = Image.new('RGBA', (im.width + 2 * p, im.height + 2 * p)); o.paste(im, (p, p)); return o
LOGO_S = glow(pad(logo.resize((230, 128)), 24))
LOGO_B = glow(pad(logo.resize((440, 245)), 30), 14)

def crop(f, box): return Image.open(D + f).convert('RGB').crop(box)
g10 = crop('g-10.png', (130, 470, 1115, 1280))
g12 = crop('g-12.png', (55, 175, 1700, 1050))
M = {i: Image.open(D + f'm{i}.png').convert('RGB') for i in range(2, 9)}
m3 = M[3]; m4 = M[4]; m6 = M[6]

def card(im, w):
    h = int(im.height * w / im.width); c = im.resize((w, h), Image.LANCZOS)
    b = Image.new('RGBA', (w + 24, h + 24), (255, 255, 255, 255)); b.paste(c, (12, 12))
    sh = Image.new('RGBA', (b.width + 120, b.height + 120), (0, 0, 0, 0))
    m = Image.new('L', b.size, 120); sh.paste((40, 30, 20, 255), (70, 80), m)
    sh = sh.filter(ImageFilter.GaussianBlur(26)); sh.alpha_composite(b, (60, 60)); return sh
CARDS = {1: card(m3, 900), 2: card(g10, 700), 3: card(g12, 900), 4: card(m4, 900), 5: card(m6, 900)}
FAN = [card(M[i], 620) for i in range(2, 9)]

# paper background with mm grid
bg = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(bg)
for x in range(0, W, 30): d.line([(x, 0), (x, H)], fill=(234, 228, 214) if x % 150 else (225, 217, 199), width=1)
for y in range(0, H, 30): d.line([(0, y), (W, y)], fill=(234, 228, 214) if y % 150 else (225, 217, 199), width=1)
nz = (np.random.default_rng(3).normal(0, 4, (H, W, 1))).astype(np.int16)
bg = Image.fromarray(np.clip(np.asarray(bg).astype(np.int16) + nz, 0, 255).astype(np.uint8))
DARK = Image.new('RGB', (W, H), DG); dd = ImageDraw.Draw(DARK)
for r in range(1400, 0, -40): dd.ellipse([W // 2 - r, 700 - r, W // 2 + r, 700 + r], fill=tuple(int(DG[i] + (G[i] - DG[i]) * (1 - r / 1400) * 0.45) for i in range(3)))

# ---------- timing ----------
VO = [0.25, 4.75, 8.75, 12.95, 18.15, 22.5, 26.3, 30.3]
VD = [4.13, 3.61, 3.79, 4.86, 4.03, 3.65, 3.28, 3.2]
LINES = [l.strip() for l in open(D + 'lines.txt', encoding='utf-8')]
LINES[7] = 'Erst planen, dann bauen. Mair Gebäudetechnik.'
SC = [(0, 4.6), (4.6, 8.6), (8.6, 12.8), (12.8, 18.0), (18.0, 22.4), (22.4, 26.0), (26.0, 30.0), (30.0, 34.0)]
STEP = {1: ('Bestand aufnehmen', ['Öl-Kessel Bj. 1997', '18.000 l pro Jahr', '12 Wohnungen']),
        2: ('Heizlast rechnen', ['78,2 kW', 'jeder Raum einzeln', 'DIN EN 12831']),
        3: ('Heizkörper prüfen', ['67 Heizkörper', '24 werden größer', 'bei 55 °C']),
        4: ('Zwei Wege rechnen', ['Pellet', 'Wärmepumpe', 'ehrlich verglichen']),
        5: ('15 Jahre Kosten', ['mit Förderung', 'pro Wohnung', 'ohne Schönrechnen'])}
DROP = 26.0

def words_at(t):
    for k, s in enumerate(VO):
        if s <= t < s + VD[k] + 0.25:
            ws = LINES[k].split(); n = len(ws); per = VD[k] / n
            i = min(n - 1, int((t - s) / per))
            return ws, i
    return None, None

def caption(img, t, dark=False):
    ws, i = words_at(t)
    if not ws: return
    # show a window of up to 4 words around current
    st = (i // 3) * 3; chunk = ws[st:st + 3]
    d = ImageDraw.Draw(img); sz = 70
    while True:
        f = F('InterDisplay-ExtraBold', sz); line = ' '.join(chunk); tw = d.textlength(line, font=f)
        if tw < 940 or sz < 40: break
        sz -= 4
    x = (W - tw) / 2; y = 1350
    for j, w in enumerate(chunk):
        cur = (st + j) == i; wl = d.textlength(w + ' ', font=f)
        if cur:
            d.rounded_rectangle([x - 10, y - 4, x + d.textlength(w, font=f) + 10, y + sz + 16], 14, fill=LG if not dark else (255, 255, 255))
            d.text((x, y), w, font=f, fill=INK)
        else:
            d.text((x, y), w, font=f, fill=(255, 255, 255) if dark else INK, stroke_width=0)
        x += wl

def timeline(img, step, p):
    d = ImageDraw.Draw(img); x0 = 140; wseg = 150; y = 470
    for k in range(5):
        c = G if k < step - 1 else (215, 208, 192)
        d.rounded_rectangle([x0 + k * (wseg + 16), y, x0 + k * (wseg + 16) + wseg, y + 12], 6, fill=c)
        if k == step - 1:
            d.rounded_rectangle([x0 + k * (wseg + 16), y, x0 + k * (wseg + 16) + wseg * eo(p), y + 12], 6, fill=G)

def chips(img, labels, t0, t):
    d = ImageDraw.Draw(img); f = F('Inter-Bold', 34); y = 1215
    ws = [d.textlength(l, font=f) + 50 for l in labels]; tot = sum(ws) + 16 * (len(ws) - 1)
    x = (W - tot) / 2
    for k, l in enumerate(labels):
        w = ws[k]; p = eob((t - t0 - 0.9 - k * 0.35) / 0.35)
        if p > 0:
            cx = x + w / 2
            col = OR if l == 'Pellet' else (G if l == 'Wärmepumpe' or k == 1 else DG)
            d.rounded_rectangle([cx - w / 2 * p, y + 31 - 31 * p, cx + w / 2 * p, y + 31 + 31 * p], 31, fill=col)
            if p > 0.6: d.text((x + 25, y + 10), l, font=f, fill='white')
        x += w + 16

def step_scene(t, k, a, b):
    img = bg.copy(); lt = t - a
    title, labs = STEP[k]
    d = ImageDraw.Draw(img)
    d.text((140, 290), f'0{k}', font=F('InterDisplay-Black', 140), fill=G)
    d.text((340, 318), 'SCHRITT ' + str(k) + ' VON 5', font=F('Inter-Bold', 30), fill=GR)
    d.text((340, 356), title, font=F('InterDisplay-ExtraBold', 66), fill=INK)
    timeline(img, k, lt / 0.6)
    c = CARDS[k]; p = eo(lt / 0.55)
    ang = -7 * (1 - p) + (-1.5 if k % 2 else 1.5) + 0.6 * math.sin(lt * 1.3)
    sc = 1.0 + 0.04 * (lt / (b - a))
    cc = c.resize((int(c.width * sc), int(c.height * sc)), Image.BILINEAR).rotate(ang, expand=True, resample=Image.BICUBIC)
    cx = W / 2 + 10 + (1 - p) * 900; cy = 840
    img.paste(cc, (int(cx - cc.width / 2), int(cy - cc.height / 2)), cc)
    chips(img, labs, a, t)
    img.paste(LOGO_S, (W - LOGO_S.width - 10, 1025), LOGO_S)
    return img

def hook(t):
    img = DARK.copy(); d = ImageDraw.Draw(img)
    items = [(0.2, '12 Wohnungen.', 120, (255, 255, 255)), (1.45, '18.000 Liter', 150, LG), (1.45, 'Heizöl im Jahr.', 100, (255, 255, 255)), (3.0, 'Und jetzt?', 170, (255, 255, 255))]
    y = 420
    for k, (s, txt, size, col) in enumerate(items):
        p = eob((t - s) / 0.3)
        if p > 0:
            f = F('InterDisplay-Black', int(size * (0.7 + 0.3 * p)))
            tw = d.textlength(txt, font=f); d.text(((W - tw) / 2, y + (1 - p) * 60), txt, font=f, fill=col)
        y += size + 45 if k != 1 else size + 15
        if k == 2: y += 60
    img.paste(LOGO_S, (W - LOGO_S.width - 40, 1520), LOGO_S)
    return img

def fan(t):
    img = bg.copy(); lt = t - 26.0; d = ImageDraw.Draw(img)
    n = len(FAN)
    for k, c in enumerate(FAN):
        p = eob((lt - k * 0.12) / 0.45)
        if p <= 0: continue
        ang = (k - (n - 1) / 2) * 7 * p
        cc = c.rotate(-ang, expand=True, resample=Image.BICUBIC)
        cx = W / 2 + (k - (n - 1) / 2) * 34 * p; cy = 900 + abs(k - (n - 1) / 2) * 14 * p - (1 - p) * 300
        img.paste(cc, (int(cx - cc.width / 2), int(cy - cc.height / 2)), cc)
    p = eob((lt - 0.9) / 0.35)
    if p > 0:
        f = F('InterDisplay-Black', int(118 * (0.6 + 0.4 * p)))
        for j, txt in enumerate(['Alles in', 'einer Mappe.']):
            tw = d.textlength(txt, font=f); d.text(((W - tw) / 2, 300 + j * 125), txt, font=f, fill=DG)
    return img

def end(t):
    img = DARK.copy(); d = ImageDraw.Draw(img); lt = t - 30.0
    img.paste(LOGO_B, ((W - LOGO_B.width) // 2, 330), LOGO_B)
    for j, (txt, col, s) in enumerate([('Erst planen.', (255, 255, 255), 0.2), ('Dann bauen.', LG, 0.55)]):
        p = eob((lt - s) / 0.35)
        if p > 0:
            f = F('InterDisplay-Black', 130); tw = d.textlength(txt, font=f); d.text(((W - tw) / 2, 690 + j * 150 + (1 - p) * 50), txt, font=f, fill=col)
    p = eob((lt - 1.1) / 0.35)
    if p > 0:
        d.rounded_rectangle([170, 1040, 910, 1180], 30, fill=(255, 255, 255))
        f = F('Inter-Bold', 44); txt = 'Kommentiere PLAN'; tw = d.textlength(txt, font=f); d.text(((W - tw) / 2, 1062), txt, font=f, fill=DG)
        f2 = F('Inter-Medium', 30); txt = 'für unsere Planungs-Checkliste'; tw = d.textlength(txt, font=f2); d.text(((W - tw) / 2, 1120), txt, font=f2, fill=GR)
    p = eo((lt - 1.5) / 0.4)
    if p > 0:
        f = F('Inter-SemiBold', 42)
        for j, txt in enumerate(['09132 / 74975-27', 'www.mair-gebäudetechnik.de']):
            tw = d.textlength(txt, font=f); d.text(((W - tw) / 2, 1250 + j * 64), txt, font=f, fill=(220, 236, 222))
    return img

def frame(t):
    if t < 4.6: img = hook(t)
    elif t < 26.0:
        for k in range(1, 6):
            a, b = SC[k]
            if a <= t < b: img = step_scene(t, k, a, b); break
    elif t < 30.0: img = fan(t)
    else: img = end(t)
    dark = t < 4.6 or t >= 30.0
    # beat punch after drop / slam at drop
    z = 1.0
    if 26.0 <= t < 30.0:
        ph = ((t - 26.0) % 0.5) / 0.5; z = 1 + 0.028 * (1 - eo(ph * 3))
    if 26.0 <= t < 26.4: z += 0.1 * (1 - (t - 26.0) / 0.4)
    if z != 1.0:
        w2, h2 = int(W * z), int(H * z); img = img.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
    if 4.6 <= t < 30.0: caption(img, t, dark)
    # white flash at drop
    if 26.0 <= t < 26.25:
        a = 1 - (t - 26.0) / 0.25; img = Image.blend(img, Image.new('RGB', (W, H), 'white'), 0.85 * a)
    # loop back to first frame
    if t > DUR - 0.4:
        img = Image.blend(img, hook(3.6), (t - (DUR - 0.4)) / 0.4)
    return img

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]: frame(float(ts)).save(D + f'f_{ts}.png')
    else:
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', D + 'video.mp4'], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait(); print('video ok')
