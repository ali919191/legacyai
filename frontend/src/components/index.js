export function ConversationHistory({ history }) {
  if (!history.length) {
    return (
      <div className="empty-state">
        Start the conversation with a memory question. Responses, linked memories, and follow-up prompts will appear here.
      </div>
    );
  }

  return (
    <div className="conversation-history">
      {history.map((entry) => (
        <article className="conversation-card" key={entry.id}>
          <div className="message-bubble message-bubble-user">
            <span className="message-label">You asked</span>
            <p>{entry.question}</p>
          </div>
          <div className="message-bubble message-bubble-ai">
            <span className="message-label">Legacy AI replied</span>
            <p>{entry.answer}</p>
            <div className="memory-chips">
              {(entry.memoriesUsed || []).map((memoryId) => (
                <span className="memory-chip" key={memoryId}>
                  {memoryId}
                </span>
              ))}
              {!entry.memoriesUsed?.length && <span className="memory-chip muted">No memories referenced</span>}
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

export function EnhancedQuestionsPanel({
  questions,
  draftAnswers,
  onDraftChange,
  onAnswer,
  answeringQuestionId,
}) {
  return (
    <div className="enhanced-panel">
      <div className="panel-heading">
        <h2>Enhanced Questions</h2>
        <p>Answer these later to enrich missing people and story details without interrupting the main conversation.</p>
      </div>
      {!questions.length ? (
        <div className="empty-state compact">
          No pending enhanced questions yet.
        </div>
      ) : (
        <div className="question-list">
          {questions.map((question) => (
            <section className="question-card" key={question.question_id}>
              <div className="question-meta-row">
                <span className={`priority-pill priority-${question.priority}`}>{question.priority}</span>
                <span className="question-status">{question.status}</span>
              </div>
              <h3>{question.question}</h3>
              <p>{question.context_description}</p>
              <textarea
                className="answer-box"
                placeholder="Add the missing detail here"
                value={draftAnswers[question.question_id] || ''}
                onChange={(event) => onDraftChange(question.question_id, event.target.value)}
              />
              <button
                className="secondary-action"
                disabled={!draftAnswers[question.question_id]?.trim() || answeringQuestionId === question.question_id}
                onClick={() => onAnswer(question)}
              >
                {answeringQuestionId === question.question_id ? 'Saving...' : 'Save answer'}
              </button>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
