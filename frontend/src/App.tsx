import React, { useState, useEffect } from 'react';
import { api, clearAuthToken, getAuthToken } from './api';
import { User } from './types';
import { Navbar } from './components/Navbar';
import { Sidebar, NavTab } from './components/Sidebar';
import { LoginView } from './views/LoginView';
import { OverviewView } from './views/OverviewView';
import { InvestigationsView } from './views/InvestigationsView';
import { EntityExplorerView } from './views/EntityExplorerView';
import { NetworkIntelligenceView } from './views/NetworkIntelligenceView';
import { EvidenceCenterView } from './views/EvidenceCenterView';
import { AIAssistantView } from './views/AIAssistantView';
import { AlertsView } from './views/AlertsView';
import { ReportsView } from './views/ReportsView';
import { SettingsAuditView } from './views/SettingsAuditView';
import { SyntheticLabModal } from './components/SyntheticLabModal';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState<NavTab>('overview');
  const [isSyntheticModalOpen, setIsSyntheticModalOpen] = useState(false);

  // Quick navigation state
  const [selectedCaseForGraph, setSelectedCaseForGraph] = useState<number | undefined>(undefined);
  const [selectedEntityForGraph, setSelectedEntityForGraph] = useState<number | undefined>(undefined);

  // Badges
  const [alertsCount, setAlertsCount] = useState<number>(0);
  const [pendingVerifications, setPendingVerifications] = useState<number>(0);

  useEffect(() => {
    checkAuth();

    const handleAuthExpired = () => {
      setCurrentUser(null);
    };
    window.addEventListener('auth-expired', handleAuthExpired);
    return () => window.removeEventListener('auth-expired', handleAuthExpired);
  }, []);

  const checkAuth = async () => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const user = await api.getMe();
      setCurrentUser(user);
      loadGlobalCounts();
    } catch {
      clearAuthToken();
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  const loadGlobalCounts = async () => {
    try {
      const [alerts, rels] = await Promise.all([
        api.listAlerts(undefined, 'NEW'),
        api.listRelationships({ verification_status: 'PENDING_REVIEW' })
      ]);
      setAlertsCount(alerts.length);
      setPendingVerifications(rels.length);
    } catch (err) {
      console.warn('Could not load badge counts', err);
    }
  };

  const handleLogout = () => {
    clearAuthToken();
    setCurrentUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080D1A] flex items-center justify-center">
        <div className="flex flex-col items-center space-y-3 text-cyan-400 font-mono text-xs">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <span>INITIALIZING SECURE INVESTIGATIVE TERMINAL...</span>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return (
      <LoginView
        onLoginSuccess={(user) => {
          setCurrentUser(user);
          loadGlobalCounts();
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#080D1A] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-black">
      <Navbar
        user={currentUser}
        onLogout={handleLogout}
        alertsCount={alertsCount}
        onOpenSyntheticLab={() => setIsSyntheticModalOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={(tab) => setCurrentTab(tab)}
          alertsCount={alertsCount}
          pendingVerifications={pendingVerifications}
        />

        <main className="flex-1 overflow-y-auto">
          {currentTab === 'overview' && (
            <OverviewView
              onNavigate={(tab) => setCurrentTab(tab)}
              onOpenSyntheticLab={() => setIsSyntheticModalOpen(true)}
            />
          )}

          {currentTab === 'investigations' && (
            <InvestigationsView
              onNavigate={(tab) => setCurrentTab(tab)}
              onSelectCase={(cId) => {
                setSelectedCaseForGraph(cId);
                setCurrentTab('graph');
              }}
            />
          )}

          {currentTab === 'entities' && (
            <EntityExplorerView
              onNavigate={(tab) => setCurrentTab(tab)}
              onSelectEntityForGraph={(eId) => {
                setSelectedEntityForGraph(eId);
                setCurrentTab('graph');
              }}
            />
          )}

          {currentTab === 'graph' && (
            <NetworkIntelligenceView
              initialCaseId={selectedCaseForGraph}
              initialEntityId={selectedEntityForGraph}
            />
          )}

          {currentTab === 'evidence' && (
            <EvidenceCenterView />
          )}

          {currentTab === 'assistant' && (
            <AIAssistantView />
          )}

          {currentTab === 'alerts' && (
            <AlertsView />
          )}

          {currentTab === 'reports' && (
            <ReportsView />
          )}

          {currentTab === 'settings' && (
            <SettingsAuditView
              currentUser={currentUser}
              onOpenSyntheticLab={() => setIsSyntheticModalOpen(true)}
            />
          )}
        </main>
      </div>

      <SyntheticLabModal
        isOpen={isSyntheticModalOpen}
        onClose={() => setIsSyntheticModalOpen(false)}
        onScenarioLoaded={() => {
          loadGlobalCounts();
          window.location.reload();
        }}
      />
    </div>
  );
};
