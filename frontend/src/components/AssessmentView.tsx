import { ArrowDown, ArrowUp, Clock3, Gauge, Minus, Quote } from 'lucide-react'

import type { Assessment } from '../types'

const directionIcon = {
  increase: ArrowUp,
  decrease: ArrowDown,
  stabilize: Minus,
}

export function AssessmentView({ assessment }: { assessment: Assessment }) {
  return (
    <div className="assessment" data-testid="assessment">
      <div className="assessment-summary">
        <p className="eyebrow">Field synthesis</p>
        <p>{assessment.summary}</p>
        <div className="confidence-line">
          <Gauge aria-hidden="true" size={18} />
          <span>Assessment confidence</span>
          <strong>{Math.round(assessment.confidence * 100)}%</strong>
        </div>
      </div>

      <section aria-labelledby="actions-title">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Prioritized actions</p>
            <h2 id="actions-title">Interventions with compound impact</h2>
          </div>
          <span className="count-mark">{assessment.recommendations.length}</span>
        </div>
        <div className="recommendation-list">
          {assessment.recommendations.map((item, index) => (
            <article className="recommendation" key={item.id}>
              <div className="recommendation-number">{String(index + 1).padStart(2, '0')}</div>
              <div className="recommendation-body">
                <div className="recommendation-meta">
                  <span><Clock3 aria-hidden="true" size={15} /> {item.time_horizon} term</span>
                  <span>{Math.round(item.confidence * 100)}% confidence</span>
                </div>
                <h3>{item.title}</h3>
                <p className="action-copy">{item.action}</p>
                <p className="rationale"><Quote aria-hidden="true" size={16} />{item.rationale}</p>
                <div className="variable-row" aria-label="Contributing variables">
                  {item.contributing_variables.map((variable) => <span key={variable}>{variable}</span>)}
                </div>
                <dl className="impact-list">
                  {item.impacts.map((impact) => {
                    const Icon = directionIcon[impact.direction as keyof typeof directionIcon] ?? Minus
                    return (
                      <div key={`${item.id}-${impact.metric}`}>
                        <dt><Icon aria-hidden="true" size={16} />{impact.metric}</dt>
                        <dd>{impact.expected_change}</dd>
                      </div>
                    )
                  })}
                </dl>
              </div>
            </article>
          ))}
        </div>
      </section>

      <details className="reasoning-disclosure">
        <summary>Inspect the reasoning trace</summary>
        <ol>
          {assessment.reasoning_trace.map((step) => (
            <li key={step.label}><strong>{step.label}</strong><p>{step.explanation}</p></li>
          ))}
        </ol>
      </details>

      <section className="caveats" aria-labelledby="caveats-title">
        <h2 id="caveats-title">Field notes before implementation</h2>
        <ul>{assessment.caveats.map((caveat) => <li key={caveat}>{caveat}</li>)}</ul>
      </section>
    </div>
  )
}
