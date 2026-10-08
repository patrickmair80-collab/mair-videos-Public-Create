"""Werbebilder Feed 4:5 + Story 9:16 aus fig3/comp_mair.jpg"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

OD = '/usr/share/fonts/opentype/inter/'
BLK = OD + 'InterDisplay-Black.otf'; BLD = OD + 'InterDisplay-Bold.otf'; SEM = OD + 'Inter-SemiBold.otf'
F = lambda p, s: ImageFont.truetype(p, s)
GREEN = (76, 176, 44); LIME = (150, 225, 110); WHITE = (255, 255, 255)
LOGO = Image.open('/home/claude/mair-videos-public-create/werkzeuge/marke/mair_logo_dunkel_clean.png').convert('RGBA')
comp = Image.open('fig3/comp_mair.jpg').convert('RGB')

def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def grad(img, y0, y1, a0, a1, col=(6, 14, 9)):
    W, H = img.size
    g = np.zeros((H, W), np.float32)
    ys = np.arange(H)
    t = np.clip((ys - y0) / max(1, (y1 - y0)), 0, 1)
    g[:] = (a0 + (a1 - a0) * t)[:, None]
    g[(ys < min(y0, y1))] = a0 if y0 < y1 else a1
    L = Image.new('RGBA', img.size, col + (0,)); L.putalpha(Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8)))
    img.alpha_composite(L)

def card(img, y, W):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, y, W - 40, y + 300], radius=34, fill=(10, 24, 14, 228))
    d.rounded_rectangle([40, y, W - 40, y + 12], radius=6, fill=GREEN)
    d.text((80, y + 40), 'IHR ANSPRECHPARTNER', font=F(BLD, 28), fill=LIME)
    d.text((80, y + 78), 'Patrick Mair', font=F(BLK, 66), fill=WHITE)
    d.text((80, y + 158), 'Heizungs- & Sanitärmeister', font=F(SEM, 34), fill=(215, 230, 215))
    d.text((80, y + 212), '09132 / 74 97 5-27', font=F(BLK, 50), fill=WHITE)
    lg = LOGO.resize((250, int(250 * LOGO.height / LOGO.width)), Image.LANCZOS)
    img.alpha_composite(lg, (W - 40 - 40 - 250, y + 52))
    d.text((W - 80 - tw(d, 'individuelles Angebot', F(SEM, 28)), y + 232), 'individuelles Angebot', font=F(SEM, 28), fill=LIME)

def headline(img, y, W, size1=78, size2=104, x0=None):
    d = ImageDraw.Draw(img)
    for txt, f, col, yy in (('Lust auf eine', F(BLK, size1), WHITE, y), ('Wärmepumpe?', F(BLK, size2), LIME, y + int(size1 * 1.12))):
        x = (W - tw(d, txt, f)) // 2 if x0 is None else x0
        d.text((x + 3, yy + 4), txt, font=f, fill=(0, 0, 0, 160)); d.text((x, yy), txt, font=f, fill=col)

def bubble(img, x, y, tip, text='Ich komm vorbei!'):
    d = ImageDraw.Draw(img); f = F(BLK, 46)
    w = tw(d, text, f) + 56; h = 92
    d.rounded_rectangle([x + 4, y + 6, x + w + 4, y + h + 6], radius=30, fill=(0, 0, 0, 90))
    d.polygon([(x + w - 70, y + 20), (x + w - 10, y + 55), tip], fill=WHITE)
    d.rounded_rectangle([x, y, x + w, y + h], radius=30, fill=WHITE)
    d.text((x + 28, y + 16), text, font=f, fill=(12, 18, 14))

# ---- Feed 4:5 ----
W, H = 1080, 1350
crop = comp.crop((522, 0, 1546, 1280)).resize((W, H), Image.LANCZOS)
img = crop.convert('RGBA')
grad(img, 0, 460, 0.62, 0.0)
grad(img, 950, H, 0.0, 0.8)
headline(img, 60, W, 70, 92, x0=56)
# Kopf liegt bei comp (1300,170) -> feed x=(1300-522)*W/1024, y=170*H/1280
hx = int((1300 - 522) * W / 1024); hy = int(170 * H / 1280)
bubble(img, 250, 300, (hx - 40, hy + 20))
card(img, H - 320, W)
img.convert('RGB').save('fig3/Mair_Anzeige_Feed_4x5.jpg', quality=93)

# ---- Story 9:16 ----
W2, H2 = 1080, 1920
bgk = comp.crop((522, 0, 1546, 1280)).resize((W2, int(1280 * W2 / 1024)), Image.LANCZOS)   # 1080x1350
st = Image.new('RGBA', (W2, H2), (8, 18, 11, 255))
blur = comp.resize((int(1920 * H2 / 1280), H2)).crop((600, 0, 600 + W2, H2)).filter(ImageFilter.GaussianBlur(30))
st.alpha_composite(blur.convert('RGBA'))
st.alpha_composite(Image.new('RGBA', (W2, H2), (6, 14, 9, 150)))
top = 300
st.alpha_composite(bgk.convert('RGBA'), (0, top))
grad(st, top + 1000, top + 1350, 0.0, 0.85)
grad(st, top, top + 180, 0.55, 0.0)
headline(st, 60, W2, 84, 112)
hx2 = int((1300 - 522) * W2 / 1024); hy2 = top + int(170 * 1350 / 1280)
bubble(st, 250, hy2 + 100, (hx2 - 40, hy2 + 20))
card(st, H2 - 400, W2)
d = ImageDraw.Draw(st); f = F(SEM, 30); s = 'Aurachtal · Herzogenaurach · Erlangen'
d.text(((W2 - tw(d, s, f)) // 2, H2 - 80), s, font=f, fill=(200, 230, 200))
st.convert('RGB').save('fig3/Mair_Anzeige_Story_9x16.jpg', quality=93)
print('ok')
