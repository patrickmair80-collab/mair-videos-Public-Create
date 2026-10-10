import sys, os, asyncio
from icons import PHONE, GLOBE, PIN
D = os.path.dirname(os.path.abspath(__file__))
B = 3  # Beschnitt mm
GREEN = '#4fae2a'; LIME = '#7cc242'; DARK = '#08140c'
QR = open(f'{D}/qr.svg').read()
SRC = {'q1': (1983, 793), 'q2': (1536, 1024), 'q3': (1254, 1254), 'h1': (941, 1672), 'h2': (941, 1672)}

def img(k, sx0, sy0, sx1, x, y, w, h, extra=''):
    """place source crop starting at (sx0,sy0), width sx1-sx0 mapped to w mm, clipped to box"""
    sw, sh = SRC[k]
    s = w / (sx1 - sx0)
    return (f'<div style="position:absolute;left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;overflow:hidden;{extra}">'
            f'<img src="up/{k}.jpg" style="position:absolute;left:{-sx0*s}mm;top:{-sy0*s}mm;width:{sw*s}mm;height:{sh*s}mm"></div>')

def logo(x, y, h, white=True):
    w = h * 1380 / 768
    return f'<img src="{"logo_white.svg" if white else "logo2.svg"}" style="position:absolute;left:{x}mm;top:{y}mm;height:{h}mm;width:{w}mm">'

def qr(x, y, size, cap=True, capcol='#fff'):
    pad = size * 0.07
    c = (f'<div style="position:absolute;left:{x}mm;top:{y}mm;width:{size}mm;height:{size}mm;background:#fff;border-radius:{size*0.04}mm;padding:{pad}mm;box-sizing:border-box">'
         f'{QR.replace("<svg ", "<svg style=\"width:100%;height:100%;display:block\" ")}</div>')
    if cap:
        c += (f'<div style="position:absolute;left:{x}mm;top:{y+size+size*0.03}mm;width:{size}mm;text-align:center;color:{capcol};'
              f'font:600 {size*0.085}mm MI;letter-spacing:.02em">Homepage scannen</div>')
    return c

def icon(svg, col, x, y, s):
    return f'<div style="position:absolute;left:{x}mm;top:{y}mm;width:{s}mm;height:{s}mm">{svg.format(c=col).replace("<svg ", "<svg style=\"width:100%;height:100%\" ")}</div>'

def contact(x, y, fs, col='#fff', phone=True, web=True, addr=True, cta=None, phonefs=None):
    """stacked contact block; fs = base font size mm"""
    out = []; cy = y
    if cta:
        out.append(f'<div style="position:absolute;left:{x}mm;top:{cy}mm;color:{LIME};font:800 {fs*1.25}mm MI;white-space:nowrap">{cta}</div>')
        cy += fs * 1.25 * 1.35
    if phone:
        pf = phonefs or fs * 2.6
        out.append(icon(PHONE, GREEN, x, cy + pf * 0.12, pf * 0.95))
        out.append(f'<div style="position:absolute;left:{x+pf*1.15}mm;top:{cy-pf*0.08}mm;color:{col};font:800 {pf}mm MI;white-space:nowrap;letter-spacing:-.01em">09132 / 74 97 5-27</div>')
        cy += pf * 1.3
    if web:
        out.append(icon(GLOBE, GREEN, x, cy + fs * 0.05, fs * 1.1))
        out.append(f'<div style="position:absolute;left:{x+fs*1.55}mm;top:{cy-fs*0.05}mm;color:{col};font:600 {fs}mm MI;white-space:nowrap">www.mair-gebäudetechnik.de</div>')
        cy += fs * 1.55
    if addr:
        out.append(icon(PIN, GREEN, x, cy + fs * 0.02, fs * 1.1))
        out.append(f'<div style="position:absolute;left:{x+fs*1.55}mm;top:{cy-fs*0.05}mm;color:{col};font:500 {fs}mm MI;white-space:nowrap">Dorfäcker 1a · 91086 Aurachtal</div>')
        cy += fs * 1.55
    return ''.join(out)

def page(W, H, body):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size:{W}mm {H}mm; margin:0 }}
@font-face{{font-family:MI;font-weight:500;font-style:normal;src:url(fonts/Inter-Medium.ttf)}}
@font-face{{font-family:MI;font-weight:600;font-style:normal;src:url(fonts/Inter-SemiBold.ttf)}}
@font-face{{font-family:MI;font-weight:700;font-style:normal;src:url(fonts/Inter-Bold.ttf)}}
@font-face{{font-family:MI;font-weight:800;font-style:normal;src:url(fonts/Inter-ExtraBold.ttf)}}
@font-face{{font-family:MI;font-weight:800;font-style:italic;src:url(fonts/Inter-ExtraBoldItalic.ttf)}}

html,body{{margin:0;padding:0}}
body{{width:{W}mm;height:{H}mm;position:relative;overflow:hidden;background:{DARK};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
img{{display:block}}
</style></head><body>{body}</body></html>'''

# ---------------- H1: Frau mit Kind (A0 hoch) ----------------
def h1():
    W, H = 841 + 2*B, 1189 + 2*B
    F = 175
    k = W / 941
    sy0 = 1309 - (H - F) / k
    b = img('h1', 0, sy0, 941, 0, 0, W, H - F)
    # Kopf: deckt das weiche Original-Logo ab, neues Vektor-Logo
    b += ('<div style="position:absolute;left:0;top:0;width:100%;height:185mm;'
          'background:linear-gradient(180deg,#06120c 0%,#06120c 68%,rgba(6,18,12,0) 100%)"></div>')
    b += logo(B + 28, B + 16, 100)
    b += (f'<div style="position:absolute;left:{B+33}mm;top:{B+122}mm;color:#fff;font:600 17mm MI;white-space:nowrap">'
          f'Heizung <span style="color:{LIME}">|</span> Sanitär <span style="color:{LIME}">|</span> Klima <span style="color:{LIME}">|</span> Wärmepumpen</div>')
    b += (f'<div style="position:absolute;right:{B+30}mm;top:{B+30}mm;text-align:right;color:#fff;font:italic 800 25mm MI;line-height:1.12">'
          f'Nachhaltig heizen.<br><span style="color:{LIME}">Heute und morgen.</span></div>')
    # Fuß
    b += (f'<div style="position:absolute;left:0;top:{H-F}mm;width:100%;height:{F}mm;background:linear-gradient(180deg,#0b1d11,#050d08);'
          f'border-top:2.5mm solid {GREEN}"></div>')
    b += contact(B + 30, H - F + 22, 17, cta='Jetzt Beratung anfragen!', phonefs=52)
    b += qr(W - B - 30 - 128, H - F + 16, 128, capcol='#cfe8c0')
    return W, H, b

# ---------------- H2: Collage Frau (A0 hoch) ----------------
def h2():
    W, H = 841 + 2*B, 1189 + 2*B
    F = 175
    k = W / 941
    b = img('h2', 0, 0, 941, 0, 0, W, H - F)
    b += (f'<div style="position:absolute;left:0;top:{H-F}mm;width:100%;height:{F}mm;background:linear-gradient(180deg,#0b1d11,#050d08);'
          f'border-top:2.5mm solid {GREEN}"></div>')
    b += contact(B + 30, H - F + 22, 17, cta='Jetzt Beratung anfragen!', phonefs=52)
    b += qr(W - B - 30 - 128, H - F + 16, 128, capcol='#cfe8c0')
    return W, H, b

# ---------------- Q1: Panorama (A0 quer) ----------------
def q1():
    W, H = 1189 + 2*B, 841 + 2*B
    k = W / 1983
    ih = 793 * k
    b = img('q1', 0, 0, 1983, 0, 0, W, ih)
    # falsches Instagram-Handle im Original abdecken und korrigieren
    b += (f'<div style="position:absolute;left:{1580*k}mm;top:{738*k}mm;width:{215*k}mm;height:{38*k}mm;background:#06120d"></div>')
    b += (f'<div style="position:absolute;left:{1625*k}mm;top:{745*k}mm;color:#fff;font:500 {14*k}mm MI;white-space:nowrap">@mair_gebaudetechnik</div>')
    P = H - ih
    b += (f'<div style="position:absolute;left:0;top:{ih}mm;width:100%;height:{P}mm;background:'
          f'radial-gradient(ellipse at 30% 0%,#123220 0%,#07130c 55%,#040b07 100%);border-top:3mm solid {GREEN}"></div>')
    y0 = ih + 42
    b += (f'<div style="position:absolute;left:{B+40}mm;top:{y0}mm;color:#fff;font:800 58mm MI;line-height:1;white-space:nowrap;letter-spacing:-.01em">'
          f'Wir beraten Sie <span style="color:{LIME}">gerne!</span></div>')
    b += (f'<div style="position:absolute;left:{B+43}mm;top:{y0+78}mm;color:#d7e9cf;font:500 24mm MI;white-space:nowrap">'
          f'Wärmepumpe, Heizung, Bad und Klima aus einer Hand.</div>')
    b += contact(B + 40, y0 + 132, 24, phonefs=74)
    q = 250
    b += qr(W - B - 45 - q, ih + 38, q, capcol='#cfe8c0')
    return W, H, b

# ---------------- Q2: Viessmann neu (A0 quer) ----------------
def q2():
    W, H = 1189 + 2*B, 841 + 2*B
    k = W / 1536
    ih = 1024 * k
    S = H - ih
    b = img('q2', 0, 0, 1536, 0, 0, W, ih)
    # Original-Logo scharf ersetzen (exakt auf Position des Original-Logos)
    b += (f'<div style="position:absolute;left:{44*k}mm;top:{38*k}mm;width:{360*k}mm;height:{200*k}mm;'
          f'background:#e9e8e7;filter:blur({4*k}mm)"></div>')
    b += f'<img src="logo2.svg" style="position:absolute;left:{49.95*k}mm;top:{39.9*k}mm;height:{193.8*k}mm;width:{348.2*k}mm">'
    # echter QR-Code statt Platzhalter
    qs = 124 * k
    b += (f'<div style="position:absolute;left:{58*k}mm;top:{846*k}mm;width:{qs}mm;height:{qs}mm;background:#4f8e1c"></div>')
    b += qr(60 * k, 848 * k, 120 * k, cap=False)
    # Zusatzstreifen unten
    b += (f'<div style="position:absolute;left:0;top:{ih}mm;width:100%;height:{S}mm;background:{GREEN}"></div>')
    b += (f'<div style="position:absolute;left:0;top:{ih}mm;width:100%;height:{S}mm;display:flex;align-items:center;justify-content:center;'
          f'color:#fff;font:700 17mm MI;white-space:nowrap;gap:22mm">'
          f'<span>Tel. 09132 / 74 97 5-27</span><span>www.mair-gebäudetechnik.de</span><span>Dorfäcker 1a · 91086 Aurachtal</span></div>')
    return W, H, b

# ---------------- Q3: Bad (A0 quer) ----------------
def q3():
    W, H = 1189 + 2*B, 841 + 2*B
    iw = H  # quadratisch
    b = img('q3', 0, 0, 1254, 0, 0, iw, H)
    PX = iw
    PW = W - iw
    b += (f'<div style="position:absolute;left:{PX}mm;top:0;width:{PW}mm;height:{H}mm;'
          f'background:linear-gradient(180deg,#14201a 0%,#0a120e 100%);border-left:3mm solid {GREEN}"></div>')
    x = PX + 34
    b += (f'<div style="position:absolute;left:{x}mm;top:{B+60}mm;width:{PW-70}mm;color:#fff;font:800 34mm MI;line-height:1.08">'
          f'Fliesen, Bad<br>&amp; Sanitär<br><span style="color:{LIME}">aus einer Hand.</span></div>')
    b += (f'<div style="position:absolute;left:{x}mm;top:{B+205}mm;width:{PW-70}mm;color:#d7e9cf;font:500 17mm MI;line-height:1.35">'
          f'Mit eigenem Fliesenleger.<br>Badausstellung in Aurachtal,<br>Termin nach Vereinbarung.</div>')
    q = 205
    b += qr(x + (PW - 70 - q) / 2, B + 292, q, capcol='#cfe8c0')
    b += (f'<div style="position:absolute;left:{x}mm;top:{B+565}mm;color:{LIME};font:800 19mm MI">Jetzt Beratung anfragen!</div>')
    b += icon(PHONE, GREEN, x, B + 600, 24)
    b += (f'<div style="position:absolute;left:{x+30}mm;top:{B+594}mm;color:#fff;font:800 27mm MI;white-space:nowrap">09132 / 74 97 5-27</div>')
    b += (f'<div style="position:absolute;left:{x}mm;top:{B+645}mm;color:#fff;font:600 14.5mm MI;white-space:nowrap">www.mair-gebäudetechnik.de</div>')
    b += logo(x, B + 715, 82)
    return W, H, b

POSTERS = {'h1': h1, 'h2': h2, 'q1': q1, 'q2': q2, 'q3': q3}

async def render(names, pdf):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for n in names:
            W, H, body = POSTERS[n]()
            html = f'{D}/{n}.html'
            open(html, 'w').write(page(W, H, body))
            pg = await br.new_page(viewport={'width': int(W * 0.8), 'height': int(H * 0.8)}, device_scale_factor=1)
            await pg.goto('file://' + html); await pg.wait_for_timeout(800)
            # Vorschau: Seite in mm -> px skalieren
            await pg.set_viewport_size({'width': int(W * 96 / 25.4), 'height': int(H * 96 / 25.4)})
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=f'{D}/prev_{n}.png', scale='css')
            from PIL import Image
            im=Image.open(f'{D}/prev_{n}.png'); im.thumbnail((1400,1400)); im.save(f'{D}/prev_{n}.png')
            if pdf:
                await pg.pdf(path=f'{D}/{n}.pdf', width=f'{W}mm', height=f'{H}mm', print_background=True, prefer_css_page_size=True, page_ranges='1')
            await pg.close()
        await br.close()

if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else list(POSTERS)
    asyncio.run(render(names, '--pdf' in sys.argv))
