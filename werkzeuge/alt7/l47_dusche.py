# L47 Team Wanne gegen Team Dusche: Vergleichs-Schieber, Vorteils-Chips, Fliesen-Zoom, Chat-Eingabe als Abschluss
from kit import *
S = ["Wanne oder begehbare Dusche? Die Frage hören wir ständig.", "Unsere Antwort: Dusche, vor allem wenn das Bad sowieso neu gemacht wird.",
     "Kein Einstieg über den Rand.", "Leicht zu putzen.", "Und das Bad wirkt größer.", "Die Fliesen macht unser eigener Fliesenleger.",
     "Schreib uns Dusche, und wir planen mit dir."]
D = [3.518, 3.784, 1.375, 0.86, 1.246, 2.12, 2.155]
TR = Track(S, D, start=0.5, gaps=[0.5, 0.5, 0.35, 0.35, 0.6, 0.6], tail=1.9)
WAN = cover(load('bad-serie/fotos/Mair_Bad_04ef2100.jpg'), 1188, 2112, 0.36, 0.5)
DUS = cover(load('bad-serie/fotos/Mair_Bad_e5a0ff98.jpg'), 1188, 2112, 0.5, 0.5)
MOS = cover(load('bad-serie/fotos/Mair_Bad_e5a0ff98.jpg'), 1296, 2304, 0.5, 0.45)

def kb(im, t, z0, z1, T, fx=0.5, fy=0.5):
    z = lerp(z0, z1, clamp(t / T)); w, h = int(W * 1.1 / z), int(H * 1.1 / z)
    x = int((im.width - w) * fx); y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)

def pill(d, x, y, txt, bg, fg, size=34, anchor='l'):
    f = F(BLACK, size); w = tw(d, txt, f) + 52
    if anchor == 'r': x = x - w
    d.rounded_rectangle([x, y, x + w, y + size + 34], (size + 34) // 2, fill=bg); d.text((x + 26, y + 14), txt, font=f, fill=fg)
    return x, w

def icon(d, kind, cx, cy, col):
    if kind == 0:   # Stufe weg: Linie eben
        d.line([(cx - 26, cy + 12), (cx + 26, cy + 12)], fill=col, width=7); d.line([(cx - 26, cy - 4), (cx - 6, cy - 4), (cx - 6, cy + 12)], fill=(200, 80, 70), width=5)
        d.line([(cx - 30, cy - 18), (cx - 2, cy + 8)], fill=(200, 80, 70), width=5)
    elif kind == 1:  # Glanz
        for a, r in ((0, 22), (1, 12)):
            x, y = cx - 8 + a * 22, cy - 6 + a * 14
            d.polygon([(x, y - r), (x + r * 0.3, y - r * 0.3), (x + r, y), (x + r * 0.3, y + r * 0.3), (x, y + r), (x - r * 0.3, y + r * 0.3), (x - r, y), (x - r * 0.3, y - r * 0.3)], fill=col)
    else:  # Pfeile auseinander
        d.line([(cx - 28, cy), (cx + 28, cy)], fill=col, width=6)
        d.polygon([(cx - 32, cy), (cx - 18, cy - 12), (cx - 18, cy + 12)], fill=col); d.polygon([(cx + 32, cy), (cx + 18, cy - 12), (cx + 18, cy + 12)], fill=col)

def subtitle(img, t, y=1470):
    i = TR.cur(t); s = TR.S[i]
    if not (s['t0'] - 0.1 <= t <= s['t1'] + 0.3) or i in (2, 3, 4, 6): return
    d = ImageDraw.Draw(img, 'RGBA'); f = F(BOLD, 46); lines = wrap(d, s['text'], f, 900)
    for k, ln in enumerate(lines):
        w = tw(d, ln, f); x = (W - w) / 2; yy = y + k * 66
        d.rounded_rectangle([x - 18, yy - 6, x + w + 18, yy + 58], 12, fill=(0, 0, 0, 170))
        d.text((x, yy), ln, font=f, fill=WHITE)

def frame(t):
    t5 = TR.st(5) - 0.35
    if t < t5:
        # Schieberposition
        if t < TR.st(1) - 0.1: sx = 540 + 150 * math.sin(t * 2.2) * ease(t / 0.8)
        else:
            k = ease((t - TR.st(1) + 0.1) / 1.1); s0 = 540 + 150 * math.sin((TR.st(1) - 0.1) * 2.2)
            sx = lerp(s0, -40, k)
        a = kb(WAN, t, 1.0, 1.06, 12, 0.4); b = kb(DUS, t, 1.0, 1.08, 12)
        img = b.copy(); sxi = int(clamp(sx, 0, W))
        if sxi > 0: img.paste(a.crop((0, 0, sxi, H)), (0, 0))
        d = ImageDraw.Draw(img, 'RGBA')
        d.rectangle([0, 0, W, 330], fill=(0, 0, 0, 70))
        if sx > -30:
            d.rectangle([sxi - 3, 0, sxi + 3, H], fill=WHITE)
            d.ellipse([sxi - 46, 900, sxi + 46, 992], fill=WHITE)
            d.polygon([(sxi - 30, 946), (sxi - 12, 932), (sxi - 12, 960)], fill=NAVY); d.polygon([(sxi + 30, 946), (sxi + 12, 932), (sxi + 12, 960)], fill=NAVY)
        won = ease((t - TR.st(1) - 0.6) / 0.4)
        if sx > 40: pill(d, 50, 220, 'TEAM WANNE', (255, 255, 255, 235), NAVY)
        x, w = pill(d, 1030, 220, 'TEAM DUSCHE', (150, 200, 40, 255) if won > 0 else (255, 255, 255, 235), NAVY, 34 + int(8 * won), 'r')
        if won > 0:
            d.ellipse([x - 70, 222, x - 14, 278], fill=GREEN); d.line([(x - 56, 250), (x - 46, 262), (x - 28, 238)], fill=WHITE, width=6)
        # Vorteils-Chips
        for i in range(3):
            st = TR.st(2 + i)
            if t < st - 0.2: continue
            e = back((t - st + 0.2) / 0.45); y = 1020 + i * 120
            x0 = int(-700 + 760 * e)
            d.rounded_rectangle([x0, y, x0 + 640, y + 100], 50, fill=(255, 255, 255, 240))
            icon(d, i, x0 + 62, y + 50, GREEN)
            d.text((x0 + 118, y + 26), ['Kein Einstieg über den Rand', 'Leicht zu putzen', 'Bad wirkt größer'][i], font=F(BOLD, 40), fill=NAVY)
        subtitle(img, t)
    else:
        lt = t - t5
        img = kb(MOS, lt, 1.35, 1.7, 4.5, 0.5, 0.42)
        if lt < 0.35:
            prev = frame_prev(t5 - 0.001); img = Image.blend(prev, img, ease(lt / 0.35))
        d = ImageDraw.Draw(img, 'RGBA')
        if t < TR.st(6) - 0.3:
            a = ease((lt - 0.3) / 0.4)
            d.rounded_rectangle([60, 1080, 60 + 760 * a, 1250], 24, fill=(255, 255, 255, 235))
            if a > 0.95:
                d.text((96, 1102), 'Fliesen vom', font=F(SEMI, 40), fill=(90, 100, 120))
                d.text((96, 1152), 'eigenen Fliesenleger', font=F(BLACK, 52), fill=GREEN)
            subtitle(img, t)
        else:
            k = ease((t - TR.st(6) + 0.3) / 0.5)
            d.rectangle([0, 0, W, H], fill=(10, 18, 32, int(150 * k)))
            lg = logo(360); ly = int(540 - 60 * (1 - k)); d.rounded_rectangle([330, ly - 30, 750, ly + lg.height + 30], 30, fill=(255, 255, 255, int(245 * k))); img.paste(lg, (360, ly), lg)
            d.text((120, 820), 'Schreib uns', font=F(SEMI, 56), fill=(255, 255, 255, int(255 * k)))
            # Chat-Eingabe mit Tipp-Animation
            y = 920; d.rounded_rectangle([90, y, 990, y + 130], 65, fill=(255, 255, 255, int(250 * k)))
            word = 'DUSCHE'; n = int(clamp((t - TR.st(6) - 0.2) / 0.9) * len(word) + 0.001)
            d.text((150, y + 30), word[:n], font=F(BLACK, 64), fill=NAVY)
            if n < len(word) and int(t * 3) % 2 == 0:
                cx = 150 + tw(d, word[:n], F(BLACK, 64)) + 6; d.rectangle([cx, y + 34, cx + 5, y + 100], fill=NAVY)
            sent = t > TR.st(6) + 1.3
            d.ellipse([880, y + 15, 980, y + 115], fill=GREEN if sent else (190, 200, 210))
            d.polygon([(905, y + 45), (955, y + 65), (905, y + 85), (915, y + 65)], fill=WHITE)
            if sent:
                e = eout((t - TR.st(6) - 1.3) / 0.4)
                d.rounded_rectangle([300, int(y + 190 - 30 * e), 990, int(y + 300 - 30 * e)], 30, fill=(150, 200, 40, int(255 * e)))
                d.text((340, int(y + 214 - 30 * e)), '…und wir planen mit dir.', font=F(BOLD, 44), fill=(12, 24, 40, int(255 * e)))
    return img

_prev = {}
def frame_prev(t):
    if 'p' not in _prev: _prev['p'] = frame(t)
    return _prev['p']

if __name__ == '__main__':
    if sys.argv[1] == 'render': render('DU', frame, TR.end)
    elif sys.argv[1] == 'still':
        for x in sys.argv[2:]: frame(float(x)).save(f'{HERE}/prev_DU_{x}.jpg', quality=85)
    elif sys.argv[1] == 'info': print(TR.end, [round(s['t0'], 2) for s in TR.S])
