export interface SubmitAnswerInput {
  question_id: string
  question_type: 'regular' | 'math'
  user_answer: string
}

export interface Review {
  id: string
  question_type: 'regular' | 'math'
  user_answer: string
  llm_feedback: string
  score: number | null
  is_correct?: boolean
  correct_answer?: number
}
