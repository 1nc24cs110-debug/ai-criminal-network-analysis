import React, { useState, useEffect } from 'react';
import {
  AlertTriangle, ShieldAlert, CheckCircle2, XCircle, Clock,
  Filter, ArrowRight, Eye, Info, Check, X
} from 'lucide-react';
import { api } from '../api';
import { NetworkPatternAlert } from '../types';

export const AlertsView: React.FC = () => {
  const [alerts, setAlerts] = useState<NetworkPatternAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  // Resolve Modal state
  const [resolvingAlert, setResolvingAlert] = useState<NetworkPatternAlert | null>(null);
  const [resolutionStatus, setResolutionStatus] = useState('RESOLVED');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [resolveLoading, setResolveLoading] = useState(false);

  useEffect(() => {
    loadAlerts();
  }, [filterStatus]);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const statusParam = filterStatus === 'ALL' ? undefined : filterStatus;
      const data = await api.listAlerts(undefined, statusParam);
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolvingAlert) return;
    setResolveLoading(true);
    try {
      await api.resolveAlert(resolvingAlert.id, resolutionStatus, resolutionNotes || 'Investigator reviewed and resolved.');
      setResolvingAlert(null);
      setResolutionNotes('');
      await loadAlerts();
    } catch (err: any) {
      alert(`Error resolving alert: ${err.message}`);
    } finally {
      setResolveLoading(false);
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-950 text-red-400 border-red-800';
      case 'HIGH':
        return 'bg-rose-950 text-rose-400 border-rose-800';
      case 'MEDIUM':
        return 'bg-amber-950 text-amber-400 border-amber-800';
      default:
        return 'bg-blue-950 text-blue-400 border-blue-800';
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold text-white tracking-wide">
              EXPLAINABLE NETWORK PATTERN ALERTS
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-rose-950 text-rose-300 border border-rose-800">
              {alerts.length} ALERTS ON FILE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated pattern detection for cross-case capital convergence, telecommunication bridges, and structural outliers.
          </p>
        </div>

        {/* Status Filters */}
        <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-xl border border-slate-800 self-start sm:self-auto">
          {['ALL', 'NEW', 'UNDER_INVESTIGATION', 'RESOLVED', 'FALSE_POSITIVE'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                filterStatus === st
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {st.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Stream */}
      {loading ? (
        <div className="py-20 flex justify-center items-center text-cyan-400 font-mono text-xs">
          FETCHING PATTERN ALERTS...
        </div>
      ) : alerts.length === 0 ? (
        <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-200">No Alerts In Selected Category</p>
          <p className="text-xs text-slate-500 mt-1">All flagged patterns have been triaged or no anomalies match the active filter.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((al) => {
            const isNew = al.status === 'NEW';
            return (
              <div
                key={al.id}
                className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2.5">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase border ${getSeverityBadge(
                        al.severity
                      )}`}
                    >
                      {al.severity} SEVERITY
                    </span>
                    <span className="text-xs font-mono font-bold text-slate-300 uppercase">
                      TYPE: {al.alert_type}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-xs font-mono">
                    <span className="text-slate-400">
                      Confidence: <strong className="text-cyan-400">{Math.round(al.confidence * 100)}%</strong>
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded uppercase font-bold text-[10px] ${
                        al.status === 'NEW'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800 animate-pulse'
                          : 'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}
                    >
                      {al.status}
                    </span>
                  </div>
                </div>

                {/* Title & Explanation */}
                <div>
                  <h3 className="text-sm font-bold text-white tracking-wide">{al.title}</h3>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800/80 font-sans">
                    {al.explanation}
                  </p>
                </div>

                {/* Affected Entities & Relationships */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 text-xs font-mono">
                  <div className="flex items-center space-x-2 text-slate-400">
                    <span>AFFECTED ENTITIES:</span>
                    <div className="flex items-center space-x-1">
                      {al.affected_entities.map((eid) => (
                        <span key={eid} className="px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 border border-slate-700 text-[10px]">
                          #{eid}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Triage / Resolve Button */}
                  {isNew && (
                    <button
                      onClick={() => {
                        setResolvingAlert(al);
                        setResolutionStatus('RESOLVED');
                      }}
                      className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-md shadow-cyan-950"
                    >
                      <span>Triage & Resolve</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Resolution Modal */}
      {resolvingAlert && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-[#0D1527] border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <button
              onClick={() => setResolvingAlert(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="text-base font-bold text-white mb-2">RESOLVE NETWORK ANOMALY</h2>
            <p className="text-xs text-slate-400 mb-4 font-mono">{resolvingAlert.title}</p>

            <form onSubmit={handleResolve} className="space-y-4">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">DECISION STATUS</label>
                <select
                  value={resolutionStatus}
                  onChange={(e) => setResolutionStatus(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                >
                  <option value="RESOLVED">CONFIRMED ANOMALY (UNDER ACTION)</option>
                  <option value="UNDER_INVESTIGATION">ASSIGN FOR DEEP SURVEILLANCE</option>
                  <option value="FALSE_POSITIVE">DISMISS AS BENIGN ACTIVITY / FALSE POSITIVE</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">INVESTIGATOR AUDIT NOTES *</label>
                <textarea
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  required
                  rows={3}
                  placeholder="Document the investigative rationale for resolving or escalating this pattern..."
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs focus:border-cyan-500 focus:outline-none leading-relaxed"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setResolvingAlert(null)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={resolveLoading}
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-all shadow-md shadow-cyan-950 disabled:opacity-50"
                >
                  {resolveLoading ? 'Recording...' : 'Commit Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
