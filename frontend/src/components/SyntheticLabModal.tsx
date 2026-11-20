import React, { useState, useEffect } from 'react';
import {
  Sparkles, X, Check, RefreshCw, Download, Database, ShieldAlert,
  ArrowRight, Layers, FileText, CheckCircle2
} from 'lucide-react';
import { api } from '../api';

interface SyntheticLabModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScenarioLoaded: () => void;
}

export const SyntheticLabModal: React.FC<SyntheticLabModalProps> = ({
  isOpen,
  onClose,
  onScenarioLoaded
}) => {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeScenarioId, setActiveScenarioId] = useState<string>('BLUE_HORIZON');
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadScenarios();
    }
  }, [isOpen]);

  const loadScenarios = async () => {
    try {
      const data = await api.listSyntheticScenarios();
      setScenarios(data);
    } catch (err) {
      console.error('Failed to load synthetic scenarios', err);
    }
  };

  const handleSelectScenario = async (scId: string) => {
    setLoading(true);
    setStatusMessage(null);
    try {
      const res = await api.loadSyntheticScenario(scId);
      setActiveScenarioId(scId);
      setStatusMessage(`Successfully loaded scenario: "${res.scenario}" (${res.entities} entities, ${res.relationships} relationships, ${res.cases} cases).`);
      onScenarioLoaded();
    } catch (err: any) {
      setStatusMessage(`Error loading scenario: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleResetToBaseline = async () => {
    setLoading(true);
    setStatusMessage(null);
    try {
      const res = await api.resetSyntheticDataset();
      setActiveScenarioId('BLUE_HORIZON');
      setStatusMessage(`Restored pristine demonstration baseline (${res.entities} entities, ${res.relationships} relationships).`);
      onScenarioLoaded();
    } catch (err: any) {
      setStatusMessage(`Error resetting dataset: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleExportDataset = async () => {
    try {
      const data = await api.exportSyntheticDataset();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `synthetic_criminal_network_dataset_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(`Export error: ${err.message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-[#0D1527] border border-cyan-800/80 rounded-2xl p-6 shadow-2xl relative max-h-[92vh] overflow-y-auto space-y-5">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div>
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-lg bg-cyan-950 border border-cyan-700 text-cyan-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-white tracking-wide">
                SYNTHETIC DATA LAB & INVESTIGATIVE SCENARIOS
              </h2>
              <p className="text-[11px] text-cyan-300 font-mono">
                SELECT, GENERATE & EVALUATE MULTI-JURISDICTION INVESTIGATIVE DATASETS
              </p>
            </div>
          </div>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            All records are original synthetic intelligence models designed to demonstrate complex graph analytics, cross-case capital convergence, and uncertainty-aware entity matching without using copyrighted datasets or real PII.
          </p>
        </div>

        {/* Feedback Alert */}
        {statusMessage && (
          <div className="p-3 rounded-lg bg-cyan-950/70 border border-cyan-700 text-cyan-200 text-xs font-mono flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>{statusMessage}</span>
          </div>
        )}

        {/* Scenarios Grid */}
        <div className="space-y-3">
          <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block">
            Pre-Packaged Multi-Agency Scenarios:
          </span>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {scenarios.map((sc) => {
              const isSelected = activeScenarioId === sc.id;
              return (
                <div
                  key={sc.id}
                  className={`p-4 rounded-xl border transition-all flex flex-col justify-between space-y-3 ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500 shadow-lg shadow-cyan-950/40 ring-1 ring-cyan-500/50'
                      : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded uppercase font-bold bg-slate-800 text-cyan-300 border border-slate-700">
                        {sc.id}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {sc.cases_count} Cases • {sc.entities_count} Entities
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-white">{sc.title}</h4>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-3">
                      {sc.description}
                    </p>

                    <div className="mt-2 text-[10px] text-cyan-400 font-mono">
                      <strong>Focus:</strong> {sc.focus}
                    </div>
                  </div>

                  <button
                    disabled={loading}
                    onClick={() => handleSelectScenario(sc.id)}
                    className={`w-full py-2 px-3 rounded-lg text-xs font-mono font-semibold flex items-center justify-center space-x-1.5 transition-all ${
                      isSelected
                        ? 'bg-cyan-600 text-white shadow-md shadow-cyan-950'
                        : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
                    }`}
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>{loading && isSelected ? 'Loading Scenario...' : isSelected ? 'Active Scenario' : 'Load Scenario'}</span>
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Global Controls: Export & Reset */}
        <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <button
              onClick={handleExportDataset}
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono flex items-center space-x-1.5 transition-colors border border-slate-700"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export Full Dataset (.JSON)</span>
            </button>
            <button
              onClick={handleResetToBaseline}
              disabled={loading}
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-300 text-xs font-mono flex items-center space-x-1.5 transition-colors border border-slate-700"
            >
              <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
              <span>Reset to Baseline</span>
            </button>
          </div>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold transition-all"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
