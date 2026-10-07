import subprocess
SFX = '/root/gh_hyperframes/skills/media-use/audio/assets/sfx/'
SH = 24.0
vo = [('vo/t1.wav', 0.3), ('va/t1.wav', 3.3), ('va/t2.wav', 8.3), ('va/t3.wav', 13.7), ('va/t4.wav', 17.3), ('va/t5.wav', 22.45), ('va/t6.wav', 29.6), ('va/t7.wav', 33.0)]
vo += [(f'vo/t{i}.wav', s + SH) for i, s in [(5, 18.3), (6, 22.0), (7, 27.2), (8, 31.3), (9, 33.6), (10, 39.6), (11, 46.3)]]
fx = []
for c in [2.85, 13.45, 22.05, 29.35]: fx.append(('whoosh-short', c, 0.45, None))
for c in [30.85, 45.85]: fx.append(('whoosh', c + SH, 0.5, None))
fx += [('impact-bass-1', 0.15, 0.7, None), ('impact-bass-1', 42.0, 0.85, None), ('riser', 40.0, 0.35, 2.0), ('impact-bass-2', 33.1, 0.6, None), ('whoosh-short', 32.85, 0.45, None), ('sparkle', 39.2, 0.5, None), ('pop', 37.0, 0.5, None), ('ping', 11.0, 0.45, None)]
for s in [23.6, 25.5, 27.2]: fx.append(('pop', s, 0.55, None))
for s in [18.9, 22.3, 24.4, 27.4, 28.5, 29.7]: fx.append(('click', s + SH, 0.6, None))
for s in [33.7, 35.0, 36.4, 38.0, 39.6, 40.4]: fx.append(('click-soft', s + SH, 0.7, None))
fx += [('sparkle', 29.9, 0.5, None), ('pop', 31.1, 0.5, None), ('sparkle', 43.5 + SH, 0.5, None), ('chime', 46.9 + SH, 0.45, None),
       ('whoosh-short', 2.35, 0.4, None)]
inp = ['-i', 'video.mp4', '-i', 'music.wav']
for fpath, _ in vo: inp += ['-i', fpath]
for n, *_ in fx: inp += ['-i', SFX + n + '.mp3']
fl = []; vl = []
for k, (_f, s) in enumerate(vo):
    fl.append(f'[{2+k}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(s*1000)}[v{k}]'); vl.append(f'[v{k}]')
fl.append(''.join(vl) + f'amix=inputs={len(vl)}:normalize=0,apad=whole_dur=74,highpass=f=90,acompressor=threshold=0.1:ratio=3:attack=5:release=80,equalizer=f=3000:t=q:w=1:g=3,volume=1.6,asplit=2[voice][sc]')
fl.append('[1:a]volume=0.5[mus]')
fl.append('[mus][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck]')
sl = []
for k, (n, s, g, d) in enumerate(fx):
    j = 2 + len(vo) + k; tr = f'atrim=0:{d},afade=t=out:st={d-0.3:.2f}:d=0.3,' if d else ''
    fl.append(f'[{j}:a]aresample=48000,aformat=channel_layouts=mono,{tr}volume={g},adelay={int(s*1000)}[s{k}]'); sl.append(f'[s{k}]')
fl.append(''.join(sl) + f'amix=inputs={len(sl)}:normalize=0[sfx]')
fl.append('[voice][duck][sfx]amix=inputs=3:normalize=0,atrim=0:74,afade=t=out:st=73.5:d=0.5,loudnorm=I=-14:TP=-1.5,volume=1.5dB,alimiter=limit=0.84:level=false,aresample=48000[a]')
L = 'Mair_Projektmappe_lang_WhatsApp.mp4'
cmd = ['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
       '-maxrate', '10M', '-bufsize', '20M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-movflags', '+faststart', L]
r = subprocess.run(cmd, capture_output=True, text=True); print('long', r.returncode, r.stderr[-300:])
for name, a, b in [('Mair_Reel_1_Was_kostet_deine_Heizung', 0, 42), ('Mair_Reel_2_So_laeuft_es_ab', 42.22, 55), ('Mair_Reel_3_Foerderantrag', 55, 70)]:
    f = (f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v1];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={b-a-0.15:.2f}:d=0.15[a1];'
         f'[0:v]trim=70:74,setpts=PTS-STARTPTS[v2];[0:a]atrim=70:74,asetpts=PTS-STARTPTS,afade=t=in:d=0.1,afade=t=out:st=3.6:d=0.4[a2];'
         f'[v1][a1][v2][a2]concat=n=2:v=1:a=1[v][a]')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', L, '-filter_complex', f, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', name + '.mp4']
    r = subprocess.run(cmd, capture_output=True, text=True); print(name, r.returncode, r.stderr[-300:])
