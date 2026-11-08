import json, os, time, requests, subprocess, pathlib

BASE="https://zerocollabs-ltx-2-3-turbo.hf.space"
API="generate_video"
PROMPTS=[
"Keep the exact same two adult felt-puppet characters, faces, clothing and tactile wool texture from the input frame. The setting naturally becomes a snowy traditional village in Ishikawa Shiramine, viewed from a warm wooden house doorway. Long clear icicles hang from the eaves. The woman notices them, stands and walks toward the doorway, points upward, looks curious and surprised. The bespectacled man follows her gaze, leans closer and looks up. Clear physical acting: walking, pointing, head turns, eye movement, hands. Professional cinematic stop-motion feel. No text, no captions, no logos, no Ken Burns, no camera-only zoom.",
"Continue seamlessly from the same felt characters and snowy Shiramine doorway. The bespectacled man steps beside the woman, points clearly at one long icicle and gestures as if explaining its local name. The woman looks at the icicle, measures its length with both hands, reacts with amused surprise, then turns to him and laughs. He nods and smiles. Snow drifts lightly outside. End on both looking back at the icicles. Natural hand/body motion, consistent faces and clothes, no text, no captions, no logos, no slow zoom."
]

def upload_image(path):
    for attempt in range(4):
        with open(path,"rb") as f:
            r=requests.post(BASE+"/gradio_api/upload",files={"files":(os.path.basename(path),f,"image/jpeg")},timeout=120)
        if r.ok:
            arr=r.json()
            if isinstance(arr,list) and arr: return arr[0]
        print("upload",attempt,r.status_code,r.text[:200],flush=True)
        time.sleep(5*(attempt+1))
    raise RuntimeError("upload failed")

def filedata(path,name):
    return {"path":path,"url":f"{BASE}/gradio_api/file={path}","orig_name":name,"size":None,"mime_type":"image/jpeg","meta":{"_type":"gradio.FileData"}}

def submit(img_path, orig, prompt):
    data=[filedata(img_path,orig),None,prompt,12.0,"Image-to-Video",False,42,True,768,512,None]
    for attempt in range(4):
        r=requests.post(BASE+f"/gradio_api/call/{API}",json={"data":data},timeout=120)
        print("submit status",r.status_code,r.text[:300],flush=True)
        if r.ok:
            j=r.json()
            if j.get("event_id"): return j["event_id"]
        time.sleep(6*(attempt+1))
    raise RuntimeError("submit failed")

def wait_result(eid):
    url=BASE+f"/gradio_api/call/{API}/{eid}"
    with requests.get(url,headers={"Accept":"text/event-stream"},stream=True,timeout=(30,900)) as r:
        r.raise_for_status()
        event=""; data=[]
        for raw in r.iter_lines(decode_unicode=True):
            if raw is None: continue
            line=raw.strip("\r")
            if not line:
                if event=="complete":
                    payload=json.loads("\n".join(data))
                    first=payload[0] if isinstance(payload,list) and payload else None
                    print("complete payload first",repr(first)[:1000],flush=True)
                    if isinstance(first,dict):
                        if first.get("url"): return first["url"]
                        if first.get("path"): return BASE+"/gradio_api/file="+first["path"]
                    if isinstance(first,str):
                        if first.startswith("http"): return first
                        return BASE+"/gradio_api/file="+first
                    raise RuntimeError("no video in complete")
                if event=="error":
                    raise RuntimeError("upstream error: "+"\n".join(data))
                event=""; data=[]; continue
            if line.startswith("event:"): event=line[6:].strip()
            elif line.startswith("data:"): data.append(line[5:].strip())
    raise RuntimeError("stream ended")

def download(url,out):
    with requests.get(url,stream=True,timeout=240) as r:
        r.raise_for_status()
        with open(out,"wb") as f:
            for c in r.iter_content(1024*1024):
                if c: f.write(c)

def run(args):
    print("+"," ".join(args),flush=True)
    subprocess.run(args,check=True)

cur="start.jpg"
for i,p in enumerate(PROMPTS,1):
    up=upload_image(cur)
    eid=submit(up,os.path.basename(cur),p)
    print("event_id",eid,flush=True)
    u=wait_result(eid)
    print("video_url",u,flush=True)
    out=f"ltx_clip{i}.mp4"; download(u,out)
    run(["ffmpeg","-v","error","-i",out,"-f","null","-"])
    run(["ffmpeg","-y","-sseof","-0.2","-i",out,"-frames:v","1","-q:v","2",f"ltx_last{i}.jpg"])
    cur=f"ltx_last{i}.jpg"
    pathlib.Path(f"ltx_clip{i}.url.txt").write_text(u)
print("DONE")
