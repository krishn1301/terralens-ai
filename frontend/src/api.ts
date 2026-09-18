import type { ChatRequest, ChatResponse, Scenario } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message =
      response.status >= 500
        ? 'The assessment service is unavailable. Your inputs are still here.'
        : 'The request could not be completed. Check the highlighted inputs and try again.'
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

export async function getScenarios(): Promise<Scenario[]> {
  return parse<Scenario[]>(await fetch(`${API_URL}/api/scenarios`))
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  return parse<ChatResponse>(
    await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  )
}
