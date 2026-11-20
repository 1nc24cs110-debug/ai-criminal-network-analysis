import React from 'react';
import { Shield, Bell, User as UserIcon, LogOut, Activity, Database, CheckCircle, Sparkles } from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  user: User | null;
  onLogout: () => void;
  activeCaseNumber?: string;
  alertsCount?: number;
  onOpenSyntheticLab?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogout, activeCaseNumber, alertsCount = 0, onOpenSyntheticLab }) => {
  return (
    <header className="h-16 bg-[#0B132B]/95 border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-40 backdrop-blur-md">
      {/* Brand & Classification */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-700 flex items-center justify-center shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-400/40">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-base tracking-wider bg-gradient-to-r from-white via-cyan-200 to-sky-400 bg-clip-text text-transparent">
                CRIMINAL NETWORK ANALYSIS
              </span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold tracking-wider">
                AI DECISION-SUPPORT v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-wide">
              EVIDENCE PROVENANCE & EXPLAINABLE GRAPH INTELLIGENCE
            </p>
          </div>
        </div>

        {/* Classification Banner */}
        <div className="hidden lg:flex items-center space-x-2 pl-4 border-l border-slate-800">
          <span className="px-2 py-0.5 text-[10px] font-mono font-bold tracking-widest bg-red-950/80 text-red-400 border border-red-800/60 rounded">
            LAW ENFORCEMENT SENSITIVE
          </span>
          <span className="text-[11px] text-slate-500 font-mono">FED-LE-AUTH-ID: 9942</span>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center space-x-4">
        {/* Active System Indicator */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-slate-300 font-mono text-[11px]">NETWORK ENGINE ONLINE</span>
        </div>

        {/* Synthetic Lab Button */}
        {onOpenSyntheticLab && (
          <button
            onClick={onOpenSyntheticLab}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-700/80 text-cyan-300 hover:text-white text-xs font-mono font-semibold transition-all shadow-md shadow-cyan-950"
            title="Switch Synthetic Investigation Scenarios & Datasets"
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span>SYNTHETIC LAB</span>
          </button>
        )}

        {/* User Profile & Badge */}
        {user && (
          <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-semibold text-slate-200 flex items-center justify-end space-x-1.5">
                <span>{user.full_name}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-sky-950 text-sky-400 border border-sky-800">
                  {user.role}
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono">
                {user.badge_number ? `BADGE: ${user.badge_number}` : user.department}
              </p>
            </div>

            <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400">
              <UserIcon className="w-4 h-4" />
            </div>

            <button
              onClick={onLogout}
              title="Sign Out"
              className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition-colors border border-transparent hover:border-red-900/50"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
