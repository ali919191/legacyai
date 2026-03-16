const apiBase = window.LEGACY_AI_API_BASE || '/api/v1';

const askButton = document.getElementById('ask-button');
const refreshButton = document.getElementById('refresh-button');
const questionInput = document.getElementById('chat-question');
const userIdInput = document.getElementById('user-id');
const historyContainer = document.getElementById('conversation-history');
const questionsContainer = document.getElementById('enhanced-questions');
const errorMessage = document.getElementById('error-message');

let history = [];
let pendingQuestions = [];

askButton.addEventListener('click', async () => {
  const query = questionInput.value.trim();
  if (!query) {
    return;
  }

  setError('');
  try {
    const response = await request('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, user_id: userIdInput.value.trim() || undefined }),
    });

    history.push({
      question: query,
      answer: response.answer,
      memories_used: response.memories_used || [],
      memory_priority: response.memory_priority || [],
    });
    if (Array.isArray(response.enhanced_questions)) {
      pendingQuestions = mergeQuestions(pendingQuestions, response.enhanced_questions);
    }
    questionInput.value = '';
    renderHistory();
    renderQuestions();
  } catch (error) {
    setError(error.message || 'Unable to reach the Legacy AI backend.');
  }
});

refreshButton.addEventListener('click', async () => {
  const userId = userIdInput.value.trim();
  if (!userId) {
    return;
  }

  setError('');
  try {
    const response = await request(`/enhanced-questions?user_id=${encodeURIComponent(userId)}`);
    pendingQuestions = mergeQuestions([], response);
    renderQuestions();
  } catch (error) {
    setError(error.message || 'Unable to load enhanced questions.');
  }
});

function renderHistory() {
  if (!history.length) {
    historyContainer.innerHTML = '<article>No conversation history yet.</article>';
    return;
  }

  historyContainer.innerHTML = history
    .map(
      (entry) => `
        <article>
          <div class="message-label">You asked</div>
          <p>${escapeHtml(entry.question)}</p>
          <div class="message-label">Legacy AI replied</div>
          <p>${escapeHtml(entry.answer)}</p>
          <div class="memory-list">
            ${entry.memories_used.length
              ? entry.memories_used.map((memoryId) => `<span class="memory-tag">${escapeHtml(memoryId)}</span>`).join('')
              : '<span class="memory-tag">No memories referenced</span>'}
          </div>
          ${entry.memory_priority?.length
            ? `<div class="memory-priority">
                 <div class="message-label">Priority Ranking</div>
                 ${entry.memory_priority
                   .slice(0, 3)
                   .map(
                     (item) =>
                       `<p>${escapeHtml(item.memory_id)} - score ${Number(item.priority_score).toFixed(3)}</p>`,
                   )
                   .join('')}
               </div>`
            : ''}
        </article>
      `,
    )
    .join('');
}

function renderQuestions() {
  const openQuestions = pendingQuestions.filter((question) => question.status !== 'answered');
  if (!openQuestions.length) {
    questionsContainer.innerHTML = '<section>No pending enhanced questions.</section>';
    return;
  }

  questionsContainer.innerHTML = '';
  openQuestions.forEach((question) => {
    const section = document.createElement('section');
    section.innerHTML = `
      <div class="priority">${escapeHtml(question.priority)}</div>
      <h3>${escapeHtml(question.question)}</h3>
      <p>${escapeHtml(question.context_description)}</p>
      <textarea class="answer-box" placeholder="Add the missing detail here"></textarea>
      <button type="button">Save answer</button>
    `;
    const answerBox = section.querySelector('textarea');
    const button = section.querySelector('button');
    button.addEventListener('click', async () => {
      const answer = answerBox.value.trim();
      if (!answer) {
        return;
      }
      setError('');
      try {
        await request(`/enhanced-questions/${encodeURIComponent(question.question_id)}/answer`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ answer }),
        });
        pendingQuestions = pendingQuestions.map((item) =>
          item.question_id === question.question_id ? { ...item, status: 'answered', answer } : item,
        );
        renderQuestions();
      } catch (error) {
        setError(error.message || 'Unable to save answer.');
      }
    });
    questionsContainer.appendChild(section);
  });
}

async function request(path, options) {
  const response = await fetch(`${apiBase}${path}`, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Request failed');
  }
  return response.json();
}

function mergeQuestions(existing, incoming) {
  const questionMap = new Map(existing.map((question) => [question.question_id, question]));
  incoming.forEach((question) => questionMap.set(question.question_id, question));
  return Array.from(questionMap.values());
}

function setError(message) {
  errorMessage.textContent = message;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

renderHistory();
renderQuestions();