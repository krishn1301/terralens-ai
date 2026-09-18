import { ArrowUpRight, FlaskConical } from 'lucide-react'

import type { LandscapeProfile, Scenario } from '../types'

interface Props {
  scenarios: Scenario[]
  loading: boolean
  error: string | null
  selectedId?: string
  profile: LandscapeProfile
  onSelect: (scenario: Scenario) => void
  onRetry: () => void
}

const pulseMetrics: Array<[keyof LandscapeProfile, string]> = [
  ['soil_organic_carbon', 'Carbon'],
  ['annual_rainfall_mm', 'Water'],
  ['habitat_diversity', 'Habitats'],
  ['species_richness', 'Species'],
  ['fragmentation_pct', 'Continuity'],
  ['pollution_level', 'Pressure'],
]

export function ScenarioRail(props: Props) {
  const known = pulseMetrics.filter(([key]) => props.profile[key] !== undefined)
  return (
    <aside className="scenario-rail" aria-labelledby="scenarios-title">
      <div className="brand-mark" aria-hidden="true"><span>T</span></div>
      <p className="eyebrow">TerraLens field lab</p>
      <h1>Read the land.<br />Restore its living systems.</h1>
      <p className="lede">Evidence-grounded biodiversity intelligence that shows its work.</p>

      <section className="pulse" aria-labelledby="pulse-title">
        <div className="section-label">
          <span id="pulse-title">Landscape pulse</span>
          <span>{known.length}/6 signals</span>
        </div>
        <ol>
          {pulseMetrics.map(([key, label]) => (
            <li className={props.profile[key] !== undefined ? 'is-known' : ''} key={key}>
              <span className="pulse-dot" aria-hidden="true" />
              <span>{label}</span>
              <strong>{props.profile[key] !== undefined ? 'observed' : 'open'}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="scenario-list" aria-labelledby="scenarios-title">
        <div className="section-label">
          <span id="scenarios-title">Field cases</span>
          <FlaskConical aria-hidden="true" size={16} />
        </div>
        {props.loading && <div className="scenario-skeleton" aria-label="Loading field cases" />}
        {props.error && (
          <div className="rail-error" role="alert">
            <p>{props.error}</p>
            <button className="text-button" onClick={props.onRetry}>Retry field cases</button>
          </div>
        )}
        {!props.loading && !props.error && props.scenarios.length === 0 && (
          <p className="muted">No sample cases are available. You can still enter your own landscape.</p>
        )}
        {props.scenarios.map((scenario, index) => (
          <button
            className="scenario-button"
            aria-pressed={props.selectedId === scenario.id}
            key={scenario.id}
            onClick={() => props.onSelect(scenario)}
          >
            <span className="scenario-index">0{index + 1}</span>
            <span>
              <strong>{scenario.name}</strong>
              <small>{scenario.description}</small>
            </span>
            <ArrowUpRight aria-hidden="true" size={16} />
          </button>
        ))}
      </section>
    </aside>
  )
}
