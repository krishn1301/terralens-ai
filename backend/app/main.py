"""TerraLens AI HTTP application."""

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.knowledge import KnowledgeStore
from app.models import ChatRequest, ChatResponse, LandscapeProfile, Scenario
from app.reasoning import ReasoningEngine
from app.sessions import SessionStore

DATA_PATH = Path(__file__).parents[1] / "data" / "evidence.json"
knowledge = KnowledgeStore(DATA_PATH)
engine = ReasoningEngine(knowledge)
sessions = SessionStore()

app = FastAPI(
    title="TerraLens AI",
    version="1.0.0",
    description="Evidence-grounded, multi-metric biodiversity intelligence.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", uuid4().hex)
    return response


SCENARIOS = [
    Scenario(
        id="semi-arid-farm",
        name="Semi-arid wheat farm",
        description="Low carbon, seasonal water stress, and monoculture simplify habitat.",
        profile=LandscapeProfile(
            region="Maharashtra, India",
            biome="semi-arid",
            land_use="monoculture wheat",
            soil_organic_carbon=0.3,
            soil_ph=7.4,
            soil_moisture_pct=14,
            annual_rainfall_mm=420,
            mean_temperature_c=27,
            species_richness=11,
            habitat_diversity=2,
            fragmentation_pct=48,
            pollution_level="moderate",
        ),
        prompt="How can this farm rebuild biodiversity without worsening water stress?",
    ),
    Scenario(
        id="fragmented-estate",
        name="Fragmented peri-urban estate",
        description="Small habitat islands face severe isolation and edge pressure.",
        profile=LandscapeProfile(
            region="Western Ghats edge",
            biome="tropical moist",
            land_use="mixed agriculture and housing",
            soil_organic_carbon=1.4,
            annual_rainfall_mm=1900,
            species_richness=18,
            habitat_diversity=3,
            fragmentation_pct=76,
            pollution_level="moderate",
        ),
        prompt="Which action would most improve ecological connectivity?",
    ),
    Scenario(
        id="polluted-riparian",
        name="Polluted farm stream",
        description="Cropland runoff, bank erosion, and low shade degrade aquatic habitat.",
        profile=LandscapeProfile(
            region="Central Indian plateau",
            biome="subtropical dry",
            land_use="cropland beside stream",
            soil_organic_carbon=0.8,
            soil_ph=6.2,
            annual_rainfall_mm=980,
            species_richness=8,
            habitat_diversity=2,
            fragmentation_pct=52,
            pollution_level="high",
        ),
        prompt="How should I reduce nutrient runoff and restore stream biodiversity?",
    ),
]


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"status": "ready", "evidence_records": len(knowledge.records), "mode": "local-grounded"}


@app.get("/api/scenarios", response_model=list[Scenario])
def get_scenarios() -> list[Scenario]:
    return SCENARIOS


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    session = sessions.get_or_create(payload.session_id)
    sessions.merge_profile(session, payload.profile)
    if payload.message:
        session.messages.append({"role": "user", "content": payload.message.strip()})
    result = engine.analyze(session.profile, payload.message or "")
    if result.clarification:
        text = result.clarification.question
        session.messages.append({"role": "assistant", "content": text})
        return ChatResponse(
            session_id=session.id,
            status="clarification",
            message=text,
            profile=session.profile,
            clarification=result.clarification,
        )
    assert result.assessment is not None
    session.messages.append({"role": "assistant", "content": result.assessment.summary})
    return ChatResponse(
        session_id=session.id,
        status="assessment",
        message=result.assessment.summary,
        profile=session.profile,
        assessment=result.assessment,
    )


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, object]:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Conversation session not found.")
    return {"id": session.id, "profile": session.profile, "messages": session.messages}


@app.delete("/api/sessions/{session_id}", status_code=204)
def delete_session(session_id: str) -> Response:
    if not sessions.delete(session_id):
        raise HTTPException(status_code=404, detail="Conversation session not found.")
    return Response(status_code=204)
