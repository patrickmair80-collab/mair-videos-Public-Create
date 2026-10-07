# Mair Werkzeugkasten (Reels, Musik, Mix)

Für jeden neuen Chat: dieses Repo klonen (`git clone https://github.com/patrickmair80-collab/mair-videos-Public-Create`), dann die passende Vorlage kopieren, Bilder/Texte tauschen, rendern. Layout vorher in `LAYOUT-LOG.md` prüfen (nie eins der letzten 3).

| Ordner | Layout | Inhalt |
|---|---|---|
| energienetz_expertdays/ | L6 Energienetz + Vollbild-Fotos mit Chips | Messe-/System-Reel (PV, Speicher, WP, Klima, E-Auto) |
| bad_magazin_dusch_wc/ | L3 Magazin/Editorial (Reel A) + L12 Haken-Karten (Reel B) | Bad-Reels, `python3 render.py A A.mp4` / `B B.mp4` |
| projektmappe/ | L5 Schreibtisch/Projektmappe | Kostenrechnung, Ablauf, Förderantrag |
| kassenbon_waermenetz/ | L4 Kassenbon/Papier | Kostenvergleich mit Stempeln |
| musik/ | eigene lizenzfreie Musik | beat_120, beat_125_energie, lounge_100, spa_ambient_72 (Bad) – BPM/DUR/DROP oben anpassen |
| mix/ | Audio-Mischung | Sprecher + Ducking + Sound-Effekte + loudnorm -14 LUFS |

Voraussetzungen:
- Python 3, Pillow, numpy, scipy, ffmpeg.
- Schriften: /usr/share/fonts/opentype/inter (Inter Display), google-fonts/Lora, DejaVu.
- Sound-Effekte: `git clone https://github.com/heygen-com/hyperframes /root/gh_hyperframes` → skills/media-use/audio/assets/sfx/
- Sprecher (kostenlos): Piper von GitHub rhasspy/piper Release 2023.11.14-2 + Stimme v0.0.2 voice-de-thorsten-low. „Maier“ statt „Mair“ schreiben; ffmpeg in Schleifen mit -nostdin.

Ablage fertiger Videos: Repo-Ordner pro Reel mit POST.md + Google Drive „Mair Werbevideos & Bilder“ (Reels-Ordner). Posten: vidIQ-Upload → Instagram; Composio Facebook.
