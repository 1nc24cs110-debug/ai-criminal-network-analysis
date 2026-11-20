import React, { useEffect, useState } from 'react';
import {
  FolderGit2, Users2, Link2, Clock, AlertTriangle, FileText,
  Activity, ArrowUpRight, ShieldCheck, CheckCircle2, ChevronRight, Zap, Sparkles
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid
} from 'recharts';
import { api } from '../api';
import { NavTab } from '../components/Sidebar';

interface OverviewViewProps {
  onNavigate: (tab: NavTab) => void;
  onOpenSyntheticLab?: () => void;
}

const COLORS = ['#06B6D4', '#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#EF4444'];

export const OverviewView: React.FC<OverviewViewProps> = ({ onNavigate, onOpenSyntheticLab }) => {
  const [stats, setStats] = useState<any>(null);
  const [charts, setCharts] = useState<any>(null);
  const [recent, setRecent] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sData, cData, rData] = await Promise.all([
        api.getDashboardStats(),
        api.getDashboardCharts(),
        api.getRecentActivity(),
      ]);
      setStats(sData);
      setCharts(cData);
      setRecent(rData);
    } catch (err) {
      console.error('Failed to load overview data', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[500px]">
        <div className="flex flex-col items-center space-y-3 text-cyan-400">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <span className="font-mono text-xs tracking-wider">LOADING INTELLIGENCE DASHBOARD...</span>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      label: 'TOTAL INVESTIGATION CASES',
      value: stats.total_cases,
      sub: '3 Active Multi-Jurisdiction Cases',
      icon: FolderGit2,
      color: 'from-blue-600/20 to-cyan-500/10 border-blue-800/60 text-cyan-400',
      action: () => onNavigate('investigations')
    },
    {
      label: 'REGISTERED ENTITIES',
      value: stats.total_entities,
      sub: 'Persons, Accounts, Phones & Hubs',
      icon: Users2,
      color: 'from-sky-600/20 to-indigo-500/10 border-sky-800/60 text-sky-400',
      action: () => onNavigate('entities')
    },
    {
      label: 'VERIFIED RELATIONSHIPS',
      value: stats.verified_relationships,
      sub: 'Confirmed Evidentiary Provenance',
      icon: ShieldCheck,
      color: 'from-emerald-600/20 to-teal-500/10 border-emerald-800/60 text-emerald-400',
      action: () => onNavigate('graph')
    },
    {
      label: 'PENDING HUMAN REVIEW',
      value: stats.pending_relationships,
      sub: 'AI Suggestions Awaiting Approval',
      icon: Clock,
      color: 'from-amber-600/20 to-yellow-500/10 border-amber-800/60 text-amber-400',
      badge: stats.pending_relationships > 0 ? 'Action Required' : undefined,
      action: () => onNavigate('evidence')
    },
    {
      label: 'PATTERNS REQUIRING REVIEW',
      value: stats.unusual_patterns_alerts,
      sub: 'Cross-Case & Topology Anomalies',
      icon: AlertTriangle,
      color: 'from-rose-600/20 to-red-500/10 border-rose-800/60 text-rose-400',
      badge: stats.unusual_patterns_alerts > 0 ? 'High Risk' : undefined,
      action: () => onNavigate('alerts')
    },
    {
      label: 'DOCUMENTED EVIDENCE PIECES',
      value: stats.total_evidence_docs,
      sub: 'Interception & Customs Records',
      icon: FileText,
      color: 'from-purple-600/20 to-violet-500/10 border-purple-800/60 text-purple-400',
      action: () => onNavigate('evidence')
    },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Top Banner / Mission Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold text-white tracking-wide">
              INTELLIGENCE OVERVIEW & CASE STATUS
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
              LIVE MULTI-AGENCY SYNCHRONIZATION
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Cross-case decision support platform enforcing evidence provenance and explainable graph topology.
          </p>
        </div>

        {/* Quick Launch Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onNavigate('graph')}
            className="px-3 py-2 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-600/40 text-xs font-semibold flex items-center space-x-1.5 transition-all"
          >
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>Launch Network Graph</span>
          </button>
          <button
            onClick={() => onNavigate('assistant')}
            className="px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-md shadow-blue-900/40"
          >
            <span>Ask AI Assistant</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Synthetic Intelligence Demo Notice */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-950/70 via-slate-900 to-blue-950/50 border border-cyan-800/80 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-start space-x-3">
          <div className="p-2 rounded-lg bg-cyan-950 border border-cyan-700 text-cyan-400 shrink-0 mt-0.5">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold text-white uppercase tracking-wider">
                SYNTHETIC DEMONSTRATION INTELLIGENCE ACTIVE
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-semibold">
                ORIGINAL DATASET // ETHICALLY COMPLIANT
              </span>
            </div>
            <p className="text-[11px] text-slate-300 mt-0.5 leading-relaxed">
              Records are synthetic investigative models demonstrating cross-case nexus discovery, multi-hop shell laundering, and uncertainty-aware matching without personal identifiable information.
            </p>
          </div>
        </div>

        {onOpenSyntheticLab && (
          <button
            onClick={onOpenSyntheticLab}
            className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-md shadow-cyan-950 shrink-0 self-start md:self-auto"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Switch Scenario</span>
          </button>
        )}
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              onClick={card.action}
              className={`p-4 rounded-xl bg-gradient-to-br ${card.color} border backdrop-blur-md cursor-pointer hover:scale-[1.01] transition-all relative group shadow-lg`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[10px] font-mono tracking-wider font-semibold text-slate-400 uppercase">
                    {card.label}
                  </p>
                  <h3 className="text-2xl font-extrabold text-white mt-1 font-mono">
                    {card.value}
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {card.sub}
                  </p>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-700/50">
                  <Icon className="w-5 h-5" />
                </div>
              </div>

              {card.badge && (
                <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/60">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-950/80 text-amber-300 border border-amber-800/80 font-bold">
                    {card.badge}
                  </span>
                  <span className="text-[10px] text-slate-400 flex items-center space-x-1 group-hover:text-cyan-300">
                    <span>Inspect</span>
                    <ChevronRight className="w-3 h-3" />
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      {charts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Entity Distribution by Type */}
          <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-300">
                  ENTITY DISTRIBUTION BY TYPE
                </h3>
                <p className="text-[11px] text-slate-500">Breakdown of structured investigative entities</p>
              </div>
              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 border border-cyan-800 px-2 py-0.5 rounded">
                {charts.entity_distribution.length} Categories
              </span>
            </div>

            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={charts.entity_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={10}
                    tick={{ fill: '#94a3b8' }}
                    angle={-25}
                    textAnchor="end"
                  />
                  <YAxis stroke="#64748b" fontSize={10} tick={{ fill: '#94a3b8' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                    labelStyle={{ color: '#38bdf8', fontWeight: 'bold' }}
                  />
                  <Bar dataKey="value" fill="#0284c7" radius={[4, 4, 0, 0]}>
                    {charts.entity_distribution.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Verification Status Breakdown */}
          <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-300">
                  RELATIONSHIP VERIFICATION STATUS
                </h3>
                <p className="text-[11px] text-slate-500">Human investigator verification pipeline status</p>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-800 px-2 py-0.5 rounded">
                Audit Monitored
              </span>
            </div>

            <div className="h-60 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={charts.verification_breakdown}
                    dataKey="count"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    innerRadius={50}
                    paddingAngle={4}
                    label={({ name, percent }) => `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    <Cell fill="#10B981" />
                    <Cell fill="#F59E0B" />
                    <Cell fill="#EF4444" />
                    <Cell fill="#64748B" />
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Recent Alerts & Live Audit Stream */}
      {recent && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Anomalies */}
          <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-300">
                  UNUSUAL PATTERN ALERTS
                </h3>
              </div>
              <button
                onClick={() => onNavigate('alerts')}
                className="text-[11px] text-cyan-400 hover:text-cyan-300 font-medium"
              >
                View All
              </button>
            </div>

            <div className="space-y-2.5">
              {recent.recent_alerts.map((alert: any) => (
                <div
                  key={alert.id}
                  onClick={() => onNavigate('alerts')}
                  className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-slate-700 cursor-pointer transition-all"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-xs text-slate-200">{alert.title}</span>
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold uppercase ${
                        alert.severity === 'CRITICAL'
                          ? 'bg-red-950 text-red-400 border border-red-800'
                          : 'bg-amber-950 text-amber-400 border border-amber-800'
                      }`}
                    >
                      {alert.severity}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3 text-[10px] text-slate-400 font-mono mt-1">
                    <span>TYPE: {alert.alert_type}</span>
                    <span>CONFIDENCE: {Math.round(alert.confidence * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Live Audit Log Feed */}
          <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-300">
                  TAMPER-EVIDENT AUDIT TRAIL (LATEST)
                </h3>
              </div>
              <button
                onClick={() => onNavigate('settings')}
                className="text-[11px] text-cyan-400 hover:text-cyan-300 font-medium"
              >
                Full Audit Log
              </button>
            </div>

            <div className="space-y-2">
              {recent.recent_audits.slice(0, 5).map((log: any) => (
                <div
                  key={log.id}
                  className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center space-x-2.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                    <span className="font-mono text-[11px] font-semibold text-slate-200">
                      {log.action}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {log.entity_type} #{log.entity_id || 'N/A'}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
