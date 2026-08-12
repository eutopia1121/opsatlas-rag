const questionInput = document.getElementById("question-input");
const askButton = document.getElementById("ask-button");
const answerArea = document.getElementById("answer-area");


askButton.addEventListener("click", async () => {
  const question = questionInput.value.trim();

  if (!question) {
    answerArea.innerHTML = "<h2>回答</h2><p>请输入问题后再提交。</p>";
    return;
  }
    askButton.disabled = true;
  askButton.textContent = "检索中...";
  answerArea.innerHTML = "<h2>回答</h2><p>正在检索知识库并生成回答，请稍候。</p>";

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: question,
      }),
    });

    if (!response.ok) {
      throw new Error("问答请求失败");
    }

    const data = await response.json();

        const sourcesHtml = data.sources
  .map((source) => {
    const pageText = source.page_number
      ? ` · 第 ${source.page_number} 页`
      : "";

    return `
      <li>
        <strong>${source.title}</strong>
        <span>
          ${source.source}${pageText}
          · Chunk ${source.chunk_id}
          · 相似度 ${source.score.toFixed(3)}
        </span>
      </li>
    `;
  })
  .join("");

    const sourceSection = data.sources.length
      ? `
        <div class="sources">
          <h3>参考来源</h3>
          <ul>${sourcesHtml}</ul>
        </div>
      `
      : `
        <div class="sources">
          <h3>参考来源</h3>
          <p>未检索到达到阈值的可靠资料。</p>
        </div>
      `;

    answerArea.innerHTML = `
      <h2>回答</h2>
      <p class="answer-text">${data.answer}</p>
      ${sourceSection}
    `;
  } catch (error) {
    answerArea.innerHTML = "<h2>回答</h2><p>请求失败，请确认后端服务和 Milvus 已启动。</p>";
  } finally {
    askButton.disabled = false;
    askButton.textContent = "开始提问";
  }
});