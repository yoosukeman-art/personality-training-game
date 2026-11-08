import json, os, wave, hashlib
from pathlib import Path
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile

SCRIPTS = [{"ep":1,"seg":1,"speaker":11,"text":"リモコンが見つからない。ソファの下も、机の上も探したのに出てこない。こんな時のイライラ、津軽弁では何と言う？"},{"ep":1,"seg":2,"speaker":10,"text":"『かちゃくちゃね』。津軽弁で『いらいらする』という意味。青森の津軽弁紹介にも載っている言葉です。"},{"ep":1,"seg":3,"speaker":11,"text":"ただ怒っているだけじゃなく、物事がうまく進まず、気持ちが落ち着かない。そんな時に出てくる一言です。"},{"ep":1,"seg":4,"speaker":10,"text":"リモコン探しが終わっても、この言葉は忘れない。『かちゃくちゃね』。一度聞いたら耳に残るね。"},{"ep":2,"seg":1,"speaker":10,"text":"屋根から長く垂れ下がった氷。そう、つらら。石川の白峰では、このつららを何と呼ぶと思う？"},{"ep":2,"seg":2,"speaker":11,"text":"答えは『がまだれ』。白峰のことばを調べた国立国語研究所の記録に、つららの呼び名として残っています。"},{"ep":2,"seg":3,"speaker":10,"text":"『つらら』と『がまだれ』。同じものなのに、音だけ聞くとまったく違う。初めて聞いたら何のことか分からないね。"},{"ep":2,"seg":4,"speaker":11,"text":"雪国で見慣れた景色にも、その土地ならではの呼び名がある。白峰のことばに残る、冬の一語です。"},{"ep":3,"seg":1,"speaker":11,"text":"お化け屋敷の入口で『俺が先に行く』と胸を張ったのに、カーテンが揺れただけで一歩も進めなくなった。"},{"ep":3,"seg":2,"speaker":10,"text":"香川の方言『おとっちゃま』。香川県立図書館の讃岐方言集では、『おくびょう者』という意味で紹介されています。"},{"ep":3,"seg":3,"speaker":11,"text":"つまり、強がっているけれど本当は怖がり。そんな人を表す言葉なんですね。音の響きも独特です。"},{"ep":3,"seg":4,"speaker":10,"text":"おとっちゃま。音はちょっとかわいいけど、言われた本人は複雑かもしれないね。"},{"ep":4,"seg":1,"speaker":10,"text":"台所で『ほいじょ取って』と言われたら、何を渡せばいい？知らないと、ちょっと戸惑う言葉です。"},{"ep":4,"seg":2,"speaker":11,"text":"山形県の方言辞典に載る『ほいじょ』は、包丁のこと。台所で使う、あの刃物です。"},{"ep":4,"seg":3,"speaker":10,"text":"包丁が『ほいじょ』。音だけ聞くと、食べ物なのか道具なのかも分からないね。"},{"ep":4,"seg":4,"speaker":11,"text":"山形の方言辞典に記録された呼び名です。いつもの道具が、知らない名前で呼ばれると新鮮ですね。"},{"ep":5,"seg":1,"speaker":11,"text":"そうめんが、汁に入っていない。フライパンで油と一緒に炒めている。沖縄のこの料理、名前がちょっと長い。"},{"ep":5,"seg":2,"speaker":10,"text":"『そーみんぷっとぅるー』。国立国語研究所のオンライン沖縄語辞典では、そうめんの油炒めという料理名です。"},{"ep":5,"seg":3,"speaker":11,"text":"長い名前だけど、意味を知ると料理の姿がすっと浮かぶ。そうめんを炒めた一皿なんですね。"},{"ep":5,"seg":4,"speaker":10,"text":"食べ物の名前にも、その土地の言葉がぎゅっと詰まっている。そーみんぷっとぅるー、覚えた？"},{"ep":6,"seg":1,"speaker":10,"text":"京都の家を訪ねて、帰り際に『お邪魔しました』。京ことばには、こんな長い言い方があります。"},{"ep":6,"seg":2,"speaker":11,"text":"『おやかまっさんどした』。京阪の京ことば紹介では、『お邪魔しました』という意味で載っています。"},{"ep":6,"seg":3,"speaker":10,"text":"『お喧し様』に『どした』がついた表現。『やかましい』が元になっているんだね。"},{"ep":6,"seg":4,"speaker":11,"text":"長いひと言だけど、意味は『お邪魔しました』。由来を知ると、京ことばの面白さが見えてきます。"},{"ep":7,"seg":1,"speaker":10,"text":"ぬかるみに足を踏み入れたら、靴が泥に沈んで抜けない。こんな時、博多では何と言う？"},{"ep":7,"seg":2,"speaker":11,"text":"『いぼる』。博多の方言紹介では、『はまる、埋まる』こと。ぬかるみに足を取られた時などに使います。"},{"ep":7,"seg":3,"speaker":10,"text":"ただ転ぶのとは違う。足が泥の中にずぶっとはまってしまう。そんな場面の言葉なんだね。"},{"ep":7,"seg":4,"speaker":11,"text":"短い言葉なのに、足が沈む様子まで浮かんでくる。博多の『いぼる』、覚えておきたいね。"}]

root = Path("voicevox_core")
onnx_candidates = sorted((root / "onnxruntime").rglob("libvoicevox_onnxruntime.so*"))
if not onnx_candidates:
    raise FileNotFoundError("VOICEVOX ONNX Runtime shared library not found")
onnx = onnx_candidates[0]
print("onnxruntime", onnx)
dict_dir = root / "dict" / "open_jtalk_dic_utf_8-1.11"
models = root / "models" / "vvms"
out = Path("hougen_audio")
out.mkdir(exist_ok=True)

runtime = Onnxruntime.load_once(filename=str(onnx))
synth = Synthesizer(runtime, OpenJtalk(str(dict_dir)))

for fn in ("0.vvm","4.vvm"):
    with VoiceModelFile.open(str(models / fn)) as model:
        synth.load_voice_model(model)

manifest = []
for item in SCRIPTS:
    q = synth.create_audio_query(item["text"], item["speaker"])
    q.speed_scale = 1.0
    wav_bytes = synth.synthesis(q, item["speaker"])
    name = f'ep{item["ep"]:02d}_seg{item["seg"]:02d}_spk{item["speaker"]}.wav'
    path = out / name
    path.write_bytes(wav_bytes)
    with wave.open(str(path), "rb") as wf:
        dur = wf.getnframes() / wf.getframerate()
        rate = wf.getframerate()
        channels = wf.getnchannels()
    manifest.append({
        **item,
        "file": name,
        "duration_sec": round(dur, 4),
        "sample_rate": rate,
        "channels": channels,
        "bytes": len(wav_bytes),
        "sha256": hashlib.sha256(wav_bytes).hexdigest(),
    })
    print(name, dur, item["speaker"])

assert len(manifest) == 28
assert all(x["duration_sec"] > 0.2 and x["bytes"] > 1000 for x in manifest)
Path("hougen_audio_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("DONE", len(manifest))
