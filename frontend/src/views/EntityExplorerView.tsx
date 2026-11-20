import React, { useState, useEffect } from 'react';
import {
  Users2, Search, Filter, Shield, Phone, Cpu, Truck, CreditCard,
  MapPin, Hash, Plus, CheckCircle2, AlertTriangle, ArrowRight, X, GitMerge, FileText
} from 'lucide-react';
import { api } from '../api';
import { Entity, EntityMatchSuggestion } from '../types';
import { NavTab } from '../components/Sidebar';

interface EntityExplorerViewProps {
  onNavigate: (tab: NavTab) => void;
  onSelectEntityForGraph?: (entityId: number) => void;
}

export const EntityExplorerView: React.FC<EntityExplorerViewProps> = ({ onNavigate, onSelectEntityForGraph }) => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [suggestions, setSuggestions] = useState<EntityMatchSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [activeTab, setActiveTab] = useState<'ENTITIES' | 'MATCHING_QUEUE'>('ENTITIES');

  // Selected Entity modal
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);

  // Match review state
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewingId, setReviewingId] = useState<number | null>(null);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [eData, sData] = await Promise.all([
        api.listEntities(),
        api.listMatchSuggestions(),
      ]);
      setEntities(eData);
      setSuggestions(sData);
    } catch (err) {
      console.error('Failed to load entities', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewSuggestion = async (id: number, status: 'APPROVED_MERGE' | 'REJECTED') => {
    try {
      await api.reviewMatchSuggestion(id, status, reviewNotes || `Investigator marked as ${status}`);
      setSuggestions(suggestions.filter((s) => s.id !== id));
      setReviewingId(null);
      setReviewNotes('');
      // Reload entities to reflect merged changes
      const updatedEntities = await api.listEntities();
      setEntities(updatedEntities);
    } catch (err: any) {
      alert(`Error reviewing match: ${err.message}`);
    }
  };

  const handleRunMatchingEngine = async () => {
    try {
      const res = await api.runEntityMatching();
      alert(`Automated scan complete: ${res.new_suggestions} new match suggestions detected.`);
      const sData = await api.listMatchSuggestions();
      setSuggestions(sData);
    } catch (err: any) {
      alert(`Error running matching engine: ${err.message}`);
    }
  };

  const getEntityIcon = (type: string) => {
    switch (type) {
      case 'PERSON': return Users2;
      case 'ORGANIZATION': return Shield;
      case 'PHONE_NUMBER': return Phone;
      case 'DEVICE': return Cpu;
      case 'VEHICLE': return Truck;
      case 'FINANCIAL_ACCOUNT': return CreditCard;
      case 'LOCATION': return MapPin;
      default: return Hash;
    }
  };

  const filteredEntities = entities.filter((e) => {
    const matchesSearch =
      e.name.toLowerCase().includes(search.toLowerCase()) ||
      (e.canonical_name && e.canonical_name.toLowerCase().includes(search.toLowerCase())) ||
      (e.aliases && e.aliases.some((a) => a.toLowerCase().includes(search.toLowerCase())));
    const matchesType = typeFilter === 'ALL' || e.entity_type === typeFilter;
    const matchesRisk = riskFilter === 'ALL' || e.risk_level === riskFilter;
    return matchesSearch && matchesType && matchesRisk;
  });

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold text-white tracking-wide">
              STRUCTURED ENTITY REPOSITORY
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
              {entities.length} TOTAL ENTITIES
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Multi-type entity records across persons, burner devices, logistics vehicles, shell companies and accounts.
          </p>
        </div>

        {/* Tab switch between directory and matching queue */}
        <div className="flex items-center space-x-2 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('ENTITIES')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
              activeTab === 'ENTITIES'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Entity Directory ({entities.length})
          </button>
          <button
            onClick={() => setActiveTab('MATCHING_QUEUE')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === 'MATCHING_QUEUE'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <GitMerge className="w-3.5 h-3.5 text-cyan-400" />
            <span>Matching Queue</span>
            {suggestions.length > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
                {suggestions.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* VIEW 1: ENTITIES DIRECTORY */}
      {activeTab === 'ENTITIES' && (
        <div className="space-y-4">
          {/* Search & Filter Bar */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 rounded-xl bg-[#0D1527]/80 border border-slate-800/80">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search entity name, documented alias, or identifier..."
                className="w-full pl-9 pr-3 py-1.5 bg-slate-900/90 border border-slate-700/80 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            {/* Type selector */}
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase">Type:</span>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
              >
                <option value="ALL">ALL TYPES</option>
                <option value="PERSON">PERSON</option>
                <option value="ORGANIZATION">ORGANIZATION</option>
                <option value="PHONE_NUMBER">PHONE NUMBER</option>
                <option value="DEVICE">DEVICE</option>
                <option value="VEHICLE">VEHICLE</option>
                <option value="FINANCIAL_ACCOUNT">FINANCIAL ACCOUNT</option>
                <option value="LOCATION">LOCATION</option>
              </select>

              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
              >
                <option value="ALL">ALL RISKS</option>
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="ELEVATED">ELEVATED</option>
                <option value="LOW">LOW</option>
              </select>
            </div>
          </div>

          {/* Grid */}
          {loading ? (
            <div className="py-20 flex justify-center items-center text-cyan-400 font-mono text-xs">
              FETCHING ENTITY DOSSIERS...
            </div>
          ) : filteredEntities.length === 0 ? (
            <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400">
              <p className="text-sm font-semibold">No entities match your search criteria.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredEntities.map((ent) => {
                const Icon = getEntityIcon(ent.entity_type);
                const isCritical = ent.risk_level === 'CRITICAL';
                const isVerified = ent.verification_status === 'VERIFIED';
                return (
                  <div
                    key={ent.id}
                    onClick={() => setSelectedEntity(ent)}
                    className="p-4 rounded-xl bg-[#0D1527]/90 border border-slate-800/80 hover:border-cyan-600/60 transition-all cursor-pointer shadow-lg hover:shadow-cyan-950/20 group flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2.5">
                          <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700/80 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform">
                            <Icon className="w-4 h-4" />
                          </div>
                          <div>
                            <span className="text-[10px] font-mono uppercase text-slate-400">
                              {ent.entity_type.replace('_', ' ')}
                            </span>
                            <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors line-clamp-1">
                              {ent.name}
                            </h3>
                          </div>
                        </div>

                        <span
                          className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                            isCritical
                              ? 'bg-rose-950 text-rose-400 border border-rose-800'
                              : 'bg-amber-950 text-amber-400 border border-amber-800'
                          }`}
                        >
                          {ent.risk_level}
                        </span>
                      </div>

                      {/* Aliases */}
                      {ent.aliases && ent.aliases.length > 0 && (
                        <div className="text-[11px] text-slate-400 font-mono mt-2 truncate">
                          <span className="text-slate-500 font-semibold">AKA: </span>
                          <span>{ent.aliases.join(', ')}</span>
                        </div>
                      )}

                      {/* Notes / Attributes */}
                      <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                        {ent.notes || Object.values(ent.attributes || {}).join(' • ') || 'No additional intelligence annotations.'}
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                      <span
                        className={`text-[10px] flex items-center space-x-1 ${
                          isVerified ? 'text-emerald-400' : 'text-amber-400'
                        }`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${isVerified ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                        <span>{isVerified ? 'FACT VERIFIED' : 'UNVERIFIED'}</span>
                      </span>

                      <span className="text-slate-400 text-[11px]">
                        Links: <strong className="text-cyan-400 font-bold">{ent.degree || 0}</strong>
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* VIEW 2: UNCERTAINTY-AWARE ENTITY MATCHING QUEUE */}
      {activeTab === 'MATCHING_QUEUE' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-[#0D1527] border border-cyan-900/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <GitMerge className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-cyan-300">
                  UNCERTAINTY-AWARE ENTITY RESOLUTION PIPELINE
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                AI cross-case identity matching evaluates phonetic similarity, token overlap, shared phones, and tax/crypto identifiers.
                Decisions require human investigator approval.
              </p>
            </div>

            <button
              onClick={handleRunMatchingEngine}
              className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs tracking-wider uppercase transition-all shadow-md shadow-cyan-950 shrink-0 self-start md:self-auto"
            >
              Run Scan on All Cases
            </button>
          </div>

          {suggestions.length === 0 ? (
            <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-200">Matching Queue Clear</p>
              <p className="text-xs text-slate-500 mt-1">No unresolved cross-case entity duplicates currently pending review.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {suggestions.map((sug) => {
                const isUnderReview = reviewingId === sug.id;
                return (
                  <div
                    key={sug.id}
                    className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800/90 shadow-xl space-y-3"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                      <div className="flex items-center space-x-2">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold uppercase">
                          CANDIDATE DUPLICATE PAIR #{sug.id}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          TYPE: {sug.primary_entity_type}
                        </span>
                      </div>

                      <div className="flex items-center space-x-2">
                        <span className="text-[11px] font-mono text-slate-400">Similarity Confidence:</span>
                        <span className="text-xs font-mono font-bold text-cyan-400 px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800">
                          {Math.round(sug.similarity_score * 100)}%
                        </span>
                      </div>
                    </div>

                    {/* Entity Pair Display */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                        <span className="text-[10px] font-mono text-cyan-400 uppercase block font-semibold">Primary Case Record</span>
                        <h4 className="text-sm font-bold text-white mt-0.5">{sug.primary_entity_name}</h4>
                        <span className="text-[11px] text-slate-400 font-mono">Entity ID #{sug.primary_entity_id}</span>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                        <span className="text-[10px] font-mono text-purple-400 uppercase block font-semibold">Candidate Duplicate Record</span>
                        <h4 className="text-sm font-bold text-white mt-0.5">{sug.candidate_entity_name}</h4>
                        <span className="text-[11px] text-slate-400 font-mono">Entity ID #{sug.candidate_entity_id}</span>
                      </div>
                    </div>

                    {/* Match Reasons */}
                    <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800/80">
                      <span className="text-[10px] font-mono uppercase text-slate-400 block font-semibold mb-1">
                        Explainable Match Reasons:
                      </span>
                      <ul className="space-y-1 text-xs text-slate-300">
                        {sug.match_reasons.map((r, i) => (
                          <li key={i} className="flex items-start space-x-1.5">
                            <span className="text-cyan-400 font-bold">•</span>
                            <span>{r}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Action Bar */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
                      <input
                        type="text"
                        value={isUnderReview ? reviewNotes : ''}
                        onChange={(e) => {
                          setReviewingId(sug.id);
                          setReviewNotes(e.target.value);
                        }}
                        placeholder="Add investigator review remarks before approving or rejecting merge..."
                        className="flex-1 px-3 py-1.5 bg-slate-900 border border-slate-700/80 rounded-lg text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                      />

                      <div className="flex items-center space-x-2 shrink-0">
                        <button
                          onClick={() => handleReviewSuggestion(sug.id, 'REJECTED')}
                          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
                        >
                          Reject Duplicate
                        </button>
                        <button
                          onClick={() => handleReviewSuggestion(sug.id, 'APPROVED_MERGE')}
                          className="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-semibold flex items-center space-x-1 transition-all shadow-md shadow-emerald-950"
                        >
                          <GitMerge className="w-3.5 h-3.5" />
                          <span>Approve Merge</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Selected Entity Dossier Modal */}
      {selectedEntity && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-2xl bg-[#0D1527] border border-slate-800 rounded-2xl p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedEntity(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2.5 mb-2">
              <span className="font-mono text-xs font-bold text-cyan-400 px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800">
                {selectedEntity.entity_type}
              </span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                  selectedEntity.verification_status === 'VERIFIED'
                    ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    : 'bg-amber-950 text-amber-400 border border-amber-800'
                }`}
              >
                {selectedEntity.verification_status}
              </span>
            </div>

            <h2 className="text-lg font-bold text-white mb-1">{selectedEntity.name}</h2>
            {selectedEntity.canonical_name && selectedEntity.canonical_name !== selectedEntity.name && (
              <p className="text-xs text-slate-400 font-mono mb-3">Canonical: {selectedEntity.canonical_name}</p>
            )}

            <div className="space-y-4 my-4 font-mono text-xs">
              {/* Aliases */}
              {selectedEntity.aliases && selectedEntity.aliases.length > 0 && (
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block mb-1">Documented Aliases / Codewords</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedEntity.aliases.map((a, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                        "{a}"
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Identifiers */}
              {selectedEntity.identifiers && Object.keys(selectedEntity.identifiers).length > 0 && (
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block mb-1">Unique Technical Identifiers</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                    {Object.entries(selectedEntity.identifiers).map(([k, v]) => (
                      <div key={k} className="p-2 rounded bg-slate-950/80 border border-slate-800/80">
                        <span className="text-slate-500 uppercase block text-[9px]">{k}</span>
                        <span className="text-slate-200 font-mono">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes */}
              {selectedEntity.notes && (
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase block mb-1">Investigative Context</span>
                  <p className="text-slate-300 leading-relaxed font-sans">{selectedEntity.notes}</p>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setSelectedEntity(null)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
              >
                Close
              </button>
              <button
                onClick={() => {
                  if (onSelectEntityForGraph) onSelectEntityForGraph(selectedEntity.id);
                  setSelectedEntity(null);
                  onNavigate('graph');
                }}
                className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-md shadow-cyan-950"
              >
                <span>Inspect in Knowledge Graph</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
