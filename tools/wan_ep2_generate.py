import json, os, time, requests, subprocess, pathlib, sys
BASE="https://cbensimon-wan2-2-fp8da-aoti-preview2.hf.space"
FN="generate_video"
NEG="色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, 最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, 画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, 杂乱的背景, 三条腿, 背景人很多, 倒着走"
PROMPTS=[
"Same two adult felt-puppet characters from the input frame, consistent faces and clothing. Transform the setting naturally into a snowy traditional village in Ishikawa Shiramine. The woman notices long clear icicles hanging from a wooden eave through the open doorway, stands up, walks two small steps closer and points upward with curious surprise. The bespectacled man follows her gaze and leans toward the doorway. Physical character movement drives the scene, hands and head turns, no text, no captions, no logos, no camera-only zoom, professional cinematic stop-motion felt texture.",
"Continue the same felt characters and snowy Shiramine setting from the previous frame. The bespectacled man steps beside the woman and clearly points at one long icicle, then gestures as if explaining its local name. The woman looks from his hand to the icicle, raises her eyebrows and makes a small 'really?' gesture with both hands. Natural hand movement, eye movement and body turns. No text or captions, no Ken Burns, no floating graphics.",
"Continue seamlessly. The woman carefully moves closer to the eave, looks up at the icicle, measures its length with her hands without touching it, then turns back toward the man with amused surprise. The man nods and smiles. Snow drifts lightly outside. Keep the exact same adult felt faces, clothing and tactile wool texture. No text, no captions, no logos, no meaningless zoom.",
"Continue seamlessly. Both characters stand safely under the sheltered doorway looking at several icicles. The woman repeats the idea with an amused expression, points once more toward the icicles, and the man laughs softly and nods. End on a clear shared reaction that feels like the punchline of a short educational comedy. Physical acting and natural framing, no text, no captions, no logos, no slow zoom."
]

def upload_image(path):
    for attempt in range(5):
        with open(path,"rb") as f:
            r=requests.post(BASE+"/gradio_api/upload",files={"files":(os.path.basename(path),f,"image/jpeg")},timeout=120)
        if r.ok:
            arr=r.json()
            if isinstance(arr,list) and arr: return arr[0]
        print("upload retry",attempt,r.status_code,r.text[:200],flush=True)
        time.sleep(8*(attempt+1))
    raise RuntimeError("upload failed")

def submit(image_path, orig, prompt):
    inp={"path":image_path,"url":f"{BASE}/gradio_api/file={image_path}","orig_name":orig,"size":None,"mime_type":"image/jpeg","meta":{"_type":"gradio.FileData"}}
    data=[inp,None,prompt,8,NEG,4.5,1,1,42,True,6,"UniPCMultistep",3.0,16,False,True]
    for attempt in range(5):
        r=requests.post(BASE+f"/gradio_api/call/{FN}",json={"data":data},timeout=120)
        if r.ok and r.json().get("event_id"): return r.json()["event_id"]
        print("submit retry",attempt,r.status_code,r.text[:300],flush=True)
        time.sleep(10*(attempt+1))
    raise RuntimeError("submit failed")

def wait_result(event_id):
    url=BASE+f"/gradio_api/call/{FN}/{event_id}"
    for reconnect in range(3):
        try:
            with requests.get(url,headers={"Accept":"text/event-stream"},stream=True,timeout=(30,420)) as r:
                r.raise_for_status()
                event=""; data=[]
                for raw in r.iter_lines(decode_unicode=True):
                    if raw is None: continue
                    line=raw.strip("\r")
                    if not line:
                        if event=="complete":
                            payload=json.loads("\n".join(data))
                            first=payload[0] if isinstance(payload,list) and payload else None
                            if isinstance(first,dict):
                                u=first.get("url")
                                p=first.get("path")
                                if u: return u
                                if p: return BASE+"/gradio_api/file="+p
                            if isinstance(first,str): return BASE+"/gradio_api/file="+first
                            raise RuntimeError("complete without video URL")
                        if event=="error":
                            raise RuntimeError("upstream error: "+"\n".join(data))
                        event=""; data=[]; continue
                    if line.startswith("event:"): event=line[6:].strip()
                    elif line.startswith("data:"): data.append(line[5:].strip())
        except Exception as e:
            print("stream reconnect",reconnect,repr(e),flush=True)
            time.sleep(10)
    raise RuntimeError("result stream ended")

def download(url,out):
    with requests.get(url,stream=True,timeout=180) as r:
        r.raise_for_status()
        with open(out,"wb") as f:
            for ch in r.iter_content(1024*1024):
                if ch: f.write(ch)

def run(cmd):
    print("+"," ".join(cmd),flush=True)
    subprocess.run(cmd,check=True)

current="start.jpg"
for i,prompt in enumerate(PROMPTS,1):
    remote=upload_image(current)
    eid=submit(remote,os.path.basename(current),prompt)
    print("event",i,eid,flush=True)
    video_url=wait_result(eid)
    print("video",i,video_url,flush=True)
    out=f"clip{i}.mp4"
    download(video_url,out)
    run(["ffmpeg","-y","-sseof","-0.15","-i",out,"-frames:v","1","-q:v","2",f"last{i}.jpg"])
    current=f"last{i}.jpg"
    pathlib.Path(f"clip{i}.url.txt").write_text(video_url)

print("DONE",flush=True)
