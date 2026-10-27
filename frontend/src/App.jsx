import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import CaseList from './components/CaseList';
import IntakeForm from './components/IntakeForm';
import MatchReview from './components/MatchReview';
import GraphView from './components/GraphView';
import AuditLogView from './components/AuditLogView';
import RakhiChatbot from './components/RakhiChatbot';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [role, setRole] = useState('Station Officer');
  const [district, setDistrict] = useState('Pune');
  const [selectedCase, setSelectedCase] = useState(null);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        role={role}
        setRole={setRole}
        district={district}
        setDistrict={setDistrict}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'dashboard' && (
          <Dashboard
            role={role}
            district={district}
            setActiveTab={setActiveTab}
            onSelectCase={setSelectedCase}
          />
        )}

        {activeTab === 'cases' && (
          <CaseList
            role={role}
            district={district}
            onSelectCase={setSelectedCase}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'intake' && (
          <IntakeForm
            role={role}
            district={district}
            onCaseCreated={(c) => setSelectedCase(c)}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'matches' && (
          <MatchReview
            selectedCase={selectedCase}
            role={role}
            district={district}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'graph' && (
          <GraphView
            role={role}
            district={district}
          />
        )}

        {activeTab === 'audit' && (
          <AuditLogView
            role={role}
            district={district}
          />
        )}
      </main>

      <RakhiChatbot />

      <footer className="bg-slate-900/60 border-t border-slate-800 py-4 text-center text-xs text-slate-500">
        <p>Rakshak Link Prototype • AI-Powered Cross-District Missing Person & Anti-Trafficking Intelligence Portal</p>
      </footer>
    </div>
  );
}
