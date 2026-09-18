import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, it, vi } from 'vitest'

import App from './App'

const scenario = {
  id: 'semi-arid-farm',
  name: 'Semi-arid wheat farm',
  description: 'Low carbon and seasonal water stress.',
  prompt: 'How can this farm rebuild biodiversity?',
  profile: {
    land_use: 'monoculture wheat',
    soil_organic_carbon: 0.3,
    annual_rainfall_mm: 420,
    habitat_diversity: 2,
  },
}

afterEach(() => vi.restoreAllMocks())

it('loads a sample landscape into the structured profile', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify([scenario]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  )
  render(<App />)
  await userEvent.click(await screen.findByRole('button', { name: /semi-arid wheat farm/i }))
  expect(screen.getByLabelText(/soil organic carbon/i)).toHaveValue(0.3)
  expect(screen.getByLabelText(/land use/i)).toHaveValue('monoculture wheat')
})

it('renders recommendations, metrics, and evidence from an assessment', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch')
  fetchMock.mockResolvedValueOnce(
    new Response(JSON.stringify([scenario]), { status: 200, headers: { 'Content-Type': 'application/json' } }),
  )
  fetchMock.mockResolvedValueOnce(
    new Response(
      JSON.stringify({
        session_id: 's1',
        status: 'assessment',
        message: 'Reconnect habitat and rebuild soil function.',
        profile: scenario.profile,
        assessment: {
          summary: 'Reconnect habitat and rebuild soil function.',
          confidence: 0.84,
          recommendations: [
            {
              id: 'dryland-agroforestry',
              title: 'Use low-density agroforestry',
              action: 'Plant drought-adapted native trees on contours.',
              rationale: 'Water, carbon, and habitat structure interact.',
              contributing_variables: ['rainfall', 'soil carbon', 'land use'],
              impacts: [{ metric: 'soil organic carbon', direction: 'increase', expected_change: 'Long-term gain' }],
              time_horizon: 'long',
              confidence: 0.83,
              evidence_ids: ['ipcc-agroforestry-resilience'],
            },
          ],
          evidence: [
            {
              id: 'ipcc-agroforestry-resilience',
              organization: 'IPCC',
              title: 'AR6 WGII Chapter 5',
              year: 2022,
              url: 'https://www.ipcc.ch/',
              claim: 'Agroforestry provides biodiversity and carbon co-benefits.',
              metrics: ['soil_organic_carbon'],
              relevance: 0.95,
            },
          ],
          reasoning_trace: [{ label: 'Connect', explanation: 'Combined three interacting variables.' }],
          caveats: ['Validate with a local baseline.'],
        },
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    ),
  )

  render(<App />)
  await userEvent.click(await screen.findByRole('button', { name: /semi-arid wheat farm/i }))
  await userEvent.click(screen.getByRole('button', { name: /run grounded assessment/i }))
  expect(await screen.findByText('Use low-density agroforestry')).toBeInTheDocument()
  expect(screen.getAllByText(/soil organic carbon/i)).not.toHaveLength(0)
  expect(screen.getByRole('link', { name: /AR6 WGII Chapter 5/i })).toHaveAttribute('href')
})
