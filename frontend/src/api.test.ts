import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, apiBaseUrl, sendChat } from './api'

describe('sendChat', () => {
  afterEach(() => vi.restoreAllMocks())

  it('posts a typed assessment request to the API', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ session_id: 's1', status: 'clarification' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    await sendChat({ message: 'Assess this landscape' })
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/chat'),
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('turns server failures into a recoverable product error', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('Unavailable', { status: 503 }))
    await expect(sendChat({ message: 'Assess this landscape' })).rejects.toEqual(
      new ApiError('The assessment service is unavailable. Your inputs are still here.', 503),
    )
  })
})

describe('network resilience', () => {
  afterEach(() => vi.restoreAllMocks())

  it('turns unreachable-service failures into a recoverable product error', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))
    await expect(sendChat({ message: 'Assess this landscape' })).rejects.toEqual(
      new ApiError(
        'The assessment service could not be reached. It may be waking up; your inputs are still here, so try again shortly.',
      ),
    )
  })
})

describe('apiBaseUrl', () => {
  it('uses the configured origin without a trailing slash', () => {
    expect(apiBaseUrl('https://api.example.org/')).toBe('https://api.example.org')
  })

  it('falls back to the local API when nothing is configured', () => {
    expect(apiBaseUrl(undefined)).toBe('http://localhost:8000')
    expect(apiBaseUrl('  ')).toBe('http://localhost:8000')
  })
})
