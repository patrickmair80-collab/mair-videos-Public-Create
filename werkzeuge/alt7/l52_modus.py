# L52 Modus-Rad: Klima-Moduswahl wie auf der Fernbedienung, Raumfarbe wechselt je Modus,
# Pollen/Feinstaub-Partikel werden vom Innengeraet eingesogen, Karaoke-Untertitel, Kachel-Finale
from kit import *
S = ["Klimaanlage im Herbst? Na klar.", "Sie kühlt nicht nur im Sommer, sie heizt auch.",
     "In der Übergangszeit ist dein Zimmer schnell und sparsam warm.", "Mit dem passenden Filter holt sie Pollen aus der Luft.",
     "Und auch Feinstaub, den du gar nicht siehst.", "Heizen, kühlen, saubere Luft. Ein Gerät für das ganze Jahr.",
     "Mair Gebäudetechnik aus Aurachtal. Kommentiere KLIMA."]
D = [2.079, 2.575, 3.377, 2.765, 2.114, 3.834, 3.395]
TR = Track(S, D, start=0.5, gaps=[0.5, 0.5, 0.5, 0.45, 0.6, 0.6], tail=1.9)
SAM = load('bausteine/klima-wp-bilder/samsung_windfree_innengeraet.jpg')
SAMC = cover(SAM, 700, 300, 0.5, 0.5)
# Modi: name, Farbe Raum, Akzent, Icon
MODES = [('HEIZEN', (226, 112, 42), (255, 196, 120)), ('KÜHLEN', (40, 120, 200), (170, 220, 255)),
         ('POLLEN', (120, 160, 40), (240, 220, 60)), ('FEINSTAUB', (96, 104, 116), (210, 214, 220))]
AUT = (150, 82, 40)

def mode_at(t):
    """aktiver Modus + Ueberblend-Faktor"""
    if t < TR.st(1) - 0.3: return -1
    if t < TR.st(3) - 0.3:
        # Satz 1: kuehlen kurz, dann heizen
        return 1 if t < TR.S[1]['words'][7][0] - 0.1 else 0
    if t < TR.st(4) - 0.3: return 2
    if t < TR.st(5) - 0.3: return 3
    return 4

def room_col(t):
    m = mode_at(t)
    col = AUT if m < 0 else ((70, 130, 60) if m == 4 else MODES[m][1])
    return col

_cc = {}
def smooth_col(t):
    # weiche Farbuebergaenge ueber 0.5 s
    acc = np.zeros(3); n = 0
    for k in range(6):
        acc += np.array(room_col(t - k * 0.1)); n += 1
    return tuple(int(v) for v in acc / n)

def bg(t):
    c = np.array(smooth_col(t), float)
    yy = np.linspace(0, 1, H)[:, None]
    top = c * 1.05 + 10; bot = c * 0.45
    a = top[None, :] * (1 - yy) + bot[None, :] * yy
    a = np.repeat(a[:, None, :], 1, axis=1)
    img = Image.fromarray(np.clip(np.broadcast_to(a, (H, 1, 3)), 0, 255).astype(np.uint8)).resize((W, H))
    return img

RNG = np.random.default_rng(11)
LEAVES = [(RNG.uniform(0, W), RNG.uniform(-400, H), RNG.uniform(40, 90), RNG.uniform(0, 6.28), RNG.uniform(60, 140)) for _ in range(14)]
PART = [(RNG.uniform(60, W - 60), RNG.uniform(700, 1450), RNG.uniform(5, 12), RNG.uniform(0, 6.28)) for _ in range(70)]
DEV = (540, 470)  # Lufteinlass Innengeraet

def leaf(d, x, y, s, ang, col):
    pts = []
    for k in range(16):
        u = k / 15 * math.pi * 2; r = s * (0.55 + 0.45 * abs(math.sin(u)))
        px = math.cos(u) * r * 0.55; py = math.sin(u) * r
        pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
    d.polygon(pts, fill=col)

def icon(d, k, cx, cy, r, col):
    if k == 0:  # Sonne / Flamme
        d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=col)
        for j in range(8):
            a = j * math.pi / 4
            d.line([(cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6), (cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9)], fill=col, width=int(r * 0.14))
    elif k == 1:  # Schneeflocke
        for j in range(3):
            a = j * math.pi / 3
            d.line([(cx - math.cos(a) * r * 0.85, cy - math.sin(a) * r * 0.85), (cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85)], fill=col, width=int(r * 0.13))
        d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=col)
    elif k == 2:  # Bluete
        for j in range(5):
            a = j * 2 * math.pi / 5
            px, py = cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45
            d.ellipse([px - r * 0.32, py - r * 0.32, px + r * 0.32, py + r * 0.32], fill=col)
        d.ellipse([cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22], fill=(255, 255, 255))
    else:  # Staubpunkte + Filtergitter
        for j in range(4):
            yy = cy - r * 0.6 + j * r * 0.4; d.line([(cx - r * 0.8, yy), (cx + r * 0.8, yy)], fill=col, width=int(r * 0.08))
        for j in range(4):
            xx = cx - r * 0.6 + j * r * 0.4; d.line([(xx, cy - r * 0.8), (xx, cy + r * 0.8)], fill=col, width=int(r * 0.08))

def device(img, t):
    d = ImageDraw.Draw(img, 'RGBA')
    k = ease((t - 0.1) / 0.5); y = int(250 + (1 - k) * -60)
    shadow(img, (190, y, 890, y + 300), rad=26, off=(0, 18), alpha=120)
    m = round_mask(700, 300, 26); img.paste(SAMC, (190, y), m)
    # Luftstrom: feine Punktwolke unter dem Geraet (WindFree-Mikroloecher), Farbe je Modus
    m_ = mode_at(t); col = (255, 200, 140) if m_ == 0 else ((190, 230, 255) if m_ in (1, 4) else (255, 255, 255))
    if m_ in (0, 1, 4):
        for j in range(60):
            ph = (t * 0.9 + j * 0.137) % 1.0
            x = 230 + (j * 97) % 620; yy = y + 300 + ph * 260
            a = int(150 * (1 - ph))
            d.ellipse([x - 3, yy - 3, x + 3, yy + 3], fill=col + (a,))
    return y

def dial(img, t, cy=1030):
    d = ImageDraw.Draw(img, 'RGBA')
    m = mode_at(t); r = 250
    app = eout((t - TR.st(1) + 0.4) / 0.5)
    if app <= 0: return
    cx = 540; rr = int(r * (0.7 + 0.3 * app))
    d.ellipse([cx - rr - 14, cy - rr - 14, cx + rr + 14, cy + rr + 14], fill=(0, 0, 0, 60))
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(248, 248, 246, int(250 * app)))
    # 4 Segmente-Icons
    for k in range(4):
        a = -math.pi / 2 + k * math.pi / 2 - math.pi / 4
        ix, iy = cx + math.cos(a) * rr * 0.66, cy + math.sin(a) * rr * 0.66
        on = (m == k) or m == 4
        col = MODES[k][1] if on else (190, 192, 196)
        pul = 1 + (0.08 * math.sin(t * 7) if m == k else 0)
        icon(d, k, ix, iy, rr * 0.2 * pul, col)
    # Zeiger
    tgt = {-1: 0, 0: 0, 1: 1, 2: 2, 3: 3, 4: 0}[m]
    # Zeiger-Winkel weich animiert
    def ang_at(tt):
        mm = mode_at(tt); tg = {-1: 0, 0: 0, 1: 1, 2: 2, 3: 3, 4: 0}[mm]
        return -math.pi / 2 + tg * math.pi / 2 - math.pi / 4
    acc = 0; n = 0
    for k in range(8): acc += ang_at(t - k * 0.05); n += 1
    ang = acc / n + (t * 1.2 if m == 4 else 0)
    d.line([(cx, cy), (cx + math.cos(ang) * rr * 0.42, cy + math.sin(ang) * rr * 0.42)], fill=NAVY, width=16)
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=NAVY)
    # Modus-Wort
    if 0 <= m < 4:
        word = 'ALLES IN EINEM' if m == 4 else MODES[m][0]
        f = F(BLACK, 76 if m < 4 else 64); w = tw(d, word, f)
        y0 = cy + rr + 40
        d.rounded_rectangle([540 - w / 2 - 34, y0, 540 + w / 2 + 34, y0 + 110], 55, fill=(255, 255, 255, 240))
        d.text((540 - w / 2, y0 + 12), word, font=f, fill=MODES[m][1] if m < 4 else GREEN)

def particles(img, t):
    m = mode_at(t)
    if m not in (2, 3): return
    d = ImageDraw.Draw(img, 'RGBA')
    t0 = TR.st(3 if m == 2 else 4) - 0.3; lt = t - t0
    for j, (x, y, s, ph) in enumerate(PART):
        delay = (j % 14) * 0.12; k = ease((lt - 0.6 - delay) / 1.6)
        px = lerp(x + 18 * math.sin(t * 1.3 + ph), DEV[0] + (j % 9 - 4) * 30, k)
        py = lerp(y + 14 * math.cos(t * 1.1 + ph), DEV[1] + 120, k)
        a = int(230 * (1 - k))
        if a <= 5: continue
        if m == 2:
            d.ellipse([px - s, py - s, px + s, py + s], fill=(250, 220, 60, a))
            d.ellipse([px - s * 0.4, py - s * 0.4, px + s * 0.4, py + s * 0.4], fill=(200, 150, 20, a))
        else:
            s2 = s * 0.55; d.ellipse([px - s2, py - s2, px + s2, py + s2], fill=(60, 62, 66, a))
    # Zaehler "gefiltert"
    f = F(XB, 40); s_ = 'Filter aktiv: ' + ('Pollen' if m == 2 else 'Feinstaub')
    d.rounded_rectangle([60, 640, 60 + tw(d, s_, f) + 52, 712], 36, fill=(0, 0, 0, 120)); d.text((86, 652), s_, font=f, fill=WHITE)

def karaoke(img, t, y=1590):
    i = TR.cur(t); s = TR.S[i]
    if not (s['t0'] - 0.1 <= t <= s['t1'] + 0.35) or i in (0, 6): return
    d = ImageDraw.Draw(img, 'RGBA'); f = F(BOLD, 50)
    words = s['words']; lines = wrap(d, s['text'], f, 900)
    wi = 0; yy = y
    _, cw = TR.word(t)
    for ln in lines:
        lw = tw(d, ln, f); x = (W - lw) / 2
        d.rounded_rectangle([x - 20, yy - 8, x + lw + 20, yy + 64], 14, fill=(0, 0, 0, 150))
        for w in ln.split():
            act = wi <= cw
            d.text((x, yy), w, font=f, fill=(255, 230, 90) if act else (255, 255, 255, 170))
            x += tw(d, w + ' ', f); wi += 1
        yy += 76

def hook(img, t):
    if t > TR.st(1) + 0.2: return
    d = ImageDraw.Draw(img, 'RGBA')
    for (x, y, s, ph, sp) in LEAVES:
        yy = (y + t * sp) % (H + 200) - 100; xx = x + 40 * math.sin(t * 1.5 + ph)
        leaf(d, xx, yy, s * 0.5, ph + t * 1.3, (200 + int(40 * math.sin(ph)), 110, 30, 220))
    k = back((t - 0.15) / 0.5)
    f = F(BLACK, 108)
    for j, ln in enumerate(['KLIMA', 'IM HERBST?']):
        w = tw(d, ln, f); d.text((540 - w / 2, 860 + j * 128 + (1 - k) * 80), ln, font=f, fill=(255, 255, 255, int(255 * clamp(k))))
    if t >= TR.S[0]['words'][3][0] - 0.05:
        e = clamp((t - TR.S[0]['words'][3][0] + 0.05) / 0.25)
        st = Image.new('RGBA', (560, 170), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([6, 6, 554, 164], 22, fill=(255, 255, 255, int(245 * min(1, e * 2))))
        ff = F(BLACK, 96); sd.text((280 - sd.textlength('Na klar.', font=ff) / 2, 28), 'Na klar.', font=ff, fill=GREEN)
        sc = lerp(1.9, 1.0, eout(e)); st = st.resize((int(560 * sc), int(170 * sc)), Image.BICUBIC)
        paste_rot(img, st, 540, 1240, -6)

def finale(img, t):
    if t < TR.st(5) - 0.3: return
    d = ImageDraw.Draw(img, 'RGBA')
    if t < TR.st(6) - 0.3:
        lt = t - TR.st(5) + 0.3
        for k in range(4):
            e = back((lt - k * 0.18) / 0.45)
            if e <= 0: continue
            col = MODES[k][1]; x0 = 90 + (k % 2) * 460; y0 = 1330 + (k // 2) * 0  # Reihe unter dem Rad
            x0 = 60 + k * 245; w = 225
            yb = int(1450 + (1 - e) * 80)
            d.rounded_rectangle([x0, yb - 120, x0 + w, yb + 20], 26, fill=col + (235,))
            icon(d, k, x0 + w / 2, yb - 60, 44, (255, 255, 255))
        return
    # Endkarte
    k = ease((t - TR.st(6) + 0.3) / 0.5)
    d.rectangle([0, 0, W, H], fill=(12, 24, 40, int(190 * k)))
    lg = logo(520); ly = int(560 - 50 * (1 - k))
    d.rounded_rectangle([250, ly - 40, 830, ly + lg.height + 40], 34, fill=(255, 255, 255, int(250 * k)))
    if k > 0.3: img.paste(lg, (280, ly), lg)
    d = ImageDraw.Draw(img, 'RGBA')
    f = F(BLACK, 66); s = 'Kommentiere KLIMA'; w = tw(d, s, f)
    d.rounded_rectangle([540 - w / 2 - 40, 980, 540 + w / 2 + 40, 1100], 60, fill=LIME + (int(255 * k),))
    d.text((540 - w / 2, 997), s, font=f, fill=NAVY)
    f2 = F(SEMI, 42); s2 = 'Heizen · Kühlen · Saubere Luft'; d.text((540 - tw(d, s2, f2) / 2, 1150), s2, font=f2, fill=(255, 255, 255, int(255 * k)))
    f3 = F(BLACK, 54); s3 = '09132 / 74 97 5-27'; d.text((540 - tw(d, s3, f3) / 2, 1250), s3, font=f3, fill=(255, 255, 255, int(255 * k)))
    f4 = F(MED, 34); s4 = 'Meisterbetrieb aus Aurachtal'; d.text((540 - tw(d, s4, f4) / 2, 1340), s4, font=f4, fill=(200, 210, 225, int(255 * k)))

def frame(t):
    img = bg(t).convert('RGB')
    img = grain(img, 3, int(t * 30) % 7)
    device(img, t)
    hook(img, t)
    if t < TR.st(6) - 0.3: dial(img, t)
    particles(img, t)
    finale(img, t)
    karaoke(img, t)
    # sanfte Kamerafahrt gegen Standbilder
    z = 1.0 + 0.03 * t / TR.end + 0.006 * math.sin(t * 1.7)
    w2, h2 = int(W / z), int(H / z); x0, y0 = (W - w2) // 2, int((H - h2) * 0.45)
    return img.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BICUBIC)

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('WF', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_WF_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
