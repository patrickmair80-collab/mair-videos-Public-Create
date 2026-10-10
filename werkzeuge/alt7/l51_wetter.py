# L51 Wetterbericht: TV-Studio, Regionalkarte mit Schnee, Thermometer, Laufband, Klimaanlage heizt
from kit import *
S = ["Das Wetter für Aurachtal: Draußen wird es kalt.", "Schon gewusst? Deine Klimaanlage kühlt nicht nur, sie heizt auch.",
     "Sie arbeitet wie eine kleine Luft-Wärmepumpe.", "Im Sommer kühlt sie, im Winter heizt sie.",
     "Mit Strom von deiner Photovoltaik-Anlage heizt du ein Stück weit mit eigener Sonne.", "Die neuen Geräte sind schon da. Kommentiere Klima."]
D = [2.474, 3.94, 1.983, 2.236, 4.111, 3.314]
TR = Track(S, D, start=0.6, gaps=[0.6, 0.5, 0.5, 0.6, 0.6], tail=1.9)
SAM = load('bausteine/klima-wp-bilder/samsung_windfree_innengeraet.jpg')
LIEF = load('woche42/roh/klima_lieferung.jpg')
BLUE1, BLUE2 = (24, 70, 150), (8, 26, 70); ORANGE = (245, 140, 40); ICE = (120, 200, 255)

def studio():
    a = np.zeros((H, W, 3)); y = np.linspace(0, 1, H)[:, None]
    a[:] = (np.array(BLUE1) * (1 - y) + np.array(BLUE2) * y)[:, None, :] if False else 0
    for c in range(3): a[..., c] = BLUE1[c] * (1 - y) + BLUE2[c] * y
    xx = np.linspace(-1, 1, W)[None, :]; a *= (1 - 0.25 * xx ** 2)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
    for k in range(0, W, 90): d.line([(k, 0), (k, H)], fill=(255, 255, 255, 10))
    return im
BG = studio()

def sun(d, cx, cy, r, t, col=(255, 200, 40)):
    for k in range(12):
        a = k / 12 * 2 * math.pi + t * 0.6
        d.line([(cx + (r + 10) * math.cos(a), cy + (r + 10) * math.sin(a)), (cx + (r + 34) * math.cos(a), cy + (r + 34) * math.sin(a))], fill=col, width=8)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
def cloud(d, cx, cy, s, col=(235, 240, 248)):
    for dx, dy, r in ((-0.6, 0.15, 0.45), (0, -0.15, 0.6), (0.6, 0.15, 0.45)):
        d.ellipse([cx + dx * s - r * s, cy + dy * s - r * s, cx + dx * s + r * s, cy + dy * s + r * s], fill=col)
    d.rounded_rectangle([cx - 1.05 * s, cy, cx + 1.05 * s, cy + 0.6 * s], int(0.3 * s), fill=col)
def flake(d, cx, cy, r, col=WHITE, w=4):
    for k in range(3):
        a = k * math.pi / 3; d.line([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))], fill=col, width=w)
def flame(d, cx, cy, s):
    d.polygon([(cx, cy - s), (cx + 0.55 * s, cy + 0.1 * s), (cx + 0.4 * s, cy + 0.6 * s), (cx, cy + 0.75 * s), (cx - 0.4 * s, cy + 0.6 * s), (cx - 0.55 * s, cy + 0.1 * s)], fill=ORANGE)
    d.polygon([(cx, cy - 0.3 * s), (cx + 0.25 * s, cy + 0.3 * s), (cx, cy + 0.6 * s), (cx - 0.25 * s, cy + 0.3 * s)], fill=(255, 220, 90))
def bolt(d, cx, cy, s):
    d.polygon([(cx + 0.1 * s, cy - s), (cx - 0.45 * s, cy + 0.1 * s), (cx - 0.05 * s, cy + 0.1 * s), (cx - 0.2 * s, cy + s), (cx + 0.45 * s, cy - 0.15 * s), (cx + 0.05 * s, cy - 0.15 * s)], fill=(255, 210, 40))

def panel(img, box, fill=(250, 251, 253)):
    shadow(img, box, rad=34, off=(0, 18), alpha=120)
    ImageDraw.Draw(img).rounded_rectangle(box, 34, fill=fill)

def ticker(img, t):
    d = ImageDraw.Draw(img); y = 1470
    d.rectangle([0, y, W, y + 70], fill=(250, 204, 21)); d.rectangle([0, y, 230, y + 70], fill=(200, 30, 30))
    d.text((24, y + 14), 'WETTER', font=F(BLACK, 38), fill=WHITE)
    msg = 'Klimaanlage heizt auch im Winter +++ Sonnenstrom vom eigenen Dach +++ Mair Gebäudetechnik, Aurachtal +++ '
    f = F(BOLD, 36); L = tw(d, msg, f); off = (t * 150) % L
    strip = Image.new('RGB', (W - 230, 70), (250, 204, 21)); sd = ImageDraw.Draw(strip)
    sd.text((-off, 15), msg + msg, font=f, fill=NAVY); img.paste(strip, (230, y))

def scene_map(img, t):
    d = ImageDraw.Draw(img, 'RGBA'); panel(img, (60, 330, 1020, 1330), fill=(214, 228, 214))
    d = ImageDraw.Draw(img, 'RGBA')
    # stilisierte Landschaft: Fluss und Strassen
    pts = [(60, 900 + 60 * math.sin(x / 140)) for x in range(0, 961, 20)]; pts = [(60 + x, 880 + 70 * math.sin(x / 150)) for x in range(0, 961, 20)]
    d.line(pts, fill=(120, 170, 220), width=16)
    d.line([(150, 420), (500, 760), (930, 1230)], fill=(255, 255, 255, 200), width=8)
    towns = [('Herzogenaurach', 470, 760), ('Aurachtal', 150, 1010), ('Erlangen', 640, 520)]
    for n, x, y in towns:
        big = n == 'Aurachtal'; r = 18 if big else 11
        d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 40, 40) if big else (60, 60, 70))
        d.text((x + 24, y - 22), n, font=F(BLACK if big else SEMI, 42 if big else 32), fill=(30, 30, 40))
    # Wolken und Schnee
    cloud(d, 300, 470, 70); cloud(d, 720, 1150, 85)
    rng = np.random.default_rng(1)
    for k in range(60):
        x = 90 + rng.uniform(0, 900); sp = 60 + rng.uniform(0, 80); y = 360 + (rng.uniform(0, 960) + t * sp) % 960
        flake(d, x, y, 9, col=(255, 255, 255, 230), w=3)
    # Thermometer
    k = ease((t - TR.st(0) - 0.6) / 1.5)
    d.rounded_rectangle([890, 360, 960, 760], 35, fill=WHITE); d.ellipse([860, 720, 990, 850], fill=WHITE)
    lvl = lerp(420, 650, k); col = tuple(int(lerp(a, b, k)) for a, b in zip((220, 50, 40), (60, 140, 230)))
    d.rounded_rectangle([908, lvl, 942, 780], 17, fill=col); d.ellipse([878, 738, 972, 832], fill=col)
    d.text((660, 1200), 'kalt', font=F(BLACK, 80), fill=(40, 110, 200))

def scene_ac(img, t, mode):
    panel(img, (60, 330, 1020, 1330)); d = ImageDraw.Draw(img, 'RGBA')
    ac = cover(SAM, 820, 300, 0.5, 0.5); img.paste(ac, (130, 420)); d = ImageDraw.Draw(img, 'RGBA')
    # Luftstrom
    col = ICE if mode == 'cool' else ORANGE
    for k in range(7):
        ph = (t * 1.2 + k / 7) % 1; y = 760 + ph * 380; x0 = 200 + k * 100
        d.arc([x0 - 60, y - 40, x0 + 60, y + 40], 200, 340, fill=col + (int(255 * (1 - ph)),), width=8)
    if mode == 'cool': flake(d, 540, 1220, 50, col=ICE, w=10)
    else: flame(d, 540, 1220, 70)

def frame(t):
    img = BG.copy(); d = ImageDraw.Draw(img)
    # Kopfzeile
    d.rounded_rectangle([60, 200, 470, 286], 18, fill=(250, 204, 21)); d.text((86, 214), 'WETTER', font=F(BLACK, 54), fill=NAVY)
    d.text((500, 220), 'für Aurachtal', font=F(BOLD, 48), fill=WHITE)
    i = TR.cur(t)
    if t < TR.st(1) - 0.25: scene_map(img, t)
    elif t < TR.st(2) - 0.25:
        lt = t - TR.st(1); scene_ac(img, t, 'cool' if lt < 2.0 else 'heat')
        d = ImageDraw.Draw(img); s = 'kühlt' if lt < 2.0 else 'heizt auch!'
        f = F(BLACK, 76); d.text((540 - tw(d, s, f) / 2, 360 + 420), '', font=f)
        d.rounded_rectangle([130, 330 + 20, 130 + 420, 330 + 20], 1, fill=None)
        lab = 'Schon gewusst?'; d.text((130, 345 - 10), '', font=f)
        d.rounded_rectangle([280, 1010, 800, 1110], 50, fill=(40, 110, 200) if lt < 2.0 else ORANGE); d.text((540 - tw(d, s, f) / 2, 1012), s, font=f, fill=WHITE)
    elif t < TR.st(3) - 0.25:
        panel(img, (60, 330, 1020, 1330)); d = ImageDraw.Draw(img, 'RGBA')
        d.text((110, 380), 'Wie eine kleine', font=F(SEMI, 50), fill=(80, 90, 110)); d.text((110, 445), 'Luft-Wärmepumpe', font=F(BLACK, 76), fill=NAVY)
        # Aussengeraet -> Innengeraet
        d.rounded_rectangle([110, 700, 420, 960], 20, fill=(210, 214, 220)); d.ellipse([170, 730, 360, 920], fill=(160, 166, 175))
        for k in range(4):
            a = t * 9 + k * math.pi / 2; d.line([(265, 825), (265 + 80 * math.cos(a), 825 + 80 * math.sin(a))], fill=(90, 95, 105), width=12)
        d.text((130, 980), 'draußen', font=F(SEMI, 36), fill=(90, 100, 120))
        d.rounded_rectangle([640, 700, 980, 820], 30, fill=(240, 242, 246), outline=(200, 205, 212), width=3)
        d.text((720, 840), 'drinnen', font=F(SEMI, 36), fill=(90, 100, 120))
        for k in range(5):
            ph = (t * 1.5 + k / 5) % 1; x = lerp(440, 620, ph)
            d.ellipse([x - 12, 820 - 12, x + 12, 820 + 12], fill=ORANGE + (int(255 * (1 - abs(ph - 0.5) * 2) ),))
        flame(d, 810, 1130, 90)
    elif t < TR.st(4) - 0.25:
        panel(img, (60, 330, 530, 1330), fill=(255, 246, 214)); panel(img, (550, 330, 1020, 1330), fill=(226, 238, 252))
        d = ImageDraw.Draw(img, 'RGBA'); a = ease((t - TR.st(3) + 0.25) / 0.4); b = ease((t - TR.S[3]['words'][4][0]) / 0.4)
        sun(d, 295, 560, 80, t); d.text((140, 760), 'Sommer', font=F(BLACK, 62), fill=NAVY)
        d.text((140, 840), 'kühlt', font=F(BOLD, 52), fill=(40, 110, 200, int(255 * a))); flake(d, 295, 1080, 60, col=ICE + (int(255 * a),), w=12)
        cloud(d, 785, 520, 90);
        rng = np.random.default_rng(3)
        for k in range(18):
            x = 570 + rng.uniform(0, 430); y = 620 + (rng.uniform(0, 120) + t * 70) % 120; flake(d, x, y, 8, col=(255, 255, 255), w=3)
        d.text((630, 760), 'Winter', font=F(BLACK, 62), fill=NAVY)
        d.text((630, 840), 'heizt', font=F(BOLD, 52), fill=ORANGE + (int(255 * b),))
        if b > 0: flame(d, 785, 1080, 80 * b + 1)
    elif t < TR.st(5) - 0.25:
        panel(img, (60, 330, 1020, 1330)); d = ImageDraw.Draw(img, 'RGBA')
        sun(d, 240, 520, 70, t)
        # PV-Modul
        d.polygon([(380, 700), (900, 700), (960, 980), (320, 980)], fill=(30, 50, 90))
        for k in range(1, 6): x = lerp(380, 900, k / 6); d.line([(x, 700), (lerp(320, 960, k / 6), 980)], fill=(120, 150, 200), width=3)
        for k in range(1, 3): y = lerp(700, 980, k / 3); d.line([(lerp(380, 320, k / 3), y), (lerp(900, 960, k / 3), y)], fill=(120, 150, 200), width=3)
        bolt(d, 640, 1130, 70 + 6 * math.sin(t * 8))
        d.text((110, 1210), 'Heizen mit eigener Sonne', font=F(BLACK, 58), fill=NAVY)
    else:
        lt = t - TR.st(5) + 0.25
        z = 1.0 + 0.08 * clamp(lt / 4)
        ph = cover(LIEF, 960 * z, 1000 * z, 0.5, 0.55); ph = ph.crop(((ph.width - 960) // 2, (ph.height - 1000) // 2, (ph.width - 960) // 2 + 960, (ph.height - 1000) // 2 + 1000))
        shadow(img, (60, 330, 1020, 1330)); img.paste(ph, (60, 330), round_mask(960, 1000, 34))
        d = ImageDraw.Draw(img, 'RGBA'); d.rounded_rectangle([60, 1030, 1020, 1330], 34, fill=(10, 20, 40, 200))
        d.text((110, 1060), 'Die neuen Geräte', font=F(BLACK, 66), fill=WHITE); d.text((110, 1140), 'sind schon da.', font=F(BLACK, 66), fill=LIME)
        d.rounded_rectangle([110, 1235, 600, 1305], 35, fill=LIME); d.text((140, 1245), 'Kommentiere KLIMA', font=F(BLACK, 40), fill=NAVY)
        lg = logo(200); d.rounded_rectangle([700, 1205, 990, 1315], 20, fill=(255, 255, 255, 240)); img.paste(lg, (745, 1215), lg)
    # Szenenwechsel-Wischer
    for k in range(1, 6):
        st = TR.st(k) - 0.25
        if st <= t < st + 0.3:
            p = (t - st) / 0.3; x = int(lerp(-W, W, p))
            ImageDraw.Draw(img).rectangle([x, 300, x + W, 1360], fill=(250, 204, 21))
    ticker(img, t)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('KL', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_KL_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
