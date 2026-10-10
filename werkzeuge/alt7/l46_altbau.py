# L46 Faktencheck: Zitatkarte, roter Stempel STIMMT NICHT, Kino-Breitbild-Band, Checkliste die sich fuellt
from kit import *
S = ["Wärmepumpe im Altbau? Vergiss es.", "Stimmt nicht.", "Vier Zeichen, dass es bei dir klappt.",
     "Erstens: Deine Heizkörper werden auch mit fünfundfünfzig Grad Vorlauf warm.",
     "Zweitens: Dein Verbrauch ist bekannt, die Heizlast lässt sich sauber berechnen.",
     "Drittens: Draußen ist Platz für das Außengerät.", "Viertens: Fenster oder Dach wurden schon mal erneuert.",
     "Wir prüfen dein Haus vor Ort. Maier Gebäudetechnik."]
D = [2.688, 0.543, 1.705, 4.25, 4.527, 2.478, 2.764, 3.264]
TR = Track(S, D, start=0.5, gaps=[0.25, 0.55, 0.5, 0.5, 0.5, 0.5, 0.6], tail=1.8)
BG0 = (13, 21, 37)
C_WP = Clip('Mair_Reel_Kurz_altbau.mp4', 0.0, 7.0, 'ab_wp', 1080, 1920)
ITEMS = [('Heizkörper werden mit', 'ca. 55 °C Vorlauf warm'), ('Verbrauch bekannt,', 'Heizlast berechenbar'),
         ('Platz für das', 'Außengerät'), ('Fenster oder Dach', 'schon erneuert')]

def bgimg():
    im = Image.new('RGB', (W, H), BG0); a = np.asarray(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 540) / 900) ** 2 + ((yy - 900) / 1300) ** 2)
    a *= (1.15 - 0.45 * np.clip(r, 0, 1))[..., None]
    return grain(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), 4, 3)
BG = bgimg()

def band(t):
    # Breitbild-Ausschnitt ohne eingebrannte Texte (y 905..1345), langsam abgespielt
    lt = max(0, t - TR.st(2) + 0.3)
    fr = C_WP.at((lt * 0.55) % 6.9)
    return fr.crop((0, 905, 1080, 1345))

def frame(t):
    img = BG.copy(); d = ImageDraw.Draw(img)
    # Label
    f = F(BLACK, 30); lab = 'FAKTENCHECK'; lw = tw(d, lab, f)
    d.rounded_rectangle([80, 200, 80 + lw + 56, 254], 27, fill=LIME); d.text((108, 207), lab, font=f, fill=NAVY)
    d.text((80 + lw + 80, 210), 'Wärmepumpe im Altbau', font=F(SEMI, 32), fill=(170, 185, 210))
    # Zitatkarte
    endk = ease((t - TR.st(7) + 0.2) / 0.6)
    qa = ease((t + 0.35) / 0.5); qy = 300 + (1 - qa) * 40
    card = Image.new('RGBA', (920, 330), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, 919, 329], 28, fill=(250, 248, 242, int(255 * qa)))
    if endk < 0.5: cd.text((40, -30), '„', font=F(SERIFB, 170), fill=(200, 60, 50, int(255 * qa)))
    if endk < 0.5:
        cd.text((60, 120), 'Wärmepumpe im Altbau?', font=F(SERIFBI, 56), fill=(30, 30, 40, int(255 * qa)))
        cd.text((60, 195), 'Vergiss es.', font=F(SERIFBI, 56), fill=(30, 30, 40, int(255 * qa)))
        cd.text((60, 272), 'hört man oft', font=F(SERIFI, 30), fill=(110, 110, 120, int(255 * qa)))
    else:
        cd.text((60, 110), 'Wir prüfen dein', font=F(BLACK, 64), fill=NAVY)
        cd.text((60, 190), 'Haus vor Ort.', font=F(BLACK, 64), fill=GREEN)
        lg = logo(230); card.alpha_composite(lg, (650, 250 - lg.height // 2 + 10))
    sh = int(9 * math.sin(t * 70) * clamp(1 - (t - TR.st(1)) / 0.3)) if TR.st(1) <= t < TR.st(1) + 0.3 else 0
    img.paste(card, (80 + sh, int(qy)), card)
    # Stempel STIMMT NICHT
    if t >= TR.st(1) - 0.05 and endk < 0.5:
        k = clamp((t - TR.st(1) + 0.05) / 0.22)
        st = Image.new('RGBA', (860, 190), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        col = (214, 40, 40, int(240 * min(1, k * 2)))
        sd.rounded_rectangle([6, 6, 854, 184], 20, outline=col, width=12)
        sd.text((44, 40), 'STIMMT NICHT', font=F(BLACK, 96), fill=col)
        sc = lerp(2.2, 1.0, eout(k)); st = st.resize((int(860 * sc), int(190 * sc)), Image.BICUBIC)
        paste_rot(img, st, 540, 470, 7)
    # Kino-Band
    if t >= TR.st(2) - 0.4:
        a = eout((t - TR.st(2) + 0.4) / 0.6)
        b = band(t); bh = int(440 * a)
        if bh > 4:
            y0 = 740 + (440 - bh) // 2
            img.paste(b.crop((0, (440 - bh) // 2, 1080, (440 - bh) // 2 + bh)), (0, y0))
            d.rectangle([0, y0 - 6, W, y0], fill=(0, 0, 0)); d.rectangle([0, y0 + bh, W, y0 + bh + 6], fill=(0, 0, 0))
        if a > 0.9 and t < TR.st(3) + 0.2:
            f = F(BLACK, 54); s = '4 Zeichen, dass es klappt'
            x = (W - tw(d, s, f)) / 2
            d.rounded_rectangle([x - 26, 1210, x + tw(d, s, f) + 26, 1290], 16, fill=(0, 0, 0))
            d.text((x, 1218), s, font=f, fill=WHITE)
    if endk >= 0.5:
        k = clamp((t - TR.st(7) - 0.1) / 0.25)
        st = Image.new('RGBA', (560, 170), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        col = (90, 170, 40, int(240 * min(1, k * 2)))
        sd.rounded_rectangle([6, 6, 554, 164], 20, outline=col, width=12); sd.text((52, 26), 'KLAPPT', font=F(BLACK, 104), fill=col)
        sc = lerp(2.0, 1.0, eout(k)); st = st.resize((int(560 * sc), int(170 * sc)), Image.BICUBIC)
        paste_rot(img, st, 540, 720, -7)
    # Checkliste
    for i, (l1, l2) in enumerate(ITEMS):
        s0 = TR.st(3 + i)
        if t < s0 - 0.25: continue
        a = eout((t - s0 + 0.25) / 0.4); y = 1210 + i * 96 + (1 - a) * 30
        act = TR.st(3 + i) - 0.25 <= t < (TR.st(4 + i) - 0.25 if i < 3 else TR.en(6) + 0.3)
        box = [70, y, 1010, y + 84]
        if act: d.rounded_rectangle(box, 18, fill=(250, 248, 242))
        else: d.rounded_rectangle(box, 18, outline=(60, 78, 110), width=2)
        ck = ease((t - s0 - 0.25) / 0.35)
        d.ellipse([92, y + 14, 148, y + 70], fill=GREEN if ck > 0 else (60, 78, 110))
        if ck > 0:
            pts = [(104, y + 43), (116, y + 56), (138, y + 30)]
            if ck < 1: pts = pts[:2] + [(lerp(116, 138, ck), lerp(y + 56, y + 30, ck))]
            d.line(pts, fill=WHITE, width=7, joint='curve')
        col = NAVY if act else (200, 210, 225)
        d.text((172, y + 8), f'{i + 1}.  {l1}', font=F(SEMI, 30), fill=(90, 100, 120) if act else (130, 145, 170))
        d.text((172, y + 40), l2, font=F(BOLD, 36), fill=col)
    # leichte Kamerabewegung
    z = 0.025 * t / TR.end
    w2, h2 = int(W / (1 + z)), int(H / (1 + z)); x0, y0 = (W - w2) // 2, (H - h2) // 2
    if z > 0.001: img = img.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BICUBIC)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('AB', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_AB_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
