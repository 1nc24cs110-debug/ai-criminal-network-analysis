import datetime
import random
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from backend.models import (
    User, Case, Entity, Relationship, EvidenceDocument,
    EvidenceReference, EntityMatchSuggestion, NetworkPatternAlert, AuditLog
)
from backend.auth import hash_password

class SyntheticDataEngine:
    """
    Advanced Synthetic Data Engine for Criminal Network Intelligence Demonstrations.
    Provides realistic, ethically safe synthetic investigation datasets, multi-jurisdiction
    scenarios, dynamic network generation, and downloadable evidence samples.
    """

    SAMPLE_DOCUMENTS = [
        {
            "id": "sample_rotterdam_customs",
            "title": "Rotterdam Port Pier 42 Surveillance & Customs Shift Intercept",
            "category": "Port Interdiction & Maritime Contraband",
            "jurisdiction": "Port Interdiction Group Delta / Europol Liaison",
            "text": """FEDERAL POLICE & CUSTOMS INTELLIGENCE REPORT
Classification: LAW ENFORCEMENT SENSITIVE // REL TO JUDICIAL
Date: 2026-03-14 | Source: Port Interdiction Group Delta
Subject: Container Discharge Surveillance at Rotterdam Terminal 4B

1. Sighting: Target Dmitri Voronov (alias "The Ghost", a.k.a. "DV-7") was spotted coordinating with senior customs inspector Klaus Richter near Port of Rotterdam Terminal 4B.
2. Intercept on phone +31-6-555-0192 (registered to KPN Prepaid, IMEI: 864921049281044) confirmed agreed inspection override codes for cargo container MSCU-892104.
3. Logistics Cover: Front organization Blue Ocean Maritime Logistics LLC filed manifests stating agricultural machinery. Dmitri Voronov acts as de facto director of Blue Ocean Maritime Logistics LLC.
4. Logistics Dispatch: White Mercedes Sprinter 7-KDX-94 (VIN: WDB9066351S892104) loaded sealed pallets directly from Pier 42 at 03:15 hours, driven under dispatch commands received from phone +31-6-555-0192.
5. Financial Settlement: Forensic tracing confirmed Klaus Richter received an escrow milestone deposit from Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88 totaling $250,000 USDT following departure of the vehicle.
"""
        },
        {
            "id": "sample_fiu_cyprus_shell",
            "title": "FIU Special Audit: Front Company Invoicing & Asset Off-Ramps",
            "category": "Trade-Based Money Laundering & Shell Entities",
            "jurisdiction": "Financial Crimes Enforcement Unit",
            "text": """FINANCIAL INTELLIGENCE UNIT (FIU) SPECIAL AUDIT MEMO
Classification: CONFIDENTIAL FINANCIAL INTELLIGENCE
Date: 2026-04-02 | Case: Operation Phantom Freight (CR-2026-0944)
Subject: Shell Company Invoicing & Asset Off-Ramps

1. Corporate Structure: Apex Global Logistics Trading Corp was incorporated in Nicosia, Cyprus under registration CY-HE-481920. Julian Morris is nominal director and sole banking signatory.
2. Inward Transfers: €4,200,000 in fake freight bills were remitted to IBAN CY12002001920000049281004128 held by Apex Global Logistics Trading Corp at Hellenic Maritime Trust.
3. Hidden Handler: Cross-border banking alerts indicate Julian Morris acts under explicit directives from advisor Dmitry Voronov (listed in advisory contracts as Dmitri V.).
4. Fake Movements: Bills show freight routing through Antwerp Customs Bonded Depot 18 without corresponding port crane physical entries.
5. Cross-Case Ledger Link: Forensic blockchain tracing verified IBAN CY12002001920000049281004128 funded deployment of Ethereum wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88, establishing direct capital lineage between Cyprus shell companies and Rotterdam maritime logistics.
"""
        },
        {
            "id": "sample_darknet_mixer",
            "title": "Cybercrime & Darknet Crypto Mixer Ledger Audit",
            "category": "Crypto Asset Laundering & Mixers",
            "jurisdiction": "Cyber Asset Recovery Unit / FinCEN Liaison",
            "text": """CYBER FINANCIAL TRACING MEMORANDUM
Classification: RESTRICTED // FORENSIC INTELLIGENCE
Date: 2026-05-10 | Case: Operation Eclipse Nexus (CR-2026-1402)
Subject: Darknet Marketplace Capital Off-Ramps via Decentralized Mixers

1. Target Nexus: Darknet vendor syndicate identified operating under handle "Eclipse Broker" on decentralized marketplace SilkRoad 4.0.
2. Primary Ingestion Wallet: Bitcoin address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa received 142.8 BTC in automated vendor disbursements.
3. Cross-Chain Swap: Funds were converted to Ethereum through bridge contract 0x00000000219ab540356cBB839Cbe05303d7705Fa and funneled into privacy mixer contract 0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc.
4. Cashout Recipient: Multiple unpegged transfers totaling €850,000 exited to Account #88192044 held by nominee courier Elena Rostova at Zurich Private Bank.
5. Hardware Intercept: Laptop recovered during border check contained private key backups corresponding to Account #88192044 and encrypted Signal messages from +49-151-555-0931.
"""
        },
        {
            "id": "sample_border_convoy",
            "title": "Tactical Vehicle Interdiction & Encrypted Radio Telematics",
            "category": "Border Smuggling & Vehicle Tracking",
            "jurisdiction": "Border Enforcement Taskforce",
            "text": """TACTICAL FIELD INTERDICTION REPORT
Classification: LAW ENFORCEMENT SENSITIVE
Date: 2026-04-18 | Case: Operation Obsidian Wire (CR-2026-1105)
Subject: Encrypted Device Pairing & Tactical Transport Dispatch

1. Coordinator: Target Tariq Al-Mansoor operated tactical mobile device +49-151-555-0931 transmitting GPS coordinates to regional dispatch drivers.
2. Device Hardware: Tariq Al-Mansoor was intercepted with an Iridium Extreme 9575 Satellite Terminal (IMEI: 300325010928100) configured with satellite relay channels.
3. Telecommunications Intercept: Intercepted communications between +49-151-555-0931 and Rotterdam burner line +31-6-555-0192 coordinated arrival of vehicle Mercedes Sprinter 7-KDX-94.
4. Logistics Staging: Vehicle Mercedes Sprinter 7-KDX-94 was tracked entering Antwerp Customs Bonded Depot 18 fourteen hours after departing Rotterdam Terminal 4B, linking maritime and land logistics.
"""
        },
        {
            "id": "sample_ransomware_nexus",
            "title": "Operation Cobalt Ghost: Extortion Escrow & Shell Transit",
            "category": "Cyber Syndicate & Extortion Flow",
            "jurisdiction": "Special Cyber Investigations Branch",
            "text": """SPECIAL CYBER INVESTIGATIONS MEMO
Classification: CONFIDENTIAL // LAW ENFORCEMENT
Date: 2026-06-01 | Case: Operation Cobalt Ghost (CR-2026-1590)
Subject: Ransomware Infrastructure & Multi-Signature Settlement

1. Syndicate Infrastructure: Threat actor group "Cobalt Ghost" operated command server infrastructure leased under shell organization Titan Cyber Dynamics LLC.
2. Nominal Controller: Subject Anton Kozlov (alias "Zero-Day") directed technical deployment from server farm located at Frankfurt Data Center Zone 3.
3. Extortion Escrow: Corporate victim wired 1,200,000 USDT to Ethereum address 0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE under extortion threat.
4. Layering Transit: Funds were immediately bridged into multisig wallet 0x71c89f54e129ad4188b02c019a823b41d8e90a88, matching the maritime escrow wallet identified in Operation Blue Horizon.
5. Tactical Phone Link: Anton Kozlov communicated via burner number +44-7700-900821 with logistics broker Julian Morris in Limassol.
"""
        },
        {
            "id": "sample_informant_debrief",
            "title": "Confidential Informant Debriefing on Shadow Syndicate Handlers",
            "category": "Human Intelligence (HUMINT)",
            "jurisdiction": "Special Field Operations Branch",
            "text": """HUMINT SOURCE DEBRIEFING MEMORANDUM
Classification: SECRET // REL TO INVESTIGATIVE TEAM ONLY
Date: 2026-06-15 | Source: Reliable Informant CI-8819 ("Sparrow")
Subject: Strategic Handlers Behind Transnational Transport & Banking

1. Source Statement: CI-8819 met with consultant Dmitry Voronov at Hotel Martinez in Geneva. Voronov confirmed he controls operational mandates for both Blue Ocean Maritime Logistics LLC and Apex Global Logistics Trading Corp.
2. Nominee Management: Julian Morris acts solely as nominee director and receives €15,000 monthly retainer for signing corporate board resolutions.
3. Burner Device Protocol: All inter-cell logistics instructions are relayed through burner phone +31-6-555-0192 using single-use SIM cards destroyed every 14 days.
4. Fleet Operations: The syndicate maintains three transport vehicles, including Mercedes Sprinter 7-KDX-94, equipped with hidden hydraulic floor compartments for high-value contraband.
5. Judicial Note: Informant statements require corroborating telemetry and financial subpoena validation before evidentiary filing.
"""
        }
    ]

    SCENARIOS = {
        "BLUE_HORIZON": {
            "id": "BLUE_HORIZON",
            "title": "Operation Blue Horizon: Maritime Port & Customs Bribery",
            "description": "Cross-border maritime contraband syndicate infiltrating Rotterdam and Antwerp container ports with corrupt customs officials and crypto escrow payouts.",
            "cases_count": 3,
            "entities_count": 15,
            "relationships_count": 15,
            "focus": "Maritime Contraband, Port Infiltration, Burner SIMs, Crypto Escrow"
        },
        "ECLIPSE_NEXUS": {
            "id": "ECLIPSE_NEXUS",
            "title": "Operation Eclipse Nexus: Darknet Marketplace & Privacy Mixers",
            "description": "Darknet marketplace narcotics trade layered through Tornado Cash mixers, decentralized cross-chain swaps, and European luxury couriers.",
            "cases_count": 3,
            "entities_count": 20,
            "relationships_count": 24,
            "focus": "Darknet Markets, Bitcoin/EVM Mixers, Zurich Nominee Accounts"
        },
        "COBALT_GHOST": {
            "id": "COBALT_GHOST",
            "title": "Operation Cobalt Ghost: Cyber Extortion & Offshore Fronts",
            "description": "Transnational ransomware syndicate laundering corporate extortion revenue through Cyprus shell companies, Dubai real estate, and burner mobile networks.",
            "cases_count": 3,
            "entities_count": 22,
            "relationships_count": 26,
            "focus": "Ransomware Escrow, Shell Invoicing, Command-and-Control Servers"
        },
        "MASTER_COMPLEX": {
            "id": "MASTER_COMPLEX",
            "title": "Master Multi-Agency Mega-Network (Comprehensive Hackathon Demo)",
            "description": "Unified 5-case super-network connecting maritime ports, trade laundering, darknet mixing, cyber extortion, and tactical vehicle dispatch into a dense multi-cluster web.",
            "cases_count": 5,
            "entities_count": 38,
            "relationships_count": 48,
            "focus": "Full Spectrum Transnational Crime, Multi-Case Overlaps, High-Betweenness Bridges, Anomalies"
        }
    }

    @classmethod
    def list_scenarios(cls) -> List[Dict[str, Any]]:
        return list(cls.SCENARIOS.values())

    @classmethod
    def list_samples(cls) -> List[Dict[str, Any]]:
        return cls.SAMPLE_DOCUMENTS

    @classmethod
    def reset_to_default(cls, db: Session) -> Dict[str, Any]:
        """Clears existing dynamic data and restores pristine initial demonstration dataset."""
        # Clean existing tables except users
        db.query(EvidenceReference).delete()
        db.query(EvidenceDocument).delete()
        db.query(Relationship).delete()
        db.query(EntityMatchSuggestion).delete()
        db.query(NetworkPatternAlert).delete()
        db.query(Entity).delete()
        db.query(Case).delete()
        db.query(AuditLog).delete()
        db.commit()

        # Re-import and run seed
        from backend.synthetic_data import seed_database
        seed_database(db)

        return {
            "status": "success",
            "message": "System successfully restored to default synthetic demonstration baseline.",
            "cases": db.query(Case).count(),
            "entities": db.query(Entity).count(),
            "relationships": db.query(Relationship).count()
        }

    @classmethod
    def load_scenario(cls, scenario_id: str, db: Session) -> Dict[str, Any]:
        """Loads a specific pre-packaged scenario into the database."""
        scenario = cls.SCENARIOS.get(scenario_id)
        if not scenario:
            scenario = cls.SCENARIOS["BLUE_HORIZON"]

        # Clear active cases, entities, relations
        db.query(EvidenceReference).delete()
        db.query(EvidenceDocument).delete()
        db.query(Relationship).delete()
        db.query(EntityMatchSuggestion).delete()
        db.query(NetworkPatternAlert).delete()
        db.query(Entity).delete()
        db.query(Case).delete()
        db.commit()

        # Ensure investigator user exists
        inv_user = db.query(User).filter(User.username == "investigator").first()
        if not inv_user:
            from backend.synthetic_data import seed_database
            seed_database(db)
            inv_user = db.query(User).filter(User.username == "investigator").first()

        if scenario_id == "ECLIPSE_NEXUS":
            cls._load_eclipse_nexus(db, inv_user)
        elif scenario_id == "COBALT_GHOST":
            cls._load_cobalt_ghost(db, inv_user)
        elif scenario_id == "MASTER_COMPLEX":
            cls._load_master_complex(db, inv_user)
        else:
            from backend.synthetic_data import seed_database
            seed_database(db)

        return {
            "status": "success",
            "scenario": scenario["title"],
            "cases": db.query(Case).count(),
            "entities": db.query(Entity).count(),
            "relationships": db.query(Relationship).count(),
            "documents": db.query(EvidenceDocument).count()
        }

    @classmethod
    def _load_eclipse_nexus(cls, db: Session, user: User):
        c1 = Case(
            case_number="CR-2026-1402",
            title="Operation Eclipse Nexus: Darknet Marketplace Syndicate",
            summary="Investigation into multi-vendor decentralized narcotics distribution and Bitcoin ledger laundering.",
            status="ACTIVE",
            priority="CRITICAL",
            jurisdiction="Cyber Asset Recovery Taskforce",
            lead_investigator_id=user.id,
            tags=["darknet", "crypto-mixer", "narcotics", "cross-border"]
        )
        c2 = Case(
            case_number="CR-2026-1455",
            title="Operation Swiss Shield: Private Banking Nominee Off-Ramps",
            summary="Tracking nominee bank accounts and cashout brokers converting mixer outputs to Swiss real estate.",
            status="ACTIVE",
            priority="HIGH",
            jurisdiction="Financial Intelligence Directorate",
            lead_investigator_id=user.id,
            tags=["private-banking", "zurich", "cashout-courier"]
        )
        db.add_all([c1, c2])
        db.commit()

        # Entities
        e1 = Entity(case_id=c1.id, name="SilkRoad 4.0 Vendor Portal", entity_type="ORGANIZATION", risk_level="CRITICAL", verification_status="VERIFIED", attributes={"role": "Decentralized Marketplace Hub"})
        e2 = Entity(case_id=c1.id, name="BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", entity_type="FINANCIAL_ACCOUNT", risk_level="CRITICAL", verification_status="VERIFIED", identifiers={"crypto": "BTC"}, attributes={"balance": "142.8 BTC"})
        e3 = Entity(case_id=c1.id, name="Tornado EVM Mixer 0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc", entity_type="FINANCIAL_ACCOUNT", risk_level="HIGH", verification_status="VERIFIED", identifiers={"type": "Smart Contract Mixer"})
        e4 = Entity(case_id=c1.id, name="Nikolai Morozov", entity_type="PERSON", aliases=["ShadowNet", "Eclipse Broker"], risk_level="CRITICAL", verification_status="VERIFIED", attributes={"role": "Marketplace Escrow Administrator"})
        e5 = Entity(case_id=c1.id, name="+49-170-555-0819", entity_type="PHONE_NUMBER", risk_level="HIGH", verification_status="VERIFIED", attributes={"carrier": "Telekom Prepaid"})

        e6 = Entity(case_id=c2.id, name="Elena Rostova", entity_type="PERSON", aliases=["The Courier"], risk_level="HIGH", verification_status="VERIFIED", attributes={"role": "Nominee Cashout Courier"})
        e7 = Entity(case_id=c2.id, name="Account #88192044", entity_type="FINANCIAL_ACCOUNT", risk_level="HIGH", verification_status="VERIFIED", identifiers={"bank": "Zurich Private Bank"})
        e8 = Entity(case_id=c2.id, name="Audi RS6 (Plate: ZH-89210)", entity_type="VEHICLE", risk_level="HIGH", verification_status="VERIFIED", identifiers={"plate": "ZH-89210"})
        e9 = Entity(case_id=c2.id, name="Zurich Vault Terminal 3", entity_type="LOCATION", risk_level="ELEVATED", verification_status="VERIFIED")

        db.add_all([e1, e2, e3, e4, e5, e6, e7, e8, e9])
        db.commit()

        # Relationships
        r1 = Relationship(source_id=e4.id, target_id=e1.id, case_id=c1.id, relation_type="SUSPECTED_HANDLER_OF", confidence_score=0.96, verification_status="VERIFIED")
        r2 = Relationship(source_id=e1.id, target_id=e2.id, case_id=c1.id, relation_type="TRANSFERRED_FUNDS_TO", confidence_score=0.99, verification_status="VERIFIED")
        r3 = Relationship(source_id=e2.id, target_id=e3.id, case_id=c1.id, relation_type="TRANSFERRED_FUNDS_TO", confidence_score=0.95, verification_status="VERIFIED")
        r4 = Relationship(source_id=e4.id, target_id=e5.id, case_id=c1.id, relation_type="OWNER_OF", confidence_score=0.94, verification_status="VERIFIED")
        # Cross-case link
        r5 = Relationship(source_id=e3.id, target_id=e7.id, case_id=c2.id, relation_type="TRANSFERRED_FUNDS_TO", confidence_score=0.92, verification_status="VERIFIED")
        r6 = Relationship(source_id=e6.id, target_id=e7.id, case_id=c2.id, relation_type="OWNER_OF", confidence_score=0.98, verification_status="VERIFIED")
        r7 = Relationship(source_id=e6.id, target_id=e8.id, case_id=c2.id, relation_type="OPERATES_VEHICLE", confidence_score=0.91, verification_status="VERIFIED")
        r8 = Relationship(source_id=e8.id, target_id=e9.id, case_id=c2.id, relation_type="LOCATED_AT", confidence_score=0.88, verification_status="VERIFIED")
        # Unverified cross-case bridge
        r9 = Relationship(source_id=e5.id, target_id=e6.id, case_id=c1.id, relation_type="COMMUNICATED_WITH", confidence_score=0.86, verification_status="PENDING_REVIEW")

        db.add_all([r1, r2, r3, r4, r5, r6, r7, r8, r9])

        # Documents
        doc = EvidenceDocument(
            case_id=c1.id,
            title=cls.SAMPLE_DOCUMENTS[2]["title"],
            file_name="darknet_crypto_mixer_audit.txt",
            file_type="txt",
            file_size=2800,
            uploaded_by_id=user.id,
            raw_text=cls.SAMPLE_DOCUMENTS[2]["text"]
        )
        db.add(doc)
        db.commit()

        # Alerts
        al = NetworkPatternAlert(
            case_id=c1.id,
            alert_type="CROSS_CASE_OVERLAP",
            severity="CRITICAL",
            title="Cross-Case Decentralized Mixer Flow: EVM Mixer ➔ Zurich Private Bank",
            explanation="Privacy mixer contract 0x12D66f... links darknet vendor SilkRoad 4.0 (CR-2026-1402) with cashout courier Elena Rostova (CR-2026-1455).",
            confidence=0.94,
            affected_entities=[e3.id, e7.id, e6.id],
            affected_relationships=[r5.id],
            status="NEW"
        )
        db.add(al)
        db.commit()

    @classmethod
    def _load_cobalt_ghost(cls, db: Session, user: User):
        c1 = Case(
            case_number="CR-2026-1590",
            title="Operation Cobalt Ghost: Corporate Cyber Extortion",
            summary="Transnational ransomware group extorting critical infrastructure and laundering funds through shell corporate accounts.",
            status="ACTIVE",
            priority="CRITICAL",
            jurisdiction="Special Cyber Counter-Extortion Division",
            lead_investigator_id=user.id,
            tags=["ransomware", "extortion", "cyber-syndicate", "offshore"]
        )
        db.add(c1)
        db.commit()

        e1 = Entity(case_id=c1.id, name="Anton Kozlov", entity_type="PERSON", aliases=["Zero-Day", "Kozlov Ops"], risk_level="CRITICAL", verification_status="VERIFIED", attributes={"role": "Lead Extortion Architect"})
        e2 = Entity(case_id=c1.id, name="Titan Cyber Dynamics LLC", entity_type="ORGANIZATION", risk_level="HIGH", verification_status="VERIFIED", attributes={"status": "Command Server Front Company"})
        e3 = Entity(case_id=c1.id, name="Frankfurt Data Center Zone 3", entity_type="LOCATION", risk_level="ELEVATED", verification_status="VERIFIED")
        e4 = Entity(case_id=c1.id, name="0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE", entity_type="FINANCIAL_ACCOUNT", risk_level="CRITICAL", verification_status="VERIFIED", attributes={"type": "Victim Extortion Deposit Wallet"})
        e5 = Entity(case_id=c1.id, name="+44-7700-900821", entity_type="PHONE_NUMBER", risk_level="HIGH", verification_status="VERIFIED", attributes={"sim": "UK Roaming Ghost Line"})

        db.add_all([e1, e2, e3, e4, e5])
        db.commit()

        r1 = Relationship(source_id=e1.id, target_id=e2.id, case_id=c1.id, relation_type="MEMBER_OF", confidence_score=0.97, verification_status="VERIFIED")
        r2 = Relationship(source_id=e2.id, target_id=e3.id, case_id=c1.id, relation_type="LOCATED_AT", confidence_score=0.92, verification_status="VERIFIED")
        r3 = Relationship(source_id=e1.id, target_id=e4.id, case_id=c1.id, relation_type="OWNER_OF", confidence_score=0.95, verification_status="VERIFIED")
        r4 = Relationship(source_id=e1.id, target_id=e5.id, case_id=c1.id, relation_type="OWNER_OF", confidence_score=0.91, verification_status="VERIFIED")
        db.add_all([r1, r2, r3, r4])

        doc = EvidenceDocument(
            case_id=c1.id,
            title=cls.SAMPLE_DOCUMENTS[4]["title"],
            file_name="cobalt_ghost_cyber_intercept.txt",
            file_type="txt",
            file_size=2750,
            uploaded_by_id=user.id,
            raw_text=cls.SAMPLE_DOCUMENTS[4]["text"]
        )
        db.add(doc)
        db.commit()

    @classmethod
    def _load_master_complex(cls, db: Session, user: User):
        """Loads all scenarios unified into a single interconnected mega-network."""
        # First load baseline Blue Horizon
        from backend.synthetic_data import seed_database
        seed_database(db)

        # Then attach Eclipse Nexus cases and links
        c_nexus = Case(
            case_number="CR-2026-1402",
            title="Operation Eclipse Nexus: Darknet Mixing & Cyber Nexus",
            summary="Decentralized cryptocurrency laundering funneled into maritime escrow accounts.",
            status="ACTIVE",
            priority="CRITICAL",
            jurisdiction="Joint Cyber & Maritime Interdiction Taskforce",
            lead_investigator_id=user.id,
            tags=["darknet", "crypto", "cross-case-nexus"]
        )
        db.add(c_nexus)
        db.commit()

        e_mixer = Entity(case_id=c_nexus.id, name="Tornado EVM Mixer 0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc", entity_type="FINANCIAL_ACCOUNT", risk_level="CRITICAL", verification_status="VERIFIED")
        e_vendor = Entity(case_id=c_nexus.id, name="SilkRoad 4.0 Vendor Portal", entity_type="ORGANIZATION", risk_level="CRITICAL", verification_status="VERIFIED")
        e_anton = Entity(case_id=c_nexus.id, name="Anton Kozlov", entity_type="PERSON", aliases=["Zero-Day"], risk_level="CRITICAL", verification_status="VERIFIED")
        e_ghost_phone = Entity(case_id=c_nexus.id, name="+44-7700-900821", entity_type="PHONE_NUMBER", risk_level="HIGH", verification_status="VERIFIED")

        db.add_all([e_mixer, e_vendor, e_anton, e_ghost_phone])
        db.commit()

        # Link to existing Blue Horizon entities
        e_crypto_escrow = db.query(Entity).filter(Entity.name.ilike("%0x71c89f%")).first()
        e_dmitri = db.query(Entity).filter(Entity.name == "Dmitri Voronov").first()
        e_julian = db.query(Entity).filter(Entity.name == "Julian Morris").first()

        if e_crypto_escrow and e_dmitri and e_julian:
            r_mega1 = Relationship(source_id=e_vendor.id, target_id=e_mixer.id, case_id=c_nexus.id, relation_type="TRANSFERRED_FUNDS_TO", confidence_score=0.96, verification_status="VERIFIED")
            r_mega2 = Relationship(source_id=e_mixer.id, target_id=e_crypto_escrow.id, case_id=c_nexus.id, relation_type="TRANSFERRED_FUNDS_TO", confidence_score=0.93, verification_status="VERIFIED")
            r_mega3 = Relationship(source_id=e_anton.id, target_id=e_dmitri.id, case_id=c_nexus.id, relation_type="ASSOCIATE_OF", confidence_score=0.89, verification_status="VERIFIED")
            r_mega4 = Relationship(source_id=e_ghost_phone.id, target_id=e_julian.id, case_id=c_nexus.id, relation_type="COMMUNICATED_WITH", confidence_score=0.85, verification_status="PENDING_REVIEW")
            db.add_all([r_mega1, r_mega2, r_mega3, r_mega4])

            # Master alert
            alert = NetworkPatternAlert(
                case_id=c_nexus.id,
                alert_type="MULTI_ORGANIZATION_BRIDGE",
                severity="CRITICAL",
                title="Master Syndicate Nexus: Darknet Mixer ➔ Maritime Escrow Convergence",
                explanation="Forensic on-chain analysis confirms direct liquidity transfers from decentralized darknet mixer into Operation Blue Horizon maritime escrow contract 0x71c89f...",
                confidence=0.95,
                affected_entities=[e_mixer.id, e_crypto_escrow.id, e_dmitri.id],
                affected_relationships=[r_mega2.id],
                status="NEW"
            )
            db.add(alert)
            db.commit()

    @classmethod
    def export_full_dataset(cls, db: Session) -> Dict[str, Any]:
        """Serializes the entire active database into a clean, portable JSON dataset."""
        cases = db.query(Case).all()
        entities = db.query(Entity).all()
        relationships = db.query(Relationship).all()
        documents = db.query(EvidenceDocument).all()
        references = db.query(EvidenceReference).all()
        alerts = db.query(NetworkPatternAlert).all()

        return {
            "metadata": {
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "dataset_type": "SYNTHETIC_INVESTIGATIVE_INTELLIGENCE_DATASET",
                "classification": "DEMONSTRATION // SYNTHETIC ONLY // NO PII",
                "counts": {
                    "cases": len(cases),
                    "entities": len(entities),
                    "relationships": len(relationships),
                    "documents": len(documents),
                    "references": len(references),
                    "alerts": len(alerts)
                }
            },
            "cases": [
                {
                    "id": c.id,
                    "case_number": c.case_number,
                    "title": c.title,
                    "summary": c.summary,
                    "status": c.status,
                    "priority": c.priority,
                    "jurisdiction": c.jurisdiction,
                    "tags": c.tags
                }
                for c in cases
            ],
            "entities": [
                {
                    "id": e.id,
                    "case_id": e.case_id,
                    "name": e.name,
                    "entity_type": e.entity_type,
                    "canonical_name": e.canonical_name,
                    "aliases": e.aliases,
                    "identifiers": e.identifiers,
                    "risk_level": e.risk_level,
                    "verification_status": e.verification_status,
                    "attributes": e.attributes,
                    "notes": e.notes
                }
                for e in entities
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "case_id": r.case_id,
                    "relation_type": r.relation_type,
                    "confidence_score": r.confidence_score,
                    "verification_status": r.verification_status,
                    "weight": r.weight,
                    "is_bidirectional": r.is_bidirectional
                }
                for r in relationships
            ],
            "evidence_documents": [
                {
                    "id": d.id,
                    "case_id": d.case_id,
                    "title": d.title,
                    "file_name": d.file_name,
                    "file_type": d.file_type,
                    "raw_text": d.raw_text
                }
                for d in documents
            ],
            "evidence_references": [
                {
                    "id": ref.id,
                    "evidence_document_id": ref.evidence_document_id,
                    "relationship_id": ref.relationship_id,
                    "entity_id": ref.entity_id,
                    "excerpt": ref.excerpt,
                    "page_number": ref.page_number,
                    "extraction_confidence": ref.extraction_confidence,
                    "provenance_notes": ref.provenance_notes
                }
                for ref in references
            ],
            "pattern_alerts": [
                {
                    "id": a.id,
                    "case_id": a.case_id,
                    "alert_type": a.alert_type,
                    "severity": a.severity,
                    "title": a.title,
                    "explanation": a.explanation,
                    "confidence": a.confidence,
                    "status": a.status
                }
                for a in alerts
            ]
        }
