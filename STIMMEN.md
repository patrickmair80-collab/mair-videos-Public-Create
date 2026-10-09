# Stimmen für Mair-Videos (Stand 09.10.2026)

**Entscheidung Patrick (09.10.2026): Stimme 4 = Männerstimme natürlich (Chatterbox, Klangvorlage Florian) ist Standard für Comic-Patrick und Sprecher.** Ersatz, wenn Chatterbox nicht erreichbar: Florian Multilingual (Nr. 3) mit Nachbearbeitung. Frauenstimme: noch offen, bis dahin Nr. 8 / Nr. 7.

Hinweis: Das kostenlose Hugging-Face-Kontingent war am 09.10. nach wenigen Durchläufen aufgebraucht. Mit kostenlosem HF-Konto + Token (Patrick) gibt es mehr Kontingent. Klangvorlagen liegen im Workbench unter /mnt/files/engines/ref_florian.wav und ref_seraphina.wav.

Ziel (Patrick): Stimme soll nicht nach KI klingen, geschmeidig, Abwechslung Mann/Frau.

## Kostenlose Optionen
| Nr. | Stimme | Werkzeug | Hinweis |
|---|---|---|---|
| 1 | Conrad (Mann, bisher) | edge-tts | klingt am ehesten nach Ansage |
| 2 | Killian (Mann) | edge-tts | |
| 3 | Florian Multilingual (Mann) | edge-tts | neuere, natürlichere Stimme |
| 4 | Mann natürlich | Chatterbox Multilingual (Resemble AI, MIT-Lizenz, kostenloser Hugging-Face-Space) mit Florian als Klangvorlage | natürlichere Betonung |
| 5 | Katja (Frau, bisher Kundin) | edge-tts | |
| 6 | Amala (Frau) | edge-tts | |
| 7 | Seraphina Multilingual (Frau) | edge-tts | neuere, natürlichere Stimme |
| 8 | Frau natürlich | Chatterbox mit Seraphina als Klangvorlage | |

Testdatei: Drive „3D-Maskottchen Comic-Patrick“ → Mair_Stimmen_Test_8_Stimmen.mp4. Patrick wählt nach Gehör.

## Nachbearbeitung (immer)
ffmpeg-Kette: Trittschall raus (80 Hz), weniger Dröhnen (250 Hz −2 dB), mehr Präsenz (3,5 kHz +2 dB), De-Esser, sanfter Kompressor, kleiner Raumklang, Lautheit −16 LUFS (Endmix −14).

## Beste Lösung: Patricks eigene Stimme
Chatterbox kann aus 10–20 s Sprachaufnahme die Stimme nachbilden. Nur mit Patricks Zustimmung und nur seine eigene Stimme (keine fremden Personen). Aufnahme: ruhiger Raum, Handy 20 cm vom Mund, normal sprechen.

## Abwechslung
- Comic-Patrick spricht mit Männerstimme (fest, wiedererkennbar).
- Kundin/Kunde, Erklär-Stimme oder Sprecherin im Wechsel mit Frauenstimme.
- Nie zweimal hintereinander dieselbe Sprecher-Kombination in Reels.

## Grenzen
- Hugging-Face-Gratiskontingent (GPU-Minuten pro Tag) ist begrenzt. Mit kostenlosem HF-Konto + Token mehr Kontingent.
- ElevenLabs/vidIQ-Stimmen nur mit Credits.
