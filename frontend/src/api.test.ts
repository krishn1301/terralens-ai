import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, sendChat } from './api'

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
