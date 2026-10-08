"""Mair-Outfit: schwarzes Arbeitsshirt mit grossem Mair-Logo, schwarze Arbeitshose, schwarze Sicherheitsschuhe."""
import cv2, numpy as np, sys
from PIL import Image

LOGO = Image.open('/home/claude/mair-videos-public-create/werkzeuge/marke/mair_logo_dunkel_clean.png').convert('RGBA')

def soft(x, k=5): return cv2.GaussianBlur(x.astype(np.float32), (k, k), 0)

def fabric(img, sel, Lch, lo=14, hi=62, holes=None, tint=(1.0, 1.0, 1.04)):
    """dunkler Stoff, Schattierung aus Original-Helligkeit; Aufdrucke (holes) werden vorher ausgeflickt"""
    Lf = Lch.astype(np.float32)
    if holes is not None and holes.any():
        Lf = cv2.inpaint(Lch.astype(np.uint8), holes.astype(np.uint8), 7, cv2.INPAINT_TELEA).astype(np.float32)
    v = Lf[sel > 0.5]
    if v.size < 50: return img
    a, b = np.percentile(v, 4), np.percentile(v, 97)
    s = np.clip((Lf - a) / (b - a + 1e-6), 0, 1) ** 1.1
    rng = np.random.default_rng(1)
    tex = rng.normal(0, 1.6, Lf.shape).astype(np.float32)          # leichte Stoffstruktur
    dark = (lo + s * (hi - lo) + tex)[..., None] * np.array(tint)[None, None]
    al = soft(sel, 5)[..., None]
    return np.clip(img * (1 - al) + dark * al, 0, 255)

def run(n, cfg):
    img = cv2.imread(f'fig3/{n}_crop.png').astype(np.float32)
    m = np.load(f'fig3/{n}_m.npy')
    for (x0, y0, x1, y1) in cfg.get('zero', []): m[y0:y1, x0:x1] = 0
    lab = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.int32)
    L, A = lab[..., 0], lab[..., 1]
    hsv = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.int32)
    inside = m > 0.35
    Hh, W = m.shape
    skin = (A > 134) & (A < 172) & (L > 70) & (hsv[..., 1] > 55) & (hsv[..., 1] < cfg.get('skin_smax', 256)) & (hsv[..., 0] < 28) & inside
    if cfg.get('skin_rule') == 'lab':
        skin = inside & (A <= cfg['amin']) & (A > 136) & (L > 40)
    if 'skin_polys' in cfg:
        pm = np.zeros(m.shape, np.uint8)
        for poly in cfg['skin_polys']: cv2.fillPoly(pm, [np.array(poly, np.int32)], 1)
        skin &= pm > 0
        notskin = (pm == 0) & inside
    else:
        notskin = None
    skin = cv2.morphologyEx(skin.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0

    # ---------- Oberteil ----------
    y0, y1 = cfg['shirt_y']
    crit = (A > cfg.get('amin', 168))
    if cfg.get('shirt_rule') == 'hsv':
        crit = ((hsv[..., 0] < 11) | (hsv[..., 0] > 168)) & (hsv[..., 1] > cfg.get('smin', 165))
    red = np.zeros_like(inside); red[y0:y1] = crit[y0:y1] & inside[y0:y1]
    shirt = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((cfg.get('close', 25),) * 2, np.uint8)) > 0
    # Löcher (Aufdrucke) füllen
    cnts, _ = cv2.findContours(shirt.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(shirt, np.uint8); cv2.drawContours(filled, cnts, -1, 1, -1)
    shirt = (filled > 0) & inside & ~skin
    for (a, b, c, d) in cfg.get('force_shirt', []):
        f = np.zeros_like(inside); f[b:d, a:c] = True; f &= inside & (A > 138)
        shirt |= f; skin &= ~f
    if notskin is not None:
        ns = np.zeros_like(inside); ns[y0:y1] = notskin[y0:y1]; shirt |= ns
    for (a, b, c, d) in cfg.get('noshirt', []): shirt[b:d, a:c] = False
    # weiche Kante: Saum-Übergang rot->haut
    edge = (A > 158) & inside & ~shirt & (cv2.dilate(shirt.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    shirt = shirt | edge
    holes = cv2.dilate((shirt & ((A < 160) if cfg.get('shirt_rule') != 'hsv' else (hsv[..., 1] < 120))).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    holes &= shirt
    shirt = (cv2.dilate(shirt.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & inside & ~skin
    img = fabric(img, shirt.astype(np.float32), L, lo=9, hi=44, holes=holes)
    lab_n = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.int32)
    rest = np.zeros_like(inside); rest[y0:y1] = (lab_n[..., 1] > cfg.get('rest_a', 160))[y0:y1] & (m[y0:y1] > 0.05)
    rest = cv2.dilate(rest.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    rest &= ~skin | (lab_n[..., 1] > cfg.get('rest_a', 160))
    for (a, b, c, d) in cfg.get('norest', []): rest[b:d, a:c] = False
    img[rest] = img[rest] * 0.2 + 18

    # ---------- Hose (Shorts + Beine) ----------
    py0, py1 = cfg['pants_y']                 # Shorts-Anfang bis Schuh-Oberkante
    pants = np.zeros_like(inside); pants[py0:py1] = inside[py0:py1]
    for (a, b, c, d) in cfg.get('nopants', []): pants[b:d, a:c] = False
    # Beine etwas breiter (Hosenbein statt Bein)
    leg_rows = np.zeros_like(inside); leg_rows[cfg['leg_y']:py1] = True
    ay0, ay1 = cfg['ankle_y']
    ank = np.zeros_like(inside); ank[ay0:ay1] = (skin | (A > 134))[ay0:ay1] & inside[ay0:ay1]
    pants |= ank
    leg_rows[py1:ay1] = True
    legs = pants & leg_rows
    if not legs.any():
        shorts = pants
        ph = cv2.dilate((pants & (L > 150)).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        pants = (cv2.dilate(pants.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & (m > 0.05) & ~skin
        img = fabric(img, pants.astype(np.float32), L.astype(np.float32), lo=10, hi=50, holes=ph & pants)
        legs = None
    if legs is not None:
     wide = cv2.dilate(legs.astype(np.uint8), np.ones((3, cfg.get('widen', 9)), np.uint8)) > 0
     wide &= leg_rows
     m = np.where(leg_rows, np.maximum(m, soft(wide, 3)), m)
     shorts = pants & ~leg_rows
     pholes = shorts & (L > 95) & ~skin
     pholes = cv2.dilate(pholes.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
     pholes &= shorts
     Lp = L.copy().astype(np.float32)
     a_, b_ = np.percentile(L[legs], 5), np.percentile(L[legs], 97)
     sh = shorts & ~pholes
     c_, d_ = np.percentile(L[sh], 5), np.percentile(L[sh], 97)
     ln = pants & (leg_rows | skin)
     Lp[ln] = c_ + (L[ln] - a_) / (b_ - a_ + 1e-6) * (d_ - c_)
     Lp[ln] = np.minimum(Lp[ln], np.percentile(L[sh], 65))
     # verbreiterte Hosenbeine: Schattierung aus Nachbarn (normierte Faltung)
     wl = legs.astype(np.float32)
     num = cv2.blur(Lp * wl, (31, 3)); den = cv2.blur(wl, (31, 3)) + 1e-6
     Lp = np.where(wide & ~legs, num / den, Lp)
     if 'flat_rows' in cfg:
         f0, f1 = cfg['flat_rows']
         fr = np.zeros_like(inside); fr[f0:f1] = True
         fr &= (pants | wide)
         Lp[fr] = np.percentile(L[sh], 45)
         pholes &= ~fr
     pants = (pants | wide)
     pants = (cv2.dilate(pants.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & (m > 0.05)
     img = fabric(img, pants.astype(np.float32), Lp, lo=10, hi=48, holes=pholes)
    # ---------- Schuhe ----------
    sy = cfg.get('shoe_y')
    if sy is None:
        sole = np.zeros_like(inside)
    else:
     pass
    sy = sy if sy is not None else Hh
    shoe = np.zeros_like(inside); shoe[sy:] = inside[sy:]
    shoe &= ~pants
    shoe = (cv2.dilate(shoe.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & (m > 0.05) & ~pants
    sole = shoe & (np.arange(Hh)[:, None] > cfg['sole_y']) & (L > 150)
    up = shoe & ~sole
    Ls = L.astype(np.float32)
    img = fabric(img, up.astype(np.float32), Ls, lo=8, hi=38)
    img = fabric(img, sole.astype(np.float32), Ls, lo=40, hi=70)

    # Reste (helle Kanten) unten abdunkeln
    lab2 = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB)[..., 0]
    res = np.zeros_like(inside); res[cfg['pants_y'][0]:] = True
    res &= (m > 0.05) & (lab2 > 72) & ~sole
    if res.any():
        img[res] = img[res] * 0.25 + 22
    # ---------- Ausgabe ----------
    rgb = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)
    P = Image.fromarray(np.dstack([rgb, (np.clip(m, 0, 1) * 255).astype(np.uint8)]), 'RGBA')
    lx, ly, lw = cfg['logo']
    Lg = LOGO.resize((lw, int(lw * LOGO.height / LOGO.width)), Image.LANCZOS)
    # Logo leicht in den Stoff "drücken": Schattierung übernehmen
    P.alpha_composite(Lg, (lx, ly))
    ys, xs = np.where(np.array(P.getchannel('A')) > 40)
    P = P.crop((max(0, xs.min() - 12), max(0, ys.min() - 12), xs.max() + 12, ys.max() + 12))
    P.save(f'fig3/{n}_mair_outfit.png')
    for nm, col in (('hell', (232, 236, 233)), ('dunkel', (40, 60, 45))):
        bg = Image.new('RGBA', P.size, col + (255,)); bg.alpha_composite(P)
        bg.convert('RGB').save(f'fig3/{n}_outfit_{nm}.jpg', quality=92)

CFG = {
 'p1': dict(shirt_y=(150, 610), close=15, pants_y=(585, 880), leg_y=880, ankle_y=(880, 880),
            zero=[(0, 0, 80, 880), (440, 255, 490, 360)], logo=(214, 228, 118), sole_y=880, amin=160, skin_rule='lab', force_shirt=[(290, 150, 425, 288)], rest_a=162, norest=[(95, 150, 225, 215)], noshirt=[(105, 130, 205, 178), (138, 178, 192, 204)],
            skin_polys=[[(55, 0), (230, 0), (225, 175), (190, 205), (130, 215), (60, 190)], [(370, 300), (460, 296), (460, 440), (395, 485), (330, 515), (250, 525), (245, 440), (335, 395)]]),
 'p3': dict(shirt_y=(200, 700), amin=168, rest_a=172, pants_y=(690, 1140), leg_y=910, widen=25, ankle_y=(1135, 1200), knee_y=(965, 1020), flat_rows=(862, 935),
            shoe_y=1150, sole_y=1290, logo=(190, 248, 140)),
}
if __name__ == '__main__':
    for n in sys.argv[1:]: run(n, CFG[n])
