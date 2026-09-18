from pathlib import Path

from app.knowledge import KnowledgeStore
from app.models import LandscapeProfile
from app.reasoning import ReasoningEngine

DATA = Path(__file__).parents[1] / "data" / "evidence.json"


def engine() -> ReasoningEngine:
    return ReasoningEngine(KnowledgeStore(DATA))


def test_incomplete_profile_returns_targeted_clarification():
    result = engine().analyze(LandscapeProfile(land_use="cropland"), "Biodiversity is falling")
    assert result.clarification is not None
    assert len(result.clarification.missing_fields) >= 2
    assert result.assessment is None


def test_semi_arid_monoculture_combines_carbon_rainfall_and_land_use():
    profile = LandscapeProfile(
        region="semi-arid Maharashtra",
        land_use="monoculture wheat",
        soil_organic_carbon=0.3,
        annual_rainfall_mm=410,
        soil_moisture_pct=14,
        habitat_diversity=2,
    )
    assessment = engine().analyze(profile, "How can I reverse biodiversity decline?").assessment
    assert assessment is not None
    agroforestry = next(
        item for item in assessment.recommendations if item.id == "dryland-agroforestry"
    )
    assert len(agroforestry.contributing_variables) >= 3
    assert any(impact.metric == "soil organic carbon" for impact in agroforestry.impacts)
    assert "ipcc-agroforestry-resilience" in agroforestry.evidence_ids


def test_acidic_wet_land_recommends_test_led_ph_restoration():
    profile = LandscapeProfile(
        land_use="degraded pasture",
        soil_ph=4.7,
        annual_rainfall_mm=1700,
        soil_moisture_pct=68,
        species_richness=7,
    )
    assessment = (
        engine().analyze(profile, "The soil is acidic and plant diversity is low").assessment
    )
    assert any(item.id == "acid-soil-restoration" for item in assessment.recommendations)


def test_fragmented_land_prioritizes_connectivity():
    profile = LandscapeProfile(
        land_use="mixed agriculture",
        fragmentation_pct=72,
        habitat_diversity=2,
        species_richness=9,
    )
    assessment = engine().analyze(profile, "Habitats are isolated").assessment
    assert assessment.recommendations[0].id == "habitat-connectivity"


def test_polluted_riparian_site_recommends_buffer_with_evidence():
    profile = LandscapeProfile(
        land_use="cropland beside stream",
        pollution_level="high",
        annual_rainfall_mm=980,
        habitat_diversity=3,
    )
    assessment = engine().analyze(profile, "Nutrient runoff enters the stream").assessment
    buffer = next(item for item in assessment.recommendations if item.id == "riparian-buffer")
    assert buffer.evidence_ids
    assert any("nitrogen" in evidence.claim.lower() for evidence in assessment.evidence)


def test_every_recommendation_has_three_variables_and_resolvable_evidence():
    profile = LandscapeProfile(
        land_use="monoculture cropland beside stream",
        soil_organic_carbon=0.4,
        annual_rainfall_mm=500,
        pollution_level="moderate",
        fragmentation_pct=55,
    )
    assessment = engine().analyze(profile, "Improve this landscape").assessment
    evidence_ids = {item.id for item in assessment.evidence}
    assert all(len(item.contributing_variables) >= 3 for item in assessment.recommendations)
    assert all(set(item.evidence_ids) <= evidence_ids for item in assessment.recommendations)
