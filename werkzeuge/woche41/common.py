"""Gemeinsame Bausteine für die Wochen-Reels (Mair Gebäudetechnik)."""
import os, subprocess, math, random, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GREEN = (108, 208, 74); DARK = (14, 20, 16); WHITE = (255, 255, 255)
PHONE = "09132 / 74 97 5-27"
SFX = "/root/gh_hyperframes/skills/media-use/audio/assets/sfx/"
FI = "/usr/share/fonts/opentype/inter/"
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
LORA_I = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"


def font(name, size):
    path = {"black": FI + "InterDisplay-Black.otf", "bold": FI + "InterDisplay-Bold.otf",
            "semi": FI + "InterDisplay-SemiBold.otf", "reg": FI + "Inter-Regular.otf",
            "med": FI + "Inter-Medium.otf", "lora": LORA, "lorai": LORA_I}[name]
    f = ImageFont.truetype(path, size)
    if name in ("lora", "lorai"):
        try: f.set_variation_by_axes([700 if name == "lora" else 500])
        except Exception: pass
    return f


def logo(width):
    lg = Image.open(os.path.join(REPO, "werkzeuge/marke/mair_logo_aus_anzeige.png")).convert("RGBA")
    h = int(lg.height * width / lg.width)
    return lg.resize((width, h), Image.LANCZOS)


def logo_glow(width, pad=18):
    lg = logo(width)
    card = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], 22, fill=(255, 255, 255, 245))
    card.alpha_composite(lg, (pad, pad))
    return card


def load(path):
    return Image.open(path if path.startswith("/") else os.path.join(REPO, path)).convert("RGB")


def cover(img, w, h, zoom=1.0, cx=0.5, cy=0.5):
    s = max(w / img.width, h / img.height) * zoom
    nw, nh = int(img.width * s + 0.5), int(img.height * s + 0.5)
    im = img.resize((nw, nh), Image.BILINEAR)
    x = int((nw - w) * cx); y = int((nh - h) * cy)
    return im.crop((x, y, x + w, y + h))


def fit_blur(img, w, h, zoom=1.0):
    bg = cover(img, w, h, 1.1).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (w, h), (0, 0, 0)), 0.35)
    s = min(w / img.width, h / img.height) * zoom
    fg = img.resize((int(img.width * s), int(img.height * s)), Image.BILINEAR)
    bg.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2))
    return bg


def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def ease_io(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def back(t):
    t = max(0.0, min(1.0, t)); c = 1.7
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def text_size(d, txt, f):
    b = d.textbbox((0, 0), txt, font=f); return b[2] - b[0], b[3] - b[1]


def wrap(d, txt, f, maxw):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_size(d, t, f)[0] <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines


def shadow_text(img, xy, txt, f, fill=WHITE, anchor="la", blur=8, sh=(0, 0, 0, 170)):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((xy[0] + 3, xy[1] + 4), txt, font=f, fill=sh, anchor=anchor)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    ImageDraw.Draw(layer).text(xy, txt, font=f, fill=fill, anchor=anchor)
    img.alpha_composite(layer) if img.mode == "RGBA" else img.paste(layer, (0, 0), layer)


class Writer:
    def __init__(self, out, dur):
        self.out = out; self.n = int(round(dur * FPS)); self.dur = self.n / FPS
        self.p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                   "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                   "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)

    def put(self, im):
        self.p.stdin.write(im.convert("RGB").tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()


def music(kind, dur, out, bpm=None, drop=None):
    """Erzeugt lizenzfreie Musik aus den Repo-Vorlagen mit angepasster Länge."""
    src = open(os.path.join(REPO, "werkzeuge/musik", kind + ".py")).read()
    src = re.sub(r"DUR\s*=\s*[0-9.]+", f"DUR = {dur:.2f}", src, count=1)
    if bpm: src = re.sub(r"BPM\s*=\s*[0-9.]+", f"BPM = {bpm}", src, count=1)
    if drop is not None: src = re.sub(r"DROP\s*=\s*[0-9.]+", f"DROP = {drop:.2f}", src, count=1)
    src = re.sub(r"wave\.open\('[^']+'", f"wave.open('{out}'", src)
    tmp = out + ".py"; open(tmp, "w").write(src)
    subprocess.run(["python3", tmp], check=True, cwd=os.path.dirname(out), stdout=subprocess.DEVNULL)


def mix(video, musicwav, sfx, out, dur, mvol=0.8):
    """sfx: Liste (zeit, datei, lautstaerke). Musik + Effekte, loudnorm -14 LUFS."""
    ins = ["-i", video, "-i", musicwav]
    fl = [f"[1:a]volume={mvol},afade=t=out:st={max(0, dur - 0.6):.2f}:d=0.6[m]"]
    labels = ["[m]"]
    for k, (t, f, v) in enumerate(sfx):
        ins += ["-i", SFX + f]
        ms = int(max(0, t) * 1000)
        fl.append(f"[{k + 2}:a]volume={v},adelay={ms}|{ms}[s{k}]"); labels.append(f"[s{k}]")
    fl.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,"
              f"atrim=0:{dur:.3f},loudnorm=I=-14:TP=-1.5,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-ac", "2", "-movflags", "+faststart", "-shortest", out], check=True)


def end_card_dark(t, title, sub, cta, accent=GREEN):
    """Abschlusskarte dunkel: Logo, Titel, Telefon, Kommentar-Wort."""
    im = Image.new("RGBA", (W, H), DARK + (255,))
    d = ImageDraw.Draw(im)
    a = ease(t / 0.5)
    lg = logo_glow(560)
    im.alpha_composite(lg, ((W - lg.width) // 2, int(420 - 60 * (1 - a))))
    f1 = font("black", 74); y = 760
    for ln in wrap(d, title, f1, 900):
        d.text((W // 2, y), ln, font=f1, fill=WHITE, anchor="ma"); y += 88
    f2 = font("semi", 46)
    for ln in wrap(d, sub, f2, 900):
        d.text((W // 2, y + 20), ln, font=f2, fill=(200, 210, 200), anchor="ma"); y += 58
    f3 = font("black", 64)
    d.rounded_rectangle([140, 1220, 940, 1330], 55, fill=accent)
    d.text((W // 2, 1275), PHONE, font=f3, fill=DARK, anchor="mm")
    if cta:
        f4 = font("bold", 44)
        pulse = 1 + 0.04 * math.sin(t * 6)
        d.text((W // 2, 1400), cta, font=f4, fill=accent, anchor="ma")
    return im
