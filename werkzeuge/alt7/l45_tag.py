# L45 Tagesprotokoll: liniertes Papier, Polaroid-Stapel, Tagesleiste mit Sonne, Analoguhr, Textmarker-Untertitel
from kit import *
S = ["Ein Tag bei Maier Gebäudetechnik.", "Morgens kommt die Lieferung.", "Vormittags fliegt beim Kunden die alte Ölheizung raus.",
     "Mittags der nächste Keller: alter Pelletkessel raus, neuer rein.", "Nachmittags wird verkabelt, und jede Ader zählt.",
     "Und als Nächstes kommt die Wärmepumpe.", "Steht bei dir auch so ein Kessel? Kommentiere Tausch."]
SUB = [s.replace('Maier', 'Mair') for s in S]
D = [1.859, 1.325, 2.984, 3.699, 2.718, 1.887, 3.351]
TR = Track(SUB, D, start=0.5, gaps=[0.5, 0.55, 0.55, 0.55, 0.7, 0.45], tail=1.8)
PW, PH = 820, 680
P_LIEF = cover(load('woche42/roh/klima_lieferung.jpg'), PW * 1.15, PH * 1.15, 0.5, 0.62)
P_OEL = cover(load('woche42/roh/oelheizung_alt.jpg'), PW * 1.15, PH * 1.15, 0.5, 0.55)
C_PEL = Clip('woche42/roh/pellet_clip.mp4', 0.0, 5.0, 't_pel', PW, PH, 1.0)
C_KAB = Clip('woche42/roh/pellet_clip.mp4', 8.4, 2.8, 't_kab', PW, PH, 1.0)
CARDS = [('Morgens', 'Die Lieferung ist da', 1, -3.0), ('Vormittags', 'Alte Ölheizung raus', 2, 2.4),
         ('Mittags', 'Pelletkessel: alt raus, neu rein', 3, -2.0), ('Nachmittags', 'Jede Ader zählt', 4, 2.8)]
PAPER = (244, 239, 227)

def bg():
    im = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(im)
    for y in range(150, H, 64): d.line([(0, y), (W, y)], fill=(208, 220, 233), width=2)
    d.line([(112, 0), (112, H)], fill=(228, 150, 150), width=3)
    return grain(im, 5, 1)
BG = bg()

def photo(i, t):
    lt = t - TR.st(CARDS[i][2])
    if i == 0: z = 1.0 + 0.06 * clamp(lt / 6); return cover(P_LIEF, PW, PH, 0.5, 0.4, zoom=z)
    if i == 1: z = 1.0 + 0.07 * clamp(lt / 6); return cover(P_OEL, PW, PH, 0.5, 0.5, zoom=z)
    if i == 2: return C_PEL.at(lt * 1.0)
    return C_KAB.at(lt)

def polaroid(i, t):
    ph = photo(i, t); bw, bt = 26, 120
    card = Image.new('RGB', (PW + 2 * bw, PH + bw + bt), (252, 252, 248)); card.paste(ph, (bw, bw))
    d = ImageDraw.Draw(card)
    d.text((bw + 6, PH + bw + 18), CARDS[i][0], font=F(SERIFBI, 40), fill=(40, 60, 110))
    d.text((bw + 6, PH + bw + 66), CARDS[i][1], font=F(SERIFI, 32), fill=(70, 70, 80))
    # Klebestreifen
    tape = Image.new('RGBA', (210, 56), (236, 222, 170, 190))
    card = card.convert('RGBA'); card.alpha_composite(tape, (card.width // 2 - 105, -18 + 18))
    return card

def clock(img, cx, cy, r, hours):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=(40, 46, 56))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 252, 248))
    for k in range(12):
        a = k / 12 * 2 * math.pi; r1 = r - (16 if k % 3 == 0 else 9)
        d.line([(cx + r1 * math.sin(a), cy - r1 * math.cos(a)), (cx + (r - 4) * math.sin(a), cy - (r - 4) * math.cos(a))], fill=INK, width=4 if k % 3 == 0 else 2)
    ah = (hours % 12) / 12 * 2 * math.pi; am = (hours % 1) * 2 * math.pi
    d.line([(cx, cy), (cx + r * 0.5 * math.sin(ah), cy - r * 0.5 * math.cos(ah))], fill=INK, width=8)
    d.line([(cx, cy), (cx + r * 0.78 * math.sin(am), cy - r * 0.78 * math.cos(am))], fill=GREEN, width=5)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=INK)

KEYS = [(0, 6.5), (TR.st(1), 7.0), (TR.st(2), 9.5), (TR.st(3), 12.5), (TR.st(4), 15.5), (TR.en(4) + 0.3, 16.75), (99, 16.75)]
def hours_at(t):
    for (a, ha), (b, hb) in zip(KEYS, KEYS[1:]):
        if t <= b: return lerp(ha, hb, ease((t - a) / max(0.01, min(b - a, 0.9))))
    return KEYS[-1][1]

STX = [215, 420, 630, 840]
def daybar(img, t, alpha=1.0):
    d = ImageDraw.Draw(img); y = 1352
    prog = 0.0
    for k in range(4):
        if t >= TR.st(CARDS[k][2]): prog = k + ease((t - TR.st(CARDS[k][2])) / 0.6) * (1 if k < 3 else 0)
    d.line([(STX[0], y), (STX[3], y)], fill=(190, 190, 185), width=8)
    xp = lerp(STX[0], STX[3], clamp(prog / 3)) if prog > 0 else STX[0]
    if t >= TR.st(1): d.line([(STX[0], y), (xp, y)], fill=GREEN, width=8)
    for k, x in enumerate(STX):
        on = t >= TR.st(CARDS[k][2])
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=GREEN if on else PAPER, outline=GREEN if on else (170, 170, 165), width=5)
        if on: d.line([(x - 10, y), (x - 3, y + 8), (x + 11, y - 9)], fill=WHITE, width=5)
        lab = CARDS[k][0]; f = F(SEMI, 27); d.text((x - tw(d, lab, f) / 2, y + 36), lab, font=f, fill=INK if on else (140, 140, 135))
    # Sonne wandert ueber die Leiste
    if t >= TR.st(1) - 0.3:
        sx = xp; sy = y - 70 - 26 * math.sin(clamp(prog / 3) * math.pi)
        for k in range(10):
            a = k / 10 * 2 * math.pi + t * 0.8
            d.line([(sx + 30 * math.cos(a), sy + 30 * math.sin(a)), (sx + 42 * math.cos(a), sy + 42 * math.sin(a))], fill=(240, 170, 30), width=5)
        d.ellipse([sx - 22, sy - 22, sx + 22, sy + 22], fill=(250, 190, 40))

def marker_sub(img, t, y0=1500):
    i, j = TR.word(t); s = TR.S[i]
    if t < s['t0'] - 0.15 or t > s['t1'] + 0.35: return
    d = ImageDraw.Draw(img); f = F(BOLD, 48)
    words = [w for _, _, w in s['words']]; lines = []; cur = []
    for k, w in enumerate(words):
        if cur and tw(d, ' '.join(words[c] for c in cur + [k]), f) > 880: lines.append(cur); cur = []
        cur.append(k)
    lines.append(cur)
    for li, ln in enumerate(lines):
        x = 140; y = y0 + li * 66
        for k in ln:
            w = words[k]; ww = tw(d, w, f)
            a, du, _ = s['words'][k]
            if t >= a:
                kk = ease((t - a) / max(0.12, du))
                d.rectangle([x - 6, y + 14, x - 6 + (ww + 12) * kk, y + 58], fill=(214, 240, 120))
            d.text((x, y), w, font=f, fill=INK)
            x += ww + tw(d, ' ', f)

def frame(t):
    img = BG.copy(); d = ImageDraw.Draw(img)
    # Kopf
    k = ease((t - TR.st(1) + 0.4) / 0.6)
    if k < 1:
        f = F(BLACK, 92); s1 = 'TAGES-'; s2 = 'PROTOKOLL'; a = ease(t / 0.5)
        y = lerp(620, 200, k)
        if k == 0:
            d.text((140, 560), 'TAGES', font=F(BLACK, 120), fill=NAVY); d.text((140, 690), 'PROTOKOLL', font=F(BLACK, 120), fill=NAVY)
            d.text((146, 850), 'Ein Tag bei Mair Gebäudetechnik', font=F(SERIFI, 46), fill=(60, 70, 100))
            lg = logo(300); img.paste(lg, (146, 960), lg)
    if k > 0:
        y = 190
        d.text((140, y), 'TAGESPROTOKOLL', font=F(BLACK, 62), fill=NAVY)
        d.text((142, y + 74), 'Ein Tag bei Mair Gebäudetechnik', font=F(SERIFI, 36), fill=(60, 70, 100))
    clock(img, 920, 250, 74, hours_at(t))
    # Polaroid-Stapel
    endk = ease((t - TR.st(5) + 0.2) / 0.7)
    for i in range(4):
        st = TR.st(CARDS[i][2])
        if t < st - 0.35: continue
        e = eout((t - st + 0.35) / 0.55)
        cx = 540 + (1 - e) * 700 + (i % 2 * 2 - 1) * 14; cy = 810 + (1 - e) * 120
        ang = CARDS[i][3] + (1 - e) * 18
        if endk > 0: cx -= endk * (1300 + i * 40); ang += endk * 10
        last = i == max(k2 for k2 in range(4) if t >= TR.st(CARDS[k2][2]) - 0.35)
        c = polaroid(i, t) if last or i == 3 else polaroid(i, min(t, TR.st(CARDS[i + 1][2]) if i < 3 else t))
        paste_rot(img, c, cx, cy, ang, shadow_a=120)
    if t >= TR.st(1) - 0.35 and endk < 1: daybar(img, t)
    # Schluss
    if endk > 0:
        d = ImageDraw.Draw(img)
        a = ease((t - TR.st(5)) / 0.5)
        y0 = 560
        d.text((140, y0 - 20 * (1 - a)), 'Als Nächstes:', font=F(SERIFBI, 64), fill=(60, 70, 100))
        d.text((140, y0 + 90), 'Wärmepumpe', font=F(BLACK, 116), fill=GREEN)
        d.text((140, y0 + 230), 'rein.', font=F(BLACK, 116), fill=NAVY)
        d.text((146, y0 + 410), 'Folg uns, Teil 2 kommt.', font=F(SERIFI, 42), fill=(70, 70, 80))
        if t >= TR.st(6) - 0.2:
            ks = clamp((t - TR.st(6) + 0.2) / 0.35)
            st = Image.new('RGBA', (760, 210), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            col = (196, 40, 40, int(235 * min(1, ks * 2)))
            sd.rounded_rectangle([6, 6, 754, 204], 18, outline=col, width=10)
            sd.text((44, 22), 'KOMMENTIERE', font=F(BLACK, 66), fill=col); sd.text((44, 100), 'TAUSCH', font=F(BLACK, 92), fill=col)
            sc = lerp(1.7, 1.0, eout(ks)); st = st.resize((int(760 * sc), int(210 * sc)), Image.BICUBIC)
            paste_rot(img, st, 540, 1200, -6)
        lg = logo(300); img.paste(lg, (W - 300 - 80, 1640 - 0), lg)
    if t < TR.st(5) - 0.1: marker_sub(img, t, 1488)
    else: marker_sub(img, t, 1440)
    z = 0
    if t < 2.9: z = 0.045 * t / 2.9
    elif t > TR.st(5) - 0.3: z = 0.05 * ease((t - TR.st(5) + 0.3) / (TR.end - TR.st(5)))
    if z > 0:
        w2, h2 = int(W / (1 + z)), int(H / (1 + z)); x0, y0 = (W - w2) // 2, (H - h2) // 2
        img = img.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BICUBIC)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('T', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_T_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
