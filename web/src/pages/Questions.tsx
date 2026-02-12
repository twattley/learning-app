import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchQuestions, deleteQuestion, type Question } from "../lib/api";

export default function Questions() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [topicFilter, setTopicFilter] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchQuestions(topicFilter || undefined);
      setQuestions(data);
    } catch (err) {
      console.error("Failed to load questions", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [topicFilter]);

  const topics = [...new Set(questions.map((q) => q.topic))].sort();

  const handleDelete = async (e: React.MouseEvent, q: Question) => {
    e.stopPropagation();
    if (!confirm(`Delete "${q.question_text.slice(0, 50)}…"?`)) return;
    try {
      await deleteQuestion(q.id);
      setQuestions((prev) => prev.filter((x) => x.id !== q.id));
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
        <span className="count">
          {questions.length} question{questions.length !== 1 ? "s" : ""}
        </span>
      </div>

      {loading ? (
        <div className="center-state">
          <div className="spinner" />
        </div>
      ) : questions.length === 0 ? (
        <p className="empty-text">No questions yet. Click + New Question to get started.</p>
      ) : (
        <div className="question-grid">
          {questions.map((q) => (
            <div
              key={q.id}
              className="card question-card"
              onClick={() => navigate(`/questions/${q.id}/edit`)}
            >
              <div className="question-card-header">
                <span className="topic-badge">{q.topic}</span>
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
