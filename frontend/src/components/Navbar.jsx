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
    <header className="bg-darkblue/95 border-b border-darkblue/40 sticky top-0 z-50 backdrop-blur-md">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        {/* Top row: Logo + Controls */}
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo */}
          <div className="flex items-center space-x-2 sm:space-x-3 cursor-pointer min-w-fit" onClick={() => setActiveTab('dashboard')}>
            <div className="p-2 bg-gradient-to-br from-earth to-yellow-600 rounded-lg shadow-lg shadow-earth/30 flex-shrink-0">
              <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-darkblue stroke-[2.5]" />
            </div>
            <div className="hidden sm:block">
              <div className="flex items-center space-x-2">
                <span className="text-lg sm:text-xl font-bold tracking-tight text-ashgray">RAKSHAK <span className="text-earth">LINK</span></span>
                <span className="text-[9px] uppercase font-extrabold px-1.5 py-0.5 bg-earth/10 text-earth border border-earth/40 rounded">v1.0</span>
              </div>
            </div>
          </div>

          {/* Role/District Switcher */}
          <div className="flex items-center space-x-1 sm:space-x-2 bg-darkblue/60 p-1 sm:p-1.5 rounded-lg border border-earth/30 text-xs flex-shrink-0">
            <UserCheck className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-earth ml-0.5 sm:ml-1 hidden sm:block" />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="bg-transparent text-ashgray font-semibold focus:outline-none text-xs cursor-pointer"
            >
              {roles.map((r) => (
                <option key={r.value} value={r.value} className="bg-darkblue text-ashgray">
                  {r.label}
                </option>
              ))}
            </select>

            <span className="text-darkblue/60 hidden sm:block">|</span>

            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className="bg-transparent text-earth font-bold focus:outline-none text-xs cursor-pointer"
            >
              {districts.map((d) => (
                <option key={d} value={d} className="bg-darkblue text-ashgray">
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Navigation Tabs - Full width on second row */}
        <nav className="flex overflow-x-auto gap-1 pb-2 border-t border-darkblue/40 pt-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-1 px-2 sm:px-3 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all whitespace-nowrap flex-shrink-0 ${
                  isActive
                    ? 'bg-earth/20 text-earth border border-earth/50 shadow-inner'
                    : 'text-ashgray hover:text-earth hover:bg-darkblue/40'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 sm:w-4 sm:h-4 ${isActive ? 'text-earth' : 'text-ashgray/70'}`} />
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="sm:hidden text-[10px]">{tab.label.split(' ')[0]}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
