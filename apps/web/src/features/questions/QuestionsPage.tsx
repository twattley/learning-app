import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useQuestions, useDeleteQuestion } from "../../api/hooks";
import type { Question } from "@recall/domain-types";

export default function QuestionsPage() {
  const navigate = useNavigate();
  const [topicFilter, setTopicFilter] = useState("");
  const [workOnly, setWorkOnly] = useState(false);

  const { data: questions = [], isLoading } = useQuestions(
    topicFilter || undefined,
    workOnly ? "work" : undefined,
  );
  const deleteQuestionMutation = useDeleteQuestion();

  const topics = [...new Set(questions.map((q: Question) => q.topic))].sort();

  const handleDelete = async (e: React.MouseEvent, q: Question) => {
    e.stopPropagation();
    const preview = (q.question_text ?? "").slice(0, 50);
    if (!confirm(`Delete "${preview}…"?`)) return;
    try {
      await deleteQuestionMutation.mutateAsync(q.id);
    } catch {
      alert("Failed to delete question");
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Questions</h1>
        <button className="btn btn-primary" onClick={() => navigate("/questions/new")}>
          + New Question
        </button>
      </div>

      <div className="filter-bar">
        <select value={topicFilter} onChange={(e) => setTopicFilter(e.target.value)}>
          <option value="">All topics</option>
          {topics.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="checkbox"
            checked={workOnly}
            onChange={(e) => setWorkOnly(e.target.checked)}
          />
          Work only
        </label>
        <span className="count">
          {questions.length} question{questions.length !== 1 ? "s" : ""}
        </span>
      </div>

      {isLoading ? (
        <div className="center-state">
          <div className="spinner" />
        </div>
      ) : questions.length === 0 ? (
        <p className="empty-text">No questions yet. Click + New Question to get started.</p>
      ) : (
        <div className="question-grid">
          {questions.map((q: Question) => (
            <div
              key={q.id}
              className="card question-card"
              onClick={() => navigate(`/questions/${q.id}/edit`)}
            >
              <div className="question-card-header">
                <span className="topic-badge">{q.topic}</span>
                {(q.is_work || q.tags?.includes("work")) && (
                  <span className="topic-badge" style={{ background: "#2563eb" }}>work</span>
                )}
                {q.answer_text == null && <span className="no-answer">no reference answer</span>}
              </div>
              <div className="question-preview">{q.question_text}</div>
              <div className="card-actions">
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={(e) => { e.stopPropagation(); navigate(`/questions/${q.id}/edit`); }}
                >
                  Edit
                </button>
                <button
                  className="btn btn-sm btn-danger"
                  onClick={(e) => handleDelete(e, q)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
