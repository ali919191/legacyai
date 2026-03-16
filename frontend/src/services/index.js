const API_BASE = process.env.REACT_APP_FAMILY_API_BASE || '/api/v1';

export async function askLegacyAI({ query, userId }) {
  return request('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      user_id: userId || undefined,
    }),
  });
}

export async function getEnhancedQuestions(userId) {
  const params = new URLSearchParams({ user_id: userId });
  return request(`/enhanced-questions?${params.toString()}`);
}

export async function answerEnhancedQuestion(questionId, answer, updates = {}) {
  return request(`/enhanced-questions/${questionId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      answer,
      memory_updates: updates.memory_updates,
      person_updates: updates.person_updates,
    }),
  });
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);

  if (!response.ok) {
    let detail = 'Request failed';
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch (error) {
      detail = error?.message || detail;
    }
    throw new Error(detail);
  }

  return response.json();
}
