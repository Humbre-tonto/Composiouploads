import sys, os, math, pickle
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from da_lib import *
from piper_voice import say as piper_say
sys.path.insert(0, "/home/claude/months")
from month6_content import FACT_OR_FAKE, QUIZZES, WYR

QUIZ_FLAT=QUIZZES
WYR_FLAT=WYR

def build_audio_voiced(ve, se, total, music_gain=0.35):
    n=int(total*SR); voice=np.zeros(n+SR,np.float32)
    for a,at in ve:
        i=int(at*SR); voice[i:i+len(a)]+=a
    for s,at in se:
        i=int(at*SR); voice[i:i+len(s)]+=s
    v=np.nan_to_num(voice[:n]); pk=float(np.max(np.abs(v)))
    if pk>0: v=(v/pk)*0.85
    mus=music(total)*music_gain
    import soundfile as sf
    sf.write(f"{DIR}/_voice.wav",v,SR); sf.write(f"{DIR}/_music.wav",mus,SR)

def build_factorfake(statement,is_fact,explanation):
    va=piper_say(f"Fact or fake? {statement}")
    se=[(whoosh(),0.2)]; q_start=0.4
    think=q_start+len(va)/SR+0.3; reveal=think+3.0
    verdict="Fact!" if is_fact else "Fake!"
    va_ans=piper_say(f"{verdict} {explanation}")
    end=reveal+max(len(va_ans)/SR+0.6,4.0)
    for k in range(3): se.append((tick(),think+k))
    se.append((correct(),reveal))
    return [(va,q_start),(va_ans,reveal+0.15)], se, dict(statement=statement,is_fact=is_fact,explanation=explanation,q_start=q_start,think=think,reveal=reveal,end=end)

def build_quiz(q,opts,ci):
    va=piper_say(q); se=[(pop(),0.3)]; q_start=0.4
    think=q_start+len(va)/SR+0.4; reveal=think+3.0
    va_ans=piper_say(f"It's {opts[ci]}.")
    end=reveal+max(len(va_ans)/SR+0.6,3.5)
    for k in range(3): se.append((tick(),think+k))
    se.append((correct(),reveal))
    item=dict(q=q,opts=opts,ci=ci,q_start=q_start,think=think,reveal=reveal,end=end)
    return [(va,q_start),(va_ans,reveal+0.15)], se, dict(intro_end=0.0,items=[item],cta_start=end), end+1.5

def build_wyr(a,b):
    va=piper_say(f"Would you rather {a.replace(chr(10),' ')}, or {b.replace(chr(10),' ')}?")
    se=[(whoosh(),0.2)]; start=0.3
    t_start=start+len(va)/SR+0.3; end=t_start+2.5
    for k in range(2): se.append((tick(),t_start+k))
    se.append((ding(),t_start+2))
    return [(va,start)], se, [dict(a=a,b=b,start=start,t_start=t_start,end=end)], end, end+3.5

A_TOP=((196,52,52),(150,26,44)); B_BOT=((36,110,190),(18,52,120))

def r_factorfake(m):
    def f(t):
        img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img,"RGBA")
        rev=t>=m["reveal"]; is_fact=m["is_fact"]
        if rev: band(d,0,0,W,H,(8,40,22),(12,70,40)) if is_fact else band(d,0,0,W,H,(50,14,14),(80,20,20))
        else: band(d,0,0,W,H,(20,16,44),(44,22,74))
        brand(d)
        d.rounded_rectangle([W//2-320,150,W//2+320,232],40,fill=(255,220,70)); center(d,"FACT OR FAKE?",W//2,164,fc(48),(30,20,10))
        block(d,m["statement"],W//2,470,fit(d,m["statement"],W-160,74),(255,255,255),sw=4)
        py=800; pw=430; ph=140; fact_x=W//2-pw-20; fake_x=W//2+20
        fact_fill=(60,220,130) if (rev and is_fact) else (255,255,255,26)
        fake_fill=(230,70,70) if (rev and not is_fact) else (255,255,255,26)
        d.rounded_rectangle([fact_x,py,fact_x+pw,py+ph],26,fill=fact_fill)
        d.rounded_rectangle([fake_x,py,fake_x+pw,py+ph],26,fill=fake_fill)
        fc_col=(15,40,25) if (rev and is_fact) else (255,255,255)
        kc_col=(40,15,15) if (rev and not is_fact) else (255,255,255)
        center(d,"FACT",fact_x+pw//2,py+38,fc(64),fc_col,sw=0 if(rev and is_fact) else 3)
        center(d,"FAKE",fake_x+pw//2,py+38,fc(64),kc_col,sw=0 if(rev and not is_fact) else 3)
        cx,cy,r=W//2,1120,110
        if not rev and t>=m["think"]:
            fr=(t-m["think"])/3
            d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(255,255,255)); d.arc([cx-r+8,cy-r+8,cx+r-8,cy+r-8],-90,-90+360*(1-fr),fill=(230,120,60),width=15)
            center(d,str(max(1,int(math.ceil(3-(t-m['think']))))),cx,cy-50,fc(94),(30,30,40))
        elif not rev: center(d,"?",cx,cy-60,fc(100),(255,255,255),sw=4)
        if rev:
            fexp=fit(d,m["explanation"],W-180,42)
            block(d,m["explanation"],W//2,1330,fexp,(255,255,255),sw=3,gap=6)
            crosspromo(d)
        return img
    return f

def r_quiz(M):
    TIMER=3
    def f(t):
        img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img,"RGBA")
        band(d,0,0,W,H,(18,20,54),(40,26,86)); brand(d)
        if t>=M["cta_start"]:
            center(d,"YOUR SCORE?",W//2,720,fc(150),(255,220,70)); center(d,"Comment below 👇",W//2,900,fb(58),(255,255,255))
            crosspromo(d); return img
        it=M["items"][0]; rev=t>=it["reveal"]
        d.rounded_rectangle([W//2-140,150,W//2+140,226],36,fill=(255,220,70)); center(d,"QUIZ",W//2,162,fc(48),(30,20,10))
        block(d,it["q"],W//2,430,fit(d,it["q"],W-160,84),(255,255,255),sw=4)
        oy=760; ow=W-160; ox=80
        for k,opt in enumerate(it["opts"]):
            yy=oy+k*175
            fillc=(60,220,130) if (rev and k==it["ci"]) else (255,255,255,18 if rev else 28)
            d.rounded_rectangle([ox,yy,ox+ow,yy+150],24,fill=fillc)
            d.ellipse([ox+26,yy+35,ox+106,yy+115],fill=(255,220,70)); center(d,chr(65+k),ox+66,yy+52,fc(64),(30,20,10))
            tc=(20,40,28) if (rev and k==it["ci"]) else (255,255,255)
            d.text((ox+150,yy+40),opt,font=fit(d,opt,ow-220,72),fill=tc,stroke_width=4 if not(rev and k==it["ci"]) else 0,stroke_fill=(0,0,0))
        cx,cy,r=W//2,1560,86
        if not rev and t>=it["think"]:
            fr=(t-it["think"])/TIMER
            d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(255,255,255)); d.arc([cx-r+6,cy-r+6,cx+r-6,cy+r-6],-90,-90+360*(1-fr),fill=(230,120,60),width=12)
            center(d,str(max(1,int(math.ceil(TIMER-(t-it['think']))))),cx,cy-44,fc(80),(30,30,40))
        return img
    return f

def r_wyr(meta,ostart):
    MID=H//2
    def f(t):
        img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img,"RGBA")
        cur=next((m for m in meta if t<m["end"]),None)
        if t<meta[0]["start"]:
            band(d,0,0,W,H,(28,14,54),(64,18,92)); brand(d)
            center(d,"WOULD YOU",W//2,700,fc(150),(255,255,255)); center(d,"RATHER?",W//2,860,fc(180),(255,220,70))
        elif t>=ostart:
            band(d,0,0,W,H,(28,14,54),(64,18,92)); brand(d)
            center(d,"A or B?",W//2,660,fc(170),(255,255,255)); center(d,"Comment your pick",W//2,860,fb(58),(255,220,70))
            crosspromo(d)
        else:
            sl=eout((t-cur["start"])/0.4); ax=int((1-sl)*-W); bx=int((1-sl)*W)
            top=Image.new("RGB",(W,MID)); dt=ImageDraw.Draw(top); band(dt,0,0,W,MID,*A_TOP)
            bot=Image.new("RGB",(W,H-MID)); db=ImageDraw.Draw(bot); band(db,0,0,W,H-MID,*B_BOT)
            img.paste(top,(ax,0)); img.paste(bot,(bx,MID)); d=ImageDraw.Draw(img,"RGBA")
            fA=fit(d,cur["a"],W-160,116); fB=fit(d,cur["b"],W-160,116)
            block(d,cur["a"],W//2+ax,MID//2,fA,(255,255,255),sw=4)
            block(d,cur["b"],W//2+bx,MID+(H-MID)//2,fB,(255,255,255),sw=4)
            center(d,"A",110,60,fc(84),(255,255,255),sw=4); center(d,"B",110,MID+30,fc(84),(255,255,255),sw=4)
            d.rounded_rectangle([W//2-290,16,W//2+290,92],38,fill=(255,220,70)); center(d,"WOULD YOU RATHER",W//2,30,fc(52),(30,20,10))
            cx,cy,r=W//2,MID,116; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(255,255,255))
            if t<cur["t_start"]: center(d,"OR",cx,cy-48,fc(90),(30,30,40))
            else:
                fr=(t-cur["t_start"])/2.0
                d.arc([cx-r+8,cy-r+8,cx+r-8,cy+r-8],-90,-90+360*(1-fr),fill=(230,60,60),width=15)
                center(d,str(max(1,int(math.ceil(2-(t-cur['t_start']))))),cx,cy-54,fc(100),(30,30,40))
        return img
    return f

def gen_factorfake(idx,out):
    s,f,e=FACT_OR_FAKE[idx]; ve,se,m=build_factorfake(s,f,e); total=m["end"]
    build_audio_voiced(ve,se,total); encode(r_factorfake(m),total,out); return total
def gen_quiz(idx,out):
    q,opts,ci=QUIZ_FLAT[idx]; ve,se,M,total=build_quiz(q,opts,ci)
    build_audio_voiced(ve,se,total); encode(r_quiz(M),total,out); return total
def gen_wyr(idx,out):
    a,b=WYR_FLAT[idx]; ve,se,meta,ost,total=build_wyr(a,b)
    build_audio_voiced(ve,se,total); encode(r_wyr(meta,ost),total,out); return total

OUTDIR="/mnt/user-data/outputs/month6"
os.makedirs(OUTDIR,exist_ok=True)
def make_day(day):
    idx=day-1; res=[]
    for typ,gen in [("fof",gen_factorfake),("quiz",gen_quiz),("wyr",gen_wyr)]:
        out=f"{OUTDIR}/m6_d{day:02d}_{typ}.mp4"
        if os.path.exists(out): res.append((out,"exists")); continue
        tot=gen(idx,out); res.append((out,round(tot,1)))
    return res

if __name__=="__main__":
    a=int(sys.argv[1]); b=int(sys.argv[2]) if len(sys.argv)>2 else a
    for day in range(a,b+1):
        for out,tot in make_day(day):
            print(f"d{day:02d}", os.path.basename(out), tot)
