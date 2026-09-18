# TerraLens AI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a keyless, evidence-grounded biodiversity intelligence application that demonstrates retrieval, multi-metric reasoning, clarification, memory, and a polished reviewer experience.

**Architecture:** A Vite React/TypeScript client consumes a FastAPI API. The backend indexes a curated structured corpus in SQLite FTS5, combines retrieval with deterministic environmental rules, and stores short-lived conversation sessions in memory. Docker Compose runs both services and GitHub Actions verifies backend and frontend changes.

**Tech Stack:** React 19, TypeScript, Vite, Vitest, FastAPI, Pydantic, SQLite FTS5, pytest, Playwright, Docker, GitHub Actions.

---

## File map

- `backend/app/models.py`: request and response contracts.
- `backend/app/knowledge.py`: evidence loading and FTS retrieval.
- `backend/app/reasoning.py`: clarification, interaction rules, scoring, recommendations.
- `backend/app/sessions.py`: bounded in-memory conversation state.
- `backend/app/main.py`: HTTP endpoints and error translation.
- `backend/data/evidence.json`: traceable scientific knowledge corpus.
- `frontend/src/api.ts`: typed API transport.
- `frontend/src/App.tsx`: workspace orchestration and state.
- `frontend/src/components/*`: focused interface components.
- `frontend/src/styles.css`: tokens, responsive layout, states, accessibility.
- `tests/`: backend and browser behavior.
- `.github/workflows/ci.yml`: repeatable verification.

### Task 1: Repository foundation

- [ ] Create repository metadata, environment example, ignore rules, backend and frontend package manifests.
- [ ] Add Dockerfiles and Compose services with health checks.
- [ ] Run dependency installation and record exact local commands in the README.
- [ ] Commit with `chore: scaffold TerraLens AI`.

### Task 2: Model contracts through TDD

- [ ] Write failing tests for profile bounds, text-or-structured input, response evidence IDs, and confidence ranges.
- [ ] Run `pytest backend/tests/test_models.py -q` and confirm the model imports fail.
- [ ] Implement Pydantic models for `LandscapeProfile`, `ChatRequest`, `Evidence`, `Recommendation`, `ReasoningStep`, and `ChatResponse`.
- [ ] Rerun the model tests and confirm zero failures.
- [ ] Commit with `feat: define environmental assessment contracts`.

### Task 3: Evidence corpus and retrieval through TDD

- [ ] Create curated records from FAO, IPCC, IPBES, USDA, and peer-reviewed synthesis sources with URLs and conservative quantified ranges.
- [ ] Write failing retrieval tests for soil carbon, semi-arid water stress, habitat connectivity, pollution, and agroforestry queries.
- [ ] Implement corpus validation, SQLite FTS5 indexing, term expansion, metric filters, and deterministic ranking.
- [ ] Verify every returned result contains a resolvable source URL and metric tags.
- [ ] Commit with `feat: add traceable biodiversity knowledge retrieval`.

### Task 4: Multi-metric reasoning through TDD

- [ ] Write failing tests proving fewer than three variables trigger targeted clarification.
- [ ] Write failing tests for semi-arid monoculture, acidic wet land, fragmented habitat, and polluted riparian scenarios.
- [ ] Implement interaction rules, suitability guards, measurable impact estimates, time horizons, caveats, and confidence calculation.
- [ ] Ensure no recommendation is emitted without supporting evidence and three contributing variables.
- [ ] Commit with `feat: reason across environmental metrics`.

### Task 5: Session-aware API through TDD

- [ ] Write failing API tests for health, new sessions, clarification continuation, JSON input, invalid values, and reset.
- [ ] Implement bounded session memory and merge follow-up values into the active landscape profile.
- [ ] Expose `/api/health`, `/api/scenarios`, `/api/chat`, `/api/sessions/{id}`, and session reset routes.
- [ ] Add CORS, consistent problem responses, request IDs, and safe error messages.
- [ ] Commit with `feat: expose conversational assessment API`.

### Task 6: Product interface

- [ ] Create accessible application shell, landmark structure, skip link, and responsive three-panel workspace.
- [ ] Build sample scenario cards and structured landscape editor with units, ranges, descriptions, and validation on blur.
- [ ] Build the conversation feed, clarification card, composer, response skeleton, retry state, and JSON import/export.
- [ ] Build recommendation, metric impact, confidence, evidence, caveat, and reasoning-trace components.
- [ ] Apply the field-notebook/climate-console visual system and reduced-motion rules.
- [ ] Commit with `feat: build TerraLens assessment workspace`.

### Task 7: Frontend tests and accessibility

- [ ] Add Vitest tests for scenario loading, profile editing, request mapping, clarification rendering, and assessment rendering.
- [ ] Add a Playwright happy-path test using the semi-arid sample.
- [ ] Add keyboard, narrow viewport, server failure, and retry coverage.
- [ ] Run accessibility checks and correct all serious or critical findings.
- [ ] Commit with `test: cover reviewer workflows and accessibility`.

### Task 8: Reviewer documentation and submission artifact

- [ ] Write README sections for value proposition, architecture, retrieval pipeline, schema, local setup, API examples, tests, Docker, CI/CD, limitations, and demo script.
- [ ] Add Mermaid architecture and request-flow diagrams plus an evidence provenance table.
- [ ] Create `SUBMISSION.docx` with clearly labeled publication fields for the future GitHub and live-demo URLs, plus run instructions and reviewer notes.
- [ ] Render the Word document to PNG and correct layout defects.
- [ ] Commit with `docs: add reviewer guide and submission document`.

### Task 9: Final verification and delivery

- [ ] Run the complete backend suite and record the passing count.
- [ ] Run frontend unit tests, lint, and the production build.
- [ ] Launch the integrated app and run Playwright at 1440x900 and 390x844.
- [ ] Inspect screenshots, console errors, overflow, focus order, and all required challenge outputs.
- [ ] Copy the verified repository to `E:\Codes\TerraLens-AI` and confirm file counts and hashes for key artifacts.
- [ ] Commit with `release: prepare hackathon submission`.
