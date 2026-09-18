from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_knowledge_ready():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["evidence_records"] >= 8


def test_scenarios_include_semi_arid_example():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert any(item["id"] == "semi-arid-farm" for item in response.json())


def test_chat_clarifies_then_merges_follow_up_profile():
    first = client.post(
        "/api/chat",
        json={"message": "Biodiversity is declining", "profile": {"land_use": "monoculture wheat"}},
    )
    assert first.status_code == 200
    assert first.json()["status"] == "clarification"
    session_id = first.json()["session_id"]

    second = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "message": "The land is dry and carbon is low",
            "profile": {"soil_organic_carbon": 0.3, "annual_rainfall_mm": 420},
        },
    )
    body = second.json()
    assert body["status"] == "assessment"
    assert body["profile"]["land_use"] == "monoculture wheat"
    assert body["assessment"]["recommendations"]


def test_chat_rejects_invalid_environmental_values():
    response = client.post("/api/chat", json={"profile": {"soil_ph": 19}})
    assert response.status_code == 422


def test_session_can_be_inspected_and_reset():
    created = client.post(
        "/api/chat",
        json={"message": "Assess this", "profile": {"land_use": "grassland"}},
    ).json()
    session_id = created["session_id"]
    assert client.get(f"/api/sessions/{session_id}").status_code == 200
    assert client.delete(f"/api/sessions/{session_id}").status_code == 204
    assert client.get(f"/api/sessions/{session_id}").status_code == 404
