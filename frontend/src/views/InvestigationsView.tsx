import React, { useState, useEffect } from 'react';
import {
  FolderGit2, Plus, Search, Filter, Calendar, MapPin, Tag,
  FileText, Users, Share2, Upload, AlertCircle, X, CheckCircle2, ChevronRight
} from 'lucide-react';
import { api } from '../api';
import { Case } from '../types';
import { NavTab } from '../components/Sidebar';

interface InvestigationsViewProps {
  onNavigate: (tab: NavTab) => void;
  onSelectCase?: (caseId: number) => void;
}

export const InvestigationsView: React.FC<InvestigationsViewProps> = ({ onNavigate, onSelectCase }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);

  // New Case Modal state
  const [showNewModal, setShowNewModal] = useState(false);
  const [newCaseNumber, setNewCaseNumber] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newSummary, setNewSummary] = useState('');
  const [newPriority, setNewPriority] = useState('HIGH');
  const [newJurisdiction, setNewJurisdiction] = useState('Federal / Multi-Agency');
  const [newTags, setNewTags] = useState('narcotics, maritime, illicit-finance');
  const [createError, setCreateError] = useState<string | null>(null);
  const [createLoading, setCreateLoading] = useState(false);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    setLoading(true);
    try {
      const data = await api.listCases();
      setCases(data);
    } catch (err) {
      console.error('Failed to load cases', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    setCreateError(null);
    try {
      const tagsList = newTags.split(',').map((t) => t.trim()).filter(Boolean);
      const created = await api.createCase({
        case_number: newCaseNumber,
        title: newTitle,
        summary: newSummary,
        priority: newPriority as any,
        jurisdiction: newJurisdiction,
        tags: tagsList,
        status: 'ACTIVE',
      });
      setCases([created, ...cases]);
      setShowNewModal(false);
      setNewCaseNumber('');
      setNewTitle('');
      setNewSummary('');
    } catch (err: any) {
      setCreateError(err.message || 'Failed to create case');
    } finally {
      setCreateLoading(false);
    }
  };

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.case_number.toLowerCase().includes(search.toLowerCase()) ||
      (c.summary && c.summary.toLowerCase().includes(search.toLowerCase()));
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold text-white tracking-wide">
              CASE INVESTIGATIONS REPOSITORY
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-blue-950 text-blue-300 border border-blue-800">
              {cases.length} REGISTERED FILES
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage multi-jurisdiction intelligence cases, link documentary evidence, and coordinate cross-case relationships.
          </p>
        </div>

        <button
          onClick={() => setShowNewModal(true)}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-950 flex items-center space-x-2 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>New Investigation</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 rounded-xl bg-[#0D1527]/80 border border-slate-800/80">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by case code, operation title, or keywords..."
            className="w-full pl-9 pr-3 py-1.5 bg-slate-900/90 border border-slate-700/80 rounded-lg text-slate-200 text-xs focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-mono text-slate-400 uppercase">Status:</span>
          {['ALL', 'ACTIVE', 'UNDER_REVIEW', 'CLOSED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono transition-all ${
                statusFilter === st
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold'
                  : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-slate-800'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Cases Grid */}
      {loading ? (
        <div className="py-20 flex justify-center items-center text-cyan-400 font-mono text-xs">
          FETCHING CASE DIRECTORY...
        </div>
      ) : filteredCases.length === 0 ? (
        <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400">
          <p className="text-sm font-semibold">No investigation cases match your filter criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredCases.map((c) => {
            const isCritical = c.priority === 'CRITICAL';
            return (
              <div
                key={c.id}
                onClick={() => setSelectedCase(c)}
                className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800/80 hover:border-cyan-700/60 transition-all cursor-pointer shadow-lg hover:shadow-cyan-950/30 flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold text-cyan-400 px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/80">
                      {c.case_number}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                        isCritical
                          ? 'bg-rose-950 text-rose-400 border border-rose-800'
                          : 'bg-amber-950 text-amber-400 border border-amber-800'
                      }`}
                    >
                      {c.priority} PRIORITY
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white group-hover:text-cyan-200 transition-colors line-clamp-2">
                    {c.title}
                  </h3>

                  <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
                    {c.summary || 'No detailed case abstract registered.'}
                  </p>

                  <div className="flex items-center space-x-1.5 text-[11px] text-slate-400 font-mono mt-3">
                    <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span className="truncate">{c.jurisdiction}</span>
                  </div>

                  {c.tags && c.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {c.tags.map((t, idx) => (
                        <span
                          key={idx}
                          className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60"
                        >
                          #{t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 font-mono">
                  <div className="flex items-center space-x-3">
                    <span title="Linked Entities" className="flex items-center space-x-1">
                      <Users className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{c.entity_count || 0}</span>
                    </span>
                    <span title="Relationships" className="flex items-center space-x-1">
                      <Share2 className="w-3.5 h-3.5 text-blue-400" />
                      <span>{c.relationship_count || 0}</span>
                    </span>
                    <span title="Evidence Documents" className="flex items-center space-x-1">
                      <FileText className="w-3.5 h-3.5 text-purple-400" />
                      <span>{c.evidence_count || 0}</span>
                    </span>
                  </div>

                  <div className="flex items-center text-cyan-400 text-[11px] font-medium group-hover:translate-x-0.5 transition-transform">
                    <span>Inspect</span>
                    <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Case Detail Modal / Drawer */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-2xl bg-[#0D1527] border border-slate-800 rounded-2xl p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedCase(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2.5 mb-2">
              <span className="font-mono text-xs font-bold text-cyan-400 px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800">
                {selectedCase.case_number}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase bg-emerald-950 text-emerald-400 border border-emerald-800">
                {selectedCase.status}
              </span>
            </div>

            <h2 className="text-lg font-bold text-white mb-2">{selectedCase.title}</h2>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800 mb-4">
              {selectedCase.summary}
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-5 font-mono text-xs">
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">Jurisdiction</span>
                <span className="text-slate-200 font-semibold">{selectedCase.jurisdiction}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">Registered Entities</span>
                <span className="text-cyan-400 font-bold">{selectedCase.entity_count || 0} Entities</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase block">Evidence Records</span>
                <span className="text-purple-400 font-bold">{selectedCase.evidence_count || 0} Documents</span>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => {
                  setSelectedCase(null);
                  onNavigate('evidence');
                }}
                className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
              >
                Upload / View Documents
              </button>
              <button
                onClick={() => {
                  if (onSelectCase) onSelectCase(selectedCase.id);
                  setSelectedCase(null);
                  onNavigate('graph');
                }}
                className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-md shadow-cyan-950"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Open in Knowledge Graph</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Case Creation Modal */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-[#0D1527] border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <button
              onClick={() => setShowNewModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2 mb-4">
              <FolderGit2 className="w-5 h-5 text-cyan-400" />
              <h2 className="text-base font-bold text-white tracking-wide">
                REGISTER NEW INVESTIGATION FILE
              </h2>
            </div>

            {createError && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/70 border border-red-800 text-red-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                <span>{createError}</span>
              </div>
            )}

            <form onSubmit={handleCreateCase} className="space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 mb-1">CASE CODE / NUMBER *</label>
                  <input
                    type="text"
                    value={newCaseNumber}
                    onChange={(e) => setNewCaseNumber(e.target.value)}
                    required
                    placeholder="e.g. CR-2026-1290"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 mb-1">PRIORITY LEVEL</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">OPERATION TITLE *</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  placeholder="e.g. Operation Northern Shield: Logistics Infiltration"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">INVESTIGATIVE ABSTRACT</label>
                <textarea
                  value={newSummary}
                  onChange={(e) => setNewSummary(e.target.value)}
                  rows={3}
                  placeholder="Describe suspected syndicate structure, jurisdictions, and operational scope..."
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs focus:border-cyan-500 focus:outline-none leading-relaxed"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">JURISDICTION</label>
                <input
                  type="text"
                  value={newJurisdiction}
                  onChange={(e) => setNewJurisdiction(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">TAGS (COMMA SEPARATED)</label>
                <input
                  type="text"
                  value={newTags}
                  onChange={(e) => setNewTags(e.target.value)}
                  placeholder="narcotics, shell-corp, crypto, customs"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLoading}
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-all shadow-md shadow-cyan-950 disabled:opacity-50"
                >
                  {createLoading ? 'Creating...' : 'Initialize Case'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
