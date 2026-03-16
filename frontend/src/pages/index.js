import { useMemo, useState } from 'react';

import { ConversationHistory, EnhancedQuestionsPanel } from '../components';
import {
  answerEnhancedQuestion,
  askLegacyAI,
  getEnhancedQuestions,
} from '../services';

export default function HomePage() {
  const [userId, setUserId] = useState('family_user');
  const [questionText, setQuestionText] = useState('');
  const [history, setHistory] = useState([]);
  const [enhancedQuestions, setEnhancedQuestions] = useState([]);
  const [draftAnswers, setDraftAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [answeringQuestionId, setAnsweringQuestionId] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const pendingCount = useMemo(
    () => enhancedQuestions.filter((question) => question.status === 'pending').length,
    [enhancedQuestions],
  );

  async function handleAsk(event) {
    event.preventDefault();
    const trimmedQuestion = questionText.trim();
    if (!trimmedQuestion) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage('');

    try {
      const result = await askLegacyAI({ query: trimmedQuestion, userId });
      setHistory((current) => [
        ...current,
        {
          id: `${Date.now()}-${current.length}`,
          question: trimmedQuestion,
          answer: result.answer,
          memoriesUsed: result.memories_used || [],
        },
      ]);
      if (Array.isArray(result.enhanced_questions) && result.enhanced_questions.length) {
        setEnhancedQuestions((current) => mergeQuestions(current, result.enhanced_questions));
      }
      setQuestionText('');
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Unable to contact the Legacy AI backend.'));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function refreshEnhancedQuestions() {
    if (!userId.trim()) {
      return;
    }
    setIsRefreshing(true);
    setErrorMessage('');
    try {
      const questions = await getEnhancedQuestions(userId.trim());
      setEnhancedQuestions(mergeQuestions([], questions));
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Unable to refresh enhanced questions.'));
    } finally {
      setIsRefreshing(false);
    }
  }

  function handleDraftChange(questionId, value) {
    setDraftAnswers((current) => ({
      ...current,
      [questionId]: value,
    }));
  }

  async function handleAnswer(question) {
    const draft = (draftAnswers[question.question_id] || '').trim();
    if (!draft) {
      return;
    }

    setAnsweringQuestionId(question.question_id);
    setErrorMessage('');
    try {
      await answerEnhancedQuestion(question.question_id, draft);
      setEnhancedQuestions((current) =>
        current.map((item) =>
          item.question_id === question.question_id
            ? { ...item, status: 'answered', answer: draft }
            : item,
        ),
      );
      setDraftAnswers((current) => {
        const nextDrafts = { ...current };
        delete nextDrafts[question.question_id];
        return nextDrafts;
      });
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Unable to save the answer.'));
    } finally {
      setAnsweringQuestionId('');
    }
  }

  return (
    <div className="chat-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Legacy AI Chat Interface</p>
          <h1>Ask memory questions and fill missing context later.</h1>
          <p className="hero-copy">
            This interface lets family members talk to the Legacy AI backend, review referenced memories,
            and answer knowledge-gap prompts in a separate workflow.
          </p>
        </div>
        <div className="hero-stats">
          <div className="stat-tile">
            <span>Conversation turns</span>
            <strong>{history.length}</strong>
          </div>
          <div className="stat-tile accent">
            <span>Pending follow-ups</span>
            <strong>{pendingCount}</strong>
          </div>
        </div>
      </header>

      <main className="workspace-grid">
        <section className="chat-column">
          <form className="composer-card" onSubmit={handleAsk}>
            <div className="field-row">
              <label htmlFor="user-id">User ID</label>
              <input
                id="user-id"
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
                placeholder="family_user"
              />
            </div>
            <div className="field-row">
              <label htmlFor="question-text">Ask Legacy AI</label>
              <textarea
                id="question-text"
                value={questionText}
                onChange={(event) => setQuestionText(event.target.value)}
                placeholder="What do you remember about your first job?"
              />
            </div>
            <div className="action-row">
              <button className="primary-action" disabled={isSubmitting || !questionText.trim()} type="submit">
                {isSubmitting ? 'Asking...' : 'Send to /ask'}
              </button>
              <button
                className="ghost-action"
                disabled={isRefreshing || !userId.trim()}
                onClick={refreshEnhancedQuestions}
                type="button"
              >
                {isRefreshing ? 'Refreshing...' : 'Load Enhanced Questions'}
              </button>
            </div>
            {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}
          </form>

          <ConversationHistory history={history} />
        </section>

        <aside className="sidebar-column">
          <EnhancedQuestionsPanel
            questions={enhancedQuestions.filter((question) => question.status !== 'answered')}
            draftAnswers={draftAnswers}
            onDraftChange={handleDraftChange}
            onAnswer={handleAnswer}
            answeringQuestionId={answeringQuestionId}
          />
        </aside>
      </main>
    </div>
  );
}

function mergeQuestions(existing, incoming) {
  const questionMap = new Map(existing.map((question) => [question.question_id, question]));
  incoming.forEach((question) => {
    questionMap.set(question.question_id, question);
  });
  return Array.from(questionMap.values()).sort((left, right) =>
    left.source_conversation_timestamp.localeCompare(right.source_conversation_timestamp),
  );
}

function getErrorMessage(error, fallback) {
  return error?.response?.data?.detail || error?.message || fallback;
}
