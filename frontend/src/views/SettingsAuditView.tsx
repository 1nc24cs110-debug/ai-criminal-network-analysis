import React, { useState, useEffect } from 'react';
import {
  Sliders, Activity, Shield, Users, Database, Search,
  CheckCircle2, AlertCircle, Key, RefreshCw, Lock, Sparkles, Download,
  Cpu, Terminal, Copy, Check
} from 'lucide-react';
import { api } from '../api';
import { AuditLog, User } from '../types';

export const SettingsAuditView: React.FC<{ currentUser: User | null; onOpenSyntheticLab?: () => void }> = ({ currentUser, onOpenSyntheticLab }) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  // Admin New User modal
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newRole, setNewRole] = useState('INVESTIGATOR');
  const [newBadge, setNewBadge] = useState('');
  const [copiedMcp, setCopiedMcp] = useState(false);

  useEffect(() => {
    loadData();
  }, [actionFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const actionParam = actionFilter === 'ALL' ? undefined : actionFilter;
      const [lData, hData] = await Promise.all([
        api.listAuditLogs(actionParam),
        api.getSystemHealth()
      ]);
      setLogs(lData);
      setHealth(hData);

      if (currentUser?.role === 'ADMIN') {
        const uData = await api.listUsers().catch(() => []);
        setUsers(uData);
      }
    } catch (err) {
      console.error('Failed to load audit logs/settings', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetch('/api/auth/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('intel_auth_token')}`
        },
        body: JSON.stringify({
          username: newUsername,
          email: newEmail,
          password: newPassword,
          full_name: newFullName,
          role: newRole,
          badge_number: newBadge
        })
      });
      alert(`User ${newUsername} created successfully.`);
      setShowAddUser(false);
      loadData();
    } catch (err: any) {
      alert(`Error creating user: ${err.message}`);
    }
  };

  const filteredLogs = logs.filter((l) => {
    const s = search.toLowerCase();
    return (
      l.action.toLowerCase().includes(s) ||
      (l.username && l.username.toLowerCase().includes(s)) ||
      (l.entity_type && l.entity_type.toLowerCase().includes(s)) ||
      JSON.stringify(l.details).toLowerCase().includes(s)
    );
  });

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold text-white tracking-wide">
              SYSTEM DIAGNOSTICS & AUDIT TRAIL
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              TAMPER-EVIDENT LOGGING
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Cryptographically tracked audit logs recording all user logins, graph queries, relationship verifications, and entity merges.
          </p>
        </div>

        <button
          onClick={loadData}
          className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono flex items-center space-x-1.5 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Refresh Audit Stream</span>
        </button>
      </div>

      {/* System Health Status Cards */}
      {health && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono text-xs">
          <div className="p-4 rounded-xl bg-[#0D1527] border border-slate-800 shadow-lg">
            <span className="text-[10px] text-slate-500 uppercase block font-semibold">Engine Status</span>
            <div className="flex items-center space-x-2 mt-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span className="text-white font-bold">{health.status}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#0D1527] border border-slate-800 shadow-lg">
            <span className="text-[10px] text-slate-500 uppercase block font-semibold">Database Store</span>
            <div className="flex items-center space-x-2 mt-1">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-white font-bold">{health.database}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#0D1527] border border-slate-800 shadow-lg">
            <span className="text-[10px] text-slate-500 uppercase block font-semibold">Active Records</span>
            <span className="text-cyan-400 font-bold block mt-1">
              {health.database_records.entities} Entities / {health.database_records.relationships} Links
            </span>
          </div>

          <div className="p-4 rounded-xl bg-[#0D1527] border border-slate-800 shadow-lg">
            <span className="text-[10px] text-slate-500 uppercase block font-semibold">Total Audit Events</span>
            <span className="text-purple-400 font-bold block mt-1">
              {health.database_records.audit_logs} Actions Recorded
            </span>
          </div>
        </div>
      )}

      {/* Synthetic Data Management & Export Hub */}
      <div className="p-5 rounded-xl bg-gradient-to-r from-cyan-950/60 via-[#0D1527] to-slate-900 border border-cyan-800/80 shadow-xl space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-2">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-white">
                SYNTHETIC DATA LAB & EXPORT CENTER
              </h3>
              <p className="text-[11px] text-slate-400">
                Manage, switch, or export synthetic criminal network demonstration scenarios
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {onOpenSyntheticLab && (
              <button
                onClick={onOpenSyntheticLab}
                className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-md shadow-cyan-950"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Switch Scenario</span>
              </button>
            )}
            <button
              onClick={async () => {
                const data = await api.exportSyntheticDataset();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `synthetic_dataset_export_${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono text-xs font-semibold flex items-center space-x-1.5 transition-all border border-slate-700"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export JSON</span>
            </button>
          </div>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          This system exclusively demonstrates investigative methods using synthetic intelligence records. You can load specific scenario profiles (e.g. Maritime Contraband, Darknet Crypto Mixers, or Ransomware Operations) or download the complete synthetic relational schema for external data science evaluations.
        </p>
      </div>

      {/* Model Context Protocol (MCP) Integration Hub */}
      <div className="p-5 rounded-xl bg-[#0B132B] border border-indigo-900/60 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-indigo-950 gap-2">
          <div className="flex items-center space-x-2.5">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-white">
                  MODEL CONTEXT PROTOCOL (MCP) SERVER
                </h3>
                <span className="px-2 py-0.5 text-[9px] font-mono rounded bg-indigo-950 text-indigo-300 border border-indigo-700">
                  JSON-RPC 2.0 (STDIO)
                </span>
                <span className="px-2 py-0.5 text-[9px] font-mono rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                  READY
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Exposes the Criminal Network Knowledge Graph, Forensic Dossiers, and NetworkX Analytics to MCP-compliant AI assistants
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              const snippet = JSON.stringify({
                mcpServers: {
                  "criminal-network-mcp": {
                    command: "python",
                    args: ["mcp_server.py"]
                  }
                }
              }, null, 2);
              navigator.clipboard.writeText(snippet);
              setCopiedMcp(true);
              setTimeout(() => setCopiedMcp(false), 2500);
            }}
            className="px-3.5 py-1.5 rounded-lg bg-indigo-900/80 hover:bg-indigo-800 text-indigo-200 font-mono text-xs font-semibold flex items-center space-x-1.5 transition-all border border-indigo-700/60 shadow-sm"
          >
            {copiedMcp ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-indigo-300" />}
            <span>{copiedMcp ? 'Config Copied!' : 'Copy mcp_config.json'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <span className="text-[10px] font-mono uppercase text-indigo-400 font-bold block mb-1">
              8 Forensic Tools
            </span>
            <div className="flex flex-wrap gap-1 font-mono text-[10px] text-slate-300">
              {['list_cases', 'search_entities', 'get_entity_dossier', 'calculate_network_metrics', 'find_shortest_evidentiary_path', 'extract_intelligence_from_document', 'get_pattern_alerts', 'verify_relationship'].map((t) => (
                <span key={t} className="px-1.5 py-0.5 bg-slate-800/90 rounded border border-slate-700/50">
                  {t}
                </span>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <span className="text-[10px] font-mono uppercase text-cyan-400 font-bold block mb-1">
              4 Evidentiary Resources
            </span>
            <div className="space-y-1 font-mono text-[10px] text-slate-300">
              {['investigation://cases', 'investigation://network-graph', 'investigation://alerts', 'investigation://audit-log'].map((r) => (
                <div key={r} className="truncate text-cyan-300/80 bg-slate-800/50 px-1.5 py-0.5 rounded border border-slate-700/40">
                  {r}
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <span className="text-[10px] font-mono uppercase text-purple-400 font-bold block mb-1">
              3 Investigation Prompts
            </span>
            <div className="space-y-1 font-mono text-[10px] text-slate-300">
              {['investigate_person_of_interest', 'cross_case_bridge_analysis', 'evidentiary_integrity_audit'].map((p) => (
                <div key={p} className="truncate text-purple-300/80 bg-slate-800/50 px-1.5 py-0.5 rounded border border-slate-700/40">
                  {p}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80 font-mono text-[11px] text-slate-400 flex items-center justify-between">
          <div className="flex items-center space-x-2 truncate">
            <Terminal className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
            <span className="text-slate-500">Run Local Server:</span>
            <code className="text-emerald-300">python mcp_server.py</code>
          </div>
          <span className="text-[10px] text-slate-500 hidden sm:inline">Official MCP Spec (2024-11-05)</span>
        </div>
      </div>

      {/* Audit Log Table Section */}
      <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
              TAMPER-EVIDENT INVESTIGATIVE AUDIT LOG
            </h3>
          </div>

          {/* Action Filter */}
          <div className="flex items-center space-x-2">
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
            >
              <option value="ALL">ALL AUDIT ACTIONS</option>
              <option value="LOGIN">LOGIN</option>
              <option value="VERIFY_RELATIONSHIP">VERIFY RELATIONSHIP</option>
              <option value="REJECT_RELATIONSHIP">REJECT RELATIONSHIP</option>
              <option value="CREATE_CASE">CREATE CASE</option>
              <option value="UPLOAD_EVIDENCE">UPLOAD EVIDENCE</option>
              <option value="COMMIT_EXTRACTIONS">COMMIT EXTRACTIONS</option>
              <option value="AI_QUERY">AI QUERY</option>
              <option value="FIND_SHORTEST_PATH">FIND SHORTEST PATH</option>
            </select>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search audit trail by username, target entity, or details payload..."
            className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700/80 rounded-lg text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
          />
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-500 uppercase">
                <th className="py-2 px-3">Timestamp (UTC)</th>
                <th className="py-2 px-3">Officer / User</th>
                <th className="py-2 px-3">Action</th>
                <th className="py-2 px-3">Target</th>
                <th className="py-2 px-3">Audit Details</th>
                <th className="py-2 px-3">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-900/40">
                  <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-3 text-slate-200 font-semibold">
                    {log.username || 'SYSTEM'}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 text-[10px] font-bold">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-400">
                    {log.entity_type ? `${log.entity_type} #${log.entity_id || ''}` : 'N/A'}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400 truncate max-w-xs font-sans text-[11px]">
                    {JSON.stringify(log.details)}
                  </td>
                  <td className="py-2.5 px-3 text-slate-500 text-[11px]">
                    {log.ip_address}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Admin User Management (if ADMIN) */}
      {currentUser?.role === 'ADMIN' && (
        <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
                ROLE-BASED ACCESS CONTROL DIRECTORY (ADMINISTRATOR ACCESS)
              </h3>
            </div>
            <button
              onClick={() => setShowAddUser(true)}
              className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs font-bold transition-all"
            >
              + Create User
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {users.map((u) => (
              <div key={u.id} className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">{u.full_name}</span>
                  <span className="px-1.5 py-0.2 rounded bg-purple-950 text-purple-300 border border-purple-800 font-mono text-[9px] font-bold">
                    {u.role}
                  </span>
                </div>
                <p className="text-slate-400 font-mono text-[11px]">{u.email}</p>
                <div className="flex items-center justify-between pt-1 text-[10px] text-slate-500 font-mono">
                  <span>Badge: {u.badge_number || 'N/A'}</span>
                  <span className="text-emerald-400 font-bold">Active</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
