"""Reels aus Baustellen-Material 08.10.2026. Aufruf: python3 reels.py r8 r9"""
import sys, os, math, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "woche41"))
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from common import *

OUT = os.path.join(REPO, "woche42"); os.makedirs(OUT, exist_ok=True)
TMP = "/tmp/claude-0/w42"; os.makedirs(TMP, exist_ok=True)
ROH = os.path.join(OUT, "roh")


def finish(name, frames_fn, dur, mus, sfx, mvol=0.8, bpm=None, drop=None):
    vid = f"{TMP}/{name}_v.mp4"; wav = f"{TMP}/{name}_m.wav"
    w = Writer(vid, dur)
    for i in range(w.n): w.put(frames_fn(i / FPS))
    w.close()
    music(mus, w.dur + 0.5, wav, bpm=bpm, drop=drop)
    mix(vid, wav, sfx, f"{OUT}/{name}.mp4", w.dur, mvol)
    print("fertig", name, round(w.dur, 2))


def clip_frames(path, start, dur, speed=1.0):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path,
                          "-vf", f"setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                          "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    return [Image.frombuffer("RGB", (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3]) for i in range(n)]


def stamp(im, txt, color, t, cx=W // 2, cy=980, size=130, rot=-8):
    """Stempel, der mit Wucht aufs Bild knallt."""
    a = ease(t / 0.18)
    if a <= 0: return
    f = font("black", size)
    tw, th = text_size(ImageDraw.Draw(im), txt, f)
    s = Image.new("RGBA", (tw + 90, th + 90), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.rounded_rectangle([8, 8, s.width - 8, s.height - 8], 26, outline=color, width=12)
    d.text((s.width // 2, s.height // 2), txt, font=f, fill=color, anchor="mm")
    s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
    k = 1.6 - 0.6 * a
    s = s.resize((int(s.width * k), int(s.height * k)))
    s.putalpha(s.getchannel("A").point(lambda v: int(v * min(1, a * 1.5))))
    im.alpha_composite(s, (cx - s.width // 2, cy - s.height // 2))


def label(im, txt, y, bg=DARK, fg=WHITE, size=64, t=1.0):
    a = ease(t / 0.25)
    if a <= 0: return
    d = ImageDraw.Draw(im); f = font("black", size)
    tw, th = text_size(d, txt, f)
    x0 = 70; w = (tw + 70) * a
    d.rectangle([x0, y, x0 + w, y + th + 50], fill=bg + (240,))
    if a > 0.7: d.text((x0 + 35, y + 18), txt, font=f, fill=fg)


# ---------------- R8  L16 Montage: Ein Tag bei Mair ----------------
def r8():
    klima = load(os.path.join(ROH, "klima_lieferung.jpg"))
    oel = load(os.path.join(ROH, "oelheizung_alt.jpg"))
    clip = os.path.join(ROH, "pellet_clip.mp4")
    walk = clip_frames(clip, 0.0, 5.2, speed=1.6)      # Rundgang Kessel, schneller
    kabel = clip_frames(clip, 8.6, 2.6, speed=1.3)     # Verkabelung
    B = 60 / 124
    seg = [("klima", 4 * B), ("oel", 4 * B), ("walk", len(walk) / FPS), ("kabel", len(kabel) / FPS), ("next", 4 * B)]
    starts = []; acc = 0
    for n, d in seg: starts.append(acc); acc += d
    END = 3.0; dur = acc + END
    RED = (230, 55, 45)

    def frame(t):
        if t >= acc:
            lt = t - acc
            im = end_card_dark(lt, "Bei dir steht auch so ein Kessel?", "Wir schauen ihn uns an und sagen dir ehrlich, was sich lohnt.",
                               "Kommentiere TAUSCH")
            if lt > END - 0.4:
                f0 = cover(klima, W, H).convert("RGBA")
                im = Image.blend(im, f0, ease((lt - (END - 0.4)) / 0.4))
            return im
        k = max(i for i, s in enumerate(starts) if s <= t); lt = t - starts[k]; name = seg[k][0]
        punch = 1 + 0.03 * max(0, 1 - (t % B) / 0.12)
        if name == "klima":
            im = cover(klima, W, H, (1.02 + 0.05 * lt / seg[k][1]) * punch).convert("RGBA")
            label(im, "Heute bei Mair:", 300, t=lt)
            stamp(im, "LIEFERUNG DA", GREEN, lt - 0.35, cy=1050, size=100)
        elif name == "oel":
            im = cover(oel, W, H, (1.02 + 0.04 * lt / seg[k][1]) * punch).convert("RGBA")
            label(im, "Ölheizung?", 300, t=lt)
            stamp(im, "RAUS", RED, lt - 0.4, cy=1000, size=190)
        elif name == "walk":
            im = walk[min(len(walk) - 1, int(lt * FPS))].convert("RGBA")
            label(im, "Pelletkessel:", 300, t=lt)
            label(im, "alter raus, neuer rein.", 410, bg=GREEN, fg=DARK, size=60, t=lt - 0.3)
        elif name == "kabel":
            im = kabel[min(len(kabel) - 1, int(lt * FPS))].convert("RGBA")
            label(im, "Jede Ader zählt.", 300, t=lt)
        else:
            base = cover(oel, W, H, 1.08).filter(ImageFilter.GaussianBlur(18))
            im = Image.blend(base, Image.new("RGB", (W, H), DARK), 0.55).convert("RGBA")
            d = ImageDraw.Draw(im)
            a = back(lt / 0.35)
            d.text((W // 2, 760), "Als Nächstes:", font=font("bold", 70), fill=WHITE, anchor="ma")
            if a > 0:
                d.text((W // 2, 870), "Wärmepumpe", font=font("black", int(120 * min(1, 0.6 + 0.4 * a))), fill=GREEN, anchor="ma")
                d.text((W // 2, 1010), "rein.", font=font("black", int(120 * min(1, 0.6 + 0.4 * a))), fill=GREEN, anchor="ma")
            d.text((W // 2, 1220), "Folg uns, Teil 2 kommt.", font=font("semi", 50), fill=(210, 220, 210), anchor="ma")
        lg = logo_glow(220, 12); im.alpha_composite(lg, (W - lg.width - 60, H - 470))
        if lt < 0.1 and k > 0:
            im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - lt / 0.1)))))
        return im

    sfx = [(starts[0] + 0.35, "impact-bass-1.mp3", 0.8), (starts[1] + 0.4, "impact-bass-2.mp3", 0.9)]
    sfx += [(s - 0.15, "whoosh.mp3", 0.5) for s in starts[1:]] + [(acc - 0.15, "whoosh-cinematic.mp3", 0.5)]
    sfx += [(starts[4] + 0.1, "riser.mp3", 0.35), (acc + 0.2, "ping.mp3", 0.4)]
    finish("08_Heute_bei_Mair_Oel_raus_Pellet_Tausch", frame, dur, "beat_125_energie", sfx, bpm=124, drop=starts[2])


# ---------------- R9  L8 POV + Farbwechsel: Klimaanlage heizt ----------------
def r9():
    klima = load(os.path.join(ROH, "klima_lieferung.jpg"))
    base = cover(klima, W, H, 1.0)
    cold = Image.blend(base, Image.new("RGB", (W, H), (40, 110, 200)), 0.32)
    warm = Image.blend(ImageEnhance.Color(base).enhance(1.2), Image.new("RGB", (W, H), (235, 120, 40)), 0.30)
    lines = [(2.6, "Schon gewusst?"), (3.6, "Deine Klimaanlage"), (4.4, "kühlt nicht nur."),
             (6.0, "Sie heizt auch."), (8.0, "Mit Strom vom eigenen Dach."), (9.2, "Auch im Winter.")]
    END = 3.2; dur = 11.4 + END

    def frame(t):
        if t >= 11.4:
            lt = t - 11.4
            im = end_card_dark(lt, "Kühlen im Sommer. Heizen im Winter.", "Ein Gerät, Strom von deiner PV-Anlage.",
                               "Kommentiere KLIMA", accent=(255, 150, 60))
            if lt > END - 0.4:
                im = Image.blend(im, cold.convert("RGBA"), ease((lt - (END - 0.4)) / 0.4))
            return im
        z = 1.0 + 0.07 * t / 11.4
        mixv = ease_io((t - 5.4) / 1.2)
        img = Image.blend(cold, warm, mixv)
        im = cover(img, W, H, z).convert("RGBA"); d = ImageDraw.Draw(im)
        # POV-Kopf
        a = ease(t / 0.3)
        d.rectangle([0, 250, W, 250 + int(250 * a)], fill=(0, 0, 0, 150))
        if a > 0.5:
            d.text((70, 280), "POV:", font=font("black", 70), fill=(255, 150, 60) if mixv > 0.5 else (120, 190, 255))
            d.text((70, 365), "Die Klimaanlagen sind da.", font=font("bold", 62), fill=WHITE)
        # Zeilen Wort für Wort mittig
        y = 900
        for st, txt in lines:
            if t < st: continue
            p = back((t - st) / 0.3)
            col = (255, 170, 80) if txt in ("Sie heizt auch.", "Auch im Winter.") else WHITE
            f = font("black", 76 if len(txt) < 20 else 62)
            lay = Image.new("RGBA", (W, 140), (0, 0, 0, 0))
            shadow_text(lay, (W // 2, 70), txt, f, fill=col, anchor="mm")
            s = 0.7 + 0.3 * min(1.1, p)
            lay = lay.resize((int(W * s), int(140 * s)))
            im.alpha_composite(lay, ((W - lay.width) // 2, y - lay.height // 2))
            y += 105
        # Thermometer-Balken rechts: blau -> orange
        h = int(500 * (0.25 + 0.6 * mixv))
        d.rounded_rectangle([60, 900, 100, 1400], 20, fill=(255, 255, 255, 120))
        d.rounded_rectangle([60, 1400 - h, 100, 1400], 20,
                            fill=tuple(int(c1 + (c2 - c1) * mixv) for c1, c2 in zip((90, 170, 255), (255, 140, 50))))
        lg = logo_glow(220, 12); im.alpha_composite(lg, (60, H - 470))
        return im

    sfx = [(0.1, "whoosh-short.mp3", 0.4)] + [(st, "pop.mp3", 0.4) for st, _ in lines]
    sfx += [(5.4, "whoosh-cinematic.mp3", 0.5), (6.0, "impact-bass-1.mp3", 0.7), (11.4, "chime.mp3", 0.45)]
    finish("09_Klimaanlage_heizt_im_Winter", frame, dur, "beat_120", sfx, bpm=104, drop=6.0)


if __name__ == "__main__":
    for a in sys.argv[1:]: globals()[a]()
