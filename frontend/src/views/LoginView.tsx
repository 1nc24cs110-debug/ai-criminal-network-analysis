import React, { useState } from 'react';
import { Shield, Lock, User, ArrowRight, AlertCircle, Key, Check } from 'lucide-react';
import { api } from '../api';
import { User as UserType } from '../types';

interface LoginViewProps {
  onLoginSuccess: (user: UserType) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('investigator');
  const [password, setPassword] = useState('Investigator@2026!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.login(username, password);
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const setDemoRole = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#060A14] flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background radial gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(14,165,233,0.12),transparent_70%)] pointer-events-none"></div>
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a10_1px,transparent_1px),linear-gradient(to_bottom,#0f172a10_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none"></div>

      {/* Main card */}
      <div className="w-full max-w-md relative z-10">
        {/* Header Badge */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-xl shadow-cyan-500/20 ring-1 ring-cyan-400/40 mb-3">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-xl font-extrabold tracking-wider text-white">
            CRIMINAL NETWORK ANALYSIS
          </h1>
          <p className="text-xs text-cyan-400 font-mono tracking-widest uppercase mt-0.5">
            AI-POWERED INVESTIGATIVE DECISION-SUPPORT
          </p>
          <div className="mt-2 inline-block px-2.5 py-0.5 rounded bg-red-950/80 border border-red-800/60 text-red-400 font-mono text-[10px] font-bold tracking-widest">
            OFFICIAL USE ONLY // RESTRICTED ACCESS
          </div>
        </div>

        {/* Login form container */}
        <div className="bg-[#0D1527]/90 border border-slate-800/90 rounded-2xl p-7 shadow-2xl backdrop-blur-xl">
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-950/60 border border-red-800/80 text-red-300 text-xs flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 font-mono">
                INVESTIGATOR USERNAME
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-900/80 border border-slate-700/80 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 font-mono"
                  placeholder="e.g. investigator"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 font-mono">
                AUTHENTICATION SECRET
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-900/80 border border-slate-700/80 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 font-mono"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-950 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{loading ? 'AUTHENTICATING...' : 'SECURE SIGN IN'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Role Selector */}
          <div className="mt-6 pt-5 border-t border-slate-800">
            <p className="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2.5 font-semibold">
              Select Demo Credentials:
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setDemoRole('investigator', 'Investigator@2026!')}
                className={`p-2 rounded-lg text-left border transition-all text-xs ${
                  username === 'investigator'
                    ? 'bg-cyan-950/70 border-cyan-700 text-cyan-200 ring-1 ring-cyan-500'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="font-semibold text-[11px]">Investigator</div>
                <div className="text-[10px] text-slate-400 font-mono">Special Agent</div>
              </button>

              <button
                type="button"
                onClick={() => setDemoRole('admin', 'Admin@2026!')}
                className={`p-2 rounded-lg text-left border transition-all text-xs ${
                  username === 'admin'
                    ? 'bg-cyan-950/70 border-cyan-700 text-cyan-200 ring-1 ring-cyan-500'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="font-semibold text-[11px]">Director</div>
                <div className="text-[10px] text-slate-400 font-mono">Administrator</div>
              </button>

              <button
                type="button"
                onClick={() => setDemoRole('analyst', 'Analyst@2026!')}
                className={`p-2 rounded-lg text-left border transition-all text-xs ${
                  username === 'analyst'
                    ? 'bg-cyan-950/70 border-cyan-700 text-cyan-200 ring-1 ring-cyan-500'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="font-semibold text-[11px]">Analyst</div>
                <div className="text-[10px] text-slate-400 font-mono">Intelligence</div>
              </button>
            </div>
          </div>
        </div>

        {/* Security Warning Footer */}
        <p className="mt-5 text-center text-[10px] font-mono text-slate-500 leading-normal">
          Authorized personnel only. All access, queries, and graph interactions are continuously recorded in the tamper-evident audit trail.
        </p>
      </div>
    </div>
  );
};
