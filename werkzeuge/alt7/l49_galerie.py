# L49 Baeder-Galerie: Museumswand mit gerahmten Bildern, Spots, Messingschildern, Kamerafahrt von Bild zu Bild
from kit import *
S = ["Willkommen in unserer kleinen Bäder-Galerie.", "Wanne unterm Dach.", "Marmor-Optik.", "Mosaik-Streifen.", "Licht im Spiegel.",
     "Alles geplant, gebaut und gefliest von uns, mit eigenem Fliesenleger.", "Die echte Ausstellung zeigen wir dir nach Termin. Kommentiere Ausstellung."]
D = [2.164, 0.871, 0.766, 0.947, 0.791, 4.046, 4.026]
TR = Track(S, D, start=0.5, gaps=[0.9, 1.3, 1.3, 1.3, 1.1, 0.8], tail=1.9)
PICS = [('Mair_Bad_04ef2100.jpg', 'Wanne unterm Dach'), ('Mair_Bad_6a435537.jpg', 'Marmor-Optik'), ('Mair_Bad_f3dafa0e.jpg', 'Mosaik-Streifen'),
        ('Mair_Bad_c38b8beb.jpg', 'Licht im Spiegel'), ('Mair_Bad_9bb2d176.jpg', 'Waschplatz mit Holz'), ('Mair_Bad_625344f4.jpg', 'Steinoptik und Grün')]
WALL = (222, 214, 200); WW = 1540 + 6 * 1000 + 600; FLOOR = 1560; CY = 820

def build():
    im = Image.new('RGB', (WW, H), WALL); a = np.asarray(im).astype(float)
    rng = np.random.default_rng(2); a += rng.normal(0, 3.5, a.shape[:2])[..., None]
    a[FLOOR:] = np.array([96, 70, 48]) + rng.normal(0, 6, (H - FLOOR, WW))[..., None]
    for x in range(0, WW, 180): a[FLOOR:, x:x + 3] *= 0.75
    a[FLOOR - 26:FLOOR] = [245, 242, 236]  # Fussleiste
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    # Spots (Lichtkegel)
    light = Image.new('L', (WW, H), 0); ld = ImageDraw.Draw(light)
    for i in range(6):
        cx = 1540 + i * 1000
        ld.polygon([(cx - 60, 80), (cx + 60, 80), (cx + 520, FLOOR), (cx - 520, FLOOR)], fill=60)
    light = light.filter(ImageFilter.GaussianBlur(60))
    im = Image.composite(Image.new('RGB', (WW, H), (255, 246, 225)), im, light)
    d = ImageDraw.Draw(im)
    for i in range(6):
        cx = 1540 + i * 1000; d.rounded_rectangle([cx - 70, 40, cx + 70, 96], 20, fill=(40, 40, 44)); d.ellipse([cx - 26, 84, cx + 26, 110], fill=(255, 240, 200))
    # Eingangsschild
    d.text((120, 420), 'BÄDER-', font=F(BLACK, 150), fill=(40, 44, 52)); d.text((120, 580), 'GALERIE', font=F(BLACK, 150), fill=(40, 44, 52))
    d.line([(124, 770), (900, 770)], fill=GREEN, width=8)
    d.text((124, 800), 'Bäder aus unserer Region', font=F(SERIFI, 48), fill=(70, 70, 80))
    d.text((124, 870), 'Eintritt frei', font=F(SEMI, 40), fill=(110, 105, 95))
    lg = logo(330); im.paste(lg, (124, 990), lg)
    # Bilder
    for i, (fn, title) in enumerate(PICS):
        cx = 1540 + i * 1000; ph = load('bad-serie/fotos/' + fn)
        land = ph.width > ph.height
        pw, phh = (760, 560) if land else (560, 760)
        p = cover(ph, pw, phh); mat = 46; fr = 26
        fw, fh = pw + 2 * (mat + fr), phh + 2 * (mat + fr)
        x0, y0 = cx - fw // 2, CY - fh // 2
        shadow(im, (x0, y0, x0 + fw, y0 + fh), rad=4, off=(0, 26), alpha=140, blur=28)
        d = ImageDraw.Draw(im)
        d.rectangle([x0, y0, x0 + fw, y0 + fh], fill=(26, 24, 22)); d.rectangle([x0 + fr, y0 + fr, x0 + fw - fr, y0 + fh - fr], fill=(250, 249, 245))
        im.paste(p, (x0 + fr + mat, y0 + fr + mat))
        # Messingschild
        py = y0 + fh + 60; d.rounded_rectangle([cx - 310, py, cx + 310, py + 130], 10, fill=(196, 168, 104))
        d.rounded_rectangle([cx - 300, py + 10, cx + 300, py + 120], 8, outline=(160, 130, 70), width=2)
        d.text((cx - 280, py + 18), f'Nr. {i + 1}', font=F(SEMI, 28), fill=(70, 50, 20))
        d.text((cx - 280, py + 54), title, font=F(SERIFB, 38), fill=(40, 28, 10))
    # Schluss-Wand
    ex = 1540 + 6 * 1000
    d.rounded_rectangle([ex - 470, 340, ex + 470, 1300], 30, fill=(250, 249, 245))
    d.text((ex - 410, 400), 'Die echte', font=F(BLACK, 92), fill=NAVY); d.text((ex - 410, 505), 'Ausstellung', font=F(BLACK, 92), fill=GREEN)
    d.text((ex - 410, 620), 'zeigen wir dir nach Termin.', font=F(SEMI, 44), fill=(80, 90, 110))
    d.rounded_rectangle([ex - 410, 740, ex + 410, 880], 70, fill=NAVY)
    d.text((ex - 360, 768), 'Kommentiere AUSSTELLUNG', font=F(BLACK, 50), fill=LIME)
    lg = logo(360); im.paste(lg, (ex - 180, 980), lg)
    return im
WIMG = build()

KEYS = [(0, 540), (TR.st(1) - 0.7, 540), (TR.st(1), 1540), (TR.st(2) - 0.7, 1610), (TR.st(2), 2540), (TR.st(3) - 0.7, 2610), (TR.st(3), 3540),
        (TR.st(4) - 0.7, 3610), (TR.st(4), 4540), (TR.st(5) - 0.4, 4600), (TR.st(5) + 1.4, 5540), (TR.st(6) - 0.9, 6540), (TR.st(6), 7540), (99, 7600)]
def cam(t):
    for (a, xa), (b, xb) in zip(KEYS, KEYS[1:]):
        if t <= b: return lerp(xa, xb, ease((t - a) / max(0.01, b - a)))
    return KEYS[-1][1]

def frame(t):
    cx = cam(t); z = 1.0 + 0.03 * math.sin(t * 0.35) ** 2
    w2, h2 = int(W / z), int(H / z); x0 = int(cx - w2 / 2); y0 = (H - h2) // 2 - 20
    x0 = max(0, min(WW - w2, x0))
    img = WIMG.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BILINEAR)
    # Staub im Licht
    d = ImageDraw.Draw(img, 'RGBA'); rng = np.random.default_rng(7)
    for k in range(40):
        px = (rng.uniform(0, WW) + t * 6 * (1 + k % 3)) % WW; py = (rng.uniform(150, FLOOR) - t * 12 * (1 + k % 2)) % FLOOR
        sx = (px - x0) * z; sy = (py - y0) * z
        if 0 < sx < W: d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 250, 230, 120))
    # Untertitel unten auf dem Boden
    i = TR.cur(t); s = TR.S[i]
    if s['t0'] - 0.1 <= t <= s['t1'] + 0.3 and i in (0, 5, 6):
        f = F(BOLD, 46); lines = wrap(d, s['text'], f, 920)
        for k, ln in enumerate(lines):
            w = tw(d, ln, f); x = (W - w) / 2; yy = 1585 + k * 66
            d.rounded_rectangle([x - 18, yy - 6, x + w + 18, yy + 58], 12, fill=(0, 0, 0, 160)); d.text((x, yy), ln, font=f, fill=WHITE)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('BA', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_BA_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
