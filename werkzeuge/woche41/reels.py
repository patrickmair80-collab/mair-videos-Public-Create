"""7 Wochen-Reels KW 41/42 2026. Aufruf: python3 reels.py r1 [r2 ...]"""
import sys, os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import *

OUT = os.path.join(REPO, "woche41"); os.makedirs(OUT, exist_ok=True)
TMP = "/tmp/claude-0/w41"; os.makedirs(TMP, exist_ok=True)
BAD = "bad-serie/fotos/Mair_Bad_{}.jpg"


def finish(name, frames_fn, dur, mus, sfx, mvol=0.8, bpm=None, drop=None):
    vid = f"{TMP}/{name}_v.mp4"; wav = f"{TMP}/{name}_m.wav"
    w = Writer(vid, dur)
    for i in range(w.n):
        w.put(frames_fn(i / FPS))
    w.close()
    music(mus, w.dur + 0.5, wav, bpm=bpm, drop=drop)
    mix(vid, wav, sfx, f"{OUT}/{name}.mp4", w.dur, mvol)
    print("fertig", name, round(w.dur, 2))


# ---------------- R1  L15 Fliesenraster: eigener Fliesenleger ----------------
def r1():
    shots = [("c4d0eb23", "Fliesen?", "Machen wir selbst."),
             ("625344f4", "Eigener", "Fliesenleger."),
             ("8c3473ed", "Kein Subunternehmer.", "Kein Warten."),
             ("f97d34de", "Bad, Garage,", "Terrasse.")]
    imgs = [load(BAD.format(s[0])) for s in shots]
    SH, END = 2.6, 3.6; dur = SH * len(shots) + END
    T = 120; cols, rows = W // T + 1, H // T + 1
    rnd = random.Random(4)
    orders = []
    for k in range(len(shots)):
        o = {}
        for c in range(cols):
            for r in range(rows):
                o[(c, r)] = (c + r) / (cols + rows) * 0.55 + rnd.random() * 0.25
        orders.append(o)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(grid)
    for c in range(cols + 1): g.line([(c * T, 0), (c * T, H)], fill=(255, 255, 255, 70), width=3)
    for r in range(rows + 1): g.line([(0, r * T), (W, r * T)], fill=(255, 255, 255, 70), width=3)
    tilebg = Image.new("RGB", (W, H), (236, 236, 232)); tb = ImageDraw.Draw(tilebg)
    for c in range(cols + 1): tb.line([(c * T, 0), (c * T, H)], fill=(205, 205, 200), width=4)
    for r in range(rows + 1): tb.line([(0, r * T), (W, r * T)], fill=(205, 205, 200), width=4)
    fA, fB = font("lora", 96), font("black", 88)

    def frame(t):
        k = int(t // SH)
        if k < len(shots):
            lt = t - k * SH
            base = Image.new("RGB", (W, H)); base.paste(tilebg)
            if k > 0: base = cover(imgs[k - 1], W, H, 1.06)
            pic = cover(imgs[k], W, H, 1.0 + 0.06 * lt / SH)
            mask = Image.new("L", (W, H), 0); md = ImageDraw.Draw(mask)
            for (c, r), st in orders[k].items():
                p = ease((lt - st) / 0.22)
                if p <= 0: continue
                s = T * p; cx, cy = c * T + T / 2, r * T + T / 2
                md.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2], fill=255)
            im = Image.composite(pic, base, mask).convert("RGBA")
            ga = 1 - ease((lt - 0.9) / 0.6)
            if ga > 0:
                gg = grid.copy(); gg.putalpha(gg.getchannel("A").point(lambda v: int(v * ga)))
                im.alpha_composite(gg)
            # Textkarte
            a1 = ease((lt - 0.25) / 0.35); a2 = ease((lt - 0.55) / 0.35)
            d = ImageDraw.Draw(im)
            l1, l2 = shots[k][1], shots[k][2]
            y0 = 300
            if a1 > 0:
                fA1 = fA if text_size(d, l1, fA)[0] < 860 else font("lora", int(96 * 860 / text_size(d, l1, fA)[0]))
                w1 = text_size(d, l1, fA1)[0]
                d.rectangle([90, y0 - 20, 90 + (w1 + 60) * a1, y0 + 115], fill=(255, 255, 255, 240))
                if a1 > 0.6: d.text((120, y0), l1, font=fA1, fill=DARK)
            if a2 > 0:
                w2 = text_size(d, l2, fB)[0]
                d.rectangle([90, y0 + 130, 90 + (w2 + 60) * a2, y0 + 250], fill=GREEN + (255,))
                if a2 > 0.6: d.text((120, y0 + 145), l2, font=fB, fill=DARK)
            lg = logo_glow(250, 12); im.alpha_composite(lg, (W - lg.width - 60, H - 470))
            return im
        lt = t - len(shots) * SH
        im = tilebg.copy().convert("RGBA"); d = ImageDraw.Draw(im)
        a = ease(lt / 0.5)
        lg = logo_glow(600); im.alpha_composite(lg, ((W - lg.width) // 2, int(380 + 40 * (1 - a))))
        d.text((W // 2, 760), "Bad & Fliesen", font=font("lora", 100), fill=DARK, anchor="ma")
        d.text((W // 2, 880), "aus einer Hand.", font=font("lora", 100), fill=DARK, anchor="ma")
        d.text((W // 2, 1030), "Mit eigenem Fliesenleger und", font=font("semi", 46), fill=(60, 70, 60), anchor="ma")
        d.text((W // 2, 1090), "eigener Badausstellung in Aurachtal.", font=font("semi", 46), fill=(60, 70, 60), anchor="ma")
        d.rounded_rectangle([140, 1200, 940, 1310], 55, fill=GREEN)
        d.text((W // 2, 1255), PHONE, font=font("black", 64), fill=DARK, anchor="mm")
        d.text((W // 2, 1370), "Kommentiere BAD für einen Termin", font=font("bold", 44), fill=(40, 120, 30), anchor="ma")
        if lt > END - 0.4:  # Loop zurück zum ersten Bild
            f0 = cover(imgs[0], W, H, 1.0).convert("RGBA")
            im = Image.blend(im, f0, ease((lt - (END - 0.4)) / 0.4))
        return im

    sfx = [(k * SH - 0.15, "whoosh-short.mp3", 0.3) for k in range(1, len(shots) + 1)]
    sfx += [(k * SH + 0.3, "pop.mp3", 0.35) for k in range(len(shots))]
    sfx += [(len(shots) * SH + 0.2, "chime.mp3", 0.5)]
    finish("01_Bad_eigener_Fliesenleger_Fliesenraster", frame, dur, "spa_ambient_72", sfx, mvol=0.9)


# ---------------- R2  L1 Vollbild-Kino: Heizsaison ----------------
def r2():
    imgs = [load(f"heizsaison/Mair_Heizsaison_{i}.jpg") for i in range(1, 7)]
    SH, END = 2.0, 3.0; dur = SH * 6 + END
    fH = font("black", 84)

    def frame(t):
        k = int(t // SH)
        if k < 6:
            lt = t - k * SH
            beat = 1 + 0.025 * max(0, 1 - (lt % 0.5) / 0.15) if t > 2 else 1
            z0 = 0.86 if k == 0 else 1.0
            im = fit_blur(imgs[k], W, H, zoom=(z0 + 0.04 * lt / SH) * beat).convert("RGBA")
            d = ImageDraw.Draw(im)
            # Kinobalken
            d.rectangle([0, 0, W, 120], fill=(0, 0, 0, 255)); d.rectangle([0, H - 120, W, H], fill=(0, 0, 0, 255))
            if k == 0:
                a = back(lt / 0.4)
                y = int(150 + 40 * (1 - a))
                shadow_text(im, (W // 2, y), "Heizung schon", fH, anchor="ma")
                shadow_text(im, (W // 2, y + 92), "gecheckt?", fH, fill=GREEN, anchor="ma")
            if lt < 0.12 and k > 0:
                fl = Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - lt / 0.12)))); im.alpha_composite(fl)
            return im
        lt = t - 6 * SH
        im = end_card_dark(lt, "Wartung vor dem ersten Frost.", "Wir kommen vorbei, du bleibst auf dem Sofa.",
                           "Kommentiere WARTUNG")
        if lt > END - 0.4:
            f0 = fit_blur(imgs[0], W, H).convert("RGBA")
            im = Image.blend(im, f0, ease((lt - (END - 0.4)) / 0.4))
        return im

    sfx = [(0.2, "impact-bass-1.mp3", 0.8)] + [(k * SH - 0.15, "whoosh.mp3", 0.5) for k in range(1, 7)]
    sfx += [(6 * SH - 1.0, "riser.mp3", 0.4)]
    finish("02_Heizsaison_Check_Kino", frame, dur, "beat_120", sfx, bpm=120, drop=2.0)


# ---------------- R3  L17 Einwand: Wärmepumpe im Altbau ----------------
def clip_frames(path, start, dur):
    """liest Frames eines Clips als Liste PIL-Bilder (1080x1920)."""
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-t", str(dur), "-i",
                          os.path.join(REPO, path), "-vf", f"scale={W}:{H},fps={FPS}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    return [Image.frombuffer("RGB", (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3]) for i in range(n)]


def r3():
    clip = clip_frames("Mair_Reel_Kurz_altbau.mp4", 0, 7.0)
    INTRO, END = 2.0, 2.6; CL = len(clip) / FPS; dur = INTRO + CL + END
    fQ = font("lorai", 78); fS = font("black", 120)

    def frame(t):
        if t < INTRO:
            im = Image.new("RGBA", (W, H), (18, 18, 18, 255)); d = ImageDraw.Draw(im)
            d.text((W // 2, 640), "„Wärmepumpe", font=fQ, fill=(230, 230, 230), anchor="ma")
            d.text((W // 2, 740), "im Altbau?", font=fQ, fill=(230, 230, 230), anchor="ma")
            d.text((W // 2, 840), "Vergiss es.“", font=fQ, fill=(230, 230, 230), anchor="ma")
            d.text((W // 2, 980), "sagt dein Nachbar", font=font("med", 40), fill=(150, 150, 150), anchor="ma")
            p = ease((t - 0.7) / 0.35)
            if p > 0: d.line([(170, 880), (170 + 740 * p, 880)], fill=(230, 60, 50), width=14)
            p2 = back((t - 1.15) / 0.35)
            if p2 > 0:
                txt = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
                ImageDraw.Draw(txt).text((W // 2, 150), "Stimmt nicht.", font=fS, fill=GREEN, anchor="mm")
                s = 0.6 + 0.4 * p2
                txt = txt.resize((int(W * s), int(300 * s)))
                im.alpha_composite(txt, ((W - txt.width) // 2, 1150 - txt.height // 2))
            return im
        if t < INTRO + CL:
            i = min(len(clip) - 1, int((t - INTRO) * FPS))
            im = clip[i].convert("RGBA")
            return im
        lt = t - INTRO - CL
        im = end_card_dark(lt, "Wir prüfen dein Haus vor Ort.", "Heizkörper, Verbrauch, Platz fürs Außengerät.",
                           "Die 4 Zeichen stehen in der Beschreibung")
        return im

    sfx = [(0.1, "typing.mp3", 0.3), (0.7, "glitch-1.mp3", 0.5), (1.15, "impact-bass-2.mp3", 0.9),
           (INTRO - 0.15, "whoosh-cinematic.mp3", 0.6), (INTRO + CL - 0.15, "whoosh.mp3", 0.5)]
    finish("03_Waermepumpe_Altbau_Einwand", frame, dur, "beat_125_energie", sfx, bpm=125, drop=INTRO)


# ---------------- R4  L7 Chat-Verlauf: begehbare Dusche ----------------
def r4():
    msgs = [(0.2, "in", "Hallo! Lohnt sich eine begehbare Dusche statt Wanne?"),
            (2.2, "out", "Ja, vor allem wenn das Bad sowieso neu gemacht wird."),
            (4.2, "img", "8c3473ed"),
            (6.6, "img", "e5a0ff98"),
            (9.0, "in", "Und wer macht die Fliesen?"),
            (10.6, "out", "Unser eigener Fliesenleger. Alles aus einer Hand.")]
    imgs = {m[2]: load(BAD.format(m[2])) for m in msgs if m[1] == "img"}
    END = 3.0; dur = 12.6 + END
    fM = font("semi", 46); fT = font("reg", 26)
    bg = Image.new("RGB", (W, H), (236, 229, 221)); bd = ImageDraw.Draw(bg)
    rnd = random.Random(2)
    for _ in range(260):
        x, y = rnd.randint(0, W), rnd.randint(0, H); r = rnd.randint(6, 16)
        bd.ellipse([x - r, y - r, x + r, y + r], outline=(222, 214, 204), width=3)
    tmpd = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    def bubble(m):
        kind, val = m[1], m[2]
        if kind == "img":
            ph = cover(imgs[val], 620, 800)
            b = Image.new("RGBA", (660, 840), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
            d.rounded_rectangle([0, 0, 659, 839], 28, fill=(220, 248, 198))
            mask = Image.new("L", (620, 800), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, 619, 799], 22, fill=255)
            b.paste(ph, (20, 20), mask); return b
        lines = wrap(tmpd, val, fM, 700)
        wmax = max(text_size(tmpd, l, fM)[0] for l in lines)
        bw, bh = wmax + 80, 70 * len(lines) + 80
        b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
        d.rounded_rectangle([0, 0, bw - 1, bh - 1], 30, fill=(255, 255, 255) if kind == "in" else (220, 248, 198))
        for i, l in enumerate(lines): d.text((40, 32 + i * 70), l, font=fM, fill=(20, 20, 20))
        d.text((bw - 30, bh - 18), "10:0" + str(min(9, int(m[0]))), font=fT, fill=(130, 130, 130), anchor="rb")
        return b

    bubbles = [bubble(m) for m in msgs]

    def frame(t):
        im = bg.copy().convert("RGBA"); d = ImageDraw.Draw(im)
        # Kopfzeile
        d.rectangle([0, 0, W, 250], fill=(7, 94, 84))
        lg = logo_glow(150, 8); im.alpha_composite(lg, (60, 115))
        d.text((260, 135), "Mair Gebäudetechnik", font=font("bold", 48), fill=WHITE)
        d.text((260, 195), "online", font=font("reg", 34), fill=(200, 230, 220))
        # Nachrichten stapeln, nach oben schieben
        y = 300; placed = []
        for (st, kind, _), b in zip(msgs, bubbles):
            if t < st: break
            a = ease((t - st) / 0.25)
            placed.append((b, kind, y, a)); y += b.height + 28
        bottom_limit = H - 430
        shift = max(0, y - bottom_limit)
        for b, kind, yy, a in placed:
            x = 50 if kind == "in" else W - 50 - b.width
            bb = b.copy()
            if a < 1: bb.putalpha(bb.getchannel("A").point(lambda v: int(v * a)))
            yy2 = int(yy - shift + 30 * (1 - a))
            if yy2 + b.height > 250: im.paste(bb, (x, yy2), bb)
        d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 250], fill=(7, 94, 84))
        im.alpha_composite(lg, (60, 115))
        d.text((260, 135), "Mair Gebäudetechnik", font=font("bold", 48), fill=WHITE)
        # Tipp-Punkte vor jeder Antwort
        for st, kind, _ in msgs:
            if kind != "in" and st - 0.9 < t < st:
                x0 = W - 230; y0 = min(y - shift, bottom_limit) + 10
                d.rounded_rectangle([x0, y0, x0 + 170, y0 + 80], 30, fill=(220, 248, 198))
                for j in range(3):
                    o = 0.5 + 0.5 * math.sin(t * 10 - j)
                    d.ellipse([x0 + 35 + j * 40, y0 + 30 - 6 * o, x0 + 55 + j * 40, y0 + 50 - 6 * o], fill=(90, 90, 90))
        if t >= 12.6:
            lt = t - 12.6; a = ease(lt / 0.4)
            ov = end_card_dark(lt, "Bad neu? Wir planen mit dir.", "Eigener Fliesenleger, eigene Badausstellung.",
                               "Schreib uns DUSCHE")
            ov.putalpha(int(255 * a)); im.alpha_composite(ov)
        return im

    sfx = [(m[0], "pop.mp3", 0.45) for m in msgs] + [(m[0] - 0.9, "typing.mp3", 0.25) for m in msgs if m[1] != "in"]
    sfx += [(12.6, "chime.mp3", 0.5)]
    finish("04_Bad_begehbare_Dusche_Chat", frame, dur, "lounge_100", sfx, bpm=100, drop=2.2)


# ---------------- R5  L16 echter Clip: 3 Fehler beim Heizungstausch ----------------
def r5():
    clip = clip_frames("Mair_Reel_Kurz_heizung.mp4", 0, 7.0)
    CL = len(clip) / FPS; END = 2.6; dur = CL + END

    def frame(t):
        if t < CL:
            i = min(len(clip) - 1, int(t * FPS))
            beat = 1 + 0.02 * max(0, 1 - (t % (60 / 110)) / 0.12) if t > 0.5 else 1
            im = clip[i]
            if beat > 1:
                im = cover(im, W, H, beat)
            return im.convert("RGBA")
        lt = t - CL
        return end_card_dark(lt, "Heizungstausch ohne teure Fehler.", "Heizlast, Abgleich, Förderung: machen wir richtig.",
                             "Liste in der Beschreibung")

    sfx = [(0.05, "impact-bass-1.mp3", 0.7), (CL - 0.15, "whoosh-cinematic.mp3", 0.6), (CL + 0.2, "ping.mp3", 0.4)]
    finish("05_Heizungstausch_3_Fehler", frame, dur, "beat_120", sfx, bpm=110, drop=4.0)


# ---------------- R6  L10 Polaroid-Stapel: Bad & Bau aus einer Hand ----------------
def r6():
    items = [("04ef2100", "Wanne unterm Dach"), ("625344f4", "Marmor-Optik"), ("f3dafa0e", "Mosaik-Streifen"),
             ("e8a74be4", "Waschtisch mit Stauraum"), ("6a435537", "Dachschräge genutzt"), ("c38b8beb", "Licht im Spiegel")]
    rnd = random.Random(7)
    pols = []
    for code, cap in items:
        ph = cover(load(BAD.format(code)), 640, 640)
        p = Image.new("RGBA", (720, 860), (250, 250, 247, 255))
        p.paste(ph, (40, 40))
        ImageDraw.Draw(p).text((360, 760), cap, font=font("lorai", 50), fill=(40, 40, 40), anchor="mm")
        sh = Image.new("RGBA", (760, 900), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([20, 28, 740, 888], fill=(0, 0, 0, 110)); sh = sh.filter(ImageFilter.GaussianBlur(14))
        sh.alpha_composite(p, (20, 20))
        pols.append((sh, rnd.uniform(-9, 9), rnd.randint(-90, 90), rnd.randint(-60, 120), rnd.choice([-1, 1])))
    # Holztisch
    yy = np.arange(H)[:, None]; xx = np.arange(W)[None, :]
    n = np.sin(xx / 37 + np.sin(yy / 230) * 3) * 0.5 + np.sin(xx / 9 + yy / 400) * 0.2
    base = np.stack([128 + 22 * n, 86 + 16 * n, 52 + 10 * n], -1).clip(0, 255).astype(np.uint8)
    wood = Image.fromarray(base).filter(ImageFilter.GaussianBlur(1.2))
    for k in range(1, 6): ImageDraw.Draw(wood).line([(k * 216, 0), (k * 216, H)], fill=(70, 45, 25), width=4)
    SH, END = 1.7, 3.4; dur = 0.8 + SH * len(items) + END
    fT = font("black", 84)

    def frame(t):
        im = wood.copy().convert("RGBA")
        for k, (p, ang, dx, dy, side) in enumerate(pols):
            st = 0.8 + k * SH
            if t < st: break
            a = ease((t - st) / 0.45)
            rot = ang + side * 25 * (1 - a)
            pr = p.rotate(rot, resample=Image.BICUBIC, expand=True)
            s = 1.0 + 0.25 * (1 - a)
            pr = pr.resize((int(pr.width * s), int(pr.height * s)), Image.BILINEAR)
            cx = W // 2 + dx + side * 900 * (1 - a); cy = 1050 + dy
            im.alpha_composite(pr, (int(cx - pr.width / 2), int(cy - pr.height / 2)))
        d = ImageDraw.Draw(im)
        a = back(t / 0.45)
        d.rounded_rectangle([60, 260, 1020, 520], 30, fill=(14, 20, 16, int(235 * min(1, a))))
        d.text((W // 2, 300), "Bäder aus unserer", font=fT, fill=WHITE, anchor="ma")
        d.text((W // 2, 400), "Region.", font=fT, fill=GREEN, anchor="ma")
        lg = logo_glow(230, 12); im.alpha_composite(lg, (W - lg.width - 60, H - 470))
        T0 = 0.8 + SH * len(items)
        if t >= T0:
            lt = t - T0; ov = end_card_dark(lt, "Bad & Bau aus einer Hand.",
                                            "Eigene Badausstellung, eigener Fliesenleger. Ausstellung nach Termin.",
                                            "Kommentiere AUSSTELLUNG")
            ov.putalpha(int(255 * ease(lt / 0.4))); im.alpha_composite(ov)
        return im

    sfx = [(0.8 + k * SH, "whoosh-short.mp3", 0.35) for k in range(len(items))]
    sfx += [(0.8 + k * SH + 0.4, "click-soft.mp3", 0.5) for k in range(len(items))]
    sfx += [(0.8 + SH * len(items), "chime.mp3", 0.45)]
    finish("06_Bad_und_Bau_aus_einer_Hand_Polaroid", frame, dur, "lounge_100", sfx, bpm=92, drop=2.4)


# ---------------- R7  L14 Text-Maske: Azubi gesucht ----------------
def r7():
    clip = clip_frames("Mair_Reel_Kurz_heizung.mp4", 0, 3.4)
    bad1, bad2 = load(BAD.format("e5a0ff98")), load(BAD.format("04ef2100"))
    fBig = font("black", 250); fMid = font("black", 300)
    bad0 = load(BAD.format("f3dafa0e"))

    def masked(word, f, src, t0, t):
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        p = back((t - t0) / 0.4); s = 0.7 + 0.3 * min(1.2, p)
        tmp = Image.new("L", (W, 420), 0)
        ImageDraw.Draw(tmp).text((W // 2, 210), word, font=f, fill=255, anchor="mm")
        tmp = tmp.resize((int(W * s), int(420 * s)))
        m.paste(tmp, ((W - tmp.width) // 2, 900 - tmp.height // 2))
        out = Image.new("RGBA", (W, H), DARK + (255,))
        out.paste(src, (0, 0), m)
        from PIL import ImageChops
        ring = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(9)), m)
        out.paste(GREEN, (0, 0), ring)
        return out

    lines = ["Wärmepumpe. Bad. Klima.", "Du lernst alles", "an echten Baustellen."]
    END = 3.0; dur = 9.0 + END

    def frame(t):
        if t < 3.0:
            src = cover(bad0, W, H, 1.0 + 0.08 * t / 3, cy=0.45)
            im = masked("AZUBI", fBig, src, 0, t); d = ImageDraw.Draw(im)
            d.text((W // 2, 560), "Wir suchen dich:", font=font("bold", 64), fill=WHITE, anchor="ma")
            d.text((W // 2, 1180), "Anlagenmechaniker SHK (m/w/d)", font=font("semi", 50), fill=GREEN, anchor="ma")
            return im
        if t < 6.0:
            src = cover(bad1, W, H, 1.0 + 0.05 * (t - 3) / 3)
            im = masked("SHK", fMid, src, 3.0, t); d = ImageDraw.Draw(im)
            for i, l in enumerate(lines):
                a = ease((t - 3.3 - i * 0.5) / 0.3)
                if a > 0: d.text((W // 2, 1180 + i * 80 + int(20 * (1 - a))), l, font=font("bold", 58),
                                 fill=WHITE if i else GREEN, anchor="ma")
            return im
        if t < 9.0:
            src = cover(bad2, W, H, 1.05 - 0.05 * (t - 6) / 3)
            im = masked("TEAM", font("black", 280), src, 6.0, t); d = ImageDraw.Draw(im)
            a = ease((t - 6.4) / 0.3)
            if a > 0:
                d.text((W // 2, 1180), "Schnuppertag? Praktikum?", font=font("bold", 58), fill=WHITE, anchor="ma")
                d.text((W // 2, 1260), "Einfach anrufen.", font=font("bold", 58), fill=GREEN, anchor="ma")
            return im
        lt = t - 9.0
        im = end_card_dark(lt, "Ausbildung bei Mair in Aurachtal.", "3,5 Jahre, verkürzbar. Meisterbetrieb.",
                           "Kommentiere AZUBI")
        if lt > END - 0.4:
            f0 = masked("AZUBI", fBig, cover(bad0, W, H, 1.0, cy=0.45), -1, 0)
            im = Image.blend(im, f0, ease((lt - (END - 0.4)) / 0.4))
        return im

    sfx = [(0.05, "impact-bass-2.mp3", 0.9), (2.85, "whoosh.mp3", 0.6), (3.0, "impact-bass-1.mp3", 0.7),
           (5.85, "whoosh.mp3", 0.6), (6.0, "impact-bass-1.mp3", 0.7), (8.85, "riser.mp3", 0.35), (9.0, "ping.mp3", 0.4)]
    finish("07_Azubi_gesucht_Textmaske", frame, dur, "beat_125_energie", sfx, bpm=128, drop=3.0)


if __name__ == "__main__":
    for a in sys.argv[1:]: globals()[a]()
