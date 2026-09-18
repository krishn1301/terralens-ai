import { BookOpenText, ExternalLink } from 'lucide-react'

import type { Evidence } from '../types'

export function EvidencePanel({ evidence }: { evidence: Evidence[] }) {
  return (
    <aside className="evidence-panel" aria-labelledby="evidence-title">
      <div className="panel-heading">
        <BookOpenText aria-hidden="true" size={18} />
        <div>
          <p className="eyebrow">Retrieved knowledge</p>
          <h2 id="evidence-title">Evidence ledger</h2>
        </div>
      </div>
      {evidence.length === 0 ? (
        <div className="evidence-empty">
          <p>Sources will appear here after an assessment.</p>
          <small>Each recommendation must resolve to at least one indexed record.</small>
        </div>
      ) : (
        <ol className="evidence-list">
          {evidence.map((item, index) => (
            <li key={item.id}>
              <div className="evidence-index">S{String(index + 1).padStart(2, '0')}</div>
              <a href={item.url} target="_blank" rel="noreferrer">
                {item.title}<ExternalLink aria-hidden="true" size={14} />
              </a>
              <p>{item.claim}</p>
              <div className="evidence-meta">
                <span>{item.organization}</span>
                <span>{item.year}</span>
                <span>{Math.round(item.relevance * 100)}% match</span>
              </div>
            </li>
          ))}
        </ol>
      )}
    </aside>
  )
}
