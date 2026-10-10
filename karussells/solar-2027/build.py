import asyncio, os
D = os.path.dirname(os.path.abspath(__file__))
P = '/tmp/claude-0/-home-claude-mair-videos-public-create/21fb353a-f208-59b6-a114-5f5699f3e0dd/scratchpad/plakat'
G = '#4fae2a'; L = '#8bd14a'; BG = '#07130c'
FF = ''.join(f"@font-face{{font-family:MI;font-weight:{w};src:url(file://{P}/fonts/Inter-{n}.ttf)}}" for w, n in [(500,'Medium'),(600,'SemiBold'),(700,'Bold'),(800,'ExtraBold')])
N = 9

SUN = f'<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="20" fill="#f5c542"/><g stroke="#f5c542" stroke-width="6" stroke-linecap="round">' + ''.join(f'<line x1="50" y1="12" x2="50" y2="22" transform="rotate({a} 50 50)"/>' for a in range(0, 360, 45)) + '</g></svg>'
HOUSE = f'<svg viewBox="0 0 200 170"><path d="M20 80 L100 15 L180 80" fill="none" stroke="#fff" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/><rect x="40" y="75" width="120" height="85" rx="6" fill="none" stroke="#fff" stroke-width="9"/><g fill="{G}"><rect x="52" y="44" width="30" height="16" transform="skewY(-39) translate(0 66)"/></g><rect x="88" y="110" width="26" height="50" rx="3" fill="{G}"/></svg>'
BATT = f'<svg viewBox="0 0 80 120"><rect x="25" y="4" width="30" height="12" rx="3" fill="#fff"/><rect x="8" y="14" width="64" height="100" rx="10" fill="none" stroke="#fff" stroke-width="7"/><rect x="18" y="58" width="44" height="46" rx="4" fill="{G}"/><rect x="18" y="26" width="44" height="26" rx="4" fill="{L}"/></svg>'
WP = f'<svg viewBox="0 0 140 120"><rect x="6" y="10" width="128" height="96" rx="10" fill="none" stroke="#fff" stroke-width="7"/><circle cx="58" cy="58" r="30" fill="none" stroke="{G}" stroke-width="7"/><g stroke="{L}" stroke-width="6" stroke-linecap="round"><line x1="58" y1="58" x2="58" y2="36"/><line x1="58" y1="58" x2="77" y2="69"/><line x1="58" y1="58" x2="39" y2="69"/></g><line x1="108" y1="28" x2="108" y2="88" stroke="#fff" stroke-width="6"/></svg>'
CAR = f'<svg viewBox="0 0 160 100"><path d="M18 70 L28 40 Q32 30 44 30 L116 30 Q128 30 132 40 L142 70" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round"/><rect x="10" y="66" width="140" height="22" rx="8" fill="none" stroke="#fff" stroke-width="7"/><circle cx="42" cy="90" r="10" fill="{G}"/><circle cx="118" cy="90" r="10" fill="{G}"/><path d="M84 40 L72 60 L84 60 L76 78" fill="none" stroke="{L}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PHONE = f'<svg viewBox="0 0 120 200"><rect x="6" y="6" width="108" height="188" rx="18" fill="#0f2416" stroke="#fff" stroke-width="7"/><rect x="44" y="16" width="32" height="6" rx="3" fill="#fff"/></svg>'


def frame(i, inner, bg=BG):
    dots = ''.join(f'<span style="width:{26 if k==i else 12}px;height:12px;border-radius:6px;background:{L if k==i else "#ffffff40"};display:inline-block;margin-right:8px"></span>' for k in range(1, N+1))
    arrow = '' if i == N else f'<div style="position:absolute;right:64px;bottom:58px;color:{L};font:700 30px MI">weiter wischen &rarr;</div>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{FF}
html,body{{margin:0}} body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:{bg};font-family:MI;color:#fff}}
.h{{font:800 92px/1.02 MI;letter-spacing:-.02em}} .t{{font:500 40px/1.35 MI;color:#d6e8cc}} .g{{color:{L}}}
.tag{{display:inline-block;background:{G};color:#fff;font:800 28px MI;padding:10px 22px;border-radius:10px;letter-spacing:.04em}}
</style></head><body>
<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 85% 0%,#1d4a24 0%,rgba(7,19,12,0) 55%)"></div>
<img src="file://{P}/logo_white.svg" style="position:absolute;left:64px;top:56px;height:96px">
<div style="position:absolute;right:64px;top:74px;font:700 30px MI;color:#ffffff99">{i}/{N}</div>
{inner}
<div style="position:absolute;left:64px;bottom:66px">{dots}</div>{arrow}
</body></html>'''

S = []
# 1 Hook
S.append(f'''<div style="position:absolute;left:64px;top:250px;right:64px">
<div class="tag">SOLAR · NEUE REGELN</div>
<div class="h" style="font-size:150px;margin-top:40px">Solar<br>ab <span class="g">2027</span>:</div>
<div class="h" style="font-size:84px;margin-top:22px">Die Regeln<br>ändern sich.</div>
<div class="t" style="margin-top:40px">Was das für dein Dach in Aurachtal,<br>Herzogenaurach und Erlangen heißt.</div></div>
<div style="position:absolute;right:40px;top:200px;width:260px;height:260px">{SUN}</div>''')
# 2 alt
S.append(f'''<div style="position:absolute;left:64px;top:260px;right:64px">
<div class="tag">BIS 31.12.2026</div>
<div class="h" style="margin-top:40px">Wer 2026 noch<br><span class="g">ans Netz geht,</span><br>bleibt im alten Recht.</div>
<div class="t" style="margin-top:44px">Feste Einspeisevergütung,<br><b style="color:#fff">20 Jahre lang garantiert.</b></div></div>
<div style="position:absolute;left:64px;right:64px;bottom:180px;height:120px;border-radius:20px;background:#0f2416;border:3px solid {G};display:flex;align-items:center;padding:0 36px;font:700 40px MI">20 Jahre<div style="flex:1;margin-left:28px;height:26px;border-radius:13px;background:linear-gradient(90deg,{G},{L})"></div></div>''')
# 3 neu
S.append(f'''<div style="position:absolute;left:64px;top:260px;right:64px">
<div class="tag" style="background:#c0392b">AB 2027 GEPLANT</div>
<div class="h" style="margin-top:40px">Keine 20 Jahre<br>Vergütung mehr.</div>
<div class="t" style="margin-top:44px">Für kleine neue Anlagen gibt es nur noch eine Übergangszahlung:<br><b style="color:#fff">rund 5,2 Cent pro kWh, höchstens 36 Monate.</b><br>Danach musst du deinen Strom selbst vermarkten.</div></div>
<div style="position:absolute;left:64px;right:64px;bottom:180px;height:120px;border-radius:20px;background:#0f2416;border:3px solid #c0392b;display:flex;align-items:center;padding:0 36px;font:700 40px MI">3 Jahre<div style="width:150px;margin-left:28px;height:26px;border-radius:13px;background:#c0392b"></div><div style="flex:1;height:26px;border-radius:13px;margin-left:10px;border:3px dashed #ffffff40"></div></div>''')
# 4 50%
S.append(f'''<div style="position:absolute;left:64px;top:260px;right:64px">
<div class="tag">DIE 50-PROZENT-GRENZE</div>
<div class="h" style="margin-top:40px">Nur noch die <span class="g">Hälfte</span><br>darf ins Netz.</div>
<div class="t" style="margin-top:44px">Neue Dachanlagen unter 100 kW dürfen dauerhaft höchstens 50 Prozent ihrer Leistung einspeisen. Auch mit Smart Meter.</div></div>
<div style="position:absolute;left:64px;right:64px;bottom:170px">
<div style="font:700 34px MI;margin-bottom:14px">Leistung deiner Anlage</div>
<div style="height:90px;border-radius:18px;background:#ffffff18;position:relative;overflow:hidden">
<div style="position:absolute;left:0;top:0;bottom:0;width:50%;background:linear-gradient(90deg,{G},{L})"></div>
<div style="position:absolute;left:50%;top:-10px;bottom:-10px;width:6px;background:#fff"></div>
<div style="position:absolute;left:24px;top:22px;font:800 40px MI">50 % ins Netz</div>
<div style="position:absolute;right:24px;top:22px;font:800 40px MI;color:#ffffffaa">gekappt</div></div></div>''')
# 5 Bedeutung
S.append(f'''<div style="position:absolute;left:64px;top:280px;right:64px">
<div class="h" style="font-size:100px">Heißt für dich:</div>
<div class="h" style="margin-top:50px;font-size:82px">Strom verkaufen<br>lohnt kaum noch.</div>
<div class="h g" style="margin-top:50px;font-size:96px">Selbst nutzen<br>ist der Gewinner.</div></div>''')
# 6 Lösung
S.append(f'''<div style="position:absolute;left:64px;top:250px;right:64px">
<div class="tag">DIE LÖSUNG</div>
<div class="h" style="margin-top:36px">Dein Strom bleibt<br><span class="g">im Haus.</span></div></div>
<div style="position:absolute;left:64px;right:64px;top:700px;display:flex;justify-content:space-between;text-align:center;font:700 34px MI">
<div style="width:290px"><div style="height:200px;display:flex;align-items:center;justify-content:center"><div style="width:120px;height:180px">{BATT}</div></div>Speicher</div>
<div style="width:290px"><div style="height:200px;display:flex;align-items:center;justify-content:center"><div style="width:220px;height:190px">{WP}</div></div>Wärmepumpe</div>
<div style="width:290px"><div style="height:200px;display:flex;align-items:center;justify-content:center"><div style="width:240px;height:150px">{CAR}</div></div>E-Auto</div></div>
<div class="t" style="position:absolute;left:64px;right:64px;top:1010px">Tagsüber heizen, laden und speichern statt für ein paar Cent einspeisen.</div>''')
# 7 ViCare
S.append(f'''<div style="position:absolute;left:64px;top:250px;width:560px">
<div class="tag">CLEVER STEUERN</div>
<div class="h" style="margin-top:36px;font-size:84px">Die Wärme&shy;pumpe läuft, wenn die <span class="g">Sonne scheint.</span></div>
<div class="t" style="margin-top:40px">Gesteuert über <b style="color:#fff">Viessmann ViCare</b>: Die Vitocal nutzt deinen eigenen Solarstrom. Das spart teuren Netzstrom.</div></div>
<div style="position:absolute;right:70px;top:330px;width:330px;height:560px">{PHONE}
<div style="position:absolute;left:30px;right:30px;top:80px;text-align:center">
<div style="width:110px;height:110px;margin:0 auto">{SUN}</div>
<div style="font:800 54px MI;margin-top:8px">ViCare</div>
<div style="font:600 26px MI;color:#d6e8cc;margin-top:6px">Wärmepumpe</div>
<div style="margin-top:22px;height:22px;border-radius:11px;background:#ffffff20;overflow:hidden"><div style="width:78%;height:100%;background:{L}"></div></div>
<div style="font:700 26px MI;margin-top:12px;color:{L}">läuft mit Sonnenstrom</div></div></div>''')
# 8 Stand
S.append(f'''<div style="position:absolute;left:64px;top:280px;right:64px">
<div class="tag" style="background:#d48a1a">WICHTIG</div>
<div class="h" style="margin-top:40px">Noch ist nichts<br>beschlossen.</div>
<div class="t" style="margin-top:44px">Der Bundestag will Mitte Oktober abstimmen, danach ist der Bundesrat dran. Starten soll das Gesetz am 1. Januar 2027. Bis dahin kann sich noch einiges ändern.</div>
<div style="margin-top:60px;font:700 32px MI;color:#ffffff99">Stand: 10.10.2026 · Gesetzentwurf EEG 2027</div></div>''')
# 9 CTA
S.append(f'''<div style="position:absolute;left:64px;top:270px;right:64px">
<div class="h">Lohnt sich PV mit<br>Wärmepumpe <span class="g">bei dir?</span></div>
<div class="t" style="margin-top:40px">Wir rechnen es für dein Haus durch. Ehrlich und mit echten Zahlen.</div>
<div style="margin-top:70px;background:{G};border-radius:22px;padding:34px 40px">
<div style="font:800 46px MI">Anfrage in 1 Minute:</div>
<div style="font:700 38px MI;margin-top:8px">Link in der Bio</div></div>
<div style="margin-top:44px;font:800 64px MI">09132 / 74 97 5-27</div>
<div style="margin-top:12px;font:600 34px MI;color:#d6e8cc">Mair Gebäudetechnik · Aurachtal</div></div>''')


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for i, inner in enumerate(S, 1):
            f = f'{D}/s{i}.html'; open(f, 'w').write(frame(i, inner))
            await pg.goto('file://' + f); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'{D}/Mair_Karussell_Solar2027_{i:02d}.png')
        await b.close()
asyncio.run(main())
