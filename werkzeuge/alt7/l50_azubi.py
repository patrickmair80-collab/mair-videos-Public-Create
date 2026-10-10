# L50 Bewerbungsbogen auf dem Klemmbrett: Kugelschreiber fuellt aus, Haken, Fotos angeklammert, Unterschrift
from kit import *
S = ["Wir suchen dich für eine Ausbildung zum Anlagenmechaniker für Sanitär-, Heizungs- und Klimatechnik.",
     "Wärmepumpe, Bad, Klima: Du lernst alles an echten Baustellen.", "Im Team und im Meisterbetrieb in Aurachtal.",
     "Dreieinhalb Jahre, verkürzbar.", "Lust auf einen Schnuppertag? Ruf an, oder schreib uns einen Kommentar."]
D = [5.1, 4.172, 2.703, 1.891, 4.001]
TR = Track(S, D, start=0.5, gaps=[0.6, 0.6, 0.5, 0.7], tail=2.0)
PEN = (28, 58, 150)
C_W = Clip('woche42/roh/pellet_clip.mp4', 0.5, 6.0, 'az_w', 270, 230)
P_B = cover(load('bad-serie/fotos/Mair_Bad_c4d0eb23.jpg'), 270, 230, 0.5, 0.35)
P_K = cover(load('woche42/roh/klima_lieferung.jpg'), 270, 230, 0.5, 0.6)

def wood():
    rng = np.random.default_rng(4); a = np.zeros((H, W, 3)); base = np.array([92, 62, 38])
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    g = np.sin(x / 9.0 + 6 * np.sin(y / 140.0) + rng.normal(0, 0.3, (1, W))) * 10 + rng.normal(0, 5, (H, W))
    a[:] = base; a += g[..., None] * np.array([1.0, 0.8, 0.6])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def build_static():
    im = wood(); d = ImageDraw.Draw(im)
    shadow(im, (70, 230, 1010, 1760), rad=30, off=(0, 20), alpha=150)
    d.rounded_rectangle([70, 230, 1010, 1760], 30, fill=(150, 108, 64))
    shadow(im, (100, 300, 980, 1720), rad=4, off=(0, 6), alpha=90, blur=10)
    d.rectangle([100, 300, 980, 1720], fill=(253, 252, 247))
    for yy in range(860, 1700, 52): d.line([(140, yy), (940, yy)], fill=(220, 228, 240), width=2)
    # Klemme
    d.rounded_rectangle([370, 200, 710, 330], 26, fill=(176, 180, 186)); d.rounded_rectangle([400, 222, 680, 300], 18, fill=(140, 144, 150))
    d.ellipse([520, 236, 560, 276], fill=(90, 94, 100))
    d.text((140, 360), 'AUSBILDUNGSPLATZ', font=F(BLACK, 58), fill=GREEN); d.text((140, 428), 'FREI', font=F(BLACK, 58), fill=NAVY)
    for k, ln in enumerate(['Anlagenmechaniker/in für Sanitär-,', 'Heizungs- und Klimatechnik (m/w/d)']):
        d.text((140, 510 + k * 42), ln, font=F(SEMI, 32), fill=(70, 80, 100))
    # Fotofeld
    for k in range(0, 200, 20):
        d.line([(745 + k, 360), (755 + k, 360)], fill=(160, 160, 160), width=3); d.line([(745 + k, 580), (755 + k, 580)], fill=(160, 160, 160), width=3)
    for k in range(0, 220, 20):
        d.line([(745, 360 + k), (745, 370 + k)], fill=(160, 160, 160), width=3); d.line([(945, 360 + k), (945, 370 + k)], fill=(160, 160, 160), width=3)
    d.text((140, 760), 'Was du lernst:', font=F(BOLD, 40), fill=NAVY)
    for k, lab in enumerate(['Wärmepumpe', 'Bad', 'Klima']):
        x = [140, 520, 740][k]; d.rectangle([x, 830, x + 48, 878], outline=NAVY, width=4); d.text((x + 64, 832), lab, font=F(SEMI, 38), fill=NAVY)
    d.text((140, 1190), 'Wo:', font=F(BOLD, 38), fill=NAVY); d.text((140, 1290), 'Dauer:', font=F(BOLD, 38), fill=NAVY)
    d.text((140, 1490), 'Unterschrift:', font=F(BOLD, 38), fill=NAVY); d.line([(400, 1540), (940, 1540)], fill=(120, 120, 130), width=3)
    lg = logo(220); im.paste(lg, (140, 620), lg)
    return im
ST = build_static()

def pen(d, x, y, txt, t0, t, size=44, cps=22):
    n = int(clamp((t - t0) * cps, 0, len(txt))); d.text((x, y), txt[:n], font=F(SERIFBI, size), fill=PEN)
    return n == len(txt)

def frame(t):
    img = ST.copy(); d = ImageDraw.Draw(img)
    # Haken
    for k in range(3):
        tk = TR.S[1]['words'][k][0]; a = clamp((t - tk) / 0.3)
        if a > 0:
            x = [140, 520, 740][k]; pts = [(x + 6, 852), (x + 20, 870), (x + 58, 818)]
            if a < 0.5: pts = [pts[0], (lerp(pts[0][0], pts[1][0], a * 2), lerp(pts[0][1], pts[1][1], a * 2))]
            elif a < 1: pts = pts[:2] + [(lerp(pts[1][0], pts[2][0], (a - 0.5) * 2), lerp(pts[1][1], pts[2][1], (a - 0.5) * 2))]
            d.line(pts, fill=PEN, width=8, joint='curve')
    # Fotos angeklammert
    for k in range(3):
        st = TR.S[1]['words'][k][0] + 0.1
        if t < st: continue
        e = back((t - st) / 0.4); ph = C_W.at(t - st) if k == 0 else (P_B if k == 1 else P_K)
        card = Image.new('RGB', (290, 290), (250, 250, 248)); card.paste(ph, (10, 10))
        cd = ImageDraw.Draw(card); cd.text((14, 248), ['an echten Baustellen', 'Bad', 'Klima'][k], font=F(SERIFI, 22), fill=(60, 60, 70))
        ang = [-4, 3, -2][k]; cx = 255 + k * 290; cy = 1040 + (1 - e) * 60
        sc = 0.6 + 0.4 * e; c2 = card.resize((int(290 * sc), int(290 * sc)))
        paste_rot(img, c2, cx, cy, ang, shadow_a=110)
        d = ImageDraw.Draw(img); d.rounded_rectangle([cx - 14, cy - 160, cx + 14, cy - 110], 6, fill=(170, 175, 182))
    pen(d, 220, 1190, 'im Team, Meisterbetrieb Aurachtal', TR.st(2), t, 36, 18)
    pen(d, 290, 1286, '3,5 Jahre (verkürzbar)', TR.st(3), t, 42, 18)
    # Schluss
    if t >= TR.st(4) - 0.2:
        a = ease((t - TR.st(4) + 0.2) / 0.4)
        f = F(BLACK, 62); d.text((140, 1370 - 20 * (1 - a)), 'Schnuppertag?', font=f, fill=GREEN)
        # Unterschrift-Kritzel
        k = clamp((t - TR.st(4) - 0.6) / 1.4); pts = []
        for j in range(int(80 * k)):
            u = j / 80; pts.append((420 + 480 * u, 1515 - 22 * math.sin(u * 19) * (1 - u * 0.5) - 8 * math.sin(u * 47)))
        if len(pts) > 1: d.line(pts, fill=PEN, width=6, joint='curve')
        # Fotofeld: Du?
        d.text((780, 420), 'Du?', font=F(SERIFBI, 70), fill=PEN)
        pk = eout((t - TR.st(4) - 0.4) / 0.5)
        if pk > 0:
            y = int(1640 - 40 * pk)
            d.rounded_rectangle([140, y - 60, 940, y + 50], 55, fill=GREEN)
            s = '09132 / 74 97 5-27'; f = F(BLACK, 56); d.text((540 - tw(d, s, f) / 2, y - 48), s, font=f, fill=WHITE)
    z = 1.0 + 0.06 * t / TR.end
    fy = 0.35 if t < TR.st(4) else lerp(0.35, 0.6, ease((t - TR.st(4)) / 1.0))
    w2, h2 = int(W / z), int(H / z); x0 = (W - w2) // 2; y0 = int((H - h2) * fy)
    return img.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BICUBIC)

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('AZ', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_AZ_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
