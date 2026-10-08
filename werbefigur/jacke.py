"""Patrick (p3) im kompletten Mair-Arbeitsoutfit:
schwarze Arbeitsjacke (lange Ärmel, Stehkragen, Reißverschluss, Logo), schwarze Arbeitshose mit
Kniepolstertaschen, schwarze Sicherheitsschuhe mit grünem Akzent, sicherer Stand auf beiden Füßen."""
import cv2, numpy as np
from PIL import Image

SS = 3                                   # Supersampling für gezeichnete Teile
GREEN = np.array([44, 176, 76], np.float32)   # BGR Mair-Grün
img0 = cv2.imread('fig3/p3_crop.png').astype(np.float32)
m0 = np.load('fig3/p3_m.npy').astype(np.float32)
H, W = m0.shape
lab = cv2.cvtColor(img0.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
L, A = lab[..., 0], lab[..., 1]
hsv = cv2.cvtColor(img0.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.int32)
inside = m0 > 0.35
rng = np.random.default_rng(3)
TEX = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7) * 2.2   # Stoffkorn

def poly_mask(pts, shape=(H, W)):
    big = np.zeros((shape[0] * SS, shape[1] * SS), np.uint8)
    cv2.fillPoly(big, [np.round(np.array(pts) * SS).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    return cv2.resize(big, (shape[1], shape[0]), interpolation=cv2.INTER_AREA).astype(np.float32) / 255

def norm(Lsrc, sel, lo, hi):
    v = Lsrc[sel]
    a, b = np.percentile(v, 3), np.percentile(v, 97)
    return lo + np.clip((Lsrc - a) / (b - a + 1e-6), 0, 1) * (hi - lo)

# ------------------------------------------------------------------ OBERKÖRPER
Y_HEM = 742                                                   # Jackensaum
skin = (A > 134) & (A < 172) & (L > 60) & (hsv[..., 0] < 28) & inside
skin = cv2.morphologyEx(skin.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
hand = poly_mask([(292, 371), (318, 366), (346, 374), (354, 400), (348, 428), (324, 442), (300, 434), (289, 404)]) > 0.5
head = np.zeros_like(inside); head[:214] = True
neck = poly_mask([(196, 150), (276, 150), (282, 238), (190, 238)]) > 0.5
face = (head | neck) & skin
arms = skin & ~face & ~hand
arms[:236] = False
shirt = inside & ~skin & ~head
shirt[Y_HEM:] = False
shirt[:200] = False
# Rot-/Pink-Säume, die noch keine Haut sind
shirt |= inside & (A > 150) & ~face & ~hand & (np.arange(H)[:, None] > 205) & (np.arange(H)[:, None] < Y_HEM)
jacket = (shirt | arms)
jacket[690:Y_HEM] |= inside[690:Y_HEM]                       # Jacke über Shorts-Bund verlängern

# Schattierung: Torso aus Originalhelligkeit (Aufdrucke ausgeflickt), Arme getrennt normiert
prints = shirt & (A < 160)
prints = cv2.dilate(prints.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
Lt = cv2.inpaint(L.astype(np.uint8), (prints & shirt).astype(np.uint8), 7, cv2.INPAINT_TELEA).astype(np.float32)
shade = np.zeros_like(L)
tor = shirt & ~prints
shade = np.where(shirt, norm(Lt, tor, 12, 50), shade)
shade = np.where(arms, norm(cv2.GaussianBlur(L, (0, 0), 1.6), arms, 10, 54), shade)
hemz = np.zeros_like(inside); hemz[690:Y_HEM] = True; hemz &= jacket & ~shirt & ~arms
shade = np.where(hemz, cv2.GaussianBlur(norm(L, inside & (np.arange(H)[:, None] > 700), 12, 40), (0, 0), 2), shade)
shade += TEX
jac_bgr = np.stack([shade * 1.03, shade * 1.0, shade * 0.97], -1)

img = img0.copy()
ja = cv2.GaussianBlur(jacket.astype(np.float32), (3, 3), 0)[..., None]
img = img * (1 - ja) + jac_bgr * ja

# Ärmelbündchen am Handgelenk (oberer Unterarm endet an der Hand)
cuff = poly_mask([(274, 368), (290, 366), (289, 440), (273, 444)]) * ((arms | jacket) & inside & ~hand)
img = img * (1 - cuff[..., None]) + (np.array([24, 24, 25]) + TEX[..., None] + 3 * np.sin(np.mgrid[0:H, 0:W][0] * 1.6)[..., None]) * cuff[..., None]
cl = poly_mask([(287, 367), (290, 367), (289, 440), (286, 441)]) * (inside & ~hand)
img = img * (1 - cl[..., None] * 0.6) + np.array([62, 62, 64]) * (cl[..., None] * 0.6)

# Stehkragen (zwei Hälften, Reißverschluss-Zipper in der Mitte)
cl_l = [(188, 242), (195, 209), (233, 221), (233, 250)]
cl_r = [(235, 250), (235, 221), (273, 209), (280, 242)]
for pts, sgn in ((cl_l, -1), (cl_r, 1)):
    cm = poly_mask(pts)
    g = 14 + 22 * np.clip(1 - (yy_ := np.mgrid[0:H, 0:W][0].astype(np.float32) - 209) / 40, 0, 1) + (8 if sgn < 0 else 0)
    cb = np.stack([g + TEX] * 3, -1)
    img = img * (1 - cm[..., None]) + cb * cm[..., None]
    top = np.clip(poly_mask(pts) - poly_mask([(p[0], p[1] + (3 if i in (1, 2) else 0)) for i, p in enumerate(pts)]), 0, 1)
    img = img * (1 - top[..., None] * 0.8) + np.array([66, 66, 68]) * top[..., None] * 0.8
pull = poly_mask([(231, 226), (237, 226), (237, 240), (231, 240)])
img = img * (1 - pull[..., None]) + np.array([120, 122, 124]) * pull[..., None]
# Reißverschluss (nur auf sichtbarem Torso, unter den Armen verdeckt)
zip_ = poly_mask([(233, 250), (236, 250), (236, Y_HEM), (233, Y_HEM)]) * (shirt | hemz).astype(np.float32)
img = img * (1 - zip_[..., None]) + np.array([38, 38, 40]) * zip_[..., None]
teeth = zip_ * ((np.arange(H)[:, None] % 4) < 2)
img = img * (1 - teeth[..., None] * 0.5) + np.array([62, 62, 65]) * teeth[..., None] * 0.5
# Saum-Bund
hemb = poly_mask([(96, Y_HEM - 16), (378, Y_HEM - 16), (378, Y_HEM), (96, Y_HEM)]) * inside
img = img * (1 - hemb[..., None]) + (np.array([16, 16, 17]) + TEX[..., None]) * hemb[..., None]
hl = poly_mask([(96, Y_HEM - 17), (378, Y_HEM - 17), (378, Y_HEM - 15), (96, Y_HEM - 15)]) * inside
img = img * (1 - hl[..., None] * 0.5) + np.array([60, 60, 62]) * hl[..., None] * 0.5
# ------------------------------------------------------------------ UNTERKÖRPER (neu aufgebaut)
FLOOR = 1342
keep = np.zeros_like(inside); keep[:Y_HEM] = True
hips = inside.copy(); hips[:Y_HEM] = False; hips[866:] = False          # echte Hosenpartie (Shorts) bis Oberschenkel
# Hüftpartie: Zylinder-Schattierung je Zeile + echte Falten (Hochpass) aus den Shorts
hskin = hips & ((A > 134) | (L > 80))
hskin = cv2.dilate(hskin.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
Lh = cv2.inpaint(np.clip(L, 0, 255).astype(np.uint8), (hskin & hips).astype(np.uint8), 9, cv2.INPAINT_TELEA).astype(np.float32)
hp = Lh - cv2.GaussianBlur(Lh, (0, 0), 6)
hp = np.clip(hp, -12, 12)
xs_ = np.arange(W, dtype=np.float32)
hsh = np.zeros_like(L)
for y in range(Y_HEM, 866):
    r = np.where(inside[y])[0]
    if r.size < 5: continue
    u = (xs_ - r.min()) / (r.max() - r.min() + 1e-6)
    hsh[y] = 12 + 26 * np.exp(-((u - 0.33) / 0.33) ** 2) - 6 * np.clip((u - 0.82) / 0.18, 0, 1)
hipsh = hsh + 0.5 * hp + TEX
img = np.where(hips[..., None], np.stack([hipsh * 1.03, hipsh, hipsh * 0.97], -1), img)
# Gesäßtaschen-/Gürtelandeutung: Gürtel unter dem Jackensaum
belt = poly_mask([(100, Y_HEM), (376, Y_HEM), (376, Y_HEM + 7), (100, Y_HEM + 7)]) * hips
img = img * (1 - belt[..., None]) + np.array([9, 9, 10]) * belt[..., None]
# Hosenbeine: geschwungene Kanten, Faltenkarte, Schritt geschlossen
row = np.where(inside[804])[0]; xl, xr = row.min() + 2, row.max() - 2
alpha = np.where(keep, m0, 0).astype(np.float32)
alpha = np.maximum(alpha, hips.astype(np.float32) * m0)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
Y0, Y1 = 800, 1286
ys = np.arange(H, dtype=np.float32)
t = np.clip((ys - Y0) / (Y1 - Y0), 0, 1)
def lerp(a, b, t): return a + (b - a) * t
bulge = np.sin(np.pi * np.clip(t * 1.25, 0, 1)) * 6           # Oberschenkel
knee = np.exp(-((ys - 1045) / 40) ** 2) * 4
wob = cv2.GaussianBlur(rng.normal(0, 1, (H, 4)).astype(np.float32), (1, 0), sigmaX=0.1, sigmaY=9) * 2.5
legs = [  # x(y) für linke und rechte Kante
    (lerp(xl, 126, t) - bulge - knee + wob[:, 0], lerp(234, 214, np.clip(t * 1.6, 0, 1)) + wob[:, 1] * 0.6),
    (lerp(235, 264, np.clip(t * 1.6, 0, 1)) + wob[:, 2] * 0.6, lerp(xr, 354, t) + bulge + knee + wob[:, 3]),
]
# Faltenkarte (quer laufende, weiche Falten)
fn = rng.normal(0, 1, (H, W)).astype(np.float32)
fold = cv2.GaussianBlur(fn, (0, 0), sigmaX=10, sigmaY=2.2)
fold = fold / (fold.std() + 1e-6)
pants_rgb = np.zeros((H, W, 3), np.float32); pants_a = np.zeros((H, W), np.float32)
for li, (xa, xb) in enumerate(legs):
    pm = np.zeros((H * SS, W * SS), np.uint8)
    pts = [(xa[y], y) for y in range(Y0, Y1 + 1)] + [(xb[y], y) for y in range(Y1, Y0 - 1, -1)]
    cv2.fillPoly(pm, [np.round(np.array(pts) * SS).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    pm = cv2.resize(pm, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    u = np.clip((xx - xa[:, None]) / (xb - xa + 1e-6)[:, None], 0, 1)
    light = 0.30 if li == 0 else 0.40                           # Licht von links
    sh = 12 + 30 * np.exp(-((u - light) / 0.30) ** 2) - 7 * np.clip((u - 0.8) / 0.2, 0, 1)
    sh += 2.8 * fold * (0.4 + 0.6 * np.exp(-((yy - 1050) / 70) ** 2) + 0.9 * np.clip((yy - 1210) / 80, 0, 1))
    sh += 7 * np.exp(-((u - 0.5) / 0.02) ** 2) * np.clip((yy - 900) / 60, 0, 1) * 0.5      # Bügelfalte
    sh += TEX
    kpl = (yy > 992) & (yy < 1088) & (u > 0.14) & (u < 0.86)
    sh = np.where(kpl, sh + 3, sh)
    edge_k = kpl & ~((yy > 995) & (yy < 1085) & (u > 0.16) & (u < 0.84))
    sh = np.where(edge_k, sh - 6, sh)
    stitch = ((np.abs(yy - 997) < 0.7) | (np.abs(yy - 1083) < 0.7)) & (u > 0.17) & (u < 0.83) & ((xx.astype(int) % 4) < 2)
    col = np.stack([sh * 1.03, sh, sh * 0.97], -1)
    col = np.where(stitch[..., None], np.array([58, 60, 62], np.float32), col)
    gp = (np.abs(yy - 993) < 1.3) & (u > 0.14) & (u < 0.86)
    col = np.where(gp[..., None], GREEN * 0.75, col)
    ramp = np.clip((yy - Y0) / 45, 0, 1)
    pmr = pm * ramp
    pants_rgb = pants_rgb * (1 - pmr[..., None]) + col * pmr[..., None]
    pants_a = np.maximum(pants_a, pmr)
img = img * (1 - pants_a[..., None]) + pants_rgb * pants_a[..., None]
alpha = np.maximum(alpha, pants_a)

# Sicherheitsschuhe (Vorderansicht, leicht nach außen gedreht)
def ell(cx, cy, rx, ry, ang=0):
    big = np.zeros((H * SS, W * SS), np.uint8)
    cv2.ellipse(big, (int(cx * SS), int(cy * SS)), (int(rx * SS), int(ry * SS)), ang, 0, 360, 255, -1, lineType=cv2.LINE_AA)
    return cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
def paint(img, mask, col):
    return img * (1 - mask[..., None]) + col * mask[..., None]
def shoe(cx, side, img, alpha):
    ox = side * 13
    shaft = poly_mask([(cx - 36, 1262), (cx + 36, 1262), (cx + 40, 1306), (cx - 40, 1306)])
    vamp = ell(cx + ox, 1308, 55, 26, side * 8)
    toe = ell(cx + ox * 1.5, 1321, 46, 16, side * 8)
    up = np.clip(shaft + vamp + toe, 0, 1)
    r = np.sqrt(((xx - (cx - 18)) / 70) ** 2 + ((yy - 1300) / 40) ** 2)
    g = 9 + 40 * np.clip(1 - r, 0, 1) ** 1.4 + TEX
    g += 70 * np.exp(-(((xx - (cx - 12 + ox * 1.5)) / 13) ** 2 + ((yy - 1318) / 4.5) ** 2))     # Glanz Zehenkappe
    g += 30 * np.exp(-(((xx - (cx - 30 + ox)) / 6) ** 2 + ((yy - 1306) / 10) ** 2))            # Kantenlicht
    upc = np.stack([g * 1.02, g, g * 0.98], -1)
    # Kappen-Naht
    capline = np.clip(ell(cx + ox * 1.5, 1322, 43, 14, side * 4) - ell(cx + ox * 1.5, 1323.5, 41, 12.5, side * 4), 0, 1)
    capline[1322:] = 0
    upc = paint(upc, capline * 0.8, np.array([60, 60, 62], np.float32))
    img = paint(img, up, upc)
    bump = np.clip(ell(cx + ox * 1.5, 1324, 49, 12, side * 8) - ell(cx + ox * 1.5, 1318, 47, 12, side * 8), 0, 1)
    bump[:1316] = 0
    img = paint(img, bump, np.stack([30 + TEX] * 3, -1))
    stl = np.clip(ell(cx + ox, 1306, 49, 21, side * 8) - ell(cx + ox, 1306, 47.6, 19.8, side * 8), 0, 1)
    stl[:1290] = 0
    stl *= ((xx.astype(int) + yy.astype(int)) % 4 < 2)
    img = paint(img, stl * 0.7, np.array([70, 70, 72], np.float32))
    # Sohle
    sole = np.clip(poly_mask([(cx - 58 + ox, 1328), (cx + 58 + ox, 1328), (cx + 56 + ox, FLOOR - 3), (cx + 50 + ox, FLOOR),
                              (cx - 50 + ox, FLOOR), (cx - 56 + ox, FLOOR - 3)]), 0, 1)
    sg = 24 + 16 * np.clip(1 - (yy - 1328) / 14, 0, 1) + TEX
    img = paint(img, sole, np.stack([sg] * 3, -1))
    tread = poly_mask([(cx - 52 + ox, FLOOR - 4), (cx + 52 + ox, FLOOR - 4), (cx + 50 + ox, FLOOR), (cx - 50 + ox, FLOOR)])
    img = paint(img, tread * 0.8, np.array([12, 12, 13], np.float32))
    grn = poly_mask([(cx - 57 + ox, 1328.2), (cx + 57 + ox, 1328.2), (cx + 57 + ox, 1330.8), (cx - 57 + ox, 1330.8)])
    img = paint(img, grn, GREEN)
    tab = poly_mask([(cx - 5, 1258), (cx + 5, 1258), (cx + 5, 1266), (cx - 5, 1266)])        # grüne Zuglasche
    return img, np.maximum(alpha, np.clip(up + sole, 0, 1))

img, alpha = shoe(172, -1, img, alpha)
img, alpha = shoe(308, 1, img, alpha)
# Hosensaum liegt auf dem Schuh (leichte Stauchung)
for li, (cx, xa, xb) in enumerate(((172, legs[0][0], legs[0][1]), (308, legs[1][0], legs[1][1]))):
    x0, x1 = xa[1280] - 1, xb[1280] + 1
    hem = poly_mask([(x0, 1268), (x1, 1268), (x1 + 2, 1286), ((x0 + x1) / 2, 1290), (x0 - 2, 1286)])
    u = np.clip((xx - x0) / (x1 - x0), 0, 1)
    hg = 12 + 24 * np.exp(-((u - 0.35) / 0.3) ** 2) - 6 * np.clip((yy - 1280) / 10, 0, 1) + TEX
    img = paint(img, hem, np.stack([hg] * 3, -1))
    alpha = np.maximum(alpha, hem)

# Logo (linke Brust)
LOGO = Image.open('/home/claude/mair-videos-public-create/werkzeuge/marke/mair_logo_dunkel_clean.png').convert('RGBA')
rgb = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)
P = Image.fromarray(np.dstack([rgb, (np.clip(alpha, 0, 1) * 255).astype(np.uint8)]), 'RGBA')
lw = 150; Lg = LOGO.resize((lw, int(lw * LOGO.height / LOGO.width)), Image.LANCZOS)
# Logo leicht abdunkeln/entsättigen wie Druck auf Stoff
la = np.array(Lg).astype(np.float32); la[..., :3] *= 1.0; Lg = Image.fromarray(la.astype(np.uint8), 'RGBA')
P.alpha_composite(Lg, (256, 266))
ys, xs = np.where(np.array(P.getchannel('A')) > 40)
P = P.crop((max(0, xs.min() - 12), max(0, ys.min() - 12), xs.max() + 12, ys.max() + 12))
P.save('fig3/p3_mair_jacke.png')
for nm, col in (('hell', (232, 236, 233)), ('dunkel', (40, 60, 45))):
    bg = Image.new('RGBA', P.size, col + (255,)); bg.alpha_composite(P)
    bg.convert('RGB').save(f'fig3/p3_jacke_{nm}.jpg', quality=93)
print('ok', P.size)
