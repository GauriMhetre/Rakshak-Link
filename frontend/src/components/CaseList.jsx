import React, { useState, useEffect } from 'react';
import { Users, Search, Filter, MapPin, Calendar, GitCompare, Lock, Eye, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function CaseList({ role, district, onSelectCase, setActiveTab }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('');
  const [districtFilter, setDistrictFilter] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadCases();
  }, [typeFilter, districtFilter, role, district]);

  const loadCases = async () => {
    setLoading(true);
    try {
      const data = await api.getCases(
        { type: typeFilter || undefined, district: districtFilter || undefined, search: search || undefined },
        role,
        district
      );
      setCases(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadCases();
  };

  return (
    <div className="space-y-6">
      {/* Top Filter Bar */}
      <div className="glass-card p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Case Directory</h2>
            <p className="text-xs text-slate-400">Scoped view for <span className="text-amber-400 font-semibold">{role} ({district})</span></p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 w-full md:w-auto items-center">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search name, ID, marks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </form>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-200 px-3 py-1.5 rounded-lg focus:outline-none"
          >
            <option value="">All Types (Missing & Found)</option>
            <option value="MISSING">Missing Only</option>
            <option value="FOUND">Found Only</option>
          </select>

          <select
            value={districtFilter}
            onChange={(e) => setDistrictFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-200 px-3 py-1.5 rounded-lg focus:outline-none"
          >
            <option value="">All Districts</option>
            <option value="Pune">Pune</option>
            <option value="Mumbai Suburban">Mumbai Suburban</option>
            <option value="Thane">Thane</option>
            <option value="Nagpur">Nagpur</option>
          </select>
        </div>
      </div>

      {/* Case Grid */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading cases...</div>
      ) : cases.length === 0 ? (
        <div className="glass-card p-12 text-center text-slate-400 space-y-2">
          <AlertCircle className="w-8 h-8 text-amber-500 mx-auto opacity-60" />
          <p className="font-semibold text-slate-200">No cases match the current filter criteria</p>
          <p className="text-xs">Try clearing search filters or changing the target district.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cases.map((c) => {
            const isMissing = c.type === 'MISSING';
            const isMatched = c.status === 'MATCHED';

            return (
              <div
                key={c.id}
                className="glass-card glass-card-hover p-4 flex flex-col justify-between space-y-3 relative group"
              >
                <div>
                  {/* Card Header Badges */}
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      isMissing ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}>
                      {c.type}
                    </span>

                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      isMatched ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {c.status}
                    </span>
                  </div>

                  {/* Profile info & Photo */}
                  <div className="flex space-x-3 items-start">
                    <div className="w-16 h-16 rounded-lg bg-slate-950 border border-slate-800 overflow-hidden relative shrink-0 flex items-center justify-center">
                      {c.photo_url ? (
                        <img src={c.photo_url} alt={c.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="text-center p-1 text-[9px] text-amber-400 flex flex-col items-center">
                          <Lock className="w-4 h-4 mb-0.5 text-amber-500" />
                          <span>Embedding Only</span>
                        </div>
                      )}
                    </div>

                    <div className="min-w-0 flex-1">
                      <h3 className="text-sm font-bold text-white truncate">{c.name}</h3>
                      {c.devanagari_name && (
                        <p className="text-xs text-amber-400/90 font-medium">{c.devanagari_name}</p>
                      )}
                      <p className="text-xs text-slate-400 mt-0.5">
                        {c.age} yrs • {c.sex} • {c.height_cm} cm
                      </p>
                      <p className="text-[11px] text-slate-500 truncate font-mono mt-0.5">{c.case_number}</p>
                    </div>
                  </div>

                  {/* Attributes */}
                  <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-1 text-xs">
                    <div className="flex items-center text-slate-300 space-x-1.5 truncate">
                      <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                      <span className="truncate">{c.last_seen_found_place}</span>
                    </div>

                    <div className="flex items-center text-slate-400 space-x-1.5 text-[11px]">
                      <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span>{new Date(c.last_seen_found_time).toLocaleDateString()}</span>
                      <span className="text-slate-600">•</span>
                      <span className="font-semibold text-slate-300">📍 {c.district}</span>
                    </div>

                    {c.marks && (
                      <p className="text-[11px] text-slate-400 line-clamp-1 italic bg-slate-950/60 p-1.5 rounded mt-1 border border-slate-800/50">
                        "{c.marks}"
                      </p>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <button
                  onClick={() => {
                    if (onSelectCase) onSelectCase(c);
                    setActiveTab('matches');
                  }}
                  className="w-full py-2 bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 text-xs font-bold rounded-lg transition-all flex items-center justify-center space-x-1.5 group-hover:border-amber-500/50 border border-slate-700"
                >
                  <GitCompare className="w-3.5 h-3.5" />
                  <span>Run Match Review</span>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
