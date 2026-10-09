import React from 'react';
import { Shield, LayoutDashboard, UserPlus, Users, GitCompare, Share2, FileText, UserCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, role, setRole, district, setDistrict }) {
  const roles = [
    { label: 'Station Officer (District)', value: 'Station Officer' },
    { label: 'CWC Officer (Child Welfare)', value: 'CWC Officer' },
    { label: 'Investigating Officer (Cross-District)', value: 'Investigating Officer' },
  ];

  const districts = ['Pune', 'Mumbai Suburban', 'Thane', 'Nagpur'];

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'cases', label: 'Case Directory', icon: Users },
    { id: 'intake', label: 'File Intake Report', icon: UserPlus },
    { id: 'matches', label: 'Match Review', icon: GitCompare },
    { id: 'graph', label: 'Trafficking Graph', icon: Share2 },
    { id: 'audit', label: 'Audit Trail', icon: FileText },
  ];

  return (
    <header className="bg-slate-900/90 border-b border-slate-800 sticky top-0 z-50 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="p-2 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg shadow-lg shadow-amber-500/20">
              <Shield className="w-6 h-6 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-white">RAKSHAK <span className="text-amber-500">LINK</span></span>
                <span className="text-[10px] uppercase font-extrabold px-1.5 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded">v1.0 Demo</span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Cross-District Intelligence & Match Engine</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-inner'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Mock Role / District Switcher */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-slate-950 p-1.5 rounded-lg border border-slate-800 text-xs">
              <UserCheck className="w-4 h-4 text-amber-500 ml-1" />
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="bg-transparent text-slate-200 font-semibold focus:outline-none text-xs cursor-pointer"
              >
                {roles.map((r) => (
                  <option key={r.value} value={r.value} className="bg-slate-900 text-slate-200">
                    {r.label}
                  </option>
                ))}
              </select>

              <span className="text-slate-700">|</span>

              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="bg-transparent text-amber-400 font-bold focus:outline-none text-xs cursor-pointer"
              >
                {districts.map((d) => (
                  <option key={d} value={d} className="bg-slate-900 text-slate-200">
                    📍 {d}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
