"""Structured evidence loading and SQLite FTS5 retrieval."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from app.models import Evidence

TOKEN_RE = re.compile(r"[a-z][a-z0-9_-]{2,}")
STOPWORDS = {"and", "the", "for", "with", "from", "into", "land"}
EXPANSIONS = {
    "carbon": {"soil_organic_carbon", "cover", "agroforestry"},
    "dry": {"semi-arid", "drought", "rainfall", "moisture"},
    "fragmentation": {"fragmented", "connectivity", "corridor"},
    "isolated": {"fragmented", "connectivity", "corridor"},
    "pollution": {"runoff", "nutrient", "buffer"},
    "acidic": {"acid", "ph", "lime"},
    "biodiversity": {"species", "habitat", "diversity"},
}


class KnowledgeStore:
    """Small, deterministic retrieval layer suitable for an offline review demo."""

    def __init__(self, data_path: str | Path):
        self.records = json.loads(Path(data_path).read_text(encoding="utf-8"))
        self.by_id = {record["id"]: record for record in self.records}
        self.db = sqlite3.connect(":memory:")
        self.db.execute(
            "CREATE VIRTUAL TABLE evidence_fts USING fts5(id UNINDEXED, body, tokenize='porter unicode61')"
        )
        for record in self.records:
            body = " ".join(
                [
                    record["title"],
                    record["claim"],
                    *record["metrics"],
                    *record["interventions"],
                    *record["conditions"],
                ]
            )
            self.db.execute("INSERT INTO evidence_fts(id, body) VALUES (?, ?)", (record["id"], body))
        self.db.commit()

    @staticmethod
    def _terms(query: str) -> set[str]:
        terms = {token for token in TOKEN_RE.findall(query.lower()) if token not in STOPWORDS}
        for token in tuple(terms):
            terms.update(EXPANSIONS.get(token, set()))
        return terms

    def search(self, query: str, limit: int = 5) -> list[Evidence]:
        terms = self._terms(query)
        if not terms:
            return []
        fts_query = " OR ".join(f'"{term}"' for term in sorted(terms))
        rows = self.db.execute(
            "SELECT id FROM evidence_fts WHERE evidence_fts MATCH ? LIMIT 20", (fts_query,)
        ).fetchall()
        candidates = [self.by_id[row[0]] for row in rows]
        scored: list[tuple[float, dict]] = []
        for record in candidates:
            interventions = " ".join(record["interventions"]).lower()
            conditions = " ".join(record["conditions"]).lower()
            searchable = " ".join(
                [
                    record["title"],
                    record["claim"],
                    *record["metrics"],
                    *record["interventions"],
                    *record["conditions"],
                ]
            ).lower()
            hits = sum(1 for term in terms if term.replace("_", " ") in searchable or term in searchable)
            metric_hits = sum(2 for metric in record["metrics"] if metric in terms)
            intervention_hits = sum(2 for term in terms if term in interventions)
            condition_hits = sum(1.5 for term in terms if term in conditions)
            score = hits + metric_hits + intervention_hits + condition_hits
            scored.append((score, record))
        scored.sort(key=lambda item: (-item[0], item[1]["id"]))
        top_score = scored[0][0] if scored else 1
        return [
            Evidence(
                id=record["id"],
                organization=record["organization"],
                title=record["title"],
                year=record["year"],
                url=record["url"],
                claim=record["claim"],
                metrics=record["metrics"],
                relevance=round(0.45 + 0.5 * score / max(top_score, 1), 2),
            )
            for score, record in scored[:limit]
        ]

    def raw(self, evidence_id: str) -> dict:
        return self.by_id[evidence_id]
