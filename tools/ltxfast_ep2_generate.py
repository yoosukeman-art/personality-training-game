import json, os, time, requests, subprocess, pathlib

BASE="https://lightricks-ltx-video-distilled.hf.space"
API="image_to_video"
NEG="worst quality, inconsistent motion, blurry, jittery, distorted, extra fingers, deformed hands, deformed face, text, captions, subtitles, logos, watermark, camera-only zoom"
PROMPTS=[
"Keep exactly the same two adult felt-puppet characters from the input image: man with black curly hair, black rectangular glasses, dark navy denim jacket and cream knit; woman with brown bob, mustard cardigan and cream top. Move the scene naturally to a snowy traditional wooden house in Ishikawa Shiramine. Long clear icicles hang from the eaves. The woman notices them, stands up, walks toward the doorway and points upward with curious surprise. The man follows her gaze and leans closer. Physical acting: walking, pointing, hands, head turns, eye movement. Cinematic handcrafted stop-motion felt texture, warm interior against cold snowy exterior. No text.",
"Continue the exact same two felt characters and snowy Shiramine doorway from the input frame. The bespectacled man steps beside the woman and points clearly at a long icicle, gesturing as if explaining its local name. The woman alternates her gaze between his hand and the icicle, raises her eyebrows and makes a small surprised gesture with both hands. Natural body motion, consistent faces and clothes, tactile wool fibers, professional framing. No text.",
"Continue seamlessly with the same felt characters. The woman moves a little closer but stays safely under the sheltered doorway, measures the visible icicle length with her hands without touching it, turns back with amused surprise and laughs. The man nods, smiles and points once more toward the icicles. Light snow drifts outside. End on both looking at the icicles together. Natural motion, same faces and clothes, no text."
]

def upload_image(path):
    for a in range(4):
        with open(path,"rb") as f:
            r=requests.post(BASE+"/gradio_api/upload",files={"files":(os.path.basename(path),f,"image/jpeg")},timeout=120)
        print("upload",a,r.status_code,r.text[:180],flush=True)
        if r.ok:
            arr=r.json()
            if isinstance(arr,list) and arr: return arr[0]
        time.sleep(5*(a+1))
    raise RuntimeError("upload failed")

def filedata(path,name):
    return {"path":path,"url":f"{BASE}/gradio_api/file={path}","orig_name":name,"size":None,"mime_type":"image/jpeg","meta":{"_type":"gradio.FileData"}}

def submit(img_path,orig,prompt):
    # prompt, neg, image, video_hidden, height, width, mode, duration, frames_to_use, seed, randomize, guidance, improve_texture
    data=[prompt,NEG,filedata(img_path,orig),None,1280,768,"image-to-video",8.5,9,42,True,3.0,True]
    for a in range(4):
        r=requests.post(BASE+f"/gradio_api/call/{API}",json={"data":data},timeout=120)
        print("submit",a,r.status_code,r.text[:300],flush=True)
        if r.ok:
            j=r.json()
            if j.get("event_id"): return j["event_id"]
        time.sleep(6*(a+1))
    raise RuntimeError("submit failed")

def wait_result(eid):
    with requests.get(BASE+f"/gradio_api/call/{API}/{eid}",headers={"Accept":"text/event-stream"},stream=True,timeout=(30,600)) as r:
        r.raise_for_status()
        event=""; data=[]
        for raw in r.iter_lines(decode_unicode=True):
            if raw is None: continue
            line=raw.strip("\r")
            if not line:
                if event=="complete":
                    payload=json.loads("\n".join(data))
                    first=payload[0] if isinstance(payload,list) and payload else None
                    print("complete",repr(first)[:1000],flush=True)
                    if isinstance(first,dict):
                        if first.get("url"): return first["url"]
                        if first.get("path"): return BASE+"/gradio_api/file="+first["path"]
                    if isinstance(first,str):
                        if first.startswith("http"): return first
                        return BASE+"/gradio_api/file="+first
                    raise RuntimeError("no video url")
                if event=="error": raise RuntimeError("upstream error: "+"\n".join(data))
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

def run(x): print("+"," ".join(x),flush=True); subprocess.run(x,check=True)

cur="start.jpg"
for i,p in enumerate(PROMPTS,1):
    up=upload_image(cur)
    eid=submit(up,os.path.basename(cur),p)
    print("event",i,eid,flush=True)
    url=wait_result(eid)
    print("url",i,url,flush=True)
    out=f"clip{i}.mp4"; download(url,out)
    run(["ffmpeg","-v","error","-i",out,"-f","null","-"])
    run(["ffmpeg","-y","-sseof","-0.15","-i",out,"-frames:v","1","-q:v","2",f"last{i}.jpg"])
    cur=f"last{i}.jpg"
    pathlib.Path(f"clip{i}.url.txt").write_text(url)
print("DONE")
