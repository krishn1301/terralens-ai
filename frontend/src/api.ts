import type { ChatRequest, ChatResponse, Scenario } from './types'

export function apiBaseUrl(configured: string | undefined): string {
  const value = configured?.trim()
  return value ? value.replace(/\/+$/, '') : 'http://localhost:8000'
}

const API_URL = apiBaseUrl(import.meta.env.VITE_API_URL)

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request(path: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(`${API_URL}${path}`, init)
  } catch {
    throw new ApiError(
      'The assessment service could not be reached. It may be waking up; your inputs are still here, so try again shortly.',
    )
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
  return parse<Scenario[]>(await request('/api/scenarios'))
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  return parse<ChatResponse>(
    await request('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  )
}
