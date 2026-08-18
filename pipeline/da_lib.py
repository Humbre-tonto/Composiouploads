import os, math, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

DIR=os.path.dirname(os.path.abspath(__file__))
W,H,FPS,SR = 1080,1920,24,24000
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FC="/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
def fb(s): return ImageFont.truetype(FB,s)
def fc(s): return ImageFont.truetype(FC,s)

def tone(fr,dur,vol=0.5,dec=6.0):
    t=np.arange(int(dur*SR))/SR
    return (np.sin(2*np.pi*fr*t)*np.exp(-dec*t)*vol).astype(np.float32)
def tick(): return tone(1150,0.08,0.5,30)
def ding():
    n=int(0.5*SR); o=np.zeros(n,np.float32)
    for fq,v,dl in [(660,0.4,0),(990,0.3,0),(1320,0.25,0.05)]:
        w=tone(fq,0.5-dl,v,5); i=int(dl*SR); o[i:i+len(w)]+=w[:n-i]
    return o
def correct():
    n=int(0.6*SR); o=np.zeros(n,np.float32)
    for fq,dl in [(523,0),(659,0.08),(784,0.16),(1046,0.24)]:
        w=tone(fq,0.4,0.35,6); i=int(dl*SR); o[i:i+len(w)]+=w[:n-i]
    return o
def whoosh():
    n=int(0.28*SR); return (np.random.randn(n)*np.linspace(0.3,0,n)).astype(np.float32)
def pop(): return tone(760,0.12,0.4,22)
NOTE={n:440*2**((i-9)/12) for i,n in enumerate(["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"])}
def nf(n,o): return NOTE[n]*2**(o-4)
def music(total,bpm=126):
    beat=60/bpm; prog=[("A",["A","C","E"]),("F",["F","A","C"]),("C",["C","E","G"]),("G",["G","B","D"])]
    n=int(total*SR)+SR; mix=np.zeros(n,np.float32); tp=0.0; bar=0
    while tp<total:
        root,tri=prog[bar%4]
        for b in range(8):
            at=int((tp+b*beat/2)*SR)
            if at>=n: break
            w=tone(nf(root,2),beat*0.45,0.5,8) if b%2==0 else sum(tone(nf(x,4),beat*0.3,0.09,12) for x in tri)
            e=min(at+len(w),n); mix[at:e]+=w[:e-at]
        tp+=4*beat; bar+=1
    return (np.tanh(mix*1.3)*0.8)[:int(total*SR)]

def build_audio_voiced(voice_events, sfx_events, total, music_gain=0.35):
    n=int(total*SR); voice=np.zeros(n+SR,np.float32)
    for a,at in voice_events:
        i=int(at*SR); voice[i:i+len(a)]+=a
    for s,at in sfx_events:
        i=int(at*SR); voice[i:i+len(s)]+=s
    v=np.nan_to_num(voice[:n]); pk=float(np.max(np.abs(v)))
    if pk>0: v=(v/pk)*0.85
    mus=music(total)*music_gain
    sf.write(f"{DIR}/_voice.wav",v,SR); sf.write(f"{DIR}/_music.wav",mus,SR)

def wrap(d,text,fnt,maxw):
    out=[]
    for para in text.split("\n"):
        words=para.split(); ln=""
        for w_ in words:
            tr=(ln+" "+w_).strip()
            if d.textbbox((0,0),tr,font=fnt)[2]<=maxw: ln=tr
            else:
                if ln: out.append(ln)
                ln=w_
        out.append(ln)
    return out
def fit(d,text,maxw,size,minsize=36):
    while size>minsize:
        f=fc(size)
        if all(d.textbbox((0,0),l,font=f)[2]<=maxw for l in wrap(d,text,f,maxw)): return f
        size-=4
    return fc(minsize)
def center(d,txt,cx,y,f,fill,sw=0,sfill=(0,0,0)):
    w=d.textbbox((0,0),txt,font=f,stroke_width=sw)[2]
    d.text((cx-w/2,y),txt,font=f,fill=fill,stroke_width=sw,stroke_fill=sfill)
def block(d,text,cx,cy,f,fill,sw=4,gap=8):
    lines=wrap(d,text,f,W-160) if "\n" not in text else text.split("\n")
    tot=len(lines)*(f.size+gap); y=cy-tot/2
    for ln in lines: center(d,ln,cx,y,f,fill,sw); y+=f.size+gap
def band(d,x0,y0,x1,y1,c0,c1):
    h=max(y1-y0,1)
    for yy in range(y0,y1,6):
        r=(yy-y0)/h
        d.rectangle([x0,yy,x1,yy+6],fill=tuple(int(c0[i]+(c1[i]-c0[i])*r) for i in range(3)))
def eout(x): x=min(max(x,0),1); return 1-(1-x)**3
def brand(d):
    f=fb(30); txt="THE DAILY BRAINY"; w=d.textbbox((0,0),txt,font=f)[2]
    d.rounded_rectangle([28,26,28+w+40,84],28,fill=(0,0,0,120))
    d.text((48,40),txt,font=f,fill=(255,220,70))
def crosspromo(d):
    f=fb(30); txt="🎬 Full episode — link in description"
    w=d.textbbox((0,0),txt,font=f)[2]
    d.rounded_rectangle([W//2-w//2-24,H-58,W//2+w//2+24,H-10],22,fill=(0,0,0,140))
    center(d,txt,W//2,H-52,f,(255,255,255))
def encode(render_fn, total, out_path):
    NF=int(total*FPS)
    proc=subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}",
        "-r",str(FPS),"-i","-","-c:v","libx264","-preset","fast","-crf","20","-pix_fmt","yuv420p",
        f"{DIR}/_video.mp4"],stdin=subprocess.PIPE,stdout=open(f"{DIR}/_ff.log","w"),stderr=subprocess.STDOUT)
    for fi in range(NF):
        proc.stdin.write(render_fn(fi/FPS).tobytes())
    proc.stdin.close(); proc.wait()
    subprocess.run(["ffmpeg","-y","-i",f"{DIR}/_video.mp4","-i",f"{DIR}/_voice.wav","-i",f"{DIR}/_music.wav",
        "-filter_complex","[1:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9[a]",
        "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","176k","-shortest",out_path],
        stdout=open(f"{DIR}/_mux.log","w"),stderr=subprocess.STDOUT)
    return out_path

# ============ LONG-FORM EPISODES (for SEO cross-promo rotation) ============
# Add new episode video IDs here as they go live.
# Used by seo_meta.py (in studio/) to inject clickable links into Short descriptions.
LONG_FORM_EPISODES=[
    {"id":"-tem5EZbavM","title":"Movies & Series Trivia Ep. 1"},
    {"id":"vOUs4qeYOTs","title":"General Trivia Ep. 1"},
    {"id":"0PKYTSpiX8o","title":"Songs & Pop Culture Trivia Ep. 1"},
    {"id":"jsm3yWgv9mQ","title":"Disney & Pixar Trivia Ep. 1"},
]
