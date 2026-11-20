import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, Base, engine
from backend.models import User, Case, Entity, Relationship
from backend.nlp_engine import EvidenceExtractionEngine
from backend.graph_engine import NetworkIntelligenceEngine
from backend.synthetic_data import seed_database

@pytest.fixture(scope="module")
def client():
    # Ensure database is seeded
    db = SessionLocal()
    seed_database(db)
    db.close()
    with TestClient(app) as c:
        yield c

def test_system_health(client):
    res = client.get("/api/system/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OPERATIONAL"
    assert data["database_records"]["cases"] >= 3

def test_authentication_workflow(client):
    # Valid login
    res = client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator@2026!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "INVESTIGATOR"
    token = data["access_token"]

    # Protected me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "investigator"

    # Invalid login
    bad_res = client.post("/api/auth/login", json={"username": "investigator", "password": "WrongPassword!"})
    assert bad_res.status_code == 401

def test_dashboard_stats_and_charts(client):
    token_res = client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator@2026!"})
    headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}

    stats_res = client.get("/api/dashboard/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_cases"] >= 3
    assert stats["total_entities"] >= 14
    assert stats["verified_relationships"] >= 10

    charts_res = client.get("/api/dashboard/charts", headers=headers)
    assert charts_res.status_code == 200
    charts = charts_res.json()
    assert len(charts["entity_distribution"]) > 0
    assert len(charts["verification_breakdown"]) > 0

def test_cases_and_entities_endpoints(client):
    token_res = client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator@2026!"})
    headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}

    cases_res = client.get("/api/cases", headers=headers)
    assert cases_res.status_code == 200
    cases = cases_res.json()
    assert len(cases) >= 3

    entities_res = client.get("/api/entities", headers=headers)
    assert entities_res.status_code == 200
    entities = entities_res.json()
    assert len(entities) >= 14

def test_human_verification_workflow(client):
    token_res = client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator@2026!"})
    headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}

    # Find a pending relationship
    rels_res = client.get("/api/relationships?verification_status=PENDING_REVIEW", headers=headers)
    assert rels_res.status_code == 200
    pending_rels = rels_res.json()
    if pending_rels:
        target_rel = pending_rels[0]
        rel_id = target_rel["id"]

        # Human verification action: approve
        verify_res = client.put(
            f"/api/relationships/{rel_id}/verify",
            json={"verification_status": "VERIFIED", "notes": "Approved following wiretap audio review."},
            headers=headers
        )
        assert verify_res.status_code == 200
        assert verify_res.json()["verification_status"] == "VERIFIED"

def test_nlp_extraction_engine():
    sample_text = (
        "Special Agent report: On 2026-03-22, suspect Dmitri Voronov was tracked driving a Mercedes Sprinter "
        "near Port of Rotterdam Terminal 4B. Wiretap intercept on phone +31-6-555-0192 confirmed he transferred "
        "funds to Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88 belonging to Klaus Richter."
    )
    entities = EvidenceExtractionEngine.extract_entities(sample_text)
    assert len(entities) >= 4
    entity_types = {e["entity_type"] for e in entities}
    assert "PHONE_NUMBER" in entity_types
    assert "FINANCIAL_ACCOUNT" in entity_types

    relationships = EvidenceExtractionEngine.extract_relationships(sample_text, entities)
    assert len(relationships) >= 1

def test_uncertainty_aware_entity_matching():
    score, reasons = EvidenceExtractionEngine.calculate_entity_similarity(
        "Dmitri Voronov", "Dmitry Voronov",
        {"aliases": ["The Ghost", "D. Voronov"], "identifiers": {}},
        {"aliases": ["D. Voronov"], "identifiers": {}}
    )
    assert score >= 0.80
    assert len(reasons) >= 1

def test_graph_analytics_and_shortest_path(client):
    token_res = client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator@2026!"})
    headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}

    # Test Graph Data
    graph_res = client.get("/api/graph/data", headers=headers)
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert len(graph_data["nodes"]) >= 10
    assert len(graph_data["edges"]) >= 10

    # Test Analytics
    analytics_res = client.get("/api/graph/analytics", headers=headers)
    assert analytics_res.status_code == 200
    analytics = analytics_res.json()
    assert len(analytics["degree_centrality"]) > 0
    assert len(analytics["betweenness_centrality"]) > 0
    assert len(analytics["pagerank"]) > 0
    assert len(analytics["communities"]) > 0

    # Test Shortest Path
    nodes = graph_data["nodes"]
    if len(nodes) >= 2:
        src_id = int(nodes[0]["data"]["id"])
        tgt_id = int(nodes[1]["data"]["id"])
        path_res = client.post(
            "/api/graph/shortest-path",
            json={"source_entity_id": src_id, "target_entity_id": tgt_id},
            headers=headers
        )
        assert path_res.status_code == 200

def test_ai_investigation_assistant(client):
    token_res = client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator@2026!"})
    headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}

    # Query unverified
    chat_res = client.post(
        "/api/assistant/chat",
        json={"query": "Which relationships have not been verified?"},
        headers=headers
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert len(chat_data["answer"]) > 20
    assert "suggested_followups" in chat_data

    # Query cross-case
    chat_cross = client.post(
        "/api/assistant/chat",
        json={"query": "What entities connect two investigation cases?"},
        headers=headers
    )
    assert chat_cross.status_code == 200
    assert len(chat_cross.json()["answer"]) > 20
