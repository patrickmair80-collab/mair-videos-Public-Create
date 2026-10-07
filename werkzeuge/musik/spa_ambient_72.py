import numpy as np, wave
from scipy.signal import lfilter
SR=48000; DUR=15.8; N=int(SR*DUR); t=np.arange(N)/SR; out=np.zeros(N)
mtof=lambda m:440*2**((m-69)/12)
BPM=72; B=60/BPM; BAR=4*B
chords=[[52,59,64,68,71],[48,55,64,67,71],[45,52,60,64,67],[47,54,59,63,66]]  # Emaj9, Cmaj7#11-ish, Am9, B
def lp(x,a): return lfilter([a],[1,-(1-a)],x)
for b in range(int(DUR/BAR)+1):
    s=int(b*BAR*SR); n=int(BAR*SR*1.4)
    if s>=N: break
    tt=np.arange(n)/SR; seg=np.zeros(n)
    for m in chords[b%4]:
        f=mtof(m); seg+=np.sin(2*np.pi*f*tt+0.3*np.sin(2*np.pi*0.2*tt))+0.3*np.sin(2*np.pi*2*f*tt)
    env=np.minimum(1,tt/1.2)*np.exp(-np.maximum(0,tt-BAR)/0.8)
    e=min(N,s+n); out[s:e]+=(seg*env)[:e-s]*0.06
# felt piano arpeggio
arp=[0,2,4,3,1,4,2,3]
for i,k in enumerate(np.arange(0.4,DUR-0.5,B/2)):
    c=chords[int(k/BAR)%4]; m=c[arp[i%8]%len(c)]+12; n=int(1.6*SR); tt=np.arange(n)/SR; f=mtof(m)
    sig=(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt)+0.08*np.sin(6*np.pi*f*tt))*np.exp(-tt*3.2)*np.minimum(1,tt/0.004)
    s=int(k*SR); e=min(N,s+n); out[s:e]+=lp(sig,0.25)[:e-s]*0.10
# soft water noise bed
nz=lp(np.random.default_rng(1).normal(0,1,N),0.02)*0.5; out+=nz*0.04
# soft low pulse after card (9.15)
for k in np.arange(9.15,DUR-0.3,B):
    n=int(0.5*SR); tt=np.arange(n)/SR; s=int(k*SR); e=min(N,s+n)
    out[s:e]+=(np.sin(2*np.pi*(45+40*np.exp(-tt*20))*tt)*np.exp(-tt*6))[:e-s]*0.25
# reverb-ish
d=int(0.11*SR); rv=np.zeros(N)
for j,g in enumerate([0.35,0.22,0.14,0.08]): rv[d*(j+1):]+=out[:N-d*(j+1)]*g
out=out+lp(rv,0.15)
out*=np.clip((DUR-t)/0.5,0,1)*np.clip(t/0.3,0,1); out/=np.max(np.abs(out))+1e-9; out*=0.85
w=wave.open('musicA2.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype(np.int16).tobytes());w.close();print('ok')
