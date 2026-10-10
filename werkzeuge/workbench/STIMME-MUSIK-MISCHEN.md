# Stimme + Musik + Mischen im Composio-Workbench (Sandbox wird regelmäßig geleert)

1. Setup (jede neue Sandbox):
   pip install -q piper-tts faster-whisper
   curl -sSL -o de_DE-thorsten-high.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx (+ .onnx.json)
2. Pro Satz: python3 -m piper -m de_DE-thorsten-high.onnx --length-scale 1.1 -f sN.wav < satz.txt
   Stille vorn/hinten weg: areverse,silenceremove,areverse,silenceremove. Dauer messen -> in Layout-Datei D=[...]
3. Bildspur lokal rendern (werkzeuge/alt7/lNN_*.py), nach reels/alt7/ committen, im Workbench über raw.githubusercontent.com/<sha>/... holen.
4. Mischen: anullsrc-Basis (duration=first) + Stimmen per adelay, loudnorm I=-16 auf Stimme; SFX (Drive "6 Soundeffekte frei") volume 0.35;
   Musik (MUSIK.md, Openverse CC0, z. B. cdn.freesound.org/previews/...) volume 0.30, sidechaincompress auf Stimme, Fade in/out, alimiter limit=0.85:level=disabled.
5. Prüfen: freezedetect n=0.001 d=1.0 (kein Treffer), ebur128 -17..-14 LUFS, Spitze <= -1 dB, Whisper tiny (Audio als numpy übergeben) -> Text vollständig, maxgap <= 1.2 s.
   Standbild am Ende: ffmpeg scale=w='trunc(1080*(1+0.04*t/D)/2)*2':h=-2:eval=frame,crop=1080:1920
6. Upload: upload_local_file -> GOOGLEDRIVE_UPLOAD_FILE {file_to_upload:{name,mimetype,s3key}, folder_to_upload_to:<Reels-Ordner>}
7. Metricool: GOOGLEDRIVE_DOWNLOAD_FILE liefert s3url -> als media an createScheduledPost (Metricool kopiert die Datei).
Speicher knapp: nie mehrere große Modelle parallel, -threads 1.
