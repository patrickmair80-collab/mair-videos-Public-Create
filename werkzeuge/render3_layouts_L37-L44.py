# Neue Layouts L37-L42 (09.10.2026): Kino, Notizbuch, Magazin, Videoanruf, Quiz, Lichtkegel
import os, sys, json, math, re, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
FPS = 30
INTER_BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
INTER_BOLD = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
INTER_REG = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SERIF_B = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
for p in ('/usr/share/fonts/opentype/inter/Inter-Regular.otf',):
    if not os.path.exists(p): INTER_REG = INTER_BOLD
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
GREEN = (80, 144, 24); LIME = (150, 200, 40); NAVY = (12, 24, 40); WHITE = (255, 255, 255)
TIM = json.load(open(D + '/timings3.json'))
LOGO = Image.open(D + '/../ds/project/assets/Logos/mair-logo.png').convert('RGBA')
la = np.asarray(LOGO).astype(float)
la[la[..., 3] < 70, 3] = 0
LOGO = Image.fromarray(np.uint8(la), 'RGBA')
g = (abs(la[..., 0] - la[..., 1]) < 18) & (abs(la[..., 1] - la[..., 2]) < 18) & (la[..., 0] < 200)
la2 = la.copy(); la2[g, :3] = 245
LOGOW = Image.fromarray(np.uint8(la2), 'RGBA')
UP = '/root/.claude/uploads/21fb353a-f208-59b6-a114-5f5699f3e0dd/'
SAM = Image.open(UP + '4d0a22c8-image.jpg').convert('RGB')
I1 = Image.open(UP + 'cc3a6a72-image.png').convert('RGB')
I3 = Image.open(UP + '8735cdb2-image.png').convert('RGB')
P = {'van': I1.crop((0, 0, 1024, 466)), 'worker': I1.crop((0, 471, 1024, 982)), 'app': I3.crop((0, 344, 765, 664)),
     'wet': I3.crop((772, 344, 1536, 664)), 'indoor': I3.crop((0, 670, 765, 1024)), 'house': I3.crop((772, 670, 1536, 1024))}
BADF = '/home/claude/mair-videos-public-create/bad-bilder/'
def _bad(name):
    for root in (BADF, D + '/', '/home/claude/mair-videos-public-create/'):
        for dp, dn, fn in os.walk(root):
            if name in fn: return Image.open(os.path.join(dp, name)).convert('RGB')
    return None
BAD_WASCH = _bad('Mair_Bad_9bb2d176.jpg'); BAD_DUSCHE = _bad('Mair_Bad_e5a0ff98.jpg')
import importlib.util
if BAD_WASCH is None or BAD_DUSCHE is None:
    spec = importlib.util.spec_from_file_location('r2', D + '/render2.py'); r2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r2)
    BAD_WASCH, BAD_DUSCHE = r2.BAD_WASCH, r2.BAD_DUSCHE

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def back(x):
    x = max(0, min(1, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def src(folder, tsrc, maxn):
    n = min(max(1, int(tsrc * FPS) + 1), maxn)
    return Image.open(f'{D}/{folder}/f_{n:04d}.jpg').convert('RGB')
def disp(w): return re.sub(r'Maier', 'Mair', w)
def clean(w): return re.sub(r'[.,!?:;]', '', w)

class Track:
    def __init__(self, key):
        self.w = [(a, a + d, t) for a, d, t in TIM[key]['w']]
        self.dur = TIM[key]['dur']
        # Sätze: an . ? ! trennen
        self.sent = []; cur = []
        for x in self.w:
            cur.append(x)
            if x[2][-1] in '.?!': self.sent.append(cur); cur = []
        if cur: self.sent.append(cur)
    def WT(self, word, after=0.0, nth=0):
        c = 0
        for a, b, t in self.w:
            if a >= after - 1e-6 and clean(t).lower() == word.lower():
                if c == nth: return a
                c += 1
        raise KeyError(word)
    def cur_sent(self, t, hold=0.5):
        for i, s in enumerate(self.sent):
            end = self.sent[i + 1][0][0] if i + 1 < len(self.sent) else s[-1][1] + hold
            if s[0][0] - 0.08 <= t < min(end, s[-1][1] + hold): return s
        return None
    def chunks(self, maxw=4):
        out = []
        for s in self.sent:
            for i in range(0, len(s), maxw): out.append(s[i:i + maxw])
        return out
    def cur_chunk(self, t, maxw=4, hold=0.45):
        ch = self.chunks(maxw)
        for i, c in enumerate(ch):
            end = ch[i + 1][0][0] if i + 1 < len(ch) else c[-1][1] + hold
            if c[0][0] - 0.06 <= t < min(end, c[-1][1] + hold): return c
        return None

def ki(d, x=40, y=212, txt='KI-Video', dark=True):
    f = F(INTER_BOLD, 24); w = d.textlength(txt, font=f)
    d.rounded_rectangle([x, y, x + w + 28, y + 36], 18, fill=(20, 20, 20) if dark else (240, 240, 240))
    d.text((x + 14, y + 4), txt, font=f, fill=(230, 230, 230) if dark else (30, 30, 30))

def contain(img, W, H, bg=(255, 255, 255)):
    r = min(W / img.width, H / img.height); im = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
    c = Image.new('RGB', (W, H), bg); c.paste(im, ((W - im.width) // 2, (H - im.height) // 2)); return c

def cover(img, W, H):
    r = max(W / img.width, H / img.height); im = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - H) // 2; return im.crop((x, y, x + W, y + H))

def kenburns(img, W, H, k, z0=1.0, z1=1.08, dx=0.0):
    z = z0 + (z1 - z0) * k; r = max(W / img.width, H / img.height) * z
    im = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.BILINEAR)
    x = int((im.width - W) / 2 + dx * (im.width - W) / 2 * (2 * k - 1)); y = (im.height - H) // 2
    x = max(0, min(im.width - W, x)); return im.crop((x, y, x + W, y + H))

def grain(img, amt=10, seed=0):
    rng = np.random.default_rng(seed); a = np.asarray(img).astype(np.int16)
    n = rng.integers(-amt, amt + 1, size=a.shape[:2], dtype=np.int16)[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))

def logo(w, white=True):
    L = LOGOW if white else LOGO
    return L.resize((w, int(w * L.height / L.width)), Image.LANCZOS)

def circle_mask(size, feather=2):
    m = Image.new('L', (size * 4, size * 4), 0); ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    return m.resize((size, size), Image.LANCZOS)

def round_mask(w, h, r):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); return m

# ====================== L37 Kino-Breitbild (Reel A) ======================
def reel_A(n):
    T = TRK['A']; t = n / FPS
    s_ein = T.WT('Ein'); s_rauf = T.WT('Rauf'); s_filter = T.WT('Filter'); s_jetzt = T.WT('Jetzt')
    s_fuer = T.WT('für'); s_heiz = T.WT('Heizen'); s_mair = T.WT('Maier')
    SEG = [(0, s_ein - 0.1, 'v', 0.0, 1.27, 'Der Staub'), (s_ein - 0.1, s_rauf - 0.1, 'img', 'van', None, 'Die Anfahrt'),
           (s_rauf - 0.1, s_filter - 0.1, 'v', 2.87, 4.47, 'Vor Ort'), (s_filter - 0.1, s_jetzt - 0.1, 'v', 4.47, 6.13, 'Die Reinigung'),
           (s_jetzt - 0.1, s_fuer - 0.1, 'v', 6.13, 9.1, 'Frische Luft'), (s_fuer - 0.1, s_heiz - 0.1, 'v', 9.1, 9.85, 'Die Familie'),
           (s_heiz - 0.1, s_mair - 0.15, 'img', 'sam', None, 'Sommer und Winter'), (s_mair - 0.15, 999, 'end', None, None, '')]
    si = [i for i, s in enumerate(SEG) if s[0] <= t < s[1]][0]; s = SEG[si]; lt = t - s[0]
    img = Image.new('RGB', (1080, 1920), (0, 0, 0))
    if s[2] == 'end':
        # Abspann
        d = ImageDraw.Draw(img)
        van = kenburns(P['van'], 1080, 600, min(1, lt / 4), 1.02, 1.1)
        van = Image.blend(van, Image.new('RGB', van.size, (0, 0, 0)), 0.35)
        img.paste(van, (0, 660))
        a = ease(lt / 0.6)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        txt = 'EIN EINSATZ VON'; f = F(SERIF, 34); w = ld.textlength(txt, font=f)
        ld.text((540 - w / 2, 330), txt, font=f, fill=(220, 210, 190, int(255 * a)))
        L = logo(520); m = L.split()[3].point(lambda v: int(v * a)); lay.paste(L, (540 - 260, 400), m)
        f2 = F(SERIF, 36); t2 = 'Heizung · Sanitär · Klima'; w = ld.textlength(t2, font=f2)
        ld.text((540 - w / 2, 1300), t2, font=f2, fill=(230, 220, 200, int(255 * a)))
        if lt > 1.2:
            b = ease((lt - 1.2) / 0.5); f3 = F(SERIF_B, 64); t3 = 'Kommentiere KLIMA'; w = ld.textlength(t3, font=f3)
            ld.text((540 - w / 2, 1380), t3, font=f3, fill=(150, 200, 40, int(255 * b)))
            f4 = F(SERIF, 32); t4 = 'individuelles Angebot · 09132 / 74 97 5-27'; w = ld.textlength(t4, font=f4)
            ld.text((540 - w / 2, 1480), t4, font=f4, fill=(220, 210, 190, int(255 * b)))
        img.paste(lay, (0, 0), lay)
    else:
        if s[2] == 'v':
            ts = s[3] + (lt / max(0.01, s[1] - s[0])) * (s[4] - s[3])
            fr = src('s3', ts, 522)
            import importlib
            fr = RC(fr)
            band = fr.crop((0, 635, 1080, 1235))
        else:
            base = P['van'] if s[3] == 'van' else SAM
            band = kenburns(base, 1080, 600, min(1, lt / max(0.5, s[1] - s[0])), 1.0, 1.1, 0.4)
        band = grain(band, 7, n)
        img.paste(band, (0, 660))
        d = ImageDraw.Draw(img)
        # Kapitel im oberen Balken
        f = F(SERIF, 30); cap = f'KAPITEL {si + 1}'; a = ease(lt / 0.4)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        w = ld.textlength(cap, font=f); ld.text((540 - w / 2, 470), cap, font=f, fill=(190, 180, 160, int(255 * a)))
        f2 = F(SERIF_B, 64); w = ld.textlength(s[5], font=f2); ld.text((540 - w / 2, 520), s[5], font=f2, fill=(255, 248, 230, int(255 * a)))
        img.paste(lay, (0, 0), lay)
    # Untertitel unten (Satz, aktives Wort hell)
    S = T.cur_sent(t)
    if S and s[2] != 'end':
        d = ImageDraw.Draw(img); f = F(SERIF, 44)
        words = [disp(x[2]) for x in S]; lines = [[]]
        for i, w_ in enumerate(words):
            test = ' '.join(words[j] for j in lines[-1] + [i])
            if d.textlength(test, font=f) > 900 and lines[-1]: lines.append([i])
            else: lines[-1].append(i)
        y = 1300
        for ln in lines:
            txt = ' '.join(words[j] for j in ln); x = 540 - d.textlength(txt, font=f) / 2
            for j in ln:
                a0, b0, _ = S[j]; spoken = t >= a0 - 0.02
                d.text((x, y), words[j], font=f, fill=(255, 236, 170) if (spoken and t < b0 + 0.1) else ((240, 236, 225) if spoken else (120, 115, 105)))
                x += d.textlength(words[j] + ' ', font=f)
            y += 58
    ki(ImageDraw.Draw(img), 40, 212)
    return img

# ====================== L38 Notizbuch + Polaroid (Reel B) ======================
PAPER = None
def paper():
    global PAPER
    if PAPER is None:
        im = Image.new('RGB', (1080, 1920), (246, 240, 226)); d = ImageDraw.Draw(im)
        for y in range(160, 1920, 64): d.line([(0, y), (1080, y)], fill=(214, 224, 236), width=2)
        d.line([(110, 0), (110, 1920)], fill=(232, 160, 160), width=3)
        a = np.asarray(im).astype(np.int16); rng = np.random.default_rng(3)
        a = a + rng.integers(-6, 7, size=a.shape[:2])[..., None]
        PAPER = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return PAPER.copy()

def polaroid(photo, w=820, cap=None, angle=0):
    pw, ph = w + 60, w + 190
    card = Image.new('RGBA', (pw, ph), (255, 255, 255, 255)); card.paste(photo.resize((w, w), Image.LANCZOS), (30, 30))
    if cap:
        d = ImageDraw.Draw(card); f = F(SERIF, 46); tw = d.textlength(cap, font=f); d.text(((pw - tw) / 2, w + 70), cap, font=f, fill=(40, 40, 50))
    sh = Image.new('RGBA', (pw + 80, ph + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([40, 50, 40 + pw, 50 + ph], fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(16)); sh.paste(card, (40, 40), card)
    return sh.rotate(angle, resample=Image.BICUBIC, expand=True)

def tick(d, x, y, k, col=(60, 150, 40)):
    p1 = (x, y + 18); p2 = (x + 14, y + 34); p3 = (x + 44, y - 4)
    if k <= 0: return
    k = min(1.0, k)
    a = min(1, k * 2); d.line([p1, (p1[0] + (p2[0] - p1[0]) * a, p1[1] + (p2[1] - p1[1]) * a)], fill=col, width=8)
    if k > 0.5:
        b = (k - 0.5) * 2; d.line([p2, (p2[0] + (p3[0] - p2[0]) * b, p2[1] + (p3[1] - p2[1]) * b)], fill=col, width=8)

def highlight_text(img, S, t, y, size=54):
    d = ImageDraw.Draw(img); f = F(INTER_BLACK, size)
    words = [disp(x[2]) for x in S]; lines = [[]]
    for i in range(len(words)):
        test = ' '.join(words[j] for j in lines[-1] + [i])
        if d.textlength(test, font=f) > 860 and lines[-1]: lines.append([i])
        else: lines[-1].append(i)
    for ln in lines:
        x = 150
        for j in ln:
            a0, b0, _ = S[j]; w = d.textlength(words[j], font=f)
            if t >= a0 - 0.02:
                k = min(1, (t - a0 + 0.02) / 0.18)
                d.rectangle([x - 6, y + size * 0.45, x - 6 + (w + 12) * k, y + size * 1.12], fill=(255, 230, 90))
            d.text((x, y), words[j], font=f, fill=(35, 35, 45) if t >= a0 - 0.02 else (170, 165, 155))
            x += w + d.textlength(' ', font=f)
        y += size + 22

def reel_B(n):
    T = TRK['B']; t = n / FPS
    s_halt = T.WT('Halterung'); s_leit = T.WT('Leitungen'); s_laeuft = T.WT('läuft'); s_echt = T.WT('echt'); s_mair = T.WT('Maier')
    img = paper(); d = ImageDraw.Draw(img)
    d.text((150, 250), 'Klima-Montage', font=F(SERIF_B, 64), fill=(35, 40, 60))
    d.text((150, 330), 'in Miniatur', font=F(SERIF, 48), fill=(90, 95, 110))
    if t < s_echt - 0.15:
        fr = src('s1', min(t, 9.3), 280).crop((150, 620, 930, 1400))
        ang = 2.5 * math.sin(t * 0.9) - 1.5
        pol = polaroid(fr, 700, None, ang); img.paste(pol, (540 - pol.width // 2 + 20, 400), pol)
        # Checkliste
        items = [('Auspacken', T.WT('auspacken')), ('Halterung', s_halt), ('Leitungen', s_leit), ('Läuft', s_laeuft)]
        y0 = 1420; f = F(SERIF, 46)
        for i, (lab, ts) in enumerate(items):
            x = 150 + (i % 2) * 430; y = y0 + (i // 2) * 90
            d.rounded_rectangle([x, y, x + 46, y + 46], 6, outline=(60, 60, 75), width=4)
            tick(d, x + 2, y + 4, (t - ts) / 0.35)
            d.text((x + 66, y - 4), lab, font=f, fill=(40, 40, 55) if t >= ts else (130, 128, 120))
    elif t < s_mair - 0.15:
        lt = t - (s_echt - 0.15)
        p1 = polaroid(contain(SAM, 900, 900, (235, 238, 242)), 600, 'in echt', -6 + 2 * ease(lt / 0.6)); img.paste(p1, (30, 400), p1)
        if lt > 0.8:
            k = back((lt - 0.8) / 0.5); p2 = polaroid(cover(P['van'], 900, 900), int(520 * max(0.3, min(1.1, k))), 'wir kommen', 7)
            img.paste(p2, (1080 - p2.width - 10, 960), p2)
    else:
        lt = t - (s_mair - 0.15)
        p1 = polaroid(contain(SAM, 900, 900, (235, 238, 242)), 560, None, -5); img.paste(p1, (60, 430), p1)
        k = back(lt / 0.45)
        note = Image.new('RGBA', (640, 560), (0, 0, 0, 0)); nd = ImageDraw.Draw(note)
        nd.rectangle([20, 20, 620, 540], fill=(255, 232, 90)); L = logo(380, False); note.paste(L, (130, 60), L)
        nd.text((60, 250), 'Kommentiere', font=F(SERIF, 52), fill=(40, 40, 50)); nd.text((60, 320), 'KLIMA', font=F(INTER_BLACK, 110), fill=(30, 30, 40))
        nd.text((60, 460), '09132 / 74 97 5-27', font=F(INTER_BOLD, 40), fill=(40, 40, 50))
        s = max(0.05, min(1.08, k)); note = note.resize((int(640 * s), int(560 * s))).rotate(4, expand=True, resample=Image.BICUBIC)
        img.paste(note, (500 - note.width // 2 + 120, 1000 - note.height // 2 + 150), note)
        # Klebestreifen
        d.rectangle([600, 830, 760, 880], fill=(230, 225, 210))
    S = T.cur_sent(t)
    if S and t < s_mair - 0.15: highlight_text(img, S, t, 1640, 50)
    ki(ImageDraw.Draw(img), 40, 212, dark=False)
    return img

# ====================== L39 Magazin-Titelseite (Reel C) ======================
ISSUES = [((14, 30, 52), (150, 200, 40)), ((236, 232, 222), (80, 144, 24)), ((150, 200, 40), (12, 24, 40)),
          ((18, 18, 18), (255, 214, 0)), ((40, 110, 180), (255, 255, 255)), ((12, 24, 40), (150, 200, 40))]
def reel_C(n):
    T = TRK['C']; t = n / FPS
    st = [0, T.WT('Viessmann') - 0.25, T.WT('Gesteuert') - 0.25, T.WT('Leise') - 0.25, T.WT('Heizung') - 0.25, T.WT('Maier') - 0.25]
    shots = ['van', 'worker', 'app', 'wet', 'indoor', 'house']
    heads = [('Wir kommen', 'zu dir.'), ('Sauber', 'eingebaut.'), ('Alles am', 'Handy.'), ('Leise im', 'Winter.'), ('Alles aus', 'einer Hand.'), ('Kommentiere', 'WÄRME')]
    kick = ['Wärmepumpe', 'Meisterbetrieb', 'Steuerung', 'Sparsam', 'Heizung · Sanitär · Klima', 'Mair Gebäudetechnik']
    i = max(j for j in range(6) if t >= st[j]); lt = t - st[i]
    def page(i, lt):
        bg, ac = ISSUES[i]; dark = sum(bg) < 300
        fg = (255, 255, 255) if dark else (20, 24, 32)
        pg = Image.new('RGB', (1080, 1920), bg); d = ImageDraw.Draw(pg)
        d.text((52, 230), 'MAIR', font=F(INTER_BLACK, 250), fill=fg)
        d.text((60, 500), f'GEBÄUDETECHNIK MAGAZIN · OKTOBER 2026 · NR. {i + 1}', font=F(INTER_BOLD, 28), fill=ac)
        ph = kenburns(P[shots[i]], 980, 640, min(1, lt / 5), 1.0, 1.08, 0.5)
        pg.paste(ph, (50, 560))
        d.rectangle([50, 1200, 1030, 1206], fill=ac)
        d.text((60, 1230), kick[i].upper(), font=F(INTER_BOLD, 34), fill=ac)
        h1, h2 = heads[i]
        d.text((56, 1280), h1, font=F(INTER_BLACK, 112), fill=fg)
        d.text((56, 1400), h2, font=F(INTER_BLACK, 112), fill=ac)
        if i == 5:
            d.text((60, 1540), 'individuelles Angebot · 09132 / 74 97 5-27', font=F(INTER_BOLD, 38), fill=fg)
            L = logo(300, True) if dark else logo(300, False); pg.paste(L, (720, 1590), L)
        # Preis-Sticker
        s = Image.new('RGBA', (230, 230), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
        sd.ellipse([0, 0, 229, 229], fill=ac + (255,)); tc = (12, 24, 40) if sum(ac) > 400 else (255, 255, 255)
        for k_, (tx, sz) in enumerate((('GRATIS', 40), ('Beratung', 34), ('vor Ort', 34))):
            w = sd.textlength(tx, font=F(INTER_BLACK, sz)); sd.text(((230 - w) / 2, 52 + k_ * 44), tx, font=F(INTER_BLACK, sz), fill=tc)
        s = s.rotate(-12, resample=Image.BICUBIC); pg.paste(s, (820, 470), s)
        return pg
    img = page(i, lt)
    if i > 0 and lt < 0.45:
        prev = page(i - 1, t - st[i - 1]); k = ease(lt / 0.45)
        x = int(1080 * (1 - k)); comp = prev.copy(); comp.paste(img.crop((0, 0, 1080 - x, 1920)), (x, 0))
        sh = Image.new('RGBA', (60, 1920), (0, 0, 0, 0))
        for j in range(60): ImageDraw.Draw(sh).line([(j, 0), (j, 1920)], fill=(0, 0, 0, int(120 * (1 - j / 60))))
        if x > 0: comp.paste(sh, (max(0, x - 60), 0), sh)
        img = comp
    # Zeile mit gesprochenem Text
    c = T.cur_chunk(t, 5)
    if c and i < 5:
        d = ImageDraw.Draw(img); f = F(INTER_BOLD, 40); x = 60; y = 1560
        bg, ac = ISSUES[i]; fg = (255, 255, 255) if sum(bg) < 300 else (20, 24, 32)
        for a0, b0, w in c:
            ww = disp(w); d.text((x, y), ww, font=f, fill=ac if a0 <= t < b0 + 0.12 else fg); x += d.textlength(ww + ' ', font=f)
    bg, _ = ISSUES[i]; ki(ImageDraw.Draw(img), 40, 180, dark=sum(bg) > 300)
    return img

# ====================== L40 Videoanruf vom Außengerät (Reel D) ======================
def face_crop(t, t0, t1):
    ts = max(0, (t - t0) / max(0.1, (t1 - t0))) * 9.3
    fr = src('s4', ts, 280); return fr.crop((0, 640, 1080, 1900))

def reel_D(n):
    T = TRK['D']; t = n / FPS
    fo = TIM['D']['face_off']; fe = TIM['D']['face_end']; no = TIM['D']['narr_off']
    img = Image.new('RGB', (1080, 1920), (18, 18, 22))
    if t < fo - 0.1:
        # klingelt
        bg = src('s4', 0, 280).resize((270, 480)).filter(ImageFilter.GaussianBlur(8)).resize((1080, 1920))
        img = Image.blend(bg, Image.new('RGB', bg.size, (10, 12, 18)), 0.55); d = ImageDraw.Draw(img)
        av = src('s4', 0.2, 280).crop((140, 560, 940, 1360)).resize((360, 360)); m = circle_mask(360)
        pulse = 1 + 0.06 * math.sin(t * 9)
        for r_, al in ((230 * pulse, 40), (260 * pulse, 20)):
            d.ellipse([540 - r_, 760 - r_, 540 + r_, 760 + r_], outline=(255, 255, 255), width=3)
        img.paste(av, (360, 580), m)
        for txt, f, y, col in (('Dein Außengerät', F(INTER_BLACK, 70), 1010, WHITE), ('ruft an …', F(INTER_BOLD, 40), 1100, (200, 200, 210))):
            w = d.textlength(txt, font=f); d.text((540 - w / 2, y), txt, font=f, fill=col)
        for cx, col, lab in ((300, (230, 60, 60), 'Ablehnen'), (780, (60, 190, 90), 'Annehmen')):
            r_ = 70 * (1.12 if (cx == 780 and t > fo - 0.6) else 1)
            d.ellipse([cx - r_, 1560 - r_, cx + r_, 1560 + r_], fill=col)
            w = d.textlength(lab, font=F(INTER_BOLD, 32)); d.text((cx - w / 2, 1650), lab, font=F(INTER_BOLD, 32), fill=WHITE)
    elif t < no - 0.2:
        d = ImageDraw.Draw(img)
        v = face_crop(t, fo, fe + 0.6).resize((1000, 1167))
        img.paste(v, (40, 270), round_mask(1000, 1167, 46))
        sec = int(t - fo); d.text((60, 190), f'Dein Außengerät  ·  00:{sec:02d}', font=F(INTER_BOLD, 34), fill=(220, 220, 228))
        # eigenes Bild (Mair)
        tile = Image.new('RGB', (250, 330), GREEN); L = logo(200); tile.paste(L, (25, 120), L)
        img.paste(tile, (770, 1080), round_mask(250, 330, 26))
        # Bedienleiste
        for cx, col in ((300, (60, 62, 70)), (540, (60, 62, 70)), (780, (230, 60, 60))):
            d.ellipse([cx - 56, 1690 - 56, cx + 56, 1690 + 56], fill=col)
        # Live-Untertitel im Video
        c = T.cur_chunk(t, 5)
        if c:
            f = F(INTER_BOLD, 50); txt = ' '.join(disp(x[2]) for x in c); w = d.textlength(txt, font=f)
            while w > 900: f = F(INTER_BOLD, f.size - 4); w = d.textlength(txt, font=f)
            lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([540 - w / 2 - 26, 1290, 540 + w / 2 + 26, 1290 + f.size + 34], 20, fill=(0, 0, 0, 170))
            x = 540 - w / 2
            for a0, b0, ww in c:
                ww = disp(ww); ld.text((x, 1305), ww, font=f, fill=(255, 214, 0) if a0 <= t < b0 + 0.1 else WHITE); x += ld.textlength(ww + ' ', font=f)
            img.paste(lay, (0, 0), lay)
        if t > fe - 0.2 and t < no - 0.2:
            k = ease((t - fe + 0.2) / 0.4); lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([90, 1460, 990, 1560], 50, fill=(80, 144, 24, int(235 * k)))
            ld.text((140, 1482), 'Mair Gebäudetechnik ist beigetreten', font=F(INTER_BOLD, 40), fill=(255, 255, 255, int(255 * k))); img.paste(lay, (0, 0), lay)
    else:
        lt = t - (no - 0.2); d = ImageDraw.Draw(img)
        img.paste(kenburns(P['van'], 1080, 760, min(1, lt / 4), 1.0, 1.08), (0, 250))
        d.text((60, 1060), 'Anruf beendet', font=F(INTER_BOLD, 38), fill=(170, 170, 180))
        d.text((60, 1110), 'Außengerät wieder frei.', font=F(INTER_BLACK, 74), fill=WHITE)
        c = T.cur_chunk(t, 4)
        card_y = 1260; d.rounded_rectangle([60, card_y, 1020, card_y + 420], 40, fill=(34, 36, 44))
        L = logo(330); img.paste(L, (100, card_y + 40), L)
        d.text((100, card_y + 200), 'Klima-Service · Reinigung · Wartung', font=F(INTER_BOLD, 36), fill=(200, 200, 210))
        d.text((100, card_y + 260), '09132 / 74 97 5-27', font=F(INTER_BLACK, 56), fill=LIME)
        if t > T.WT('Kommentiere') - 0.1:
            d.rounded_rectangle([100, card_y + 340, 620, card_y + 400], 30, fill=(255, 214, 0)); d.text((126, card_y + 348), 'Kommentiere SAUBER', font=F(INTER_BLACK, 38), fill=NAVY)
        if c:
            txt = ' '.join(disp(x[2]) for x in c); f = F(INTER_BOLD, 44); d.text((60, 1720), txt, font=f, fill=(230, 230, 236))
    ki(ImageDraw.Draw(img), 40, 120)
    return img

# ====================== L41 Quiz (Reel E) ======================
def reel_E(n):
    T = TRK['E']; t = n / FPS
    s_k = T.WT('Kartusche'); s_tropft = T.WT('Tropft'); s_mair = T.WT('Maier')
    img = Image.new('RGB', (1080, 1920), (14, 22, 40)); d = ImageDraw.Draw(img)
    for y in range(0, 1920, 8):
        c = int(14 + 22 * y / 1920); d.line([(0, y), (1080, y)], fill=(c, c + 8, c + 26))
    d.rounded_rectangle([60, 260, 520, 330], 35, fill=(255, 214, 0)); d.text((88, 270), 'QUIZ · Bad-Wissen', font=F(INTER_BLACK, 40), fill=NAVY)
    # Kreis
    R = 400; cx, cy = 540, 780
    if t < s_tropft - 0.15:
        fr = src('s5', min(t, 8.05), 242); ph = fr.crop((20, 480, 820, 1280)).resize((2 * R, 2 * R))
    else:
        ph = kenburns(BAD_WASCH, 2 * R, 2 * R, min(1, (t - s_tropft) / 6), 1.0, 1.1)
    ring = 8 + 3 * math.sin(t * 4)
    d.ellipse([cx - R - ring, cy - R - ring, cx + R + ring, cy + R + ring], fill=(255, 214, 0))
    img.paste(ph, (cx - R, cy - R), circle_mask(2 * R))
    d = ImageDraw.Draw(img)
    if t < s_tropft - 0.15:
        d.text((60, 1240), 'Was mischt warm', font=F(INTER_BLACK, 66), fill=WHITE); d.text((60, 1315), 'und kalt?', font=F(INTER_BLACK, 66), fill=WHITE)
        opts = [('A', 'Ventil'), ('B', 'Kartusche'), ('C', 'Siphon')]
        for i, (k_, o) in enumerate(opts):
            y = 1420 + i * 110; right = (o == 'Kartusche') and t >= s_k
            fill = (60, 170, 80) if right else ((40, 52, 76) if t < s_k else (30, 38, 56))
            d.rounded_rectangle([60, y, 1020, y + 90], 45, fill=fill)
            d.text((96, y + 18), f'{k_})  {o}', font=F(INTER_BOLD, 48), fill=WHITE if (t < s_k or right) else (120, 128, 145))
            if right: tick(d, 940, y + 26, (t - s_k) / 0.3, WHITE)
        if t < s_k:
            k = max(0, 1 - t / s_k); d.rectangle([60, 1760, 60 + 960 * k, 1772], fill=(255, 214, 0))
    elif t < s_mair - 0.15:
        d.text((60, 1240), 'Tropft deiner?', font=F(INTER_BLACK, 76), fill=WHITE)
        chips = [('Armatur tauschen', T.WT('tauschen')), ('Ganzes Bad', T.WT('Bäder')), ('Eigener Fliesenleger', T.WT('Fliesenleger'))]
        for i, (lab, ts) in enumerate(chips):
            if t >= ts - 0.1:
                k = back((t - ts + 0.1) / 0.35); y = 1360 + i * 110
                w = d.textlength(lab, font=F(INTER_BOLD, 48)) + 130
                d.rounded_rectangle([60, y, 60 + w * min(1, k), y + 90], 45, fill=(60, 170, 80))
                if k > 0.6: d.text((100, y + 18), '✓  ' + lab if False else lab, font=F(INTER_BOLD, 48), fill=WHITE); tick(d, 60 + w - 70, y + 26, (t - ts) / 0.3, WHITE)
    else:
        lt = t - (s_mair - 0.15)
        d.text((60, 1240), 'Richtig!', font=F(INTER_BLACK, 110), fill=(255, 214, 0))
        L = logo(420); img.paste(L, (60, 1390), L)
        d.rounded_rectangle([60, 1560, 640, 1650], 45, fill=(255, 214, 0)); d.text((92, 1576), 'Kommentiere BAD', font=F(INTER_BLACK, 50), fill=NAVY)
        d.text((60, 1680), 'mit eigenem Fliesenleger · 09132 / 74 97 5-27', font=F(INTER_BOLD, 34), fill=(210, 215, 228))
        rng = random.Random(7)
        for j in range(40):
            x = rng.randint(40, 1040); y0 = rng.randint(-200, 300); sp = rng.uniform(300, 600)
            y = y0 + sp * lt
            if 0 < y < 1900: d.rectangle([x, y, x + 14, y + 22], fill=rng.choice([(255, 214, 0), (150, 200, 40), (255, 255, 255), (64, 160, 230)]))
    c = T.cur_chunk(t, 6)
    if c and t < s_mair - 0.15:
        txt = ' '.join(disp(x[2]) for x in c); f = F(INTER_REG, 38); w = d.textlength(txt, font=f)
        d.text((540 - w / 2, 1790), txt, font=f, fill=(200, 205, 220))
    ki(ImageDraw.Draw(img), 40, 180)
    return img

# ====================== L42 Lichtkegel + Textring (Reel F) ======================
def text_ring(txt, R, size, ang, col):
    S = 2 * R + 200; lay = Image.new('RGBA', (S, S), (0, 0, 0, 0)); f = F(INTER_BOLD, size)
    n = len(txt); step = 360 / n
    for i, ch in enumerate(txt):
        a = math.radians(ang + i * step); x = S / 2 + R * math.cos(a); y = S / 2 + R * math.sin(a)
        g_ = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0)); ImageDraw.Draw(g_).text((size * 0.5, size * 0.3), ch, font=f, fill=col)
        g_ = g_.rotate(-(ang + i * step) - 90, resample=Image.BICUBIC); lay.paste(g_, (int(x - size), int(y - size)), g_)
    return lay

def reel_F(n):
    T = TRK['F']; t = n / FPS
    s_lust = T.WT('Lust'); s_mair = T.WT('Maier')
    img = Image.new('RGB', (1080, 1920), (8, 16, 30)); d = ImageDraw.Draw(img)
    # Lichtkegel
    glow = Image.new('L', (1080, 1920), 0); gd = ImageDraw.Draw(glow); gd.polygon([(440, 0), (640, 0), (1040, 1500), (40, 1500)], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(60)); img = Image.composite(Image.new('RGB', img.size, (60, 140, 220)), img, glow)
    R = 400; cx, cy = 540, 820
    if t < s_lust - 0.15:
        ph = src('s6', min(t, 8.8), 266).crop((140, 560, 940, 1360)).resize((2 * R, 2 * R)); ring_txt = 'REGENDUSCHE · VON INNEN · MAIR GEBÄUDETECHNIK · '
    elif t < s_mair - 0.15:
        ph = kenburns(BAD_DUSCHE, 2 * R, 2 * R, min(1, (t - s_lust) / 6), 1.0, 1.12); ring_txt = 'DEINE NEUE DUSCHE · BODENGLEICH · EIGENER FLIESENLEGER · '
    else:
        ph = None; ring_txt = 'KOMMENTIERE DUSCHE · 09132 / 74 97 5-27 · MAIR · '
    if ph is not None:
        img.paste(ph, (cx - R, cy - R), circle_mask(2 * R))
    else:
        lt = t - (s_mair - 0.15); k = ease(lt / 0.5)
        dd = ImageDraw.Draw(img); r2 = int(R * (1 - 0.15 * k)); dd.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(255, 255, 255))
        L = logo(560, False); img.paste(L, (cx - 280, cy - 130), L)
    ring = text_ring(ring_txt, R + 46, 34, -t * 22, (220, 236, 255, 255))
    img.paste(ring, (cx - ring.width // 2, cy - ring.height // 2), ring)
    d = ImageDraw.Draw(img)
    if t < s_mair - 0.15:
        # Einzelwort groß
        cw = None
        for a0, b0, w in T.w:
            if a0 - 0.05 <= t < b0 + 0.08: cw = (a0, w)
        if cw:
            w = disp(clean(cw[1])).upper(); k = back((t - cw[0] + 0.05) / 0.18); sz = int(120 * (0.8 + 0.2 * min(1.2, k)))
            f = F(INTER_BLACK, sz); tw = d.textlength(w, font=f)
            while tw > 980: sz -= 8; f = F(INTER_BLACK, sz); tw = d.textlength(w, font=f)
            d.text((540 - tw / 2, 1380), w, font=f, fill=WHITE)
        S = T.cur_sent(t)
        if S:
            txt = ' '.join(disp(x[2]) for x in S); f = F(INTER_BOLD, 36)
            lines = [[]]
            for wd in txt.split():
                tt = ' '.join(lines[-1] + [wd])
                if d.textlength(tt, font=f) > 900 and lines[-1]: lines.append([wd])
                else: lines[-1].append(wd)
            y = 1560
            for ln in lines:
                s_ = ' '.join(ln); tw = d.textlength(s_, font=f); d.text((540 - tw / 2, y), s_, font=f, fill=(150, 175, 205)); y += 48
    else:
        lt = t - (s_mair - 0.15)
        f = F(INTER_BLACK, 84); s_ = 'Kommentiere'; tw = d.textlength(s_, font=f); d.text((540 - tw / 2, 1360), s_, font=f, fill=WHITE)
        f = F(INTER_BLACK, 140); s_ = 'DUSCHE'; tw = d.textlength(s_, font=f); d.text((540 - tw / 2, 1450), s_, font=f, fill=(90, 180, 250))
        f = F(INTER_BOLD, 36); s_ = 'gefliest vom eigenen Fliesenleger · 09132 / 74 97 5-27'; tw = d.textlength(s_, font=f); d.text((540 - tw / 2, 1630), s_, font=f, fill=(200, 215, 235))
    ki(ImageDraw.Draw(img), 40, 180)
    return img


# ====================== L43 Kündigungsschreiben an die Ölheizung (Reel O) ======================
OEL = Image.open('/home/claude/mair-videos-public-create/bausteine/oelkessel/alter_oelkessel_keller.jpg').convert('RGB')
C3 = Image.open('/home/claude/mair-videos-public-create/bausteine/klima-wp-bilder/mair_team_viessmann_collage_3.png').convert('RGB')
RED = (214, 40, 36)
def caption_bar(img, T, t, y=1640, hi=(255, 214, 0)):
    c = T.cur_chunk(t, 4)
    if not c: return
    d = ImageDraw.Draw(img); f = F(INTER_BLACK, 66)
    txt = ' '.join(disp(clean(x[2])).upper() for x in c); w = d.textlength(txt, font=f)
    while w > 960: f = F(INTER_BLACK, f.size - 4); w = d.textlength(txt, font=f)
    x = 540 - w / 2
    for a0, b0, ww in c:
        ww = disp(clean(ww)).upper(); d.text((x, y), ww, font=f, fill=hi if a0 <= t < b0 + 0.1 else WHITE, stroke_width=7, stroke_fill=(0, 0, 0)); x += d.textlength(ww + ' ', font=f)

def reel_O(n):
    T = TRK['O']; t = n / FPS
    s1 = T.WT('Schmeiß') - 0.1; s2 = T.WT('Wärmepumpe') - 0.35; s3 = T.WT('Kommentiere') - 0.15
    if t < s1:
        k = t / s1; img = kenburns(OEL, 1080, 1920, k, 1.05, 1.22, 0.3)
        a = np.asarray(img).astype(float); g_ = a.mean(2, keepdims=True); a = a * 0.45 + g_ * 0.55; a[..., 0] *= 1.08
        img = Image.fromarray(np.clip(a * 0.85, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        d.text((60, 290), 'Die Alte', font=F(INTER_BLACK, 150), fill=WHITE, stroke_width=8, stroke_fill=(0, 0, 0))
        if t >= T.WT('nervt') - 0.05: d.text((60, 450), 'nervt.', font=F(INTER_BLACK, 150), fill=RED, stroke_width=8, stroke_fill=(0, 0, 0))
        for i, (lab, w_) in enumerate((('Ölpreis', 'Ölpreis'), ('Wartung', 'Wartung'), ('Gestank im Keller', 'Gestank'))):
            ts = T.WT(w_)
            if t >= ts - 0.05:
                kk = back((t - ts + 0.05) / 0.3); y = 700 + i * 120
                d.rounded_rectangle([60, y, 60 + 90 + d.textlength(lab, font=F(INTER_BLACK, 60)) + 30, y + 96], 20, fill=(0, 0, 0))
                d.text((80, y + 6), '✕' if False else 'X', font=F(INTER_BLACK, 70), fill=RED); d.text((150, y + 14), lab, font=F(INTER_BLACK, 60), fill=WHITE)
    elif t < s2:
        lt = t - s1
        bg = OEL.resize((270, 480)).filter(ImageFilter.GaussianBlur(6)).resize((1080, 1920)); img = Image.blend(bg, Image.new('RGB', bg.size, (20, 18, 16)), 0.5)
        k = ease(lt / 0.5); y0 = int(260 + 900 * (1 - k))
        sheet = Image.new('RGB', (900, 1300), (250, 248, 240)); sd = ImageDraw.Draw(sheet)
        sd.text((70, 70), 'KÜNDIGUNG', font=F(SERIF_B, 84), fill=(30, 30, 40))
        sd.text((70, 190), 'Aurachtal, im Oktober 2026', font=F(SERIF, 32), fill=(90, 90, 100))
        body = ['Liebe Ölheizung,', '', 'hiermit kündige ich dich', 'fristlos.', '', 'Gründe: Ölpreis, Wartung,', 'Gestank im Keller.', '', 'Ich steige um auf', 'erneuerbare Energie.', '', 'Dein Hausbesitzer']
        nshow = int(len(body) * min(1, max(0, (lt - 0.3) / max(0.6, (s2 - s1) * 0.7)))) + 1
        for i, ln in enumerate(body[:nshow]): sd.text((70, 290 + i * 66), ln, font=F(SERIF, 46), fill=(30, 30, 40))
        sheet = sheet.rotate(-2, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0))
        m = Image.new('L', sheet.size, 0); ImageDraw.Draw(m).polygon([(0, 0), (sheet.width, 0), (sheet.width, sheet.height), (0, sheet.height)], fill=255)
        img.paste(sheet, (80, y0)); d = ImageDraw.Draw(img)
        st_t = T.WT('raus')
        if t >= st_t - 0.05:
            kk = min(1, (t - st_t + 0.05) / 0.15); sc = 1.8 - 0.8 * kk
            st = Image.new('RGBA', (820, 230), (0, 0, 0, 0)); sd2 = ImageDraw.Draw(st)
            sd2.rounded_rectangle([8, 8, 812, 222], 24, outline=RED, width=14); tw = sd2.textlength('RAUS DAMIT', font=F(INTER_BLACK, 130)); sd2.text(((820 - tw) / 2, 30), 'RAUS DAMIT', font=F(INTER_BLACK, 130), fill=RED)
            st = st.rotate(-10, expand=True, resample=Image.BICUBIC); st = st.resize((int(st.width * sc), int(st.height * sc)))
            img.paste(st, (540 - st.width // 2, 1440 - st.height // 2), st)
    elif t < s3:
        lt = t - s2
        wp = C3.crop((772, 344, 1536, 664)) if False else P['wet']
        img = Image.new('RGB', (1080, 1920), (14, 22, 34)); d = ImageDraw.Draw(img)
        img.paste(kenburns(P['house'], 1080, 1100, min(1, lt / 5), 1.0, 1.1), (0, 260))
        d = ImageDraw.Draw(img)
        k = back(lt / 0.4)
        d.rounded_rectangle([60, 1180, 60 + int(560 * min(1, k)), 1280], 50, fill=LIME); 
        if k > 0.7: d.text((95, 1196), 'DIE NEUE', font=F(INTER_BLACK, 60), fill=NAVY)
        d.text((60, 1310), 'Wärmepumpe', font=F(INTER_BLACK, 96), fill=WHITE); d.text((60, 1420), 'von Viessmann', font=F(INTER_BOLD, 60), fill=(200, 210, 220))
        L = logo(300); img.paste(L, (700, 1440), L)
    else:
        lt = t - s3; img = Image.new('RGB', (1080, 1920), NAVY); d = ImageDraw.Draw(img)
        img.paste(kenburns(P['van'], 1080, 640, min(1, lt / 4), 1.0, 1.08), (0, 260))
        d = ImageDraw.Draw(img)
        d.text((60, 960), 'Raus mit', font=F(INTER_BLACK, 120), fill=WHITE); d.text((60, 1080), 'der Alten.', font=F(INTER_BLACK, 120), fill=LIME)
        w_ = d.textlength('Kommentiere RAUS', font=F(INTER_BLACK, 56)); d.rounded_rectangle([60, 1240, 130 + w_, 1340], 50, fill=RED); d.text((95, 1254), 'Kommentiere RAUS', font=F(INTER_BLACK, 56), fill=WHITE)
        d.text((60, 1380), 'individuelles Angebot · 09132 / 74 97 5-27', font=F(INTER_BOLD, 40), fill=WHITE)
        d.text((60, 1440), 'Herzogenaurach · Aurachtal · Erlangen', font=F(INTER_BOLD, 36), fill=(180, 190, 205))
    if t < s3: caption_bar(img, T, t)
    ki(ImageDraw.Draw(img), 40, 212)
    return img

# ====================== L44 Handy-Dashboard mit Zahlen-Stickern (Reel X) ======================
def phone(fr):
    sc = fr.crop((0, 44, 540, 1170)).resize((600, 1251), Image.LANCZOS)
    ph = Image.new('RGBA', (650, 1317), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
    d.rounded_rectangle([0, 0, 649, 1316], 70, fill=(18, 18, 20)); ph.paste(sc, (25, 33), round_mask(600, 1251, 52)); return ph

def sticker(img, x, y, big, small, k, bg=LIME, fg=NAVY, ang=-4):
    if k <= 0: return
    f1 = F(INTER_BLACK, 92); f2 = F(INTER_BOLD, 34)
    tmp = ImageDraw.Draw(img); w = max(tmp.textlength(big, font=f1), tmp.textlength(small, font=f2)) + 70
    s = Image.new('RGBA', (int(w), 190), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
    sd.rounded_rectangle([0, 0, int(w) - 1, 189], 34, fill=bg + (255,)); sd.text((35, 14), big, font=f1, fill=fg); sd.text((37, 125), small, font=f2, fill=fg)
    sc = max(0.05, min(1.1, k)); s = s.resize((max(1, int(s.width * sc)), max(1, int(190 * sc)))).rotate(ang, expand=True, resample=Image.BICUBIC)
    img.paste(s, (int(x - s.width / 2), int(y - s.height / 2)), s)

def reel_X(n):
    T = TRK['X']; t = n / FPS
    s_end = T.WT('Maier') - 0.2
    img = Image.new('RGB', (1080, 1920), (10, 22, 30)); d = ImageDraw.Draw(img)
    for y in range(0, 1920, 6):
        c = int(10 + 30 * y / 1920); d.line([(0, y), (1080, y)], fill=(c // 2, c, c + 10))
    if t < s_end:
        fi = min(587, int(t / max(1, s_end) * 587) + 1)
        fr = Image.open(f'{D}/e3app/f_{fi:04d}.jpg').convert('RGB')
        ph = phone(fr); k = ease(t / 0.6); img.paste(ph, (215, int(330 + 120 * (1 - k))), ph)
        d = ImageDraw.Draw(img)
        d.text((60, 190), 'Trüber Tag.', font=F(INTER_BLACK, 76), fill=WHITE)
        d.text((520, 190), 'Speicher voll.', font=F(INTER_BLACK, 76), fill=LIME) if t >= T.WT('voll') - 0.05 else None
        sticker(img, 820, 620, '100 %', 'Batterie voll', back((t - T.WT('voll')) / 0.35), LIME, NAVY, -6)
        sticker(img, 260, 980, '33,5 kWh', 'Sonnenstrom heute', back((t - T.WT('dreiunddreißig')) / 0.35), WHITE, NAVY, 5)
        sticker(img, 820, 1300, '11 kWh', 'ins Netz eingespeist', back((t - T.WT('elf')) / 0.35), (255, 214, 0), NAVY, -5)
        sticker(img, 300, 1520, 'KI', 'entscheidet selbst', back((t - T.WT('künstliche')) / 0.35), LIME, NAVY, 4)
        if t >= T.WT('eigene') - 0.1:
            k2 = back((t - T.WT('eigene') + 0.1) / 0.4)
            ph2 = cover(Image.open('/home/claude/mair-videos-public-create/bausteine/e3dc/e3dc_anlage_ohne_fremdmarken_4x5.jpg').convert('RGB'), 520, 650)
            card = Image.new('RGBA', (560, 760), (255, 255, 255, 255)); card.paste(ph2, (20, 20)); ImageDraw.Draw(card).text((30, 684), 'Eigene Anlage vom Chef', font=F(INTER_BLACK, 40), fill=NAVY)
            sc = max(0.05, min(1.05, k2)); card = card.resize((int(560 * sc), int(760 * sc))).rotate(-6, expand=True, resample=Image.BICUBIC)
            img.paste(card, (560 - card.width // 2 + 200, 1050 - card.height // 2), card)
        d = ImageDraw.Draw(img); d.text((60, 1800), 'Echte Werte: E3/DC-App, eigene Anlage, 09.10.2026', font=F(INTER_BOLD, 26), fill=(150, 170, 180))
    else:
        lt = t - s_end; d = ImageDraw.Draw(img)
        ph2 = cover(Image.open('/home/claude/mair-videos-public-create/bausteine/e3dc/e3dc_anlage_ohne_fremdmarken_4x5.jpg').convert('RGB'), 1080, 900)
        img.paste(ph2, (0, 240)); d = ImageDraw.Draw(img)
        L = logo(420); img.paste(L, (60, 1180), L)
        d.text((60, 1350), 'Photovoltaik · Speicher · Wärmepumpe', font=F(INTER_BOLD, 40), fill=WHITE)
        w_ = d.textlength('Kommentiere STROM', font=F(INTER_BLACK, 54)); d.rounded_rectangle([60, 1430, 130 + w_, 1530], 50, fill=LIME); d.text((95, 1444), 'Kommentiere STROM', font=F(INTER_BLACK, 54), fill=NAVY)
        d.text((60, 1570), 'individuelles Angebot · 09132 / 74 97 5-27', font=F(INTER_BOLD, 38), fill=WHITE)
    if t < s_end: caption_bar(img, T, t, 1680)
    ki(ImageDraw.Draw(img), 40, 120)
    return img

# Grün-Umfärbung der Mini-Monteure aus render2 übernehmen
def _rc():
    spec = importlib.util.spec_from_file_location('r2b', D + '/render2.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.recolor_green
RC = None
TRK = {}
if __name__ == '__main__':
    which, s, e = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    TRK[which] = Track(which)
    if which == 'A': RC = _rc()
    out = f'{D}/o3_{which}'; os.makedirs(out, exist_ok=True)
    fn = {'A': reel_A, 'B': reel_B, 'C': reel_C, 'D': reel_D, 'E': reel_E, 'F': reel_F, 'O': reel_O, 'X': reel_X}[which]
    N = int(TIM[which]['DUR'] * FPS)
    for n in range(s, min(e, N)):
        fn(n).save(f'{out}/f_{n:04d}.jpg', quality=90)
