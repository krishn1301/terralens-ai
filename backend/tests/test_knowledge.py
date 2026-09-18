from pathlib import Path

from app.knowledge import KnowledgeStore


DATA = Path(__file__).parents[1] / "data" / "evidence.json"


def test_retrieval_prioritizes_cover_crops_for_low_soil_carbon():
    store = KnowledgeStore(DATA)
    results = store.search("low soil organic carbon monoculture cover crops", limit=3)
    assert results
    assert results[0].id in {"fao-cover-crops", "ipcc-soil-carbon"}
    assert "soil_organic_carbon" in results[0].metrics


def test_retrieval_finds_water_adapted_evidence_for_semi_arid_land():
    store = KnowledgeStore(DATA)
    results = store.search("semi-arid low rainfall water retention agroforestry", limit=4)
    ids = {item.id for item in results}
    assert "ipcc-agroforestry-resilience" in ids


def test_retrieval_connects_fragmentation_to_habitat_corridors():
    store = KnowledgeStore(DATA)
    results = store.search("fragmented habitat isolated species corridor connectivity", limit=3)
    assert results[0].id == "ipbes-connectivity"


def test_retrieval_returns_source_urls_and_bounded_relevance():
    store = KnowledgeStore(DATA)
    for evidence in store.search("riparian pollution runoff biodiversity", limit=5):
        assert str(evidence.url).startswith("http")
        assert 0 <= evidence.relevance <= 1
