import subprocess
SFX='/root/gh_hyperframes/skills/media-use/audio/assets/sfx/'
VO=[0.25,4.75,8.75,12.95,18.15,22.5,26.3,30.3]
vo=[(f'vo/t{i}.wav',s) for i,s in enumerate(VO)]
fx=[('impact-bass-1',0.2,0.75,None),('impact-bass-1',3.0,0.8,None),('riser',24.0,0.4,2.0),('impact-bass-2',26.0,0.85,None),('whoosh',29.85,0.5,None),('chime',31.2,0.45,None),('sparkle',26.9,0.45,None)]
for c in [4.45,8.45,12.65,17.85,22.25]: fx.append(('whoosh-short',c,0.5,None))
for a in [4.6,8.6,12.8,18.0,22.4]:
    for k in range(3): fx.append(('pop',a+0.9+k*0.35,0.45,None))
inp=['-i','video.mp4','-i','music.wav']
for f,_ in vo: inp+=['-i',f]
for n,*_ in fx: inp+=['-i',SFX+n+'.mp3']
fl=[];vl=[]
for k,(_,s) in enumerate(vo):
    fl.append(f'[{2+k}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(s*1000)}[v{k}]'); vl.append(f'[v{k}]')
fl.append(''.join(vl)+f'amix=inputs={len(vl)}:normalize=0,apad=whole_dur=34,highpass=f=90,acompressor=threshold=0.1:ratio=3:attack=5:release=80,equalizer=f=3000:t=q:w=1:g=3,volume=1.6,asplit=2[voice][sc]')
fl.append('[1:a]volume=0.45[mus]')
fl.append('[mus][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck]')
sl=[]
for k,(n,s,g,d) in enumerate(fx):
    j=2+len(vo)+k; tr=f'atrim=0:{d},afade=t=out:st={d-0.3:.2f}:d=0.3,' if d else ''
    fl.append(f'[{j}:a]aresample=48000,aformat=channel_layouts=mono,{tr}volume={g},adelay={int(s*1000)}[s{k}]'); sl.append(f'[s{k}]')
fl.append(''.join(sl)+f'amix=inputs={len(sl)}:normalize=0[sfx]')
fl.append('[voice][duck][sfx]amix=inputs=3:normalize=0,atrim=0:34,afade=t=out:st=33.5:d=0.5,loudnorm=I=-14:TP=-1.5,aresample=48000[a]')
cmd=['ffmpeg','-nostdin','-y','-loglevel','error']+inp+['-filter_complex',';'.join(fl),'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','Mair_Reel_So_planen_wir_ein_Heizungsprojekt.mp4']
subprocess.run(cmd,check=True)
# TikTok version music only
subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i','video.mp4','-i','music.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','Mair_Reel_Heizungsprojekt_nur_Musik_TikTok.mp4'],check=True)
print('mix ok')
