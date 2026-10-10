# L48 Baustellen-Warnschild: Absperrband, Warndreieck, gelbe Fehlerkarten mit rotem X, Umklappen auf gruene Loesung
from kit import *
S = ["Drei Fehler beim Heizungstausch, die richtig Geld kosten.", "Fehler eins: keine Heizlastberechnung. Dann ist das Gerät zu groß oder zu klein.",
     "Fehler zwei: kein hydraulischer Abgleich. Räume werden ungleich warm, und Strom wird verschwendet.",
     "Fehler drei: Förderung zu spät beantragt. Der Antrag muss vor dem Start stehen.", "Wir machen das von Anfang an richtig. Maier Gebäudetechnik."]
D = [3.046, 5.095, 5.861, 4.627, 3.468]
TR = Track(S, D, start=0.5, gaps=[0.6, 1.4, 1.4, 1.1], tail=1.8)
YEL = (250, 204, 21); ASPH = (36, 37, 40); RED = (210, 40, 40)
C_WP = Clip('Mair_Reel_Kurz_heizung.mp4', 0.0, 7.0, 'fe_wp', 1080, 1920)
ERR = [('Keine Heizlast-', 'berechnung', 'Gerät zu groß oder zu klein', 'Heizlast vorher berechnen'),
       ('Kein hydraulischer', 'Abgleich', 'Räume ungleich warm, Strom weg', 'Abgleich bei jedem Tausch'),
       ('Förderung zu spät', 'beantragt', 'Antrag muss vor dem Start stehen', 'Antrag vor dem Auftrag')]

def bgimg():
    im = Image.new('RGB', (W, H), ASPH); return grain(im, 9, 5)
BG = bgimg()

def tape(img, y, t, h=64, dirn=1):
    strip = Image.new('RGB', (W + 200, h), YEL); d = ImageDraw.Draw(strip)
    off = int((t * 90 * dirn) % 100)
    for x in range(-200, W + 400, 100):
        d.polygon([(x + off, 0), (x + off + 50, 0), (x + off + 50 - h, h), (x + off - h, h)], fill=(20, 20, 20))
    img.paste(strip.crop((100, 0, 100 + W, h)), (0, y))

def triangle(d, cx, cy, s, fill=YEL, mark=True):
    p = [(cx, cy - s), (cx + s * 1.1, cy + s * 0.8), (cx - s * 1.1, cy + s * 0.8)]
    d.polygon(p, fill=(20, 20, 20)); k = 0.78
    d.polygon([(cx, cy - s * k + 6), (cx + s * 1.1 * k, cy + s * 0.8 * k - 4), (cx - s * 1.1 * k, cy + s * 0.8 * k - 4)], fill=fill)
    if mark:
        d.rounded_rectangle([cx - s * 0.08, cy - s * 0.42, cx + s * 0.08, cy + s * 0.22], 6, fill=(20, 20, 20))
        d.ellipse([cx - s * 0.09, cy + s * 0.32, cx + s * 0.09, cy + s * 0.5], fill=(20, 20, 20))

def errcard(i, t, flip):
    c = Image.new('RGBA', (960, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    good = flip >= 0.5
    col = (92, 170, 40) if good else YEL
    d.rounded_rectangle([0, 0, 959, 559], 34, fill=(20, 20, 20)); d.rounded_rectangle([12, 12, 947, 547], 26, fill=col)
    if not good:
        d.ellipse([44, 44, 164, 164], fill=(20, 20, 20)); n = str(i + 1); f = F(BLACK, 84)
        d.text((104 - tw(d, n, f) / 2, 50), n, font=f, fill=YEL)
        d.text((196, 52), 'FEHLER', font=F(BLACK, 40), fill=(20, 20, 20)); d.text((196, 98), f'{i + 1} von 3', font=F(SEMI, 34), fill=(70, 60, 10))
        d.text((48, 210), ERR[i][0], font=F(BLACK, 72), fill=(20, 20, 20)); d.text((48, 292), ERR[i][1], font=F(BLACK, 72), fill=(20, 20, 20))
        d.text((48, 410), '→ ' + ERR[i][2], font=F(BOLD, 40), fill=(60, 50, 10))
    else:
        d.ellipse([44, 44, 164, 164], fill=WHITE); d.line([(74, 104), (98, 130), (138, 76)], fill=(92, 170, 40), width=14)
        d.text((196, 52), 'SO GEHT ES', font=F(BLACK, 40), fill=WHITE); d.text((196, 98), 'richtig', font=F(SEMI, 34), fill=(225, 245, 210))
        lines = wrap(d, ERR[i][3], F(BLACK, 76), 860)
        for k, ln in enumerate(lines): d.text((48, 220 + k * 92), ln, font=F(BLACK, 76), fill=WHITE)
    # Klapp-Effekt: horizontal stauchen
    sx = abs(math.cos(flip * math.pi)) if 0 < flip < 1 else 1.0
    if sx < 0.999:
        nw = max(2, int(960 * sx)); c = c.resize((nw, 560), Image.BICUBIC)
    return c

def frame(t):
    img = BG.copy(); d = ImageDraw.Draw(img)
    tape(img, 150, t); tape(img, 1660, t, dirn=-1)
    # Intro: grosses Warndreieck
    ik = ease((t - TR.st(1) + 0.5) / 0.6)
    if ik < 1:
        a = back(t / 0.5) if t < 0.5 else 1.0
        s = 250 * a * (1 - ik) + 1
        triangle(d, 540, 640 - 120 * ik, s)
        if ik < 0.5:
            f = F(BLACK, 150); txt = '3 FEHLER'; d.text(((W - tw(d, txt, f)) / 2, 980), txt, font=f, fill=YEL)
            for k, ln in enumerate(['beim Heizungstausch, die', 'richtig Geld kosten']):
                f = F(BOLD, 54); d.text(((W - tw(d, ln, f)) / 2, 1170 + k * 70), ln, font=f, fill=WHITE)
    if t >= TR.st(1) - 0.5:
        # Baustellenfoto oben
        a = eout((t - TR.st(1) + 0.5) / 0.6)
        fr = C_WP.at(((t - TR.st(1)) * 0.6) % 6.9).crop((0, 215, 1080, 605))
        h = int(390 * a)
        if h > 4: img.paste(fr.crop((0, 0, 1080, h)), (0, 240))
        d.rectangle([0, 240 + h, W, 240 + h + 8], fill=(20, 20, 20))
        # Zaehler
        for k in range(3):
            on = t >= TR.st(1 + k) - 0.3
            triangle(d, 760 + k * 100, 680, 36, fill=YEL if on else (90, 90, 90), mark=False)
            f = F(BLACK, 30); d.text((760 + k * 100 - 9, 676), str(k + 1), font=f, fill=(20, 20, 20))
    # Fehlerkarten
    for i in range(3):
        st = TR.st(1 + i); en = TR.en(1 + i)
        if t < st - 0.4: continue
        nxt = TR.st(2 + i) - 0.4 if i < 2 else TR.st(4) - 0.4
        if t > nxt + 0.6: continue
        ein = eout((t - st + 0.4) / 0.5); aus = ease((t - nxt) / 0.5) if t > nxt else 0
        flip = clamp((t - (en - 0.2)) / 0.45)
        c = errcard(i, t, flip)
        x = 540 - c.width / 2 + (1 - ein) * 1100 - aus * 1200; y = 780
        img.paste(c, (int(x), y), c)
        # rotes X
        xk = clamp((t - st - 0.9) / 0.25)
        if xk > 0 and flip < 0.5 and aus == 0:
            sz = int(lerp(320, 170, eout(xk))); xx = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); xd = ImageDraw.Draw(xx)
            wv = max(10, sz // 7); xd.line([(wv, wv), (sz - wv, sz - wv)], fill=RED + (235,), width=wv); xd.line([(sz - wv, wv), (wv, sz - wv)], fill=RED + (235,), width=wv)
            img.paste(xx, (int(860 - sz / 2 + (1 - ein) * 1100), int(860 - sz / 2)), xx)
    # Schluss
    if t >= TR.st(4) - 0.3:
        k = eout((t - TR.st(4) + 0.3) / 0.6)
        c = Image.new('RGBA', (960, 620), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle([0, 0, 959, 619], 34, fill=(250, 250, 246))
        cd.text((56, 60), 'Von Anfang an', font=F(BLACK, 84), fill=NAVY); cd.text((56, 160), 'richtig.', font=F(BLACK, 84), fill=GREEN)
        for j in range(3):
            cx = 90 + j * 110; cd.ellipse([cx - 40, 300, cx + 40, 380], fill=GREEN); cd.line([(cx - 20, 340), (cx - 4, 358), (cx + 22, 322)], fill=WHITE, width=9)
        lg = logo(330); c.alpha_composite(lg, (56, 450))
        img.paste(c, (60, int(780 + (1 - k) * 1100)), c)
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('FE', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_FE_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
