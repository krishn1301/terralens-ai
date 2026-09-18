import { Download, Leaf, RotateCcw, Send, Sparkles } from 'lucide-react'
import { FormEvent, useEffect, useState } from 'react'

import { getScenarios, sendChat } from './api'
import { AssessmentView } from './components/AssessmentView'
import { EvidencePanel } from './components/EvidencePanel'
import { ProfilePanel } from './components/ProfilePanel'
import { ScenarioRail } from './components/ScenarioRail'
import type { ChatResponse, LandscapeProfile, Scenario } from './types'

function App() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [scenarioState, setScenarioState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [selectedId, setSelectedId] = useState<string>()
  const [profile, setProfile] = useState<LandscapeProfile>({})
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState<ChatResponse>()
  const [sessionId, setSessionId] = useState<string>()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    getScenarios()
      .then((items) => {
        if (active) {
          setScenarios(items)
          setScenarioState('ready')
        }
      })
      .catch(() => active && setScenarioState('error'))
    return () => { active = false }
  }, [])

  const retryScenarios = () => {
    setScenarioState('loading')
    getScenarios()
      .then((items) => {
        setScenarios(items)
        setScenarioState('ready')
      })
      .catch(() => setScenarioState('error'))
  }

  const chooseScenario = (scenario: Scenario) => {
    setSelectedId(scenario.id)
    setProfile(scenario.profile)
    setPrompt(scenario.prompt)
    setResponse(undefined)
    setError(null)
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!prompt.trim() && Object.keys(profile).length === 0) {
      setError('Describe the issue or add at least one landscape metric before assessment.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const next = await sendChat({ session_id: sessionId, message: prompt.trim() || undefined, profile })
      setResponse(next)
      setSessionId(next.session_id)
      setProfile(next.profile)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'The assessment could not be completed. Try again.')
    } finally {
      setBusy(false)
    }
  }

  const reset = () => {
    setSelectedId(undefined)
    setProfile({})
    setPrompt('')
    setResponse(undefined)
    setSessionId(undefined)
    setError(null)
  }

  const exportAssessment = () => {
    if (!response?.assessment) return
    const body = JSON.stringify(response, null, 2)
    const url = URL.createObjectURL(new Blob([body], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'terralens-assessment.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <>
      <a className="skip-link" href="#workspace">Skip to assessment workspace</a>
      <div className="app-shell">
        <ScenarioRail
          scenarios={scenarios}
          loading={scenarioState === 'loading'}
          error={scenarioState === 'error' ? 'Field cases could not be loaded.' : null}
          selectedId={selectedId}
          profile={profile}
          onSelect={chooseScenario}
          onRetry={retryScenarios}
        />

        <main id="workspace" className="workspace" tabIndex={-1}>
          <header className="workspace-header">
            <div className="status-line"><span aria-hidden="true" />Local evidence engine ready</div>
            <div className="header-actions">
              <button className="quiet-button" onClick={reset}><RotateCcw aria-hidden="true" size={16} />New case</button>
              <button className="quiet-button" onClick={exportAssessment} disabled={!response?.assessment}>
                <Download aria-hidden="true" size={16} />Export JSON
              </button>
            </div>
          </header>

          <section className="conversation" aria-labelledby="conversation-title">
            <div className="conversation-title-row">
              <div>
                <p className="eyebrow">Environmental scientist / grounded mode</p>
                <h2 id="conversation-title">Biodiversity assessment</h2>
              </div>
              <Leaf aria-hidden="true" size={28} />
            </div>

            {!response && !selectedId && (
              <div className="first-use">
                <Sparkles aria-hidden="true" size={22} />
                <h2>Start with a field case or your own measurements.</h2>
                <p>I will ask for missing signals before recommending anything. No value is silently assumed.</p>
              </div>
            )}

            {response?.status === 'clarification' && response.clarification && (
              <section className="clarification" aria-labelledby="clarification-title">
                <p className="eyebrow">More context needed</p>
                <h2 id="clarification-title">{response.clarification.question}</h2>
                <p>Known context: {response.clarification.known_context.join(' · ') || 'No measured values yet'}</p>
              </section>
            )}

            {response?.assessment && <AssessmentView assessment={response.assessment} />}

            {busy && (
              <div className="response-skeleton" aria-label="Building grounded assessment" aria-live="polite">
                <span /><span /><span />
              </div>
            )}
            <div className="sr-only" aria-live="polite" aria-atomic="true">
              {busy ? 'Assessment in progress' : response ? `${response.status} received` : ''}
            </div>
            {error && <div className="persistent-error" role="alert"><p>{error}</p><span>Your profile and message have been preserved.</span></div>}
          </section>

          <form className="composer" onSubmit={submit}>
            <label htmlFor="question">What is changing on this land?</label>
            <textarea
              id="question"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Describe the decline, pressure, or outcome you need..."
              rows={3}
            />
            <div className="composer-footer">
              <span>Text + structured JSON profile · evidence required</span>
              <button className="primary-button" type="submit" aria-busy={busy} disabled={busy}>
                <Send aria-hidden="true" size={17} />{busy ? 'Grounding evidence…' : 'Run grounded assessment'}
              </button>
            </div>
          </form>
        </main>

        <div className="right-rail">
          <ProfilePanel profile={profile} onChange={setProfile} />
          <EvidencePanel evidence={response?.assessment?.evidence ?? []} />
        </div>
      </div>
    </>
  )
}

export default App
