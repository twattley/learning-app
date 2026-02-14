const API_BASE = "/api/v1";

export interface Question {
  id: string;
  question_text?: string;
  answer_text?: string | null;
  topic: string;
  created_at: string;
  updated_at?: string;
  display_text?: string;
  question_type: "regular" | "math";
  template_type?: string;  // For math questions
  hint?: string;           // Formula hint for math questions
}

export interface Review {
  id: string;
  question_type: "regular" | "math";
  user_answer: string;
  llm_feedback: string;
  score: number | null;       // For regular questions
  is_correct?: boolean;       // For math questions
  correct_answer?: number;    // For math questions (revealed after submission)
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Questions ──

export function fetchQuestions(topic?: string): Promise<Question[]> {
  const qs = topic ? `?topic=${encodeURIComponent(topic)}` : "";
  return request(`/questions${qs}`);
}

export function getQuestion(id: string): Promise<Question> {
  return request(`/questions/${id}`);
}

export function createQuestion(data: {
  question_text: string;
  answer_text?: string;
  topic: string;
}): Promise<Question> {
  return request("/questions", { method: "POST", body: JSON.stringify(data) });
}

export function updateQuestion(
  id: string,
  data: { question_text?: string; answer_text?: string; topic?: string }
): Promise<Question> {
  return request(`/questions/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteQuestion(id: string): Promise<void> {
  return request(`/questions/${id}`, { method: "DELETE" });
}

export function refineQuestion(data: {
  topic: string;
  question: string;
  answer: string;
}): Promise<{ question: string; answer: string }> {
  return request("/questions/refine", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ── Learning ──

export function fetchNextQuestion(topic?: string): Promise<Question> {
  const qs = topic ? `?topic=${encodeURIComponent(topic)}` : "";
  return request(`/learn/next${qs}`);
}

export function submitAnswer(data: {
  question_id: string;
  question_type: "regular" | "math";
  user_answer: string;
}): Promise<Review> {
  return request("/learn/submit", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ── LLM Mode ──

export interface LLMMode {
  mode: string;
  provider: string;
  model: string;
}

export function getLLMMode(): Promise<LLMMode> {
  return request("/settings/llm-mode");
}

export function setLLMMode(mode: string): Promise<LLMMode> {
  return request("/settings/llm-mode", {
    method: "PUT",
    body: JSON.stringify({ mode }),
  });
}
