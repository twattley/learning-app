import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  getQuestion,
  createQuestion,
  updateQuestion,
  refineQuestion,
} from "../lib/api";

export default function QuestionForm() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const isEditing = !!id;

  const [topic, setTopic] = useState("");
  const [tagsText, setTagsText] = useState("");
  const [isWork, setIsWork] = useState(false);
  const [questionText, setQuestionText] = useState("");
  const [answerText, setAnswerText] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refining, setRefining] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getQuestion(id)
      .then((q) => {
        setTopic(q.topic);
        const existingTags = q.tags ?? [];
        setTagsText(existingTags.filter((tag) => tag !== "work").join(", "));
        setIsWork(q.is_work ?? existingTags.includes("work"));
        setQuestionText(q.question_text ?? "");
        setAnswerText(q.answer_text ?? "");
      })
      .catch(() => alert("Failed to load question"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSave = async () => {
    if (!topic.trim() || !questionText.trim()) {
      alert("Topic and question are required.");
      return;
    }
    setSaving(true);
    try {
      const parsedTags = tagsText
        .split(",")
        .map((tag) => tag.trim().toLowerCase())
        .filter(Boolean);

      if (parsedTags.length > 2) {
        alert("Please use up to 2 tags.");
        setSaving(false);
        return;
      }

      const data = {
        question_text: questionText.trim(),
        answer_text: answerText.trim() || undefined,
        topic: topic.trim().toLowerCase(),
        tags: parsedTags,
        is_work: isWork,
      };

      if (isEditing) {
        await updateQuestion(id!, data);
      } else {
        await createQuestion(data as any);
      }
      navigate("/questions");
    } catch {
      alert("Failed to save question");
    } finally {
      setSaving(false);
    }
  };

  const handleRefine = async () => {
    if (!questionText.trim()) {
      alert("Enter a question first.");
      return;
    }
    setRefining(true);
    try {
      const result = await refineQuestion({
        topic: topic.trim() || "general",
        question: questionText.trim(),
        answer: answerText.trim(),
      });
      setQuestionText(result.question);
      setAnswerText(result.answer);
    } catch {
      alert("Failed to refine question");
    } finally {
      setRefining(false);
    }
  };

  // Handle Tab key in textareas to insert spaces
  const handleTab = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const el = e.currentTarget;
      const start = el.selectionStart;
      el.value =
        el.value.substring(0, start) +
        "  " +
        el.value.substring(el.selectionEnd);
      el.selectionStart = el.selectionEnd = start + 2;
    }
  };

  // Cmd+Enter / Ctrl+Enter to save
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      handleSave();
    }
  };

  if (loading) {
    return (
      <div className="center-state">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 700 }} onKeyDown={handleKeyDown}>
      <div className="page-header">
        <h1>{isEditing ? "Edit Question" : "New Question"}</h1>
      </div>

      <div className="form-group">
        <label>Topic</label>
        <input
          className="input"
          type="text"
          placeholder="e.g. python, sql, networking"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          autoFocus
        />
      </div>

      <div className="form-group">
        <label>Tags (optional, up to 2)</label>
        <input
          className="input"
          type="text"
          placeholder="e.g. backend, cert-prep"
          value={tagsText}
          onChange={(e) => setTagsText(e.target.value)}
        />
        <div className="form-hint">Comma-separated. "work" is controlled by the toggle below.</div>
      </div>

      <div className="form-group" style={{ marginTop: 8 }}>
        <label style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <input
            type="checkbox"
            checked={isWork}
            onChange={(e) => setIsWork(e.target.checked)}
          />
          Mark as work question
        </label>
      </div>

      <div className="form-group">
        <label>Question</label>
        <textarea
          className="textarea"
          placeholder="Supports markdown — use ```lang for code blocks"
          value={questionText}
          onChange={(e) => setQuestionText(e.target.value)}
          onKeyDown={handleTab}
        />
        <div className="form-hint">
          Markdown supported. Use triple backticks for code blocks. Cmd+Enter to
          save.
        </div>
      </div>

      <div className="form-group">
        <label>
          Reference Answer <span className="optional">(optional)</span>
        </label>
        <textarea
          className="textarea"
          placeholder="The ideal answer — leave blank to let the LLM grade solo"
          value={answerText}
          onChange={(e) => setAnswerText(e.target.value)}
          onKeyDown={handleTab}
        />
        <div className="form-hint">Markdown supported.</div>
      </div>

      <div style={{ marginTop: 16, marginBottom: 8 }}>
        <button
          className="btn btn-secondary"
          disabled={refining || !questionText.trim()}
          onClick={handleRefine}
          style={{
            background: "#6366f1",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          {refining ? (
            <>
              <span
                className="spinner"
                style={{ width: 14, height: 14, borderWidth: 2 }}
              />
              Refining…
            </>
          ) : (
            <>✨ Refine with Gemini</>
          )}
        </button>
        <div className="form-hint" style={{ marginTop: 6 }}>
          Polish the question and expand the answer using AI
        </div>
      </div>

      <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
        <button
          className="btn btn-secondary"
          onClick={() => navigate("/questions")}
        >
          Cancel
        </button>
        <button
          className="btn btn-primary"
          disabled={saving}
          onClick={handleSave}
        >
          {saving ? "Saving…" : isEditing ? "Update" : "Create"}
        </button>
      </div>
    </div>
  );
}
