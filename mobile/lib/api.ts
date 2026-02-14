import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL_KEY = "api_base_url";
const DEFAULT_API_URL = "http://server:8003/api/v1";

let cachedApiUrl: string | null = null;

async function getApiBase(): Promise<string> {
  if (cachedApiUrl) return cachedApiUrl;
  const stored = await AsyncStorage.getItem(API_URL_KEY);
  cachedApiUrl = stored ?? DEFAULT_API_URL;
  return cachedApiUrl;
}

export function clearApiCache() {
  cachedApiUrl = null;
}

export interface Question {
  id: string;
  question_text: string;
  answer_text: string | null;
  topic: string;
  created_at: string;
  updated_at: string;
  display_text?: string;
  question_type?: string;
}

export interface Review {
  id: string;
  question_id: string;
  user_answer: string;
  llm_feedback: string;
  score: number | null;
  created_at: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const apiBase = await getApiBase();
  const res = await fetch(`${apiBase}${path}`, {
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

// ── Learning ──

export function fetchNextQuestion(topic?: string): Promise<Question> {
  const qs = topic ? `?topic=${encodeURIComponent(topic)}` : "";
  return request(`/learn/next${qs}`);
}

export function submitAnswer(data: {
  question_id: string;
  question_type: string;
  user_answer: string;
}): Promise<Review> {
  return request("/learn/submit", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
