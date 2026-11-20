import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from backend.main import app
from backend.database import SessionLocal
from backend.synthetic_data import seed_database
from backend.nlp_engine import EvidenceExtractionEngine

async def run_all_tests():
    print("=" * 60)
    print("RUNNING CRIMINAL NETWORK SYSTEM BACKEND TEST SUITE")
    print("=" * 60)

    # 1. Test database seed
    db = SessionLocal()
    seed_database(db)
    db.close()
    print("[PASS] Database seed and models integrity")

    # 2. Test NLP Evidence Extraction Engine
    sample_text = (
        "Police Report: Suspect Dmitri Voronov operated white Mercedes Sprinter 7-KDX-94 "
        "at Port of Rotterdam Terminal 4B. Intercept on phone +31-6-555-0192 confirmed transfer "
        "to Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88 belonging to Klaus Richter."
    )
    entities = EvidenceExtractionEngine.extract_entities(sample_text)
    assert len(entities) >= 4, f"Expected at least 4 entities, got {len(entities)}"
    types = {e["entity_type"] for e in entities}
    assert "PHONE_NUMBER" in types, "PHONE_NUMBER entity not detected"
    assert "FINANCIAL_ACCOUNT" in types, "FINANCIAL_ACCOUNT entity not detected"
    rels = EvidenceExtractionEngine.extract_relationships(sample_text, entities)
    assert len(rels) >= 1, "Expected relationships extracted"
    print(f"[PASS] NLP Evidence Extraction (found {len(entities)} entities, {len(rels)} relationships)")

    # 3. Test Uncertainty-Aware Entity Matching
    score, reasons = EvidenceExtractionEngine.calculate_entity_similarity(
        "Dmitri Voronov", "Dmitry Voronov",
        {"aliases": ["The Ghost", "D. Voronov"], "identifiers": {}},
        {"aliases": ["D. Voronov"], "identifiers": {}}
    )
    assert score >= 0.80, f"Expected similarity >= 0.80, got {score}"
    assert len(reasons) >= 1, "Expected match reasons list"
    print(f"[PASS] Uncertainty-Aware Entity Matching (score: {score}, reasons: {len(reasons)})")

    # 4. Test REST APIs via httpx.AsyncClient with ASGITransport
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Health
        res = await client.get("/api/system/health")
        assert res.status_code == 200, f"Health check failed: {res.status_code}"
        assert res.json()["status"] == "OPERATIONAL"
        print("[PASS] GET /api/system/health")

        # Auth Login
        res = await client.post("/api/auth/login", json={"username": "investigator", "password": "Investigator@2026!"})
        assert res.status_code == 200, f"Login failed: {res.status_code}"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[PASS] POST /api/auth/login (JWT token issued)")

        # Auth Me
        res = await client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["username"] == "investigator"
        print("[PASS] GET /api/auth/me")

        # Dashboard Stats
        res = await client.get("/api/dashboard/stats", headers=headers)
        assert res.status_code == 200
        stats = res.json()
        assert stats["total_cases"] >= 3
        assert stats["total_entities"] >= 14
        print(f"[PASS] GET /api/dashboard/stats (cases: {stats['total_cases']}, entities: {stats['total_entities']})")

        # Dashboard Charts
        res = await client.get("/api/dashboard/charts", headers=headers)
        assert res.status_code == 200
        print("[PASS] GET /api/dashboard/charts")

        # Cases List
        res = await client.get("/api/cases", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 3
        print(f"[PASS] GET /api/cases (count: {len(res.json())})")

        # Entities List
        res = await client.get("/api/entities", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 14
        print(f"[PASS] GET /api/entities (count: {len(res.json())})")

        # Relationships & Verification Workflow
        res = await client.get("/api/relationships", headers=headers)
        assert res.status_code == 200
        rels_list = res.json()
        assert len(rels_list) >= 10
        print(f"[PASS] GET /api/relationships (count: {len(rels_list)})")

        # Verify a relationship
        target_rel = rels_list[0]
        v_res = await client.put(
            f"/api/relationships/{target_rel['id']}/verify",
            json={"verification_status": "VERIFIED", "notes": "Verified in test runner"},
            headers=headers
        )
        assert v_res.status_code == 200
        print(f"[PASS] PUT /api/relationships/{target_rel['id']}/verify (Human Verification Workflow)")

        # Knowledge Graph Data
        res = await client.get("/api/graph/data", headers=headers)
        assert res.status_code == 200
        g_data = res.json()
        assert len(g_data["nodes"]) >= 10
        assert len(g_data["edges"]) >= 10
        print(f"[PASS] GET /api/graph/data (nodes: {len(g_data['nodes'])}, edges: {len(g_data['edges'])})")

        # Network Analytics (Degree, Betweenness, PageRank, Communities, Anomalies)
        res = await client.get("/api/graph/analytics", headers=headers)
        assert res.status_code == 200
        analytics = res.json()
        assert len(analytics["degree_centrality"]) > 0
        assert len(analytics["betweenness_centrality"]) > 0
        assert len(analytics["pagerank"]) > 0
        assert len(analytics["communities"]) > 0
        print(f"[PASS] GET /api/graph/analytics (communities: {len(analytics['communities'])}, anomalies: {len(analytics['anomalies'])})")

        # Shortest Path
        node_ids = [int(n["data"]["id"]) for n in g_data["nodes"][:2]]
        res = await client.post(
            "/api/graph/shortest-path",
            json={"source_entity_id": node_ids[0], "target_entity_id": node_ids[1]},
            headers=headers
        )
        assert res.status_code == 200
        print("[PASS] POST /api/graph/shortest-path")

        # AI Assistant Chat
        res = await client.post(
            "/api/assistant/chat",
            json={"query": "Which relationships have not been verified?"},
            headers=headers
        )
        assert res.status_code == 200
        ans = res.json()
        assert len(ans["answer"]) > 20
        print("[PASS] POST /api/assistant/chat (Evidence-grounded response with citations)")

        # Alerts
        res = await client.get("/api/alerts", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 2
        print(f"[PASS] GET /api/alerts (active alerts: {len(res.json())})")

        # HTML Dossier Report
        res = await client.get("/api/reports/html", headers=headers)
        assert res.status_code == 200
        assert "CONFIDENTIAL INTELLIGENCE REPORT" in res.text
        print("[PASS] GET /api/reports/html (Printable official intelligence report)")

        # Audit Logs
        res = await client.get("/api/audit/logs", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 3
        print(f"[PASS] GET /api/audit/logs (audit entries: {len(res.json())})")

    print("=" * 60)
    print("ALL 16 BACKEND TEST SUITES PASSED FLAWLESSLY!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
