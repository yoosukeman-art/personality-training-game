import json, os, time, requests, subprocess, pathlib

BASE="https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space"
API="generate_video"
NEG="色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, 最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, 画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, 杂乱的背景, 三条腿, 背景人很多, 倒着走, text, captions, subtitles, logos, watermark"
PROMPT="Keep exactly the same two adult felt-puppet characters from the input image: man with black curly hair, black rectangular glasses, dark navy denim jacket and cream knit; woman with brown bob, mustard cardigan and cream top. The room opens naturally onto a snowy traditional wooden village in Ishikawa Shiramine. Long clear icicles hang from the eaves. The woman notices the icicles, stands up, walks toward the doorway, points upward with curious surprise. The bespectacled man follows her gaze and leans closer. Physical acting drives the scene: walking, pointing, head turns, eye movement, hands. Preserve crisp wool fibers and handcrafted stop-motion feel. No text, no captions, no logos, no camera-only zoom."

def upload(path):
    with open(path,"rb") as f:
        r=requests.post(BASE+"/gradio_api/upload",files={"files":(os.path.basename(path),f,"image/jpeg")},timeout=120)
    print("upload",r.status_code,r.text[:500],flush=True); r.raise_for_status()
    arr=r.json(); return arr[0]

def filedata(p,name):
    return {"path":p,"url":f"{BASE}/gradio_api/file={p}","orig_name":name,"size":None,"mime_type":"image/jpeg","meta":{"_type":"gradio.FileData"}}

def wait(eid):
    with requests.get(BASE+f"/gradio_api/call/{API}/{eid}",headers={"Accept":"text/event-stream"},stream=True,timeout=(30,600)) as r:
        r.raise_for_status(); event=""; data=[]
        for raw in r.iter_lines(decode_unicode=True):
            if raw is None: continue
            line=raw.strip("\r")
            if not line:
                if event=="complete":
                    payload=json.loads("\n".join(data)); print("complete",repr(payload)[:1500],flush=True)
                    first=payload[0] if isinstance(payload,list) and payload else None
                    if isinstance(first,dict):
                        if first.get("url"): return first["url"]
                        if first.get("path"): return BASE+"/gradio_api/file="+first["path"]
                    if isinstance(first,str):
                        return first if first.startswith("http") else BASE+"/gradio_api/file="+first
                    raise RuntimeError("no video")
                if event=="error": raise RuntimeError("upstream error: "+"\n".join(data))
                event=""; data=[]; continue
            if line.startswith("event:"): event=line[6:].strip()
            elif line.startswith("data:"): data.append(line[5:].strip())
    raise RuntimeError("stream ended")

p=upload("start.jpg")
data=[filedata(p,"start.jpg"),PROMPT,4,NEG,5.0,1.0,1.0,42,True]
r=requests.post(BASE+f"/gradio_api/call/{API}",json={"data":data},timeout=120)
print("submit",r.status_code,r.text[:1000],flush=True); r.raise_for_status()
eid=r.json().get("event_id")
if not eid: raise RuntimeError("no event")
url=wait(eid); print("video_url",url,flush=True)
with requests.get(url,stream=True,timeout=240) as rr:
    rr.raise_for_status()
    with open("probe.mp4","wb") as f:
        for c in rr.iter_content(1024*1024):
            if c:f.write(c)
subprocess.run(["ffmpeg","-v","error","-i","probe.mp4","-f","null","-"],check=True)
subprocess.run(["ffmpeg","-y","-ss","2.5","-i","probe.mp4","-frames:v","1","-q:v","2","probe_mid.jpg"],check=True)
pathlib.Path("probe.url.txt").write_text(url)
print("DONE")
