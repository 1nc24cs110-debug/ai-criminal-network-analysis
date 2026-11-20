import datetime
from typing import Dict, List, Any, Tuple, Optional
import networkx as nx
import numpy as np
from sklearn.ensemble import IsolationForest

LEGAL_ETHICAL_DISCLAIMER = (
    "LEGAL DISCLAIMER: Topological graph metrics measure structural connectivity "
    "within the available case records. They DO NOT establish criminal intent, liability, "
    "or guilt. High centrality may indicate a high-volume legitimate service, common transit point, "
    "victim of exploitation, or unwitting intermediary."
)

class NetworkIntelligenceEngine:
    """
    Analyzes investigative knowledge graphs using NetworkX and Scikit-Learn.
    Computes Degree Centrality, Betweenness Centrality, PageRank,
    Community Modularity (Louvain/Greedy), Shortest Paths, and Explainable Anomaly Detection.
    """

    @classmethod
    def build_graph(
        cls,
        entities: List[Any],
        relationships: List[Any],
        include_unverified: bool = True,
        min_confidence: float = 0.0
    ) -> nx.Graph:
        G = nx.Graph()

        # Add entity nodes
        for e in entities:
            G.add_node(
                e.id,
                name=e.name,
                canonical_name=e.canonical_name or e.name,
                entity_type=e.entity_type,
                risk_level=e.risk_level,
                verification_status=e.verification_status,
                case_id=e.case_id,
                aliases=e.aliases or [],
                identifiers=e.identifiers or {},
                attributes=e.attributes or {}
            )

        # Add relationship edges
        for r in relationships:
            if not include_unverified and r.verification_status != "VERIFIED":
                continue
            if r.confidence_score < min_confidence:
                continue
            if G.has_node(r.source_id) and G.has_node(r.target_id):
                G.add_edge(
                    r.source_id,
                    r.target_id,
                    rel_id=r.id,
                    relation_type=r.relation_type,
                    confidence=r.confidence_score,
                    verification_status=r.verification_status,
                    weight=r.weight or 1.0,
                    temporal_start=r.temporal_start.isoformat() if r.temporal_start else None,
                    temporal_end=r.temporal_end.isoformat() if r.temporal_end else None
                )

        return G

    @classmethod
    def compute_all_metrics(cls, G: nx.Graph) -> Dict[str, Any]:
        """
        Computes degree, betweenness, PageRank, community clustering, and explainable anomalies.
        """
        if len(G) == 0:
            return {
                "degree_centrality": [],
                "betweenness_centrality": [],
                "pagerank": [],
                "communities": [],
                "anomalies": [],
                "methodology_notes": {
                    "degree": "Identifies entities with highest number of direct links (hub entities).",
                    "betweenness": "Identifies bridge entities controlling the shortest paths between different sub-networks.",
                    "pagerank": "Identifies structural importance based on connections to other well-connected entities.",
                    "disclaimer": LEGAL_ETHICAL_DISCLAIMER
                }
            }

        # Centrality metrics
        deg_cent = nx.degree_centrality(G)
        bet_cent = nx.betweenness_centrality(G, weight="weight")
        try:
            pagerank = nx.pagerank(G, alpha=0.85)
        except Exception:
            pagerank = {n: 1.0 / len(G) for n in G.nodes()}

        # Community Detection
        communities_raw = []
        try:
            communities_raw = list(nx.algorithms.community.greedy_modularity_communities(G))
        except Exception:
            communities_raw = [set(G.nodes())]

        node_community_map = {}
        communities_out = []
        for comm_idx, comm_set in enumerate(communities_raw):
            comm_nodes = []
            for node_id in comm_set:
                node_community_map[node_id] = comm_idx
                comm_nodes.append({
                    "id": node_id,
                    "name": G.nodes[node_id].get("name", "Unknown"),
                    "type": G.nodes[node_id].get("entity_type", "Unknown")
                })
            communities_out.append({
                "community_id": comm_idx,
                "label": f"Cell / Cluster #{comm_idx + 1}",
                "size": len(comm_nodes),
                "members": comm_nodes
            })

        # Format metric rankings
        degree_ranking = sorted(
            [
                {
                    "id": node_id,
                    "name": G.nodes[node_id].get("name"),
                    "entity_type": G.nodes[node_id].get("entity_type"),
                    "score": round(deg_cent[node_id], 4),
                    "raw_degree": G.degree[node_id],
                    "explanation": f"Connected directly to {G.degree[node_id]} other entities. Represents a high-connectivity operational hub."
                }
                for node_id in G.nodes()
            ],
            key=lambda x: x["score"],
            reverse=True
        )

        betweenness_ranking = sorted(
            [
                {
                    "id": node_id,
                    "name": G.nodes[node_id].get("name"),
                    "entity_type": G.nodes[node_id].get("entity_type"),
                    "score": round(bet_cent[node_id], 4),
                    "explanation": (
                        f"Acts as a critical communication or logistics bridge with a betweenness score of {round(bet_cent[node_id], 4)}. "
                        "Controls indirect flow between disconnected cells."
                    )
                }
                for node_id in G.nodes()
            ],
            key=lambda x: x["score"],
            reverse=True
        )

        pagerank_ranking = sorted(
            [
                {
                    "id": node_id,
                    "name": G.nodes[node_id].get("name"),
                    "entity_type": G.nodes[node_id].get("entity_type"),
                    "score": round(pagerank[node_id], 4),
                    "explanation": (
                        f"Structural prominence score {round(pagerank[node_id], 4)}. "
                        "Entity is referenced or transacted with by other high-prominence nodes."
                    )
                }
                for node_id in G.nodes()
            ],
            key=lambda x: x["score"],
            reverse=True
        )

        # Explainable Anomaly Detection
        anomalies = cls._detect_graph_anomalies(G, deg_cent, bet_cent, pagerank, node_community_map)

        return {
            "degree_centrality": degree_ranking[:15],
            "betweenness_centrality": betweenness_ranking[:15],
            "pagerank": pagerank_ranking[:15],
            "communities": communities_out,
            "anomalies": anomalies,
            "node_metrics": {
                node_id: {
                    "degree": G.degree[node_id],
                    "degree_centrality": round(deg_cent.get(node_id, 0.0), 4),
                    "betweenness": round(bet_cent.get(node_id, 0.0), 4),
                    "pagerank": round(pagerank.get(node_id, 0.0), 4),
                    "community": node_community_map.get(node_id, 0)
                }
                for node_id in G.nodes()
            },
            "methodology_notes": {
                "degree": "Identifies entities with highest direct link volume (hub entities).",
                "betweenness": "Identifies bridge entities controlling the shortest paths between different operational cells.",
                "pagerank": "Structural influence accounting for recursive neighbor authority.",
                "anomalies": "Multi-dimensional anomaly detection identifying structural outliers, cross-cell bridges, and unverified critical bottlenecks.",
                "disclaimer": LEGAL_ETHICAL_DISCLAIMER
            }
        }

    @classmethod
    def _detect_graph_anomalies(
        cls,
        G: nx.Graph,
        deg_cent: Dict[int, float],
        bet_cent: Dict[int, float],
        pagerank: Dict[int, float],
        community_map: Dict[int, int]
    ) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []

        if len(G) < 3:
            return anomalies

        # Feature matrix for IsolationForest
        nodes = list(G.nodes())
        features = []
        for n in nodes:
            # Degree, betweenness, pagerank, clustering coeff
            cc = nx.clustering(G, n)
            features.append([deg_cent[n], bet_cent[n], pagerank[n], cc])

        X = np.array(features)
        if len(nodes) >= 6:
            try:
                clf = IsolationForest(contamination=0.15, random_state=42)
                preds = clf.fit_predict(X)
                scores = clf.decision_function(X)
                for idx, pred in enumerate(preds):
                    if pred == -1:  # Outlier
                        n_id = nodes[idx]
                        node_data = G.nodes[n_id]
                        anomalies.append({
                            "entity_id": n_id,
                            "entity_name": node_data.get("name"),
                            "entity_type": node_data.get("entity_type"),
                            "anomaly_type": "STRUCTURAL_TOPOLOGICAL_OUTLIER",
                            "severity": "HIGH",
                            "confidence": round(float(abs(scores[idx])), 2),
                            "explanation": (
                                f"Machine learning isolation model flagged {node_data.get('name')} as a statistical network outlier. "
                                f"Exhibits atypical combination of high bridge potential (Betweenness: {round(bet_cent[n_id], 3)}) "
                                f"and sparse local clustering."
                            )
                        })
            except Exception:
                pass

        # Heuristic 1: Cross-Community Broker Anomaly
        for n in nodes:
            neighbors = list(G.neighbors(n))
            neighbor_comms = {community_map.get(nbr) for nbr in neighbors if community_map.get(nbr) is not None}
            if len(neighbor_comms) >= 2 and bet_cent.get(n, 0) > 0.10:
                node_data = G.nodes[n]
                if not any(a["entity_id"] == n and a["anomaly_type"] == "CROSS_COMMUNITY_BRIDGE" for a in anomalies):
                    anomalies.append({
                        "entity_id": n,
                        "entity_name": node_data.get("name"),
                        "entity_type": node_data.get("entity_type"),
                        "anomaly_type": "CROSS_COMMUNITY_BRIDGE",
                        "severity": "CRITICAL",
                        "confidence": 0.92,
                        "explanation": (
                            f"Entity links {len(neighbor_comms)} distinct operational clusters. "
                            "Often indicates a high-level courier, broker, or joint financial intermediary bridging isolated cells."
                        )
                    })

        # Heuristic 2: Critical Bottleneck with Unverified Evidence
        for n in nodes:
            if bet_cent.get(n, 0) > 0.15:
                # Check incident edges
                unverified_count = 0
                for nbr in G.neighbors(n):
                    edge_data = G.get_edge_data(n, nbr)
                    if edge_data and edge_data.get("verification_status") != "VERIFIED":
                        unverified_count += 1
                if unverified_count >= 1:
                    node_data = G.nodes[n]
                    anomalies.append({
                        "entity_id": n,
                        "entity_name": node_data.get("name"),
                        "entity_type": node_data.get("entity_type"),
                        "anomaly_type": "UNVERIFIED_CRITICAL_BOTTLENECK",
                        "severity": "HIGH",
                        "confidence": 0.88,
                        "explanation": (
                            f"Entity holds critical bridge centrality (score: {round(bet_cent[n], 3)}) "
                            f"yet relies on {unverified_count} unverified relationship(s). "
                            "Priority human verification is recommended before investigative actions."
                        )
                    })

        return anomalies[:10]

    @classmethod
    def find_shortest_path(
        cls,
        G: nx.Graph,
        source_id: int,
        target_id: int,
        relationships_lookup: Dict[Tuple[int, int], Any]
    ) -> Dict[str, Any]:
        """
        Finds the shortest evidence-supported investigative chain connecting two entities.
        """
        if not G.has_node(source_id) or not G.has_node(target_id):
            return {
                "found": False,
                "path_nodes": [],
                "path_edges": [],
                "total_hops": 0,
                "evidence_chain": ["One or both entities not found in active graph."]
            }

        try:
            path_node_ids = nx.shortest_path(G, source=source_id, target=target_id, weight=None)
        except nx.NetworkXNoPath:
            return {
                "found": False,
                "path_nodes": [],
                "path_edges": [],
                "total_hops": 0,
                "evidence_chain": ["No direct or indirect investigative connection discovered between the selected entities."]
            }

        path_nodes = []
        for nid in path_node_ids:
            ndata = G.nodes[nid]
            path_nodes.append({
                "id": str(nid),
                "name": ndata.get("name"),
                "entity_type": ndata.get("entity_type"),
                "risk_level": ndata.get("risk_level"),
                "verification_status": ndata.get("verification_status")
            })

        path_edges = []
        evidence_chain = []
        for i in range(len(path_node_ids) - 1):
            u = path_node_ids[i]
            v = path_node_ids[i + 1]
            edge_data = G.get_edge_data(u, v) or {}
            rel = relationships_lookup.get((u, v)) or relationships_lookup.get((v, u))

            rel_type = edge_data.get("relation_type", "CONNECTED_TO")
            status = edge_data.get("verification_status", "UNKNOWN")
            conf = edge_data.get("confidence", 0.85)

            u_name = G.nodes[u].get("name")
            v_name = G.nodes[v].get("name")

            step_desc = f"Hop {i+1}: {u_name} --[{rel_type} (conf: {round(conf*100)}%, status: {status})]--> {v_name}"
            evidence_chain.append(step_desc)

            path_edges.append({
                "source": str(u),
                "target": str(v),
                "relation_type": rel_type,
                "confidence_score": conf,
                "verification_status": status
            })

        return {
            "found": True,
            "path_nodes": path_nodes,
            "path_edges": path_edges,
            "total_hops": len(path_node_ids) - 1,
            "evidence_chain": evidence_chain
        }
