import os, sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 30
REPO = '/home/claude/mair-videos-public-create'
HERE = os.path.dirname(os.path.abspath(__file__))
FD = '/usr/share/fonts/opentype/inter/'
BLACK = FD + 'Inter-Black.otf'; XB = FD + 'Inter-ExtraBold.otf'; BOLD = FD + 'InterDisplay-Bold.otf'
SEMI = FD + 'Inter-SemiBold.otf'; REG = FD + 'Inter-Regular.otf'; MED = FD + 'Inter-Medium.otf'
DJ = '/usr/share/fonts/truetype/dejavu/'
SERIF = DJ + 'DejaVuSerif.ttf'; SERIFB = DJ + 'DejaVuSerif-Bold.ttf'; SERIFI = DJ + 'DejaVuSerif-Italic.ttf'
SERIFBI = DJ + 'DejaVuSerif-BoldItalic.ttf'; MONO = DJ + 'DejaVuSansMono-Bold.ttf'; COND = DJ + 'DejaVuSansCondensed-Bold.ttf'
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]

GREEN = (80, 144, 24); LIME = (150, 200, 40); NAVY = (12, 24, 40); WHITE = (255, 255, 255); INK = (28, 30, 34)

_L = Image.open(HERE + '/../ds/project/assets/Logos/mair-logo.png').convert('RGBA')
_la = np.asarray(_L).astype(float); _la[_la[..., 3] < 70, 3] = 0
LOGO = Image.fromarray(np.uint8(_la), 'RGBA')
_g = (abs(_la[..., 0] - _la[..., 1]) < 18) & (abs(_la[..., 1] - _la[..., 2]) < 18) & (_la[..., 0] < 200)
_la2 = _la.copy(); _la2[_g, :3] = 245
LOGOW = Image.fromarray(np.uint8(_la2), 'RGBA')
def logo(w, white=False):
    L = LOGOW if white else LOGO
    return L.resize((int(w), int(w * L.height / L.width)), Image.LANCZOS)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k

def load(p): return Image.open(p if p.startswith('/') else os.path.join(REPO, p)).convert('RGB')
def cover(im, w, h, fx=0.5, fy=0.5, zoom=1.0):
    w, h = int(w), int(h)
    s = max(w / im.width, h / im.height) * zoom
    nw, nh = int(im.width * s + 0.5), int(im.height * s + 0.5)
    r = im.resize((nw, nh), Image.BILINEAR)
    x = int((nw - w) * fx); y = int((nh - h) * fy)
    return r.crop((x, y, x + w, y + h))

class Clip:
    """frames of a video section, pre-extracted to jpg"""
    def __init__(self, src, start, dur, name, w, h, speed=1.0):
        self.dir = os.path.join(HERE, 'clips', name); self.n = int(dur * FPS)
        if not os.path.exists(os.path.join(self.dir, f'{self.n:04d}.jpg')):
            os.makedirs(self.dir, exist_ok=True)
            vf = f"setpts=PTS/{speed},fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-i', src if src.startswith('/') else os.path.join(REPO, src),
                            '-t', str(dur / speed * speed), '-vf', vf, '-frames:v', str(self.n + 1), '-q:v', '3', self.dir + '/%04d.jpg'], check=True)
        self.files = sorted(f for f in os.listdir(self.dir) if f.endswith('.jpg'))
    def at(self, t):
        i = int(clamp(t * FPS, 0, len(self.files) - 1)); return Image.open(os.path.join(self.dir, self.files[i])).convert('RGB')

class Track:
    """sentence timing from durations; words with char-proportional timing"""
    def __init__(self, sents, durs, start=0.4, gaps=None, tail=1.6):
        self.S = []; t = start
        for i, (s, d) in enumerate(zip(sents, durs)):
            words = s.split(); tot = sum(len(w) + 1 for w in words); ws = []; c = t
            for w in words:
                wd = d * (len(w) + 1) / tot; ws.append((c, wd, w)); c += wd
            self.S.append(dict(t0=t, t1=t + d, text=s, words=ws))
            g = gaps[i] if gaps and i < len(gaps) else 0.45
            t += d + g
        self.end = self.S[-1]['t1'] + tail
        self.vo = []
    def st(self, i): return self.S[i]['t0']
    def en(self, i): return self.S[i]['t1']
    def cur(self, t):
        for i, s in enumerate(self.S):
            if t < s['t1'] + 0.3: return i
        return len(self.S) - 1
    def word(self, t):
        i = self.cur(t)
        for j, (a, d, w) in enumerate(self.S[i]['words']):
            if t < a + d: return i, j
        return i, len(self.S[i]['words']) - 1
    def placements(self): return [[s['t0']] for s in self.S]

def shadow(img, box, rad=30, off=(0, 14), alpha=110, blur=24):
    x0, y0, x1, y1 = box
    m = Image.new('L', (x1 - x0 + 4 * blur, y1 - y0 + 4 * blur), 0)
    ImageDraw.Draw(m).rounded_rectangle([2 * blur, 2 * blur, 2 * blur + x1 - x0, 2 * blur + y1 - y0], rad, fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    img.paste((0, 0, 0), (x0 - 2 * blur + off[0], y0 - 2 * blur + off[1]), m)

def paste_rot(base, im, cx, cy, ang, shadow_a=0):
    imr = im.convert('RGBA').rotate(ang, Image.BICUBIC, expand=True)
    x, y = int(cx - imr.width / 2), int(cy - imr.height / 2)
    if shadow_a:
        a = imr.split()[3].filter(ImageFilter.GaussianBlur(18)).point(lambda v: v * shadow_a // 255)
        base.paste((0, 0, 0), (x + 10, y + 22), a)
    base.paste(imr, (x, y), imr)

def round_mask(w, h, r):
    m = Image.new('L', (int(w), int(h)), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, int(w) - 1, int(h) - 1], r, fill=255); return m

def tw(d, s, f): return d.textlength(s, font=f)

def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if tw(d, t, f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def grain(img, amt=7, seed=0):
    rng = np.random.default_rng(seed); a = np.asarray(img).astype(np.int16)
    n = rng.integers(-amt, amt + 1, size=a.shape[:2], dtype=np.int16)[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))

def render(name, frame_fn, dur, out_dir=None, procs=2):
    out_dir = out_dir or os.path.join(HERE, 'out', name); os.makedirs(out_dir, exist_ok=True)
    N = int(round(dur * FPS))
    s, e = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, N)
    for n in range(s, min(e, N)):
        p = f'{out_dir}/{n:04d}.jpg'
        if not os.path.exists(p): frame_fn(n / FPS).convert('RGB').save(p, quality=90)
    return N

def encode(name, dur, dst):
    d = os.path.join(HERE, 'out', name)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', d + '/%04d.jpg', '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst], check=True)
