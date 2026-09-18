export type PollutionLevel = 'low' | 'moderate' | 'high'

export interface LandscapeProfile {
  region?: string
  biome?: string
  land_use?: string
  soil_organic_carbon?: number
  soil_ph?: number
  soil_moisture_pct?: number
  annual_rainfall_mm?: number
  mean_temperature_c?: number
  species_richness?: number
  habitat_diversity?: number
  fragmentation_pct?: number
  pollution_level?: PollutionLevel
}

export interface Scenario {
  id: string
  name: string
  description: string
  prompt: string
  profile: LandscapeProfile
}

export interface Evidence {
  id: string
  organization: string
  title: string
  year: number
  url: string
  claim: string
  metrics: string[]
  relevance: number
}

export interface Recommendation {
  id: string
  title: string
  action: string
  rationale: string
  contributing_variables: string[]
  impacts: Array<{ metric: string; direction: string; expected_change: string }>
  time_horizon: 'short' | 'medium' | 'long'
  confidence: number
  evidence_ids: string[]
}

export interface Assessment {
  summary: string
  confidence: number
  recommendations: Recommendation[]
  evidence: Evidence[]
  reasoning_trace: Array<{ label: string; explanation: string }>
  caveats: string[]
}

export interface ChatResponse {
  session_id: string
  status: 'clarification' | 'assessment'
  message: string
  profile: LandscapeProfile
  clarification?: { question: string; missing_fields: string[]; known_context: string[] }
  assessment?: Assessment
}

export interface ChatRequest {
  session_id?: string
  message?: string
  profile?: LandscapeProfile
}
