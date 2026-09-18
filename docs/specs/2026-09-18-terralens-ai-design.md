# TerraLens AI Product Design

## Purpose

TerraLens AI is a reviewer-friendly biodiversity intelligence workspace that behaves like an environmental scientist. It gathers missing context, retrieves relevant scientific evidence, reasons across several environmental variables, and returns measurable recommendations with sources, confidence, and time horizons.

## Architecture

The product uses a React and TypeScript client with a Python FastAPI service. The service owns session memory, input validation, evidence retrieval, and deterministic reasoning. A structured JSON evidence corpus is indexed with SQLite FTS5 at startup. An optional OpenAI adapter may improve wording, but retrieved evidence and engine calculations remain authoritative, so the default experience works without credentials.

## Core workflow

1. A user selects a sample landscape or describes a problem in text.
2. Structured fields capture soil organic carbon, pH, moisture, rainfall, temperature, land use, habitat diversity, species richness, pollution, and fragmentation.
3. If fewer than three useful variables are present, the assistant asks a targeted clarification and remembers the answer.
4. The retriever searches metric, biome, pressure, and intervention terms and returns traceable evidence chunks.
5. The reasoning engine identifies interacting stressors, ranks suitable interventions, estimates likely metric movement, and computes a transparent confidence score.
6. The API returns a structured assessment containing a synthesis, recommendations, impacted metrics, expected ranges, time horizons, caveats, evidence, and a reasoning trace.

## Interface direction

The visual direction is a field-research notebook crossed with a modern climate operations console: warm mineral background, deep forest ink, lichen accent, restrained topographic lines, editorial serif display type, and compact data-dense panels. The primary workspace pairs a conversation stream with a landscape profile and evidence panel. It avoids generic gradient-heavy chatbot styling.

Desktop uses a three-column layout with conversation at the center. Tablet collapses evidence into an accessible drawer. Mobile uses a single-column flow with a sticky composer and explicit buttons for profile and evidence. All controls have visible focus, 44-pixel targets, semantic labels, and reduced-motion behavior.

## States and recovery

The first-use state offers three meaningful sample landscapes. Incomplete inputs produce a clarification card rather than a weak recommendation. Loading preserves existing conversation and shows a delayed response skeleton. Network failures preserve the draft and offer retry. Empty retrieval returns a clearly labeled low-confidence assessment with data requests. Validation errors identify the affected field in plain language.

## Knowledge and reasoning boundaries

Evidence records include stable IDs, source organization, publication title, year, URL, applicable conditions, metrics, intervention tags, claim text, and quantified ranges. The engine never presents a numeric estimate without a supporting record. Recommendations require at least one retrieved source and at least three contributing variables. Contradictory or weak evidence lowers confidence and is exposed in caveats.

## Scope

The first release includes text and JSON input, multi-turn session memory, evidence inspection, sample scenarios, exportable JSON assessments, health endpoints, unit and API tests, browser tests, Docker, CI, architecture documentation, and a Word submission document. User accounts, remote vector infrastructure, live satellite ingestion, and production authentication are deliberately excluded.

## Verification

Backend tests cover retrieval ranking, clarification rules, multi-metric reasoning, evidence linkage, confidence, session memory, and API validation. Frontend tests cover rendering and response mapping. Browser verification covers the happy path, clarification flow, error recovery, keyboard access, and desktop/mobile layouts. Final checks include linting, production builds, automated accessibility scanning, and fresh end-to-end execution.
