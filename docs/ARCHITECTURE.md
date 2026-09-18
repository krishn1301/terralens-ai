# TerraLens AI Architecture

## System boundaries

The React client owns presentation and draft inputs. FastAPI owns validation and response contracts. `SessionStore` owns short-lived conversation state. `KnowledgeStore` owns evidence loading and SQLite FTS5 retrieval. `ReasoningEngine` owns clarification, rule suitability, metric interactions, confidence, caveats, and evidence linkage.

## Landscape schema

`LandscapeProfile` supports region, biome, land use, soil organic carbon, soil pH, soil moisture, annual rainfall, mean temperature, species richness, habitat diversity, fragmentation, and pollution pressure. Each numeric field has an explicit environmental bound. Missing values remain absent and are never imputed.

## Retrieval pipeline

1. Evidence JSON is validated and loaded at service start.
2. Titles, claims, metrics, interventions, and conditions are indexed in an in-memory SQLite FTS5 table with Porter stemming.
3. Queries are normalized and expanded with a small environmental synonym map.
4. FTS candidates are reranked by term, metric, intervention, and condition overlap.
5. The engine resolves stable evidence IDs for each suitable recommendation.

This design satisfies the retrievable-knowledge requirement without network access or a proprietary vector service. Replacing `KnowledgeStore` with a vector adapter does not change API or reasoning contracts.

## Reasoning model

The engine requires at least three populated variables. Guarded rules identify interacting constraints such as low carbon plus low rainfall plus monoculture, or pollution plus waterways plus low habitat diversity. Each rule produces an action, mechanism, affected metrics, measurable monitoring target, time horizon, local confidence, and stable evidence IDs.

Overall assessment confidence combines profile completeness and evidence coverage and is capped below certainty. Missing region and species baselines appear as caveats. Recommendations are ranked by the severity of the limiting ecological process, reversibility, co-benefits, and evidence fit.

## Conversation memory

Every chat response includes a session ID. Follow-up profiles are merged field by field with prior values, so clarification answers preserve earlier context. The bounded in-memory store evicts the least recently used session after 200 active sessions.

## Failure behavior

Pydantic returns field-level validation for impossible values. The client preserves drafts on network errors and offers retry. Missing sample scenarios do not block manual use. Empty evidence produces no unsupported numeric claim. Request IDs are returned for service diagnostics.

## Production path

For deployment, move sessions to Redis or PostgreSQL, persist the evidence index, add authentication and rate limits, and schedule source review. A semantic embedding adapter can be introduced behind `KnowledgeStore`, while the deterministic reasoning layer continues to prevent unsupported claims.
