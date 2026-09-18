import pytest
from pydantic import ValidationError

from app.models import ChatRequest, ChatResponse, LandscapeProfile


def test_landscape_profile_rejects_impossible_ph():
    with pytest.raises(ValidationError):
        LandscapeProfile(soil_ph=15)


def test_landscape_profile_accepts_environmental_bounds():
    profile = LandscapeProfile(
        soil_organic_carbon=0.3,
        soil_ph=6.4,
        annual_rainfall_mm=420,
        land_use="monoculture wheat",
    )
    assert profile.soil_organic_carbon == 0.3
    assert profile.annual_rainfall_mm == 420


def test_chat_request_requires_message_or_profile():
    with pytest.raises(ValidationError):
        ChatRequest()


def test_chat_request_accepts_structured_input_without_message():
    request = ChatRequest(profile=LandscapeProfile(land_use="mixed farm"))
    assert request.message is None


def test_response_confidence_is_bounded_and_evidence_is_linked():
    schema = ChatResponse.model_json_schema()
    confidence = schema["$defs"]["Assessment"]["properties"]["confidence"]
    assert confidence["minimum"] == 0
    assert confidence["maximum"] == 1
    recommendation = schema["$defs"]["Recommendation"]
    assert "evidence_ids" in recommendation["properties"]
