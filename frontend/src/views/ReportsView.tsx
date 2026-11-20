import React, { useState, useEffect } from 'react';
import {
  FileText, Printer, Download, Eye, ShieldCheck, AlertTriangle,
  FolderGit2, Users, Share2, CheckCircle2, ChevronRight, ExternalLink
} from 'lucide-react';
import { api } from '../api';
import { Case } from '../types';

export const ReportsView: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<number | ''>('');
  const [loading, setLoading] = useState(true);

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

  const handleOpenPrintableReport = () => {
    const url = api.getReportUrl(selectedCaseId ? Number(selectedCaseId) : undefined);
    window.open(url, '_blank');
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold text-white tracking-wide">
              INVESTIGATION INTELLIGENCE DOSSIER GENERATOR
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-blue-950 text-blue-300 border border-blue-800">
              JUDICIAL & INTER-AGENCY EXPORT
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Compile audited intelligence summaries with evidence provenance citations, centrality analysis, and verification signatures.
          </p>
        </div>

        <button
          onClick={handleOpenPrintableReport}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-blue-950 flex items-center space-x-2 self-start sm:self-auto"
        >
          <Printer className="w-4 h-4" />
          <span>Generate Printable Dossier / PDF</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Case Selection & Options Box */}
      <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            REPORT SCOPE & PARAMETERS
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-[11px] font-mono text-slate-400 uppercase mb-1">
              Select Investigation Scope
            </label>
            <select
              value={selectedCaseId}
              onChange={(e) => setSelectedCaseId(e.target.value ? Number(e.target.value) : '')}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
            >
              <option value="">Full Comprehensive Multi-Agency Summary (All Cases)</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.case_number} - {c.title}
                </option>
              ))}
            </select>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-300 font-mono flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-500 uppercase block">Classification Standard</span>
              <span className="text-red-400 font-bold">LAW ENFORCEMENT SENSITIVE // REL TO JUDICIAL</span>
            </div>
            <ShieldCheck className="w-6 h-6 text-cyan-400 shrink-0" />
          </div>
        </div>
      </div>

      {/* Report Structure Preview Cards */}
      <div className="space-y-4">
        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
          INCLUDED DOSSIER CHAPTERS & EVIDENCE AUDIT:
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
            <span className="text-[10px] font-mono text-cyan-400 uppercase font-bold">Chapter 1</span>
            <h4 className="font-bold text-white">Executive Case Summary</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Jurisdictional background, interdiction dates, primary objectives, and cross-case operational scope.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
            <span className="text-[10px] font-mono text-cyan-400 uppercase font-bold">Chapter 2</span>
            <h4 className="font-bold text-white">Entity Inventory & Roles</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Full structured breakdown of persons, shell corporations, burner SIMs, vehicles, and crypto/bank accounts.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
            <span className="text-[10px] font-mono text-cyan-400 uppercase font-bold">Chapter 3</span>
            <h4 className="font-bold text-white">Verified Relational Evidence</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Audited table of confirmed links citing primary documents, timestamps, and investigator authorization.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
            <span className="text-[10px] font-mono text-amber-400 uppercase font-bold">Chapter 4</span>
            <h4 className="font-bold text-white">Unverified AI Suggestions</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Segregated log of AI NLP-extracted relationship hypotheses pending human verification.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
            <span className="text-[10px] font-mono text-blue-400 uppercase font-bold">Chapter 5</span>
            <h4 className="font-bold text-white">Graph Topology & Centrality</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Mathematical rankings of degree hubs, betweenness bridges, and greedy modularity operational clusters.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
            <span className="text-[10px] font-mono text-rose-400 uppercase font-bold">Chapter 6</span>
            <h4 className="font-bold text-white">Evidentiary Safeguards & Signatures</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Presumption of innocence disclaimer and signature blocks for Lead Investigator & Directorate Reviewer.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
