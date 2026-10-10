# Werkzeug-Kette Video (ohne Zusatzkosten zuerst)

Patrick (09.10.2026): Erst mal kein Geld investieren. Wenn Credits bei einem Programm leer sind, automatisch zum nächsten wechseln.
Stand: 09.10.2026. Gratis-Bedingungen ändern sich oft: vor jedem Einsatz die Preisseite prüfen.

## 1. Läuft heute schon kostenlos (eigene Engine im Composio-Workbench)
| Baustein | Werkzeug | Lizenz/Kosten |
|---|---|---|
| Stimme | edge-tts (Conrad, Katja) | gratis |
| Schnitt, Untertitel, Sound, Musik | Python + ffmpeg (eigene Engine, Layouts L21–L23) | gratis |
| Earth-Zoom auf Aurachtal/Herzogenaurach | NASA Blue Marble (gemeinfrei) + Luftbild Bayern DOP40 (CC BY 4.0, Quelle im Bild nennen) | gratis |
| Freistellen | Moda „Hintergrund entfernen“ (Moda-Credits, aktuell 500 frei) | im Plan enthalten |
| Bilder 3D-Figur | Figma generate_image | im Plan enthalten |
| Herstellerbilder | viessmann.de / novelan.com Produktbilder (Freigabe liegt vor). Keine AdobeStock-Motive von Herstellerseiten nehmen. | Freigabe |

## 2. Figur bewegen / Mund bewegen (Reihenfolge)
1. **PixVerse** (tägliche Gratis-Credits, hat Lip Sync). Prüfen: Wasserzeichen und kommerzielle Nutzung im Gratis-Tarif.
2. **Kling AI** (tägliche Gratis-Credits, Bild-zu-Video „läuft auf die Kamera zu“). Gleiche Prüfung.
3. **Hedra** (Gratis-Tarif, Bild + Audio = sprechende Figur). Laut Drittquelle gratis nicht kommerziell.
4. **MuseTalk 1.5** (Open Source, MIT, kommerziell erlaubt, kostenloser Hugging-Face-Space). Braucht ein Video als Basis, Gesicht 256 px. Test mit Comic-Patrick offen.
5. **Wan 2.2 TI2V-5B** (Apache 2.0, kommerziell erlaubt, Hugging-Face-Space) für stumme Bewegungsclips.
6. **ElevenLabs** (MiniMax H3 Max Lip Sync, OmniHuman 1.5) und **vidIQ** (Kling, Veo, Seedance): erst wenn wieder Credits da sind (vidIQ: 150 neue am 26.10.).

Regel: Gratis-Ergebnis mit Wasserzeichen oder ohne kommerzielle Freigabe wird NICHT gepostet.

## 3. Was Patrick einbinden kann (Konto anlegen, dann verbinde ich es)
- PixVerse und Kling: Konto anlegen (gratis), dann teste ich die Comic-Figur.
- Hugging Face: gratis Konto + Token, damit MuseTalk/Wan-Spaces zuverlässiger laufen.
- Remotion: für Firmen bis 3 Mitarbeiter gratis, falls wir später auf React-Videos umsteigen.

## 4. Earth-Zoom (neu, L23-Opener)
- Globus dreht sich → Europa → Franken → Aurachtal, Pin „Mair Gebäudetechnik“.
- Kundenbaustellen nur bis auf Ortsebene zoomen (Ortsmitte), nie auf das Haus: keine Adresse erkennbar.
- Quelle unten im Bild: „Luftbild © Bayerische Vermessungsverwaltung (CC BY 4.0) · NASA Blue Marble“.

## Stand 10.10.2026: neue Bausteine
- Google-Unternehmensprofil (Metricool "gmb", Typ photo/Video) bei allen Reels bis 30 s mit dabei: lokale Sichtbarkeit in Google Maps/Suche.
- B-Roll frei nutzbar: Pixabay (API-Schlüssel von Patrick, Lizenz frei kommerziell), Drive Reels/"7 B-Roll frei nutzbar (Pixabay)". Keine Clips mit Personen/fremden Marken.
- Soundeffekte CC0 (Freesound via Openverse): Drive Reels/"6 Soundeffekte frei (CC0)" – Stempel, Schreibmaschine, Papier, Kamera, Tropfen, Wind, Feuer, Klick, Swipe, Pop.
- Instagram-Analyse über Composio-Instagram (Business-Konto, 35 Follower Stand 10.10.): Reichweite ist der Engpass, nicht die Produktion.
- Instagram Edits (gratis, Handy): für Patricks eigene Baustellen-Clips, automatische Untertitel, Export ohne Wasserzeichen, Insights der letzten 10 Reels.
- Probeweise Trial-Reels (Metricool instagramData.type TRIAL_REEL) für Hook-Tests bei Nicht-Followern.

## Große Dateien ins Google Drive (seit 10.10.2026)
Datei ins Repo committen und pushen, dann im Composio-Workbench per raw.githubusercontent.com laden, mit upload_local_file + GOOGLEDRIVE_UPLOAD_FILE in den Ordner legen. Metricool nimmt raw.githubusercontent.com-Links direkt als Medien.
Drive-Ordner: Werbeplakate 1G-dnbcMa5J70STB4mAimanYA_hXM4VJO, Reels/Karussells 13sIx9_3yTFB6lF6IIYP5AYnoqdqDj2h6.
