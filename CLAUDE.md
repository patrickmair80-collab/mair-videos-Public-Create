# Mair Gebäudetechnik – feste Regeln für jede Sitzung

Dieses Repo gehört Patrick Mair (Mair Gebäudetechnik, Dorfäcker 1a, 91086 Aurachtal). Die Regeln hier gelten automatisch in jeder Sitzung, auch für die geplanten Agenten. Sie ersetzen den Mod `werkzeuge/mods/mair-regeln`, solange der nicht geladen ist.

## Antworten
- Deutsch, kurz, ADHS-freundlich: Abschnitte, fett, am Ende Next Steps.
- Stop-Slop: menschlich, keine KI-Floskeln, wenige Gedankenstriche.
- Rückfragen nur bei Geld, Senden/Posten an Fremde, Kundendaten, Herstellerbildern. Sonst selbst machen, Fehler selbst nachprüfen und beheben.

## Caption-Prüfer (Pflicht vor JEDEM Metricool-Post oder -Update)
Vor createScheduledPost / updateScheduledPost die Caption prüfen. Erst senden, wenn alles stimmt:
1. Ort im ersten Satz (Aurachtal, Herzogenaurach, Erlangen, Höchstadt, …).
2. Genau 5 Hashtags, davon mindestens 2 Orte.
3. Zeile „Anfrage in 1 Minute: Link in der Bio“ ist drin.
4. Nie „nur noch X Termine“. Stattdessen z. B. „Für diese Heizsaison sind noch Kapazitäten frei.“
5. Zahlen nur mit Quelle, Gesetze/Förderung mit Stand-Datum.
Ausnahme: reine Stories ohne Text.
Die Prüffunktion steht in `werkzeuge/mods/mair-regeln/hooks/register.ts` (`pruefeCaption`).

## Lösch-Warnung
- Kein `git push --force`, kein `rm -rf` auf das Repo, `~` oder `/`.
- Im Drive alte Versionen nur ersetzen, wenn die neue sicher hochgeladen ist.

## Videos
- Immer Thorsten-Stimme (Piper de_DE-thorsten-high, length-scale 1.1), nie stumm.
- Nie gleiches Layout oder gleiche Musik zweimal (LAYOUT-LOG.md, MUSIK.md). Keine Standbilder über 1 s.
- Keine Kundennamen, keine fremden Gesichter oder Marken außer freigegebenen Herstellern (Viessmann, Novelan, hansgrohe, Samsung, E3/DC).
- Nie fremde Beiträge umlabeln (z. B. Mitbewerber). Nur Thema und Format übernehmen.

## Posting-Rhythmus
- Mo–Fr 10:00, optional 17:30 (mind. 6 h Abstand). Wochenende max. 1 Post.
- Klima-Mittwoch 17:30, Mythos Wärmepumpe Freitag 10:00, 1 Wisch-Karussell pro Woche (plus Reel-Version für TikTok/YouTube im gleichen Slot).

## Dateien
- Drive-Namen: `Mair_<Thema>_<Ort>_<JJJJ-MM-TT>`, keine Umlaute.
- Große Dateien ins Drive: ins Repo committen, im Composio-Workbench über raw.githubusercontent.com holen und hochladen (WERKZEUG-KETTE.md).
- Was gut ankommt: WAS-WIRKT.md. Neue Werkzeuge: SKILL-RADAR.md.
