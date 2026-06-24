const traits = ["外向性", "協調性", "誠実性", "情緒安定性", "開放性"];

const questions = [
  { text: "初対面の人がいる場でも、自分から会話のきっかけを作ることが多い", trait: "外向性" },
  { text: "チームの雰囲気がぎくしゃくしていると、橋渡し役を意識する", trait: "協調性" },
  { text: "締切や段取りを逆算して、早めに準備を始める", trait: "誠実性" },
  { text: "急な変更があっても、状況を整理して落ち着いて対応しやすい", trait: "情緒安定性" },
  { text: "前例のないテーマでも、面白がって調べたり試したりする", trait: "開放性" },
  { text: "大人数の場で発言するより、少人数で考えを深める方が自然だ", trait: "外向性", reverse: true },
  { text: "相手の困りごとに気づくと、声をかけたり手を貸したりしたくなる", trait: "協調性" },
  { text: "細かい確認作業は、つい後回しにしがちだ", trait: "誠実性", reverse: true },
  { text: "予定外の指摘を受けても、必要な情報として受け止めやすい", trait: "情緒安定性" },
  { text: "慣れた方法を守るより、新しい視点を取り入れる方に関心が向く", trait: "開放性" },
  { text: "会議では、沈黙が続くと意見や質問を出して流れを作る", trait: "外向性" },
  { text: "自分の意見と違っても、まず相手の背景を理解しようとする", trait: "協調性" },
  { text: "作業の抜け漏れを防ぐために、メモやチェックリストを活用する", trait: "誠実性" },
  { text: "忙しい時期でも、気持ちを切り替えて優先順位をつけられる", trait: "情緒安定性" },
  { text: "異なる分野の知識を組み合わせて考えるのが好きだ", trait: "開放性" },
  { text: "周囲を巻き込みながら、場の熱量を上げることがある", trait: "外向性" },
  { text: "誰かが発言しにくそうな時、話しやすい空気を作ろうとする", trait: "協調性" },
  { text: "細部の精度より、まず動かしてみることを優先しやすい", trait: "誠実性", reverse: true },
  { text: "想定外のトラブルでも、必要以上に引きずらず次の手を考える", trait: "情緒安定性" },
  { text: "資料やデータから、まだ見えていないパターンを探すのが好きだ", trait: "開放性" },
  { text: "自分の考えを言葉にして周囲へ共有することに抵抗が少ない", trait: "外向性" },
  { text: "成果だけでなく、関わる人の納得感も大切にしたい", trait: "協調性" },
  { text: "決めたことを継続し、安定して積み上げることが得意だ", trait: "誠実性" },
  { text: "プレッシャーがある場面でも、表情や声の調子は比較的安定している", trait: "情緒安定性" },
  { text: "新しい学びや発想に触れると、仕事への応用を考えたくなる", trait: "開放性" },
  { text: "一人で集中して進める時間が長い方が、力を発揮しやすい", trait: "外向性", reverse: true },
  { text: "対立が起きた時、双方の接点を探して整理したい", trait: "協調性" },
  { text: "ルールや手順を整えることで、チームの安心感を作りたい", trait: "誠実性" },
  { text: "変化の大きい状況でも、まず事実と感情を分けて考える", trait: "情緒安定性" },
  { text: "まだ答えがない問いについて、仮説を立てて探究するのが好きだ", trait: "開放性" }
];

const answerLabels = [
  "まったく当てはまらない",
  "あまり当てはまらない",
  "どちらともいえない",
  "やや当てはまる",
  "とても当てはまる"
];

const typeProfiles = [
  { key: "織田信長タイプ：突破型", title: "突破の旗振り役", match: s => s.外向性 >= 22 && s.開放性 >= 22 && s.情緒安定性 >= 18, work: "変化の局面で方向を示し、周囲が動き出すきっかけを作る人として見えやすいです。", strength: "意思決定の速さ、挑戦の打ち出し、停滞感を動かす推進力。", challenge: "合意形成や細かな調整が長く続く場面では、もどかしさを感じやすいかもしれません。", tips: "目的、制約、任せたい範囲を明確にすると、前進力を活かしやすくなります。" },
  { key: "豊臣秀吉タイプ：巻き込み型", title: "場を動かす調整役", match: s => s.外向性 >= 21 && s.協調性 >= 22, work: "人との距離を縮めながら、協力の輪を広げる存在として見えやすいです。", strength: "関係構築、場の活性化、相手に合わせた働きかけ。", challenge: "一人で黙々と進める作業が続くと、手応えを感じにくいことがあります。", tips: "相談相手や共有の場を用意すると、巻き込み力が自然に発揮されます。" },
  { key: "徳川家康タイプ：安定構築型", title: "腰を据えた基盤づくり役", match: s => s.誠実性 >= 22 && s.情緒安定性 >= 22, work: "慌ただしい場面でも土台を整え、継続しやすい形にする人として見えやすいです。", strength: "継続力、リスクの見立て、仕組みを安定させる力。", challenge: "短期間で大きく方向転換する場面では、確認したい点が多くなりやすいです。", tips: "背景情報と判断期限を共有すると、安定した進行管理につながります。" },
  { key: "坂本龍馬タイプ：改革接続型", title: "違いをつなぐ変革役", match: s => s.開放性 >= 23 && s.協調性 >= 19 && s.外向性 >= 18, work: "異なる立場やアイデアを結び、次の可能性を提案する人として見えやすいです。", strength: "橋渡し、発想転換、新しい協力関係の設計。", challenge: "細部の詰めや定型的な手続きが続くと、関心が分散しやすいかもしれません。", tips: "自由に考える時間と、最後に整える役割を分けると進めやすくなります。" },
  { key: "渋沢栄一タイプ：実務構築型", title: "理念を形にする設計役", match: s => s.誠実性 >= 22 && s.協調性 >= 20 && s.開放性 >= 17, work: "目的を現実的な手順に落とし込み、関係者と進める人として見えやすいです。", strength: "実務設計、信頼形成、長期視点での積み上げ。", challenge: "目的が曖昧なまま走り出す場面では、動き出しにくさを感じることがあります。", tips: "なぜ取り組むのかを共有すると、実行計画への落とし込みが進みます。" },
  { key: "伊能忠敬タイプ：精密探究型", title: "確かな情報を集める探究役", match: s => s.誠実性 >= 23 && s.開放性 >= 20, work: "丁寧に観察し、根拠を積み重ねて判断材料を作る人として見えやすいです。", strength: "精度の高い確認、地道な調査、情報の整理。", challenge: "十分な確認時間がない場面では、落ち着かなさを感じやすいかもしれません。", tips: "必要な精度と期限を先に合わせると、探究の深さを活かせます。" },
  { key: "紫式部タイプ：空気観察型", title: "場の機微を読む観察役", match: s => s.協調性 >= 22 && s.外向性 <= 18 && s.開放性 >= 17, work: "発言の背景や場の空気を読み取り、言葉にしにくい変化に気づく人として見えやすいです。", strength: "洞察、丁寧な表現、相手の感情への配慮。", challenge: "即興で大きく発言を求められる場面では、考える時間が欲しくなることがあります。", tips: "事前情報や書いて共有する選択肢があると、観察から得た気づきが出やすくなります。" },
  { key: "ナイチンゲールタイプ：支援改善型", title: "安心を整える改善役", match: s => s.協調性 >= 23 && s.誠実性 >= 20, work: "人が動きやすい環境を整え、困りごとを改善する人として見えやすいです。", strength: "支援、改善提案、現場目線の気づき。", challenge: "周囲の困りごとを抱え込みすぎると、負荷が集中しやすいことがあります。", tips: "支援範囲と優先順位を一緒に決めると、持続的に力を発揮できます。" },
  { key: "ニュートンタイプ：分析集中型", title: "原理を掘り下げる分析役", match: s => s.開放性 >= 22 && s.外向性 <= 17 && s.情緒安定性 >= 17, work: "複雑な課題を一段深く考え、構造や原因を見つける人として見えやすいです。", strength: "集中、論理的な分析、本質的な問いの発見。", challenge: "頻繁な割り込みや雑談中心の場面では、集中のリズムを作りにくいことがあります。", tips: "考える時間を確保し、論点を絞って相談すると洞察を共有しやすくなります。" },
  { key: "ダーウィンタイプ：観察探究型", title: "変化を読み解く観察役", match: s => s.開放性 >= 21 && s.情緒安定性 >= 19, work: "小さな変化を観察し、仮説を立てながら学びを広げる人として見えやすいです。", strength: "観察、仮説検証、長い目で変化を捉える力。", challenge: "結論だけを急ぐ場面では、検討したい観点を残したまま進む感覚があるかもしれません。", tips: "途中経過の共有を歓迎すると、観察から得た学びがチームに広がります。" },
  { key: "バランス接続タイプ：対話促進型", title: "全体を見渡す対話役", match: () => true, work: "状況に応じて聞く、話す、整えるを切り替える人として見えやすいです。", strength: "バランス感覚、対話の促進、状況に合わせた関わり方。", challenge: "役割が曖昧な場面では、どこまで踏み込むか迷いやすいことがあります。", tips: "期待する役割を言葉にすると、柔軟な動き方を合わせやすくなります。" }
];

let scores = createInitialScores();
let currentQuestionIndex = 0;
let currentCardText = "";

const introArea = document.getElementById("introArea");
const startButton = document.getElementById("startButton");
const questionArea = document.getElementById("questionArea");
const questionText = document.getElementById("questionText");
const answerButtons = document.getElementById("answerButtons");
const progressText = document.getElementById("progressText");
const progressFill = document.getElementById("progressFill");
const resultArea = document.getElementById("resultArea");
const resultCard = document.getElementById("resultCard");
const copyButton = document.getElementById("copyButton");
const restartButton = document.getElementById("restartButton");
const copyMessage = document.getElementById("copyMessage");

startButton.addEventListener("click", startDiagnosis);
restartButton.addEventListener("click", startDiagnosis);
copyButton.addEventListener("click", copyResultCard);

function createInitialScores() {
  return traits.reduce((accumulator, trait) => {
    accumulator[trait] = 0;
    return accumulator;
  }, {});
}

function startDiagnosis() {
  scores = createInitialScores();
  currentQuestionIndex = 0;
  copyMessage.textContent = "";
  introArea.classList.add("hidden");
  resultArea.classList.add("hidden");
  questionArea.classList.remove("hidden");
  showQuestion();
}

function showQuestion() {
  const question = questions[currentQuestionIndex];
  questionText.textContent = question.text;
  progressText.textContent = `${currentQuestionIndex + 1} / ${questions.length}`;
  progressFill.style.width = `${(currentQuestionIndex / questions.length) * 100}%`;
  answerButtons.innerHTML = "";

  answerLabels.forEach((label, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", () => handleAnswer(index + 1));
    answerButtons.appendChild(button);
  });
}

function handleAnswer(rawScore) {
  const question = questions[currentQuestionIndex];
  const finalScore = question.reverse ? 6 - rawScore : rawScore;
  scores[question.trait] += finalScore;
  currentQuestionIndex += 1;

  if (currentQuestionIndex < questions.length) {
    showQuestion();
  } else {
    progressFill.style.width = "100%";
    showResult();
  }
}

function showResult() {
  const profile = typeProfiles.find(typeProfile => typeProfile.match(scores));
  const card = buildCard(profile);
  currentCardText = card.text;

  questionArea.classList.add("hidden");
  resultArea.classList.remove("hidden");
  resultCard.innerHTML = card.html;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function buildCard(profile) {
  const sections = [
    ["歴史上の人物にたとえたタイプ", profile.key],
    ["職場での見え方", profile.work],
    ["強み", profile.strength],
    ["苦手になりやすい場面", profile.challenge],
    ["一緒に働くコツ", profile.tips],
    ["研修ゲーム用の匿名カード", `私は「${profile.key}」です。職場では「${profile.title}」として関わることが多そうです。話しかける時は、${profile.tips}`]
  ];

  const html = `
    <h3>${profile.title}</h3>
    <p class="historical-type">${profile.key}</p>
    ${sections.map(([heading, body]) => `
      <section class="result-section">
        <h4>${heading}</h4>
        <p>${body}</p>
      </section>
    `).join("")}
  `;

  const text = [`タイプ名：${profile.title}`, ...sections.map(([heading, body]) => `${heading}：${body}`)].join("\n");
  return { html, text };
}

async function copyResultCard() {
  try {
    await navigator.clipboard.writeText(currentCardText);
    copyMessage.textContent = "結果カードをコピーしました。";
  } catch (error) {
    copyMessage.textContent = "コピーできない場合は、カード本文を選択してコピーしてください。";
  }
}
