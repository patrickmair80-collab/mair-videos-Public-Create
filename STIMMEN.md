# Sprecherstimme: immer "Stimme 4" (Stand 09.10.2026)

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
