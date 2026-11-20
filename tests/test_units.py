import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, Base, engine
from backend.models import User, Case, Entity, Relationship
from backend.schemas import (
    UserLogin, CaseCreate, EntityCreate, RelationshipVerificationUpdate,
    ShortestPathRequest, AIChatRequest
)
from backend.main import (
    login, get_dashboard_stats, get_dashboard_charts,
    list_cases, create_case, list_entities, create_entity,
    list_relationships, verify_relationship,
    get_graph_data, get_graph_analytics, find_investigative_path,
    chat_investigation_assistant, list_alerts, list_audit_logs, system_health
)
from backend.synthetic_data import seed_database
from backend.nlp_engine import EvidenceExtractionEngine
from backend.graph_engine import NetworkIntelligenceEngine

def run_tests():
    print("=" * 65)
    print("AI-POWERED CRIMINAL NETWORK SYSTEM - FULL VERIFICATION TEST")
    print("=" * 65)

    db = SessionLocal()
    seed_database(db)

    # 1. System Health
    health = system_health(db)
    assert health["status"] == "OPERATIONAL"
    print(f"[OK] System Health: {health['status']} | DB Records: {health['database_records']}")

    # 2. Authentication
    login_res = login(UserLogin(username="investigator", password="Investigator@2026!"), db)
    assert login_res["access_token"]
    test_user = login_res["user"]
    print(f"[OK] Auth Login: User '{test_user.username}' (Role: {test_user.role})")

    # 3. Dashboard Stats & Charts
    stats = get_dashboard_stats(test_user, db)
    assert stats["total_cases"] >= 3
    assert stats["total_entities"] >= 14
    print(f"[OK] Dashboard Stats: {stats['total_cases']} Cases, {stats['total_entities']} Entities, {stats['verified_relationships']} Verified Rels")

    charts = get_dashboard_charts(test_user, db)
    assert len(charts["entity_distribution"]) > 0
    assert len(charts["verification_breakdown"]) > 0
    print(f"[OK] Dashboard Charts: {len(charts['entity_distribution'])} Entity Types visualized")

    # 4. Case Management
    cases = list_cases(test_user, db)
    assert len(cases) >= 3
    print(f"[OK] Case Management: {len(cases)} cases retrieved (Lead: {cases[0].lead_investigator_id})")

    # 5. Entity Management
    entities = list_entities(None, None, None, None, None, test_user, db)
    assert len(entities) >= 14
    types_found = {e.entity_type for e in entities}
    print(f"[OK] Entity Management: {len(entities)} entities across {len(types_found)} types ({', '.join(types_found)})")

    # 6. Relationships & Human Verification Workflow
    rels = list_relationships(None, None, test_user, db)
    assert len(rels) >= 10
    pending = [r for r in rels if r.verification_status == "PENDING_REVIEW"]
    print(f"[OK] Relationships: {len(rels)} total relationships ({len(pending)} pending review)")

    if pending:
        target = pending[0]
        verified_rel = verify_relationship(
            target.id,
            RelationshipVerificationUpdate(verification_status="VERIFIED", notes="Test verification approval"),
            test_user,
            db
        )
        assert verified_rel.verification_status == "VERIFIED"
        print(f"[OK] Human Verification Workflow: Successfully approved relationship #{target.id}")

    # 7. NLP Evidence Extraction Engine
    sample_text = (
        "Tactical Report: Suspect Dmitri Voronov operated white Mercedes Sprinter 7-KDX-94 "
        "at Port of Rotterdam Terminal 4B. Wiretap intercept on phone +31-6-555-0192 confirmed transfer "
        "to Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88 belonging to Klaus Richter."
    )
    extracted_ents = EvidenceExtractionEngine.extract_entities(sample_text)
    assert len(extracted_ents) >= 4
    extracted_rels = EvidenceExtractionEngine.extract_relationships(sample_text, extracted_ents)
    assert len(extracted_rels) >= 1
    print(f"[OK] NLP Extraction Engine: {len(extracted_ents)} entities extracted, {len(extracted_rels)} relationships linked")

    # 8. Uncertainty-Aware Entity Matching
    score, reasons = EvidenceExtractionEngine.calculate_entity_similarity(
        "Dmitri Voronov", "Dmitry Voronov",
        {"aliases": ["The Ghost", "D. Voronov"], "identifiers": {}},
        {"aliases": ["D. Voronov"], "identifiers": {}}
    )
    assert score >= 0.80
    assert len(reasons) >= 1
    print(f"[OK] Uncertainty-Aware Matching: Score {score} with reasons: {reasons[0]}")

    # 9. Knowledge Graph & Cytoscape Formatting
    kg = get_graph_data(None, True, 0.0, None, test_user, db)
    assert len(kg.nodes) >= 14
    assert len(kg.edges) >= 10
    print(f"[OK] Knowledge Graph: {len(kg.nodes)} Cytoscape nodes, {len(kg.edges)} Cytoscape edges")

    # 10. Real Network Analytics (Degree, Betweenness, PageRank, Communities, Anomalies)
    analytics = get_graph_analytics(None, test_user, db)
    assert len(analytics.degree_centrality) > 0
    assert len(analytics.betweenness_centrality) > 0
    assert len(analytics.pagerank) > 0
    assert len(analytics.communities) > 0
    top_deg = analytics.degree_centrality[0]
    top_bet = analytics.betweenness_centrality[0]
    print(f"[OK] Network Analytics:")
    print(f"     - Top Degree Hub: {top_deg['name']} (degree: {top_deg['raw_degree']})")
    print(f"     - Top Bridge (Betweenness): {top_bet['name']} (score: {top_bet['score']})")
    print(f"     - Community Clusters Found: {len(analytics.communities)}")
    print(f"     - Explainable Anomalies Detected: {len(analytics.anomalies)}")

    # 11. Shortest Path Finder
    n1 = int(kg.nodes[0]["data"]["id"])
    n2 = int(kg.nodes[1]["data"]["id"])
    path_res = find_investigative_path(ShortestPathRequest(source_entity_id=n1, target_entity_id=n2), test_user, db)
    print(f"[OK] Shortest Path Finder: Path between #{n1} and #{n2} (Found: {path_res['found']}, Hops: {path_res['total_hops']})")

    # 12. AI Investigation Assistant (Evidence-grounded)
    ai_unverified = chat_investigation_assistant(AIChatRequest(query="Which relationships have not been verified?"), test_user, db)
    assert len(ai_unverified.answer) > 20
    print(f"[OK] AI Assistant (Unverified query): {len(ai_unverified.answer)} chars response")

    ai_cross = chat_investigation_assistant(AIChatRequest(query="What entities connect two investigation cases?"), test_user, db)
    assert len(ai_cross.answer) > 20
    print(f"[OK] AI Assistant (Cross-case query): {len(ai_cross.answer)} chars response with {len(ai_cross.evidence_citations)} citations")

    # 13. Alerts & Audit Logs
    alerts = list_alerts(None, None, test_user, db)
    assert len(alerts) >= 2
    audits = list_audit_logs(None, None, test_user, db)
    assert len(audits) >= 3
    print(f"[OK] Alerts & Audits: {len(alerts)} alerts active, {len(audits)} tamper-evident audit records")

    # 14. Synthetic Data Engine Scenarios & Samples
    from backend.synthetic_engine import SyntheticDataEngine
    scenarios = SyntheticDataEngine.list_scenarios()
    assert len(scenarios) >= 4
    samples = SyntheticDataEngine.list_samples()
    assert len(samples) >= 6
    print(f"[OK] Synthetic Data Engine: {len(scenarios)} multi-agency scenarios, {len(samples)} realistic evidence samples")

    # 15. Synthetic Dataset Export
    export_payload = SyntheticDataEngine.export_full_dataset(db)
    assert "cases" in export_payload
    assert "entities" in export_payload
    assert "metadata" in export_payload
    print(f"[OK] Synthetic Dataset Export: Serialized {export_payload['metadata']['counts']['entities']} entities and {export_payload['metadata']['counts']['relationships']} relationships to JSON")

    db.close()
    print("=" * 65)
    print("ALL 15 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
