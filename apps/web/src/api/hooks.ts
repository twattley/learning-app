import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiFetch, apiPost, apiPut, apiDelete } from './http'
import type {
  Question,
  Review,
  LLMMode,
  CreateQuestionInput,
  UpdateQuestionInput,
  RefineInput,
  RefineResult,
  SubmitAnswerInput,
} from '@recall/domain-types'

export const useQuestions = (topic?: string, focus?: 'work') => {
  const params = new URLSearchParams()
  if (topic) params.set('topic', topic)
  if (focus) params.set('focus', focus)
  const qs = params.toString() ? `?${params}` : ''
  return useQuery<Question[]>({
    queryKey: ['questions', topic, focus],
    queryFn: () => apiFetch(`/questions${qs}`),
  })
}

export const useQuestion = (id: string) =>
  useQuery<Question>({
    queryKey: ['question', id],
    queryFn: () => apiFetch(`/questions/${id}`),
    enabled: !!id,
  })

export const useCreateQuestion = () => {
  const qc = useQueryClient()
  return useMutation<Question, Error, CreateQuestionInput>({
    mutationFn: (data) => apiPost('/questions', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['questions'] }),
  })
}

export const useUpdateQuestion = () => {
  const qc = useQueryClient()
  return useMutation<Question, Error, { id: string } & UpdateQuestionInput>({
    mutationFn: ({ id, ...data }) => apiPut(`/questions/${id}`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['questions'] }),
  })
}

export const useDeleteQuestion = () => {
  const qc = useQueryClient()
  return useMutation<void, Error, string>({
    mutationFn: (id) => apiDelete(`/questions/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['questions'] }),
  })
}

export const useRefineQuestion = () =>
  useMutation<RefineResult, Error, RefineInput>({
    mutationFn: (data) => apiPost('/questions/refine', data),
  })

export const useSubmitAnswer = () =>
  useMutation<Review, Error, SubmitAnswerInput>({
    mutationFn: (data) => apiPost('/learn/submit', data),
  })

export const useLLMMode = () =>
  useQuery<LLMMode>({
    queryKey: ['llm-mode'],
    queryFn: () => apiFetch('/settings/llm-mode'),
  })

export const useSetLLMMode = () => {
  const qc = useQueryClient()
  return useMutation<LLMMode, Error, string>({
    mutationFn: (mode) => apiPut('/settings/llm-mode', { mode }),
    onSuccess: (data) => qc.setQueryData(['llm-mode'], data),
  })
}
