export interface Question {
  id: string
  question_text: string
  answer_text: string | null
  topic: string
  tags: string[]
  is_work: boolean
  question_type: 'regular' | 'math'
  template_type?: string
  hint?: string
  display_text?: string
  created_at: string
  updated_at: string
}

export interface CreateQuestionInput {
  question_text: string
  answer_text?: string
  topic: string
  tags?: string[]
  is_work?: boolean
}

export interface UpdateQuestionInput {
  question_text?: string
  answer_text?: string
  topic?: string
  tags?: string[]
  is_work?: boolean
}

export interface RefineInput {
  topic: string
  question: string
  answer: string
}

export interface RefineResult {
  question: string
  answer: string
}
