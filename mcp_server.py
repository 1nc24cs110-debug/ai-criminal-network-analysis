"""
AI-POWERED CRIMINAL NETWORK ANALYSIS SYSTEM
MODEL CONTEXT PROTOCOL (MCP) SERVER

Exposes the Criminal Network Analysis Knowledge Graph, Graph Intelligence (Degree/Betweenness/PageRank),
Forensic Dossiers, Evidence Provenance Engine, NLP Extraction, and Pattern Alerts as native MCP tools,
resources, and investigative prompts for MCP-compliant AI assistants (Antigravity, Claude, Cursor, etc.).

Complies with the official Model Context Protocol (JSON-RPC 2.0 over stdio).
Presumption of innocence disclaimer: All network topology metrics are investigative indicators and
do NOT constitute legal proof of guilt.
"""

import sys
import os
import json
import traceback
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import SessionLocal
from backend.models import (
    Case, Entity, Relationship, EvidenceDocument, EvidenceReference,
    EntityMatchSuggestion, NetworkPatternAlert, AuditLog, User
)
from backend.nlp_engine import EvidenceExtractionEngine
from backend.graph_engine import NetworkIntelligenceEngine

SERVER_NAME = "criminal-network-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

LEGAL_DISCLAIMER = (
    "LEGAL DISCLAIMER: Topological centrality, algorithmic clusters, and network analytics "
    "are structural metrics for investigative prioritization only and do NOT establish legal guilt, "
    "criminal intent, or evidentiary culpability."
)

# ---------------------------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "list_cases",
        "description": "List all criminal investigation operations with priority, jurisdiction, status, entity count, and lead investigator.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "UNDER_REVIEW", "CLOSED", "COLD", "ALL"],
                    "description": "Filter by status (default ALL)"
                }
            }
        }
    },
    {
        "name": "search_entities",
        "description": "Search the criminal network knowledge graph across all registered entities (Persons, Organizations, Phones, Vehicles, Accounts, Devices, Locations).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term for entity name, alias, or identifier (e.g., SSN, VIN, IBAN, IMEI)"
                },
                "case_id": {
                    "type": "integer",
                    "description": "Optional investigation case ID filter"
                },
                "entity_type": {
                    "type": "string",
                    "enum": ["PERSON", "ORGANIZATION", "PHONE_NUMBER", "DEVICE", "VEHICLE", "FINANCIAL_ACCOUNT", "LOCATION", "CASE_ANCHOR"],
                    "description": "Optional entity type filter"
                }
            }
        }
    },
    {
        "name": "get_entity_dossier",
        "description": "Retrieve comprehensive investigative dossier on an entity, including verified and unverified relationships, attributes, aliases, risk ratings, and exact character-offset evidence provenance references.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "integer",
                    "description": "Target entity database ID"
                }
            },
            "required": ["entity_id"]
        }
    },
    {
        "name": "calculate_network_metrics",
        "description": "Execute NetworkX graph analytics to calculate Degree Centrality, Betweenness Centrality (bridges), PageRank, Community Clusters, and anomaly outliers for an investigation network.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "integer",
                    "description": "Target case ID (omit to analyze cross-case global intelligence network)"
                }
            }
        }
    },
    {
        "name": "find_shortest_evidentiary_path",
        "description": "Calculate the shortest evidence-supported path between two entities in the criminal network knowledge graph.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_entity_id": {
                    "type": "integer",
                    "description": "Database ID of starting entity"
                },
                "target_entity_id": {
                    "type": "integer",
                    "description": "Database ID of destination entity"
                }
            },
            "required": ["source_entity_id", "target_entity_id"]
        }
    },
    {
        "name": "extract_intelligence_from_document",
        "description": "Run NLP entity extraction and relationship triple identification on raw surveillance narrative, witness testimony, or dispatch text with character offsets and confidence scores.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Raw intelligence narrative text to parse"
                },
                "document_title": {
                    "type": "string",
                    "description": "Optional title for reference"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "get_pattern_alerts",
        "description": "Retrieve active intelligence alerts for suspicious graph patterns (Cross-Case Bridge, Communication Spikes, Hub Funneling, High-Risk Clustering).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_severity": {
                    "type": "string",
                    "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    "description": "Minimum alert severity (default HIGH)"
                }
            }
        }
    },
    {
        "name": "verify_relationship",
        "description": "Perform Human-in-the-Loop verification or flagging of an AI-suggested relationship edge, recording investigator notes and maintaining provenance integrity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "relationship_id": {
                    "type": "integer",
                    "description": "Relationship ID to update"
                },
                "action": {
                    "type": "string",
                    "enum": ["VERIFY", "FLAG", "DISPUTE"],
                    "description": "Action: VERIFY (confirmed evidence), FLAG (suspicious/unreliable), DISPUTE (contradicted by facts)"
                },
                "notes": {
                    "type": "string",
                    "description": "Evidentiary rationale for verification status change"
                }
            },
            "required": ["relationship_id", "action"]
        }
    }
]

# ---------------------------------------------------------------------------
# Resources Definitions
# ---------------------------------------------------------------------------

RESOURCES = [
    {
        "uri": "investigation://cases",
        "name": "Investigation Operations",
        "description": "Catalog of all registered cases, their threat priorities, and operational statuses.",
        "mimeType": "application/json"
    },
    {
        "uri": "investigation://network-graph",
        "name": "Global Knowledge Graph Summary",
        "description": "High-level summary of entities, verified links, and unverified AI suggestions across the system.",
        "mimeType": "application/json"
    },
    {
        "uri": "investigation://alerts",
        "name": "Active Anomaly Pattern Alerts",
        "description": "Unresolved structural anomalies and suspicious graph topological patterns flagged for human review.",
        "mimeType": "application/json"
    },
    {
        "uri": "investigation://audit-log",
        "name": "Tamper-Evident Audit Trail",
        "description": "Recent investigator verification events, merges, and system actions.",
        "mimeType": "text/markdown"
    }
]

# ---------------------------------------------------------------------------
# Prompt Templates
# ---------------------------------------------------------------------------

PROMPTS = [
    {
        "name": "investigate_person_of_interest",
        "description": "Formulate a systematic evidentiary investigation plan for a Person of Interest (POI), analyzing connections, verification status, and provenance.",
        "arguments": [
            {
                "name": "person_name",
                "description": "Name or alias of the person of interest",
                "required": True
            }
        ]
    },
    {
        "name": "cross_case_bridge_analysis",
        "description": "Analyze entities connecting two separate criminal investigations, detecting shared infrastructure, financial conduits, or burner phones.",
        "arguments": [
            {
                "name": "case_1_number",
                "description": "Case number of first investigation",
                "required": True
            },
            {
                "name": "case_2_number",
                "description": "Case number of second investigation",
                "required": True
            }
        ]
    },
    {
        "name": "evidentiary_integrity_audit",
        "description": "Audit an investigation case for unverified AI extractions, missing source document references, and potential false-positive entity links.",
        "arguments": [
            {
                "name": "case_number",
                "description": "Investigation case number",
                "required": True
            }
        ]
    }
]

# ---------------------------------------------------------------------------
# Tool Execution Handlers
# ---------------------------------------------------------------------------

def handle_list_cases(params: Dict[str, Any]) -> str:
    db = SessionLocal()
    try:
        query = db.query(Case)
        status_filter = params.get("status", "ALL")
        if status_filter and status_filter != "ALL":
            query = query.filter(Case.status == status_filter)
        cases = query.all()

        output = []
        for c in cases:
            entity_count = db.query(Entity).filter(Entity.case_id == c.id).count()
            output.append({
                "id": c.id,
                "case_number": c.case_number,
                "title": c.title,
                "status": c.status,
                "priority": c.priority,
                "jurisdiction": c.jurisdiction,
                "entity_count": entity_count,
                "tags": c.tags or []
            })
        return json.dumps({"cases": output, "count": len(output)}, indent=2)
    finally:
        db.close()

def handle_search_entities(params: Dict[str, Any]) -> str:
    db = SessionLocal()
    try:
        query = db.query(Entity)
        case_id = params.get("case_id")
        entity_type = params.get("entity_type")
        q = params.get("query", "").strip()

        if case_id:
            query = query.filter(Entity.case_id == case_id)
        if entity_type:
            query = query.filter(Entity.entity_type == entity_type)
        if q:
            search_pattern = f"%{q}%"
            query = query.filter(
                (Entity.name.ilike(search_pattern)) |
                (Entity.canonical_name.ilike(search_pattern)) |
                (Entity.notes.ilike(search_pattern))
            )

        entities = query.limit(50).all()
        results = []
        for e in entities:
            results.append({
                "id": e.id,
                "name": e.name,
                "canonical_name": e.canonical_name,
                "entity_type": e.entity_type,
                "risk_level": e.risk_level,
                "verification_status": e.verification_status,
                "case_id": e.case_id,
                "aliases": e.aliases or [],
                "identifiers": e.identifiers or {},
                "attributes": e.attributes or {}
            })
        return json.dumps({"entities": results, "count": len(results)}, indent=2)
    finally:
        db.close()

def handle_get_entity_dossier(params: Dict[str, Any]) -> str:
    db = SessionLocal()
    try:
        entity_id = params.get("entity_id")
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            return json.dumps({"error": f"Entity with ID {entity_id} not found."})

        # Outgoing relationships
        outgoing = db.query(Relationship).filter(Relationship.source_id == entity.id).all()
        # Incoming relationships
        incoming = db.query(Relationship).filter(Relationship.target_id == entity.id).all()

        rels = []
        for r in outgoing:
            target = db.query(Entity).filter(Entity.id == r.target_id).first()
            refs = db.query(EvidenceReference).filter(EvidenceReference.relationship_id == r.id).all()
            rels.append({
                "relationship_id": r.id,
                "direction": "OUTGOING",
                "connected_entity": target.name if target else f"ID {r.target_id}",
                "connected_entity_type": target.entity_type if target else "UNKNOWN",
                "relationship_type": r.relation_type,
                "confidence_score": r.confidence_score,
                "verification_status": r.verification_status,
                "evidence_provenance": [
                    {
                        "document_id": ref.evidence_document_id,
                        "quote": ref.excerpt,
                        "char_start": ref.char_offset_start,
                        "char_end": ref.char_offset_end
                    }
                    for ref in refs
                ]
            })

        for r in incoming:
            source = db.query(Entity).filter(Entity.id == r.source_id).first()
            refs = db.query(EvidenceReference).filter(EvidenceReference.relationship_id == r.id).all()
            rels.append({
                "relationship_id": r.id,
                "direction": "INCOMING",
                "connected_entity": source.name if source else f"ID {r.source_id}",
                "connected_entity_type": source.entity_type if source else "UNKNOWN",
                "relationship_type": r.relation_type,
                "confidence_score": r.confidence_score,
                "verification_status": r.verification_status,
                "evidence_provenance": [
                    {
                        "document_id": ref.evidence_document_id,
                        "quote": ref.excerpt,
                        "char_start": ref.char_offset_start,
                        "char_end": ref.char_offset_end
                    }
                    for ref in refs
                ]
            })

        dossier = {
            "entity_id": entity.id,
            "name": entity.name,
            "canonical_name": entity.canonical_name,
            "entity_type": entity.entity_type,
            "case_id": entity.case_id,
            "risk_level": entity.risk_level,
            "verification_status": entity.verification_status,
            "aliases": entity.aliases or [],
            "identifiers": entity.identifiers or {},
            "attributes": entity.attributes or {},
            "investigator_notes": entity.notes,
            "total_connections": len(rels),
            "relationships": rels,
            "presumption_of_innocence": LEGAL_DISCLAIMER
        }
        return json.dumps(dossier, indent=2)
    finally:
        db.close()

def handle_calculate_network_metrics(params: Dict[str, Any]) -> str:
    db = SessionLocal()
    try:
        case_id = params.get("case_id")
        e_query = db.query(Entity)
        r_query = db.query(Relationship)
        if case_id:
            e_query = e_query.filter(Entity.case_id == case_id)
            r_query = r_query.filter(Relationship.case_id == case_id)
        entities = e_query.all()
        relationships = r_query.all()

        G = NetworkIntelligenceEngine.build_graph(entities, relationships, include_unverified=True)
        metrics = NetworkIntelligenceEngine.compute_all_metrics(G)
        metrics["disclaimer"] = LEGAL_DISCLAIMER
        return json.dumps(metrics, indent=2)
    finally:
        db.close()

def handle_find_shortest_evidentiary_path(params: Dict[str, Any]) -> str:
    db = SessionLocal()
    try:
        source_id = params.get("source_entity_id")
        target_id = params.get("target_entity_id")
        if not source_id or not target_id:
            return json.dumps({"error": "source_entity_id and target_entity_id are required"})

        entities = db.query(Entity).all()
        relationships = db.query(Relationship).all()
        G = NetworkIntelligenceEngine.build_graph(entities, relationships, include_unverified=True)
        rel_lookup = {(r.source_id, r.target_id): r for r in relationships}

        result = NetworkIntelligenceEngine.find_shortest_path(
            G, source_id, target_id, rel_lookup
        )
        return json.dumps(result, indent=2)
    finally:
        db.close()

def handle_extract_intelligence(params: Dict[str, Any]) -> str:
    text = params.get("text", "")
    if not text:
        return json.dumps({"error": "text is required"})
    entities = EvidenceExtractionEngine.extract_entities(text=text)
    relationships = EvidenceExtractionEngine.extract_relationships(text=text, entities=entities)
    return json.dumps({
        "extracted_entities": entities,
        "extracted_relationships": relationships,
        "count_entities": len(entities),
        "count_relationships": len(relationships)
    }, indent=2)

def handle_get_pattern_alerts(params: Dict[str, Any]) -> str:
    db = SessionLocal()
    try:
        min_sev = params.get("min_severity", "HIGH")
        severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        threshold = severity_order.get(min_sev, 3)

        alerts = db.query(NetworkPatternAlert).filter(NetworkPatternAlert.status != "RESOLVED").all()
        filtered = [
            {
                "id": a.id,
                "case_id": a.case_id,
                "pattern_type": a.alert_type,
                "severity": a.severity,
                "confidence_score": a.confidence,
                "title": a.title,
                "description": a.explanation,
                "affected_entity_ids": a.affected_entities or [],
                "created_at": str(a.created_at)
            }
            for a in alerts
            if severity_order.get(a.severity, 1) >= threshold
        ]
        return json.dumps({"alerts": filtered, "count": len(filtered)}, indent=2)
    finally:
        db.close()

def handle_verify_relationship(params: Dict[str, Any]) -> str:
    db = SessionLocal()
    try:
        rel_id = params.get("relationship_id")
        action = params.get("action", "").upper()
        notes = params.get("notes", "Updated via MCP Server")

        rel = db.query(Relationship).filter(Relationship.id == rel_id).first()
        if not rel:
            return json.dumps({"error": f"Relationship {rel_id} not found"})

        status_map = {
            "VERIFY": "VERIFIED",
            "FLAG": "FLAGGED",
            "DISPUTE": "UNVERIFIED"
        }
        new_status = status_map.get(action, "VERIFIED")
        old_status = rel.verification_status
        rel.verification_status = new_status
        rel.notes = f"{rel.notes or ''}\n[MCP Audit]: {action} - {notes}".strip()

        audit = AuditLog(
            user_id=1,
            action="RELATIONSHIP_VERIFIED" if new_status == "VERIFIED" else "RELATIONSHIP_FLAGGED",
            entity_type="RELATIONSHIP",
            entity_id=rel.id,
            details={
                "previous_status": old_status,
                "new_status": new_status,
                "notes": notes,
                "client": "Model Context Protocol (MCP)"
            }
        )
        db.add(audit)
        db.commit()
        db.refresh(rel)

        return json.dumps({
            "success": True,
            "relationship_id": rel.id,
            "previous_status": old_status,
            "current_status": rel.verification_status,
            "message": f"Relationship {rel.id} successfully updated to {new_status}."
        }, indent=2)
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Resource Handlers
# ---------------------------------------------------------------------------

def handle_read_resource(uri: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        if uri == "investigation://cases":
            cases = db.query(Case).all()
            data = [
                {
                    "case_number": c.case_number,
                    "title": c.title,
                    "status": c.status,
                    "priority": c.priority,
                    "jurisdiction": c.jurisdiction,
                    "entities": len(c.entities)
                }
                for c in cases
            ]
            return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(data, indent=2)}]}

        elif uri == "investigation://network-graph":
            nodes_count = db.query(Entity).count()
            rels_count = db.query(Relationship).count()
            verified_count = db.query(Relationship).filter(Relationship.verification_status == "VERIFIED").count()
            data = {
                "total_entities": nodes_count,
                "total_relationships": rels_count,
                "verified_relationships": verified_count,
                "pending_verification": rels_count - verified_count,
                "disclaimer": LEGAL_DISCLAIMER
            }
            return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(data, indent=2)}]}

        elif uri == "investigation://alerts":
            alerts = db.query(NetworkPatternAlert).filter(NetworkPatternAlert.status != "RESOLVED").all()
            data = [
                {
                    "id": a.id,
                    "pattern": a.alert_type,
                    "severity": a.severity,
                    "title": a.title,
                    "description": a.explanation
                }
                for a in alerts
            ]
            return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(data, indent=2)}]}

        elif uri == "investigation://audit-log":
            logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(20).all()
            lines = ["# Investigation Audit Trail", ""]
            for l in logs:
                lines.append(f"- **{l.created_at}** [{l.action}] on `{l.entity_type} #{l.entity_id}`: `{json.dumps(l.details)}`")
            return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": "\n".join(lines)}]}

        else:
            raise ValueError(f"Resource not found: {uri}")
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Prompt Handlers
# ---------------------------------------------------------------------------

def handle_get_prompt(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "investigate_person_of_interest":
        poi = args.get("person_name", "UNKNOWN")
        prompt_text = (
            f"You are conducting an investigative intelligence review of Person of Interest: '{poi}'.\n"
            f"1. Call `search_entities(query='{poi}')` to locate the entity record and its database ID.\n"
            f"2. Call `get_entity_dossier(entity_id=...)` to retrieve all known incoming and outgoing connections.\n"
            f"3. Differentiate between VERIFIED connections (backed by quoted character-offset evidence) and UNVERIFIED suggestions.\n"
            f"4. Identify any high-risk financial, phone, or corporate entities linked to {poi}.\n"
            f"5. IMPORTANT: Adhere to the presumption of innocence. Frame all findings as investigative hypotheses supported by evidence references."
        )
        return {
            "description": f"Evidentiary investigation plan for {poi}",
            "messages": [
                {"role": "user", "content": {"type": "text", "text": prompt_text}}
            ]
        }
    elif name == "cross_case_bridge_analysis":
        c1 = args.get("case_1_number", "CASE-A")
        c2 = args.get("case_2_number", "CASE-B")
        prompt_text = (
            f"Analyze cross-case nexus between operation '{c1}' and '{c2}'.\n"
            f"1. Query `list_cases()` to get the respective IDs for {c1} and {c2}.\n"
            f"2. Inspect active alerts using `get_pattern_alerts()` for 'CROSS_CASE_BRIDGE' alerts.\n"
            f"3. Search entities in both cases and identify overlapping phones, financial accounts, or shell companies.\n"
            f"4. Use `find_shortest_evidentiary_path` between primary targets of both operations.\n"
            f"5. Summarize evidentiary strength and indicate which connections require field investigator verification."
        )
        return {
            "description": f"Cross-case nexus analysis between {c1} and {c2}",
            "messages": [
                {"role": "user", "content": {"type": "text", "text": prompt_text}}
            ]
        }
    elif name == "evidentiary_integrity_audit":
        case_no = args.get("case_number", "TARGET")
        prompt_text = (
            f"Perform an evidentiary integrity and provenance audit on Case '{case_no}'.\n"
            f"1. Retrieve the case entities and network relationships.\n"
            f"2. Identify any relationships marked 'UNVERIFIED' that have not been vetted by a human investigator.\n"
            f"3. Check for evidence references lacking character start/end offsets.\n"
            f"4. Highlight any potential duplicate entities in `search_entities` requiring deduplication review."
        )
        return {
            "description": f"Audit of evidentiary integrity for {case_no}",
            "messages": [
                {"role": "user", "content": {"type": "text", "text": prompt_text}}
            ]
        }
    else:
        raise ValueError(f"Prompt '{name}' not found")

# ---------------------------------------------------------------------------
# Main JSON-RPC Dispatcher
# ---------------------------------------------------------------------------

def dispatch_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                }
            }
        }

    elif method == "notifications/initialized":
        # Notification from client, no response required
        return None

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "list_cases":
                text_result = handle_list_cases(arguments)
            elif tool_name == "search_entities":
                text_result = handle_search_entities(arguments)
            elif tool_name == "get_entity_dossier":
                text_result = handle_get_entity_dossier(arguments)
            elif tool_name == "calculate_network_metrics":
                text_result = handle_calculate_network_metrics(arguments)
            elif tool_name == "find_shortest_evidentiary_path":
                text_result = handle_find_shortest_evidentiary_path(arguments)
            elif tool_name == "extract_intelligence_from_document":
                text_result = handle_extract_intelligence(arguments)
            elif tool_name == "get_pattern_alerts":
                text_result = handle_get_pattern_alerts(arguments)
            elif tool_name == "verify_relationship":
                text_result = handle_verify_relationship(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found."
                    }
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": text_result
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Execution error in tool '{tool_name}': {str(e)}",
                    "data": traceback.format_exc()
                }
            }

    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": RESOURCES
            }
        }

    elif method == "resources/read":
        uri = params.get("uri")
        try:
            res = handle_read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": res
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Failed to read resource '{uri}': {str(e)}"
                }
            }

    elif method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "prompts": PROMPTS
            }
        }

    elif method == "prompts/get":
        prompt_name = params.get("name")
        prompt_args = params.get("arguments", {})
        try:
            res = handle_get_prompt(prompt_name, prompt_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": res
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": str(e)
                }
            }

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not implemented."
            }
        }

def run_stdio_server():
    """Run line-delimited JSON-RPC 2.0 loop over stdin/stdout."""
    # Ensure stdout is unbuffered
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            # Check if line is Content-Length header framing
            if line.startswith("Content-Length:"):
                length = int(line.split(":")[1].strip())
                # Read following blank line
                sys.stdin.readline()
                content = sys.stdin.read(length)
                req = json.loads(content)
            else:
                req = json.loads(line)

            response = dispatch_request(req)
            if response is not None:
                resp_str = json.dumps(response)
                sys.stdout.write(resp_str + "\n")
                sys.stdout.flush()

        except json.JSONDecodeError as err:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(err)}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
        except Exception as err:
            sys.stderr.write(f"MCP Server error: {traceback.format_exc()}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    run_stdio_server()
