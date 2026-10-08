"""Patrick (Mair-Outfit, p3) maßstabsgetreu rechts neben Viessmann-Wärmepumpe (Render c3d7ac3b)."""
import sys, numpy as np, cv2
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

BG = '/root/.claude/uploads/21fb353a-f208-59b6-a114-5f5699f3e0dd/c3d7ac3b-image.jpg'
FIG = 'fig3/p3_mair_outfit.png'
FH = int(sys.argv[1]) if len(sys.argv) > 1 else 820      # Körpergröße in px (~1,85 m bei ~440 px/m)
CX = int(sys.argv[2]) if len(sys.argv) > 2 else 1300     # Mitte Füße x
FY = int(sys.argv[3]) if len(sys.argv) > 3 else 952      # Fußlinie y

bg = Image.open(BG).convert('RGBA')
fig = Image.open(FIG).convert('RGBA')
FW = int(fig.width * FH / fig.height)
fig = fig.resize((FW, FH), Image.LANCZOS)

# --- Farbangleich: warmes Abendlicht von links ---
rgb = np.array(fig.convert('RGB')).astype(np.float32)
a = np.array(fig.getchannel('A')).astype(np.float32) / 255
xx = np.linspace(0, 1, FW)[None, :, None]
warm = np.array([1.10, 1.00, 0.86])[None, None]
shade = np.array([0.80, 0.84, 0.92])[None, None]
grade = warm * (1 - xx) + shade * xx            # links warm beleuchtet, rechts kühler Schatten
rgb = rgb * grade
rgb = (rgb - 128) * 1.0 + 128 + np.array([3, 0, -4])
# Rim-Light links (Sonnenkante)
edge = cv2.Canny((a * 255).astype(np.uint8), 50, 150).astype(np.float32) / 255
kern = np.zeros((1, 9), np.float32); kern[0, 5:] = 1 / 4             # nur innen rechts der linken Kante
rim = cv2.filter2D(edge, -1, kern) * (1 - xx[..., 0]) * a
rim = cv2.GaussianBlur(rim, (5, 5), 0)
rgb += rim[..., None] * np.array([90, 60, 25])
rgb = np.clip(rgb, 0, 255).astype(np.uint8)
fig = Image.fromarray(np.dstack([rgb, (a * 255).astype(np.uint8)]), 'RGBA')

# Kanten säubern: Alpha 1px einziehen, Randfarben von innen nachziehen
A8 = (a * 255).astype(np.uint8)
A8 = cv2.erode(A8, np.ones((3, 3), np.uint8))
A8 = cv2.GaussianBlur(A8, (3, 3), 0)
band = ((A8 > 0) & (A8 < 250)).astype(np.uint8)
band = cv2.dilate(band, np.ones((5, 5), np.uint8))
fixed = cv2.inpaint(rgb, band, 4, cv2.INPAINT_TELEA)
inner = cv2.erode((A8 >= 250).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
rgb = np.where(inner[..., None], rgb, fixed)
fig = Image.fromarray(np.dstack([rgb, A8]), 'RGBA')
x0 = CX - FW // 2; y0 = FY - FH
out = bg.copy()

# --- Schatten: Kontaktschatten + Schlagschatten nach rechts hinten (Sonne links tief) ---
sil = Image.new('L', bg.size, 0); sil.paste(fig.getchannel('A'), (x0, y0))
S = np.array(sil).astype(np.float32) / 255
src = np.float32([[x0, y0], [x0 + FW, y0], [x0, FY]])
dst = np.float32([[x0 + FH * 0.95, FY - FH * 0.10], [x0 + FW + FH * 0.95, FY - FH * 0.10], [x0, FY]])
M = cv2.getAffineTransform(src, dst)
cast = cv2.warpAffine(S, M, bg.size)
cast = cv2.GaussianBlur(cast, (0, 0), 9)
# Schatten fällt nur auf Boden (unterhalb Hauswand-Sockel ~ y 900) und an die Wand
ground = np.zeros_like(cast); ground[880:] = 1
cast = cast * (0.42 * ground + 0.22 * (1 - ground))
cont = np.zeros_like(S)
cv2.ellipse(cont, (CX, FY - 4), (int(FW * 0.42), 16), 0, 0, 360, 1, -1)
cont = cv2.GaussianBlur(cont, (0, 0), 7) * 0.55
shadow = np.clip(cast + cont, 0, 0.75)
o = np.array(out).astype(np.float32)
o[..., :3] *= (1 - shadow[..., None] * np.array([1.0, 1.0, 0.92])[None, None])
out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8), 'RGBA')

out.alpha_composite(fig, (x0, y0))

# --- Vordergrund-Gras wieder darüber (Gräser vor den Füßen) ---
orig = np.array(bg.convert('RGB')).astype(np.float32)
hsv = cv2.cvtColor(orig.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.int32)
grass = ((hsv[..., 0] > 18) & (hsv[..., 0] < 45) & (hsv[..., 1] > 50)).astype(np.float32)
grass[:FY - 40] = 0
grass = cv2.GaussianBlur(grass, (3, 3), 0)
o = np.array(out).astype(np.float32)
o[..., :3] = o[..., :3] * (1 - grass[..., None]) + orig * grass[..., None]
out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8), 'RGBA')

# --- leichter Kino-Look (warm, Vignette) ---
o = np.array(out.convert('RGB')).astype(np.float32) / 255
H, W = o.shape[:2]
yy, xg = np.mgrid[0:H, 0:W]
vig = 1 - 0.28 * np.clip(((xg - W * 0.55) / (W * 0.75)) ** 2 + ((yy - H * 0.5) / (H * 0.8)) ** 2, 0, 1)
o = o * vig[..., None]
o = o ** np.array([0.97, 1.0, 1.06])
o = np.clip(o * 255, 0, 255).astype(np.uint8)
Image.fromarray(o).save('fig3/comp_mair.jpg', quality=93)
Image.fromarray(o).crop((1000, 80, 1600, 1000)).save('fig3/comp_zoom.jpg', quality=90)
print('figure box', x0, y0, FW, FH)
