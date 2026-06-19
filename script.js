const questions = [
  { text: "人と話す場面では、比較的自分から話しかける方だ", trait: "外向性", reverse: false },
  { text: "細かい段取りを考えるのはあまり得意ではない", trait: "誠実性", reverse: true },
  { text: "新しいやり方やアイデアを試すのは好きだ", trait: "開放性", reverse: false },
  { text: "相手の立場を考えて行動する方だ", trait: "協調性", reverse: false },
  { text: "急な予定変更があると、かなり動揺しやすい", trait: "情緒安定性", reverse: true }
];

const scores = {
  外向性: 0,
  協調性: 0,
  誠実性: 0,
  情緒安定性: 0,
  開放性: 0
};

let currentQuestionIndex = 0;

const startButton = document.getElementById("startButton");
const questionArea = document.getElementById("questionArea");
const questionText = document.getElementById("questionText");
const answerButtons = document.getElementById("answerButtons");
const resultArea = document.getElementById("resultArea");
const resultText = document.getElementById("resultText");

startButton.addEventListener("click", () => {
  startButton.classList.add("hidden");
  questionArea.classList.remove("hidden");
  showQuestion();
});

function showQuestion() {
  const question = questions[currentQuestionIndex];
  questionText.textContent = question.text;
  answerButtons.innerHTML = "";

  const labels = [
    "まったく当てはまらない",
    "あまり当てはまらない",
    "どちらともいえない",
    "やや当てはまる",
    "とても当てはまる"
  ];

  labels.forEach((label, index) => {
    const button = document.createElement("button");
    button.textContent = label;
    button.addEventListener("click", () => {
      const rawScore = index + 1;
      const finalScore = question.reverse ? 6 - rawScore : rawScore;
      scores[question.trait] += finalScore;

      currentQuestionIndex++;

      if (currentQuestionIndex < questions.length) {
        showQuestion();
      } else {
        showResult();
      }
    });
    answerButtons.appendChild(button);
  });
}

function showResult() {
  questionArea.classList.add("hidden");
  resultArea.classList.remove("hidden");

  resultText.innerHTML = `
    <p>外向性：${scores["外向性"]}</p>
    <p>協調性：${scores["協調性"]}</p>
    <p>誠実性：${scores["誠実性"]}</p>
    <p>情緒安定性：${scores["情緒安定性"]}</p>
    <p>開放性：${scores["開放性"]}</p>
  `;
}
