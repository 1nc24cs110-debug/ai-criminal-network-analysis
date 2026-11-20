import datetime
from sqlalchemy.orm import Session
from backend.models import (
    User, Case, Entity, Relationship, EvidenceDocument,
    EvidenceReference, EntityMatchSuggestion, NetworkPatternAlert, AuditLog
)
from backend.auth import hash_password

def seed_database(db: Session):
    """
    Seeds database with original synthetic demonstration dataset.
    Includes multi-case investigation records, evidence documents with exact excerpts,
    provenance references, cross-case entity overlaps, and anomaly alerts.
    """
    # Check if already seeded
    if db.query(User).count() > 0:
        return

    print("[*] Seeding database with synthetic intelligence records...")

    # 1. Seed Users
    admin_user = User(
        username="admin",
        email="admin@intel.gov",
        hashed_password=hash_password("Admin@2026!"),
        full_name="Director Sarah Jenkins",
        role="ADMIN",
        badge_number="FED-0019",
        department="Federal Intelligence Directorate"
    )
    investigator_user = User(
        username="investigator",
        email="investigator@intel.gov",
        hashed_password=hash_password("Investigator@2026!"),
        full_name="Special Agent Marcus Vance",
        role="INVESTIGATOR",
        badge_number="INV-4821",
        department="Transnational Organized Crime Taskforce"
    )
    analyst_user = User(
        username="analyst",
        email="analyst@intel.gov",
        hashed_password=hash_password("Analyst@2026!"),
        full_name="Senior Analyst Elena Rostova",
        role="ANALYST",
        badge_number="ANA-9012",
        department="Graph Intelligence & Analytics Unit"
    )
    db.add_all([admin_user, investigator_user, analyst_user])
    db.commit()

    # 2. Seed Investigation Cases
    case_1 = Case(
        case_number="CR-2026-0812",
        title="Operation Blue Horizon: Maritime Port Infiltration",
        summary="Investigation into a sophisticated contraband distribution and logistics syndicate operating through Rotterdam and Antwerp container terminals.",
        status="ACTIVE",
        priority="CRITICAL",
        jurisdiction="Federal Inter-Agency / Europol Liaison",
        lead_investigator_id=investigator_user.id,
        tags=["narcotics", "maritime", "corrupt-officials", "cross-border"]
    )
    case_2 = Case(
        case_number="CR-2026-0944",
        title="Operation Phantom Freight: Trade-Based Capital Laundering",
        summary="Inquiry into front-company shipping networks, fraudulent invoices, and crypto off-ramps utilized to disguise illicit revenue across European ports.",
        status="ACTIVE",
        priority="HIGH",
        jurisdiction="Financial Crimes Enforcement Unit",
        lead_investigator_id=investigator_user.id,
        tags=["money-laundering", "shell-companies", "crypto-wash", "customs-fraud"]
    )
    case_3 = Case(
        case_number="CR-2026-1105",
        title="Operation Obsidian Wire: Encrypted Communications & Fleet Dispatch",
        summary="Analysis of burner device telecommunications, hardware tokens, and fleet vehicle movements orchestrating regional drop-off logistics.",
        status="UNDER_REVIEW",
        priority="MEDIUM",
        jurisdiction="Cyber Surveillance & Counter-Smuggling Taskforce",
        lead_investigator_id=investigator_user.id,
        tags=["burner-phones", "telecoms", "vehicle-tracking", "encrypted-chat"]
    )
    db.add_all([case_1, case_2, case_3])
    db.commit()

    # 3. Seed Entities across cases
    # Case 1 Entities (Blue Horizon)
    e_dmitri = Entity(
        case_id=case_1.id,
        name="Dmitri Voronov",
        canonical_name="Dmitri Voronov",
        entity_type="PERSON",
        aliases=["The Ghost", "DV-7", "D. Voronov"],
        identifiers={"passport": "RU-8921441", "alias_code": "ALPHA-01"},
        risk_level="CRITICAL",
        attributes={"suspected_role": "Maritime Logistics Coordinator", "nationality": "Dual RU/CY"},
        verification_status="VERIFIED",
        notes="Subject of multiple customs surveillance reports at Rotterdam Terminal 4B."
    )
    e_klaus = Entity(
        case_id=case_1.id,
        name="Klaus Richter",
        canonical_name="Klaus Richter",
        entity_type="PERSON",
        aliases=["Herr Richter", "Doc"],
        identifiers={"customs_id": "NL-ROT-9921"},
        risk_level="HIGH",
        attributes={"suspected_role": "Corrupt Customs Specialist", "clearance": "Port Zone 1"},
        verification_status="VERIFIED",
        notes="Senior customs inspection officer suspected of clearing tagged containers without scan."
    )
    e_blue_ocean = Entity(
        case_id=case_1.id,
        name="Blue Ocean Maritime Logistics LLC",
        canonical_name="Blue Ocean Maritime Logistics LLC",
        entity_type="ORGANIZATION",
        aliases=["BO Maritime", "Blue Ocean NV"],
        identifiers={"vat_id": "NL882910401B01", "imo_company": "5921004"},
        risk_level="HIGH",
        attributes={"incorporation": "Rotterdam, Netherlands", "primary_business": "Freight Forwarding"},
        verification_status="VERIFIED",
        notes="Registered owner of commercial storage units at Haven 42."
    )
    e_phone_dmitri = Entity(
        case_id=case_1.id,
        name="+31-6-555-0192",
        canonical_name="+31-6-555-0192",
        entity_type="PHONE_NUMBER",
        aliases=["Rotterdam Burner #1"],
        identifiers={"carrier": "KPN Prepaid", "imei": "864921049281044"},
        risk_level="HIGH",
        attributes={"device": "Nokia 105", "registration": "Anonymous SIM"},
        verification_status="VERIFIED",
        notes="Intercepted in frequent encrypted text exchanges with port shift supervisor."
    )
    e_rotterdam_port = Entity(
        case_id=case_1.id,
        name="Port of Rotterdam Terminal 4B",
        canonical_name="Port of Rotterdam Terminal 4B",
        entity_type="LOCATION",
        aliases=["Haven 4B Pier", "Maasvlakte 2"],
        identifiers={"un_locode": "NLRTM-T4B", "coords": "51.956, 4.021"},
        risk_level="ELEVATED",
        attributes={"type": "Deepwater Container Terminal", "security_level": "ISPS Level 2"},
        verification_status="VERIFIED",
        notes="Primary offloading node for flagged South American transatlantic freight."
    )
    e_sprinter_van = Entity(
        case_id=case_1.id,
        name="Mercedes Sprinter 7-KDX-94",
        canonical_name="Mercedes Sprinter 7-KDX-94",
        entity_type="VEHICLE",
        aliases=["White Cargo Van 94"],
        identifiers={"license_plate": "7-KDX-94", "vin": "WDB9066351S892104"},
        risk_level="HIGH",
        attributes={"color": "White", "make": "Mercedes-Benz Sprinter 316 CDI"},
        verification_status="VERIFIED",
        notes="Observed exiting Pier 42 at 03:15 hours following anomalous container discharge."
    )
    e_crypto_escrow = Entity(
        case_id=case_1.id,
        name="0x71c89f54e129ad4188b02c019a823b41d8e90a88",
        canonical_name="0x71c89f54e129ad4188b02c019a823b41d8e90a88",
        entity_type="FINANCIAL_ACCOUNT",
        aliases=["EVM Multisig Escrow #1"],
        identifiers={"blockchain": "Ethereum", "type": "Smart Contract Multisig"},
        risk_level="CRITICAL",
        attributes={"balance_usd": "$2,450,000 equivalent", "token": "USDT"},
        verification_status="VERIFIED",
        notes="Disbursed automated milestone payouts following confirmed container clearance."
    )

    # Case 2 Entities (Phantom Freight)
    e_dmitri_candidate = Entity(
        case_id=case_2.id,
        name="Dmitry Voronov",
        canonical_name="Dmitry Voronov",
        entity_type="PERSON",
        aliases=["Dmitri V.", "Voronov Consulting"],
        identifiers={"tax_no": "CY-490218-A"},
        risk_level="HIGH",
        attributes={"suspected_role": "Beneficial Owner / Consultant", "jurisdiction": "Limassol, Cyprus"},
        verification_status="UNVERIFIED",
        notes="Listed as non-executive advisor to European shell import companies."
    )
    e_apex_holding = Entity(
        case_id=case_2.id,
        name="Apex Global Logistics Trading Corp",
        canonical_name="Apex Global Logistics Trading Corp",
        entity_type="ORGANIZATION",
        aliases=["Apex Logistics Ltd"],
        identifiers={"reg_number": "CY-HE-481920", "jurisdiction": "Nicosia"},
        risk_level="CRITICAL",
        attributes={"status": "Shell Corporation", "turnover_mismatch": "High"},
        verification_status="VERIFIED",
        notes="Invoiced €8.4M in fictitious maritime warehousing services."
    )
    e_julian_morris = Entity(
        case_id=case_2.id,
        name="Julian Morris",
        canonical_name="Julian Morris",
        entity_type="PERSON",
        aliases=["J. Morris", "The Accountant"],
        identifiers={"passport": "UK-66810291"},
        risk_level="HIGH",
        attributes={"suspected_role": "Corporate Nominee & Escrow Controller", "profession": "Fiduciary Agent"},
        verification_status="VERIFIED",
        notes="Appears as sole nominal director on 14 dormant logistics shell corporations."
    )
    e_iban_cyprus = Entity(
        case_id=case_2.id,
        name="IBAN CY12002001920000049281004128",
        canonical_name="IBAN CY12002001920000049281004128",
        entity_type="FINANCIAL_ACCOUNT",
        aliases=["Hellenic Commercial Account #4128"],
        identifiers={"bank": "Hellenic Maritime Trust", "bic": "HELLCY2N"},
        risk_level="HIGH",
        attributes={"currency": "EUR", "jurisdiction": "Cyprus"},
        verification_status="VERIFIED",
        notes="Transferred €1.2M directly to crypto conversion brokers in Zurich."
    )
    e_antwerp_warehouse = Entity(
        case_id=case_2.id,
        name="Antwerp Customs Bonded Depot 18",
        canonical_name="Antwerp Customs Bonded Depot 18",
        entity_type="LOCATION",
        aliases=["Depot 18 Scheldt"],
        identifiers={"un_locode": "BEANR-D18"},
        risk_level="ELEVATED",
        attributes={"facility": "Bonded Warehousing", "bonded_code": "BE-BOND-88"},
        verification_status="VERIFIED",
        notes="Holding area for transit containers billed by Apex Global Trading."
    )

    # Case 3 Entities (Obsidian Wire)
    e_tariq_al_mansoor = Entity(
        case_id=case_3.id,
        name="Tariq Al-Mansoor",
        canonical_name="Tariq Al-Mansoor",
        entity_type="PERSON",
        aliases=["Abu Rashid", "The Dispatcher"],
        identifiers={"national_id": "AE-784-1982-99021"},
        risk_level="CRITICAL",
        attributes={"suspected_role": "Tactical Fleet Coordinator & Burner Controller", "base": "Dubai / Frankfurt"},
        verification_status="VERIFIED",
        notes="Directs courier vehicle movements across borders using pre-paid encrypted SIMs."
    )
    e_encrypted_phone = Entity(
        case_id=case_3.id,
        name="+49-151-555-0931",
        canonical_name="+49-151-555-0931",
        entity_type="PHONE_NUMBER",
        aliases=["Frankfurt Ghost Line"],
        identifiers={"imei": "358921094829104", "hardware": "Google Pixel 7 (GrapheneOS)"},
        risk_level="HIGH",
        attributes={"encryption": "Signal Private Messenger", "sim_type": "German Roaming eSIM"},
        verification_status="VERIFIED",
        notes="Sent automated coordinates for container drops to Mercedes Sprinter driver."
    )
    e_device_satellite = Entity(
        case_id=case_3.id,
        name="Iridium Extreme 9575 Satellite Terminal",
        canonical_name="Iridium Extreme 9575 Satellite Terminal",
        entity_type="DEVICE",
        aliases=["Satcom Unit Alpha"],
        identifiers={"imei": "300325010928100", "isat_msisdn": "+881631589201"},
        risk_level="HIGH",
        attributes={"network": "Iridium Satellite Network", "encryption": "AES-256 Voice"},
        verification_status="VERIFIED",
        notes="Discovered during warehouse raid; paired with maritime terminal data transmissions."
    )

    db.add_all([
        e_dmitri, e_klaus, e_blue_ocean, e_phone_dmitri, e_rotterdam_port, e_sprinter_van, e_crypto_escrow,
        e_dmitri_candidate, e_apex_holding, e_julian_morris, e_iban_cyprus, e_antwerp_warehouse,
        e_tariq_al_mansoor, e_encrypted_phone, e_device_satellite
    ])
    db.commit()

    # 4. Seed Evidence Documents
    doc_1 = EvidenceDocument(
        case_id=case_1.id,
        title="Rotterdam Customs Intercept Report #RT-2026-04",
        file_name="rotterdam_customs_intercept_04.txt",
        file_type="txt",
        file_size=3240,
        uploaded_by_id=investigator_user.id,
        metadata_info={"classification": "LAW ENFORCEMENT SENSITIVE", "source_unit": "Port Interdiction Group"},
        raw_text="""FEDERAL POLICE & CUSTOMS INTELLIGENCE REPORT
Date: 2026-03-14 | Source: Port Interdiction Group Delta
Subject: Container Discharge Surveillance at Rotterdam Terminal 4B

1. Surveillance Target: Dmitri Voronov (alias "The Ghost") was sighted coordinating with senior customs inspector Klaus Richter at Port of Rotterdam Terminal 4B on March 12, 2026.
2. Communications intercepted between Dmitri Voronov using phone number +31-6-555-0192 and Klaus Richter confirmed agreed inspection override codes for cargo container MSCU-892104.
3. Registered freight entity Blue Ocean Maritime Logistics LLC filed fraudulent manifests stating agricultural machinery. Dmitri Voronov acts as de facto operational director of Blue Ocean Maritime Logistics LLC.
4. White Mercedes Sprinter 7-KDX-94 was observed loading sealed pallets directly from Pier 42 at 03:15 hours, driven under dispatch commands received from phone number +31-6-555-0192.
5. On-chain forensic tracing verified that Klaus Richter received an escrow milestone deposit from Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88 totaling $250,000 USDT following departure of the vehicle.
"""
    )

    doc_2 = EvidenceDocument(
        case_id=case_2.id,
        title="Financial Crimes Unit Audit: Apex Global Trading",
        file_name="fiu_audit_apex_cyprus.txt",
        file_type="txt",
        file_size=2980,
        uploaded_by_id=investigator_user.id,
        metadata_info={"classification": "CONFIDENTIAL FINANCIAL INTELLIGENCE", "source_unit": "FIU Special Audit"},
        raw_text="""FINANCIAL INTELLIGENCE UNIT (FIU) SPECIAL AUDIT MEMO
Date: 2026-04-02 | Case: Operation Phantom Freight (CR-2026-0944)
Subject: Shell Company Invoicing & Asset Off-Ramps

1. Corporate Entity Review: Apex Global Logistics Trading Corp was incorporated in Nicosia, Cyprus under registration CY-HE-481920. Julian Morris is listed as nominal director and sole signatory.
2. Inward wire transfers totaling €4,200,000 were remitted to IBAN CY12002001920000049281004128 held by Apex Global Logistics Trading Corp.
3. Intelligence from cross-border banking alerts indicates Julian Morris operates strictly on the instructions of consultant Dmitry Voronov (listed in advisory contracts as Dmitri V.).
4. Freight bills show shipments purported to route through Antwerp Customs Bonded Depot 18 without corresponding port crane physical log entries.
5. High-risk cross-case financial tie: Forensic blockchain graph reveals IBAN CY12002001920000049281004128 funded the deployment of Ethereum multisig wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88, establishing direct financial lineage between Cyprus shell companies and Rotterdam maritime logistics.
"""
    )

    doc_3 = EvidenceDocument(
        case_id=case_3.id,
        title="Tactical Cyber Intercept: Burner Telemetry Log",
        file_name="telecom_intercept_obsidian_wire.txt",
        file_type="txt",
        file_size=2450,
        uploaded_by_id=investigator_user.id,
        metadata_info={"classification": "SECRET / NOFORN", "source_unit": "Technical Surveillance Branch"},
        raw_text="""TECHNICAL SURVEILLANCE BRANCH - INTERCEPT REPORT
Date: 2026-04-18 | Case: Operation Obsidian Wire (CR-2026-1105)
Subject: Encrypted Device Pairing & Tactical Transport Dispatch

1. Tactical Coordinator: Tariq Al-Mansoor operated encrypted communications line +49-151-555-0931 transmitting GPS waypoints and automated dead-drop confirmation triggers.
2. Surveillance confirms Tariq Al-Mansoor paired Iridium Extreme 9575 Satellite Terminal with high-frequency encrypted relays to transmit dispatch orders across international borders.
3. Signal intercept on April 15 revealed repeated tactical coordination between +49-151-555-0931 and burner phone +31-6-555-0192 regarding scheduled arrival of vehicle Mercedes Sprinter 7-KDX-94.
4. GPS telematics placed Mercedes Sprinter 7-KDX-94 at Antwerp Customs Bonded Depot 18 just 14 hours after departing Rotterdam Terminal 4B, linking all three operational jurisdictions.
"""
    )

    db.add_all([doc_1, doc_2, doc_3])
    db.commit()

    # 5. Seed Relationships with Evidence References (Provenance Engine)
    # Relationship 1: Dmitri Voronov <-> Klaus Richter (COMMUNICATED_WITH)
    r1 = Relationship(
        source_id=e_dmitri.id,
        target_id=e_klaus.id,
        case_id=case_1.id,
        relation_type="COMMUNICATED_WITH",
        confidence_score=0.96,
        temporal_start=datetime.datetime(2026, 3, 12, 14, 20),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 3, 15, 10, 0),
        weight=1.5,
        is_bidirectional=True
    )
    # Relationship 2: Dmitri Voronov -> Blue Ocean Maritime Logistics LLC (SUSPECTED_HANDLER_OF)
    r2 = Relationship(
        source_id=e_dmitri.id,
        target_id=e_blue_ocean.id,
        case_id=case_1.id,
        relation_type="SUSPECTED_HANDLER_OF",
        confidence_score=0.92,
        temporal_start=datetime.datetime(2025, 11, 1),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 3, 15, 10, 30),
        weight=2.0
    )
    # Relationship 3: Dmitri Voronov -> +31-6-555-0192 (OWNER_OF)
    r3 = Relationship(
        source_id=e_dmitri.id,
        target_id=e_phone_dmitri.id,
        case_id=case_1.id,
        relation_type="OWNER_OF",
        confidence_score=0.98,
        temporal_start=datetime.datetime(2026, 1, 10),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 3, 15, 11, 0),
        weight=1.0
    )
    # Relationship 4: Blue Ocean -> Port of Rotterdam Terminal 4B (LOCATED_AT)
    r4 = Relationship(
        source_id=e_blue_ocean.id,
        target_id=e_rotterdam_port.id,
        case_id=case_1.id,
        relation_type="LOCATED_AT",
        confidence_score=0.95,
        temporal_start=datetime.datetime(2025, 6, 1),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 3, 15, 11, 15),
        weight=1.0
    )
    # Relationship 5: +31-6-555-0192 -> Mercedes Sprinter 7-KDX-94 (OPERATES_VEHICLE)
    r5 = Relationship(
        source_id=e_phone_dmitri.id,
        target_id=e_sprinter_van.id,
        case_id=case_1.id,
        relation_type="OPERATES_VEHICLE",
        confidence_score=0.91,
        temporal_start=datetime.datetime(2026, 3, 12, 3, 15),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 3, 15, 11, 30),
        weight=1.2
    )
    # Relationship 6: 0x71c89f54e129ad4188b02c019a823b41d8e90a88 -> Klaus Richter (TRANSFERRED_FUNDS_TO)
    r6 = Relationship(
        source_id=e_crypto_escrow.id,
        target_id=e_klaus.id,
        case_id=case_1.id,
        relation_type="TRANSFERRED_FUNDS_TO",
        confidence_score=0.99,
        temporal_start=datetime.datetime(2026, 3, 12, 4, 30),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 3, 15, 12, 0),
        weight=2.5
    )

    # Case 2 Relationships
    # Relationship 7: Julian Morris -> Apex Global Logistics Trading Corp (MEMBER_OF)
    r7 = Relationship(
        source_id=e_julian_morris.id,
        target_id=e_apex_holding.id,
        case_id=case_2.id,
        relation_type="MEMBER_OF",
        confidence_score=0.97,
        temporal_start=datetime.datetime(2024, 8, 14),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 4, 3, 14, 0),
        weight=1.5
    )
    # Relationship 8: Dmitry Voronov -> Julian Morris (SUSPECTED_HANDLER_OF) [PENDING REVIEW]
    r8 = Relationship(
        source_id=e_dmitri_candidate.id,
        target_id=e_julian_morris.id,
        case_id=case_2.id,
        relation_type="SUSPECTED_HANDLER_OF",
        confidence_score=0.86,
        temporal_start=datetime.datetime(2025, 1, 1),
        verification_status="PENDING_REVIEW",
        weight=1.8
    )
    # Relationship 9: Apex Global Logistics Trading Corp -> IBAN CY12002001920000049281004128 (OWNER_OF)
    r9 = Relationship(
        source_id=e_apex_holding.id,
        target_id=e_iban_cyprus.id,
        case_id=case_2.id,
        relation_type="OWNER_OF",
        confidence_score=0.99,
        temporal_start=datetime.datetime(2024, 9, 1),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 4, 3, 14, 30),
        weight=2.0
    )
    # Relationship 10: Apex Global -> Antwerp Customs Bonded Depot 18 (LOCATED_AT)
    r10 = Relationship(
        source_id=e_apex_holding.id,
        target_id=e_antwerp_warehouse.id,
        case_id=case_2.id,
        relation_type="LOCATED_AT",
        confidence_score=0.88,
        temporal_start=datetime.datetime(2025, 4, 1),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 4, 3, 15, 0),
        weight=1.0
    )
    # Relationship 11: Cross-case bridge: IBAN CY12... -> 0x71c89f54e129ad4188b02c019a823b41d8e90a88 (TRANSFERRED_FUNDS_TO)
    r11 = Relationship(
        source_id=e_iban_cyprus.id,
        target_id=e_crypto_escrow.id,
        case_id=case_2.id,
        relation_type="TRANSFERRED_FUNDS_TO",
        confidence_score=0.94,
        temporal_start=datetime.datetime(2026, 2, 18),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 4, 4, 9, 30),
        weight=2.8
    )

    # Case 3 Relationships
    # Relationship 12: Tariq Al-Mansoor -> +49-151-555-0931 (OWNER_OF)
    r12 = Relationship(
        source_id=e_tariq_al_mansoor.id,
        target_id=e_encrypted_phone.id,
        case_id=case_3.id,
        relation_type="OWNER_OF",
        confidence_score=0.95,
        temporal_start=datetime.datetime(2026, 2, 1),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 4, 19, 11, 0),
        weight=1.0
    )
    # Relationship 13: Tariq Al-Mansoor -> Iridium Extreme 9575 Satellite Terminal (OWNER_OF)
    r13 = Relationship(
        source_id=e_tariq_al_mansoor.id,
        target_id=e_device_satellite.id,
        case_id=case_3.id,
        relation_type="OWNER_OF",
        confidence_score=0.93,
        temporal_start=datetime.datetime(2026, 1, 15),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 4, 19, 11, 30),
        weight=1.0
    )
    # Relationship 14: Cross-case bridge: +49-151-555-0931 <-> +31-6-555-0192 (COMMUNICATED_WITH) [PENDING REVIEW]
    r14 = Relationship(
        source_id=e_encrypted_phone.id,
        target_id=e_phone_dmitri.id,
        case_id=case_3.id,
        relation_type="COMMUNICATED_WITH",
        confidence_score=0.89,
        temporal_start=datetime.datetime(2026, 4, 15, 21, 40),
        verification_status="PENDING_REVIEW",
        weight=1.6,
        is_bidirectional=True
    )
    # Relationship 15: Mercedes Sprinter 7-KDX-94 -> Antwerp Customs Bonded Depot 18 (LOCATED_AT)
    r15 = Relationship(
        source_id=e_sprinter_van.id,
        target_id=e_antwerp_warehouse.id,
        case_id=case_3.id,
        relation_type="LOCATED_AT",
        confidence_score=0.94,
        temporal_start=datetime.datetime(2026, 3, 13, 17, 30),
        verification_status="VERIFIED",
        verified_by_id=investigator_user.id,
        verified_at=datetime.datetime(2026, 4, 20, 10, 0),
        weight=1.5
    )

    db.add_all([r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15])
    db.commit()

    # 6. Seed Evidence References (Provenance Engine)
    ref_1 = EvidenceReference(
        evidence_document_id=doc_1.id,
        relationship_id=r1.id,
        entity_id=e_dmitri.id,
        case_id=case_1.id,
        excerpt='Surveillance Target: Dmitri Voronov (alias "The Ghost") was sighted coordinating with senior customs inspector Klaus Richter at Port of Rotterdam Terminal 4B on March 12, 2026.',
        page_number=1,
        line_number=4,
        char_offset_start=135,
        char_offset_end=312,
        extraction_confidence=0.96,
        provenance_notes="Visual sighting logged by surveillance team Bravo with photographic timestamp confirmation."
    )
    ref_2 = EvidenceReference(
        evidence_document_id=doc_1.id,
        relationship_id=r6.id,
        entity_id=e_crypto_escrow.id,
        case_id=case_1.id,
        excerpt="On-chain forensic tracing verified that Klaus Richter received an escrow milestone deposit from Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88 totaling $250,000 USDT following departure of the vehicle.",
        page_number=1,
        line_number=8,
        char_offset_start=810,
        char_offset_end=1025,
        extraction_confidence=0.99,
        provenance_notes="Blockchain transaction hash: 0x98f41... verified via public ledger explorer and exchange KYC."
    )
    ref_3 = EvidenceReference(
        evidence_document_id=doc_2.id,
        relationship_id=r11.id,
        entity_id=e_iban_cyprus.id,
        case_id=case_2.id,
        excerpt="Forensic blockchain graph reveals IBAN CY12002001920000049281004128 funded the deployment of Ethereum multisig wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88, establishing direct financial lineage between Cyprus shell companies and Rotterdam maritime logistics.",
        page_number=1,
        line_number=8,
        char_offset_start=890,
        char_offset_end=1160,
        extraction_confidence=0.94,
        provenance_notes="Financial intelligence unit bank audit and on-ramp gateway KYC correlation."
    )
    ref_4 = EvidenceReference(
        evidence_document_id=doc_3.id,
        relationship_id=r14.id,
        entity_id=e_encrypted_phone.id,
        case_id=case_3.id,
        excerpt="Signal intercept on April 15 revealed repeated tactical coordination between +49-151-555-0931 and burner phone +31-6-555-0192 regarding scheduled arrival of vehicle Mercedes Sprinter 7-KDX-94.",
        page_number=1,
        line_number=6,
        char_offset_start=540,
        char_offset_end=735,
        extraction_confidence=0.89,
        provenance_notes="Cell tower signal tap under judicial warrant #JW-2026-441."
    )
    db.add_all([ref_1, ref_2, ref_3, ref_4])
    db.commit()

    # 7. Seed Uncertainty-Aware Entity Match Suggestions
    match_sug = EntityMatchSuggestion(
        primary_entity_id=e_dmitri.id,
        candidate_entity_id=e_dmitri_candidate.id,
        similarity_score=0.88,
        match_reasons=[
            "High phonetic and Levenshtein name similarity between 'Dmitri Voronov' and 'Dmitry Voronov' (0.92)",
            "Shared alias 'D. Voronov' documented in Cyprus advisory contracts",
            "Co-occurrence in maritime logistics financial flows involving wallet 0x71c89f..."
        ],
        status="PENDING",
        review_notes="Investigator review required to confirm if Dmitry Voronov (Cyprus consultant) is the identical individual behind maritime front company."
    )
    db.add(match_sug)
    db.commit()

    # 8. Seed Explainable Network Pattern Alerts
    alert_1 = NetworkPatternAlert(
        case_id=case_1.id,
        alert_type="CROSS_CASE_OVERLAP",
        severity="CRITICAL",
        title="Cross-Case Capital Convergence: Wallet 0x71c89f...",
        explanation="Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88 acts as a financial nexus linking Operation Blue Horizon (Case CR-2026-0812) and Operation Phantom Freight (Case CR-2026-0944). Funds originated from Cyprus IBAN CY12002... and were subsequently disbursed to Rotterdam customs inspector Klaus Richter.",
        confidence=0.96,
        affected_entities=[e_crypto_escrow.id, e_iban_cyprus.id, e_klaus.id],
        affected_relationships=[r6.id, r11.id],
        status="NEW"
    )
    alert_2 = NetworkPatternAlert(
        case_id=case_3.id,
        alert_type="CROSS_CASE_OVERLAP",
        severity="HIGH",
        title="Cross-Jurisdictional Burner Telemetry: +31-6-555-0192",
        explanation="Burner phone +31-6-555-0192 registered in Operation Blue Horizon was detected communicating directly with tactical coordinator Tariq Al-Mansoor (+49-151-555-0931) in Operation Obsidian Wire. This relationship is currently PENDING HUMAN VERIFICATION.",
        confidence=0.89,
        affected_entities=[e_phone_dmitri.id, e_encrypted_phone.id, e_tariq_al_mansoor.id],
        affected_relationships=[r14.id],
        status="NEW"
    )
    alert_3 = NetworkPatternAlert(
        case_id=case_1.id,
        alert_type="HIGH_CENTRALITY_UNVERIFIED",
        severity="MEDIUM",
        title="High Bridge Centrality with Unverified Links: Julian Morris",
        explanation="Entity Julian Morris acts as the sole topological gateway between Cyprus banking entities and suspected coordinator Dmitry Voronov. Relationship link #r8 is unverified. If this link is disproven, the network separates into two disconnected clusters.",
        confidence=0.86,
        affected_entities=[e_julian_morris.id, e_dmitri_candidate.id],
        affected_relationships=[r8.id],
        status="NEW"
    )
    db.add_all([alert_1, alert_2, alert_3])
    db.commit()

    # 9. Seed Audit Logs
    audit_1 = AuditLog(
        user_id=investigator_user.id,
        action="CREATE_CASE",
        entity_type="CASE",
        entity_id=case_1.id,
        case_id=case_1.id,
        details={"case_number": case_1.case_number, "title": case_1.title},
        ip_address="10.200.4.12"
    )
    audit_2 = AuditLog(
        user_id=investigator_user.id,
        action="UPLOAD_EVIDENCE",
        entity_type="EVIDENCE_DOCUMENT",
        entity_id=doc_1.id,
        case_id=case_1.id,
        details={"document_title": doc_1.title, "file_name": doc_1.file_name},
        ip_address="10.200.4.12"
    )
    audit_3 = AuditLog(
        user_id=investigator_user.id,
        action="VERIFY_RELATIONSHIP",
        entity_type="RELATIONSHIP",
        entity_id=r1.id,
        case_id=case_1.id,
        details={"relation_type": r1.relation_type, "source_id": r1.source_id, "target_id": r1.target_id, "previous_status": "PENDING_REVIEW", "new_status": "VERIFIED"},
        ip_address="10.200.4.12"
    )
    db.add_all([audit_1, audit_2, audit_3])
    db.commit()

    print("[+] Synthetic demonstration dataset successfully initialized with 3 cases, 15 entities, 15 relationships, 3 evidence reports, and 4 provenance references.")
