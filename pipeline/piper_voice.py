import os, subprocess, urllib.request
import numpy as np
import soundfile as sf

VOICE_DIR="/home/claude/studio2/voice"
os.makedirs(VOICE_DIR, exist_ok=True)
ONNX=f"{VOICE_DIR}/en-us-lessac-medium.onnx"
CFG=f"{VOICE_DIR}/en-us-lessac-medium.onnx.json"
BASE="https://raw.githubusercontent.com/Humbre-tonto/Composiouploads/main/"

def ensure_voice():
    if not os.path.exists(ONNX):
        print("downloading voice model..."); urllib.request.urlretrieve(BASE+"piper_en-us-lessac-medium.onnx",ONNX)
    if not os.path.exists(CFG):
        urllib.request.urlretrieve(BASE+"piper_en-us-lessac-medium.onnx.json",CFG)

def resample_linear(a,sr_in,sr_out):
    if sr_in==sr_out: return a
    n_out=int(len(a)*sr_out/sr_in)
    return np.interp(np.linspace(0,1,n_out),np.linspace(0,1,len(a)),a).astype(np.float32)

def say(text,target_sr=24000):
    ensure_voice()
    tmp="/tmp/_piper_out.wav"
    subprocess.run(["python3","-m","piper","--model",ONNX,"--output_file",tmp],
                   input=text,capture_output=True,text=True,timeout=30)
    a,sr=sf.read(tmp)
    a=np.nan_to_num(a.astype(np.float32),nan=0.0,posinf=0.0,neginf=0.0)
    bad=np.abs(a)>1.0001
    if bad.any():
        idx=np.arange(len(a)); good=~bad
        a[bad]=np.interp(idx[bad],idx[good],a[good]) if good.any() else 0.0
    pk=float(np.max(np.abs(a)))
    if pk>0: a=(a/pk)*0.92
    return resample_linear(a,sr,target_sr)
