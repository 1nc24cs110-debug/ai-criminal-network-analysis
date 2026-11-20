import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, EventObject } from 'cytoscape';
import {
  Share2, ZoomIn, ZoomOut, Maximize2, RotateCcw, Filter, Search,
  Sliders, ShieldCheck, Clock, AlertTriangle, Layers, Route, Info,
  CheckCircle2, XCircle, ArrowRight, Eye, ChevronRight, Sparkles
} from 'lucide-react';
import { api } from '../api';
import { GraphData, CentralityAnalytics } from '../types';

interface NetworkIntelligenceViewProps {
  initialCaseId?: number;
  initialEntityId?: number;
}

const ENTITY_COLORS: Record<string, string> = {
  PERSON: '#06B6D4',           // Cyan
  ORGANIZATION: '#3B82F6',     // Electric Blue
  PHONE_NUMBER: '#F59E0B',     // Amber
  DEVICE: '#8B5CF6',           // Purple
  VEHICLE: '#10B981',          // Emerald
  FINANCIAL_ACCOUNT: '#EC4899',// Pink
  LOCATION: '#EF4444',         // Red
  CASE_ANCHOR: '#6366F1'       // Indigo
};

const ENTITY_SHAPES: Record<string, cytoscape.Css.NodeShape> = {
  PERSON: 'ellipse',
  ORGANIZATION: 'round-rectangle',
  PHONE_NUMBER: 'diamond',
  DEVICE: 'round-diamond',
  VEHICLE: 'hexagon',
  FINANCIAL_ACCOUNT: 'round-octagon',
  LOCATION: 'star',
  CASE_ANCHOR: 'triangle'
};

export const NetworkIntelligenceView: React.FC<NetworkIntelligenceViewProps> = ({
  initialCaseId,
  initialEntityId
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [analytics, setAnalytics] = useState<CentralityAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedCaseId, setSelectedCaseId] = useState<number | undefined>(initialCaseId);
  const [includeUnverified, setIncludeUnverified] = useState(true);
  const [minConfidence, setMinConfidence] = useState(0.0);
  const [selectedTypeFilter, setSelectedTypeFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentLayout, setCurrentLayout] = useState('cose');

  // Inspection Drawer
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<any | null>(null);
  const [activeTab, setActiveTab] = useState<'GRAPH' | 'CENTRALITY' | 'COMMUNITIES' | 'PATH_FINDER'>('GRAPH');

  // Path Finder state
  const [pathSourceId, setPathSourceId] = useState<number | ''>('');
  const [pathTargetId, setPathTargetId] = useState<number | ''>('');
  const [pathResult, setPathResult] = useState<any | null>(null);
  const [pathLoading, setPathLoading] = useState(false);

  // Verification in-drawer action
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    loadGraphAndAnalytics();
  }, [selectedCaseId, includeUnverified, minConfidence, selectedTypeFilter]);

  const loadGraphAndAnalytics = async () => {
    setLoading(true);
    try {
      const typeParam = selectedTypeFilter === 'ALL' ? undefined : selectedTypeFilter;
      const [gData, aData] = await Promise.all([
        api.getGraphData({
          case_id: selectedCaseId,
          include_unverified: includeUnverified,
          min_confidence: minConfidence,
          entity_types: typeParam
        }),
        api.getGraphAnalytics(selectedCaseId)
      ]);
      setGraphData(gData);
      setAnalytics(aData);
      initCytoscape(gData);
    } catch (err) {
      console.error('Failed to load graph data', err);
    } finally {
      setLoading(false);
    }
  };

  const initCytoscape = (data: GraphData) => {
    if (!containerRef.current) return;

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const elements = [
      ...data.nodes.map((n) => ({
        group: 'nodes' as const,
        data: n.data
      })),
      ...data.edges.map((e) => ({
        group: 'edges' as const,
        data: e.data
      }))
    ];

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#F8FAFC',
            'font-family': 'Plus Jakarta Sans, sans-serif',
            'font-size': '11px',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'text-outline-color': '#080D1A',
            'text-outline-width': 2,
            'background-color': (ele: any) => ENTITY_COLORS[ele.data('entity_type')] || '#06B6D4',
            'shape': (ele: any) => ENTITY_SHAPES[ele.data('entity_type')] || 'ellipse',
            'width': (ele: any) => Math.max(30, 24 + (ele.data('degree') || 1) * 7),
            'height': (ele: any) => Math.max(30, 24 + (ele.data('degree') || 1) * 7),
            'border-width': 2,
            'border-color': (ele: any) =>
              ele.data('risk_level') === 'CRITICAL' ? '#EF4444' : '#1E293B',
            'transition-property': 'background-color, line-color, target-arrow-color',
            'transition-duration': 0.2
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#38BDF8',
            'border-width': 4,
            'border-opacity': 1
          }
        },
        {
          selector: 'edge',
          style: {
            'width': (ele: any) => Math.max(1.5, (ele.data('weight') || 1) * 2),
            'line-color': (ele: any) => {
              if (ele.data('verification_status') === 'VERIFIED') return '#0284C7';
              if (ele.data('verification_status') === 'PENDING_REVIEW') return '#F59E0B';
              return '#EF4444';
            },
            'target-arrow-color': (ele: any) => {
              if (ele.data('verification_status') === 'VERIFIED') return '#0284C7';
              if (ele.data('verification_status') === 'PENDING_REVIEW') return '#F59E0B';
              return '#EF4444';
            },
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'line-style': (ele: any) =>
              ele.data('verification_status') === 'VERIFIED' ? 'solid' : 'dashed',
            'opacity': 0.8,
            'label': 'data(label)',
            'font-size': '9px',
            'color': '#94A3B8',
            'text-outline-color': '#080D1A',
            'text-outline-width': 1.5,
            'text-rotation': 'autorotate'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#38BDF8',
            'target-arrow-color': '#38BDF8',
            'width': 4,
            'opacity': 1.0
          }
        },
        {
          selector: '.highlighted',
          style: {
            'border-color': '#38BDF8',
            'border-width': 4,
            'line-color': '#38BDF8',
            'target-arrow-color': '#38BDF8'
          }
        },
        {
          selector: '.faded',
          style: {
            'opacity': 0.15
          }
        }
      ],
      layout: {
        name: currentLayout,
        padding: 50
      } as any
    });

    cy.on('tap', 'node', (evt: EventObject) => {
      const node = evt.target;
      setSelectedNode(node.data());
      setSelectedEdge(null);
    });

    cy.on('tap', 'edge', (evt: EventObject) => {
      const edge = evt.target;
      setSelectedEdge(edge.data());
      setSelectedNode(null);
    });

    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedNode(null);
        setSelectedEdge(null);
        cy.elements().removeClass('highlighted faded');
      }
    });

    cyRef.current = cy;

    // Focus on initial entity if provided
    if (initialEntityId) {
      const targetNode = cy.$(`node[id = "${initialEntityId}"]`);
      if (targetNode.length) {
        targetNode.select();
        setSelectedNode(targetNode.data());
        cy.center(targetNode);
        cy.zoom(1.4);
      }
    }
  };

  const handleSearchEntity = (term: string) => {
    setSearchTerm(term);
    if (!cyRef.current) return;
    const cy = cyRef.current;

    if (!term.trim()) {
      cy.elements().removeClass('highlighted faded');
      return;
    }

    const matchedNodes = cy.nodes().filter((ele) => {
      const name = ele.data('name') || '';
      return name.toLowerCase().includes(term.toLowerCase());
    });

    if (matchedNodes.length > 0) {
      cy.elements().addClass('faded');
      matchedNodes.removeClass('faded').addClass('highlighted');
      matchedNodes.connectedEdges().removeClass('faded').addClass('highlighted');
      matchedNodes.neighborhood().nodes().removeClass('faded');
      cy.center(matchedNodes);
    } else {
      cy.elements().removeClass('highlighted faded');
    }
  };

  const handleLayoutChange = (layoutName: string) => {
    setCurrentLayout(layoutName);
    if (cyRef.current) {
      cyRef.current.layout({ name: layoutName, animate: true, animationDuration: 500 } as any).run();
    }
  };

  const handleVerifyEdge = async (relId: number, newStatus: string) => {
    setVerifying(true);
    try {
      await api.verifyRelationship(relId, newStatus, 'Investigator verified via graph inspector');
      await loadGraphAndAnalytics();
      if (selectedEdge) {
        setSelectedEdge({ ...selectedEdge, verification_status: newStatus });
      }
    } catch (err: any) {
      alert(`Verification failed: ${err.message}`);
    } finally {
      setVerifying(false);
    }
  };

  const handleFindPath = async () => {
    if (!pathSourceId || !pathTargetId) return;
    setPathLoading(true);
    try {
      const res = await api.findShortestPath(Number(pathSourceId), Number(pathTargetId));
      setPathResult(res);

      // Highlight path on Cytoscape graph
      if (cyRef.current && res.found) {
        const cy = cyRef.current;
        cy.elements().addClass('faded');

        res.path_nodes.forEach((n: any) => {
          cy.$(`node[id = "${n.id}"]`).removeClass('faded').addClass('highlighted');
        });

        res.path_edges.forEach((e: any) => {
          cy.$(`edge[source = "${e.source}"][target = "${e.target}"]`).removeClass('faded').addClass('highlighted');
          cy.$(`edge[source = "${e.target}"][target = "${e.source}"]`).removeClass('faded').addClass('highlighted');
        });
      }
    } catch (err: any) {
      alert(`Pathfinding error: ${err.message}`);
    } finally {
      setPathLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col overflow-hidden bg-[#080D1A]">
      {/* Top Toolbar */}
      <div className="h-14 px-6 bg-[#0D1527]/90 border-b border-slate-800/80 flex items-center justify-between shrink-0 gap-4">
        {/* Navigation Tabs */}
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => setActiveTab('GRAPH')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'GRAPH'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Graph Canvas
          </button>
          <button
            onClick={() => setActiveTab('CENTRALITY')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'CENTRALITY'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Centrality Rankings
          </button>
          <button
            onClick={() => setActiveTab('COMMUNITIES')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'COMMUNITIES'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Modularity Cells
          </button>
          <button
            onClick={() => setActiveTab('PATH_FINDER')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all flex items-center space-x-1 ${
              activeTab === 'PATH_FINDER'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Route className="w-3.5 h-3.5 text-cyan-400" />
            <span>Path Finder</span>
          </button>
        </div>

        {/* Live Search & Stats */}
        <div className="flex items-center space-x-3">
          <div className="relative w-48 sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => handleSearchEntity(e.target.value)}
              placeholder="Highlight entity in network..."
              className="w-full pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-700/80 rounded-lg text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
            />
          </div>

          {graphData && (
            <div className="hidden lg:flex items-center space-x-3 text-[11px] font-mono text-slate-400 border-l border-slate-800 pl-3">
              <span>NODES: <strong className="text-cyan-400">{graphData.stats.node_count}</strong></span>
              <span>EDGES: <strong className="text-blue-400">{graphData.stats.edge_count}</strong></span>
              <span className="text-emerald-400">VERIFIED: {graphData.stats.verified_edge_count}</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* TAB 1: GRAPH CANVAS */}
        {activeTab === 'GRAPH' && (
          <div className="flex-1 flex relative">
            {/* Cytoscape Container */}
            <div ref={containerRef} className="flex-1 h-full bg-[#060A14] cursor-grab active:cursor-grabbing" />

            {/* Canvas Floating Controls */}
            <div className="absolute top-4 left-4 z-20 flex flex-col space-y-2">
              {/* Zoom & Fit controls */}
              <div className="bg-[#0D1527]/90 border border-slate-800 rounded-xl p-1.5 flex flex-col space-y-1 shadow-2xl backdrop-blur-md">
                <button
                  onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded"
                  title="Zoom In"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <button
                  onClick={() => cyRef.current?.fit(undefined, 40)}
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded"
                  title="Fit to Screen"
                >
                  <Maximize2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => cyRef.current?.reset()}
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded"
                  title="Reset Position"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>

              {/* Layout selector */}
              <div className="bg-[#0D1527]/90 border border-slate-800 rounded-xl p-2 shadow-2xl backdrop-blur-md">
                <span className="text-[9px] font-mono text-slate-500 uppercase block font-semibold mb-1">
                  LAYOUT ENGINE
                </span>
                <select
                  value={currentLayout}
                  onChange={(e) => handleLayoutChange(e.target.value)}
                  className="w-full text-xs bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 font-mono focus:outline-none"
                >
                  <option value="cose">Force-Directed (COSE)</option>
                  <option value="concentric">Concentric (Hubs)</option>
                  <option value="circle">Circular Ring</option>
                  <option value="breadthfirst">Hierarchical Tree</option>
                  <option value="grid">Orthogonal Grid</option>
                </select>
              </div>
            </div>

            {/* Filter Bar overlay at bottom left */}
            <div className="absolute bottom-4 left-4 z-20 bg-[#0D1527]/90 border border-slate-800 rounded-xl p-3 shadow-2xl backdrop-blur-md max-w-sm space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-slate-300">
                <span className="flex items-center space-x-1.5">
                  <Filter className="w-3.5 h-3.5 text-cyan-400" />
                  <span>GRAPH FILTERS</span>
                </span>
                <label className="flex items-center space-x-1.5 cursor-pointer text-[10px]">
                  <input
                    type="checkbox"
                    checked={includeUnverified}
                    onChange={(e) => setIncludeUnverified(e.target.checked)}
                    className="accent-cyan-500"
                  />
                  <span>Show Unverified</span>
                </label>
              </div>

              {/* Entity Type Filter pills */}
              <div className="flex flex-wrap gap-1 text-[10px] font-mono">
                {['ALL', 'PERSON', 'PHONE_NUMBER', 'ORGANIZATION', 'FINANCIAL_ACCOUNT', 'VEHICLE'].map((t) => (
                  <button
                    key={t}
                    onClick={() => setSelectedTypeFilter(t)}
                    className={`px-2 py-0.5 rounded border ${
                      selectedTypeFilter === t
                        ? 'bg-cyan-950 text-cyan-300 border-cyan-700 font-bold'
                        : 'bg-slate-900 text-slate-400 border-slate-800'
                    }`}
                  >
                    {t.replace('_', ' ')}
                  </button>
                ))}
              </div>

              {/* Confidence slider */}
              <div className="pt-1">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mb-1">
                  <span>Min Extraction Confidence:</span>
                  <span className="text-cyan-400 font-bold">{Math.round(minConfidence * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="0.95"
                  step="0.05"
                  value={minConfidence}
                  onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>
            </div>

            {/* Right Inspector Panel */}
            {(selectedNode || selectedEdge) && (
              <div className="w-80 sm:w-96 bg-[#0D1527]/95 border-l border-slate-800 p-5 flex flex-col justify-between overflow-y-auto z-30 shadow-2xl backdrop-blur-md">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-bold">
                      {selectedNode ? 'ENTITY DOSSIER INSPECTOR' : 'SUPPORTING EVIDENCE INSPECTOR'}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedNode(null);
                        setSelectedEdge(null);
                      }}
                      className="text-slate-400 hover:text-white text-xs font-mono"
                    >
                      ✕ Close
                    </button>
                  </div>

                  {/* Selected Node Details */}
                  {selectedNode && (
                    <div className="space-y-4 mt-4">
                      <div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded uppercase font-bold bg-slate-800 text-cyan-300 border border-slate-700">
                          {selectedNode.entity_type}
                        </span>
                        <h3 className="text-base font-extrabold text-white mt-1.5">{selectedNode.name}</h3>
                        {selectedNode.canonical_name && selectedNode.canonical_name !== selectedNode.name && (
                          <p className="text-xs text-slate-400 font-mono">Canonical: {selectedNode.canonical_name}</p>
                        )}
                      </div>

                      {/* Structural Metrics */}
                      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-500 uppercase block">Connections</span>
                          <span className="text-cyan-400 font-bold text-sm">{selectedNode.degree || 0} links</span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-500 uppercase block">Betweenness</span>
                          <span className="text-blue-400 font-bold text-sm">
                            {selectedNode.betweenness ? Number(selectedNode.betweenness).toFixed(4) : '0.000'}
                          </span>
                        </div>
                      </div>

                      {/* Aliases */}
                      {selectedNode.aliases && selectedNode.aliases.length > 0 && (
                        <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                          <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Aliases:</span>
                          <p className="text-xs text-slate-200 font-mono">{selectedNode.aliases.join(', ')}</p>
                        </div>
                      )}

                      {/* Identifiers */}
                      {selectedNode.identifiers && Object.keys(selectedNode.identifiers).length > 0 && (
                        <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
                          <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Identifiers:</span>
                          {Object.entries(selectedNode.identifiers).map(([k, v]) => (
                            <div key={k} className="font-mono text-[11px] text-slate-300">
                              <span className="text-slate-500">{k}:</span> {String(v)}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Selected Edge Details (Provenance Engine) */}
                  {selectedEdge && (
                    <div className="space-y-4 mt-4">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span
                            className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-bold ${
                              selectedEdge.verification_status === 'VERIFIED'
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                : 'bg-amber-950 text-amber-400 border border-amber-800'
                            }`}
                          >
                            {selectedEdge.verification_status}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400">
                            Confidence: {Math.round(selectedEdge.confidence_score * 100)}%
                          </span>
                        </div>

                        <h3 className="text-sm font-extrabold text-white mt-2">
                          {selectedEdge.relation_type.replace('_', ' ')}
                        </h3>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">
                          Source #{selectedEdge.source} ➔ Target #{selectedEdge.target}
                        </p>
                      </div>

                      {/* Evidence Citations / Actions */}
                      <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 space-y-2">
                        <span className="text-[10px] font-mono uppercase text-cyan-400 font-semibold block">
                          Human Verification Controls:
                        </span>
                        <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
                          Investigators must approve AI-extracted relationship triples before they can be considered confirmed evidence.
                        </p>

                        <div className="flex items-center space-x-2 pt-2">
                          <button
                            disabled={verifying || selectedEdge.verification_status === 'VERIFIED'}
                            onClick={() => handleVerifyEdge(selectedEdge.rel_id, 'VERIFIED')}
                            className="flex-1 py-1.5 px-3 rounded bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 text-white font-mono text-xs font-semibold flex items-center justify-center space-x-1 transition-all"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Verify Fact</span>
                          </button>
                          <button
                            disabled={verifying || selectedEdge.verification_status === 'REJECTED'}
                            onClick={() => handleVerifyEdge(selectedEdge.rel_id, 'REJECTED')}
                            className="flex-1 py-1.5 px-3 rounded bg-red-900/60 hover:bg-red-800 disabled:opacity-40 text-red-200 border border-red-700 font-mono text-xs font-semibold flex items-center justify-center space-x-1 transition-all"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Reject Link</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Disclaimer */}
                <div className="mt-6 pt-3 border-t border-slate-800 text-[10px] text-slate-500 font-mono leading-normal">
                  NOTICE: High connectivity does not indicate criminal culpability. Verified documents required.
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: CENTRALITY METRICS RANKINGS */}
        {activeTab === 'CENTRALITY' && analytics && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6 max-w-6xl mx-auto">
            {/* Plain language banner */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950/60 to-slate-900 border border-blue-800/60 flex items-start space-x-3">
              <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
              <div className="text-xs leading-relaxed text-slate-300">
                <span className="font-bold text-white uppercase font-mono block mb-0.5">
                  Explainable Graph Centrality Methodology:
                </span>
                {analytics.methodology_notes.disclaimer}
              </div>
            </div>

            {/* Three Columns: Degree, Betweenness, PageRank */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Degree Centrality */}
              <div className="p-5 rounded-xl bg-[#0D1527] border border-slate-800 shadow-xl space-y-3">
                <div className="border-b border-slate-800 pb-2">
                  <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-cyan-400">
                    DEGREE CENTRALITY (HUBS)
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">Entities with highest volume of direct links</p>
                </div>
                <div className="space-y-2.5">
                  {analytics.degree_centrality.map((item, idx) => (
                    <div key={item.id} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200 truncate">{idx + 1}. {item.name}</span>
                        <span className="font-mono text-cyan-400 font-bold">{item.raw_degree} links</span>
                      </div>
                      <p className="text-[10px] text-slate-400 mt-1">{item.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Betweenness Centrality */}
              <div className="p-5 rounded-xl bg-[#0D1527] border border-slate-800 shadow-xl space-y-3">
                <div className="border-b border-slate-800 pb-2">
                  <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-blue-400">
                    BETWEENNESS (BRIDGES)
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">Gateway nodes controlling flow across cells</p>
                </div>
                <div className="space-y-2.5">
                  {analytics.betweenness_centrality.map((item, idx) => (
                    <div key={item.id} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200 truncate">{idx + 1}. {item.name}</span>
                        <span className="font-mono text-blue-400 font-bold">{item.score.toFixed(4)}</span>
                      </div>
                      <p className="text-[10px] text-slate-400 mt-1">{item.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* PageRank */}
              <div className="p-5 rounded-xl bg-[#0D1527] border border-slate-800 shadow-xl space-y-3">
                <div className="border-b border-slate-800 pb-2">
                  <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-purple-400">
                    PAGERANK (STRUCTURAL INFLUENCE)
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">Recursive centrality from influential neighbors</p>
                </div>
                <div className="space-y-2.5">
                  {analytics.pagerank.map((item, idx) => (
                    <div key={item.id} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200 truncate">{idx + 1}. {item.name}</span>
                        <span className="font-mono text-purple-400 font-bold">{item.score.toFixed(4)}</span>
                      </div>
                      <p className="text-[10px] text-slate-400 mt-1">{item.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: MODULARITY & COMMUNITIES */}
        {activeTab === 'COMMUNITIES' && analytics && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6 max-w-6xl mx-auto">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-extrabold text-white tracking-wide">
                  GREEDY MODULARITY COMMUNITY DETECTION
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Algorithms mathematically identify tightly connected sub-cells and functional modules within the criminal network.
                </p>
              </div>
              <span className="px-3 py-1 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono text-xs">
                {analytics.communities.length} Communities Discovered
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {analytics.communities.map((comm) => (
                <div key={comm.community_id} className="p-5 rounded-xl bg-[#0D1527] border border-slate-800 shadow-xl">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <span className="text-sm font-bold text-white">{comm.label}</span>
                    <span className="text-xs font-mono text-cyan-400 px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800">
                      {comm.size} Members
                    </span>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-2">
                    {comm.members.map((m) => (
                      <span
                        key={m.id}
                        className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700/80 text-xs font-mono text-slate-200 flex items-center space-x-1.5"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        <span>{m.name}</span>
                        <span className="text-[9px] text-slate-500 uppercase">({m.type})</span>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: SHORTEST PATH FINDER */}
        {activeTab === 'PATH_FINDER' && graphData && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6 max-w-4xl mx-auto">
            <div>
              <h2 className="text-base font-extrabold text-white tracking-wide">
                INVESTIGATIVE CHAIN & SHORTEST PATH FINDER
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Calculate the shortest evidence-backed investigative link connecting any two entities across cases.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-[#0D1527] border border-slate-800 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase mb-1">Source Entity</label>
                  <select
                    value={pathSourceId}
                    onChange={(e) => setPathSourceId(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="">Select origin entity...</option>
                    {graphData.nodes.map((n) => (
                      <option key={n.data.id} value={n.data.id}>
                        {n.data.name} ({n.data.entity_type})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase mb-1">Target Entity</label>
                  <select
                    value={pathTargetId}
                    onChange={(e) => setPathTargetId(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="">Select destination entity...</option>
                    {graphData.nodes.map((n) => (
                      <option key={n.data.id} value={n.data.id}>
                        {n.data.name} ({n.data.entity_type})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                disabled={!pathSourceId || !pathTargetId || pathLoading}
                onClick={handleFindPath}
                className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs tracking-wider uppercase transition-all shadow-md shadow-cyan-950 disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                <Route className="w-4 h-4" />
                <span>{pathLoading ? 'Tracing Connection...' : 'Calculate Evidentiary Path'}</span>
              </button>
            </div>

            {/* Path Results */}
            {pathResult && (
              <div className="p-5 rounded-xl bg-[#0D1527] border border-cyan-800/80 shadow-xl space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span className="font-mono text-xs font-bold text-cyan-300">
                    PATH RESULT: {pathResult.found ? `${pathResult.total_hops} HOPS DISCOVERED` : 'NO PATH FOUND'}
                  </span>
                  {pathResult.found && (
                    <button
                      onClick={() => setActiveTab('GRAPH')}
                      className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center space-x-1"
                    >
                      <span>View on Graph Canvas</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <div className="space-y-2.5">
                  {pathResult.evidence_chain.map((step: string, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-200 flex items-start space-x-2"
                    >
                      <span className="text-cyan-400 font-bold shrink-0">{idx + 1}.</span>
                      <span className="leading-relaxed">{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
