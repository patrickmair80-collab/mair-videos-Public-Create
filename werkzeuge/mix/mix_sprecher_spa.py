import subprocess
SFX='/root/gh_hyperframes/skills/media-use/audio/assets/sfx/'
B=60/118; HB=2*B
AT=[3*HB+i*HB for i in range(0,6)]; ACARD=AT[-1]+HB; AEND=ACARD+3*HB; DUR=15.8
fx=[('chime',0.05,0.35),('chime',AEND,0.35),('sparkle',AEND+1.6,0.35)]+[('whoosh-short',c-0.12,0.3) for c in AT]
vo=[('vo/v1.wav',0.35),('vo/v2.wav',ACARD+0.15),('vo/v4.wav',AEND+0.25)]
def build(with_voice,out):
    inp=['-i','A.mp4','-i','musicA2.wav']; fl=[]
    for f,_ in vo: inp+=['-i',f]
    for n,*_ in fx: inp+=['-i',SFX+n+'.mp3']
    o=2+len(vo); vl=[]
    for i,(f,s) in enumerate(vo):
        fl.append(f'[{2+i}:a]aresample=48000,aformat=channel_layouts=mono,highpass=f=90,acompressor=threshold=0.1:ratio=3:attack=5:release=80,equalizer=f=3000:t=q:w=1:g=3,adelay={int(s*1000)}[v{i}]');vl.append(f'[v{i}]')
    fl.append(''.join(vl)+f'amix=inputs={len(vl)}:normalize=0,volume=1.7,apad=whole_dur={DUR},asplit=2[voice][sc]')
    fl.append('[1:a]aresample=48000,volume=0.9[mus0]')
    fl.append('[mus0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=400[mus]' if with_voice else '[mus0]anull[mus];[sc]anullsink')
    sl=[]
    for i,(n,s,g) in enumerate(fx):
        fl.append(f'[{o+i}:a]aresample=48000,aformat=channel_layouts=mono,volume={g},adelay={int(s*1000)}[s{i}]');sl.append(f'[s{i}]')
    fl.append(''.join(sl)+f'amix=inputs={len(sl)}:normalize=0[sfx]')
    if with_voice: fl.append(f'[voice][mus][sfx]amix=inputs=3:normalize=0,atrim=0:{DUR},afade=t=out:st={DUR-0.4:.2f}:d=0.4,loudnorm=I=-14:TP=-1.5,aresample=48000[a]')
    else: fl.append(f'[mus][sfx]amix=inputs=2:normalize=0,atrim=0:{DUR},afade=t=out:st={DUR-0.4:.2f}:d=0.4,loudnorm=I=-14:TP=-1.5,aresample=48000[a];[voice]anullsink')
    cmd=['ffmpeg','-nostdin','-v','error','-y']+inp+['-filter_complex',';'.join(fl),'-map','0:v','-map','[a]','-c:v','libx264','-preset','medium','-crf','22','-maxrate','8M','-bufsize','16M','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ac','2','-movflags','+faststart',out]
    r=subprocess.run(cmd,capture_output=True,text=True);print(out,r.returncode,r.stderr[-300:])
build(True,'Mair_Reel_Bad_eigener_Fliesenleger.mp4'); build(False,'Mair_Reel_Bad_eigener_Fliesenleger_nur_Musik.mp4')
