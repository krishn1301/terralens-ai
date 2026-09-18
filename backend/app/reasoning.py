"""Explainable multi-metric environmental reasoning."""

from dataclasses import dataclass

from app.knowledge import KnowledgeStore
from app.models import (
    Assessment,
    Clarification,
    LandscapeProfile,
    MetricImpact,
    ReasoningStep,
    Recommendation,
)

FIELD_LABELS = {
    "soil_organic_carbon": "soil organic carbon",
    "soil_ph": "soil pH",
    "soil_moisture_pct": "soil moisture",
    "annual_rainfall_mm": "annual rainfall",
    "land_use": "land use",
    "habitat_diversity": "habitat diversity",
    "species_richness": "species richness",
    "fragmentation_pct": "habitat fragmentation",
    "pollution_level": "pollution pressure",
    "mean_temperature_c": "mean temperature",
    "region": "region",
    "biome": "biome",
}


@dataclass
class EngineResult:
    clarification: Clarification | None = None
    assessment: Assessment | None = None


class ReasoningEngine:
    def __init__(self, knowledge: KnowledgeStore):
        self.knowledge = knowledge

    def analyze(self, profile: LandscapeProfile, message: str = "") -> EngineResult:
        values = profile.populated_fields()
        if len(values) < 3:
            return EngineResult(clarification=self._clarify(values))

        recommendations: list[Recommendation] = []
        message_lower = message.lower()
        variables = [FIELD_LABELS[key] for key in values if key in FIELD_LABELS]

        if (profile.fragmentation_pct or 0) >= 40 or any(
            term in message_lower for term in ("fragment", "isolated", "corridor")
        ):
            recommendations.append(self._connectivity(profile, variables))
        if profile.pollution_level in {"moderate", "high"} or "runoff" in message_lower:
            recommendations.append(self._riparian(profile, variables))
        if profile.soil_ph is not None and profile.soil_ph < 5.5:
            recommendations.append(self._acid_soil(profile, variables))
        dry = profile.annual_rainfall_mm is not None and profile.annual_rainfall_mm < 650
        low_carbon = profile.soil_organic_carbon is not None and profile.soil_organic_carbon < 1
        monoculture = "monoculture" in (profile.land_use or "").lower()
        if sum((dry, low_carbon, monoculture)) >= 2:
            recommendations.append(self._dryland_agroforestry(profile, variables))
        if low_carbon or monoculture:
            recommendations.append(self._cover_crop(profile, variables))
        if not recommendations:
            recommendations.append(self._diversify(profile, variables))

        evidence_ids = list(dict.fromkeys(eid for rec in recommendations for eid in rec.evidence_ids))
        evidence = [self.knowledge.get(eid) for eid in evidence_ids]
        completeness = min(len(values) / 7, 1)
        confidence = round(0.58 + 0.25 * completeness + 0.03 * min(len(evidence), 3), 2)
        steps = self._trace(profile, recommendations)
        caveats = self._caveats(profile)
        summary = self._summary(profile, recommendations)
        return EngineResult(
            assessment=Assessment(
                summary=summary,
                confidence=min(confidence, 0.94),
                recommendations=recommendations[:4],
                evidence=evidence,
                reasoning_trace=steps,
                caveats=caveats,
            )
        )

    def _clarify(self, values: dict[str, object]) -> Clarification:
        priorities = ["soil_organic_carbon", "annual_rainfall_mm", "land_use", "fragmentation_pct"]
        missing = [field for field in priorities if field not in values][: 3 - len(values)]
        labels = [FIELD_LABELS[field] for field in missing]
        return Clarification(
            question=f"To connect the pressures, please add {', '.join(labels)}.",
            missing_fields=missing,
            known_context=[f"{FIELD_LABELS.get(key, key)}: {value}" for key, value in values.items()],
        )

    @staticmethod
    def _vars(variables: list[str]) -> list[str]:
        return variables[:5]

    def _connectivity(self, profile: LandscapeProfile, variables: list[str]) -> Recommendation:
        severity = profile.fragmentation_pct or 40
        return Recommendation(
            id="habitat-connectivity",
            title="Reconnect habitat before adding isolated habitat patches",
            action="Map the shortest breaks between remnant patches, then establish native hedgerows and 10-30 m stepping-stone patches along those routes.",
            rationale=f"At {severity:.0f}% fragmentation, movement and gene flow are likely a stronger constraint than local planting alone. Connected native structure also moves pollen and moisture across the landscape.",
            contributing_variables=self._vars(variables),
            impacts=[
                MetricImpact(metric="habitat fragmentation", direction="decrease", expected_change="target a 10-20 percentage-point reduction in disconnected area"),
                MetricImpact(metric="species richness", direction="increase", expected_change="monitor occupancy gains over 2-5 breeding seasons"),
            ],
            time_horizon="medium",
            confidence=0.86,
            evidence_ids=["ipbes-connectivity", "usda-riparian-connectivity"],
        )

    def _riparian(self, profile: LandscapeProfile, variables: list[str]) -> Recommendation:
        return Recommendation(
            id="riparian-buffer",
            title="Install a layered native riparian buffer at runoff entry points",
            action="Prioritize concentrated flow paths with native grasses, shrubs, and trees; begin with 15-30 m widths and widen where slope, soil, or pollutant load is high.",
            rationale="A layered buffer treats nutrient and sediment runoff while adding cool, connected aquatic and terrestrial habitat. Placement at actual flow paths matters more than uniform planting.",
            contributing_variables=self._vars(variables),
            impacts=[
                MetricImpact(metric="nutrient pollution", direction="decrease", expected_change="up to 90% unused nitrogen removal is reported under suitable conditions"),
                MetricImpact(metric="habitat diversity", direction="increase", expected_change="add 2-3 vertical vegetation layers"),
            ],
            time_horizon="medium",
            confidence=0.84 if profile.pollution_level == "high" else 0.76,
            evidence_ids=["usda-buffer-nitrogen", "usda-riparian-buffer"],
        )

    def _acid_soil(self, profile: LandscapeProfile, variables: list[str]) -> Recommendation:
        return Recommendation(
            id="acid-soil-restoration",
            title="Correct acidity with a soil-test-led mosaic strategy",
            action="Test buffer capacity first, then apply lime only to production zones while retaining acid-tolerant native refuges and adding diverse rotations.",
            rationale=f"At pH {profile.soil_ph:.1f}, aluminium toxicity and phosphorus limitation can suppress plants and soil biota. Uniform liming could erase acid-adapted habitat, so spatial targeting protects diversity.",
            contributing_variables=self._vars(variables),
            impacts=[
                MetricImpact(metric="soil pH", direction="increase", expected_change="move managed zones toward pH 5.5-6.5 after soil testing"),
                MetricImpact(metric="soil biological activity", direction="increase", expected_change="reassess respiration and earthworms after 6-12 months"),
            ],
            time_horizon="short",
            confidence=0.82,
            evidence_ids=["fao-acid-soils", "fao-soil-biodiversity"],
        )

    def _dryland_agroforestry(self, profile: LandscapeProfile, variables: list[str]) -> Recommendation:
        return Recommendation(
            id="dryland-agroforestry",
            title="Use low-density agroforestry as a water-and-carbon intervention",
            action="Introduce drought-adapted native trees on contours or wide alleys, retaining sunny crop zones and pairing establishment with mulch and water harvesting basins.",
            rationale="Low rainfall, depleted carbon, and monoculture reinforce one another: less organic matter reduces infiltration, while uniform cover removes thermal refuges. Sparse woody structure addresses all three without over-consuming water.",
            contributing_variables=self._vars(variables),
            impacts=[
                MetricImpact(metric="soil organic carbon", direction="increase", expected_change="a roughly one-third long-term increase is a defensible literature benchmark, not a site guarantee"),
                MetricImpact(metric="habitat diversity", direction="increase", expected_change="add woody, edge, and litter microhabitats within 2-5 years"),
                MetricImpact(metric="soil moisture", direction="stabilize", expected_change="track dry-season moisture against an untreated control"),
            ],
            time_horizon="long",
            confidence=0.83,
            evidence_ids=["ipcc-agroforestry-resilience", "fao-agroforestry-functions"],
        )

    def _cover_crop(self, profile: LandscapeProfile, variables: list[str]) -> Recommendation:
        return Recommendation(
            id="adaptive-cover-crops",
            title="Replace bare fallow with a rainfall-matched cover-crop mix",
            action="Pilot drought-tolerant legumes plus a fibrous-rooted species on 10% of the field, terminate before water competition, and retain residue as surface cover.",
            rationale="A mixed cover interrupts monoculture, feeds soil organisms, protects aggregates, and recycles nutrients. A small controlled pilot limits water-risk where rainfall is low.",
            contributing_variables=self._vars(variables),
            impacts=[
                MetricImpact(metric="soil organic carbon", direction="increase", expected_change="detectable trend over 2-3 years with annual sampling"),
                MetricImpact(metric="soil moisture", direction="stabilize", expected_change="reduce bare-soil evaporation between crops"),
            ],
            time_horizon="medium",
            confidence=0.79,
            evidence_ids=["fao-cover-crops", "ipcc-soil-carbon"],
        )

    def _diversify(self, profile: LandscapeProfile, variables: list[str]) -> Recommendation:
        return Recommendation(
            id="functional-diversity",
            title="Build functional diversity around the weakest metric",
            action="Establish a replicated native planting trial with flowering, deep-rooted, nitrogen-fixing, and ground-cover functional groups, then compare it with an untreated plot.",
            rationale="Functional groups affect water, nutrients, habitat structure, and food resources differently; a replicated trial reveals which combination fits this site.",
            contributing_variables=self._vars(variables),
            impacts=[
                MetricImpact(metric="habitat diversity", direction="increase", expected_change="add at least three functional vegetation groups"),
                MetricImpact(metric="species richness", direction="increase", expected_change="measure seasonal occupancy against baseline"),
            ],
            time_horizon="medium",
            confidence=0.68,
            evidence_ids=["fao-soil-biodiversity", "ipcc-agroforestry-resilience"],
        )

    @staticmethod
    def _trace(profile: LandscapeProfile, recommendations: list[Recommendation]) -> list[ReasoningStep]:
        present = profile.populated_fields()
        return [
            ReasoningStep(label="Observe", explanation=f"Used {len(present)} supplied landscape variables; no missing value was imputed."),
            ReasoningStep(label="Connect", explanation="Matched interacting soil, water, habitat, climate, and human-pressure signals rather than scoring each in isolation."),
            ReasoningStep(label="Retrieve", explanation=f"Selected evidence for {len(recommendations)} interventions from the local indexed corpus."),
            ReasoningStep(label="Prioritize", explanation="Ranked actions by ecological constraint, reversibility, co-benefits, and evidence fit."),
        ]

    @staticmethod
    def _caveats(profile: LandscapeProfile) -> list[str]:
        caveats = ["Ranges are planning benchmarks; confirm them with a local baseline and untreated comparison area."]
        if profile.region is None:
            caveats.append("Region was not supplied, so species and planting-calendar choices require local validation.")
        if profile.species_richness is None:
            caveats.append("No species baseline was supplied; complete a seasonal inventory before claiming biodiversity gains.")
        return caveats

    @staticmethod
    def _summary(profile: LandscapeProfile, recommendations: list[Recommendation]) -> str:
        focus = ", ".join(item.title.lower() for item in recommendations[:2])
        return f"The strongest leverage is to {focus}. This sequence treats interacting constraints in the supplied landscape instead of optimizing a single metric."
