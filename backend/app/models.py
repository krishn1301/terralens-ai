"""Typed contracts shared by the TerraLens API and reasoning engine."""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator


class LandscapeProfile(BaseModel):
    region: str | None = Field(default=None, max_length=120)
    biome: str | None = Field(default=None, max_length=80)
    land_use: str | None = Field(default=None, max_length=120)
    soil_organic_carbon: float | None = Field(default=None, ge=0, le=20)
    soil_ph: float | None = Field(default=None, ge=0, le=14)
    soil_moisture_pct: float | None = Field(default=None, ge=0, le=100)
    annual_rainfall_mm: float | None = Field(default=None, ge=0, le=12000)
    mean_temperature_c: float | None = Field(default=None, ge=-50, le=60)
    species_richness: int | None = Field(default=None, ge=0, le=100000)
    habitat_diversity: int | None = Field(default=None, ge=1, le=10)
    fragmentation_pct: float | None = Field(default=None, ge=0, le=100)
    pollution_level: Literal["low", "moderate", "high"] | None = None

    def populated_fields(self) -> dict[str, object]:
        return self.model_dump(exclude_none=True)


class ChatRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=80)
    message: str | None = Field(default=None, max_length=2000)
    profile: LandscapeProfile | None = None

    @model_validator(mode="after")
    def require_input(self) -> "ChatRequest":
        if not (self.message and self.message.strip()) and not (
            self.profile and self.profile.populated_fields()
        ):
            raise ValueError("Provide a message or at least one landscape metric.")
        return self


class Evidence(BaseModel):
    id: str
    organization: str
    title: str
    year: int
    url: HttpUrl
    claim: str
    metrics: list[str]
    relevance: float = Field(ge=0, le=1)


class MetricImpact(BaseModel):
    metric: str
    direction: Literal["increase", "decrease", "stabilize"]
    expected_change: str


class Recommendation(BaseModel):
    id: str
    title: str
    action: str
    rationale: str
    contributing_variables: list[str] = Field(min_length=3)
    impacts: list[MetricImpact]
    time_horizon: Literal["short", "medium", "long"]
    confidence: float = Field(ge=0, le=1)
    evidence_ids: list[str] = Field(min_length=1)


class ReasoningStep(BaseModel):
    label: str
    explanation: str


class Clarification(BaseModel):
    question: str
    missing_fields: list[str]
    known_context: list[str]


class Assessment(BaseModel):
    summary: str
    confidence: float = Field(ge=0, le=1)
    recommendations: list[Recommendation]
    evidence: list[Evidence]
    reasoning_trace: list[ReasoningStep]
    caveats: list[str]


class ChatResponse(BaseModel):
    session_id: str
    status: Literal["clarification", "assessment"]
    message: str
    profile: LandscapeProfile
    clarification: Clarification | None = None
    assessment: Assessment | None = None


class Scenario(BaseModel):
    id: str
    name: str
    description: str
    profile: LandscapeProfile
    prompt: str
