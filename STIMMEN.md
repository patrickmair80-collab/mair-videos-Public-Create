# Sprecherstimme (Stand 09.10.2026, final)

**Gewählt: Hörprobe 3 "Thorsten rein deutsch"** = Piper-Modell `de_DE-thorsten-high` (rhasspy/piper-voices, Sprecher Thorsten Müller, frei nutzbar). Rein deutsch, deterministisch, kein Stocken, kein Englisch. length-scale 1.1, sentence-silence 0.4. Chatterbox (Stimme 4) wird NICHT mehr verwendet.

Aussprache-Schreibweisen nur für die Stimme (Untertitel bleiben normal): Gebäudetechnik → "Gebäude-Technik", Stromspeicher → "Strohmspeicher", Wärmepumpe → "Wärme-Pumpe", Aurachtal → "Aurachthal" (Betonung AU-rach-tal), Strom → "Strohm", Sonnenstrom → "Strohm von der Sonne" (zusammengesetzt wird "Sonnen" verschluckt), "schickt dir" nur mit length-scale 1.25. Neue Wörter vorher mit phonemize() prüfen.

---

# Alt: "Stimme 4"

**Regel von Patrick:** In allen Videos immer dieselbe Stimme. Langsam, sauber, natürlich. Kein Englisch, kein amerikanischer Slang, keine Abkürzungen im Sprechertext. Nicht zwischen Stimmen wechseln.

## Technik
- Modell: Chatterbox Multilingual (Resemble AI, MIT-Lizenz), Sprache `de`
- Referenzstimme: `ref_florian.wav` (Sicherung im Composio-Arbeitsbereich unter /mnt/files/stimme4/)
- Einstellungen: exaggeration 0.4 (Figuren/Gesichter 0.65), temperature 0.6, cfg 0.5, seed 42
- Danach: atempo 0.95 (etwas langsamer), Stille abschneiden, VCHAIN (Hochpass, EQ, De-Esser, Kompressor, loudnorm -15 LUFS)
- Server: Hugging Face Space `ResembleAI/Chatterbox-Multilingual-TTS` (Gratis-Kontingent nach ~3 Sätzen leer), Ausweich-Server mit gleichem Modell: `TGPro1/Chatterbox-Multilingual-TTS` (CPU, ca. 30-45 s pro Satz, kein Kontingent)
- Kontrolle: jede Zeile per Whisper zurückschreiben, bei Wiederholungen/Nuscheln mit anderem Seed neu erzeugen und die bessere nehmen (pick.py)

## Schreibregeln für Sprechertexte
- "Maier" schreiben, damit es richtig ausgesprochen wird (im Bild steht "Mair")
- Keine sehr kurzen Einzelsätze (1-2 Wörter): das Modell wiederholt sie sonst. Lieber zusammenfassen ("Die Halterung. Die Leitungen. Und sie läuft.")
- Ersetzen: App → am Handy · KI → künstliche Intelligenz · E3/DC → Hauskraftwerk/Speicher · WindFree → weglassen (nur im Bild) · 200-A ie → "die Wärmepumpe von Viessmann" · Zahlen ausschreiben
- Produktnamen und Abkürzungen dürfen im Bild stehen, nicht im Sprechertext

## Umgestellte Videos (Drive-Ordner Reels)
| Video | Datei |
|---|---|
| Klima Mini-Monteure (L31) | Klima_MiniMonteure_HUD_Stimme4.mp4 |
| Klima Miniatur Schritte (L32) | Klima_Miniatur_Schritte_Stimme4.mp4 |
| Wärmepumpe Viessmann Split (L33) | Waermepumpe_Viessmann_Split_Stimme4.mp4 |
| Klima Gesicht spricht (L34) | Klima_Gesicht_spricht_Comic_Stimme4.mp4 |
| Bad Armatur Röntgenblick (L35) | Bad_Armatur_Roentgenblick_Stimme4.mp4 |
| Bad Regendusche (L36) | Bad_Regendusche_von_innen_Stimme4.mp4 |
| Ölkessel raus (L25) | Oelkessel_Raus_damit_L25_Stimme4.mp4 (geplant Di 13.10. 17:30) |
| E3DC eigene Anlage (L26) | E3DC_eigene_Anlage_L26_Stimme4.mp4 (geplant Sa 10.10. 17:30) |

## Nachbearbeitung jeder Zeile (Pflicht, seit 09.10.2026 abends)
- Patrick: "Stimme stockt, Ton nach dem Sprechen". Ursache: Chatterbox erzeugt Pausen bis 1,3 s und ein leises Rauschen/Pfeifen nach dem letzten Wort; loudnorm hat es hörbar gemacht.
- clean2.py: Sprache per Pegel erkennen, direkt nach dem letzten Wort hart schneiden + 80 ms ausblenden, Pausen > 0,25 s auf 0,22 s kürzen, kurze Geräusch-Fetzen nach langer Pause verwerfen, feste Lautstärke statt loudnorm.
- Stimmkette ohne loudnorm: Hochpass, EQ, sanfter Kompressor, +10 dB. Ergebnis ca. -16 LUFS.
- Kontrolle: Sprachspur allein messen, zwischen den Sätzen muss echte Stille sein.

## Wasserzeichen in fremden Clips
- Instagram-Name wandert am Clip-Ende (ca. ab Bild 280 von 300) nach unten links oder als großes Logo in die Bildmitte. Fremde Clips deshalb immer vor diesem Punkt einfrieren/abschneiden und jedes Video am Ende Bild für Bild prüfen.
