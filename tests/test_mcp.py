"""
Unit tests for Criminal Network MCP (Model Context Protocol) Server.
Tests JSON-RPC 2.0 dispatching for tools, resources, and prompt templates.
"""

import os
import sys
import json
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcp_server import dispatch_request

def test_mcp_initialize():
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    res = dispatch_request(req)
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == 1
    assert "result" in res
    assert res["result"]["serverInfo"]["name"] == "criminal-network-mcp"
    assert "tools" in res["result"]["capabilities"]
    assert "resources" in res["result"]["capabilities"]
    assert "prompts" in res["result"]["capabilities"]

def test_mcp_ping():
    req = {"jsonrpc": "2.0", "id": 2, "method": "ping"}
    res = dispatch_request(req)
    assert res["result"] == {}

def test_mcp_tools_list():
    req = {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}
    res = dispatch_request(req)
    tools = res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "list_cases" in tool_names
    assert "search_entities" in tool_names
    assert "get_entity_dossier" in tool_names
    assert "calculate_network_metrics" in tool_names
    assert "find_shortest_evidentiary_path" in tool_names
    assert "extract_intelligence_from_document" in tool_names
    assert "get_pattern_alerts" in tool_names
    assert "verify_relationship" in tool_names

def test_mcp_call_list_cases():
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "list_cases",
            "arguments": {"status": "ACTIVE"}
        }
    }
    res = dispatch_request(req)
    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert "cases" in content
    assert content["count"] >= 1

def test_mcp_call_search_entities():
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "search_entities",
            "arguments": {"query": "Voronov"}
        }
    }
    res = dispatch_request(req)
    content = json.loads(res["result"]["content"][0]["text"])
    assert "entities" in content
    assert len(content["entities"]) >= 1
    assert any("Voronov" in e["name"] for e in content["entities"])

def test_mcp_call_entity_dossier():
    req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "get_entity_dossier",
            "arguments": {"entity_id": 1}
        }
    }
    res = dispatch_request(req)
    dossier = json.loads(res["result"]["content"][0]["text"])
    assert "entity_id" in dossier
    assert "relationships" in dossier
    assert "presumption_of_innocence" in dossier

def test_mcp_call_network_metrics():
    req = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "calculate_network_metrics",
            "arguments": {}
        }
    }
    res = dispatch_request(req)
    metrics = json.loads(res["result"]["content"][0]["text"])
    assert "degree_centrality" in metrics
    assert "betweenness_centrality" in metrics
    assert "pagerank" in metrics
    assert "communities" in metrics
    assert "disclaimer" in metrics

def test_mcp_call_shortest_path():
    req = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "find_shortest_evidentiary_path",
            "arguments": {"source_entity_id": 1, "target_entity_id": 2}
        }
    }
    res = dispatch_request(req)
    path_res = json.loads(res["result"]["content"][0]["text"])
    assert "found" in path_res

def test_mcp_call_extract_intel():
    sample_text = "Target Elena Rostova was spotted communicating with phone +1-555-0199 outside Zurich Vault."
    req = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "extract_intelligence_from_document",
            "arguments": {"text": sample_text}
        }
    }
    res = dispatch_request(req)
    intel = json.loads(res["result"]["content"][0]["text"])
    assert "extracted_entities" in intel
    assert len(intel["extracted_entities"]) >= 1

def test_mcp_call_pattern_alerts():
    req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "get_pattern_alerts",
            "arguments": {"min_severity": "MEDIUM"}
        }
    }
    res = dispatch_request(req)
    data = json.loads(res["result"]["content"][0]["text"])
    assert "alerts" in data

def test_mcp_resources():
    list_req = {"jsonrpc": "2.0", "id": 11, "method": "resources/list"}
    list_res = dispatch_request(list_req)
    resources = list_res["result"]["resources"]
    uris = [r["uri"] for r in resources]
    assert "investigation://cases" in uris
    assert "investigation://network-graph" in uris

    read_req = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "resources/read",
        "params": {"uri": "investigation://cases"}
    }
    read_res = dispatch_request(read_req)
    assert len(read_res["result"]["contents"]) >= 1
    assert "application/json" in read_res["result"]["contents"][0]["mimeType"]

def test_mcp_prompts():
    list_req = {"jsonrpc": "2.0", "id": 13, "method": "prompts/list"}
    list_res = dispatch_request(list_req)
    prompts = list_res["result"]["prompts"]
    pnames = [p["name"] for p in prompts]
    assert "investigate_person_of_interest" in pnames

    get_req = {
        "jsonrpc": "2.0",
        "id": 14,
        "method": "prompts/get",
        "params": {
            "name": "investigate_person_of_interest",
            "arguments": {"person_name": "Viktor Reznikov"}
        }
    }
    get_res = dispatch_request(get_req)
    assert "messages" in get_res["result"]
    assert "Viktor Reznikov" in get_res["result"]["messages"][0]["content"]["text"]
