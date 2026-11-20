import React from 'react';
import {
  LayoutDashboard,
  FolderGit2,
  Users2,
  Share2,
  FileSearch,
  BotMessageSquare,
  AlertTriangle,
  FileText,
  Sliders,
  ChevronRight
} from 'lucide-react';

export type NavTab =
  | 'overview'
  | 'investigations'
  | 'entities'
  | 'graph'
  | 'evidence'
  | 'assistant'
  | 'alerts'
  | 'reports'
  | 'settings';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  alertsCount?: number;
  pendingVerifications?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  alertsCount = 0,
  pendingVerifications = 0
}) => {
  const navItems: Array<{ id: NavTab; label: string; icon: any; badge?: number; badgeColor?: string }> = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'investigations', label: 'Investigations', icon: FolderGit2 },
    { id: 'entities', label: 'Entity Explorer', icon: Users2 },
    { id: 'graph', label: 'Network Intelligence', icon: Share2 },
    {
      id: 'evidence',
      label: 'Evidence Center',
      icon: FileSearch,
      badge: pendingVerifications > 0 ? pendingVerifications : undefined,
      badgeColor: 'bg-amber-950 text-amber-400 border-amber-800'
    },
    { id: 'assistant', label: 'AI Assistant', icon: BotMessageSquare },
    {
      id: 'alerts',
      label: 'Alerts & Anomalies',
      icon: AlertTriangle,
      badge: alertsCount > 0 ? alertsCount : undefined,
      badgeColor: 'bg-rose-950 text-rose-400 border-rose-800'
    },
    { id: 'reports', label: 'Dossier Reports', icon: FileText },
    { id: 'settings', label: 'Audit & Settings', icon: Sliders },
  ];

  return (
    <aside className="w-64 bg-[#0B132B]/80 border-r border-slate-800/80 flex flex-col justify-between py-4 backdrop-blur-md shrink-0">
      <div className="space-y-1 px-3">
        <div className="px-3 pb-2 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
          Investigative Modules
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-950/80 to-blue-950/40 text-cyan-300 border border-cyan-800/60 shadow-sm shadow-cyan-950'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon
                  className={`w-4 h-4 transition-colors ${
                    isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-300'
                  }`}
                />
                <span className="tracking-wide">{item.label}</span>
              </div>

              <div className="flex items-center space-x-1">
                {item.badge !== undefined && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full border ${item.badgeColor || 'bg-slate-800 text-slate-300'}`}
                  >
                    {item.badge}
                  </span>
                )}
                {isActive && <ChevronRight className="w-3.5 h-3.5 text-cyan-400/80" />}
              </div>
            </button>
          );
        })}
      </div>

      {/* Evidentiary Notice Footer */}
      <div className="px-4 py-3 mx-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-[11px] text-slate-400">
        <div className="flex items-center space-x-1.5 text-cyan-400 font-semibold mb-1">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
          <span className="text-[10px] uppercase font-mono tracking-wider">Investigative Safeguard</span>
        </div>
        <p className="text-[10px] text-slate-500 leading-relaxed font-sans">
          Graph metrics do not infer guilt. All facts require verified evidentiary provenance.
        </p>
      </div>
    </aside>
  );
};
