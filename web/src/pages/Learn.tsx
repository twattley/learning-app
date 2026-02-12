import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import Calculator from "../components/Calculator";
import {
  fetchNextQuestion,
  submitAnswer,
  type Question,
  type Review,
} from "../lib/api";

type Phase = "loading" | "question" | "feedback" | "error" | "empty";

export default function Learn() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [question, setQuestion] = useState<Question | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [review, setReview] = useState<Review | null>(null);
  const [error, setError] = useState("");
  const [showHint, setShowHint] = useState(false);

  const loadQuestion = async () => {
    setPhase("loading");
    setUserAnswer("");
    setReview(null);
    setShowHint(false);
    try {
      const q = await fetchNextQuestion();
      setQuestion(q);
      setPhase("question");
    } catch (e: any) {
      if (e.message?.includes("404")) {
        setPhase("empty");
      } else {
        setError(e.message);
        setPhase("error");
      }
    }
  };

  const handleSubmit = async () => {
    if (!question || !userAnswer.trim()) return;
    setPhase("loading");
    try {
      const r = await submitAnswer({
        question_id: question.id,
        question_type: question.question_type || "regular",
        user_answer: userAnswer.trim(),
      });
      setReview(r);
      setPhase("feedback");
    } catch (e: any) {
      setError(e.message);
      setPhase("error");
    }
  };

  // Cmd+Enter / Ctrl+Enter to submit, or just Enter for math questions
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      handleSubmit();
    }
    // For math questions, Enter alone submits
    if (question?.question_type === "math" && e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    loadQuestion();
  }, []);

  const isMath = question?.question_type === "math";

  return (
    <div className="learn-container">
      {phase === "loading" && (
        <div className="center-state">
          <div className="spinner" />
        </div>
      )}

      {phase === "empty" && (
        <div className="center-state">
          <p>No questions yet.</p>
          <p style={{ marginTop: 8 }}>Add some in the Questions tab to get started.</p>
        </div>
      )}

      {phase === "error" && (
        <div className="center-state">
          <p style={{ color: "#f87171", fontWeight: 600, marginBottom: 8 }}>Something went wrong</p>
          <p style={{ fontSize: 13, marginBottom: 16, maxWidth: 500, textAlign: "center" }}>{error}</p>
          <button className="btn btn-primary" onClick={loadQuestion}>Try Again</button>
        </div>
      )}

      {phase === "question" && question && (
        <div>
          <div style={{ marginBottom: 16, display: "flex", gap: 8, alignItems: "center" }}>
            <span className="topic-badge">{question.topic}</span>
            {isMath && (
              <span className="topic-badge" style={{ background: "#7c3aed" }}>
                Math
              </span>
            )}
          </div>

          <div className="md-content" style={{ fontSize: 18, lineHeight: 1.6, marginBottom: 20 }}>
            <ReactMarkdown components={markdownComponents}>
              {question.display_text ?? question.question_text ?? ""}
            </ReactMarkdown>
          </div>

          {isMath && (
            <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "flex-start" }}>
              <Calculator onUseResult={(result) => setUserAnswer(result)} />
              {question.hint && !showHint && (
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={() => setShowHint(true)}
                >
                  💡 Show Hint
                </button>
              )}
            </div>
          )}

          {showHint && question.hint && (
            <div className="hint-card" style={{
              background: "var(--surface)",
              border: "1px solid #6366f1",
              borderRadius: "var(--radius)",
              padding: 16,
              marginBottom: 16,
            }}>
              <div style={{ fontSize: 12, color: "#a5b4fc", marginBottom: 8, fontWeight: 600 }}>
                💡 HINT
              </div>
              <div className="md-content" style={{ fontSize: 14 }}>
                <ReactMarkdown components={markdownComponents}>
                  {question.hint}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {isMath ? (
            <input
              type="text"
              inputMode="decimal"
              className="answer-input"
              placeholder="Enter your answer (number)…"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
              style={{ fontFamily: "monospace", fontSize: 18 }}
            />
          ) : (
            <textarea
              className="answer-input"
              placeholder="Type your answer…"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
            />
          )}

          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <button
              className="btn btn-primary"
              disabled={!userAnswer.trim()}
              onClick={handleSubmit}
            >
              Submit
            </button>
            <span className="form-hint">
              {isMath ? "Enter to submit" : "Cmd+Enter to submit"}
            </span>
          </div>
        </div>
      )}

      {phase === "feedback" && review && (
        <div>
          {review.question_type === "math" ? (
            <div className="score-row">
              <span className="score-label">Result</span>
              <span 
                className="score-value" 
                style={{ color: review.is_correct ? "#4ade80" : "#f87171" }}
              >
                {review.is_correct ? "✓ Correct!" : "✗ Incorrect"}
              </span>
              {review.correct_answer != null && !review.is_correct && (
                <span style={{ marginLeft: 16, color: "#94a3b8", fontSize: 14 }}>
                  Correct answer: <strong style={{ color: "#f8fafc" }}>{review.correct_answer.toPrecision(4)}</strong>
                </span>
              )}
            </div>
          ) : (
            <div className="score-row">
              <span className="score-label">Score</span>
              <span className="score-value">
                {review.score != null ? `${review.score}/5` : "—"}
              </span>
            </div>
          )}

          <div className="feedback-card md-content">
            <ReactMarkdown components={markdownComponents}>
              {review.llm_feedback}
            </ReactMarkdown>
          </div>

          <button className="btn btn-primary" onClick={loadQuestion}>
            Next Question →
          </button>
        </div>
      )}
    </div>
  );
}

// Custom components for react-markdown with syntax highlighting
const markdownComponents = {
  code({ className, children, ...props }: any) {
    const match = /language-(\w+)/.exec(className || "");
    const inline = !match && !className;

    if (inline) {
      return <code style={{ background: "#334155", padding: "2px 6px", borderRadius: 4, fontSize: "0.9em" }} {...props}>{children}</code>;
    }

    return (
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={match?.[1] || "text"}
        PreTag="div"
        customStyle={{
          background: "#0f172a",
          border: "1px solid #334155",
          borderRadius: 8,
          padding: 14,
          margin: "12px 0",
          fontSize: 13,
        }}
        {...props}
      >
        {String(children).replace(/\n$/, "")}
      </SyntaxHighlighter>
    );
  },
};
