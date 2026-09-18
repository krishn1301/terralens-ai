import { SlidersHorizontal } from 'lucide-react'

import type { LandscapeProfile, PollutionLevel } from '../types'

interface Props {
  profile: LandscapeProfile
  onChange: (profile: LandscapeProfile) => void
}

const numericFields: Array<{
  key: keyof LandscapeProfile
  label: string
  unit: string
  min: number
  max: number
  step?: number
}> = [
  { key: 'soil_organic_carbon', label: 'Soil organic carbon', unit: '%', min: 0, max: 20, step: 0.1 },
  { key: 'soil_ph', label: 'Soil pH', unit: 'pH', min: 0, max: 14, step: 0.1 },
  { key: 'soil_moisture_pct', label: 'Soil moisture', unit: '%', min: 0, max: 100 },
  { key: 'annual_rainfall_mm', label: 'Annual rainfall', unit: 'mm', min: 0, max: 12000 },
  { key: 'mean_temperature_c', label: 'Mean temperature', unit: '°C', min: -50, max: 60, step: 0.1 },
  { key: 'species_richness', label: 'Observed species', unit: 'count', min: 0, max: 100000 },
  { key: 'habitat_diversity', label: 'Habitat diversity', unit: '/ 10', min: 1, max: 10 },
  { key: 'fragmentation_pct', label: 'Fragmented area', unit: '%', min: 0, max: 100 },
]

export function ProfilePanel({ profile, onChange }: Props) {
  const update = (key: keyof LandscapeProfile, value: string | number | undefined) =>
    onChange({ ...profile, [key]: value })

  return (
    <aside className="profile-panel" aria-labelledby="profile-title">
      <div className="panel-heading">
        <SlidersHorizontal aria-hidden="true" size={18} />
        <div>
          <p className="eyebrow">Structured input</p>
          <h2 id="profile-title">Landscape profile</h2>
        </div>
      </div>
      <p className="panel-intro">Add measured values when available. Empty fields are never guessed.</p>

      <div className="field-stack">
        <label className="field">
          <span>Region</span>
          <input
            value={profile.region ?? ''}
            onChange={(event) => update('region', event.target.value || undefined)}
            placeholder="e.g. Maharashtra, India"
            autoComplete="off"
          />
        </label>
        <label className="field">
          <span>Land use</span>
          <input
            value={profile.land_use ?? ''}
            onChange={(event) => update('land_use', event.target.value || undefined)}
            placeholder="e.g. monoculture wheat"
            autoComplete="off"
          />
        </label>
        {numericFields.map((field) => {
          const hintId = `${field.key}-hint`
          return (
            <label className="field metric-field" key={field.key}>
              <span>{field.label}</span>
              <span className="input-with-unit">
                <input
                  aria-describedby={hintId}
                  inputMode="decimal"
                  type="number"
                  min={field.min}
                  max={field.max}
                  step={field.step ?? 1}
                  value={(profile[field.key] as number | undefined) ?? ''}
                  onChange={(event) =>
                    update(field.key, event.target.value === '' ? undefined : Number(event.target.value))
                  }
                />
                <small id={hintId}>{field.unit}</small>
              </span>
            </label>
          )
        })}
        <label className="field">
          <span>Pollution pressure</span>
          <select
            value={profile.pollution_level ?? ''}
            onChange={(event) =>
              update('pollution_level', (event.target.value || undefined) as PollutionLevel | undefined)
            }
          >
            <option value="">Not measured</option>
            <option value="low">Low</option>
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
          </select>
        </label>
      </div>
    </aside>
  )
}
